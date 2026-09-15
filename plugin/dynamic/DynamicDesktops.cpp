#include "DynamicDesktops.hpp"
#include "StartupPolicy.hpp"
#include "../VirtualDesktopBar.hpp"

#include <QCoreApplication>
#include <QDBusArgument>
#include <QDBusConnection>
#include <QDBusInterface>
#include <QDBusReply>
#include <QDBusServiceWatcher>
#include <QFile>
#include <QTimer>
#include <KConfig>
#include <KConfigGroup>

namespace {
const QString service = QStringLiteral("org.kde.plasma.virtualdesktopbar.dynamic");
const QString scriptName = QStringLiteral("virtualdesktopbar-dynamic-desktops");
const QString systemd = QStringLiteral("org.freedesktop.systemd1");

QVariantMap properties(const QString &unit, const QString &interface)
{
    QDBusInterface manager(systemd, QStringLiteral("/org/freedesktop/systemd1"),
                           QStringLiteral("org.freedesktop.systemd1.Manager"));
    QDBusReply<QDBusObjectPath> path = manager.call(QStringLiteral("GetUnit"), unit);
    if (!path.isValid()) return {};
    QDBusInterface object(systemd, path.value().path(), QStringLiteral("org.freedesktop.DBus.Properties"));
    QDBusReply<QVariantMap> reply = object.call(QStringLiteral("GetAll"), interface);
    return reply.isValid() ? reply.value() : QVariantMap{};
}

int activityReadiness()
{
    QDBusInterface activities(QStringLiteral("org.kde.ActivityManager"),
                              QStringLiteral("/ActivityManager/Activities"),
                              QStringLiteral("org.kde.ActivityManager.Activities"));
    const auto reply = activities.call(QStringLiteral("ListActivitiesWithInformation"));
    if (reply.type() == QDBusMessage::ErrorMessage || reply.arguments().size() != 1) return -1;
    const auto data = qvariant_cast<QDBusArgument>(reply.arguments().first());
    // Fail closed on unknown API versions, stopped/starting activities, or an
    // unavailable activity service: those activities can have unrestored windows.
    if (data.currentSignature() != QStringLiteral("a(ssssi)")) return -1;
    bool any = false;
    data.beginArray();
    while (!data.atEnd()) {
        QString id, name, description, icon;
        int state = 0;
        data.beginStructure();
        data >> id >> name >> description >> icon >> state;
        data.endStructure();
        if (state != 2) return 0; // KActivities Running
        any = true;
    }
    data.endArray();
    return any ? 1 : -1;
}
}

DynamicDesktops *DynamicDesktops::instance()
{
    static auto instance = new DynamicDesktops(QCoreApplication::instance());
    return instance;
}

DynamicDesktops::DynamicDesktops(QObject *parent) : QObject(parent)
{
    auto bus = QDBusConnection::sessionBus();
    bus.connect(systemd, QStringLiteral("/org/freedesktop/systemd1"),
                QStringLiteral("org.freedesktop.systemd1.Manager"), QStringLiteral("JobRemoved"),
                this, SLOT(jobRemoved(uint,QDBusObjectPath,QString,QString)));
    QDBusInterface manager(systemd, QStringLiteral("/org/freedesktop/systemd1"),
                           QStringLiteral("org.freedesktop.systemd1.Manager"));
    manager.call(QStringLiteral("Subscribe"));
    auto watcher = new QDBusServiceWatcher(QStringLiteral("org.kde.KWin"), bus,
                                         QDBusServiceWatcher::WatchForOwnerChange, this);
    connect(watcher, &QDBusServiceWatcher::serviceOwnerChanged, this, &DynamicDesktops::scheduleReload);
    for (const auto &signal : {"ActivityAdded", "ActivityRemoved", "ActivityStarted", "ActivityStopped"})
        bus.connect(QStringLiteral("org.kde.ActivityManager"), QStringLiteral("/ActivityManager/Activities"),
                    QStringLiteral("org.kde.ActivityManager.Activities"), QString::fromLatin1(signal),
                    this, (QString::fromLatin1(signal) == QStringLiteral("ActivityStopped"))
                        ? SLOT(activityRestoring()) : SLOT(scheduleReload()));

    // KSMServer completion means applications have been launched, not that all
    // restored windows exist. Without a reliable per-application completion API,
    // keep all persisted destinations for the lifetime of this controller.
    KConfig session(QStringLiteral("ksmserverrc"), KConfig::NoGlobals);
    const auto mode = session.group(QStringLiteral("General")).readEntry("loginMode", QStringLiteral("restorePreviousLogout"));
    if (mode != QStringLiteral("emptySession")) {
        for (const auto &group : session.groupList()) {
            if ((group.startsWith(QStringLiteral("Session:")) || group.startsWith(QStringLiteral("LegacySession:")))
                && session.group(group).readEntry("count", 0) > 0) {
                KConfig kwin(QStringLiteral("kwinrc"), KConfig::NoGlobals);
                m_preserveCount = qMax(1, kwin.group(QStringLiteral("Desktops")).readEntry("Number", 1));
                m_preserveCount = qMax(m_preserveCount, int(VirtualDesktopBar::requestDesktopInfoList().size()));
                qInfo() << "virtualdesktopbar: preserving" << m_preserveCount << "startup desktops for asynchronous session restoration";
                break;
            }
        }
    }
}

