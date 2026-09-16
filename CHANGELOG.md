# Changelog

## 0.1.1 — Dynamic workspace reconciliation fix

### Fixed

- Ignore unmanaged KWin surfaces when computing workspace occupancy. Their empty
  desktop membership previously triggered the sticky-application safeguard and
  blocked subsequent spare creation, including after successful create/collapse
  cycles. Managed sticky applications retain their conservative protection.
- Add repeated launch and move regression tests, each exercising 20 cycles.

## 0.1.0 — Initial preview

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
- The maintainer reports that the real logout/login regression passed on the
  validated environment: one occupied desktop, one trailing empty spare, and two
  indicators. The startup bug did not recur.
- Broader Plasma-version, distribution, hardware, monitor and activity testing
  remains limited; this single-system result does not expand compatibility claims.

Upstream release notes remain in [docs/upstream-changelog.md](docs/upstream-changelog.md).
