# Origin and compatibility

Upstream: https://github.com/lenonk/virtual-desktop-bar.git

Base: `45245af650cde38050eba6e40c758c2136efd55b`

The standalone branch descends directly from that upstream commit. It imports all
54 files from the reviewed authoritative implementation, rather than taking local
modifications from an older upstream working checkout. The older checkout has the
indicator edits but differs in ten files belonging to native reconciliation and
initialization. No files from it are used as modification sources.

## Changes from the base

Fifteen added/modified implementation files comprise the functional import:

- `main.xml`, `DesktopButton.qml`, `IndicatorGeometry.js`, `AppearanceTab.qml` and
  `BehaviorTab.qml`: label-free dimensions, spacing/radius controls and layout.
- `Container.qml` and `common/Backend.qml`: native dynamic settings and initialization
  handling without duplicate desktop indicators.
- `plugin/CMakeLists.txt`, `VirtualDesktopBar.cpp` and `VirtualDesktopBar.hpp`:
  native controller integration.
- All five `plugin/dynamic/` files: controller, readiness predicate, embedded KWin
  script and resources.

`source-provenance.json` records the upstream base and hashes for the 49 files
preserved byte-for-byte after branding. Intentional adaptations are the README,
changelog, root CMake project/test setup, public package metadata and Support tab
wording. The support link is explicitly attributed to the original upstream author.
Production reconciliation and indicator code remain unchanged by standalone
preparation. Tests and documentation are standalone additions.

## Stable internal identity

Public name: **Plasma Flow**. Repository: **plasma-flow**.

The following are intentionally retained:

- Plasma package ID `org.kde.plasma.virtualdesktopbar`;
- QML import `org.kde.plasma.virtualdesktopbar 1.0` and type `VirtualDesktopBar`;
- native target/file `virtualdesktopbar` / `libvirtualdesktopbar.so`;
- existing namespace/class names, icon IDs and configuration keys;
- DBus service `org.kde.plasma.virtualdesktopbar.dynamic`, object
  `/DynamicDesktops`, interface `org.kde.plasma.virtualdesktopbar.DynamicDesktops`;
- KWin script name `virtualdesktopbar-dynamic-desktops`.

Changing these would require a migration for installed widgets and settings.
Plasma Flow replaces the upstream installation and cannot coexist with it under
these identities. Its independent `0.1.0` version is not an upstream-version
upgrade promise; downstream packagers must account for the new project identity.

## Authorship and source hygiene

Upstream authors, commit history, copyright notices and GPL version 3 license text
are retained. Plasma Flow is an independent community derivative, not an official
KDE project. New commits use the public maintainer identity with a noreply address.

The current source tree excludes screenshots, IDE metadata, build products and
machine state. Preserving upstream history also preserves **upstream's historical**
screenshot/IDE blobs and original author metadata. Those are absent from the
current tree; history has not been rewritten. No personal desktop captures,
configuration, identifiers, logs or backups were imported into the new commits.
