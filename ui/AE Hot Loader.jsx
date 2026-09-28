(function AEHotLoaderPanel(thisObj) {
    var PRODUCT = "AE Hot Loader";
    // Stamped by tools/build_panel.py. The raw source is deliberately not installable.
    var PANEL_IDENTITY = null; // @AEHL_PANEL_IDENTITY@
    var sequence = 0;
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
        if (typeof text !== "string" || text.length > 16384 || !/\n$/.test(text)) {
            throw new Error("Incomplete or oversized bridge response");
        }
        var out = {};
        var seen = {};
        var lines = text.split(/\r?\n/);
        for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            var p = line.indexOf("=");
            if (p > 0) {
                var key = line.substring(0, p);
                if (key !== "version" && key !== "request_id" && key !== "status" && key !== "message" &&
                    key !== "agent_build_id" && key !== "agent_git_commit" &&
                    key !== "agent_source_clean" && key !== "agent_target" && key !== "agent_version") {
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
        if (file.exists && file.length > 16384) {
            throw new Error("Oversized bridge response");
        }
        file.encoding = "UTF-8";
        if (!file.exists || !file.open("r")) {
            return null;
        }
        var text;
        var closed;
        try {
            text = file.read();
        } finally {
            closed = file.close();
        }
        if (!closed) { throw new Error("Cannot close bridge response"); }
        return text;
    }

    function validateResponse(data) {
        if (data.version !== "1" ||
            (data.status !== "success" && data.status !== "noop" && data.status !== "error")) {
            throw new Error("Unsupported bridge response");
        }
    }

    function verifyAgent(state, data) {
        var keys = ["build_id", "git_commit", "source_clean", "target", "version"];
        for (var i = 0; i < keys.length; i++) {
            if (!data["agent_" + keys[i]]) {
                throw new Error("Agent identity missing. Use panel and Agent from the same package.");
            }
        }
        if (!/^[A-Za-z0-9._-]{1,128}$/.test(data.agent_build_id) ||
            !/^[0-9a-f]{40}$/.test(data.agent_git_commit)) {
            throw new Error("Invalid Agent identity");
        }
        // Do not trust or execute the Agent message as JSON/code.
        state.identityText.text = "Panel: " + (PANEL_IDENTITY ? PANEL_IDENTITY.build_id : "unbuilt") +
            "\nAgent: " + data.agent_build_id + " @ " + data.agent_git_commit.substring(0, 12);
        if (!PANEL_IDENTITY || PANEL_IDENTITY.source_clean !== true) {
            throw new Error("Unbuilt panel. Use an identified clean package; scan blocked.");
        }
        for (var j = 0; j < keys.length; j++) {
            if (data["agent_" + keys[j]] !== String(PANEL_IDENTITY[keys[j]])) {
                throw new Error("Agent identity mismatch (" + keys[j] + "). " +
                    "Use panel and Agent from the same package; an older Agent stays loaded until AE restarts.");
            }
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

    function writeRequest(requestId, command) {
        if (command !== "get_build_identity" && command !== "reload_plugins") {
            throw new Error("Invalid bridge command");
        }
        var folder = bridgeFolder();
        var request = new File(folder.fsName + "/" + REQUEST_FILE_NAME);
        if (request.exists) {
            throw new Error("Bridge busy: pending request preserved.");
        }
        // Each request owns its temporary file. Never delete somebody else's request.
        var temp = new File(folder.fsName + "/request." + requestId + ".tmp");
        if (temp.exists) { throw new Error("Bridge temporary file already exists"); }
        temp.encoding = "UTF-8";

        if (!temp.open("w")) {
            throw new Error(
                "Cannot write AE Hot Loader request. " +
                "Enable scripting file access in After Effects preferences."
            );
        }

        temp.lineFeed = "Unix";
        var wrote = false;
        var closed = false;
        try {
            wrote = temp.write(
                "version=1\n" +
                "command=" + command + "\n" +
                "request_id=" + requestId + "\n" +
                "timestamp=" + (new Date()).getTime() + "\n"
            );
        } finally {
            closed = temp.close();
        }
        if (!wrote || !closed) {
            try { temp.remove(); } catch (e) {}
            throw new Error("Cannot write bridge request.");
        }

        if (request.exists || !temp.rename(REQUEST_FILE_NAME)) {
            try { temp.remove(); } catch (e) {}
            throw new Error("Cannot publish bridge request.");
        }
    }


    function finish(state, message) {
        if (state.taskId !== null) {
            try { app.cancelTask(state.taskId); } catch (e) {}
            state.taskId = null;
        }
        state.waiting = false;
        state.button.enabled = PANEL_IDENTITY !== null;
        state.diagnosticsButton.enabled = true;
        state.status.text = message;
    }

    function schedulePoll(state) {
        // Bind callbacks to one request so a late diagnostic timer cannot poll a scan.
        state.taskId = app.scheduleTask("AEHotLoader_pollResponse('" + state.requestId + "')", 250, false);
    }

    function dispatch(state, command) {
        sequence++;
        state.requestId = String((new Date()).getTime()) + "-" + String(sequence) + "-" +
            String(Math.floor(Math.random() * 1000000));
        state.startedAt = (new Date()).getTime();
        state.phase = command;
        state.waiting = true;
        state.button.enabled = false;
        state.diagnosticsButton.enabled = false;
        writeRequest(state.requestId, command);
        schedulePoll(state);
    }

    $.global.AEHotLoader_pollResponse = function (expectedId) {
        var state = $.global.AEHotLoader_state;
        if (!state || !state.waiting || expectedId !== state.requestId) { return; }
        try {
            var folder = bridgeFolder();
            var response = new File(folder.fsName + "/" + RESPONSE_FILE_NAME);
            if (response.exists) {
                var text = readText(response);
                if (text !== null) {
                    var data = parseKeyValue(text);
                    if (data.request_id === state.requestId) {
                        validateResponse(data);
                        verifyAgent(state, data);
                        if (state.phase === "get_build_identity" && data.status !== "success") {
                            throw new Error("Agent diagnostics failed; scan not started.");
                        }
                        if (!response.remove()) { throw new Error("Cannot consume bridge response"); }
                        if (state.taskId !== null) {
                            try { app.cancelTask(state.taskId); } catch (e) {}
                            state.taskId = null;
                        }
                        if (state.phase === "get_build_identity" && state.scanAfterIdentity) {
                            // Snapshot only immediately before the scan, never before diagnostics.
                            state.beforeRegistry = snapshotRegistry();
                            state.status.text = "Build matched. Scanning for new effects…";
                            dispatch(state, "reload_plugins");
                            return;
                        }
                        finish(state, state.phase === "get_build_identity"
                            ? "Build match verified. No plugins scanned."
                            : responseSummary(state.beforeRegistry, data));
                        return;
                    }
                }
            }
            if ((new Date()).getTime() - state.startedAt > 30000) {
                finish(state, state.phase === "get_build_identity"
                    ? "Agent diagnostics timed out; scan not started."
                    : "Native helper timed out; result unknown. Scan may still be running.");
                return;
            }
            schedulePoll(state);
        } catch (e) {
            var suffix = state.phase === "reload_plugins" ? " Scan result unverified." : " Scan not started.";
            finish(state, "Error: " + e.toString() + suffix);
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

        var diagnosticsButton = panel.add("button", undefined, "Diagnostics");
        var identityText = panel.add("statictext", undefined,
            PANEL_IDENTITY ? "Panel: " + PANEL_IDENTITY.build_id + "\nAgent: not checked" :
                "Unbuilt source panel. Use an identified package.", { multiline: true });
        identityText.preferredSize.height = 48;
        reloadButton.enabled = PANEL_IDENTITY !== null;
        var status = panel.add("statictext", undefined, "Ready", { multiline: true });
        status.alignment = ["fill", "top"];
        status.preferredSize.height = 64;

        $.global.AEHotLoader_state = {
            button: reloadButton,
            diagnosticsButton: diagnosticsButton,
            identityText: identityText,
            status: status,
            taskId: null,
            phase: "",
            scanAfterIdentity: false,
            requestId: "",
            startedAt: 0,
            waiting: false,
            beforeRegistry: null
        };

        function begin(scan) {
            var state = $.global.AEHotLoader_state;
            if (state.waiting) { return; }
            try {
                if (scan && !PANEL_IDENTITY) {
                    throw new Error("Unbuilt panel. Use an identified clean package; scan blocked.");
                }
                state.scanAfterIdentity = scan;
                state.beforeRegistry = null;
                state.status.text = "Checking resident Agent build…";
                dispatch(state, "get_build_identity");
            } catch (e) {
                finish(state, "Error: " + e.toString() + " Scan not started.");
            }
        }
        reloadButton.onClick = function () { begin(true); };
        diagnosticsButton.onClick = function () { begin(false); };

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
