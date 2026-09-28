'use strict';
// Host mocks exercise the shipped JSX. They are NOT live After Effects evidence.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const template = fs.readFileSync(path.join(__dirname, '../ui/AE Hot Loader.jsx'), 'utf8');
const expected = {
    component: 'panel', schema_version: 1,
    git_commit: process.env.PANEL_COMMIT_EXPECTED || 'a'.repeat(40),
    build_id: process.env.PANEL_BUILD_EXPECTED || 'test-panel-1',
    source_clean: true, target: 'aarch64-apple-darwin', version: '0.1.0'
};
const marker = 'var PANEL_IDENTITY = null; // @AEHL_PANEL_IDENTITY@';
const source = process.env.PANEL_SOURCE ? fs.readFileSync(process.env.PANEL_SOURCE, 'utf8') :
    template.replace(marker, 'var PANEL_IDENTITY = ' + JSON.stringify(expected) + ';');

function harness(panelSource = source) {
    const files = new Map();
    const root = '/test/Unicode Илья/AE Hot Loader/bridge/';
    const faults = {};
    let now = 1000;
    let effects = [{matchName: 'Existing'}];
    let registryReads = 0;
    let closes = 0;
    const scheduled = [];
    function File(name) { this.fsName = name; }
    Object.defineProperty(File.prototype, 'exists', {get() { return files.has(this.fsName); }});
    Object.defineProperty(File.prototype, 'length', {get() { return (files.get(this.fsName) || '').length; }});
    File.prototype.open = function(mode) { this.mode = mode; return !faults.open; };
    File.prototype.read = function() { if (faults.read) throw Error('read failed'); return files.get(this.fsName); };
    File.prototype.write = function(text) { if (faults.write) return false; files.set(this.fsName, text); return true; };
    File.prototype.close = function() { closes++; return !faults.close; };
    File.prototype.remove = function() { return !faults.remove && files.delete(this.fsName); };
    File.prototype.rename = function(name) {
        if (faults.rename) return false;
        const dest = this.fsName.substring(0, this.fsName.lastIndexOf('/') + 1) + name;
        files.set(dest, files.get(this.fsName)); files.delete(this.fsName); this.fsName = dest;
        return true;
    };
    function Folder(name) { this.fsName = name; this.exists = !faults.folder; }
    Folder.userData = {fsName: '/test/Unicode Илья'};
    Folder.prototype.create = function() { return !faults.folder; };
    function Window() {
        this.layout = {layout() {}, resize() {}};
        this.center = this.show = function() {};
        this.add = function(type, unused, text) { return {text, enabled: true, preferredSize: {}}; };
    }
    function Clock() {}
    Clock.prototype.getTime = function() { return now; };
    const global = {};
    const cancelled = [];
    const app = {
        scheduleTask(code) { if (faults.schedule) throw Error('schedule failed'); scheduled.push(code); return scheduled.length; },
        cancelTask(id) { cancelled.push(id); }
    };
    Object.defineProperty(app, 'effects', {get() {
        registryReads++;
        if (faults.registry) throw Error('registry unavailable');
        return effects;
    }});
    Object.defineProperty(app, 'project', {get() { throw Error('Panel must not touch the project'); }});
    const context = {File, Folder, Window, Panel: function() {}, app, $: {global}, Date: Clock};
    vm.runInNewContext(panelSource, context, {filename: 'AE Hot Loader.jsx', timeout: 1000});
    return {
        faults, files, scheduled, cancelled,
        state() { return global.AEHotLoader_state; },
        click() { global.AEHotLoader_state.button.onClick(); },
        diagnostics() { global.AEHotLoader_state.diagnosticsButton.onClick(); },
        poll(id = this.state().requestId) { global.AEHotLoader_pollResponse(id); },
        startScan() {
            this.click();
            if (this.state().waiting && this.state().phase === 'get_build_identity') {
                this.response(); this.poll();
            }
        },
        response(status = 'success', message = 'ordinary-discovery-v1: loaded:364 post_load_modules:9', id) {
            this.reply({status, message}, id);
        },
        reply(overrides = {}, id = this.state().requestId) {
            const data = {
                version: '1', request_id: id, status: 'success', message: 'diagnostics',
                agent_build_id: expected.build_id, agent_git_commit: expected.git_commit,
                agent_source_clean: 'true', agent_target: expected.target, agent_version: expected.version,
                ...overrides
            };
            if (id === this.state().requestId) files.delete(root + 'request.txt');
            files.set(root + 'response.txt', Object.entries(data).filter(([, v]) => v !== undefined).map(([k,v]) => k + '=' + v).join('\n') + '\n');
        },
        raw(text) { files.delete(root + 'request.txt'); files.set(root + 'response.txt', text); },
        registry(names) { effects = names.map(matchName => ({matchName})); },
        advance(ms) { now += ms; },
        reads() { return registryReads; },
        closes() { return closes; },
        request() { return files.get(root + 'request.txt'); },
        pending(text) { files.set(root + 'request.txt', text); }
    };
}
function complete(h, status) { h.response(status); h.poll(); return h.state().status.text; }

