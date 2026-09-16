"""Run the shipped KWin reconciler against event-driven, isolated KWin doubles."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DYNAMIC = ROOT / 'plugin/dynamic'
HARNESS = r'''
const fs = require('fs'), vm = require('vm'), assert = require('assert');
function signal() {
    const slots = [];
    return {connect(f) {slots.push(f);}, emit(...args) {slots.slice().forEach(f => f(...args));}};
}
function setup(count, occupied, ready=true, floor=1) {
    let queue=[], operations=[], serial=count, permission={ready,preserveCount:floor,name:'Spare'};
    const w = {desktops:Array.from({length:count},(_,i)=>({id:'d'+(i+1)})),
        windows:[], windowAdded:signal(),windowRemoved:signal(),desktopsChanged:signal(),
        currentDesktopChanged:signal(),activitiesChanged:signal(),currentActivityChanged:signal()};
    w.currentDesktop=w.desktops[0];
    function window(desktops, other={}) {
        return Object.assign({desktops:desktops.map(n=>w.desktops[n-1]),onAllDesktops:false,
            managed:true,desktopsChanged:signal(),activitiesChanged:signal(),screen:0,activities:['a']},other);
    }
    w.windows=occupied.map(n=>window([n]));
    w.windowList=()=>w.windows.slice();
    w.createDesktop=(pos,name)=>{assert.equal(pos,w.desktops.length);operations.push('create');
        w.desktops.push({id:'d'+(++serial)});w.desktopsChanged.emit();};
    w.removeDesktop=(d)=>{
        assert.equal(d,w.desktops[w.desktops.length-1]);
        assert(!w.windows.some(win=>!win.deleted&&win.managed!==false&&!win.dock&&!win.desktopWindow&&
            (win.onAllDesktops||win.desktops.includes(d))),'occupied desktop removed');
        operations.push('remove:'+d.id);w.desktops.pop();w.desktopsChanged.emit();};
    const context={workspace:w,callDBus:(service,path,iface,method,...args)=>{
        if(method==='permission')queue.push(()=>args[0](Object.assign({},permission)));
    }};
    vm.createContext(context);vm.runInContext(fs.readFileSync(process.argv[1],'utf8'),context);
    function flush() {let limit=100;while(queue.length){assert(--limit>0,'reconciliation loop');queue.shift()();}}
    return {w,window,operations,permission,context,flush,queue};
}
'''

@unittest.skipUnless(shutil.which('node'), 'Node required for actual reconciler tests')
class DynamicDesktopTests(unittest.TestCase):
    def run_case(self, code):
        result = subprocess.run(['node', '-e', HARNESS + code, str(DYNAMIC/'reconcile.js')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_repeated_launch_occupy_collapse_cycles_with_unmanaged_surface(self):
        self.run_case("""const t=setup(2,[1]);t.flush();
        for(let cycle=0;cycle<20;cycle++) {
            assert.equal(t.w.desktops.length,2);
            t.w.currentDesktop=t.w.desktops[1];t.w.currentDesktopChanged.emit();
            const app=t.window([2]);t.w.windows.push(app);t.w.windowAdded.emit(app);t.flush();
            assert.equal(t.w.desktops.length,3,'launch cycle '+cycle);
            assert.equal(t.operations.filter(x=>x==='create').length,cycle+1);
            t.w.windows=t.w.windows.filter(w=>w!==app);app.deleted=true;t.w.windowRemoved.emit(app);
            t.w.currentDesktop=t.w.desktops[0];t.w.currentDesktopChanged.emit();t.flush();
            assert.equal(t.w.desktops.length,2);
            if(cycle===0) {
                const helper=t.window([],{managed:false,onAllDesktops:true,normalWindow:false});
                t.w.windows.push(helper);t.w.windowAdded.emit(helper);t.flush();
            }
        }
        assert.equal(t.operations.length,40);assert.equal(t.queue.length,0);
        """)

    def test_repeated_move_occupy_collapse_cycles_with_unmanaged_surface(self):
        self.run_case("""const t=setup(2,[1,1]);t.flush();const app=t.w.windows[1];
        for(let cycle=0;cycle<20;cycle++) {
            app.desktops=[t.w.desktops[1]];app.desktopsChanged.emit();t.flush();
            assert.equal(t.w.desktops.length,3,'move cycle '+cycle);
            app.desktops=[t.w.desktops[0]];app.desktopsChanged.emit();t.flush();
            assert.equal(t.w.desktops.length,2);
            if(cycle===0) {
                const helper=t.window([],{managed:false,onAllDesktops:true,normalWindow:false});
                t.w.windows.push(helper);t.w.windowAdded.emit(helper);t.flush();
            }
        }
        assert.equal(t.operations.length,40);assert.equal(t.queue.length,0);
        """)

    def test_unmanaged_surface_does_not_reserve_a_desktop(self):
        self.run_case("""const t=setup(3,[1]);
        t.w.windows.push(t.window([3],{managed:false}));t.flush();
        assert.equal(t.w.desktops.length,2);""")

    def test_managed_sticky_window_still_pauses_after_successful_cycle(self):
        self.run_case("""const t=setup(2,[1]);t.flush();const app=t.w.windows[0];
        app.desktops=[t.w.desktops[1]];app.desktopsChanged.emit();t.flush();
        assert.equal(t.w.desktops.length,3);
        app.desktops=[t.w.desktops[0]];app.desktopsChanged.emit();t.flush();
        assert.equal(t.w.desktops.length,2);
        app.desktops=[];app.onAllDesktops=true;app.desktopsChanged.emit();t.flush();
        assert.equal(t.w.desktops.length,2);assert.equal(t.operations.length,2);
        app.onAllDesktops=false;app.desktops=[t.w.desktops[1]];app.desktopsChanged.emit();t.flush();
        assert.equal(t.w.desktops.length,3);""")

    def test_delayed_desktop_assignment_retriggers_on_membership_signal(self):
        self.run_case("""const t=setup(2,[1]);t.flush();
        const app=t.window([]);t.w.windows.push(app);t.w.windowAdded.emit(app);t.flush();
        assert.equal(t.w.desktops.length,2);
        app.desktops=[t.w.desktops[1]];app.desktopsChanged.emit();t.flush();
        assert.equal(t.w.desktops.length,3);""")

    def test_persisted_three_reconciles_after_startup_without_task_count_change(self):
        self.run_case("""const t=setup(3,[1],false);t.flush();assert.equal(t.w.desktops.length,3);
        t.permission.ready=true;t.context.reconcile();t.flush();assert.equal(t.w.desktops.length,2);
        assert.deepEqual(t.operations,['remove:d3']);""")

    def test_empty_initial_model_does_not_create_desktop(self):
        self.run_case("const t=setup(0,[]);t.flush();assert.deepEqual(t.operations,[]);")

    def test_repeated_initialization_requests_are_coalesced_and_idempotent(self):
        self.run_case("""const t=setup(1,[1]);for(let i=0;i<20;i++)t.context.reconcile();
        assert.equal(t.queue.length,1);t.flush();assert.equal(t.w.desktops.length,2);
        for(let i=0;i<20;i++){t.context.reconcile();t.flush();}assert.deepEqual(t.operations,['create']);""")

    def test_restored_window_arriving_before_permission_is_not_removed(self):
        self.run_case("""const t=setup(3,[1]);const win=t.window([3]);t.w.windows.push(win);
        t.w.windowAdded.emit(win);t.flush();assert.equal(t.w.desktops.length,4);
        assert.deepEqual(t.operations,['create']);""")

    def test_unsafe_restoration_destinations_are_preserved(self):
        self.run_case("""const t=setup(3,[],true,3);t.flush();assert.equal(t.w.desktops.length,3);
        const win=t.window([3]);t.w.windows.push(win);t.w.windowAdded.emit(win);t.flush();
        assert.equal(t.w.desktops.length,4);""")

    def test_other_screen_activity_minimized_and_skip_taskbar_windows_count(self):
        self.run_case("""const t=setup(4,[1,3]);Object.assign(t.w.windows[1],
        {screen:99,activities:['hidden'],minimized:true,skipTaskbar:true,skipPager:true});
        t.flush();assert.equal(t.w.desktops.length,4);assert.deepEqual(t.operations,[]);""")

    def test_membership_change_without_count_change_reconciles(self):
        self.run_case("""const t=setup(2,[1]);t.flush();t.w.windows[0].desktops=[t.w.desktops[1]];
        t.w.windows[0].desktopsChanged.emit();t.flush();assert.equal(t.w.desktops.length,3);
        t.w.windows[0].desktops=[t.w.desktops[0]];t.w.windows[0].desktopsChanged.emit();t.flush();
        assert.equal(t.w.desktops.length,2);""")

    def test_only_trailing_empty_desktops_are_removed(self):
        self.run_case("""const t=setup(6,[1,3]);t.flush();assert.equal(t.w.desktops.length,4);
        assert.deepEqual(t.operations,['remove:d6','remove:d5']);""")

    def test_current_empty_desktop_is_preserved_until_switch(self):
        self.run_case("""const t=setup(3,[1]);t.w.currentDesktop=t.w.desktops[2];t.flush();
        assert.equal(t.w.desktops.length,3);t.w.currentDesktop=t.w.desktops[0];
        t.w.currentDesktopChanged.emit();t.flush();assert.equal(t.w.desktops.length,2);""")

    def test_sticky_application_window_is_conservative_and_does_not_loop(self):
        self.run_case("""const t=setup(3,[1]);t.w.windows[0].onAllDesktops=true;
        t.flush();assert.deepEqual(t.operations,[]);""")

    def test_desktop_panels_do_not_occupy_spare(self):
        self.run_case("""const t=setup(3,[1]);t.w.windows.push(t.window([],{dock:true,onAllDesktops:true}));
        t.w.windows.push(t.window([],{desktopWindow:true,onAllDesktops:true}));t.flush();
        assert.equal(t.w.desktops.length,2);""")

    def test_all_empty_retains_one_desktop(self):
        self.run_case("const t=setup(3,[]);t.flush();assert.equal(t.w.desktops.length,1);")

    def test_unavailable_permission_never_mutates(self):
        self.run_case("const t=setup(3,[],false);t.flush();assert.deepEqual(t.operations,[]);")

class StartupPolicyTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('c++'), 'C++ compiler required')
    def test_actual_startup_guard(self):
        code = r'''
#include "StartupPolicy.hpp"
#include <cassert>
int main() {
 assert(!restorationReady(true,true,true,0,100,0)); // inactive, never started
 assert(!restorationReady(true,true,true,0,100,90)); // previous login
 assert(!restorationReady(true,false,true,0,100,110)); // still restoring
 assert(!restorationReady(false,true,true,0,100,110)); // session stopped
 assert(!restorationReady(true,true,false,0,100,110)); // failure
 assert(!restorationReady(true,true,true,1,100,110)); // failed executable
 assert(!restorationReady(true,true,true,0,0,110)); // unknown session
 assert(restorationReady(true,true,true,0,100,110));
}
'''
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'test.cpp'; source.write_text(code)
            binary = Path(directory)/'test'
            subprocess.run(['c++','-std=c++17','-I',str(DYNAMIC),str(source),'-o',str(binary)],check=True)
            subprocess.run([str(binary)],check=True)

if __name__ == '__main__':
    unittest.main()