void DynamicDesktops::configure(QObject *owner, bool enabled, const QString &name, const QString &command)
{
    if (!enabled) { forget(owner); return; }
    const auto value = qMakePair(name, command);
    if (m_owners.contains(owner) && m_owners.value(owner) == value) return;
    m_owners.insert(owner, value);
    scheduleReload();
}

void DynamicDesktops::forget(QObject *owner)
{
    if (m_owners.remove(owner)) scheduleReload();
}

void DynamicDesktops::activityRestoring()
{
    // Keep stopped activity destinations even if it starts again before the
    // session gate opens. Do not mistake normal initial ActivityStarted for a
    // stopped activity: that would pin the very extra desktop being repaired.
    m_preserveCount = qMax(m_preserveCount, int(VirtualDesktopBar::requestDesktopInfoList().size()));
    scheduleReload();
}

void DynamicDesktops::scheduleReload()
{
    if (m_reloadQueued) return;
    m_reloadQueued = true;
    // Event-loop coalescing only, never an elapsed-time readiness assumption.
    QTimer::singleShot(0, this, [this] { m_reloadQueued = false; reload(); });
}

void DynamicDesktops::jobRemoved(uint, const QDBusObjectPath &, const QString &unit, const QString &)
{
    if (unit == QStringLiteral("plasma-restoresession.service") || unit == QStringLiteral("plasma-ksmserver.service")
        || unit == QStringLiteral("plasma-workspace.target")) scheduleReload();
}

void DynamicDesktops::reload()
{
    auto bus = QDBusConnection::sessionBus();
    if (!m_registered && !m_owners.isEmpty()) {
        if (!bus.registerService(service)) {
            qWarning() << "virtualdesktopbar: another process owns dynamic desktop management";
            return;
        }
        m_registered = bus.registerObject(QStringLiteral("/DynamicDesktops"), this, QDBusConnection::ExportAllSlots);
        if (!m_registered) { bus.unregisterService(service); return; }
    }
    if (!m_registered) return;
    QDBusInterface scripting(QStringLiteral("org.kde.KWin"), QStringLiteral("/Scripting"), QStringLiteral("org.kde.kwin.Scripting"));
    scripting.call(QStringLiteral("unloadScript"), scriptName);
    if (m_owners.isEmpty()) return;
    if (!m_script.isOpen()) {
        QFile source(QStringLiteral(":/virtualdesktopbar/reconcile.js"));
        if (!source.open(QIODevice::ReadOnly) || !m_script.open()) return;
        m_script.write(source.readAll());
        m_script.flush();
    }
    QDBusReply<int> loaded = scripting.call(QStringLiteral("loadScript"), m_script.fileName(), scriptName);
    if (!loaded.isValid() || loaded.value() < 0) {
        qWarning() << "virtualdesktopbar: cannot load dynamic desktop reconciler";
        return;
    }
    QDBusInterface script(QStringLiteral("org.kde.KWin"), QStringLiteral("/Scripting/Script%1").arg(loaded.value()),
                          QStringLiteral("org.kde.kwin.Script"));
    script.asyncCall(QStringLiteral("run"));
}

QVariantMap DynamicDesktops::permission()
{
    QVariantMap answer{{QStringLiteral("ready"), false}};
    if (m_owners.isEmpty() || m_reloadQueued) return answer;
    const auto restore = properties(QStringLiteral("plasma-restoresession.service"), QStringLiteral("org.freedesktop.systemd1.Service"));
    const auto ksm = properties(QStringLiteral("plasma-ksmserver.service"), QStringLiteral("org.freedesktop.systemd1.Unit"));
    const auto restoreUnit = properties(QStringLiteral("plasma-restoresession.service"), QStringLiteral("org.freedesktop.systemd1.Unit"));
    if (!restorationReady(ksm.value(QStringLiteral("ActiveState")).toString() == QStringLiteral("active"),
                          restoreUnit.value(QStringLiteral("ActiveState")).toString() == QStringLiteral("inactive"),
                          restore.value(QStringLiteral("Result")).toString() == QStringLiteral("success"),
                          restore.value(QStringLiteral("ExecMainStatus"), -1).toInt(),
                          ksm.value(QStringLiteral("ActiveEnterTimestampMonotonic")).toULongLong(),
                          restore.value(QStringLiteral("ExecMainExitTimestampMonotonic")).toULongLong())) return answer;
    QDBusInterface ksmserver(QStringLiteral("org.kde.ksmserver"), QStringLiteral("/KSMServer"), QStringLiteral("org.kde.KSMServerInterface"));
    QDBusReply<bool> shuttingDown = ksmserver.call(QStringLiteral("isShuttingDown"));
    if (!shuttingDown.isValid() || shuttingDown.value()) return answer;
    const int activityState = activityReadiness();
    if (activityState == 0) {
        // Starting a stopped activity launches windows asynchronously too.
        m_preserveCount = qMax(m_preserveCount, int(VirtualDesktopBar::requestDesktopInfoList().size()));
    }
    if (activityState != 1) return answer;
    answer[QStringLiteral("ready")] = true;
    answer[QStringLiteral("preserveCount")] = m_preserveCount;
    answer[QStringLiteral("name")] = m_owners.first().first;
    return answer;
}

void DynamicDesktops::spareCreated()
{
    if (!m_owners.isEmpty() && !m_owners.first().second.isEmpty())
        VirtualDesktopBar::run(m_owners.first().second);
}
