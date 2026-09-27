(function AEHotLoaderPanel(thisObj) {
    var PRODUCT = "AE Hot Loader";
    var BRIDGE_FOLDER_NAME = "AE Hot Loader";
    var REQUEST_FILE_NAME = "request.txt";
    var RESPONSE_FILE_NAME = "response.txt";

    function bridgeFolder() {
        var folder = new Folder(Folder.userData.fsName + "/" + BRIDGE_FOLDER_NAME + "/bridge");
        if (!folder.exists) {
            folder.create();
        }
        return folder;
    }

    function parseKeyValue(text) {
        var out = {};
        var lines = text.split(/\r?\n/);
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            var p = line.indexOf("=");
            if (p > 0) {
                out[line.substring(0, p)] = line.substring(p + 1);
            }
        }
        return out;
    }

    function readText(file) {
        if (!file.exists || !file.open("r")) {
            return null;
        }
        var text = file.read();
        file.close();
        return text;
    }

    function writeRequest(requestId) {
        var folder = bridgeFolder();
        var response = new File(folder.fsName + "/" + RESPONSE_FILE_NAME);
        if (response.exists) {
            try { response.remove(); } catch (e) {}
        }

        var request = new File(folder.fsName + "/" + REQUEST_FILE_NAME);
        if (request.exists) {
            try { request.remove(); } catch (e) {}
        }

        var temp = new File(folder.fsName + "/request.tmp");
        if (temp.exists) {
            try { temp.remove(); } catch (e) {}
        }

        if (!temp.open("w")) {
            throw new Error("Cannot open bridge request file.");
        }

        temp.lineFeed = "Unix";
        temp.write(
            "version=1\n" +
            "command=reload_plugins\n" +
            "request_id=" + requestId + "\n" +
            "timestamp=" + (new Date()).getTime() + "\n"
        );
        temp.close();

        if (!temp.rename(REQUEST_FILE_NAME)) {
            try { temp.remove(); } catch (e) {}
            throw new Error("Cannot publish bridge request.");
        }
    }


    $.global.AEHotLoader_pollResponse = function () {
        var state = $.global.AEHotLoader_state;
        if (!state || !state.waiting) {
            return;
        }

        var folder = bridgeFolder();
        var response = new File(folder.fsName + "/" + RESPONSE_FILE_NAME);

        if (response.exists) {
            var text = readText(response);
            if (text !== null) {
                var data = parseKeyValue(text);
                if (data.request_id === state.requestId) {
                    state.waiting = false;
                    state.button.enabled = true;
                    state.status.text = data.message || data.status || "Done";
                    try { response.remove(); } catch (e) {}
                    return;
                }
            }
        }

        var elapsed = (new Date()).getTime() - state.startedAt;
        if (elapsed > 30000) {
            state.waiting = false;
            state.button.enabled = true;
            state.status.text = "Native helper did not answer.";
            return;
        }

        app.scheduleTask("AEHotLoader_pollResponse()", 250, false);
    };

    function buildUI(thisObj) {
        var panel = (thisObj instanceof Panel)
            ? thisObj
            : new Window("palette", PRODUCT, undefined, { resizeable: true });

        panel.orientation = "column";
        panel.alignChildren = ["fill", "top"];
        panel.spacing = 8;
        panel.margins = 10;

        var reloadButton = panel.add("button", undefined, "Reload Plugins");
        reloadButton.preferredSize.height = 30;

        var status = panel.add("statictext", undefined, "Ready");
        status.alignment = ["fill", "top"];

        $.global.AEHotLoader_state = {
            button: reloadButton,
            status: status,
            requestId: "",
            startedAt: 0,
            waiting: false
        };

        reloadButton.onClick = function () {
            try {
                var state = $.global.AEHotLoader_state;
                state.requestId = String((new Date()).getTime()) + "-" + String(Math.floor(Math.random() * 1000000));
                state.startedAt = (new Date()).getTime();
                state.waiting = true;
                state.button.enabled = false;
                state.status.text = "Reloading plugins…";

                writeRequest(state.requestId);
                app.scheduleTask("AEHotLoader_pollResponse()", 250, false);
            } catch (e) {
                var state = $.global.AEHotLoader_state;
                state.waiting = false;
                state.button.enabled = true;
                state.status.text = "Error: " + e.toString();
            }
        };

        panel.onResizing = panel.onResize = function () {
            this.layout.resize();
        };

        return panel;
    }

    var panel = buildUI(thisObj);
    if (panel instanceof Window) {
        panel.center();
        panel.show();
    } else {
        panel.layout.layout(true);
    }
})(this);
