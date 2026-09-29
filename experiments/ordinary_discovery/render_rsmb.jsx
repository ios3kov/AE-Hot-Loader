(function () {
    var MATCH = "Smart Motion Blur 3.x";
    var id = "aehl-rsmb-" + (new Date()).getTime() + "-" + Math.floor(Math.random() * 1000000);
    var root = new Folder("~/Downloads/" + id);
    if (root.exists || !root.create()) throw Error("Cannot create unique evidence folder");
    var report = new File(root.fsName + "/report.json");
    var renderPrefix = "rsmb-render-" + id;
    var renderFile = new File(root.fsName + "/" + renderPrefix + ".mov");

    function quote(s) {
        return '"' + String(s).replace(/[\\\"\u0000-\u001f\u2028\u2029]/g, function (c) {
            return "\\u" + ("0000" + c.charCodeAt(0).toString(16)).slice(-4);
        }) + '"';
    }
    function json(v) {
        if (v === null) return "null";
        if (typeof v === "string") return quote(v);
        if (typeof v === "boolean" || typeof v === "number") return String(v);
        var a = [], k, i;
        if (v instanceof Array) {
            for (i = 0; i < v.length; i++) a.push(json(v[i]));
            return "[" + a.join(",") + "]";
        }
        for (k in v) if (v.hasOwnProperty(k)) a.push(quote(k) + ":" + json(v[k]));
        return "{" + a.join(",") + "}";
    }
    function writeReport(data) {
        report.encoding = "UTF-8";
        report.lineFeed = "Unix";
        if (report.exists || !report.open("w")) throw Error("Cannot create report");
        var wrote = false, closed = false;
        try { wrote = report.write(json(data) + "\n"); }
        finally { closed = report.close(); }
        if (!wrote || !closed) throw Error("Incomplete report write");
    }

    var data = {
        schema_version: 1, run_id: id, host_version: String(app.version),
        status: "FAIL", baseline: {status:"NOT RUN"}, apply: {status:"NOT RUN"},
        render: {status:"NOT RUN"}, cleanup: {status:"NOT RUN"}
    };
    var disposable = false;
    var previousOnError = app.onError;
    $.global.__AEHL_RSMB_RENDER_ERROR = "";
    $.global.__AEHL_RSMB_ON_ERROR = function (message, severity) {
        $.global.__AEHL_RSMB_RENDER_ERROR = String(message);
        try {
            if (app.project && app.project.renderQueue.rendering) app.project.renderQueue.stopRendering();
        } catch (_) {}
    };

    try {
        var baseline = app.project;
        if (!baseline) throw Error("Project unavailable");
        if (baseline.numItems !== 0 || baseline.dirty !== false || baseline.file !== null ||
            baseline.renderQueue.numItems !== 0 || baseline.renderQueue.rendering) {
            throw Error("Unsafe baseline: requires blank, unsaved, clean, idle project");
        }
        var registered = false;
        for (var e = 0; e < app.effects.length; e++) {
            if (app.effects[e].matchName === MATCH) registered = true;
        }
        if (!registered) throw Error("RSMB match name not registered");
        data.baseline = {status:"PASS", items:0, saved:false, dirty:false, queued:0, rsmb_present:true};

        var p = app.newProject();
        if (!p) throw Error("Could not create disposable project");
        disposable = true;

        var duration = 1.0 / 24.0;
        var comp = p.items.addComp("AEHL RSMB probe", 64, 64, 1, duration, 24);
        var layer = comp.layers.addSolid([0.25, 0.5, 0.75], "Probe input", 64, 64, 1, duration);
        var effects = layer.property("ADBE Effect Parade");
        if (!effects || !effects.canAddProperty(MATCH)) throw Error("RSMB cannot be added");
        var fx = effects.addProperty(MATCH);
        if (!fx || fx.matchName !== MATCH) throw Error("Wrong effect added");
        data.apply = {status:"PASS", match_name:String(fx.matchName), parameters:fx.numProperties};

        var item = p.renderQueue.items.add(comp);
        item.timeSpanStart = 0;
        item.timeSpanDuration = duration;
        try { item.queueItemNotify = false; } catch (_) {}
        try { p.renderQueue.queueNotify = false; } catch (_) {}
        var om = item.outputModule(1);
        om.file = renderFile;
        try { om.postRenderAction = PostRenderAction.NONE; } catch (_) {}
        var outputModuleName = String(om.name);

        app.onError = "__AEHL_RSMB_ON_ERROR";
        p.renderQueue.render();
        app.onError = previousOnError;
        if ($.global.__AEHL_RSMB_RENDER_ERROR)
            throw Error("Render error: " + $.global.__AEHL_RSMB_RENDER_ERROR);

        var outputs = root.getFiles(renderPrefix + "*");
        var names = [], bytes = 0;
        for (var i = 0; i < outputs.length; i++) {
            if (outputs[i] instanceof File && outputs[i].name !== report.name) {
                names.push(outputs[i].name);
                bytes += outputs[i].length;
            }
        }
        if (names.length === 0 || bytes <= 0) throw Error("No non-empty render output");
        data.render = {status:"PASS", files:names, total_bytes:bytes, output_module:outputModuleName};
        data.status = "PASS";
    } catch (error) {
        data.reason = String(error).slice(0, 500);
        if (data.apply.status === "PASS" && data.render.status !== "PASS")
            data.render = {status:"FAIL", reason:data.reason};
    } finally {
        try { app.onError = previousOnError; } catch (_) {}
        try { delete $.global.__AEHL_RSMB_ON_ERROR; delete $.global.__AEHL_RSMB_RENDER_ERROR; } catch (_) {}
        if (disposable) {
            try {
                if (app.project) app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
                var restored = app.newProject();
                if (!restored) throw Error("Could not restore blank project");
                if (restored.numItems !== 0 || restored.dirty !== false || restored.file !== null ||
                    restored.renderQueue.numItems !== 0 || restored.renderQueue.rendering) {
                    throw Error("Restored project is not blank/clean");
                }
                data.cleanup = {status:"PASS", items:0, saved:false, dirty:false, queued:0};
            } catch (cleanupError) {
                data.cleanup = {status:"FAIL", reason:String(cleanupError).slice(0, 400)};
                data.status = "FAIL";
            }
        } else {
            data.cleanup = {status:"N/A", reason:"No disposable project was created"};
        }
        writeReport(data);
    }
    return report.fsName;
}());