test('loaded binaries without registry growth are not registration success', () => {
    const h = harness(); h.startScan();
    assert.match(complete(h), /Registry unchanged/);
    assert.equal(h.reads(), 2);
});
test('new match name is observed, but apply/render is not claimed', () => {
    const h = harness(); h.startScan(); h.registry(['Existing', 'New']);
    assert.match(complete(h), /Registry: 1 added/);
    assert.match(h.state().status.text, /Apply\/render not checked/);
});
test('equal counts with replaced identities are not treated as unchanged', () => {
    const h = harness(); h.startScan(); h.registry(['Replacement']);
    assert.match(complete(h), /Registry changed unexpectedly: 1 removed/);
});
test('registry order changes do not imply new effects', () => {
    const h = harness(); h.registry(['A', 'B']); h.startScan(); h.registry(['B', 'A']);
    assert.match(complete(h), /Registry unchanged/);
});
test('duplicate match names block the request', () => {
    const h = harness(); h.registry(['Duplicate', 'Duplicate']); h.startScan();
    assert.match(h.state().status.text, /Duplicate effect match name/);
    assert.equal(h.request(), undefined);
    assert.equal(h.state().button.enabled, true);
});
test('unavailable baseline registry blocks the scan after read-only diagnostics', () => {
    const h = harness(); h.faults.registry = true; h.startScan();
    assert.equal(h.request(), undefined);
    assert.match(h.state().status.text, /registry unavailable/);
});
test('unavailable after-registry cannot produce success', () => {
    const h = harness(); h.startScan(); h.faults.registry = true;
    assert.match(complete(h), /Error:.*registry unavailable/);
    assert.equal(h.state().waiting, false);
});
test('partial scan failure remains an error even when an effect appears', () => {
    const h = harness(); h.startScan(); h.registry(['Existing', 'New']);
    assert.match(complete(h, 'error'), /^Scan incomplete:/);
    assert.match(h.state().status.text, /Registry: 1 added/);
});
test('noop from agent does not bypass independent registry check', () => {
    const h = harness(); h.startScan();
    assert.match(complete(h, 'noop'), /Registry unchanged/);
});
test('unknown response version is rejected', () => {
    const h = harness(); h.startScan();
    h.raw('version=2\nrequest_id=' + h.state().requestId + '\nstatus=success\nmessage=PASS\n'); h.poll();
    assert.match(h.state().status.text, /Unsupported bridge response/);
});
test('unknown status is rejected', () => {
    const h = harness(); h.startScan();
    assert.match(complete(h, 'mystery'), /Unsupported bridge response/);
});
test('stale request identity never completes the current request', () => {
    const h = harness(); h.startScan(); h.response('success', 'STALE PASS', 'older-run'); h.poll();
    assert.equal(h.state().waiting, true);
    assert.doesNotMatch(h.state().status.text, /STALE PASS/);
});
test('missing response times out without claiming no work occurred', () => {
    const h = harness(); h.startScan(); h.advance(30001); h.poll();
    assert.match(h.state().status.text, /result unknown/);
    assert.equal(h.state().waiting, false);
});
test('late response after timeout does not overwrite the timeout result', () => {
    const h = harness(); h.startScan(); h.advance(30001); h.poll();
    const text = h.state().status.text; h.response(); h.poll();
    assert.equal(h.state().status.text, text);
});
test('poll read exception unlocks UI and closes the file', () => {
    const h = harness(); h.startScan(); h.response(); h.faults.read = true;
    const before = h.closes(); h.poll();
    assert.match(h.state().status.text, /Error:.*read failed/);
    assert.equal(h.state().button.enabled, true);
    assert.equal(h.closes(), before + 1);
});
test('double click while pending does not publish a second request', () => {
    const h = harness(); h.startScan(); const request = h.request(); const count = h.scheduled.length; h.advance(1); h.click();
    assert.equal(h.request(), request);
    assert.equal(h.scheduled.length, count);
});
test('request write failure cannot publish an incomplete request', () => {
    const h = harness(); h.faults.write = true; h.startScan();
    assert.equal(h.request(), undefined);
    assert.match(h.state().status.text, /Cannot write bridge request/);
});
test('request publish failure is reported and UI is restored', () => {
    const h = harness(); h.faults.rename = true; h.startScan();
    assert.match(h.state().status.text, /Cannot publish bridge request/);
    assert.equal(h.state().button.enabled, true);
});
test('response removal follows successful consumption', () => {
    const h = harness(); h.startScan(); complete(h);
    assert.equal([...h.files.keys()].some(p => p.endsWith('response.txt')), false);
});
test('names resembling object properties are compared safely', () => {
    const h = harness(); h.registry(['__proto__']); h.startScan(); h.registry(['__proto__', 'constructor']);
    assert.match(complete(h), /Registry: 1 added/);
});
test('duplicate protocol fields are rejected, not silently overwritten', () => {
    const h = harness(); h.startScan();
    h.raw('version=1\nrequest_id=' + h.state().requestId + '\nstatus=error\nstatus=success\n'); h.poll();
    assert.match(h.state().status.text, /Duplicate bridge field/);
});
test('a complete scan can be repeated with a fresh registry baseline', () => {
    const h = harness(); h.startScan(); h.registry(['Existing', 'New']); complete(h);
    h.advance(1); h.startScan(); assert.match(complete(h), /Registry unchanged/);
    assert.equal(h.reads(), 4);
});

