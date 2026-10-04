#pragma once
#include <string>

namespace startup_color {
// Same target route/setter order; fixed subcauses, no raw host exception text.
constexpr const char* script = R"JS((function () {
    var p=app.project, stage='before';
    function fail(reason) { return 'AEHL-CAL-COLOR-DIAG-1\nstage='+stage+'\nreason='+reason+'\n'; }
    function workingSpaceFacts() {
        var value=p.workingSpace, kind=typeof value, category='other';
        if (value===null) category='null';
        else if (kind==='undefined') category='undefined';
        else if (kind==='string') category=value===''?'empty':value==='None'?'none-token':'other-string';
        return 'AEHL-CAL-COLOR-FACTS-1\nstage=final\nreason=working-space-mismatch\nvalue='+category+'\n';
    }
    function safe() {
        if (!p) return 'no-project';
        if (app.project!==p) return 'project-changed';
        if (p.file!==null) return 'saved-project';
        if (p.numItems!==0) return 'nonempty-project';
        if (p.bitsPerChannel!==8) return 'depth';
        if (p.renderQueue.numItems!==0) return 'queue';
        if (p.renderQueue.rendering!==false) return 'rendering';
        return '';
    }
    try {
        var reason=safe(); if (reason) return fail(reason);
        stage='working-space'; p.workingSpace=''; reason=safe(); if (reason) return fail(reason);
        stage='linear-blending'; p.linearBlending=false; reason=safe(); if (reason) return fail(reason);
        stage='linearize'; p.linearizeWorkingSpace=false; reason=safe(); if (reason) return fail(reason);
        stage='final';
        // AE25.6x101 returned the exact None token after the empty-string setter.
        // The native caller separately requires the public non-OCIO engine guard.
        if (p.workingSpace!=='' && p.workingSpace!=='None') return workingSpaceFacts();
        if (p.linearBlending!==false) return fail('linear-blending-mismatch');
        if (p.linearizeWorkingSpace!==false) return fail('linearize-mismatch');
        return 'AEHL-CAL-COLOR-1\n';
    } catch (error) { return fail('script-exception'); }
})())JS";

inline std::string Diagnostic(const std::string& response) {
    for (const auto* category : {"null", "undefined", "empty", "none-token", "other-string", "other"}) {
        const auto fixed=std::string("AEHL-CAL-COLOR-FACTS-1\nstage=final\nreason=working-space-mismatch\nvalue=")+category+"\n";
        if (response==fixed) return fixed;
    }
    for (const auto* stage : {"before", "working-space", "linear-blending", "linearize", "final"})
        for (const auto* reason : {"no-project", "project-changed", "saved-project", "nonempty-project",
                "depth", "queue", "rendering", "working-space-mismatch", "linear-blending-mismatch",
                "linearize-mismatch", "script-exception"}) {
            const auto fixed=std::string("AEHL-CAL-COLOR-DIAG-1\nstage=")+stage+"\nreason="+reason+"\n";
            if (response==fixed) return fixed;
        }
    return "AEHL-CAL-COLOR-DIAG-1\nstage=response\nreason=unrecognized-response\n";
}
inline std::string SDKFailure(const std::string& stage) {
    for (const auto* fixed : {"scripting-available", "script-execution", "script-result"})
        if (stage==fixed) return std::string("AEHL-CAL-COLOR-DIAG-1\nstage=")+fixed+"\nreason=sdk-script-failed\n";
    return "AEHL-CAL-COLOR-DIAG-1\nstage=script-api\nreason=sdk-script-failed\n";
}
}
