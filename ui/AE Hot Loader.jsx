(function AEHotLoaderPanel(thisObj) {
    var PRODUCT = "AE Hot Loader";
    var BRIDGE_FOLDER_NAME = "AE Hot Loader";
    var REQUEST_FILE_NAME = "request.txt";
    var RESPONSE_FILE_NAME = "response.txt";

    function bridgeFolder() {
        var folder = new Folder(Folder.userData.fsName + "/" + BRIDGE_FOLDER_NAME + "/bridge");
        if (!folder.exists && !folder.create()) {
            throw new Error(
                "Cannot create AE Hot Loader bridge folder. " +
                "Enable scripting file access in After Effects preferences."
            );
        }
        return folder;
    }

    function parseKeyValue(text) {
        var out = {};
        var seen = {};
        var lines = text.split(/\r?\n/);
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            var p = line.indexOf("=");
            if (p > 0) {
                var key = line.substring(0, p);
                if (key !== "version" && key !== "request_id" && key !== "status" && key !== "message") {
                    continue;
                }
                if (seen["$" + key]) {
                    throw new Error("Duplicate bridge field: " + key);
                }
                seen["$" + key] = true;
                out[key] = line.substring(p + 1);
            }
        }
        return out;
    }

    function readText(file) {
        if (!file.exists || !file.open("r")) {
            return null;
        }
        try {
            return file.read();
        } finally {
            file.close();
        }
    }

    // app.effects is read-only. Copy identities, not native module counts.
    // This checks registry presence only; it never applies or renders an effect.
    function snapshotRegistry() {
        var effects = app.effects;
        if (!effects || typeof effects.length !== "number") {
            throw new Error("Installed Effects Registry is unavailable");
        }
        var names = {};
        for (var i = 0; i < effects.length; i++) {
            var name = effects[i].matchName;
            if (typeof name !== "string" || name.length === 0) {
                throw new Error("Invalid effect match name in registry");
            }
            var key = "$" + name;
            if (names[key]) {
                throw new Error("Duplicate effect match name in registry");
            }
            names[key] = true;
        }
        return names;
    }

    function responseSummary(before, data) {
        if (data.version !== "1" ||
            (data.status !== "success" && data.status !== "noop" && data.status !== "error")) {
            throw new Error("Unsupported bridge response");
        }
        var after = snapshotRegistry();
        var added = 0;
        var removed = 0;
        var key;
        for (key in after) {
            if (after.hasOwnProperty(key) && !before[key]) { added++; }
        }
        for (key in before) {
            if (before.hasOwnProperty(key) && !after[key]) { removed++; }
        }
        var summary;
        if (removed > 0) {
            summary = "Registry changed unexpectedly: " + removed + " removed; " + added + " added.";
        } else if (added > 0) {
            summary = "Registry: " + added + " added. Apply/render not checked.";
        } else {
            summary = "Registry unchanged. No new effects confirmed.";
        }
        if (data.status === "error") {
            return "Scan incomplete: " + (data.message || "Agent error") + "\n" + summary;
        }
        return summary;
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
            throw new Error(
                "Cannot write AE Hot Loader request. " +
                "Enable scripting file access in After Effects preferences."
            );
        }

        temp.lineFeed = "Unix";
        var wrote = false;
        try {
            wrote = temp.write(
                "version=1\n" +
                "command=reload_plugins\n" +
                "request_id=" + requestId + "\n" +
                "timestamp=" + (new Date()).getTime() + "\n"
            );
        } finally {
            temp.close();
        }
        if (!wrote) {
            try { temp.remove(); } catch (e) {}
            throw new Error("Cannot write bridge request.");
        }

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

        try {
            var folder = bridgeFolder();
            var response = new File(folder.fsName + "/" + RESPONSE_FILE_NAME);

            if (response.exists) {
                var text = readText(response);
                if (text !== null) {
                    var data = parseKeyValue(text);
                    if (data.request_id === state.requestId) {
                        var summary = responseSummary(state.beforeRegistry, data);
                        state.waiting = false;
                        state.button.enabled = true;
                        state.status.text = summary;
                        try { response.remove(); } catch (e) {}
                        return;
                    }
                }
            }

            var elapsed = (new Date()).getTime() - state.startedAt;
            if (elapsed > 30000) {
                state.waiting = false;
                state.button.enabled = true;
                state.status.text = "Native helper timed out; result unknown. Scan may still be running.";
                return;
            }

            app.scheduleTask("AEHotLoader_pollResponse()", 250, false);
        } catch (e) {
            state.waiting = false;
            state.button.enabled = true;
            state.status.text = "Error: " + e.toString();
        }
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

        var status = panel.add("statictext", undefined, "Ready", { multiline: true });
        status.alignment = ["fill", "top"];
        status.preferredSize.height = 64;

        $.global.AEHotLoader_state = {
            button: reloadButton,
            status: status,
            requestId: "",
            startedAt: 0,
            waiting: false,
            beforeRegistry: null
        };

        reloadButton.onClick = function () {
            try {
                var state = $.global.AEHotLoader_state;
                if (state.waiting) { return; }
                state.beforeRegistry = snapshotRegistry();
                state.requestId = String((new Date()).getTime()) + "-" + String(Math.floor(Math.random() * 1000000));
                state.startedAt = (new Date()).getTime();
                state.waiting = true;
                state.button.enabled = false;
                state.status.text = "Scanning for new effects…";

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
