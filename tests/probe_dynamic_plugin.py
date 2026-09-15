"""Private-bus smoke test for the built plugin. Never connects to the real desktop.
Run through tests/smoke.py; the launcher creates a private bus.
"""
import os
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

parser = argparse.ArgumentParser()
parser.add_argument('module_path', type=Path)
parser.add_argument('--qml', type=Path, required=True)
args = parser.parse_args()
assert os.environ.get('PLASMA_FLOW_PRIVATE_BUS') == '1', 'Use tests/smoke.py'
assert os.environ.get('DBUS_SESSION_BUS_ADDRESS') != os.environ.get('PLASMA_FLOW_PARENT_BUS'), 'Private bus required'
module = args.module_path / 'org/kde/plasma/virtualdesktopbar'
assert (module/'qmldir').is_file() and (module/'libvirtualdesktopbar.so').is_file(), 'Staged plugin missing'
assert args.qml.is_file(), 'Qt 6 qml executable missing'
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
loop = GLib.MainLoop()
objects = []
finished = 0
loads = 0
passed = False

class Manager(dbus.service.Object):
    @dbus.service.method('org.freedesktop.systemd1.Manager', in_signature='s', out_signature='o')
    def GetUnit(self, unit):
        return '/restore' if unit == 'plasma-restoresession.service' else '/ksm'
    @dbus.service.method('org.freedesktop.systemd1.Manager', in_signature='', out_signature='')
    def Subscribe(self):
        pass
    @dbus.service.signal('org.freedesktop.systemd1.Manager', signature='uoss')
    def JobRemoved(self, number, path, unit, result):
        pass

class Unit(dbus.service.Object):
    @dbus.service.method('org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        if self.__dbus_object_path__ == '/ksm':
            return {'ActiveState':'active','ActiveEnterTimestampMonotonic':dbus.UInt64(100)}
        if interface.endswith('.Unit'):
            return {'ActiveState':'inactive'}
        return {'Result':'success','ExecMainStatus':dbus.Int32(0),'ExecMainExitTimestampMonotonic':dbus.UInt64(finished)}

class Ksm(dbus.service.Object):
    @dbus.service.method('org.kde.KSMServerInterface', in_signature='', out_signature='b')
    def isShuttingDown(self):
        return False

class Activities(dbus.service.Object):
    @dbus.service.method('org.kde.ActivityManager.Activities', in_signature='', out_signature='a(ssssi)')
    def ListActivitiesWithInformation(self):
        return [('activity1','One','','',2),('activity2','Two','','',2)]

class Scripting(dbus.service.Object):
    @dbus.service.method('org.kde.kwin.Scripting', in_signature='s', out_signature='b')
    def unloadScript(self, name):
        return True
    @dbus.service.method('org.kde.kwin.Scripting', in_signature='ss', out_signature='i')
    def loadScript(self, path, name):
        global loads
        assert 'workspace.windowList()' in Path(path).read_text()
        loads += 1
        return 1

class Script(dbus.service.Object):
    @dbus.service.method('org.kde.kwin.Script', in_signature='', out_signature='')
    def run(self):
        GLib.idle_add(check)

names = [dbus.service.BusName(n,bus) for n in ['org.freedesktop.systemd1','org.kde.ksmserver','org.kde.ActivityManager','org.kde.KWin']]
manager=Manager(bus,'/org/freedesktop/systemd1');objects.append(manager)
objects += [Unit(bus,'/restore'),Unit(bus,'/ksm'),Ksm(bus,'/KSMServer'),Activities(bus,'/ActivityManager/Activities'),Scripting(bus,'/Scripting'),Script(bus,'/Scripting/Script1')]

def fail(error):
    print(error,file=sys.stderr);loop.quit()

def result(value):
    global finished,passed
    if not finished:
        assert not value['ready'], value
        finished = 110
        manager.JobRemoved(1,'/job/1','plasma-restoresession.service','done')
    else:
        assert value['ready'], value
        assert value['preserveCount']==1, value
        assert value['name']=='Spare', value
        assert loads==2, loads  # one initial load, one lifecycle-triggered load
        passed=True;loop.quit()

def check():
    bus.call_async('org.kde.plasma.virtualdesktopbar.dynamic','/DynamicDesktops',
                   'org.kde.plasma.virtualdesktopbar.DynamicDesktops','permission','',(),result,fail)
    return False

with tempfile.TemporaryDirectory() as directory:
    qml=Path(directory)/'probe.qml'
    qml.write_text('''import QtQuick
import org.kde.plasma.virtualdesktopbar 1.0
Item {
 VirtualDesktopBar { id: a }
 VirtualDesktopBar { id: b }
 Component.onCompleted: {
  a.configureDynamicDesktops(true,"Spare","");
  a.configureDynamicDesktops(true,"Spare","");
  b.configureDynamicDesktops(true,"Spare","");
 }
}''')
    env=dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',
             QML_IMPORT_PATH=str(args.module_path.resolve()), QML2_IMPORT_PATH='',
             XDG_CONFIG_HOME=directory, XDG_CACHE_HOME=directory+'/cache',
             XDG_DATA_HOME=directory+'/data', XDG_STATE_HOME=directory+'/state',
             XDG_RUNTIME_DIR=directory)
    # Never let user-level QML modules or session configuration satisfy the test.
    process=subprocess.Popen([str(args.qml),str(qml)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    GLib.timeout_add_seconds(15,lambda:loop.quit())
    try:
        loop.run()
    finally:
        process.terminate()
        out,err=process.communicate(timeout=5)
    if not passed:
        print(out,err,file=sys.stderr)
        raise SystemExit('Plugin probe failed')
print('Built plugin: resource load, duplicate owners, startup guard, DBus decoding and lifecycle retry passed')
