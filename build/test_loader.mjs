/* Contract tests for web/loader.js against the shipped timeline.

       node build/test_loader.mjs           (Node 18+; no packages)

   Adapted from Tectonic Atlas's surface.test.mjs and earth.test.mjs for the
   port of 2026-09-07. What these protect: an exact keyframe binds itself
   alone; every fractional age is bracketed by its real neighbours; the
   broker deduplicates, bounds its cache, retries transient failures once,
   never retries a real 404, cancels superseded work on a seek, and calls
   fetch as a function; the weather clock cannot leap; and the GMST chart
   reproduces the anchor values the brief names. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const here = new URL('.', import.meta.url);
const read = (p) => fs.readFileSync(new URL(p, here), 'utf8');
const context = {AbortSignal, AbortController, setTimeout, clearTimeout, fetch, performance, Date, Blob};
vm.runInNewContext(read('../web/loader.js'), context);
const {TectonicLoader, TectonicPolicy: policy} = context;
// Objects made inside the vm realm carry that realm's Object.prototype, which
// deepStrictEqual compares; flatten them before comparing.
const plain = (o) => JSON.parse(JSON.stringify(o));
const timeline = JSON.parse(read('../web/timeline.json'));
const ages = timeline.map((f) => f.age);

test('the timeline is 251 keyframes, ascending, 5 Myr apart, -250 to 1000', () => {
  assert.equal(timeline.length, 251);
  assert.equal(ages[0], -250);
  assert.equal(ages.at(-1), 1000);
  ages.slice(1).forEach((a, i) => assert.equal(a - ages[i], 5));
});

test('an exact keyframe uses itself alone; every fractional age is bracketed', () => {
  for (let i = 0; i < ages.length; i++) {
    const f = policy.frameAt(ages, ages[i]);
    assert.deepEqual(plain(f), {i, j: i, t: 0});
  }
  for (let age = -249.75; age < 1000; age += 0.5) {
    const f = policy.frameAt(ages, age);
    if (ages.includes(age)) continue;
    assert.equal(f.j, f.i + 1);
    assert.ok(ages[f.i] < age && age < ages[f.j]);
    assert.ok(f.t > 0 && f.t < 1);
    assert.ok(Math.abs(ages[f.i] * (1 - f.t) + ages[f.j] * f.t - age) < 1e-8);
  }
  assert.deepEqual(plain(policy.frameAt(ages, -1000)), {i: 0, j: 0, t: 0});
  assert.deepEqual(plain(policy.frameAt(ages, 5000)), {i: 250, j: 250, t: 0});
  assert.deepEqual(plain(policy.frameAt(ages, NaN)), {i: 0, j: 0, t: 0}, 'a bad age must not throw inside the render loop');
  // The present sits between the last future keyframe and the first past one.
  assert.deepEqual(plain(policy.frameAt(ages, 0)), {i: 50, j: 50, t: 0});
  assert.deepEqual(plain(policy.frameAt(ages, 0.5)), {i: 50, j: 51, t: 0.1});
  assert.deepEqual(plain(policy.frameAt(ages, -0.5)), {i: 49, j: 50, t: 0.9});
});

test('requests deduplicate and keep only a bounded compressed cache', async () => {
  let calls = 0, active = 0, peak = 0;
  const loader = new TectonicLoader({
    concurrency: 2,
    maxBytes: 15,
    fetcher: async () => {
      calls++; active++; peak = Math.max(peak, active);
      await new Promise((r) => setTimeout(r, 5));
      active--;
      return {ok: true, blob: async () => new Blob(['1234567890'])};
    },
  });
  await Promise.all([loader.get('a'), loader.get('a'), loader.get('b'), loader.get('c')]);
  assert.equal(calls, 3);
  assert.equal(peak, 2);
  assert.ok(loader.bytes <= 15);
  const cached = [...loader.cache.keys()][0];
  await loader.get(cached);
  assert.equal(calls, 3, 'a cached blob is not fetched again');
  assert.equal(loader.stats.fetched, 3);
  assert.ok(loader.stats.msEMA > 0, 'latency is measured');
});

test('fetch is called as a function, never as a method on the loader', async () => {
  const loader = new TectonicLoader({
    fetcher: function () {
      assert.equal(this, undefined);
      return Promise.resolve({ok: true, blob: async () => new Blob(['ok'])});
    },
  });
  assert.equal((await loader.get('browser-receiver')).size, 2);
});

test('a transient failure retries once; a real 404 fails at once and is marked missing', async () => {
  let calls = 0;
  const loader = new TectonicLoader({
    fetcher: async () => {
      calls++;
      return calls === 1 ? {ok: false, status: 503} : {ok: true, blob: async () => new Blob(['ok'])};
    },
  });
  assert.equal((await loader.get('retry')).size, 2);
  assert.equal(calls, 2);
  let missing = 0;
  const absent = new TectonicLoader({fetcher: async () => { missing++; return {ok: false, status: 404}; }});
  await assert.rejects(absent.get('missing'), (e) => e.status === 404 && !TectonicLoader.retryable(e));
  assert.equal(missing, 1);
  assert.equal(absent.stats.missing, 1);
  let down = 0;
  const server = new TectonicLoader({fetcher: async () => { down++; return {ok: false, status: 500}; }});
  await assert.rejects(server.get('down'), (e) => e.status === 500 && TectonicLoader.retryable(e));
  assert.equal(down, 2, 'one retry, then the caller decides');
});

test('a seek cancels stale queued and active requests without retrying them', async () => {
  const calls = [];
  const loader = new TectonicLoader({
    concurrency: 1,
    fetcher: (url, {signal}) => {
      calls.push(url);
      if (url === 'old' || url === 'queued-old')
        return new Promise((resolve, reject) => signal.addEventListener('abort', () => reject(new Error('aborted'))));
      return Promise.resolve({ok: true, blob: async () => new Blob([url])});
    },
  });
  const old = assert.rejects(loader.get('old', 25, 1), (e) => e.name === 'AbortError' && e.superseded && !TectonicLoader.retryable(e));
  const stale = assert.rejects(loader.get('queued-old', 25, 2), (e) => e.superseded);
  loader.retargetFrames([50, 51], [50, 51]);
  assert.equal(await (await loader.get('current', 20, 50)).text(), 'current');
  await Promise.all([old, stale]);
  assert.deepEqual(calls, ['old', 'current']);
  assert.equal(loader.stats.failed, 0, 'a superseded request is not a failure');
  assert.equal(loader.queue.length, 0);
  assert.equal(loader.stats.cancelled, 2);
  await assert.rejects(loader.get('elsewhere', 5, 7), (e) => e.superseded, 'a frame outside the window is refused up front');
  await loader.get('imagery', 1, null);
});

test('the pair comes first, and a later caller raises a queued request', async () => {
  const order = [];
  const loader = new TectonicLoader({
    concurrency: 1,
    fetcher: async (url) => { order.push(url); await new Promise((r) => setTimeout(r, 2)); return {ok: true, blob: async () => new Blob(['x'])}; },
  });
  loader.retargetFrames([10, 11, 12, 13], [11, 12]);
  const p = [loader.get('spec13', 5, 13), loader.get('spec10', 5, 10), loader.get('pairA', 5, 11), loader.get('pairB', 20, 12)];
  loader.get('spec10', 40, 10);   // the same URL, wanted sooner now
  await Promise.all(p);
  assert.equal(order[0], 'spec13', 'the first request was already running');
  assert.deepEqual(order.slice(1), ['pairB', 'pairA', 'spec10']);
});

test('clouds hide during playback and the weather clock cannot leap', () => {
  const state = {playing: false, view: 'globe', shade: 'sat', layers: {clouds: true, weather: true}};
  assert.equal(policy.cloudsVisible(state), true);
  assert.equal(policy.weatherActive(state, false), true);
  assert.equal(policy.cloudsVisible({...state, playing: true}), false);
  assert.equal(policy.cloudsVisible({...state, layers: {clouds: false}}), false);
  assert.equal(policy.cloudsVisible({...state, layers: {clouds: true, weather: false}}), true, 'animation off keeps the clouds');
  assert.equal(policy.weatherActive({...state, layers: {clouds: true, weather: false}}, false), false);
  assert.equal(policy.weatherActive(state, true), false, 'a hidden tab freezes weather');
  assert.equal(policy.weatherStep(1000 / 60, true), 1 / 60);
  assert.equal(policy.weatherStep(60000, true), 0.1);
  assert.equal(policy.weatherStep(500, false), 0);
});

test('the playback look-ahead follows speed and measured latency, bounded', () => {
  assert.equal(policy.lookahead(3, 300, 150, false), 3);
  assert.equal(policy.lookahead(10, 300, 150, false), 5);
  assert.equal(policy.lookahead(10, 1500, 400, false), 8);
  assert.equal(policy.lookahead(10, 20000, 400, false), 8, 'never the whole timeline');
  assert.equal(policy.lookahead(10, 300, 150, true), 2, 'constrained links stay lean');
});

test('the GMST graph reproduces the anchor values and interpolates the shipped records', () => {
  const g = (age) => policy.gmstAt(timeline, age);
  assert.equal(g(1000), 20.0);
  assert.equal(g(300), 15.0);
  assert.equal(g(0), 14.4);
  assert.equal(g(-250), 24.0);
  assert.ok(Math.abs(g(66) - 27.36) < 1e-9, '66 Ma is the 65/70 Ma records interpolated: ' + g(66));
  assert.ok(Math.abs(g(302.5) - 14.85) < 1e-9);
  for (const f of timeline) assert.equal(g(f.age), f.gmst, 'exact at ' + f.age);
  for (let i = 0; i < 250; i++) {
    const a = timeline[i], b = timeline[i + 1];
    assert.ok(Math.abs(g(a.age + 2.5) - (a.gmst + b.gmst) / 2) < 1e-9);
  }
  assert.equal(g(2000), 20.0, 'clamped at the deep end');
  assert.equal(g(-400), 24.0, 'clamped at the future end');
  assert.equal(policy.gmstAt([], 0), null);
  assert.equal(policy.gmstAt(null, 0), null);
  assert.equal(policy.gmstAt([{age: 0}], 0), null, 'a record without gmst is malformed, not zero');
  assert.equal(policy.gmstAt(timeline, NaN), null);
  assert.equal(policy.chartX(1000, 272), 0);
  assert.ok(Math.abs(policy.chartX(0, 272) - 217.6) < 1e-9, 'the present sits 80% across');
  assert.equal(policy.chartX(-250, 272), 272);
  const scale = policy.chartScale(timeline);
  assert.deepEqual(plain(scale), {lo: -50, hi: 40}, 'the shipped -23..33 C fits the fixed scale');
  assert.ok(Math.abs(policy.chartY(0, scale, 10, 62) - (62 - (50 / 90) * 52)) < 1e-9);
  const wide = policy.chartScale([{age: 0, gmst: 61}]);
  assert.ok(wide.hi >= 61, 'a hotter future table widens the scale instead of clipping');
});
