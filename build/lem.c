/* The landscape-evolution core of Tectonic Earth's relief bake (lem.py).

   Stream-power incision with n = 1, solved implicitly down the receiver tree
   (Braun & Willett 2013, "A very efficient O(n), implicit and parallel method
   to solve the stream power equation governing fluvial incision and landscape
   evolution", Geomorphology 180-181), with drainage routed over depressions
   by a priority flood (Barnes, Lehman & Mulla 2014), so a closed hollow fills
   by deposition instead of trapping the network.

   The grid is the app's equirectangular one: H rows north to south, W columns,
   longitude periodic. Cell widths come in per row (dx[r], metres east-west)
   plus one dy (metres north-south). Only ACTIVE cells evolve; every inactive
   cell is fixed, and inactive cells bordering the active set are the base
   level the flood starts from (the belt's foothills, the sea).

   Built by lem.py with the system C compiler; no Python headers, only plain
   arrays passed through ctypes. */
#include <stdint.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

typedef struct { float h; int32_t i; } Node;

static void heap_push(Node *hp, int64_t *n, Node v) {
    int64_t k = (*n)++;
    while (k > 0) {
        int64_t p = (k - 1) >> 1;
        if (hp[p].h <= v.h) break;
        hp[k] = hp[p]; k = p;
    }
    hp[k] = v;
}

static Node heap_pop(Node *hp, int64_t *n) {
    Node top = hp[0], last = hp[--(*n)];
    int64_t k = 0;
    for (;;) {
        int64_t c = 2 * k + 1;
        if (c >= *n) break;
        if (c + 1 < *n && hp[c + 1].h < hp[c].h) c++;
        if (hp[c].h >= last.h) break;
        hp[k] = hp[c]; k = c;
    }
    hp[k] = last;
    return top;
}

static const int DR[8] = {-1, -1, -1, 0, 0, 1, 1, 1};
static const int DC[8] = {-1, 0, 1, -1, 1, -1, 0, 1};

static inline float ndist(int r, int k, const float *dx, float dy) {
    float ex = dx[r] * (float)DC[k], ey = dy * (float)DR[k];
    return sqrtf(ex * ex + ey * ey);
}

/* Route the active cells: returns the number of active cells ordered.
   hf    out: the flooded surface (h raised to spill level plus epsilon)
   rec   out: each active cell's receiver (steepest descent on hf); -1 elsewhere
   order out: active cells from base level upstream (receivers before donors)
   dist  out: distance to the receiver, metres */
int lem_route(int H, int W, const float *h, const uint8_t *active,
              const float *dx, float dy, float eps,
              float *hf, int32_t *rec, int32_t *order, float *dist)
{
    int64_t N = (int64_t)H * W, nh = 0, no = 0;
    uint8_t *seen = (uint8_t *)calloc(N, 1);
    Node *hp = (Node *)malloc(sizeof(Node) * (N + 8));
    if (!seen || !hp) { free(seen); free(hp); return -1; }
    for (int64_t i = 0; i < N; i++) { hf[i] = h[i]; rec[i] = -1; dist[i] = 0.0f; }
    /* seeds: every fixed cell that touches an active one */
    for (int r = 0; r < H; r++) {
        for (int c = 0; c < W; c++) {
            int64_t i = (int64_t)r * W + c;
            if (active[i]) continue;
            int touch = 0;
            for (int k = 0; k < 8 && !touch; k++) {
                int rr = r + DR[k]; if (rr < 0 || rr >= H) continue;
                int cc = (c + DC[k] + W) % W;
                if (active[(int64_t)rr * W + cc]) touch = 1;
            }
            if (touch) { seen[i] = 1; Node v = {hf[i], (int32_t)i}; heap_push(hp, &nh, v); }
        }
    }
    while (nh > 0) {
        Node cur = heap_pop(hp, &nh);
        int r = (int)(cur.i / W), c = (int)(cur.i % W);
        for (int k = 0; k < 8; k++) {
            int rr = r + DR[k]; if (rr < 0 || rr >= H) continue;
            int cc = (c + DC[k] + W) % W;
            int64_t j = (int64_t)rr * W + cc;
            if (seen[j] || !active[j]) continue;
            seen[j] = 1;
            float lift = hf[cur.i] + eps * ndist(r, k, dx, dy);
            if (hf[j] < lift) hf[j] = lift;
            rec[j] = cur.i;                              /* the flood parent, a valid fallback */
            dist[j] = ndist(r, k, dx, dy);
            order[no++] = (int32_t)j;
            Node v = {hf[j], (int32_t)j};
            heap_push(hp, &nh, v);
        }
    }
    /* steepest descent on the flooded surface, among strictly lower cells: the
       flood order is non-decreasing in hf, so any strictly lower receiver was
       ordered first and the order stays a valid stack */
    for (int64_t q = 0; q < no; q++) {
        int64_t i = order[q];
        int r = (int)(i / W), c = (int)(i % W);
        float best = 0.0f; int32_t bj = -1; float bd = 0.0f;
        for (int k = 0; k < 8; k++) {
            int rr = r + DR[k]; if (rr < 0 || rr >= H) continue;
            int cc = (c + DC[k] + W) % W;
            int64_t j = (int64_t)rr * W + cc;
            float d = ndist(r, k, dx, dy);
            float s = (hf[i] - hf[j]) / d;
            if (s > best) { best = s; bj = (int32_t)j; bd = d; }
        }
        if (bj >= 0) { rec[i] = bj; dist[i] = bd; }
    }
    free(seen); free(hp);
    return (int)no;
}

