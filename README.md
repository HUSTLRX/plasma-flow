# Plasma Flow

**Dynamic workspaces for KDE Plasma.**

Plasma Flow is a configurable workspace bar for KDE Plasma, with compact
label-free indicators and optional dynamic workspace management. It is an
**independent community project**, derived from
[lenonk/virtual-desktop-bar](https://github.com/lenonk/virtual-desktop-bar),
and is **not an official KDE project**.

## Features

- Switch workspaces by clicking or scrolling; retain upstream label, color,
  tooltip and indicator-style options.
- Enable dynamic workspaces to keep **exactly one trailing empty spare when
  reconciliation is safe**. Occupying the last workspace adds another spare;
  unnecessary trailing empty workspaces are removed.
- Use **None** as the label style for indicators without workspace text.
- Configure None-mode indicator width, height, spacing and corner radius.
- Reconcile at startup and on window/desktop changes, with duplicate requests
  coalesced and duplicate initialization events handled safely.
- Determine occupancy across screens and activities, independently of display
  filtering, including minimized and skip-taskbar windows.

Dynamic management preserves occupied workspaces, interior gaps and the current
workspace. Session-restoration reservations and sticky windows can leave extra
empty workspaces. This is a safety choice, not a guarantee of immediate trimming
in every session; see [how reconciliation works](docs/reconciliation.md).

## Screenshots

| Planned illustration | Status |
| --- | --- |
| Label-free workspace bar | Placeholder — not yet provided |
| None-mode sizing controls | Placeholder — not yet provided |
| Dynamic workspace creation and trimming | Placeholder — not yet provided |

No screenshots are included in this source tree.

## Compatibility and dependencies

The substantiated environment for this implementation is **Fedora 44, KDE Plasma
6.7.5, KDE Frameworks 6.30, and Wayland**. These are validated versions, not claimed
minimum requirements. Plasma 6 / Wayland is the focus; other distributions,
versions, X11, and physical multi-monitor arrangements need independent validation.

Building requires:

- CMake (the build declares 3.27), a C++23 compiler, and Ninja or Make;
- Qt 6 development components: Core, DBus, Qml and Widgets;
- Extra CMake Modules and KDE Frameworks development packages: I18n, Service,
  WindowSystem, plus their transitive dependencies;
- Plasma, Plasma Activities and KWin development packages.

The inherited CMake checks accept Qt 6.4 / Frameworks 6.0, but that does **not**
establish runtime compatibility with those versions. KWin's development API must
match the installed compositor. The dynamic controller currently needs the
systemd user-session restoration service, KSMServer, KWin scripting, and the
supported Activities DBus API. It leaves desktops alone if readiness is unknown.

Tests additionally need Python 3, Node.js and a C++ compiler. The native smoke test
needs Qt 6's `qml` executable, `dbus-run-session`, Python `dbus` and PyGObject/GLib.
See [development and testing](docs/development.md).

## Build

```sh
git clone https://github.com/HUSTLRX/plasma-flow.git
cd plasma-flow
cmake -S . -B ../plasma-flow-build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
cmake --build ../plasma-flow-build -j2
ctest --test-dir ../plasma-flow-build --output-on-failure
```

Use `-DBUILD_TESTING=OFF` for a build without the Python test dependency. Building
and running unit tests do not install the widget or change the desktop.

## Install

Plasma Flow has a **native plugin as well as QML**. Installing only the widget
package with a package-manager command for plasmoids is insufficient.

```sh
sudo cmake --install ../plasma-flow-build
```

Install only while Plasma is stopped, normally after logging out and switching to
a text console. This avoids overwriting a native library mapped into a running
shell. For a staged package instead of a live install:

```sh
DESTDIR=/tmp/plasma-flow-stage cmake --install ../plasma-flow-build
```

Log in again, then add **Plasma Flow** from Plasma's widget picker. Existing Virtual
Desktop Bar instances use the same internal identity and do not need recreating.
The two projects therefore **cannot be installed side by side**: Plasma Flow
replaces Virtual Desktop Bar's package and native module. If a distribution
package owns these paths, resolve that package conflict before manual installation.

## Update

For updates from the project's main branch:

```sh
git switch main
git pull --ff-only origin main
cmake -S . -B ../plasma-flow-build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
cmake --build ../plasma-flow-build -j2
ctest --test-dir ../plasma-flow-build --output-on-failure
```

Alternatively, check out a reviewed release tag before rebuilding. Install both
QML and native code together. Stop Plasma before installation as
above, then log back in. Existing widget settings are retained; do not delete or
recreate panels. A new library on disk does not replace code already loaded by a
running shell.

Before changing versions, retain the previous source/build or distribution package
for rollback. Do not replace only one half of the QML/native pair.

## Uninstall

Remove the widget from any panels where you no longer want it, then log out before
removing the native files. From a text console, review the build's installation
manifest and remove exactly those files:

```sh
cat ../plasma-flow-build/install_manifest.txt
sudo xargs -d '\n' rm -- < ../plasma-flow-build/install_manifest.txt
```

Use the manifest from the actual system installation, not a staged installation.
Do not use this command for a distribution-managed package; uninstall that package
instead. This leaves personal Plasma configuration intact and may leave empty
installation directories. To return to upstream Virtual Desktop Bar, install its
matching QML/native pair before your next login.

## Configuration

Open the widget's settings:

- **Appearance:** choose label style **None** to remove text. Adjust None-mode
  width, height, spacing and radius; choose the indicator style and colors.
  Edge/side-line styles still use line thickness on their thin axis. Radius is
  limited to half the indicator's dimensions.
- **Behavior:** enable dynamic desktops, configure wheel navigation, and optionally
  filter the displayed window information by screen. That filter never limits the
  occupancy check used to remove workspaces.
- The optional new-desktop command retains upstream behavior. Leave it empty if
  no command is needed.

Internal settings remain `DynamicDesktops`, `LabelStyle`, `NoneIndicatorWidth`,
`NoneIndicatorHeight`, `NoneButtonSpacing` and `NoneIndicatorRadius`. Existing
settings are reused; the project does not impose a saved desktop count.

## Known limitations and restoration safety

- KDE reports session applications as launched before every restored window
  necessarily exists. Potential restoration destinations stay protected for the
  controller's lifetime; extra empty workspaces may remain in such sessions.
- Sticky application windows pause dynamic mutations. An empty current trailing
  workspace is retained until the user switches away. Interior holes are retained.
- Unknown/failed startup state, shutdown, and unavailable or unsupported activity
  APIs prevent changes. Non-systemd sessions do not currently reconcile dynamically.
- Application-managed restoration outside KDE's saved session records cannot be
  inferred from an empty window list.
- Vertical-panel behavior and physical multi-monitor combinations need broader
  testing. Automated cross-screen/activity tests are not hardware certification.
- The maintainer reports a successful real logout/login regression on Fedora 44,
  Plasma 6.7.5, Frameworks 6.30, Wayland: one occupied desktop plus one trailing
  empty spare, with two indicators and no recurrence of the startup bug. This
  single-system result does not establish broader compatibility. `0.1.1` remains
  an early release with these compatibility limitations.

See [reconciliation and startup safety](docs/reconciliation.md) for the exact
policy and [differences from upstream](docs/upstream.md) for compatibility choices.

## Development, attribution and license

Run `python3 -B -m unittest discover -s tests -v` for the standalone regression
suite; no surrounding desktop-configuration repository is needed. Native smoke
checks use fake services on a private DBus bus. See [development.md](docs/development.md)
for staging, testing and validation limits.

Plasma Flow retains the Git history, authorship and copyright notices of
**Virtual Desktop Bar**, including the upstream authors **Lenon Kitchens** and
**wsdfhjxc**. The upstream repository is
[lenonk/virtual-desktop-bar](https://github.com/lenonk/virtual-desktop-bar).
Its original license text is preserved unchanged in [LICENSE](LICENSE), the
GNU General Public License, version 3. Earlier release history is preserved in
[the upstream changelog](docs/upstream-changelog.md) and Git history.
