# Dynamic workspaces and startup safety

When the state is safe to reconcile, the target is one empty workspace after the
highest occupied workspace. With no application windows, one workspace remains.
Only trailing empty workspaces are removed. Empty interior workspaces keep their
positions, and the user is not switched away from a current trailing workspace.

The native controller owns a single KWin script per session through a DBus service
name. Multiple widget instances in a Plasma process share that controller. QML
supplies settings but does not decide global workspace occupancy.

The script listens to desktop changes, window addition/removal, window desktop
membership, and activity/current-desktop changes. It coalesces pending requests,
then inspects a fresh `workspace.windowList()` after the authorization callback.
Checking membership and removing the empty tail happen in the same KWin callback.
Only one workspace is changed per pass, followed by another pass when the desktop
list changes. This avoids acting repeatedly on an out-of-date QML ListModel.

All screens and activities contribute to occupancy. Minimized, skip-pager and
skip-taskbar application windows count. Desktop backgrounds and panels do not.
Sticky application windows pause mutation rather than making every new spare
appear occupied and causing unbounded desktop creation.

## Startup boundary

Authorization requires a successful `plasma-restoresession.service` completion
newer than the current KSMServer startup, a running session, no shutdown, and a
ready Activities service. An inactive service that has never run is not ready;
neither is a successful completion retained from an earlier login. A systemd
`JobRemoved` event prompts another reconciliation without requiring a task-count
change. The zero-duration Qt timer only coalesces event-loop work; it is not a
readiness delay or polling loop.

KSMServer completion means applications have been launched, not that every restored
window exists. The public KWin session/scripting APIs used here do not provide a
reliable per-application restoration-complete signal. Consequently:

- Saved KSMServer/legacy application state reserves the initial desktop range for
  the controller lifetime. Desktops beyond that range still grow and shrink.
- Stopped/starting activities can reserve potential restoration destinations too.
- Unknown activity signatures, service failures and shutdown fail closed.
- No timeout releases reservations. Extra empty desktops can remain when safe
  convergence cannot be established. Independent application restoration outside
  KDE's session records is not detectable from the current window list.

The current Activities reply signature is `a(ssssi)` with running state `2`.
These assumptions are explicit compatibility boundaries, not claims about all
Plasma 6 versions or future APIs.

## Startup defects addressed

The former QML completion handler could see an empty initial desktop list and add
a desktop. Desktop initialization itself did not trigger another reconciliation;
only changes to a mutable, filtered task count did. Repeated calls could also
observe the list before a previous creation was reflected in it.

A separate display race appended a `desktopCreated` notification whose UUID was
already in the startup snapshot. The backend now refreshes that snapshot on a
creation notification, preventing duplicate indicators from queued initial events.

Tests cover a persisted third desktop, readiness transitions without task-count
changes, idempotence, delayed windows, membership changes, global occupancy,
protected restoration destinations and conservative exceptions. A real logout/login
regression still needs confirmation; simulated startup and a runtime trim check do
not substitute for it.