test('Reload first issues only read-only diagnostics with both buttons disabled', () => {
    const h = harness(); h.click();
    assert.match(h.request(), /command=get_build_identity\n/);
    assert.doesNotMatch(h.request(), /command=reload_plugins/);
    assert.equal(h.state().button.enabled, false);
    assert.equal(h.state().diagnosticsButton.enabled, false);
    assert.equal(h.reads(), 0);
});
test('verified diagnostic reply issues a fresh scan request and baseline', () => {
    const h = harness(); h.click(); const id = h.state().requestId;
    h.response(); h.poll();
    assert.match(h.request(), /command=reload_plugins\n/);
    assert.notEqual(h.state().requestId, id);
    assert.equal(h.reads(), 1);
    assert.equal(h.state().waiting, true);
});
test('Diagnostics checks identity but never scans or reads the registry', () => {
    const h = harness(); h.diagnostics(); h.response(); h.poll();
    assert.equal(h.request(), undefined);
    assert.equal(h.reads(), 0);
    assert.match(h.state().status.text, /Build match verified. No plugins scanned/);
    assert.match(h.state().identityText.text, new RegExp(expected.build_id));
    assert.equal(h.state().diagnosticsButton.enabled, true);
});
for (const [field, value] of Object.entries({
    agent_build_id: 'different-build', agent_git_commit: 'b'.repeat(40),
    agent_source_clean: 'false', agent_target: 'x86_64-apple-darwin', agent_version: '0.0.1'
})) {
    test('mismatched ' + field + ' blocks native scan', () => {
        const h = harness(); h.click(); h.reply({[field]: value}); h.poll();
        assert.match(h.state().status.text, /identity mismatch/);
        assert.equal(h.request(), undefined);
        assert.equal(h.reads(), 0);
        assert.equal(h.state().waiting, false);
    });
    test('missing ' + field + ' from legacy Agent blocks scan', () => {
        const h = harness(); h.click(); h.reply({[field]: undefined}); h.poll();
        assert.match(h.state().status.text, /identity missing/);
        assert.equal(h.request(), undefined);
        assert.equal(h.reads(), 0);
    });
}
test('duplicate identity fields cannot overwrite an incompatible Agent', () => {
    const h = harness(); h.click(); h.reply();
    const file = [...h.files.keys()].find(x => x.endsWith('response.txt'));
    h.raw(h.files.get(file) + 'agent_build_id=another\n'); h.poll();
    assert.match(h.state().status.text, /Duplicate bridge field/);
    assert.equal(h.request(), undefined);
});
test('diagnostic error must never start scan even with matching metadata', () => {
    const h = harness(); h.click(); h.reply({status: 'error'}); h.poll();
    assert.match(h.state().status.text, /diagnostics failed/);
    assert.equal(h.reads(), 0); assert.equal(h.request(), undefined);
});
test('noop is not a successful identity handshake', () => {
    const h = harness(); h.click(); h.reply({status: 'noop'}); h.poll();
    assert.match(h.state().status.text, /diagnostics failed/);
    assert.equal(h.reads(), 0);
});
test('diagnostic timeout explicitly reports scan not started', () => {
    const h = harness(); h.click(); h.advance(30001); h.poll();
    assert.match(h.state().status.text, /diagnostics timed out; scan not started/);
    assert.doesNotMatch(h.request(), /command=reload_plugins/);
});
test('old diagnostic timer cannot process a scan response or add polling', () => {
    const h = harness(); h.click(); const oldId = h.state().requestId;
    h.response(); h.poll(); const count = h.scheduled.length;
    h.response(); h.poll(oldId);
    assert.equal(h.scheduled.length, count);
    assert.equal(h.state().waiting, true);
    assert.equal(h.reads(), 1);
    h.poll(); assert.equal(h.state().waiting, false);
});
test('old diagnostic reply cannot complete a later scan', () => {
    const h = harness(); h.click(); const oldId = h.state().requestId;
    h.response(); h.poll(); h.response('success', 'stale', oldId); h.poll();
    assert.equal(h.state().waiting, true);
    assert.equal(h.reads(), 1);
});
test('scan reply is reverified and rejects a switched Agent identity', () => {
    const h = harness(); h.startScan(); h.registry(['Existing', 'New']);
    h.reply({agent_build_id: 'switched-build'}); h.poll();
    assert.match(h.state().status.text, /identity mismatch/);
    assert.match(h.state().status.text, /Scan result unverified/);
    assert.doesNotMatch(h.state().status.text, /Registry: 1 added/);
});
test('Diagnostics and Reload share the pending-operation guard', () => {
    const h = harness(); h.diagnostics(); const request = h.request();
    h.click(); h.diagnostics();
    assert.equal(h.request(), request); assert.equal(h.scheduled.length, 1);
});
test('raw unstamped source cannot dispatch a scan even through its handler', () => {
    const h = harness(template); h.click();
    assert.equal(h.state().button.enabled, false);
    assert.equal(h.request(), undefined);
    assert.match(h.state().status.text, /Unbuilt panel/);
});
test('message content is never executed or relied on as identity', () => {
    const h = harness(); h.click();
    h.reply({message: 'throw Error("execute attack")'}); h.poll();
    assert.match(h.request(), /command=reload_plugins/);
});
test('unfinished response cannot initiate scan', () => {
    const h = harness(); h.click(); h.reply();
    const file = [...h.files.keys()].find(x => x.endsWith('response.txt'));
    h.raw(h.files.get(file).trimEnd()); h.poll();
    assert.match(h.state().status.text, /Incomplete/); assert.equal(h.reads(), 0);
});
test('response size is bounded before consuming the file', () => {
    const h = harness(); h.click(); h.raw('x'.repeat(16385)); h.poll();
    assert.match(h.state().status.text, /Oversized/); assert.equal(h.reads(), 0);
});
test('pre-existing request is preserved rather than overwritten', () => {
    const h = harness(); h.pending('another-client'); h.click();
    assert.equal(h.request(), 'another-client');
    assert.match(h.state().status.text, /Bridge busy/);
});
test('request close failure prevents publication', () => {
    const h = harness(); h.faults.close = true; h.click();
    assert.equal(h.request(), undefined);
    assert.match(h.state().status.text, /Cannot write bridge request/);
});
test('failed response removal prevents scan dispatch', () => {
    const h = harness(); h.click(); h.reply(); h.faults.remove = true; h.poll();
    assert.equal(h.request(), undefined);
    assert.match(h.state().status.text, /Cannot consume bridge response/);
});
test('matching reply ends polling and restores both buttons', () => {
    const h = harness(); h.diagnostics(); h.response(); h.poll();
    assert.equal(h.cancelled.length, 1);
    const count = h.scheduled.length; h.poll();
    assert.equal(h.scheduled.length, count);
    assert.equal(h.state().button.enabled, true);
    assert.equal(h.state().diagnosticsButton.enabled, true);
});