/* Drainage area (square metres times the rain weight) accumulated down the tree. */
void lem_area(int64_t no, const int32_t *order, const int32_t *rec,
              const float *cellw, float *A)
{
    for (int64_t q = no - 1; q >= 0; q--) {
        int64_t i = order[q];
        A[i] += cellw[i];
        if (rec[i] >= 0) A[rec[i]] += A[i];
    }
}

/* One implicit stream-power step: h <- (h + dt U + F h_rec) / (1 + F),
   F = K dt A^m / L, receivers first. Inactive cells keep their height. */
void lem_incise(int64_t no, const int32_t *order, const int32_t *rec,
                const float *dist, const float *A, const float *K,
                float m, float dt, const float *U, float *h)
{
    for (int64_t q = 0; q < no; q++) {
        int64_t i = order[q];
        int64_t j = rec[i];
        float hi = h[i] + dt * U[i];
        if (j < 0 || dist[i] <= 0.0f) { h[i] = hi; continue; }
        float F = K[i] * dt * powf(A[i], m) / dist[i];
        float hn = (hi + F * h[j]) / (1.0f + F);
        h[i] = hn;
    }
}

/* Explicit hillslope diffusion on the active cells (kappa dt / dx^2 kept
   under the stability bound by the caller). */
void lem_diffuse(int H, int W, const uint8_t *active, const float *dx, float dy,
                 float kdt, const float *h, float *out)
{
    for (int r = 0; r < H; r++) {
        /* explicit diffusion is stable only while ax + ay < 1/2, and toward a
           pole the east-west cell shrinks with cos(lat): clamp each axis */
        float ax = fminf(kdt / (dx[r] * dx[r]), 0.2f), ay = fminf(kdt / (dy * dy), 0.2f);
        for (int c = 0; c < W; c++) {
            int64_t i = (int64_t)r * W + c;
            if (!active[i]) { out[i] = h[i]; continue; }
            int cl = (c - 1 + W) % W, cr = (c + 1) % W;
            float hn = r > 0 ? h[(int64_t)(r - 1) * W + c] : h[i];
            float hs = r < H - 1 ? h[(int64_t)(r + 1) * W + c] : h[i];
            float he = h[(int64_t)r * W + cr], hw = h[(int64_t)r * W + cl];
            out[i] = h[i] + ax * (he + hw - 2.0f * h[i]) + ay * (hn + hs - 2.0f * h[i]);
        }
    }
}

/* Threshold hillslopes: no cell stands more than Sc * L above its receiver.
   Landsliding caps relief wherever incision outpaces the hillslopes; without
   it the interfluves between large rivers rise without bound under uplift. */
void lem_limit(int64_t no, const int32_t *order, const int32_t *rec,
               const float *dist, float Sc, float *h)
{
    for (int64_t q = 0; q < no; q++) {
        int64_t i = order[q];
        int64_t j = rec[i];
        if (j < 0) continue;
        float cap = h[j] + Sc * dist[i];
        if (h[i] > cap) h[i] = cap;
    }
}

/* The detachment-limited steady state on a given network: dh/dt = 0 with
   stream power n = 1 means each channel cell's slope is its local
   E / A^m (E = uplift over erodibility, in metres per unit of A^-m), capped
   at the threshold slope Sc. One sweep from base level upstream. Inactive
   cells (the base level) keep their height. */
void lem_steady(int64_t no, const int32_t *order, const int32_t *rec,
                const float *dist, const float *A, const float *E, float m,
                float Sc, float *h)
{
    for (int64_t q = 0; q < no; q++) {
        int64_t i = order[q];
        int64_t j = rec[i];
        if (j < 0) continue;
        float s = E[i] * powf(fmaxf(A[i], 1.0f), -m);
        if (s > Sc) s = Sc;
        h[i] = h[j] + dist[i] * s;
    }
}
