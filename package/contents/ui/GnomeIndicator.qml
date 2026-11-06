// GNOME-style Activities button. Metrics follow GNOME Shell's panel.js/_panel.scss.
import QtQuick
import QtQuick.Layouts

FocusScope {
    id: root
    required property var desktops
    required property QtObject controller
    property bool animations: true
    property bool vertical: false
    readonly property real dotSize: 8
    readonly property real widthMultiplier: desktops.count <= 2 ? 3.625 : desktops.count <= 5 ? 3.25 : 2.75
    property real position: currentIndex()
    property real wheelRemainder: 0
    implicitWidth: vertical ? 32 : dots.implicitWidth + 24
    implicitHeight: vertical ? dots.implicitHeight + 24 : 32
    width: implicitWidth
    height: implicitHeight
    activeFocusOnTab: true
    Accessible.role: Accessible.Button
    Accessible.name: qsTr("Activities")
    Accessible.onPressAction: controller.toggleOverview()
    Keys.onSpacePressed: controller.toggleOverview()
    Keys.onReturnPressed: controller.toggleOverview()

    function currentIndex() {
        for (let i = 0; i < desktops.count; ++i)
            if (desktops.get(i).is_current) return i;
        return 0;
    }
    function updatePosition() { position = currentIndex(); }
    Connections {
        target: root.desktops
        function onDataChanged() { root.updatePosition(); }
        function onCountChanged() { root.updatePosition(); }
    }
    Behavior on position {
        enabled: root.animations
        NumberAnimation { duration: 250; easing.type: Easing.OutCubic }
    }
    function scroll(delta) {
        if (scrollCooldown.running) return;
        wheelRemainder += delta;
        if (Math.abs(wheelRemainder) < 120) return;
        const target = Math.max(0, Math.min(desktops.count - 1,
            currentIndex() + (wheelRemainder > 0 ? -1 : 1)));
        wheelRemainder = 0;
        if (target !== currentIndex()) controller.setCurrentDesktop(target + 1);
        scrollCooldown.start();
    }
    Timer { id: scrollCooldown; interval: 250 }
    Rectangle {
        anchors.fill: parent
        radius: 8
        color: "white"
        opacity: mouse.pressed ? 0.25 : mouse.containsMouse || root.activeFocus ? 0.17 : 0
        Behavior on opacity { NumberAnimation { duration: 150 } }
    }
    GridLayout {
        id: dots
        anchors.centerIn: parent
        flow: root.vertical ? GridLayout.TopToBottom : GridLayout.LeftToRight
        rows: root.vertical ? -1 : 1
        columns: root.vertical ? 1 : -1
        rowSpacing: 5
        columnSpacing: 5
        Repeater {
            model: root.desktops
            delegate: Item {
                id: dot
                required property int index
                readonly property real expansion: Math.max(0, 1 - Math.abs(index - root.position))
                readonly property real length: Math.round(root.dotSize * (1 + (root.widthMultiplier - 1) * expansion))
                implicitWidth: root.vertical ? root.dotSize : length
                implicitHeight: root.vertical ? length : root.dotSize
                Rectangle {
                    anchors.centerIn: parent
                    width: parent.width
                    height: parent.height
                    radius: Math.min(width, height) / 2
                    color: "#fafafa"
                    opacity: 0.5 + 0.5 * dot.expansion
                    scale: 0.75 + 0.25 * dot.expansion
                }
                Component.onCompleted: if (root.animations) appear.start();
                NumberAnimation { id: appear; target: dot; property: "scale"; from: 0; to: 1; duration: 500; easing.type: Easing.OutCubic }
            }
        }
    }
    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton
        onClicked: root.controller.toggleOverview()
        onWheel: wheel => {
            root.scroll(wheel.angleDelta.y !== 0 ? wheel.angleDelta.y : wheel.angleDelta.x);
            wheel.accepted = true;
        }
    }
    DropArea {
        anchors.fill: parent
        onEntered: dragHover.start()
        onExited: dragHover.stop()
        onDropped: dragHover.stop()
    }
    Timer { id: dragHover; interval: 250; onTriggered: root.controller.toggleOverview() }
}
