'use strict';
// Host mocks exercise the shipped JSX. They are NOT live After Effects evidence.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(process.env.PANEL_SOURCE || path.join(__dirname, '../ui/AE Hot Loader.jsx'), 'utf8');

function harness() {
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
    File.prototype.open = function(mode) { this.mode = mode; return !faults.open; };
    File.prototype.read = function() { if (faults.read) throw Error('read failed'); return files.get(this.fsName); };
    File.prototype.write = function(text) { if (faults.write) return false; files.set(this.fsName, text); return true; };
    File.prototype.close = function() { closes++; return true; };
    File.prototype.remove = function() { return files.delete(this.fsName); };
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
    const app = {scheduleTask(code) { scheduled.push(code); return scheduled.length; }};
    Object.defineProperty(app, 'effects', {get() {
        registryReads++;
        if (faults.registry) throw Error('registry unavailable');
        return effects;
    }});
    Object.defineProperty(app, 'project', {get() { throw Error('Panel must not touch the project'); }});
    const context = {File, Folder, Window, Panel: function() {}, app, $: {global}, Date: Clock};
    vm.runInNewContext(source, context, {filename: 'AE Hot Loader.jsx', timeout: 1000});
    return {
        faults, files, scheduled,
        state() { return global.AEHotLoader_state; },
        click() { global.AEHotLoader_state.button.onClick(); },
        poll() { global.AEHotLoader_pollResponse(); },
        response(status = 'success', message = 'ordinary-discovery-v1: loaded:364 post_load_modules:9', id) {
            files.set(root + 'response.txt', 'version=1\nrequest_id=' + (id || this.state().requestId) + '\nstatus=' + status + '\nmessage=' + message + '\n');
        },
        raw(text) { files.set(root + 'response.txt', text); },
        registry(names) { effects = names.map(matchName => ({matchName})); },
        advance(ms) { now += ms; },
        reads() { return registryReads; },
        closes() { return closes; },
        request() { return files.get(root + 'request.txt'); }
    };
}
function complete(h, status) { h.response(status); h.poll(); return h.state().status.text; }

test('loaded binaries without registry growth are not registration success', () => {
    const h = harness(); h.click();
    assert.match(complete(h), /Registry unchanged/);
    assert.equal(h.reads(), 2);
});
test('new match name is observed, but apply/render is not claimed', () => {
    const h = harness(); h.click(); h.registry(['Existing', 'New']);
    assert.match(complete(h), /Registry: 1 added/);
    assert.match(h.state().status.text, /Apply\/render not checked/);
});
test('equal counts with replaced identities are not treated as unchanged', () => {
    const h = harness(); h.click(); h.registry(['Replacement']);
    assert.match(complete(h), /Registry changed unexpectedly: 1 removed/);
});
test('registry order changes do not imply new effects', () => {
    const h = harness(); h.registry(['A', 'B']); h.click(); h.registry(['B', 'A']);
    assert.match(complete(h), /Registry unchanged/);
});
test('duplicate match names block the request', () => {
    const h = harness(); h.registry(['Duplicate', 'Duplicate']); h.click();
    assert.match(h.state().status.text, /Duplicate effect match name/);
    assert.equal(h.request(), undefined);
    assert.equal(h.state().button.enabled, true);
});
test('unavailable baseline registry blocks scan before any write', () => {
    const h = harness(); h.faults.registry = true; h.click();
    assert.equal(h.request(), undefined);
    assert.match(h.state().status.text, /registry unavailable/);
});
test('unavailable after-registry cannot produce success', () => {
    const h = harness(); h.click(); h.faults.registry = true;
    assert.match(complete(h), /Error:.*registry unavailable/);
    assert.equal(h.state().waiting, false);
});
test('partial scan failure remains an error even when an effect appears', () => {
    const h = harness(); h.click(); h.registry(['Existing', 'New']);
    assert.match(complete(h, 'error'), /^Scan incomplete:/);
    assert.match(h.state().status.text, /Registry: 1 added/);
});
test('noop from agent does not bypass independent registry check', () => {
    const h = harness(); h.click();
    assert.match(complete(h, 'noop'), /Registry unchanged/);
});
test('unknown response version is rejected', () => {
    const h = harness(); h.click();
    h.raw('version=2\nrequest_id=' + h.state().requestId + '\nstatus=success\nmessage=PASS\n'); h.poll();
    assert.match(h.state().status.text, /Unsupported bridge response/);
});
test('unknown status is rejected', () => {
    const h = harness(); h.click();
    assert.match(complete(h, 'mystery'), /Unsupported bridge response/);
});
test('stale request identity never completes the current request', () => {
    const h = harness(); h.click(); h.response('success', 'STALE PASS', 'older-run'); h.poll();
    assert.equal(h.state().waiting, true);
    assert.doesNotMatch(h.state().status.text, /STALE PASS/);
});
test('missing response times out without claiming no work occurred', () => {
    const h = harness(); h.click(); h.advance(30001); h.poll();
    assert.match(h.state().status.text, /result unknown/);
    assert.equal(h.state().waiting, false);
});
test('late response after timeout does not overwrite the timeout result', () => {
    const h = harness(); h.click(); h.advance(30001); h.poll();
    const text = h.state().status.text; h.response(); h.poll();
    assert.equal(h.state().status.text, text);
});
test('poll read exception unlocks UI and closes the file', () => {
    const h = harness(); h.click(); h.response(); h.faults.read = true;
    const before = h.closes(); h.poll();
    assert.match(h.state().status.text, /Error:.*read failed/);
    assert.equal(h.state().button.enabled, true);
    assert.equal(h.closes(), before + 1);
});
test('double click while pending does not publish a second request', () => {
    const h = harness(); h.click(); const request = h.request(); h.advance(1); h.click();
    assert.equal(h.request(), request);
    assert.equal(h.scheduled.length, 1);
});
test('request write failure cannot publish an incomplete request', () => {
    const h = harness(); h.faults.write = true; h.click();
    assert.equal(h.request(), undefined);
    assert.match(h.state().status.text, /Cannot write bridge request/);
});
test('request publish failure is reported and UI is restored', () => {
    const h = harness(); h.faults.rename = true; h.click();
    assert.match(h.state().status.text, /Cannot publish bridge request/);
    assert.equal(h.state().button.enabled, true);
});
test('response removal follows successful consumption', () => {
    const h = harness(); h.click(); complete(h);
    assert.equal([...h.files.keys()].some(p => p.endsWith('response.txt')), false);
});
test('names resembling object properties are compared safely', () => {
    const h = harness(); h.registry(['__proto__']); h.click(); h.registry(['__proto__', 'constructor']);
    assert.match(complete(h), /Registry: 1 added/);
});
test('duplicate protocol fields are rejected, not silently overwritten', () => {
    const h = harness(); h.click();
    h.raw('version=1\nrequest_id=' + h.state().requestId + '\nstatus=error\nstatus=success\n'); h.poll();
    assert.match(h.state().status.text, /Duplicate bridge field/);
});
test('a complete scan can be repeated with a fresh registry baseline', () => {
    const h = harness(); h.click(); h.registry(['Existing', 'New']); complete(h);
    h.advance(1); h.click(); assert.match(complete(h), /Registry unchanged/);
    assert.equal(h.reads(), 4);
});
