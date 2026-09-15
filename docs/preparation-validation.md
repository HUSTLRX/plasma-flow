# Standalone preparation validation

Validated on Fedora 44 with Plasma 6.7.5, Frameworks 6.30 and Wayland. Build/test
tools included CMake 4.3, Python 3.14 and Node.js 24. These observations do not define
minimum supported versions.

## Provenance and scope

- Upstream HEAD and import base both equal `45245af650cde38050eba6e40c758c2136efd55b`.
- Imported all 54 authoritative files exactly in commit `d46166e`.
- The older working checkout differs from the authoritative source in ten native
  reconciliation/initialization files; none of its modifications were used.
- All 15 functional differences from the upstream base are retained. After public
  preparation, 49 imported files remain byte-identical. The five reviewed
  adaptations are documentation, root CMake naming/test setup, public metadata and
  Support-tab wording; no reconciliation or indicator behavior was changed.
- Original authors, complete upstream ancestry and LICENSE were preserved. LICENSE
  is byte-identical to upstream. Source hashes are in `source-provenance.json`.
- Both reference working directories were checked against their pre-preparation
  file hashes and remained unchanged. No system installation or desktop changes
  were made during standalone preparation.

## Build and tests

- A completely fresh Release build from this standalone directory succeeded.
- All 19 standalone unit/regression tests passed, with zero skips.
- Both CTest entries passed: AppStream validation and the regression suite.
- Staged native-plugin QML/DBus smoke testing passed.
- Native dependency/symbol resolution found no missing libraries or symbols.
- A separate clone with independent Git objects completed another fresh Release
  build, both CTest entries and the native smoke test while both reference
  directories and the original standalone directory were inaccessible in a mount
  namespace.
- The smoke test also passed with the system-installed copy of this widget hidden,
  verifying use of the staged module instead of a fallback to an installed copy.

Builds, stages and raw test output were outside the source tree. Tests used fake
KWin/systemd/KSMServer/Activities services on a private DBus session.

## Source-tree privacy audit

No personal filesystem paths, machine usernames, real desktop/activity UUIDs,
personal screenshots, configuration files, logs, backups, build products, IDE
metadata or runtime state were found in the tracked tree. Public project/upstream
identities and copyright attribution remain intentionally. Screenshots are text
placeholders only; SVG application icons are inherited source assets.

Retaining upstream ancestry retains its historical screenshot/IDE blobs and author
metadata. They were removed from the branch tip, not erased from upstream history.
New commits introduce none of those historical assets or any personal machine data.

## Remaining release limits

The maintainer subsequently reported successful real logout/login startup
validation on Fedora 44, Plasma 6.7.5, Frameworks 6.30, Wayland. After login, the
system returned to one occupied desktop plus exactly one trailing empty spare
and two workspace indicators; the previous startup bug did not recur. This was
a real-world test reported outside the automated test session, not another
simulated test.

Protected restoration ranges can still retain extra empty workspaces. Broader
Plasma-version, distribution, hardware, multi-monitor and activity coverage remains
limited. The single-system result does not expand compatibility claims; **0.1.0**
remains an initial preview rather than a stable 1.0.0 release. No GitHub repository,
push, project tag or release was created during the original preparation phase.
