# Development and testing

This repository contains its complete widget, native plugin and tests. No external
working checkout, desktop configuration project, installed copy of this widget,
or personal configuration is required to build and test it.

## Release build and unit tests

```sh
cmake -S . -B ../plasma-flow-build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
cmake --build ../plasma-flow-build -j2
ctest --test-dir ../plasma-flow-build --output-on-failure
# Equivalent direct suite:
python3 -B -m unittest discover -s tests -v
```

Python 3, Node.js and a C++ compiler are needed to run all tests. A missing Node.js
or compiler may skip individual tests; a complete validation must report zero
skips. The reconciler tests execute the shipped JavaScript with event-driven KWin
doubles. Startup tests compile the actual C++ readiness predicate. Geometry tests
execute the indicator module. Source integrity tests protect the authoritative
import and compatibility-sensitive package identity.

## Native plugin smoke test

Stage into a new temporary directory; this does not install into the live system:

```sh
DESTDIR=/tmp/plasma-flow-stage cmake --install ../plasma-flow-build
python3 -B tests/smoke.py \
  /tmp/plasma-flow-stage/usr/lib64/qt6/qml
```

The staged QML directory above is the Fedora layout. Use the directory actually
reported by `cmake --install` on another platform. Supply `--qml /path/to/qt6/bin/qml`
if Qt 6's executable cannot be discovered using `qtpaths6`/`qtpaths`.

The launcher always creates a new DBus session, then starts the staged module in
Qt's offscreen mode with temporary configuration/data/cache directories. It fakes
KWin, systemd, KSMServer and Activities; it does not connect to the live desktop.
Python DBus bindings and PyGObject/GLib must be installed for that interpreter.

This validates compiled-module/resource loading, multiple widget owners,
idempotent configuration, startup refusal, real Qt DBus decoding and readiness
retry. It does not run a real compositor or prove a complete login sequence.

## Reproducibility and contributions

Use an independent clone for release validation, build outside the source tree,
and run both the unit suite and native smoke test. Inspect `git status` afterwards.
Do not commit generated files, captures, personal config, logs or IDE state.

`docs/source-provenance.json` records the initial implementation hashes. If changing
protected implementation code, update its regression tests and explicitly review
and update the relevant hashes in the same change; the file is an integrity record,
not a dependency on a missing source repository.

A real logout/login regression has passed on the validated environment, as
reported by the maintainer. Before a stable 1.0 release, extend coverage with and without saved
applications, delayed restoration, multiple activities, physical monitors and
sticky windows. Record versions and outcomes, not users' raw configs or window
identifiers. Broader compatibility claims require corresponding evidence.

See [preparation-validation.md](preparation-validation.md) for the initial standalone
build, test, source-comparison and privacy audit results.
