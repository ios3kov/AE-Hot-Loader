'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[2],'utf8');

function run(opts={}){
  let reportText='', newProjects=0, closes=0, renderCalls=0;
  let renderBacking={exists:false,length:0,name:''};
  function File(path){this.path=path;this.name=path.split('/').pop();this.encoding='';this.lineFeed='';
    Object.defineProperty(this,'exists',{get:()=>this.name==='report.json'?false:renderBacking.exists});
    Object.defineProperty(this,'length',{get:()=>renderBacking.length});
    this.open=()=>true;this.write=s=>{reportText=s;return true;};this.close=()=>true;}
  function Folder(path){this.fsName=path.replace('~','/Users/test');this.exists=false;this.create=()=>true;
    this.getFiles=()=>renderBacking.exists?[new File(this.fsName+'/'+renderBacking.name)]:[];}
  function makeProject(baseline){
    const p={numItems:0,dirty:!!(baseline&&opts.dirty),file:null,
      items:{addComp(){p.numItems++;return {layers:{addSolid(){return {property(){return {
        canAddProperty(){return opts.canAdd!==false;},
        addProperty(){if(opts.addFail)throw Error('add fail');return {matchName:'Smart Motion Blur 3.x',numProperties:5};}
      };}};}}};}},
      renderQueue:{numItems:0,rendering:false,queueNotify:false,items:{add(){p.renderQueue.numItems++;
        const om={name:'Mock Lossless',file:null,postRenderAction:null};
        return {timeSpanStart:0,timeSpanDuration:0,queueItemNotify:false,outputModule(){return om;}};}},
        render(){renderCalls++;if(opts.renderFail)throw Error('render fail');renderBacking={exists:true,length:123,name:'rsmb-render-mock.mov'};}},
      close(){closes++;}};
    return p;
  }
  let current=makeProject(true);
  const app={version:'25.6x101',onError:null,effects:opts.missing?[]:[{matchName:'Smart Motion Blur 3.x'}],
    get project(){return current;},newProject(){newProjects++;current=makeProject(false);return current;}};
  const sandbox={app,File,Folder,PostRenderAction:{NONE:0},CloseOptions:{DO_NOT_SAVE_CHANGES:0},Math,Date,$:{global:{}}};
  let error=null;try{vm.runInNewContext(source,sandbox,{timeout:1000});}catch(e){error=e;}
  return {d:reportText?JSON.parse(reportText):null,newProjects,closes,renderCalls,error};
}
let n=0;
let r=run();assert.equal(r.d.status,'PASS');assert.equal(r.d.apply.status,'PASS');assert.equal(r.d.render.status,'PASS');assert.equal(r.d.cleanup.status,'PASS');n++;
r=run({dirty:true});assert.equal(r.d.status,'FAIL');assert.equal(r.newProjects,0);n++;
r=run({missing:true});assert.equal(r.d.status,'FAIL');assert.equal(r.newProjects,0);n++;
r=run({canAdd:false});assert.equal(r.d.status,'FAIL');assert.equal(r.d.cleanup.status,'PASS');n++;
r=run({addFail:true});assert.equal(r.d.status,'FAIL');assert.equal(r.d.cleanup.status,'PASS');n++;
r=run({renderFail:true});assert.equal(r.d.status,'FAIL');assert.equal(r.d.render.status,'FAIL');assert.equal(r.d.cleanup.status,'PASS');n++;
console.log('RSMB JSX mocks: '+n+'/6');
