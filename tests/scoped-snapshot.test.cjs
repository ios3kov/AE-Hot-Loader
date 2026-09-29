'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const native = fs.readFileSync(path.join(__dirname, '../experiments/ordinary_discovery/ScopedDiscovery.cpp'), 'utf8');
const source = native.match(/snapshot_script = R"JS\(([\s\S]*?)\)JS";/)[1];
function app() {
  return {version: '25.6x101', buildNumber: 101,
    project: {file: null, dirty: false, numItems: 0, revision: 1,
      renderQueue: {numItems: 0, rendering: false}},
    effects: [{matchName: 'Z name'}, {matchName: 'A\nname'}]};
}
function run(a) {
  const before = JSON.stringify(a);
  const result = vm.runInNewContext(source, {app: a}, {timeout: 1000});
  assert.equal(JSON.stringify(a), before, 'snapshot must not mutate host state');
  return result;
}
test('exact snapshot encodes names and preserves state', () => {
  assert.equal(run(app()), 'AEHL-SNAPSHOT-1\n1\nA%0Aname\nZ%20name\n');
});
for (const [name, mutate] of [
  ['wrong version', a => a.version = '25.5'],
  ['wrong build', a => a.buildNumber = 100],
  ['missing project', a => a.project = null],
  ['saved project', a => a.project.file = {name: 'test.aep'}],
  ['dirty project', a => a.project.dirty = true],
  ['nonempty project', a => a.project.numItems = 1],
  ['queued item', a => a.project.renderQueue.numItems = 1],
  ['active render', a => a.project.renderQueue.rendering = true],
  ['unknown revision', a => delete a.project.revision],
  ['invalid registry identity', a => a.effects[0].matchName = ''],
]) {
  test(name + ' blocks snapshot', () => {
    const a = app(); mutate(a); assert.equal(run(a), 'BLOCKED');
  });
}
