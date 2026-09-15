# Changelog

## 0.1.0 — proposed initial preview, unreleased

### Added

- Plasma Flow public identity: Dynamic workspaces for KDE Plasma.
- Label-free / None-mode indicators with configurable width, height, spacing and
  corner radius, including dimension-aware radius clamping.
- Standalone regression tests and isolated native QML/DBus smoke testing.
- Build, installation, update, removal and restoration-safety documentation.

### Fixed

- Startup reconciliation no longer creates spares from an uninitialized QML model.
- Queued desktop-created events no longer append duplicate initial indicators.
- Shared native management coalesces repeated requests and responds to lifecycle,
  desktop changes and window-membership events.
- Occupancy considers windows across screens/activities independently of display
  filtering; only unnecessary trailing empty workspaces are trimmed.

### Compatibility and limitations

- Existing internal package/module/DBus/configuration identities are preserved.
- Validated environment: Fedora 44, Plasma 6.7.5, Frameworks 6.30, Wayland. These are
  tested versions, not supported minimums.
- Potential restoration destinations, current workspaces and sticky windows are
  protected. Exact one-spare convergence can be deferred conservatively.
- Real logout/login regression and broader hardware/version testing remain open.

Upstream release notes remain in [docs/upstream-changelog.md](docs/upstream-changelog.md).
