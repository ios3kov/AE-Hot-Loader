(function () {
    var root = new File($.fileName).parent.parent.parent;
    var output = new Folder(root.fsName + "/build-ae-hot-loader/ordinary-discovery");
    var id = new Date().getTime();
    var log = new File(output.fsName + "/render-" + id + ".txt");
    log.lineFeed = "Unix";
    if (!log.open("w")) throw Error(log.error);
    var comp = null, source = null;
    app.beginUndoGroup("AE Hot Loader discovery test");
    try {
        comp = app.project.items.addComp("AEHL discovery " + id, 128, 128, 1, 1, 24);
        var layer = comp.layers.addSolid([0, 0, 0], "Probe input", 128, 128, 1);
        source = layer.source;
        var effects = layer.property("ADBE Effect Parade");
        var canAdd = effects.canAddProperty("StellarLabs.StellarGradient");
        log.writeln("canAdd=" + canAdd);
        if (!canAdd) throw Error("Effect cannot be applied");
        var effect = effects.addProperty("StellarLabs.StellarGradient");
        log.writeln("applied=" + effect.matchName + " params=" + effect.numProperties);
        var frame = new File(output.fsName + "/stellar-" + id + ".mov");
        var queueItem = app.project.renderQueue.items.add(comp);
        var outputModule = queueItem.outputModule(1);
        outputModule.file = frame;
        log.writeln("render_begin=" + frame.fsName);
        app.project.renderQueue.render();
        var rendered = [];
        for (var wait = 0; wait < 40 && rendered.length === 0; ++wait) {
            rendered = output.getFiles("stellar-" + id + "*");
            if (rendered.length === 0) $.sleep(250);
        }
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
            if (source) source.remove();
        } finally {
            app.endUndoGroup();
            log.close();
        }
    }
}());
