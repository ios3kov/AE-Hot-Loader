(function () {
    var root = new File($.fileName).parent.parent.parent;
    var output = new Folder(root.fsName + "/build-ae-hot-loader/ordinary-discovery");
    var id = new Date().getTime();
    var log = new File(output.fsName + "/rust-render-" + id + ".txt");
    log.lineFeed = "Unix";
    if (!log.open("w")) throw Error(log.error);
    var comp = null;
    app.beginUndoGroup("AE Hot Loader ordinary discovery render test");
    try {
        comp = app.project.items.addComp("AEHL Rust render " + id, 128, 128, 1, 1, 24);
        var layer = comp.layers.addSolid([0.25, 0.5, 0.75], "Probe input", 128, 128, 1);
        var effects = layer.property("ADBE Effect Parade");
        var matchName = "OS3KOV.AEHotLoader.RustProbe";
        log.writeln("canAdd=" + effects.canAddProperty(matchName));
        if (!effects.canAddProperty(matchName)) throw Error("Effect cannot be applied");
        var effect = effects.addProperty(matchName);
        log.writeln("applied=" + effect.matchName + " params=" + effect.numProperties);
        var frame = new File(output.fsName + "/rust-probe-" + id + ".png");
        comp.saveFrameToPng(0, frame);
        var rendered = output.getFiles("rust-probe-" + id + "*");
        if (!rendered || rendered.length === 0) throw Error("Missing render output");
        var renderedBytes = 0;
        if (rendered[0].open("r")) {
            rendered[0].seek(0, 2);
            renderedBytes = rendered[0].tell();
            rendered[0].close();
        }
        if (renderedBytes <= 0) throw Error("Empty render output");
        log.writeln("render=" + rendered[0].fsName + " bytes=" + renderedBytes);
        log.writeln("PASS apply and render");
    } catch (error) {
        log.writeln("FAIL " + error.toString());
    } finally {
        try {
            if (comp) comp.remove();
        } finally {
            app.endUndoGroup();
            log.close();
        }
    }
}());
