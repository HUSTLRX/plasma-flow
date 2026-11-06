import QtQuick
import QtTest
import "../../package/contents/ui" as Flow
TestCase {
    name: "GnomeIndicator"
    when: windowShown
    width: 400; height: 100
    visible: true
    ListModel { id: desktops }
    QtObject {
        id: backend
        property int toggles: 0
        property int selected: 0
        function toggleOverview() { toggles++; }
        function setCurrentDesktop(number) { selected = number; }
    }
    Flow.GnomeIndicator { id: indicator; desktops: desktops; controller: backend; animations: false }
    function init() {
        wait(260);
        desktops.clear();
        desktops.append({is_current:true});
        desktops.append({is_current:false});
        indicator.updatePosition();
        indicator.wheelRemainder = 0;
        backend.toggles = 0; backend.selected = 0;
    }
    function test_geometry() {
        compare(indicator.widthMultiplier, 3.625);
        tryCompare(indicator, "implicitWidth", 66); // 29px pill + 8px dot slot + 5px gap + 24px padding
        for (let i=0; i<4; i++) desktops.append({is_current:false});
        compare(indicator.widthMultiplier, 2.75);
    }
    function test_click_opens_overview() {
        mouseClick(indicator, indicator.width/2, indicator.height/2);
        compare(backend.toggles, 1);
        compare(backend.selected, 0);
    }
    function test_keyboard() {
        indicator.forceActiveFocus();
        keyClick(Qt.Key_Space);
        compare(backend.toggles, 1);
    }
    function test_scroll_bounds_and_direction() {
        indicator.scroll(120);
        compare(backend.selected, 0);
        wait(260);
        indicator.scroll(-120);
        compare(backend.selected, 2);
    }
    function test_current_changes() {
        desktops.setProperty(0,"is_current",false);
        desktops.setProperty(1,"is_current",true);
        compare(indicator.position, 1);
    }
}
