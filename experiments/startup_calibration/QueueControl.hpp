#pragma once
#include <cstdint>
#include <stdexcept>
#include <string>

// Separate public scripting Render Queue control. No async receipt fallback.
namespace startup_queue {
inline std::string Quote(const std::string& value) {
    std::string text="\"";
    for (unsigned char c : value) {
        if (c<32 || c>126) throw std::invalid_argument("queue control requires ASCII");
        if (c=='\\' || c=='\"') text+='\\';
        text+=static_cast<char>(c);
    }
    return text+'\"';
}
inline std::string Script(const std::string& fixture, const std::string& match,
                          const std::string& output, std::uint64_t deadline,
                          std::int64_t revision) {
    if (revision<1 || deadline==0) throw std::invalid_argument("invalid queue scope");
    return std::string(R"JS((function () {
    var n=)JS")+Quote(fixture)+",m="+Quote(match)+",out="+Quote(output)+
        ",deadline="+std::to_string(deadline)+",revision="+std::to_string(revision)+R"JS(;
    var p=app.project,c=null,f=null,q=null,om=null,phase='scope';
    function fail(reason) {return 'AEHL-CAL-QUEUE-1\nstatus=REFUSED\nstage='+phase+'\nreason='+reason+'\n';}
    function guard(queued) {
        if (Math.floor((new Date()).getTime()/1000)>=deadline) return 'deadline';
        if (!p || p!==app.project || p.file!==null || p.bitsPerChannel!==8 ||
            (p.workingSpace!=='' && p.workingSpace!=='None') || p.linearBlending!==false ||
            p.linearizeWorkingSpace!==false || p.renderQueue.rendering!==false) return 'project';
        if(typeof p.revision!=='number' || p.revision<1 || Math.floor(p.revision)!==p.revision) return 'revision';
        if (p.renderQueue.numItems!==(queued?1:0) ||
            (queued && (p.renderQueue.item(1)!==q || q.comp!==c))) return 'queue';
        var folders=0,cc=null,ff=null;
        for(var i=1;i<=p.numItems;i++) {
            var x=p.item(i);
            if(x instanceof CompItem && x.name===n && !cc && x.width===64 && x.height===48 &&
                x.frameRate===24 && x.duration===1 && x.pixelAspect===1 && x.numLayers===1) cc=x;
            else if(x instanceof FootageItem && x.name===n && !ff && x.width===64 && x.height===48) ff=x;
            else if(x instanceof FolderItem && x.parentFolder===p.rootFolder && x.numItems===1 &&
                x.item(1) instanceof FootageItem && x.item(1).name===n) folders++;
            else return 'items';
        }
        if(!cc || !ff || folders>1 || (c && c!==cc) || (f && f!==ff)) return 'fixture';
        c=cc;f=ff;
        var l=c.layer(1),e=l.property('ADBE Effect Parade');
        if(l.source!==f || l.name!==n || l.enabled!==true || e.numProperties!==1 ||
            e.property(1).matchName!==m || e.property(1).enabled!==true ||
            c.resolutionFactor[0]!==1 || c.resolutionFactor[1]!==1) return 'effect';
        var t=l.property('ADBE Transform Group');
        function pair(key,a,b) {var v=t.property(key).value;return v[0]===a && v[1]===b;}
        if(!pair('ADBE Anchor Point',32,24) || !pair('ADBE Position',32,24) ||
            !pair('ADBE Scale',100,100) || t.property('ADBE Rotate Z').value!==0 ||
            t.property('ADBE Opacity').value!==100) return 'transform';
        return '';
    }
    try {
        var reason=guard(false);if(reason) return fail(reason);
        if(p.revision!==revision) return fail('revision');
        var folder=new Folder(out);
        if(!folder.exists || folder.getFiles().length!==0) return fail('output-not-empty');
        phase='queue-add';q=p.renderQueue.items.add(c);
        reason=guard(true);if(reason) return fail(reason);
        phase='settings';q.timeSpanStart=1/24;q.timeSpanDuration=1/24;
        q.setSettings({'Quality':'Best','Resolution':'Full','Effects':'All On'});
        reason=guard(true);if(reason) return fail(reason);
        om=q.outputModule(1);
        var found=0;
        for(var j=0;j<om.templates.length;j++) if(om.templates[j]==='PNG Sequence') found++;
        if(found!==1) return fail('png-template-unavailable');
        om.applyTemplate('PNG Sequence');
        // Reacquire after settings changes; do not retain an invalidated OM.
        om=q.outputModule(1);om.postRenderAction=PostRenderAction.NONE;
        om.file=new File(out+'/control[#####].png');
        var settings=om.getSettings(GetSettingsFormat.STRING),rs=q.getSettings(GetSettingsFormat.STRING);
        if(settings.Format!=='PNG Sequence' || (settings.Channels!=='RGB' && settings.Channels!=='RGB + Alpha') ||
            rs.Quality!=='Best' || rs.Resolution!=='Full' || rs.Effects!=='All On' ||
            q.timeSpanStart!==1/24 || q.timeSpanDuration!==1/24 || q.render!==true ||
            om.postRenderAction!==PostRenderAction.NONE || om.file.fsName!==new File(out+'/control[#####].png').fsName)
            return fail('settings-readback');
        reason=guard(true);if(reason) return fail(reason);
        if(folder.getFiles().length!==0) return fail('output-changed');
        phase='render';p.renderQueue.render();
        phase='after-render';reason=guard(true);if(reason) return fail(reason);
        if(q.status!==RQItemStatus.DONE) return fail('not-done');
        // Leave this exact queue item in the owned project as diagnostic evidence.
        return 'AEHL-CAL-QUEUE-1\nstatus=DONE\nstage=after-render\nformat=PNG Sequence\nchannels='+
            settings.Channels+'\nwidth=64\nheight=48\ntime=1/24\nduration=1/24\nrevision='+p.revision+'\n';
    } catch (_) {return fail('script-exception');}
})())JS";
}
} // namespace startup_queue
