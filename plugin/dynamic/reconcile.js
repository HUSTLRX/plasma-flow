// Runs inside KWin: window membership is never filtered by screen/activity.
// The DBus callback is asynchronous, so always inspect a NEW snapshot afterwards.
var pending = false;
var dirty = false;
var applying = false;

function reconcile() {
    dirty = true;
    if (pending || applying) return;
    pending = true;
    callDBus("org.kde.plasma.virtualdesktopbar.dynamic", "/DynamicDesktops",
             "org.kde.plasma.virtualdesktopbar.DynamicDesktops", "permission", function (permission) {
        pending = false;
        dirty = false;
        if (!permission || !permission.ready) return;
        applying = true;
        try {
            var desktops = workspace.desktops;
            if (!desktops.length) return;
            var occupied = {};
            var windows = workspace.windowList();
            for (var i = 0; i < windows.length; ++i) {
                var window = windows[i];
                // windowList() also contains unmanaged X11/override-redirect
                // surfaces. Their empty desktop list is not a sticky application;
                // treating it as one vetoes every later create/collapse cycle.
                if (window.deleted || window.managed === false || window.desktopWindow || window.dock) continue;
                // Sticky application windows must not cause endless spare creation.
                // Conservatively leave the layout alone while any are present.
                if (window.onAllDesktops || !window.desktops.length) return;
                for (var j = 0; j < window.desktops.length; ++j)
                    occupied[window.desktops[j].id] = true;
            }
            var lastOccupied = -1;
            for (var k = 0; k < desktops.length; ++k)
                if (occupied[desktops[k].id]) lastOccupied = k;
            var wanted = Math.max(1, lastOccupied + 2, permission.preserveCount);
            if (desktops.length < wanted) {
                var previousCount = desktops.length;
                workspace.createDesktop(previousCount, permission.name);
                if (workspace.desktops.length > previousCount)
                    callDBus("org.kde.plasma.virtualdesktopbar.dynamic", "/DynamicDesktops",
                             "org.kde.plasma.virtualdesktopbar.DynamicDesktops", "spareCreated");
            } else if (desktops.length > wanted) {
                var last = desktops[desktops.length - 1];
                // Never move the user off their current desktop. Switching away
                // emits currentDesktopChanged and completes deferred trimming.
                if (last.id !== workspace.currentDesktop.id && !occupied[last.id])
                    workspace.removeDesktop(last);
            }
        } finally {
            applying = false;
            if (dirty) reconcile();
        }
    });
}

function watchWindow(window) {
    window.desktopsChanged.connect(reconcile);
    if (window.activitiesChanged) window.activitiesChanged.connect(reconcile);
}
workspace.windowList().forEach(watchWindow);
workspace.windowAdded.connect(function (window) { watchWindow(window); reconcile(); });
workspace.windowRemoved.connect(reconcile);
workspace.desktopsChanged.connect(reconcile);
workspace.currentDesktopChanged.connect(reconcile);
workspace.activitiesChanged.connect(reconcile);
workspace.currentActivityChanged.connect(reconcile);
reconcile();
