// Execute the actual diagnostic script against our model, never against AE.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const header = fs.readFileSync(new URL('../experiments/startup_calibration/ColorPreparation.hpp', import.meta.url), 'utf8');
const program = header.match(/R"JS\(([\s\S]*?)\)JS"/)[1];
const properties = ['workingSpace', 'linearBlending', 'linearizeWorkingSpace'];
let cases = 0;
function scenario({initial, after, throws, ignores} = {}) {
    const writes = [], p = {file: null, numItems: 0, bitsPerChannel: 8, renderQueue: {numItems: 0, rendering: false}};
    const app = {project: p};
    const values = {workingSpace: 'own-initial-profile', linearBlending: true, linearizeWorkingSpace: true};
    for (const key of properties) Object.defineProperty(p, key, {
        get() { return values[key]; },
        set(value) {
            writes.push(key);
            if (throws === key) throw Error('must never be disclosed');
            if (ignores !== key) values[key] = value;
            if (after?.key === key) after.change(app, p);
        }
    });
    if (initial) initial(app, p);
    const response = vm.runInNewContext(program, {app}, {timeout: 1000});
    assert(!response.includes('must never be disclosed'));
    cases++;
    return {response, writes, values};
}
let s = scenario();
assert.equal(s.response, 'AEHL-CAL-COLOR-1\n');
assert.deepEqual(s.writes, properties);
assert.deepEqual(s.values, {workingSpace: '', linearBlending: false, linearizeWorkingSpace: false});
const guards = [
    ['project-changed', (app) => {app.project = {};}],
    ['saved-project', (_, p) => {p.file = {};}],
    ['nonempty-project', (_, p) => {p.numItems = 1;}],
    ['depth', (_, p) => {p.bitsPerChannel = 32;}],
    ['queue', (_, p) => {p.renderQueue.numItems = 1;}],
    ['rendering', (_, p) => {p.renderQueue.rendering = true;}]
];
const stages = ['working-space', 'linear-blending', 'linearize'];
// A changed app.project before capture is the current project. Use null to
// exercise no-project, and each after-setter change to test identity loss.
s = scenario({initial: (app) => {app.project = null;}});
assert.equal(s.response, 'AEHL-CAL-COLOR-DIAG-1\nstage=before\nreason=no-project\n');
assert.equal(s.writes.length, 0);
for (const [reason, change] of guards.slice(1)) {
    s = scenario({initial: change});
    assert.equal(s.response, `AEHL-CAL-COLOR-DIAG-1\nstage=before\nreason=${reason}\n`);
    assert.equal(s.writes.length, 0);
}
for (let i = 0; i < properties.length; i++) {
    for (const [reason, change] of guards) {
        s = scenario({after: {key: properties[i], change}});
        assert.equal(s.response, `AEHL-CAL-COLOR-DIAG-1\nstage=${stages[i]}\nreason=${reason}\n`);
        assert.deepEqual(s.writes, properties.slice(0, i + 1));
    }
    s = scenario({throws: properties[i]});
    assert.equal(s.response, `AEHL-CAL-COLOR-DIAG-1\nstage=${stages[i]}\nreason=script-exception\n`);
    assert.deepEqual(s.writes, properties.slice(0, i + 1));
    s = scenario({ignores: properties[i]});
    assert.equal(s.response, `AEHL-CAL-COLOR-DIAG-1\nstage=final\nreason=${stages[i]}-mismatch\n`);
}
console.log(`COLOR_SCRIPT_CASES=${cases} PASS; model-only; Adobe_calls=0`);
