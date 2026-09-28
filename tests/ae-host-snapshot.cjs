'use strict';
// Execute the collector's exact emitted JSX, never an emulated replacement.
const vm = require('node:vm');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const template = fs.readFileSync(0, 'utf8');
const rsmb = ['Smart Motion Blur 3.x', 'RS Motion Blur Pro A 3.x', 'RS Motion Blur Pro Vectors 3.x'];
function run({names = rsmb, saved = false, dirty = false, missingProject = false,
              expired = false, existing = false, writeFail = false, closeFail = false} = {}) {
    let output, writes = 0;
    const conf = {run_id: 'unique', phase: 'before', rsmb, deadline_ms: expired ? 0 : Date.now() + 10000,
                  output: '/owned/Илья/before.json'};
    function File(name) { assert.equal(name, conf.output); this.exists = existing; }
    File.prototype.open = () => true;
    File.prototype.write = (s) => { writes++; output = s; return !writeFail; };
    File.prototype.close = () => !closeFail;
    const project = Object.freeze({numItems: 500, revision: 12, file: saved ? {fsName: '/PRIVATE/project.aep'} : null,
                                   dirty, renderQueue: Object.freeze({numItems: 3, rendering: false})});
    const app = Object.freeze({project: missingProject ? null : project, version: '25.6x101', buildNumber: 101,
                               effects: names.map(matchName => Object.freeze({matchName}))});
    vm.runInNewContext(template.replace('__CONFIG__', JSON.stringify(conf)), {app, File, Date}, {timeout: 1000});
    assert.equal(writes, 1);
    assert.ok(output.endsWith('\n'));
    assert.ok(!output.includes('PRIVATE'));
    return JSON.parse(output);
}
let count = 0;
assert.equal(run({saved: true, dirty: true}).status, 'PASS'); count++;
assert.deepEqual(run({names: []}).rsmb.map(x => x.present), [false, false, false]); count++;
assert.equal(run({names: ['duplicate', 'duplicate']}).status, 'BLOCKED'); count++;
assert.equal(run({missingProject: true}).status, 'BLOCKED'); count++;
assert.equal(run({expired: true}).status, 'BLOCKED'); count++;
assert.throws(() => run({existing: true}), /overwrite/); count++;
assert.throws(() => run({writeFail: true}), /Incomplete/); count++;
assert.throws(() => run({closeFail: true}), /Incomplete/); count++;
const special = run({names: ['__proto__', 'constructor', '\\"\n\u2028']});
assert.equal(special.status, 'PASS'); assert.equal(special.effect_count, 3); count++;
console.log('snapshot mocks: ' + count + '/9');
