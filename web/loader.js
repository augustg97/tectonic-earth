/* Tectonic Earth -- the request broker and the pure time policy.

   index.html loads this before app.js; build_site.py inlines it into the
   deployed page in the same order. It has no DOM and no three.js in it, so
   build/test_loader.mjs can load it into Node and test the contracts below
   against the shipped timeline.

   Adapted from Tectonic Atlas's asset-loader.js and surface-policy.js
   (commit cb57e9f, 2026-09-06) for the port of 2026-09-07. The parts of
   Atlas's policy that belonged to its lighter renderer -- its field subset,
   its mesh caps -- are deliberately not here; the original terrain shader
   decides what it needs (see FIELD_KINDS in app.js).

   THE BROKER. One bounded queue for every field, sheet and imagery fetch:
   the same URL asked for twice is one request; a request's priority is
   raised when a later caller wants it sooner; the keyframes the viewer is
   at come first; and when the viewer seeks somewhere else, queued and active
   requests for keyframes no longer wanted are cancelled (aborted) rather
   than left to drain ahead of the new target. Six concurrent fetches and a
   small compressed LRU are Atlas's starting settings, not constants of the
   hardware; the browser's HTTP cache remains the compressed archive.

   MISSING IS NOT THE SAME AS UNAVAILABLE. Only HTTP 404 and 410 mean a
   field is genuinely absent (not every keyframe has every kind). A timeout,
   an abort, a 5xx or a network failure rejects with a retryable error, and a
   request superseded by a seek rejects with `superseded` set -- the caller
   must not record either as a missing field. fetch is called as a FUNCTION:
   a browser rejects fetch invoked as a method with a non-Window receiver. */
