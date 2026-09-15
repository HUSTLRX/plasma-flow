# Plasma Flow 0.1.0 — Initial preview

**Dynamic workspaces for KDE Plasma.**

Plasma Flow is an independent community project derived from
[lenonk/virtual-desktop-bar](https://github.com/lenonk/virtual-desktop-bar),
not an official KDE project. Upstream history, authorship and GPL version 3 license
are retained.

This first preview combines label-free workspace indicators with native dynamic
workspace reconciliation. None-mode width, height, spacing and radius are
configurable. Startup, repeated requests and queued desktop initialization are
handled explicitly; global occupancy checks include other screens and activities.

When safe, dynamic mode keeps one trailing empty spare. Existing restoration
destinations, current workspaces and sticky windows receive conservative
protection, so extra empty workspaces may remain while safety is uncertain.

The implementation has automated reconciliation/geometry/startup coverage and a
private-DBus native QML smoke test. The validated environment is Fedora 44, Plasma
6.7.5, Frameworks 6.30, Wayland. Other combinations are not yet certified; a full
logout/login regression remains pending.

This is a preview (`0.1.0`), not the proposed stable `1.0.0`. Existing internal
plugin, DBus and configuration IDs are preserved for compatibility: this replaces
Virtual Desktop Bar rather than installing alongside it. Build/install both the
native plugin and QML; retain your existing widgets and settings when updating.

See the README for installation and known limitations. No prebuilt binaries or
screenshots are included in this proposed release.
