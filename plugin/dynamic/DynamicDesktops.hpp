#pragma once

#include <QObject>
#include <QDBusObjectPath>
#include <QMap>
#include <QVariantMap>
#include <QTemporaryFile>

// One manager per Plasma process, one DBus owner per session. Multiple bars do
// not independently create spare desktops or race asynchronous desktop models.
class DynamicDesktops : public QObject {
    Q_OBJECT
    Q_CLASSINFO("D-Bus Interface", "org.kde.plasma.virtualdesktopbar.DynamicDesktops")
public:
    static DynamicDesktops *instance();
    void configure(QObject *owner, bool enabled, const QString &name, const QString &command);
    void forget(QObject *owner);
public Q_SLOTS:
    QVariantMap permission();
    void spareCreated();
private Q_SLOTS:
    void scheduleReload();
    void activityRestoring();
    void jobRemoved(uint id, const QDBusObjectPath &path, const QString &unit, const QString &result);
private:
    explicit DynamicDesktops(QObject *parent);
    void reload();
    QMap<QObject *, QPair<QString, QString>> m_owners;
    QTemporaryFile m_script;
    bool m_registered = false;
    bool m_reloadQueued = false;
    int m_preserveCount = 1;
};
