'use strict';
const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const source=fs.readFileSync('experiments/ordinary_discovery/apply_registration_probe.jsx','utf8');
const match='AEHL.Dynamic.50650366d8b6';
function run(o={}) {
  let report, created=0, removed=0;
  function project(dirty=false) {
    const p={numItems:0,file:null,dirty,renderQueue:{numItems:0,rendering:false},close(){return !o.closeFail;}};
    p.items={addComp(){return {layers:{addSolid(){
      const layer={enabled:true,property(){return {
        canAddProperty(){return !o.canAddFail;},
        addProperty(){assert.equal(layer.enabled,false);if(o.addFail)throw Error('add failed');
          return {matchName:match,numProperties:o.countFail?1:0,remove(){removed++;}};}
      };}}; return layer;
    }}};}}; return p;
  }
  const app={project:project(!!o.dirty),effects:o.missing?[]:[{matchName:match}],
    newProject(){created++;return this.project=project();}};
  function File(){this.exists=false;this.open=()=>true;this.write=s=>{report=JSON.parse(s);return true;};this.close=()=>true;}
  vm.runInNewContext(source,{app,File,CloseOptions:{DO_NOT_SAVE_CHANGES:0},
    __AEHL_PAIR_APPLY_CONFIG:{match,report:'report.json',run_id:'test',deadline_ms:Date.now()+5000}},{timeout:1000});
  return {report,created,removed};
}
let r=run();assert.equal(r.report.apply,'PASS');assert.equal(r.report.cleanup,'PASS');assert.equal(r.removed,1);
for(const key of ['dirty','missing','canAddFail','addFail','countFail','closeFail']) {
  r=run({[key]:true});assert.equal(r.report.apply,'FAIL');
  assert.equal(r.report.cleanup,['dirty','missing'].includes(key)?'NOT RUN':key==='closeFail'?'FAIL':'PASS');
  if(['dirty','missing'].includes(key))assert.equal(r.created,0);
}
console.log('PASS: registration apply JSX 7/7');
