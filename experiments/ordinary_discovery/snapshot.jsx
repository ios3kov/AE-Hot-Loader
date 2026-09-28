// Execute through DoScriptFile. Writes metadata only; does not change the project.
(function () {
    var root = new File($.fileName).parent.parent.parent;
    var output = new Folder(root.fsName + "/build-ae-hot-loader/ordinary-discovery");
    if (!output.exists && !output.create()) throw Error("Cannot create evidence directory");
    var file = new File(output.fsName + "/registry-" + new Date().getTime() + ".txt");
    file.encoding = "UTF-8";
    file.lineFeed = "Unix";
    if (!file.open("w")) throw Error(file.error);
    try {
        file.writeln("version=" + app.version);
        file.writeln("items=" + app.project.numItems + " dirty=" + app.project.dirty);
        var effects = app.effects;
        file.writeln("count=" + effects.length);
        for (var i = 0; i < effects.length; ++i)
            file.writeln(effects[i].matchName + "\t" + effects[i].displayName + "\t" + effects[i].category);
    } finally { file.close(); }
}());
