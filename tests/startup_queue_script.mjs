import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const program=fs.readFileSync(process.argv[2],'utf8');
let cases=0;
function scenario(mode='ok') {
    const calls=[];
    class CompItem {} class FootageItem {} class FolderItem {}
    class File {constructor(path){this.fsName=path;}}
    class Folder {constructor(){this.exists=mode!=='folder-missing';} getFiles(){return mode==='output-present'?[{}]:[];}}
    const source=Object.assign(new FootageItem(),{name:'own fixture',width:64,height:48});
    const effect={matchName:'own.match',enabled:true};
    const values={'ADBE Anchor Point':[32,24], 'ADBE Position':[32,24], 'ADBE Scale':[100,100],
        'ADBE Rotate Z':0,'ADBE Opacity':100};
    const transform={property(key){return {value:values[key]};}};
    const layer={name:'own fixture',source,enabled:true,property(key){return key==='ADBE Effect Parade'?
        {numProperties:1,property(){return effect;}}:transform;}};
    const comp=Object.assign(new CompItem(),{name:'own fixture',width:64,height:48,frameRate:24,duration:1,
        pixelAspect:1,numLayers:1,resolutionFactor:[1,1],layer(){return layer;}});
    const settings={Format:'PNG Sequence',Channels:'RGB'};
    const om={templates:mode==='template-missing'?[]:['PNG Sequence'],
        applyTemplate(){calls.push('template');if(mode==='exception')throw Error('secret');},getSettings(){return settings;}};
    const item={comp,render:true,status:0,outputModule(){return om;},setSettings(s){calls.push('settings');this.settings=s;},
        getSettings(){return this.settings;}};
    const queue={numItems:0,rendering:false,item(){return item;},items:{add(){calls.push('add');queue.numItems++;
        if(mode==='changed-on-add')app.project={};return item;}},render(){calls.push('render');item.status=1;
        if(mode==='user-stopped')item.status=2;
        if(mode==='changed-on-render')app.project={};
        if(mode==='edited-on-render')values['ADBE Scale']=[50,50];
        if(mode==='render-exception')throw Error('secret');}};
    const p={file:null,bitsPerChannel:8,workingSpace:'',linearBlending:false,linearizeWorkingSpace:false,
        revision:7,numItems:2,renderQueue:queue,item(i){return i===1?comp:source;}};
    const app={project:p};
    if(mode==='saved')p.file={}; if(mode==='depth')p.bitsPerChannel=32;
    if(mode==='working-space')p.workingSpace='sRGB'; if(mode==='linear')p.linearBlending=true;
    if(mode==='queue-present')queue.numItems=1;if(mode==='rendering')queue.rendering=true;
    if(mode==='revision')p.revision=8;if(mode==='wrong-match')effect.matchName='foreign';
    if(mode==='disabled-effect')effect.enabled=false;if(mode==='disabled-layer')layer.enabled=false;
    if(mode==='transform')values['ADBE Scale']=[50,50];if(mode==='resolution')comp.resolutionFactor=[2,2];
    if(mode==='foreign-item')p.numItems=3;if(mode==='wrong-format')settings.Format='QuickTime';
    if(mode==='wrong-channels')settings.Channels='Alpha';
    if(mode==='readback')item.getSettings=()=>({Quality:'Draft',Resolution:'Full',Effects:'All On'});
    const date=class {getTime(){return mode==='expired'?4000000000000:100000;}};
    const response=vm.runInNewContext(program,{app,CompItem,FootageItem,FolderItem,File,Folder,Date:date,
        PostRenderAction:{NONE:0},RQItemStatus:{DONE:1},GetSettingsFormat:{STRING:1}},{timeout:1000});
    assert(!response.includes('secret'));
    cases++;return {calls,response,queue,item,om};
}
let result=scenario();assert(result.response.includes('status=DONE\n'));
assert.deepEqual(result.calls,['add','settings','template','render']);
assert(result.response.includes('revision=7\n'));
assert.equal(result.queue.numItems,1);assert.equal(result.item.timeSpanStart,1/24);
assert.equal(result.item.timeSpanDuration,1/24);assert.equal(result.om.file.fsName,'/owned/output/control[#####].png');
for(const mode of ['saved','depth','working-space','linear','queue-present','rendering','revision','wrong-match',
    'disabled-effect','disabled-layer','transform','resolution','foreign-item','expired','folder-missing','output-present']) {
    result=scenario(mode);assert(result.response.includes('status=REFUSED\n'),mode);assert.deepEqual(result.calls,[],mode);
}
for(const mode of ['changed-on-add','template-missing','exception','wrong-format','wrong-channels','readback']) {
    result=scenario(mode);assert(result.response.includes('status=REFUSED\n'),mode);assert(!result.calls.includes('render'),mode);
}
for(const mode of ['user-stopped','changed-on-render','edited-on-render','render-exception']) {
    result=scenario(mode);assert(result.response.includes('status=REFUSED\n'),mode);
    assert.equal(result.calls.filter(x=>x==='render').length,1);
}
console.log(`QUEUE_SCRIPT_CASES=${cases} PASS; model-only; Adobe_calls=0`);