(function (root) {
  class TectonicLoader {
    constructor({fetcher, concurrency = 6, maxBytes = 8 * 1024 * 1024} = {}) {
      // Bind at CALL time, not construction time: the verification driver
      // wraps window.fetch to simulate latency after the app has booted.
      this.fetcher = fetcher ? (...args) => fetcher(...args) : (...args) => fetch(...args);
      this.concurrency = concurrency;
      this.maxBytes = maxBytes;
      this.active = 0;
      this.queue = [];
      this.pending = new Map();
      this.cache = new Map();
      this.bytes = 0;
      this.running = new Set();
      this.frames = null;          // keyframes still wanted (null: everything)
      this.primaryFrames = new Set();
      /* Measured latency, an EMA of successful fetches in ms, so the playback
         look-ahead can be sized by what the connection actually does rather
         than by a constant. Counters are for the perf HUD and the harness. */
      this.stats = {fetched: 0, bytes: 0, cancelled: 0, failed: 0, missing: 0, msEMA: 0};
    }
    cancelled() {
      const error = new Error('Superseded by the selected geological time');
      error.name = 'AbortError';
      error.superseded = true;
      return error;
    }
    /* The keyframes the viewer wants now, and the two they are between.
       Queued work for any other keyframe is rejected as superseded; active
       requests for them are aborted. Requests without a frame (imagery, the
       manifest) are never touched. */
    retargetFrames(frames, primary) {
      this.frames = new Set(frames);
      this.primaryFrames = new Set(primary);
      const stale = (job) => job.frame !== null && !this.frames.has(job.frame);
      this.queue = this.queue.filter((job) => {
        if (!stale(job)) return true;
        this.pending.delete(job.url);
        this.stats.cancelled++;
        job.reject(this.cancelled());
        return false;
      });
      for (const job of this.running)
        if (stale(job) && !job.cancelled) {
          job.cancelled = true;
          this.stats.cancelled++;
          if (job.controller) job.controller.abort();
        }
      this.pump();
    }
    get(url, priority = 0, frame = null) {
      if (frame !== null && this.frames && !this.frames.has(frame))
        return Promise.reject(this.cancelled());
      if (this.cache.has(url)) {
        const value = this.cache.get(url);
        this.cache.delete(url);
        this.cache.set(url, value);
        return Promise.resolve(value);
      }
      if (this.pending.has(url)) {
        const job = this.pending.get(url);
        job.priority = Math.max(job.priority, priority);
        // A frame that has become current promotes its queued work.
        if (frame !== null && job.frame !== null && this.primaryFrames.has(frame)) job.frame = frame;
        return job.promise;
      }
      const job = {url, priority, frame, cancelled: false, controller: null};
      job.promise = new Promise((resolve, reject) => {
        job.resolve = resolve;
        job.reject = reject;
      });
      this.pending.set(url, job);
      this.queue.push(job);
      this.pump();
      return job.promise;
    }
    async run(job) {
      let error;
      for (let attempt = 0; attempt < 2; attempt++) {
        if (job.cancelled) throw this.cancelled();
        job.controller = new AbortController();
        const timeout = setTimeout(() => job.controller.abort(), 15000);
        const t0 = (typeof performance !== 'undefined' ? performance : Date).now();
        try {
          const response = await this.fetcher(job.url, {
            priority: job.priority > 5 ? 'high' : 'low',
            signal: job.controller.signal,
          });
          if (!response.ok) {
            const e = new Error('Asset request returned ' + response.status);
            e.status = response.status;
            throw e;
          }
          const blob = await response.blob();
          const ms = (typeof performance !== 'undefined' ? performance : Date).now() - t0;
          this.stats.fetched++;
          this.stats.bytes += blob.size;
          this.stats.msEMA = this.stats.msEMA ? this.stats.msEMA * 0.8 + ms * 0.2 : ms;
          if (blob.size <= this.maxBytes) {
            this.cache.set(job.url, blob);
            this.bytes += blob.size;
            while (this.bytes > this.maxBytes && this.cache.size) {
              const key = this.cache.keys().next().value;
              this.bytes -= this.cache.get(key).size;
              this.cache.delete(key);
            }
          }
          return blob;
        } catch (e) {
          if (job.cancelled) throw this.cancelled();
          error = e;
          if (e.status === 404 || e.status === 410) { this.stats.missing++; break; }
          if (attempt === 0) await new Promise((r) => setTimeout(r, 200));
        } finally {
          clearTimeout(timeout);
        }
      }
      this.stats.failed++;
      throw error;
    }
    pump() {
      const rank = (job) =>
        job.frame === null
          ? job.priority
          : (this.primaryFrames.has(job.frame) ? 100 : 0) + job.priority;
      this.queue.sort((a, b) => rank(b) - rank(a));
      while (this.active < this.concurrency && this.queue.length) {
        const job = this.queue.shift();
        this.active++;
        this.running.add(job);
        this.run(job)
          .then(job.resolve, job.reject)
          .finally(() => {
            this.active--;
            this.running.delete(job);
            this.pending.delete(job.url);
            this.pump();
          });
      }
    }
    /* True for an error a caller may retry later; false for a genuinely
       absent asset or a superseded request. */
    static retryable(error) {
      return !(error && (error.superseded || error.status === 404 || error.status === 410));
    }
  }

  const TectonicPolicy = {
    /* THE EXACT TIME BRACKET. Binary search over the ascending keyframe ages:
       an age that IS a keyframe returns that keyframe alone ({i,j:i,t:0}), a
       fractional age its actual adjacent pair, the ends clamp. The old linear
       scan returned (the next younger keyframe, this one, t=1) at an exact
       keyframe, so every marker jump bound the interval fields of the
       neighbour (README 7.16). A non-finite age is the first keyframe rather
       than an exception: this runs inside the render loop. */
    frameAt(ages, age) {
      const n = ages.length;
      if (!n) return {i: 0, j: 0, t: 0};
      if (!Number.isFinite(age) || age <= ages[0]) return {i: 0, j: 0, t: 0};
      if (age >= ages[n - 1]) return {i: n - 1, j: n - 1, t: 0};
      let lo = 0, hi = n - 1;
      while (lo <= hi) {
        const mid = (lo + hi) >> 1;
        if (ages[mid] === age) return {i: mid, j: mid, t: 0};
        if (ages[mid] < age) lo = mid + 1;
        else hi = mid - 1;
      }
      return {i: hi, j: lo, t: (age - ages[hi]) / (ages[lo] - ages[hi])};
    },
    /* Clouds are a paused-time layer: geological playback exposes the
       surface, and hiding them never changes the user's layer setting. */
    cloudsVisible(state) {
      return !state.playing && state.shade !== 'schem' && state.layers.clouds !== false;
    },
    weatherActive(state, hidden) {
      return !hidden && TectonicPolicy.cloudsVisible(state) && state.layers.weather !== false;
    },
    /* Weather seconds per rendered frame: real time, clamped at a tenth of a
       second so returning to a tab does not leap through weather phases. */
    weatherStep(milliseconds, active) {
      return active ? Math.max(0, Math.min(0.1, milliseconds / 1000)) : 0;
    },
    /* How many keyframes AHEAD playback should keep warm: enough to cover a
       fetch, a decode and two seconds of slack at this speed, clamped so the
       fastest playback stays fed without warming the whole timeline. */
    lookahead(speedMyrPerS, fetchMs, decodeMs, lean) {
      if (lean) return 2;
      const secs = ((fetchMs || 300) + (decodeMs || 150)) / 1000 + 2.0;
      return Math.max(3, Math.min(8, Math.ceil((speedMyrPerS || 3) * secs / 5)));
    },
    /* Modelled global mean surface temperature at an age, from the shipped
       timeline's gmst column: exact at a keyframe, linear between adjacent
       keyframes, clamped at the ends. Returns null for empty or malformed
       data. Never sorts the timeline: its indices address the fields. */
    gmstAt(timeline, age) {
      if (!Array.isArray(timeline) || !timeline.length || !Number.isFinite(age)) return null;
      const ages = timeline.map((f) => f && f.age);
      if (ages.some((a) => !Number.isFinite(a))) return null;
      const f = TectonicPolicy.frameAt(ages, age);
      const A = timeline[f.i], B = timeline[f.j];
      if (!Number.isFinite(A.gmst) || !Number.isFinite(B.gmst)) return null;
      return A.gmst + (B.gmst - A.gmst) * f.t;
    },
    /* The chart's axes: 1000 Ma at the left edge, the present 80% across,
       +250 Myr at the right; temperature on a fixed scale that the data must
       fit inside, widened (never clipped) if a future table exceeds it. */
    chartX(age, width) {
      return (1000 - age) / 1250 * width;
    },
    chartScale(timeline) {
      let lo = -50, hi = 40;
      for (const f of timeline || []) {
        if (!f || !Number.isFinite(f.gmst)) continue;
        if (f.gmst < lo) lo = Math.floor(f.gmst / 10) * 10 - 10;
        if (f.gmst > hi) hi = Math.ceil(f.gmst / 10) * 10 + 10;
      }
      return {lo, hi};
    },
    chartY(gmst, scale, top, bottom) {
      const c = Math.max(scale.lo, Math.min(scale.hi, gmst));
      return bottom - ((c - scale.lo) / (scale.hi - scale.lo)) * (bottom - top);
    },
  };

  root.TectonicLoader = TectonicLoader;
  root.TectonicPolicy = TectonicPolicy;
})(typeof globalThis !== 'undefined' ? globalThis : this);
