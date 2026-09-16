# Plasma Flow 0.1.1

Fixed dynamic workspace reconciliation becoming blocked after successful
create/collapse cycles. Explicitly unmanaged KWin surfaces with empty desktop
membership are no longer mistaken for managed sticky applications. Managed
sticky applications retain their conservative protection.

Added repeated launch/collapse and move/collapse regression coverage. No polling,
recurring timers, or arbitrary delays were introduced. Startup/restoration
safeguards, widget settings, and internal plugin identities remain unchanged.

Validation: 24 tests, CTest 2/2, Release build, and isolated native smoke test
passed. Regression coverage exercised 20 repeated launch cycles and 20 repeated
move cycles; bounded live testing passed three cycles of each without restarting
the session. Broader platform compatibility remains subject to the documented
limitations.

Source-only bugfix release following v0.1.0. Upstream history, attribution, and
GPL licensing are preserved. GitHub-generated source archives are sufficient;
no machine-specific binaries or diagnostic artifacts are attached.
