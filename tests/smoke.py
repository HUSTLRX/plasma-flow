"""Load a staged native plugin against fake services on a new private DBus bus."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('module_path', type=Path, help='Staged QML import directory')
parser.add_argument('--qml', type=Path, help='Qt 6 qml executable (auto-detected if omitted)')
args = parser.parse_args()
qml = args.qml
if qml is None:
    qtpaths = shutil.which('qtpaths6') or shutil.which('qtpaths')
    if qtpaths:
        qml = Path(subprocess.check_output([qtpaths, '--query', 'QT_INSTALL_BINS'], text=True).strip())/'qml'
if qml is None or not qml.is_file():
    parser.error('Supply the Qt 6 qml executable with --qml')
if not shutil.which('dbus-run-session'):
    parser.error('dbus-run-session is required')
env = dict(os.environ, PLASMA_FLOW_PRIVATE_BUS='1',
           PLASMA_FLOW_PARENT_BUS=os.environ.get('DBUS_SESSION_BUS_ADDRESS', ''),
           PYTHONDONTWRITEBYTECODE='1')
raise SystemExit(subprocess.call(['dbus-run-session', '--', sys.executable, '-B',
    str(Path(__file__).with_name('probe_dynamic_plugin.py')), str(args.module_path.resolve()),
    '--qml', str(qml.resolve())], env=env))
