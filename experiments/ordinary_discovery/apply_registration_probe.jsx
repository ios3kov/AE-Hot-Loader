// Configure __AEHL_PAIR_APPLY_CONFIG in an owned wrapper before evaluation.
// Application/parameter setup only. The layer is disabled before adding FX.
(function () {
    var cfg = __AEHL_PAIR_APPLY_CONFIG;
    var file = new File(cfg.report);
    if (file.exists) throw Error("Existing report; refusing overwrite");
    var result = "FAIL", cleanup = "NOT RUN", reason = "", count = -1;
    var owned = false;
    function blank(p) {
        return p && p.numItems === 0 && p.file === null && p.dirty === false &&
            p.renderQueue.numItems === 0 && !p.renderQueue.rendering;
    }
    function q(value) {
        return '"' + String(value).replace(/[\\"\u0000-\u001f]/g, function (c) {
            return "\\u" + ("0000" + c.charCodeAt(0).toString(16)).slice(-4);
        }) + '"';
    }
    try {
        if (!(cfg.deadline_ms >= new Date().getTime())) throw Error("Expired probe");
        if (!blank(app.project)) throw Error("Requires blank unsaved clean idle project");
        if (!/^AEHL\.Dynamic\.[0-9a-f]{12}$/.test(cfg.match)) throw Error("Invalid fixture identity");
        var found = false;
        for (var i = 0; i < app.effects.length; ++i)
            if (app.effects[i].matchName === cfg.match) found = true;
        if (!found) throw Error("Exact fixture not registered");
        var p = app.newProject();
        if (!p) throw Error("Cannot create disposable project");
        owned = true;
        var comp = p.items.addComp("AEHL parameter check", 64, 64, 1, 1/24, 24);
        var layer = comp.layers.addSolid([0,0,0], "Disabled test input", 64,64,1,1/24);
        layer.enabled = false;
        var group = layer.property("ADBE Effect Parade");
        if (!group.canAddProperty(cfg.match)) throw Error("canAddProperty rejected fixture");
        var fx = group.addProperty(cfg.match);
        if (!fx || fx.matchName !== cfg.match) throw Error("Wrong effect identity");
        fx.enabled = false;
        count = fx.numProperties;
        if (count !== 0) throw Error("Expected zero user parameters");
        fx.remove();
        result = "PASS";
    } catch (error) {
        reason = String(error).slice(0,500);
    } finally {
        if (owned) {
            try {
                if (!app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES)) throw Error("Close rejected");
                if (!blank(app.newProject())) throw Error("Blank restore failed");
                cleanup = "PASS";
            } catch (error) { cleanup = "FAIL"; reason += String(error); result = "FAIL"; }
        }
        file.encoding = "UTF-8";
        if (!file.open("w")) throw Error("Cannot create report");
        try {
            if (!file.write('{"run_id":'+q(cfg.run_id)+',"match":'+q(cfg.match)+
                ',"apply":'+q(result)+',"user_parameters":'+count+',"cleanup":'+q(cleanup)+
                ',"render":"NOT RUN","reason":'+q(reason)+'}\n')) throw Error("Report write failed");
        } finally { file.close(); }
    }
}());
