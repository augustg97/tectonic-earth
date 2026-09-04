/* Tectonic Earth -- the application. index.html loads this after three.min.js
   and shaders.js (generated from web/shaders/*.glsl by build/check_shader.py);
   build_site.py inlines all three into the single deployed docs/index.html.
   Edit the shaders in web/shaders/, never here. */
const DEG=Math.PI/180;
const $=s=>document.querySelector(s);
/* Opening state is "press play and watch Earth's history run": start at the
   deep end, travel forward. `dir` is added to the AGE, so dir=-1 makes the age
   count down, which is time moving forwards — and on the timeline, forwards is
   left-to-right, 1000 Ma toward +250 Myr. Plate boundaries start off; they are
   a specialist overlay and they crowd the first look at the globe. */
const state={
  age:1000, view:'globe', shade:'sat', playing:false, dir:-1, speed:3,
  /* Render quality. 'auto' keeps native resolution until the measured frame
     interval says the GPU cannot -- an M1 driving a 5K display runs this
     terrain shader at 3 fps, and a slideshow is also not the model at its
     best. Auto steps the RENDER scale (terrain only -- labels, panels and
     lines are DOM/overlay and stay native-sharp) and steps back up when
     there is headroom. 'full' pins native; 'balanced'/'perf' pin lower. */
  quality:(function(){try{return localStorage.getItem('te_quality')||'auto';}catch(e){return 'auto';}})(),
  layers:{boundaries:false,vectors:false,hotspots:false,labels:true,rotate:false},
  ambient:false, rot:0, tilt:0, zoom:3.05, selPlate:null,
  // rot/tilt are the LONGITUDE and LATITUDE of the point the camera looks at.
  // gtilt and head are the Google Earth pair layered on top: how far the camera
  // leans off that point's vertical, and which way it faces once it has. Both
  // zero reproduces the old straight-down-the-normal view exactly, which is what
  // keeps this from being a regression on every framing verified so far.
  gtilt:0, head:0, spin:1, mapLon:0
};
let DATA={};   // timeline, boundaries, plates, hotspots, labels
let ELI=[], RNI=[], MOI=[], WLI=[], SFI=[], OCI=[], VLI=[], PLI=[], TCI=[], FRI=[], FQI=[], FXI=[];   // elevation / rainfall / motion / lake-depth / surface-process / ocean-structure / displacement fields
let WOLD=null, WOLD_TEX=null;         // present-day lakes minus the Holocene ones
const MOTDATA=new Map();      // keyframe -> decoded motion pixels (CPU side)
/* UNIFIED IMAGE+TEXTURE RESIDENCY (crash fix, 2026-07-30 evening).

   The first ImageBitmap loader decoded every field at fetch time and kept the
   bitmap in the per-kind arrays forever. A decoded bitmap holds its full
   uncompressed raster -- on macOS usually an IOSurface, invisible to RSS --
   and the prefetch pump fetches all ~2,510 files: measured 3,150 MB pinned
   within seconds of boot, ~19 GB by completion. The GPU process dies within
   minutes ("Aw, Snap!", error 5), fastest while dragging the globe, and the
   thrash on the way down is itself jank.

   So decoded pixels are now a WINDOW, not an archive. One cache entry per
   kind+keyframe owns BOTH the decoded bitmap and the GPU texture built from
   it; they are accounted and evicted together (never dispose one and keep the
   other -- a context restore would try to re-upload from a closed bitmap).
   The prefetch pump only warms the browser's HTTP cache, which stores the
   COMPRESSED bytes (~127 MB for the whole timeline) and is exactly the store
   the old <img> pipeline leaned on; re-decoding a frame that left the window
   is a ~1 ms disk-cache hit plus an off-thread decode.

   Budget counts w*h*8 per entry -- decoded copy plus GPU copy -- so ~4-5
   keyframes stay warm around the viewer on a desktop, fewer on low-memory
   devices. */
const TEXCACHE=new Map(); let texClock=0, _texBytes=0;
/* The floor matters: a bound PAIR accounts ~300 MB at 8 bytes/px, and a
   budget below that would evict the very textures being drawn -- permanent
   thrash. 360 keeps one pair plus a little headroom on small devices. */
const TEX_BUDGET=((navigator.deviceMemory||8)<8?360:950)*1048576;
/* Decode-ahead order is by VISUAL IMPORTANCE, not array order: elevation and
   rainfall define the frame, displacement and material coordinates define
   how time LOOKS between frames (uWarp/uMat), and the rest refine. The
   FIELD_KINDS order put m/w/d/o ahead of v/p, so at playback speed the
   decode budget was spent before the motion model ever got a slot --
   measured 33-48% of playback frames with uWarp or uMat dark. */
const KIND_PRIORITY=['e','r','v','p','w','d','o','m','t','f','q','x'];
const _bmPending=new Map();   // kind+i -> in-flight decode promise
/* Textures bound to the material in the last couple of frames are PINNED
   against eviction. Without this, a fast slider scrub floods the cache with
   new decodes, the budget evicts the least-recently-TOUCHED entries -- which
   are exactly the pair still on screen, because the scrub stopped touching
   them -- and three.js is left holding a disposed texture whose source
   bitmap is closed: the globe renders BLANK until the target pair lands. */
let _frameNo=0; const _boundAt=new Map();
/* Scrubbing = the age moved more than a keyframe for 2+ consecutive frames
   (one big frame is a JUMP and decodes immediately; a run of them is a drag).
   While scrubbing, no new decodes start at all: createImageBitmap cannot be
   cancelled, so every age the slider sweeps past would otherwise queue ahead
   of the age the user finally stops on -- measured 1.37 s from release to
   render, almost all of it stale decodes draining. The stale pair stays on
   screen (pinned above), resident spans still bind live, and the target
   decodes the moment the drag settles. */
let _scrubN=0,_scrubbing=false;
let _lastBoundE=-1;   // which elevation keyframe is on screen (diagnostics + scrub stepping)
function nearestResidentE(target){
  let bi=-1,bd=1e9;
  for(const[k,v]of TEXCACHE){
    if(k.charCodeAt(0)!==101||!v.bm)continue;   // 'e' entries only
    const i=+k.slice(1), d=Math.abs(i-target);
    if(d<bd){bd=d;bi=i;}
  }
  return bi;
}
const _bmMissing=new Set();   // kind+i whose file genuinely 404s (legit: not every keyframe has every kind)
function _cacheTouch(e){e.u=++texClock;}
function _cacheEvict(keepKey){
  while(_texBytes>TEX_BUDGET&&TEXCACHE.size>1){
    let victim=null,best=Infinity;
    for(const[k,v]of TEXCACHE){
      if(k===keepKey)continue;
      const ba=_boundAt.get(k);
      if(ba!==undefined&&_frameNo-ba<3)continue;   // on screen -- never evict
      if(v.u<best){best=v.u;victim=k;}}
    if(victim===null)break;
    const v=TEXCACHE.get(victim);
    _texBytes-=v.b;
    if(v.t)v.t.dispose();
    if(v.bm&&v.bm.close)v.bm.close();
    TEXCACHE.delete(victim);
  }
}
/* Decode one field into the residency window (idempotent, off-thread). The
   fetch is a cache hit whenever the prefetch pump has been past this file. */
function ensureBitmap(kind,i,force){
  if(!_BITMAPS)return Promise.resolve();
  /* During a scrub only ELEVATION decodes: crust shape is what "change over
     time" means on screen, the climate colouring rides uniforms that already
     track the slider, and every non-elevation decode would queue ahead of the
     next crust step. */
  if(_scrubbing&&!force&&kind!=='e')return Promise.resolve();
  const key=kind+i;
  const e0=TEXCACHE.get(key);
  if(e0&&e0.bm)return Promise.resolve();
  if(_bmMissing.has(key))return Promise.resolve();
  const p0=_bmPending.get(key); if(p0)return p0;
  const pri=(kind==='e'||kind==='r')?'high':'low';
  const p=fetch(fieldSrc(fieldFile(i,kind)),{priority:pri})
    .then(r=>{if(!r.ok)throw 0;return r.blob();})
    .then(b=>createImageBitmap(b,{imageOrientation:'flipY',
      premultiplyAlpha:'none',colorSpaceConversion:'none'}))
    .then(bm=>{
      _bmPending.delete(key);
      /* A scrub kicked decodes for every age the slider swept past; by the
         time one completes the viewer may be hundreds of Myr away. Inserting
         it would evict something wanted; close it instead -- the HTTP cache
         still holds the compressed bytes if that age comes back. */
      const cur=DATA.timeline?frameAt(state.age).i:i;
      let lim=4;
      if(_scrubbing&&kind==='e'){
        const nb=nearestResidentE(cur);
        lim=Math.max(4,nb<0?1e9:Math.abs(nb-cur));   // closer than what's shown
      }
      if(Math.abs(i-cur)>lim){bm.close&&bm.close();return;}
      const e={bm,t:null,u:0,b:bm.width*bm.height*8};
      TEXCACHE.set(key,e);_texBytes+=e.b;_cacheTouch(e);
      _cacheEvict(key);
    })
    .catch(()=>{_bmPending.delete(key);_bmMissing.add(key);});
  _bmPending.set(key,p);
  return p;
}
function fieldImage(kind,i){
  if(_BITMAPS){const e=TEXCACHE.get(kind+i);return(e&&e.bm)||null;}
  return (kind==='e'?ELI:kind==='r'?RNI:kind==='w'?WLI:kind==='d'?SFI:kind==='o'?OCI:kind==='v'?VLI:kind==='p'?PLI:kind==='t'?TCI:kind==='f'?FRI:kind==='q'?FQI:kind==='x'?FXI:MOI)[i]||null;
}
function getTex(kind,i){
  const key=kind+i;
  let e=TEXCACHE.get(key);
  let src=null;
  if(_BITMAPS){
    if(!e||!e.bm)return null;             // not decoded into the window yet
    src=e.bm;
  }else{
    src=(kind==='e'?ELI:kind==='r'?RNI:kind==='w'?WLI:kind==='d'?SFI:kind==='o'?OCI:kind==='v'?VLI:kind==='p'?PLI:kind==='t'?TCI:kind==='f'?FRI:kind==='q'?FQI:kind==='x'?FXI:MOI)[i];
    if(!src)return null;
    if(!e){e={bm:null,t:null,u:0,b:(src.width*src.height*8)||2097152};
      TEXCACHE.set(key,e);_texBytes+=e.b;}
  }
  if(!e.t){
    const t=new THREE.Texture(src);
    // Field data, not colour: keep it linear and unfiltered by mipmaps so
    // elevation isn't averaged across scales before the shader reads it.
    t.colorSpace=THREE.NoColorSpace;
    // Bitmaps are baked pre-flipped: UNPACK_FLIP_Y_WEBGL is ignored for
    // ImageBitmap uploads by spec, so flipY must not be left on.
    if(_BITMAPS)t.flipY=false;
    /* NEAREST for the plate-slot raster only. Every other field is a
       quantity and wants smoothing; a slot is a LABEL, and interpolating
       between slot 3 and slot 17 gives slot 10 -- a plate that is not there,
       whose rotation would carry that crust's texture somewhere arbitrary. */
    const nearest=(kind==='p'||kind==='q'||kind==='x');   // q: 16-bit byte pairs cannot be filtered as bytes; the shader interpolates the decoded values
    t.minFilter=nearest?THREE.NearestFilter:THREE.LinearFilter;
    t.magFilter=nearest?THREE.NearestFilter:THREE.LinearFilter;
    t.generateMipmaps=false; t.wrapS=THREE.RepeatWrapping; t.wrapT=THREE.ClampToEdgeWrapping;
    t.needsUpdate=true;
    e.t=t;
  }
  _cacheTouch(e);
  _cacheEvict(key);
  return e.t;
}
/* THE SMALL-FIELD STACK (2026-09-03). A fragment shader has 16 texture units
   on real GPUs (MAX_TEXTURE_IMAGE_UNITS: Apple/ANGLE Metal, most desktop GL)
   and 32 on the software GL the WP-10 rounds were reviewed on, so the samplers
   rounds 2-3 added linked there and failed here -- "texture image units count
   exceeds MAX_TEXTURE_IMAGE_UNITS(16)" and a black globe (README 7.17). The
   four small per-keyframe fields (_t, _f, _q, _x) now share one 1024x1024 RGBA
   texture per keyframe, composed ON THE GPU from the decoded bitmaps as they
   land: texSubImage2D through copyTextureToTexture, no canvas, so nothing is
   premultiplied and the 16-bit byte pairs of _q and _x survive. The layout is
   documented at the FRAG uniforms (stkFore, stkTect, foldTaps): _f rows 0-511
   full width; _t rows 512-767 twice side by side, so the right-hand copy wraps
   at the dateline; _q at (0,768), _x at (512,768). A stack is a TEXCACHE entry
   ('s'+i, 4 MB, no bitmap), so the budget and eviction treat it like a field;
   `have` records the bands filled so far, and bindStacks() sends a band that
   one keyframe of the pair lacks to the other, which is the per-field fallback
   the separate samplers had. Terrain shader: 20 units -> 16; check_shader.py
   counts them. */
const STK_W=1024, STK_H=1024, STK_BYTES=STK_W*STK_H*4;
const STK_BANDS={f:[[0,0]], t:[[0,512],[512,512]], q:[[0,768]], x:[[512,768]]};
let _stkZero=null; const _stkPos=new THREE.Vector2();
function stackEntry(i){
  const key='s'+i; let e=TEXCACHE.get(key);
  if(!e){
    if(!_stkZero)_stkZero=new Uint8Array(STK_BYTES);
    const t=new THREE.DataTexture(_stkZero,STK_W,STK_H,THREE.RGBAFormat,THREE.UnsignedByteType);
    t.colorSpace=THREE.NoColorSpace; t.premultiplyAlpha=false;
    t.flipY=!_BITMAPS;   // bitmaps are pre-flipped; an <img> fallback is not
    t.minFilter=THREE.LinearFilter; t.magFilter=THREE.LinearFilter; t.generateMipmaps=false;
    t.wrapS=THREE.RepeatWrapping; t.wrapT=THREE.ClampToEdgeWrapping; t.needsUpdate=true;
    e={bm:null,t:t,u:0,b:STK_BYTES,have:new Set()};
    TEXCACHE.set(key,e); _texBytes+=e.b;
  }
  return e;
}
/* Fill whichever bands of keyframe i's stack have landed. get(kind) is the
   caller's own binder (bindTex / gT / T): it may kick a decode and return
   null, in which case the band waits for a later frame, exactly as a late
   texture did. Returns the stack entry. */
function stackFill(i,get){
  const e=stackEntry(i);
  let gl=null;
  for(const k in STK_BANDS){
    if(e.have.has(k))continue;
    const src=get(k); if(!src)continue;
    const img=src.image||src;                        // a THREE.Texture, or a bare bitmap
    if(!gl){gl=renderer.getContext(); gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL,gl.NONE);}
    for(const xy of STK_BANDS[k])renderer.copyTextureToTexture(_stkPos.set(xy[0],xy[1]),{image:img},e.t);
    e.have.add(k);
  }
  _cacheTouch(e); _boundAt.set('s'+i,_frameNo);
  return e;
}
/* Bind the pair's stacks and the flags and selectors that go with them. SA is
   keyframe i's entry, SB keyframe j's (the same entry for a still). A band
   missing from one keyframe reads from the other: _t and _f from i, else j;
   the _q/_x A-taps from i, else j; their B-taps from j, else i -- "one
   missing: a still", as the separate samplers had it. */
function bindStacks(u,SA,SB){
  u.stkA.value=SA.t; u.stkB.value=SB.t;
  const hA=SA.have, hB=SB.have, has=(k)=>hA.has(k)||hB.has(k);
  u.uTect.value=has('t')?1.0:0.0;
  u.uFore.value=has('f')?1.0:0.0;
  u.uFoldOn.value=has('q')?1.0:0.0;
  u.uDrainOn.value=(has('x')&&!_sq.has('nodrain'))?1.0:0.0;
  u.uStkSel.value.set(hA.has('t')?0:1, hA.has('f')?0:1, hA.has('q')?0:1, hA.has('x')?0:1);
  u.uStkSelB.value.set(hB.has('q')?1:0, hB.has('x')?1:0);
}
/* The present frame's lake field holds the REAL lakes, traced from Natural
   Earth. Most of the big ones are Holocene: the Great Lakes date from about
   14 ka, when the Laurentide ice sheet withdrew, and Ladoga and Great Slave are
   the same story. The keyframes are 5 Myr apart, so interpolating those lakes
   out of the present frame left them visible ~4 Myr either side of today —
   the Great Lakes sitting there in the Pliocene, which is simply false.

   So they are baked separately (phan_0000_wold.webp is the present WITHOUT
   them) and the present frame's texture is swapped for that one outside the
   window they actually occupy. Forward, glacial isostatic rebound is expected
   to tilt the basins and reorganise the drainage over 10^4–10^5 years, so the
   projection stops well before the first future keyframe rather than pretending
   to 5 Myr. */
function youngLakeWeight(age){
  if(age>0.02)return 0;      // before ~20 ka they did not exist
  if(age<-0.4)return 0;      // beyond any defensible projection forward
  return 1;
}
function presentIndex(){
  if(presentIndex._i===undefined)
    presentIndex._i=DATA.timeline.findIndex(f=>Math.abs(f.age)<1e-9);
  return presentIndex._i;
}
function oldLakeTex(){
  if(!WOLD)return null;
  if(!WOLD_TEX){
    WOLD_TEX=new THREE.Texture(WOLD);
    WOLD_TEX.colorSpace=THREE.NoColorSpace;
    if(_BITMAPS&&WOLD instanceof ImageBitmap)WOLD_TEX.flipY=false;
    WOLD_TEX.minFilter=THREE.LinearFilter; WOLD_TEX.magFilter=THREE.LinearFilter;
    WOLD_TEX.generateMipmaps=false;
    WOLD_TEX.wrapS=THREE.RepeatWrapping; WOLD_TEX.wrapT=THREE.ClampToEdgeWrapping;
    WOLD_TEX.needsUpdate=true;
  }
  return WOLD_TEX;
}

/* ================= data load =================

   DATA_V busts the browser cache on the JSON data files. Pages serves them with
   max-age=600 and an ETag, but a returning viewer can sit on a stale copy well
   past that — bfcache, a background tab that never revalidates, a heuristic
   freshness window — and the symptom is silent: the app runs fine and simply
   shows yesterday's content. That has now bitten labels.json, plates_time.json
   and life.json in turn. Stamped by build/stamp_data_version.py, which
   build_site.py runs, so a deploy always changes the URL.
   Deliberately NOT applied to fields/ — those are 1,500 textures that rarely
   change and busting them on every data edit would re-download the lot.

   FIELD_V exists for the times they DO change, and is bumped BY HAND rather
   than stamped, precisely so an ordinary data edit does not trigger it. The
   elevation field was rebuilt at 2048x4096 in July 2026: same filenames, new
   contents, ~145 MB of them. Without a bust a returning viewer would keep the
   old coarse textures and see a sea floor built to constants that no longer
   match them — the same silent failure DATA_V exists to prevent, at fifty times
   the size. Bump this whenever build_fields, reskin_seafloor or anything they
   call changes what lands in web/fields. */
const DATA_V='20260904-0427';
const FIELD_V='20260804-fabric';   // bumped: two keyframes gained a _t that had none
/* ASSET BASES (WP-10, D4). The per-keyframe fields and the world sheets are
   the repository's weight; when they are hosted elsewhere -- a GitHub
   release, an object store, a second Pages site -- build_site.py stamps
   window.FIELD_BASE / window.SHEET_BASE into the deployed page and the
   fetches below go there instead of alongside the page. Each is the
   DIRECTORY the files sit in (a release's assets are flat, so no 'fields/'
   is appended). Empty, the default, means fields/ and sheets/ next to the
   page, as always. The manifests stay in git and are always read locally.
   ?fieldbase= and ?sheetbase= override either for a test. */
const _base=(q,w)=>{const v=new URLSearchParams(location.search).get(q);const b=v!=null?v:(window[w]||'');return b&&!b.endsWith('/')?b+'/':b;};
const FIELD_BASE=_base('fieldbase','FIELD_BASE'), SHEET_BASE=_base('sheetbase','SHEET_BASE');
async function loadAll(){
  const files=['timeline','boundaries','plates','hotspots','labels','plates_time','eras','life','art','photos','platerot'];
  if(window.INLINE_JSON){files.forEach(f=>DATA[f]=window.INLINE_JSON[f]);}
  else{const res=await Promise.all(files.map(f=>fetch(f+'.json?v='+DATA_V).then(r=>r.json()).catch(()=>null)));files.forEach((f,i)=>DATA[f]=res[i]);}
  DATA.eras=DATA.eras||{intervals:[],supercontinents:[]};
  DATA.life=DATA.life||{biomes:[],life:[],regional:{}};
  DATA.art=DATA.art||{art:{},byType:{}};
  DATA.photos=DATA.photos||{};
  DATA.platerot=DATA.platerot||{slots:48,rot:{}};
  // Shipped world sheets, if the bake script has run (WP-10 plan A3). Optional,
  // and nothing waits on it: the app bakes its own sheets until it arrives.
  fetch('sheets/manifest.json?v='+SHEET_V).then(r=>r.ok?r.json():null).then(m=>{SHEET_MANIFEST=m;}).catch(()=>{});
  // Present-day lakes MINUS the Holocene glacial ones. See youngLakeWeight().
  // Seven kilobytes, and the lake swap can be asked for at any age, so it is the
  // one field that is always resident.
  await (_BITMAPS
    ? fetch(fieldSrc('phan_0000_wold.webp')).then(r=>{if(!r.ok)throw 0;return r.blob();})
        .then(b=>createImageBitmap(b,{imageOrientation:'flipY',
          premultiplyAlpha:'none',colorSpaceConversion:'none'}))
        .then(bm=>{WOLD=bm;}).catch(()=>{})
    : new Promise(res=>{const im=new Image();im.onload=()=>{WOLD=im;res();};
        im.onerror=()=>res();im.src=fieldSrc('phan_0000_wold.webp');}));
  // ...and the two keyframes the opening age actually sits between. Everything
  // else arrives in the background; see the note on loadFrame below.
  await ensureFrames(state.age, true);
}

/* ================= fields, fetched when they are needed =================

   This used to await all 1,506 of them -- every one of the six fields at every
   one of the 251 keyframes -- before the globe appeared. Measured: 148.8 MB and
   17.9 seconds on localhost with a warm cache, which is fetch and decode alone,
   before a single byte crosses a network. What the opening frame actually needs
   is the two keyframes it interpolates between: twelve files, about a megabyte.
   The other 274-fold was being paid up front for footage the viewer might never
   scrub to.

   Nothing about the data changes. The same files are fetched, in full, at the
   same fidelity -- just when they are wanted. Three things already in the
   architecture make that safe, and it is worth naming them because they are why
   this is a loader change and not a rewrite:

     * bindTextures() is written `if(ea) ... if(eb||ea)`, so a keyframe that has
       not arrived keeps the previously bound texture rather than binding null.
     * getTex() creates GPU textures lazily behind an LRU cap, so residency was
       never tied to how many images were in memory.
     * every CPU-side reader of the elevation raster goes through elevField(),
       which returns null for a frame it does not have, and every caller of that
       already handles null -- because a _w or _o file has always been allowed to
       be missing.

   So the only genuinely new requirement is that the frames around the CURRENT
   age be there, which is what ensureFrames and the prefetch pump below do. */
const FIELD_KINDS=[['e',()=>ELI],['r',()=>RNI],['m',()=>MOI],
                   ['w',()=>WLI],['d',()=>SFI],['o',()=>OCI],['v',()=>VLI],['p',()=>PLI],['t',()=>TCI],['f',()=>FRI],
                   ['q',()=>FQI],    // fold coordinates (build_foldphase.py), lossless WebP
                   ['x',()=>FXI]];   // drainage coordinates (build_drainphase.py), lossless WebP
const fieldSrc=n=>(FIELD_BASE||'fields/')+n+'?v='+FIELD_V;
const _fieldTried=new Set();     // kind+i once a fetch has SETTLED, success or not
const _fieldPending=new Map();   // kind+i -> in-flight promise, so nothing is asked for twice

function fieldFile(i,kind){
  const fr=DATA.timeline[i];
  if(kind==='e')return fr.e;
  if(kind==='r')return fr.r;
  if(kind==='m')return fr.m;
  // The lake, surface-process and ocean-structure fields are baked alongside the
  // elevation field and named by the same convention, so derive rather than
  // threading three more names through the timeline JSON.
  /* Elevation ships as AVIF and the other five as WebP, so the sibling name
     cannot be a blind replace of '_e.webp' -- that returns the string
     UNCHANGED the moment elevation is not a .webp, and the app would ask for
     the elevation six times over with nothing to say so. Split on '_e'. */
  const cut=fr.e.lastIndexOf('_e');
  // The fold coordinates are two 16-bit potentials split across byte pairs; a
  // lossy codec would terrace them and a sawtooth would seam, so they are PNG.
  return fr.e.slice(0,cut)+'_'+kind+'.webp';
}

/* The opening frame needs twelve files, so the splash counts those and nothing
   else. It used to count all 1,506 -- which is why it sat at low percentages for
   most of a minute and then jumped. */
let _bootWant=0,_bootGot=0;
/* DECODE OFF THE RENDER PATH (perf audit P1, WP-09 F4). The old loader stored a
   raw HTMLImageElement, and nothing ever decoded it until the first render()
   that bound it -- where Chrome paid AVIF/WebP decode plus GPU upload inside
   ONE frame. Measured on the M1: a keyframe crossing stalled ~153 ms, of which
   ~122 ms was exactly this (the two 4096x2048 elevation AVIFs alone are
   ~112 ms). createImageBitmap decodes on the browser's worker pool instead, so
   what reaches texSubImage2D is finished pixels.

   THE FLIP LIVES AT DECODE TIME NOW. UNPACK_FLIP_Y_WEBGL is IGNORED for
   ImageBitmap uploads by spec, so the usual Texture.flipY=true silently does
   nothing for these -- the bitmap is therefore baked flipped
   (imageOrientation:'flipY') and getTex sets flipY=false for bitmap sources.
   The two CPU readers (elevField, the motion decoder) un-flip at drawImage
   through drawFieldImage below, so every consumer sees the orientation it
   always did. colorSpaceConversion:'none' because these are DATA rasters, not
   colour -- a profile-aware decode would silently rewrite elevation bytes. */
const _BITMAPS=typeof createImageBitmap==='function';
function drawFieldImage(cx,img,w,h){
  if(_BITMAPS&&img instanceof ImageBitmap){
    cx.save();cx.translate(0,h);cx.scale(1,-1);cx.drawImage(img,0,0,w,h);cx.restore();
  } else cx.drawImage(img,0,0,w,h);
}
function loadField(i,kind,boot){
  const key=kind+i;
  if(_fieldTried.has(key))return Promise.resolve();
  const p0=_fieldPending.get(key); if(p0)return p0;
  const arr=FIELD_KINDS.find(k=>k[0]===kind)[1]();
  if(boot)_bootWant++;
  // Mark tried on BOTH paths. A 404 is legitimate here -- a keyframe may have
  // no lake field -- and retrying it forever would make the prefetch pump spin.
  const fin=()=>{
    _fieldPending.delete(key);_fieldTried.add(key);
    if(boot){_bootGot++;const el=$('#loadPct');
      if(el)el.textContent=Math.round(_bootGot/Math.max(_bootWant,1)*100)+'%';}};
  let p;
  if(_BITMAPS){
    /* Fetch and DISCARD: this populates the browser's HTTP cache (compressed
       bytes, disk-backed, browser-managed) and nothing else. Decoding into
       memory is ensureBitmap's job, and only for the residency window --
       decoding everything here is the exact mistake that pinned gigabytes of
       IOSurfaces and crashed the tab. Elevation and rainfall still ride at
       high priority; the refinement kinds follow. */
    const pri=(kind==='e'||kind==='r')?'high':'low';
    p=fetch(fieldSrc(fieldFile(i,kind)),{priority:pri})
      .then(r=>{if(!r.ok)throw 0;return r.blob();})
      .then(()=>fin())
      .catch(fin);
  } else p=new Promise(res=>{
    const img=new Image();
    img.onload=()=>{arr[i]=img;fin();res();};
    img.onerror=()=>{fin();res();};
    img.src=fieldSrc(fieldFile(i,kind));
  });
  _fieldPending.set(key,p);
  return p;
}
/* Two waves (perf audit P6): elevation+rainfall first -- the per-kind uniform
   gates in bindTextures make a partial bind safe, so on a jump the first
   CORRECT frame needs only these two, and the other eight kinds land behind
   them without holding it up. At boot the frames must also be DECODED, not
   just cached, or the splash would lift onto a globe with nothing to bind. */
const loadFrame=(i,boot)=>
  Promise.all([loadField(i,'e',boot),loadField(i,'r',boot)])
    .then(()=>boot?Promise.all([ensureBitmap('e',i,true),ensureBitmap('r',i,true)]):null)
    .then(()=>Promise.all(FIELD_KINDS.map(([k])=>loadField(i,k,boot))))
    .then(()=>boot?Promise.all(FIELD_KINDS.map(([k])=>ensureBitmap(k,i,true))):null);
const frameSettled=i=>FIELD_KINDS.every(([k])=>_fieldTried.has(k+i));
/* Diagnostic: what image memory is this page actually PINNING? A decoded
   ImageBitmap holds its full uncompressed raster (often an IOSurface on
   macOS, invisible to RSS) for as long as a reference lives. */
window.__MEM=()=>{
  let n=0,bytes=0,legacy=0;
  for(const[k,v]of TEXCACHE){if(v.bm){n++;bytes+=v.bm.width*v.bm.height*4;}}
  for(const[,get]of FIELD_KINDS){for(const im of get()){if(im&&im.width)legacy++;}}
  return {tried:_fieldTried.size,bitmaps:n,pinnedMB:Math.round(bytes/1048576),
          legacyImgs:legacy,cacheMB:Math.round(_texBytes/1048576),
          entries:TEXCACHE.size,pendingDecodes:_bmPending.size,
          boundE:_lastBoundE,scrubbing:_scrubbing};
};

/* The frames an age sits between. `block` is true only at boot: everywhere else
   this is fire-and-forget, because bindTextures already has something to draw. */
function ensureFrames(age,block){
  const f=frameAt(age);
  const p=Promise.all([loadFrame(f.i,block),loadFrame(f.j,block)]);
  return block?p:undefined;
}

/* PREFETCH, re-centred on every completion. Rather than a fixed queue, ask each
   time for the nearest keyframe to wherever the viewer is NOW -- so scrubbing
   across the timeline re-aims the fill instead of waiting out a plan made
   before they moved. Four at a time: enough to saturate a connection, few
   enough that a frame the viewer is actually waiting for is not stuck behind a
   queue of speculative ones. */
const PREFETCH_CONCURRENCY=4;
let _prefetchBusy=0, _prefetchOn=false;
/* WHAT THE PUMP MAY FETCH (WP-10, A5.5). It used to warm the entire 138 MB
   timeline into the browser cache on every visit, four files at a time, on
   battery, on metered connections, and in hidden tabs. Now: a hidden tab
   fetches nothing until it is shown again; on a metered connection
   (navigator.connection.saveData) or on battery (navigator.getBattery, where
   the browser offers it) it fetches only the keyframes within LEAN_RADIUS of
   the viewer, two at a time -- enough lookahead for playback in either
   direction, re-aimed on every completion as before -- and the full fill
   happens only on mains power over an unmetered link. */
const LEAN_RADIUS=4;
let _lean=!!(navigator.connection&&navigator.connection.saveData), _charging=true;
if(navigator.getBattery){navigator.getBattery().then(b=>{
  const upd=()=>{_charging=b.charging;pumpPrefetch();};
  b.addEventListener('chargingchange',upd);upd();}).catch(()=>{});}
function prefetchRadius(){return (_lean||!_charging)?LEAN_RADIUS:DATA.timeline.length;}
function nextWantedFrame(){
  const n=DATA.timeline.length, c=frameAt(state.age).i, R=Math.min(n,prefetchRadius());
  for(let d=0;d<=R;d++){
    for(const i of (d?[c-d,c+d]:[c])) if(i>=0&&i<n&&!frameSettled(i))return i;
  }
  return -1;
}
function pumpPrefetch(){
  if(!_prefetchOn||document.hidden)return;
  const cap=(_lean||!_charging)?2:PREFETCH_CONCURRENCY;
  while(_prefetchBusy<cap){
    const i=nextWantedFrame(); if(i<0)return;
    _prefetchBusy++;
    loadFrame(i).then(()=>{_prefetchBusy--;pumpPrefetch();});
  }
}
document.addEventListener('visibilitychange',()=>{if(!document.hidden)pumpPrefetch();});
function startPrefetch(){_prefetchOn=true;pumpPrefetch();}

/* PREDICTIVE GPU RESIDENCY (perf audit P3, WP-09 F4-F6). Fetch-and-decode
   (loadField) gets pixels into memory; this gets them onto the GPU BEFORE the
   crossing that needs them, so bindTextures binds already-resident textures
   and the per-crossing upload storm never lands in a visible frame. One
   texture per frame: the largest (elevation) uploads in ~5-15 ms from a
   decoded bitmap, which one frame can absorb, while a crossing used to demand
   eighteen at once. Direction-aware -- playback warms the keyframe ahead;
   paused warms both neighbours, which is what scrubbing wants. */
const _upQ=[];
function queueUploads(f){
  if(!DATA.timeline||!renderer.initTexture)return;
  if(_scrubbing)return;   // the queue was flushed; bindTex owns the decode slots
  const n=DATA.timeline.length;
  const dir=state.playing?(state.dir<0?-1:+1):0;
  /* The pair itself comes first: bindTextures touches only the kinds it binds,
     and the interval kinds (v/p/t/f/m) of the B-frame are NOT among them --
     yet they are exactly what the next crossing binds. Warming "the pair" is
     really warming those. */
  const deep=TEX_BUDGET>500*1048576;   // small windows cannot hold a deep lookahead
  const want=[f.i,f.j];
  if(dir<=0){want.push(f.i-1);if(dir<0&&deep){want.push(f.i-2);want.push(f.i-3);}}
  if(dir>=0){want.push(f.j+1);if(dir>0&&deep){want.push(f.j+2);want.push(f.j+3);}}
  let decodesKicked=0;
  for(const w of want){
    if(w<0||w>=n)continue;
    for(const k of KIND_PRIORITY){
      const key=k+w;
      if(_bmMissing.has(key))continue;
      if(!_fieldTried.has(key))continue;            // not even fetched yet
      const e=TEXCACHE.get(key);
      /* Resident means: on the GPU where the shader will read it. For the
         four stack kinds that is a band in the keyframe's stack (the member
         texture is never bound), and the crossing-storm gate counts every
         upload the crossing frame pays -- a stack composed at bind time
         paid seven (2026-09-03), so its bands are warmed here like a field. */
      if(k in STK_BANDS){const S=TEXCACHE.get('s'+w); if(S&&S.have.has(k))continue;}
      else if(e&&e.t)continue;                      // fully resident
      if(_BITMAPS&&(!e||!e.bm)){
        // Stage 1, DECODE: off-thread, so a few can run concurrently without
        // touching the frame. ensureBitmap is idempotent. Playback burns
        // through keyframes, so it gets a deeper decode pipeline.
        const kick=state.playing?5:3, inflight=state.playing?7:4;
        if(decodesKicked<kick&&_bmPending.size<inflight){ensureBitmap(k,w);decodesKicked++;}
        continue;
      }
      // Stage 2, UPLOAD: decoded and waiting for its GPU copy.
      if(_upQ.some(q=>q.k===k&&q.i===w))continue;
      _upQ.push({k,i:w});
    }
  }
  // The current pair's own arrivals go through bindTextures; while those are
  // still outstanding they own the frame budget, so hold the speculative work.
  if(!frameSettled(f.i)||!frameSettled(f.j))return;
  // And a crossing frame already carries the new frame's label work -- don't
  // stack a speculative upload on the one frame that can least afford it.
  // Instead, spend this one on the OTHER thing the next crossing will need:
  // the 256x128 CPU elevation raster snapLabel probes against.
  if(f.i!==queueUploads._lf){
    queueUploads._lf=f.i;
    if(typeof elevField==='function'){elevField(Math.max(0,f.i-1));elevField(Math.min(DATA.timeline.length-1,f.j+1));}
    return;
  }
  let drains=state.playing?2:1;                     // playback burns keyframes faster
  while(_upQ.length&&drains>0){
    const q=_upQ.shift();
    if(Math.abs(q.i-f.i)>4)continue;                // stale after a far jump
    const e=TEXCACHE.get(q.k+q.i);
    if(q.k in STK_BANDS){
      const S=TEXCACHE.get('s'+q.i);
      if(!(S&&S.have.has(q.k))){
        const t=getTex(q.k,q.i);                    // null until decoded
        if(t){stackFill(q.i,k=>k===q.k?t:null);drains--;}   // one band into the stack, ahead of the crossing
      }
    } else if(!e||!e.t){
      const t=getTex(q.k,q.i);                      // null until decoded
      if(t){renderer.initTexture(t);drains--;}
    }
  }
}

/* map timeline (sorted asc by age) to helpers */
/* The timeline never changes after load, but this used to rebuild a fresh
   251-element array on EVERY call -- and frameAt calls it several times a
   frame. Pure allocation churn; cache it once. */
let _AGES=null;
function ages(){return _AGES||(_AGES=DATA.timeline.map(f=>f.age));}
function frameAt(age){
  // returns {i,j,t} interpolation between adjacent frames
  const A=ages();
  if(age<=A[0])return{i:0,j:0,t:0};
  if(age>=A[A.length-1])return{i:A.length-1,j:A.length-1,t:0};
  for(let k=0;k<A.length-1;k++){
    if(age>=A[k]&&age<=A[k+1]){
      const t=(age-A[k])/(A[k+1]-A[k]);
      return{i:k,j:k+1,t};
    }
  }
  return{i:0,j:0,t:0};
}

/* ================= three.js globe ================= */
let renderer,scene,cam,orthoCam,globe,mapMesh,mat,starfield,atmo,clouds;
const overlay={boundaries:new THREE.Group(),derived:new THREE.Group(),vectors:new THREE.Group(),hotspots:new THREE.Group(),rivers:new THREE.Group()};
let dragging=false,lastX=0,lastY=0;
let lastOverlayFrame=-1,lastVecOn=null,lastHotOn=null,lastBndOn=null;

function ll2v(lon,lat,r){
  const phi=(90-lat)*DEG, theta=(lon+180)*DEG;
  return new THREE.Vector3(-r*Math.sin(phi)*Math.cos(theta), r*Math.cos(phi), r*Math.sin(phi)*Math.sin(theta));
}

/* The globe used to be a perfectly smooth ball whose relief existed only in the
   fragment shader's shading. That reads correctly looking straight down and
   falls apart the moment you tilt: a shaded sphere seen edge-on is still a
   sphere, with a smooth silhouette and no mountains standing against the sky.
   Tilt is only worth having if the terrain has real height, so the terrain now
   has real height -- the elevation field displaces the vertices themselves.

   texture2D, NOT texture2DLod. The reasoning for the LOD variant is sound in
   GLSL ES 1.00 -- a vertex shader has no implicit derivatives -- but three.js
   compiles ShaderMaterial to GLSL ES 3.00 under WebGL2, where the compatibility
   layer #defines texture2D to texture() and provides no texture2DLod at all.
   The result was "no matching overloaded function", a vertex shader that never
   compiled, and a globe that drew as a featureless blue ball because the whole
   program was dead. texture() in the vertex stage samples the base level, which
   is what was wanted. The decode duplicates decElev from the fragment shader
   (one line, signed-sqrt, Z_RANGE 8000) rather than sharing it, because the two
   stages are compiled from separate strings.

   Gated on uMapProj because this same material draws the flat map, where
   "displace along the normal" would push the plane bodily at the camera.

   DECODE BOTH KEYFRAMES, THEN MIX -- in that order, and it matters. This stage
   used to mix the two encoded BYTES and decode the result, while baseElev in
   the fragment shader decodes each keyframe and mixes the metres. The encoding
   is signed-sqrt, so decoding is quadratic and mix(dec(a),dec(b)) is not
   dec(mix(a,b)): the two stages disagreed everywhere except at a keyframe. The
   gap is widest where the two frames straddle sea level, which is exactly a
   migrating coastline, so displaced geometry and shaded elevation parted
   company at the one place a viewer is watching. Same arithmetic as decElev
   below; duplicated rather than shared because the two stages compile from
   separate strings.

   AND IT MUST ADVECT TOO. The fragment stage now carries each keyframe toward
   the other so crust slides instead of cross-fading; if this stage kept
   sampling at a fixed uv the displaced geometry would sit where the terrain
   used to be while the shading drew it where it has moved to -- reintroducing
   the same divorce between height and colour that decode-then-mix just closed,
   at up to 65 texels instead of a few hundred metres. Same offsets, duplicated
   for the same reason the decode is. */
/* THE NOISE LATTICE, BAKED (perf audit P4, WP-09 F1). Measured on the M1:
   ~80% of the whole GPU frame was vnoise3 -- eight sin()-hash lattice corners
   and a trilinear mix, per octave, per tap, per fragment, with fbm3 running
   five octaves and detail3 ten. The values at integer lattice points are just
   fixed random numbers, so they are baked once into a 64^3 lattice stored as
   an 8x8 atlas of 66x66 tiles (one-texel gutters carry the wrap so bilinear
   never bleeds a neighbouring slice). The shader then reads a corner-mixed
   value with TWO texture fetches: sampling at (corner + smoothstepped
   fraction) makes the hardware bilinear compute exactly the mix() tree the
   old code computed -- same interpolation weights, same lattice periodicity
   trick fbm's 2.07 octave growth already relies on to stay incommensurate.
   Seeded PRNG, so every visitor and every deploy sees the same Earth.
   ?oldnoise switches the sin()-hash implementation back on for A/B.

   The one real difference: the lattice VALUES are a different random draw
   than sin-hash produced (sin-hash is aperiodic and cannot be tabulated), so
   the specific instance of each mottle moves while its amplitude, frequency,
   anisotropy and character are bit-identical -- the statistics are the model;
   the instance never was. Verified by side-by-side screenshot pairs. */
const NZOLD=new URLSearchParams(location.search).has('oldnoise');
/* The two implementations, chosen once at boot. Plain top-level literals --
   NEVER nest a backtick string inside the FRAG/CFRAG literals; that is the
   template-literal trap check_shader.py exists to catch. */
const VN_OLD=`float vnoise3(vec3 p){
  vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
  float a=mix(mix(hash3(i),hash3(i+vec3(1,0,0)),f.x),mix(hash3(i+vec3(0,1,0)),hash3(i+vec3(1,1,0)),f.x),f.y);
  float b=mix(mix(hash3(i+vec3(0,0,1)),hash3(i+vec3(1,0,1)),f.x),mix(hash3(i+vec3(0,1,1)),hash3(i+vec3(1,1,1)),f.x),f.y);
  return mix(a,b,f.z);
}`;
const VN_NEW=`float vnoise3(vec3 p){
  vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
  vec3 w=mod(i,64.0);
  vec2 xy=w.xy+f.xy+0.5;
  float z1=mod(w.z+1.0,64.0);
  vec2 t0=vec2(mod(w.z,8.0),floor(w.z*0.125))*66.0+1.0;
  vec2 t1=vec2(mod(z1,8.0),floor(z1*0.125))*66.0+1.0;
  float a=texture2D(uNz,(t0+xy)*(1.0/528.0)).r;
  float b=texture2D(uNz,(t1+xy)*(1.0/528.0)).r;
  return mix(a,b,f.z);
}`;
const CN_OLD=`float ch(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
    float cn(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
      float a=mix(mix(ch(i),ch(i+vec3(1,0,0)),f.x),mix(ch(i+vec3(0,1,0)),ch(i+vec3(1,1,0)),f.x),f.y);
      float b=mix(mix(ch(i+vec3(0,0,1)),ch(i+vec3(1,0,1)),f.x),mix(ch(i+vec3(0,1,1)),ch(i+vec3(1,1,1)),f.x),f.y);
      return mix(a,b,f.z);}`;
const CN_NEW=`float cn(vec3 p){
      vec3 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
      vec3 w=mod(i,64.0);
      vec2 xy=w.xy+f.xy+0.5;
      float z1=mod(w.z+1.0,64.0);
      vec2 t0=vec2(mod(w.z,8.0),floor(w.z*0.125))*66.0+1.0;
      vec2 t1=vec2(mod(z1,8.0),floor(z1*0.125))*66.0+1.0;
      float a=texture2D(uNz,(t0+xy)*(1.0/528.0)).r;
      float b=texture2D(uNz,(t1+xy)*(1.0/528.0)).r;
      return mix(a,b,f.z);}`;
function bakeNoiseLUT(){
  const mulberry32=a=>()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);
    t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};
  const rnd=mulberry32(0x9E3779B9);
  const P=64,A=528;
  const V=new Float32Array(P*P*P);
  // Floor at the smallest NORMAL half float: the encoder below has no
  // subnormal path, and an unlucky tiny value would decode as ~2.0 -- a
  // bright pinprick somewhere on the planet. 6e-5 on a noise value is
  // beneath any visible threshold; a mangled lattice point is not.
  for(let i=0;i<V.length;i++)V[i]=Math.max(6.104e-5,rnd());
  /* Half-float, not bytes. An R8 lattice quantises the values to 1/255, and
     detail3's ridged transform -- (1-|2n-1|)^2 -- turns each tiny flat step
     near n=0.5 into a flat facet exactly at the crease tip. Measured: the
     ridge crop lost ~11% of its Laplacian energy, i.e. visibly softer crests.
     Half floats carry ~2,000 levels through the same trick at 2 bytes/texel
     (557 KB), and the crispness comes back to parity. */
  const f2h=v=>{const f32=new Float32Array(1),u32=new Uint32Array(f32.buffer);
    f32[0]=v;const x=u32[0];
    return((x>>16)&0x8000)|((((x>>23)&0xff)-112)<<10)&0x7c00|((x>>13)&0x03ff);};
  const data=new Uint16Array(A*A);
  for(let z=0;z<P;z++){
    const col=z%8,row=(z/8)|0;
    for(let y=0;y<66;y++){const ly=(y+63)%64;
      for(let x=0;x<66;x++){const lx=(x+63)%64;
        data[(row*66+y)*A+col*66+x]=f2h(V[(z*P+ly)*P+lx]);}}}
  const t=new THREE.DataTexture(data,A,A,THREE.RedFormat,THREE.HalfFloatType);
  t.minFilter=THREE.LinearFilter;t.magFilter=THREE.LinearFilter;
  t.generateMipmaps=false;t.colorSpace=THREE.NoColorSpace;
  t.wrapS=THREE.ClampToEdgeWrapping;t.wrapT=THREE.ClampToEdgeWrapping;
  t.needsUpdate=true;
  return t;
}
const VERT=SHADERS.VERT;

/* ---------------------------------------------------------------------------
   Terrain shader.

   The page ships ELEVATION and RAINFALL fields per keyframe rather than
   finished pictures. Interpolating elevation between two keyframes makes a
   coastline migrate across the grid — real motion — where cross-fading two
   colour images could only dissolve one coastline into another. Temperature is
   recomputed here from latitude, elevation and the era anomaly, and relief is
   shaded per pixel, so detail stays crisp no matter how far you zoom in.
--------------------------------------------------------------------------- */
const FRAG=SHADERS.FRAG.replace('/*@vnoise*/', NZOLD?VN_OLD:VN_NEW);

/* ================= THE LITE MATERIAL (WP-10, plan A2) =================
   Draws the globe and the map from two baked WORLD SHEETS instead of running
   the terrain shader per pixel. A sheet is one keyframe's whole shaded world
   (the FRAG above rendered once into an equirect render target, uMapProj 2),
   so per frame this only has to: carry each sheet toward the other on the
   displacement warp exactly as the keyframe fields are carried, blend by mixf,
   and add back the three things a sheet cannot hold -- the coastline's exact
   position (from the interpolated height, so it still migrates rather than
   dissolving), the schematic shading, and the globe's terminator and limb.
   No noise, no field decoding: two sheet reads, two height reads, one warp.
   Never put a backtick in here: it is a JS template literal like FRAG. */
const LFRAG=SHADERS.LFRAG;
let liteMat=null;
function initGL(){
  const cv=$('#gl');
  /* preserveDrawingBuffer costs a copy of the whole frame at this resolution
     (perf audit P5) and exists only so pixels can be read back later. Every
     reader in this project -- APP.snap, the screenshot recipes -- renders and
     then reads in the SAME task, which the spec guarantees without preserve.
     MSAA stays: the globe interior is shaded per-pixel either way, but the
     silhouette against the stars and the overlay LINES visibly need it. */
  renderer=new THREE.WebGLRenderer({canvas:cv,antialias:true,preserveDrawingBuffer:false});
  renderer.setPixelRatio(renderScale());
  scene=new THREE.Scene();
  cam=new THREE.PerspectiveCamera(38,innerWidth/innerHeight,.01,100);
  orthoCam=new THREE.OrthographicCamera(-1,1,1,-1,-10,10);
  mat=new THREE.ShaderMaterial({uniforms:{
    elevA:{value:null},elevB:{value:null},rainA:{value:null},rainB:{value:null},
    motA:{value:null},waterA:{value:null},waterB:{value:null},
    surfA:{value:null},surfB:{value:null},
    oceanA:{value:null},oceanB:{value:null},
    dispA:{value:null},uWarp:{value:0},
    plateA:{value:null},uMat:{value:0},
    uTect:{value:0},uFore:{value:0},uFoldOn:{value:0},uDrainOn:{value:0},
    // the small-field stack: _t, _f, _q, _x of a keyframe in ONE texture (stackFill)
    stkA:{value:null},stkB:{value:null},uStkSel:{value:new THREE.Vector4(0,0,0,0)},uStkSelB:{value:new THREE.Vector2(0,0)},
    uPlateQ:{value:Array.from({length:48},()=>new THREE.Vector4(0,0,1,0))},
    mixf:{value:0},uTemp:{value:-0.55},uVeg:{value:1},uGrass:{value:1},uIceT:{value:-30},
    uSeaT:{value:-14},uSchem:{value:0},uDetail:{value:1},
    uMapProj:{value:0},uBounds:{value:0},uMapLon:{value:0},uDisp:{value:0},uDry:{value:0},uSeaTint:{value:1},uTime:{value:0},
    uSnowball:{value:0},
    uDbg:{value:new THREE.Vector4(1,1,1,1)},
    uAtlas:{value:null},uAtlasOn:{value:0},
    uAtlasK:{value:new THREE.Vector4(+(_sq.get('atlasN')||1),+(_sq.get('atlasT')||1),+(_sq.get('atlasH')||1),+(_sq.get('plainsK')||1))},
    uBasin:{value:_sq.get('basin')==='0'?0:1},
    uErgK:{value:+(_sq.get('erg')||1)},        // wind-steered dune lineation (0 off)
    uFoldK:{value:+(_sq.get('fold')||0)},      // fold-belt atlas relief: ships OFF (review 2026-09-03), ?fold=1 to see it
    uPlatK:{value:+(_sq.get('plat')||0)},      // DEM-driven plateau envelope on the atlas: OFF by default (see FRAG reliefEnv), ?plat=1 to try
    uArcK:{value:+(_sq.get('arc')||1)},        // belt type: arcs lose the fold ridges (0 off)
    uShow:{value:+(_sq.get('show')||0)},       // mask view: draw one gate as grey (see FRAG)
    uNz:{value:bakeNoiseLUT()},
    // One texel of the SURFACE-PROCESS and lake fields (2048x1024), which is what
    // it is used to warp -- not the elevation, which is now twice that.
    uTexel:{value:new THREE.Vector2(1/2048,1/1024)}
  },vertexShader:VERT,fragmentShader:FRAG,
    extensions:{derivatives:true}});   // fwidth() for screen-space shoreline AA
  // 1024x512 is 525k vertices -- 0.35 deg, ~39 km a quad -- which is what it
  // takes for a displaced range to read as a range rather than as a bulge.
  // Phones keep the old mesh: they cannot afford half a million vertices and
  // are not the device anyone tilts to admire the Himalaya on.
  const SEG=matchMedia('(max-width:720px),(max-height:560px)').matches?[256,128]:[1024,512];
  globe=new THREE.Mesh(new THREE.SphereGeometry(1,SEG[0],SEG[1]),mat);
  scene.add(globe);
  /* The lite material shares the terrain material's uniform OBJECTS for
     everything it reads from the keyframe pair, so bindTextures() keeps both
     materials in step without knowing the second one exists. */
  const U=mat.uniforms;
  liteMat=new THREE.ShaderMaterial({uniforms:{
    sheetA:{value:null},sheetB:{value:null},
    elevA:U.elevA,elevB:U.elevB,dispA:U.dispA,mixf:U.mixf,uWarp:U.uWarp,
    uMapProj:U.uMapProj,uMapLon:U.uMapLon,uSchem:U.uSchem,uDisp:U.uDisp},
    vertexShader:VERT,fragmentShader:LFRAG});
  // the flat map is the same shader on a plane, so both views agree exactly
  mapMesh=new THREE.Mesh(new THREE.PlaneGeometry(1,1),mat);
  mapMesh.visible=false; scene.add(mapMesh);
  /* The orogen atlas (WP-10, plan B3), optional: the shader draws exactly the
     old picture until it has loaded. 2048x2048 RGBA, mipmapped, repeat. */
  mat.uniforms.uAtlas.value=new THREE.DataTexture(new Uint8Array([128,128,128,255]),1,1,THREE.RGBAFormat);
  mat.uniforms.uAtlas.value.needsUpdate=true;
  fetch('atlas.webp?v='+FIELD_V).then(r=>{if(!r.ok)throw 0;return r.blob();})
    .then(b=>createImageBitmap(b,{imageOrientation:'flipY',premultiplyAlpha:'none',colorSpaceConversion:'none'}))
    .then(bm=>{const t=new THREE.Texture(bm);t.flipY=false;t.colorSpace=THREE.NoColorSpace;
      t.minFilter=THREE.LinearMipmapLinearFilter;t.magFilter=THREE.LinearFilter;t.generateMipmaps=true;
      t.wrapS=THREE.RepeatWrapping;t.wrapT=THREE.RepeatWrapping;t.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
      t.needsUpdate=true;mat.uniforms.uAtlas.value=t;mat.uniforms.uAtlasOn.value=_sq.has('noatlas')?0:1;
      for(const s of SHEETS.values())s.ready=false;   // sheets baked without it are stale
    }).catch(()=>{});
  // Neutral fallback for the ocean-structure field: mid-grey is "no data" (age
  // 0.5, spreading vector 0 -> aniso 0), so a keyframe whose _o failed to load
  // draws NO abyssal fabric rather than reading a black texture as a fixed
  // diagonal grain. Real _o textures overwrite this per frame in bindTextures.
  const _oceanGray=new THREE.DataTexture(new Uint8Array([128,128,128,255]),1,1,THREE.RGBAFormat);
  _oceanGray.needsUpdate=true;
  mat.uniforms.oceanA.value=_oceanGray; mat.uniforms.oceanB.value=_oceanGray;
  // atmosphere
  const ageo=new THREE.SphereGeometry(1.03,64,32);
  /* uAtm and uRim exist because this shell was written for ONE viewing
     situation -- the whole globe, centred, seen from far away -- where the
     opaque Earth covers the middle and only a rim of shell is left showing.
     Tilt breaks that assumption completely: the camera drops to just above the
     shell and looks along it, so the line of sight runs a long tangential path
     through the atmosphere and the edge-on term (0.72-dot -> 0.43 alpha) paints
     the entire screen pale blue. uAtm dims the whole shell as the camera closes
     in and uRim sharpens it onto the limb, which is exactly what a real horizon
     looks like from low orbit -- a thin bright band, not a fog. */
  const amat=new THREE.ShaderMaterial({transparent:true,side:THREE.BackSide,
    uniforms:{uAtm:{value:1},uRim:{value:2.2}},
    vertexShader:`varying vec3 vN;void main(){vN=normalize(normalMatrix*normal);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
    fragmentShader:`uniform float uAtm,uRim;varying vec3 vN;void main(){
      /* CLAMP THE BASE TO 0..1 BEFORE THE POWER. On the back faces this
         shell is drawn with, dot() goes negative, so 0.72-dot reaches 1.72 --
         and raising a number GREATER THAN ONE to a higher power amplifies it
         instead of attenuating it. Tightening the rim by lifting uRim to 6.5
         therefore produced 1.72^6.5 = 35, a fully saturated white disc over
         the entire planet. It read as a terrain bug and was this one line. */
      float i=pow(clamp(0.72-dot(vN,vec3(0,0,1.0)),0.0,1.0),uRim);
      gl_FragColor=vec4(0.36,0.62,0.86,1.0)*i*0.9*uAtm;}`});
  atmo=new THREE.Mesh(ageo,amat); scene.add(atmo);

  /* Cloud layer -- the single biggest "seen from space" cue. It is a thin shell
     just above the terrain, and it reads the SAME shipped rainfall field the
     biomes come from, so clouds gather where each era is actually wet: a bright
     ITCZ band over the tropics, mid-latitude storm tracks, and clear subtropical
     high belts over the deserts. Slowly drifting fBm breaks it into real weather
     cells. It shares the terrain material's rain textures and clock, so it
     tracks the era for free. */
  const CVERT=SHADERS.CVERT;
  const CFRAG=SHADERS.CFRAG.replace('/*@cnoise*/', NZOLD?CN_OLD:CN_NEW);
  const cmat=new THREE.ShaderMaterial({transparent:true,depthWrite:false,
    side:THREE.FrontSide, uniforms:{
      rainA:mat.uniforms.rainA, rainB:mat.uniforms.rainB,   // shared with terrain
      mixf:mat.uniforms.mixf, uTime:mat.uniforms.uTime,
      uNz:mat.uniforms.uNz,   // the baked noise lattice, shared with the terrain
      uCloud:{value:1.0}},
    vertexShader:CVERT, fragmentShader:CFRAG});
  clouds=new THREE.Mesh(new THREE.SphereGeometry(1.014,128,64),cmat);
  globe.add(clouds);   // co-rotates with the terrain; drift comes from uTime
  // stars
  const sg=new THREE.BufferGeometry();const N=1800;const pos=new Float32Array(N*3);
  for(let i=0;i<N;i++){const r=40+Math.random()*30;const th=Math.random()*6.283;const ph=Math.acos(2*Math.random()-1);
    pos[i*3]=r*Math.sin(ph)*Math.cos(th);pos[i*3+1]=r*Math.cos(ph);pos[i*3+2]=r*Math.sin(ph)*Math.sin(th);}
  sg.setAttribute('position',new THREE.BufferAttribute(pos,3));
  starfield=new THREE.Points(sg,new THREE.PointsMaterial({color:0x9fb0c8,size:.09,sizeAttenuation:true,transparent:true,opacity:.55}));
  scene.add(starfield);
  globe.add(overlay.boundaries);globe.add(overlay.derived);globe.add(overlay.vectors);globe.add(overlay.hotspots);globe.add(overlay.rivers);
  resize();
  /* PINCH. The old code tracked one pointer, so a second finger was invisible
     to the app and the browser handled the gesture instead. Every active
     pointer is now kept, and two of them mean pinch rather than drag: the zoom
     follows the RATIO of the finger separation, which is what makes it track
     the fingers instead of drifting, and dragging is suspended so the globe
     does not lurch as the midpoint wanders. */
  const ptrs=new Map(); let pinchD=0;
  cv.addEventListener('pointerdown',e=>{
    ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(ptrs.size>=2){dragging=false;pinchD=0;state.dragMoved=true;return;}
    dragging=true;lastX=e.clientX;lastY=e.clientY;
    try{cv.setPointerCapture(e.pointerId);}catch(_){}
    state.dragMoved=false;});
  const endPtr=e=>{ptrs.delete(e.pointerId);
    if(ptrs.size<2){pinchD=0;
      // hand the remaining finger back to drag, from where it is NOW, or the
      // globe jumps by however far the pinch travelled
      if(ptrs.size===1){const q=[...ptrs.values()][0];
        lastX=q.x;lastY=q.y;dragging=true;}else dragging=false;}};
  cv.addEventListener('pointercancel',endPtr);
  cv.addEventListener('pointermove',e=>{
    if(ptrs.has(e.pointerId))ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});
    if(ptrs.size>=2){
      const[a,b]=[...ptrs.values()];
      const d=Math.hypot(a.x-b.x,a.y-b.y);
      if(pinchD>0&&d>0)
        state.zoom=Math.max(1.35,Math.min(5,state.zoom*(pinchD/d)));
      pinchD=d; return;
    }
    if(!dragging)return;
    const dx=e.clientX-lastX,dy=e.clientY-lastY;
    if(Math.abs(dx)+Math.abs(dy)>3)state.dragMoved=true;
    /* DRAG IS IN SCREEN SPACE, so it has to be rotated INTO world space by the
       heading. rot and tilt are longitude and latitude; screen-right equals
       "east" only while heading is zero. At heading 90 the compass has been
       turned a quarter turn under the user, so dragging right used to walk the
       globe along a line running up the screen -- the control still worked, it
       just no longer pointed where the hand was going. Rotating the delta by
       -heading restores the only property that actually matters here: dragging
       left and right always moves the globe left and right on screen, at every
       heading, which is what makes the axis feel like an axis.

       Latitude is clamped, so the drag is scaled by cos(heading) on the tilt
       term rather than allowed to fight the clamp near the poles. */
    const h=(state.head||0)*Math.PI/180, ch=Math.cos(h), sh=Math.sin(h);
    /* Sign check, because it is easy to rotate the delta the wrong way and the
       result still looks plausible until you try it. At heading 90 you face
       east, so north is on your LEFT and south on your right; dragging right
       therefore has to push the view centre NORTH. That means +dx must raise
       the latitude term, not lower it. Verified at 0 (identity) and 90. */
    const wx= dx*ch - dy*sh;      // screen -> world longitude component
    const wy= dx*sh + dy*ch;      // screen -> world latitude component
    /* ZOOM-PROPORTIONAL DRAG (user round, 2026-07-31). The rad-per-pixel
       factor was constant while the visible ground span shrinks like
       (zoom - surface): camera distance is LINEAR in state.zoom (see the
       aim block) and the surface sits just under the 1.35 clamp, so at the
       closest zoom the span is ~5x smaller than at boot and the same wrist
       motion crossed most of the screen -- "difficult to navigate
       precisely", as reported. Scale by height above the surface,
       normalised at the boot zoom (3.05) so the default view feels exactly
       as before; at the 1.35 clamp the drag is ~5x finer. */
    const zs=.006*Math.max(.06,(state.zoom-.95)/2.10);
    state.rot+=wx*zs;
    state.tilt=Math.max(-1.3,Math.min(1.3,state.tilt+wy*zs));
    lastX=e.clientX;lastY=e.clientY;});
  cv.addEventListener('pointerup',e=>{const solo=ptrs.size<=1;endPtr(e);
    if(solo){dragging=false;if(!state.dragMoved)pickGlobe(e);}});
  // Safari's own gesture events fire even with touch-action set, and they are
  // what scale the page on iOS. Refuse them explicitly.
  for(const g of ['gesturestart','gesturechange','gestureend'])
    cv.addEventListener(g,e=>e.preventDefault(),{passive:false});
  // The wheel step scales the same way: a fixed step near the surface used
  // to leap past whole zoom levels of visible span.
  cv.addEventListener('wheel',e=>{e.preventDefault();
    const ws=.0016*Math.max(.12,(state.zoom-.95)/2.10);
    state.zoom=Math.max(1.35,Math.min(5,state.zoom+e.deltaY*ws));},{passive:false});
}

function lineSeg(list,color,width,rBase){
  const g=new THREE.BufferGeometry();const arr=[];
  for(const s of list){const a=ll2v(s[0],s[1],rBase),b=ll2v(s[2],s[3],rBase);arr.push(a.x,a.y,a.z,b.x,b.y,b.z);}
  g.setAttribute('position',new THREE.Float32BufferAttribute(arr,3));
  const m=new THREE.LineBasicMaterial({color,transparent:true,opacity:.9});
  return new THREE.LineSegments(g,m);
}
/* Derived boundaries are drawn as real line geometry, exactly like the
   surveyed present-day set, so they read as boundaries rather than as a
   coloured field. Rebuilt whenever the keyframe changes. */
function nearestKeyAge(){
  const A=DATA.timeline; let b=A[0].age,bd=1e9;
  for(const r of A){const d=Math.abs(r.age-state.age); if(d<bd){bd=d;b=r.age;}}
  return b;
}
const BND_COL={ridge:0xe8534e,trench:0x59b0d6,transform:0xe0b23a};
function eraPlates(){return DATA.plates_time[String(nearestKeyAge())]||{b:[],p:[]};}
/* Boundaries arrive as traced polylines, so they are drawn as continuous
   curves rather than loose segments. A run is cut only where it crosses the
   antimeridian, which would otherwise streak across the whole map. */
/* The boundaries are traced from a rasterised plate-label field, so raw they
   are a staircase of grid-aligned steps — which is the "rough" look. Two
   rounds of Chaikin corner-cutting round that off into a smooth curve without
   moving it off the boundary, and it is cheap enough to run every rebuild. A
   run is only smoothed if it is long enough that the trace, not the geometry,
   is what makes it jagged. */
function chaikin(pts,iter){
  for(let k=0;k<iter;k++){
    if(pts.length<3)break;
    const out=[pts[0]];
    for(let i=0;i<pts.length-1;i++){
      const a=pts[i],b=pts[i+1];
      // guard the antimeridian: never interpolate across a 180 wrap
      if(Math.abs(a[0]-b[0])>180){out.push(a,b);continue;}
      out.push([a[0]*0.75+b[0]*0.25, a[1]*0.75+b[1]*0.25],
               [a[0]*0.25+b[0]*0.75, a[1]*0.25+b[1]*0.75]);
    }
    out.push(pts[pts.length-1]);
    pts=out;
  }
  return pts;
}
/* Group.clear() detaches children but never frees their GPU buffers, and the
   overlay groups rebuild on every keyframe crossing -- measured: +93 orphaned
   geometries per crossing with the layers on, 2,400 within a minute of
   playback (perf audit P7). Dispose what the group owns, then clear it.
   Geometries and materials are often shared across children of one build, so
   collect unique ones first. */
function clearGroup(grp){
  const gs=new Set(), ms=new Set();
  grp.traverse(c=>{
    if(c.geometry)gs.add(c.geometry);
    if(c.material){Array.isArray(c.material)?c.material.forEach(m=>ms.add(m)):ms.add(c.material);}
  });
  gs.forEach(g=>g.dispose()); ms.forEach(m=>m.dispose());
  grp.clear();
}
function buildDerivedBounds(){
  clearGroup(overlay.derived);
  const R=1.006;
  for(const b of eraPlates().b){
    let run=[];
    const flush=()=>{
      if(run.length>1){
        const sm=run.length>=4?chaikin(run,2):run;
        const g=new THREE.BufferGeometry().setFromPoints(sm.map(q=>ll2v(q[0],q[1],R)));
        const ln=new THREE.Line(g,new THREE.LineBasicMaterial({
          color:BND_COL[b.c]||0xffffff,transparent:true,opacity:.9}));
        ln.userData.baseOp=.9; overlay.derived.add(ln);
      }
      run=[];
    };
    for(const q of b.p){
      if(run.length&&Math.abs(q[0]-run[run.length-1][0])>180)flush();
      run.push(q);
    }
    flush();
  }
}
/* RIVERS AS GEOMETRY (iterations 22-24). The reference draws major rivers
   as fine dark threads at every zoom; per-pixel texture sampling cannot (the
   corridor field's p99 is 0.11 at regional footprints -- measured), so the
   threads are LINE GEOMETRY traced at each keyframe from the drainage bitmap
   the cache already holds: hysteresis (strong seeds grown across the weak
   network, because log-accumulation decays upstream), components under
   ~300 km dropped, each adjacent pair of network cells one segment. Zero
   new data shipped; ~10 ms per crossing.
   VERIFICATION NOTE (iteration 24): GL line primitives do NOT rasterize in
   the --headless=new ANGLE Metal pipeline (boundaries-only control: 42 px
   over the Mid-Atlantic Ridge), so this layer -- like every line layer --
   verifies headlessly by the snap() compositor and by data diagnostics,
   and visually only in a real browser. */
const RIVDATA=new Map();
let _rivWant=-1;
function riverPaths(i){
  if(RIVDATA.has(i))return RIVDATA.get(i);
  const img=fieldImage('d',i); if(!img){ensureBitmap('d',i);return null;}
  const RW=2048,RH=1024;                       // native: half-res fattens channels
  const c=document.createElement('canvas');c.width=RW;c.height=RH;
  const cx=c.getContext('2d',{willReadFrequently:true});
  drawFieldImage(cx,img,RW,RH);
  const px=cx.getImageData(0,0,RW,RH).data;
  const N=RW*RH, drain=new Uint8Array(N), on=new Uint8Array(N);
  for(let k=0;k<N;k++)drain[k]=px[k*4];
  /* Components by hysteresis: strong seeds grown across the weak network,
     because log-accumulation decays upstream and one threshold cannot hold
     a river together. */
  const lab=new Int32Array(N), stack=new Int32Array(N);
  let nl=0; const comp=[];
  for(let s=0;s<N;s++){
    if(drain[s]<=109||lab[s])continue;
    nl++; let top=0; stack[top++]=s; lab[s]=nl; const cells=[];
    while(top){
      const q=stack[--top]; cells.push(q);
      const qx=q%RW, qy=(q/RW)|0;
      for(let dy=-1;dy<=1;dy++){
        const ny=qy+dy; if(ny<0||ny>=RH)continue;
        for(let dx=-1;dx<=1;dx++){
          if(!dx&&!dy)continue;
          const nk=ny*RW+((qx+dx+RW)%RW);
          if(!lab[nk]&&drain[nk]>55){lab[nk]=nl;stack[top++]=nk;}
        }
      }
    }
    if(cells.length>=40)comp.push(cells);   // ~300 km of channel, at native res
  }
  /* THIN THE NETWORK TO ONE CELL (iteration 26). The drainage field's
     channels are several cells wide at EVERY resolution -- it is a smoothed,
     meander-warped log-accumulation, not a crisp D8 network -- so drawing
     its cells directly gives combs and ladders whatever the threshold
     (measured: 88-90% of channel cells have three or more channel
     neighbours). Zhang-Suen thinning erodes the blob to its medial axis
     while preserving connectivity: what remains is one cell wide, which is
     what a river is. Iterating over the network's own cells rather than the
     grid keeps this at a few milliseconds. */
  let live=[];
  for(const cells of comp)for(const q of cells){on[q]=1;live.push(q);}
  const at=(x,y)=>(y<0||y>=RH)?0:on[y*RW+((x%RW)+RW)%RW];
  for(let pass=0;pass<14;pass++){
    let removed=0;
    for(let step=0;step<2;step++){
      const kill=[];
      for(const q of live){
        if(!on[q])continue;
        const x=q%RW, y=(q/RW)|0;
        const p2=at(x,y-1),p3=at(x+1,y-1),p4=at(x+1,y),p5=at(x+1,y+1),
              p6=at(x,y+1),p7=at(x-1,y+1),p8=at(x-1,y),p9=at(x-1,y-1);
        const B=p2+p3+p4+p5+p6+p7+p8+p9;
        if(B<2||B>6)continue;
        const seq=[p2,p3,p4,p5,p6,p7,p8,p9,p2];
        let A=0; for(let k=0;k<8;k++)if(!seq[k]&&seq[k+1])A++;
        if(A!==1)continue;
        if(step===0){ if(p2*p4*p6||p4*p6*p8)continue; }
        else        { if(p2*p4*p8||p2*p6*p8)continue; }
        kill.push(q);
      }
      for(const q of kill){on[q]=0;removed++;}
    }
    live=live.filter(q=>on[q]);
    if(!removed)break;
  }
  /* ONE EDGE PER CELL, DOWNSTREAM: flow accumulation grows downstream, so
     the highest-drainage neighbour is the one this cell drains into. A tree,
     never a mesh. Then strip headwater tips, since a river begins where flow
     has gathered rather than at every hillslope pixel. */
  const best=new Int32Array(N).fill(-1), indeg=new Uint16Array(N);
  for(const q of live){
    const qx=q%RW, qy=(q/RW)|0;
    let bk=-1,bv=drain[q];
    for(let dy=-1;dy<=1;dy++){
      const ny=qy+dy; if(ny<0||ny>=RH)continue;
      for(let dx=-1;dx<=1;dx++){
        if(!dx&&!dy)continue;
        const nk=ny*RW+((qx+dx+RW)%RW);
        if(on[nk]&&drain[nk]>bv){bv=drain[nk];bk=nk;}
      }
    }
    best[q]=bk;
  }
  for(const q of live)if(best[q]>=0)indeg[best[q]]++;
  const dead=[];
  for(const q of live)if(!indeg[q])dead.push(q);
  for(const q of dead){on[q]=0;if(best[q]>=0)indeg[best[q]]--;}
  const segs=[];
  const lonf=x=>(x+0.5)/RW*360-180, latf=y=>90-(y+0.5)/RH*180;
  for(const q of live){
    const b=best[q];
    if(!on[q]||b<0||!on[b])continue;
    segs.push([lonf(q%RW),latf((q/RW)|0),lonf(b%RW),latf((b/RW)|0)]);
  }
  RIVDATA.set(i,segs);
  if(RIVDATA.size>12){for(const k of RIVDATA.keys()){if(k!==i){RIVDATA.delete(k);break;}}}
  return segs;
}
function buildRivers(){
  clearGroup(overlay.rivers);
  const fi=curFrame().i;
  const segs=riverPaths(fi);
  if(!segs){_rivWant=fi;return;}
  _rivWant=-1;
  if(!segs.length)return;
  const ln=lineSeg(segs,0x27556b,1,1.0035);
  ln.material.opacity=0.55;
  overlay.rivers.add(ln);
}
function buildBoundaries(){
  clearGroup(overlay.boundaries);
  const R=1.006;
  overlay.boundaries.add(lineSeg(DATA.boundaries.ridge,0xe8534e,1,R));
  overlay.boundaries.add(lineSeg(DATA.boundaries.trench,0x59b0d6,1,R));
  overlay.boundaries.add(lineSeg(DATA.boundaries.transform,0xe0b23a,1,R));
}
/* Decode a motion field once so the arrow layer can read it. R/G hold the
   east/north components, B the confidence: abyssal plain has no structure to
   match against, so those cells are deliberately reported as unreliable and
   simply go undrawn rather than showing invented motion. */
const MOT_W=128, MOT_H=64, MOT_RANGE=160;
function motionField(i){
  if(MOTDATA.has(i))return MOTDATA.get(i);
  const img=fieldImage('m',i); if(!img){ensureBitmap('m',i);return null;}
  const c=document.createElement('canvas');c.width=MOT_W;c.height=MOT_H;
  const cx=c.getContext('2d',{willReadFrequently:true});
  drawFieldImage(cx,img,MOT_W,MOT_H);
  const d=cx.getImageData(0,0,MOT_W,MOT_H).data;
  const out={vx:new Float32Array(MOT_W*MOT_H),vy:new Float32Array(MOT_W*MOT_H),
             cf:new Float32Array(MOT_W*MOT_H)};
  for(let k=0;k<MOT_W*MOT_H;k++){
    out.vx[k]=(d[k*4]/255*2-1)*MOT_RANGE;
    out.vy[k]=(d[k*4+1]/255*2-1)*MOT_RANGE;
    out.cf[k]=d[k*4+2]/255;
  }
  MOTDATA.set(i,out);
  if(MOTDATA.size>40){for(const k of MOTDATA.keys()){if(k!==i){MOTDATA.delete(k);break;}}}
  return out;
}
function motionAt(fld,lon,lat){
  const c=Math.min(MOT_W-1,Math.max(0,Math.floor((lon+180)/360*MOT_W)));
  const r=Math.min(MOT_H-1,Math.max(0,Math.floor((90-lat)/180*MOT_H)));
  const k=r*MOT_W+c;
  return {vx:fld.vx[k],vy:fld.vy[k],cf:fld.cf[k]};
}
/* Labels are authored at approximate positions, but the world moves under
   them: an ocean name can end up sitting on a continent a few frames later.
   Decode the elevation field per keyframe and nudge each label to the nearest
   cell of the right kind, so seas stay on water and landmasses on land. */
const ELEV_W=256, ELEV_H=128, ELEV_RANGE=8000;
const ELEVDATA=new Map();
function elevField(i){
  if(ELEVDATA.has(i))return ELEVDATA.get(i);
  const img=fieldImage('e',i); if(!img){ensureBitmap('e',i);return null;}
  const c=document.createElement('canvas');c.width=ELEV_W;c.height=ELEV_H;
  const cx=c.getContext('2d',{willReadFrequently:true});
  drawFieldImage(cx,img,ELEV_W,ELEV_H);
  const d=cx.getImageData(0,0,ELEV_W,ELEV_H).data;
  const z=new Float32Array(ELEV_W*ELEV_H);
  for(let k=0;k<z.length;k++){
    const e=d[k*4]/255*2-1;                 // signed-sqrt decode
    z[k]=Math.sign(e)*e*e*ELEV_RANGE;
  }
  ELEVDATA.set(i,z);
  if(ELEVDATA.size>30){for(const k of ELEVDATA.keys()){if(k!==i){ELEVDATA.delete(k);break;}}}
  return z;
}
function elevAtLL(z,lon,lat){
  const c=((Math.round((lon+180)/360*ELEV_W)%ELEV_W)+ELEV_W)%ELEV_W;
  const r=Math.min(ELEV_H-1,Math.max(0,Math.round((90-lat)/180*ELEV_H)));
  return z[r*ELEV_W+c];
}
const SNAP=new Map();
function snapLabel(l,fi){
  // A TRACKED label rides its plate along the real Merdith rotation (`tr`), so
  // its position is recomputed from the age every frame (smooth, feature-locked)
  // and only lightly refined onto matching terrain nearby — never flung across
  // the globe. An UNTRACKED label (deep-Precambrian, authored in its era's frame)
  // keeps the original wide terrain search, cached per keyframe.
  const tracked=!!l.tr;
  const key=l.n+'@'+fi;
  if(!tracked && SNAP.has(key))return SNAP.get(key);
  const z=elevField(fi);
  const base = tracked ? trackPos(l.tr, l.lon, l.lat) : [l.lon, l.lat];
  let out=base;
  if(z){
    // Only seas and oceans belong on water; every other feature type — lakes,
    // rifts, deserts, forests, ice sheets, basins, plateaus, islands/terranes,
    // regions, orogens, continents — is a LAND feature and must snap to land.
    const wantLand=!(l.t==='sea'||l.t==='ocean');
    // Require a substantial patch, not a single stray pixel.
    const solid=(lo,la)=>{
      let hit=0,n=0;
      for(let dy=-4;dy<=4;dy+=4)for(let dx=-6;dx<=6;dx+=6){
        const e=elevAtLL(z,((lo+dx+540)%360)-180,Math.max(-88,Math.min(88,la+dy)));
        n++; if((e>0)===wantLand)hit++;
      }
      return hit/n>=0.65;
    };
    if(!solid(base[0],base[1])){
      // Tracked: the plate track already puts the name in the right place, so
      // only NUDGE onto nearby matching terrain. The radius used to be 24°,
      // which is ~2600 km at the equator — far enough that a sea whose water had
      // drained would find the next ocean over and sit there, which is how the
      // Western Interior Seaway ended up labelled off the southeast US coast.
      // The paleo-DEM also under-resolves shallow epicontinental seas, so a
      // "no matching terrain" result is at least as likely to be the DEM's fault
      // as the track's; staying put is then the honest answer.
      // Untracked keeps the wide search (to 90°) — a static coord authored in
      // the present frame really can sit far from where the world moved it.
      const maxrad=tracked?14:90, astep=tracked?15:10;
      let best=null;
      for(let rad=4;rad<=maxrad&&!best;rad+=4){
        for(let a=0;a<360;a+=astep){
          const dlon=rad*Math.cos(a*DEG)/Math.max(0.25,Math.cos(base[1]*DEG));
          const lo=((base[0]+dlon+540)%360)-180;
          const la=Math.max(-86,Math.min(86,base[1]+rad*Math.sin(a*DEG)));
          if(solid(lo,la)){best=[lo,la];break;}
        }
      }
      // Tracked keeps its plate position even if terrain disagrees (better than
      // dropping); untracked drops rather than float a name in open ocean.
      out = best || (tracked ? base : null);
    }
  }
  if(!tracked){ SNAP.set(key,out); if(SNAP.size>4000)SNAP.clear(); }
  return out;
}
function hotspotsNow(){
  const a=state.age;
  return DATA.hotspots.filter(h=>a>=Math.min(h.a0,h.a1)&&a<=Math.max(h.a0,h.a1));
}
/* Where a feature sits at the displayed age. Craters and large igneous
   provinces carry a `tr` track — their position along their plate's real
   rotation (Merdith 2021), sampled every 5 Myr — so they ride the plate
   continuously instead of freezing at one spot. Plumes have no track: they are
   mantle-anchored and stay put while the crust slides past. h.lon/h.lat is the
   present-day position and the fallback. */
// Interpolate a Merdith track [[age,lon,lat],...] at the current age. Shared by
// craters/LIPs (featurePos) and now labels (snapLabel), so both ride their plate.
function trackPos(tr,lon,lat){
  if(!tr||tr.length<2)return [lon,lat];
  // NOT Math.max(0, ...). That clamp made every future age read the age-0
  // position, so a label could not move in the future even once its track had
  // points there -- and it was invisible, because when no track went past the
  // present the clamp and the a<=tr[0][0] branch below returned the same thing.
  // Tracks that still stop at the present are unaffected: a negative age falls
  // into that same first branch and returns exactly what it did before.
  const a=state.age;
  if(a<=tr[0][0])return [tr[0][1],tr[0][2]];
  const last=tr[tr.length-1];
  if(a>=last[0])return [last[1],last[2]];
  for(let i=0;i<tr.length-1;i++){
    if(a>=tr[i][0]&&a<=tr[i+1][0]){
      const t=(a-tr[i][0])/(tr[i+1][0]-tr[i][0]||1);
      let lo0=tr[i][1],lo1=tr[i+1][1];
      if(Math.abs(lo1-lo0)>180){if(lo1>lo0)lo0+=360;else lo1+=360;}  // wrap
      let lo=((lo0+(lo1-lo0)*t+540)%360)-180;
      return [lo, tr[i][2]+(tr[i+1][2]-tr[i][2])*t];
    }
  }
  return [lon,lat];
}
function featurePos(h){ return trackPos(h.tr, h.lon, h.lat); }
function buildHotspots(){
  clearGroup(overlay.hotspots);
  const geo=new THREE.SphereGeometry(.008,8,8);
  const mm=new THREE.MeshBasicMaterial({color:0xff7d3a});
  const lipm=new THREE.MeshBasicMaterial({color:0xffd257});
  for(const h of hotspotsNow()){
    const isLip=h.k==='lip', isImp=h.k==='impact';
    const[flon,flat]=featurePos(h);   // rides its plate if it has a track
    // a large igneous province erupts in a geological instant; flag the pulse
    const erupting=(isLip||isImp)&&h.peak!==undefined&&Math.abs(state.age-h.peak)<6;
    if(isImp){
      /* A crater is a scar, not an event: bright at the moment of impact, then
         a ring that fades as it is buried and eroded. How long that takes runs
         over two orders of magnitude, so it is per-crater rather than a flat
         rate — Chicxulub was buried within about two million years, while
         Manicouagan is 215 Myr old and still unmistakable from orbit. Once the
         scar is gone, a structure that left a global signature stays on as a
         small dim mark: the hole has closed but the record has not. */
      const p=ll2v(flon,flat,1.012);
      let rr=Math.max(.014,Math.min(.05,(h.d||30)/180*.05));
      const since=Math.max(0,h.peak-state.age);        // Myr since the impact
      const sl=h.sl||90;
      const gone=since>sl;
      const fresh=Math.exp(-since/Math.max(2,sl));
      const col=erupting?0xffe9a8:gone?0x8792a6:0xc9d6e8;
      if(gone)rr*=0.45;
      const ring=new THREE.Mesh(new THREE.RingGeometry(rr*(erupting?.3:.62),rr,24),
        new THREE.MeshBasicMaterial({color:col,transparent:true,
          opacity:erupting?.85:gone?.17:.20+.40*fresh,side:THREE.DoubleSide}));
      ring.position.copy(p);ring.lookAt(p.clone().multiplyScalar(2));
      overlay.hotspots.add(ring);
      if(erupting){
        const flash=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({color:0xfff4d0}));
        flash.position.copy(p);flash.scale.setScalar(2.2);overlay.hotspots.add(flash);
      }
      continue;
    }
    /* Three states, not two. A plume is a live centre; a province mid-eruption
       is the loudest thing on the map; and a province that erupted long ago is
       still a landform — a basalt plateau, muted and fading as erosion strips
       it — which is why its window now runs far past its eruption. */
    const standing=isLip&&!erupting;
    const col=erupting?0xffd257:standing?0xb08968:0xff7d3a;
    const p=ll2v(flon,flat,1.012);
    const sp=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({color:col,
      transparent:true,opacity:standing?.55:1}));
    sp.position.copy(p);
    if(erupting)sp.scale.setScalar(1.9); else if(isLip)sp.scale.setScalar(1.15);
    overlay.hotspots.add(sp);
    const rr=erupting?.034:isLip?.026:.02;
    // fade the ring over the province's life as a landform
    let fade=1;
    if(standing&&h.peak!==undefined){
      const span=Math.max(12,h.peak-(h.vu!==undefined?h.vu:0));
      fade=Math.max(.25,1-(h.peak-state.age)/span);
    }
    const ring=new THREE.Mesh(new THREE.RingGeometry(rr*0.6,rr,20),
      new THREE.MeshBasicMaterial({color:col,transparent:true,
        opacity:(erupting?.55:.32)*fade,side:THREE.DoubleSide}));
    ring.position.copy(p);ring.lookAt(p.clone().multiplyScalar(2));overlay.hotspots.add(ring);
  }
}
// motion vectors: sample grid, assign plate by point-in-poly, compute velocity
function pointInRings(lon,lat,rings){
  let inside=false;
  for(const ring of rings){
    for(let i=0,j=ring.length-1;i<ring.length;j=i++){
      const xi=ring[i][0],yi=ring[i][1],xj=ring[j][0],yj=ring[j][1];
      if(((yi>lat)!=(yj>lat))&&(lon<(xj-xi)*(lat-yi)/(yj-yi)+xi))inside=!inside;
    }
  }
  return inside;
}
function velocityAt(lon,lat,motion){
  // omega vector along euler pole, magnitude deg/Myr
  const pole=ll2v(motion.lon,motion.lat,1).normalize();
  const w=motion.w*DEG; // rad/Myr
  const omega=pole.multiplyScalar(w);
  const p=ll2v(lon,lat,1).normalize();
  const v=new THREE.Vector3().crossVectors(omega,p); // rad/Myr tangent
  const speed=v.length()*6371; // mm/yr  (rad/Myr * km  ~ mm/yr)
  return {v,speed};
}
function buildVectors(){
  clearGroup(overlay.vectors);
  const fld=motionField(curFrame().i); if(!fld)return;
  const arr=[];const heads=[];
  for(let lat=-78;lat<=78;lat+=9){
    for(let lon=-180;lon<180;lon+=9){
      const m=motionAt(fld,lon,lat);
      if(m.cf<0.30)continue;                       // no structure -> no claim
      const speed=Math.hypot(m.vx,m.vy);
      if(speed<6)continue;
      const base=ll2v(lon,lat,1.008);
      // east/north components -> a tangent vector on the sphere
      const north=new THREE.Vector3(0,1,0);
      const n=base.clone().normalize();
      const e=new THREE.Vector3().crossVectors(north,n).normalize();
      const nn=new THREE.Vector3().crossVectors(n,e).normalize();
      const dir=e.multiplyScalar(m.vx).add(nn.multiplyScalar(m.vy)).normalize();
      const len=Math.min(.085,.016+speed*.0007);
      const tip=base.clone().add(dir.multiplyScalar(len));
      arr.push(base.x,base.y,base.z,tip.x,tip.y,tip.z);
      // arrowhead
      const back=tip.clone().sub(base).normalize().multiplyScalar(len*.4);
      const side=new THREE.Vector3().crossVectors(tip.clone().normalize(),back).multiplyScalar(.4);
      const h1=tip.clone().sub(back).add(side),h2=tip.clone().sub(back).sub(side);
      heads.push(tip.x,tip.y,tip.z,h1.x,h1.y,h1.z, tip.x,tip.y,tip.z,h2.x,h2.y,h2.z);
    }
  }
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(arr,3));
  overlay.vectors.add(new THREE.LineSegments(g,new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.8})));
  const g2=new THREE.BufferGeometry();g2.setAttribute('position',new THREE.Float32BufferAttribute(heads,3));
  overlay.vectors.add(new THREE.LineSegments(g2,new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.8})));
}

function pickGlobe(e){
  const rect=$('#gl').getBoundingClientRect();
  const mx=((e.clientX-rect.left)/rect.width)*2-1;
  const my=-((e.clientY-rect.top)/rect.height)*2+1;
  const ray=new THREE.Raycaster();ray.setFromCamera({x:mx,y:my},cam);
  const hit=ray.intersectObject(globe,false);
  if(!hit.length){closeInfo();return;}
  const lp=globe.worldToLocal(hit[0].point.clone()).normalize();
  const lat=Math.asin(THREE.MathUtils.clamp(lp.y,-1,1))/DEG;
  let lon=Math.atan2(lp.z,-lp.x)/DEG-180; // invert ll2v
  lon=((lon+540)%360)-180;
  selectAt(lon,lat,e);
}

/* ================= 2D map ================= */
const mcv=$('#map2d'),mctx=mcv.getContext('2d');
const DPR=Math.min(devicePixelRatio,2);
let mapView={dx:0,dy:0,dw:0,dh:0};
/* The map is drawn by the same terrain shader on a plane; this positions that
   plane and then paints only the vector overlays onto a transparent canvas
   stacked above it. */
function layoutMap(){
  const W=innerWidth,H=innerHeight;
  const topR=90, botR=150, avail=Math.max(120,H-topR-botR);
  let dw=W*0.98, dh=dw/2;
  if(dh>avail){dh=avail;dw=dh*2;}
  const dx=(W-dw)/2, dy=topR+(avail-dh)/2;
  mapView={dx,dy,dw,dh};
  orthoCam.left=-W/2; orthoCam.right=W/2; orthoCam.top=H/2; orthoCam.bottom=-H/2;
  orthoCam.updateProjectionMatrix();
  mapMesh.scale.set(dw,dh,1);
  mapMesh.position.set(dx+dw/2-W/2, H/2-(dy+dh/2), 0);
}
function drawMapOverlays(){
  mctx.clearRect(0,0,mcv.width,mcv.height);
  const {dx,dy,dw,dh}=mapView;
  const X=dx*DPR,Y=dy*DPR,Wd=dw*DPR,Hd=dh*DPR;
  const fade=presentFade();
  if(state.layers.boundaries&&fade>0)drawBoundariesMap(X,Y,Wd,Hd,fade);
  const dfade=Math.min(1,Math.max(0,1-fade*1.25));
  if(state.layers.boundaries&&dfade>0)drawDerivedBoundsMap(X,Y,Wd,Hd,dfade);
  if(state.layers.hotspots)drawHotspotsMap(X,Y,Wd,Hd,1);
  if(state.layers.vectors)drawVectorsMap(X,Y,Wd,Hd,1);
}
/* Mollweide, matching the shader. Equal-area, so the flat map keeps polar
   regions in something close to their true proportion instead of smearing
   them across the full width as equirectangular does. */
function mollFwd(lon,lat){
  const ph=lat*DEG, la=lon*DEG;
  let th=ph;                                  // solve 2th+sin2th = pi*sin(phi)
  if(Math.abs(Math.abs(ph)-Math.PI/2)<1e-6){ th=ph; }
  else{ for(let k=0;k<6;k++){
      const dv=(2*th+Math.sin(2*th)-Math.PI*Math.sin(ph))/(2+2*Math.cos(2*th));
      th-=dv; if(Math.abs(dv)<1e-8)break; } }
  return [ (2/Math.PI)*la*Math.cos(th), Math.sin(th) ];   // x -2..2, y -1..1
}
function mollInv(xn,yn){
  if(xn*xn*0.25+yn*yn>1) return null;
  const th=Math.asin(Math.max(-1,Math.min(1,yn)));
  const lat=Math.asin(Math.max(-1,Math.min(1,(2*th+Math.sin(2*th))/Math.PI)))/DEG;
  const c=Math.cos(th); if(Math.abs(c)<1e-6) return null;
  const lon=(Math.PI*xn/(2*c))/DEG;
  if(Math.abs(lon)>180) return null;
  return [lon,lat];
}
function ll2map(lon,lat,dx,dy,dw,dh){
  /* THE PAN HAS TO HAPPEN HERE, and only here. The shader shifts the central
     meridian when it samples the terrain, but every overlay -- labels, plate
     boundaries, hotspots, click targets -- reaches the screen through this one
     function, so without the matching shift the map slid underneath a layer of
     labels that stayed where they were and floated over the wrong continents.
     One funnel, one correction: a feature at world longitude L is drawn at map
     longitude L - mapLon, wrapped, which is the exact inverse of what the
     fragment shader does to find which pixel shows that feature. */
  const ml=((lon-(state.mapLon||0))%360+540)%360-180;
  const [xn,yn]=mollFwd(ml,lat);
  return [dx+(xn/4+0.5)*dw, dy+(0.5-yn/2)*dh];
}
function drawBoundariesMap(dx,dy,dw,dh,fade){
  const draw=(list,color)=>{mctx.strokeStyle=color;mctx.globalAlpha=fade*.95;mctx.lineWidth=1.4;mctx.beginPath();
    for(const s of list){const[a,b]=ll2map(s[0],s[1],dx,dy,dw,dh);const[c,d]=ll2map(s[2],s[3],dx,dy,dw,dh);if(Math.abs(s[0]-s[2])>180)continue;mctx.moveTo(a,b);mctx.lineTo(c,d);}mctx.stroke();};
  draw(DATA.boundaries.ridge,'#e8534e');draw(DATA.boundaries.trench,'#59b0d6');draw(DATA.boundaries.transform,'#e0b23a');
  mctx.globalAlpha=1;
}
const BND_CSS={ridge:'#e8534e',trench:'#59b0d6',transform:'#e0b23a'};
function drawDerivedBoundsMap(dx,dy,dw,dh,fade){
  mctx.globalAlpha=fade*0.92; mctx.lineWidth=1.7*DPR;
  mctx.lineJoin='round'; mctx.lineCap='round';
  for(const b of eraPlates().b){
    mctx.strokeStyle=BND_CSS[b.c]||'#fff';
    mctx.beginPath();
    let pen=false, prev=null;
    for(const q of b.p){
      if(prev&&Math.abs(q[0]-prev[0])>180)pen=false;
      const a=ll2map(q[0],q[1],dx,dy,dw,dh);
      if(!pen){mctx.moveTo(a[0],a[1]);pen=true;}else mctx.lineTo(a[0],a[1]);
      prev=q;
    }
    mctx.stroke();
  }
  mctx.globalAlpha=1;
}
function drawHotspotsMap(dx,dy,dw,dh,fade){
  mctx.globalAlpha=fade;
  for(const h of hotspotsNow()){
    const fp=featurePos(h);
    const[x,y]=ll2map(fp[0],fp[1],dx,dy,dw,dh);
    const erupting=h.peak!==undefined&&Math.abs(state.age-h.peak)<6;
    if(h.k==='impact'){
      const R=Math.max(4,Math.min(11,(h.d||30)/180*11));
      const fresh=Math.exp(-Math.max(0,h.peak-state.age)/90);
      mctx.strokeStyle=erupting?'rgba(255,244,208,.9)':`rgba(201,214,232,${(.25+.4*fresh).toFixed(2)})`;
      mctx.lineWidth=(erupting?2.2:1.4)*DPR;
      mctx.beginPath();mctx.arc(x,y,R*DPR,0,6.28);mctx.stroke();
      if(erupting){mctx.fillStyle='rgba(255,244,208,.5)';mctx.beginPath();
        mctx.arc(x,y,R*.45*DPR,0,6.28);mctx.fill();}
      continue;
    }
    const R=erupting?9:h.k==='lip'?6.5:5, col=erupting?'255,210,87':'255,125,58';
    mctx.fillStyle=`rgba(${col},.32)`;mctx.beginPath();mctx.arc(x,y,R*DPR,0,6.28);mctx.fill();
    mctx.fillStyle=`rgb(${col})`;mctx.beginPath();mctx.arc(x,y,(erupting?3.4:2.2)*DPR,0,6.28);mctx.fill();
  }
  mctx.globalAlpha=1;
}
function drawVectorsMap(dx,dy,dw,dh,fade){
  const fld=motionField(curFrame().i); if(!fld)return;
  mctx.globalAlpha=fade*.85;mctx.strokeStyle='#fff';mctx.lineWidth=1.2*DPR;
  for(let lat=-78;lat<=78;lat+=9)for(let lon=-180;lon<180;lon+=9){
    const m=motionAt(fld,lon,lat);
    if(m.cf<0.30)continue;
    const speed=Math.hypot(m.vx,m.vy); if(speed<6)continue;
    // step a short way along the motion and project both ends
    const dlat=lat+m.vy*0.045, dlon=lon+m.vx*0.045/Math.max(0.25,Math.cos(lat*DEG));
    if(Math.abs(dlat)>88||Math.abs(dlon-lon)>60)continue;
    const a=ll2map(lon,lat,dx,dy,dw,dh), b=ll2map(dlon,dlat,dx,dy,dw,dh);
    const ang=Math.atan2(b[1]-a[1],b[0]-a[0]);
    const L=Math.min(17,5+speed*.16)*DPR;
    const ex=a[0]+Math.cos(ang)*L, ey=a[1]+Math.sin(ang)*L;
    mctx.beginPath();mctx.moveTo(a[0],a[1]);mctx.lineTo(ex,ey);
    mctx.lineTo(ex-Math.cos(ang-.4)*4*DPR,ey-Math.sin(ang-.4)*4*DPR);
    mctx.moveTo(ex,ey);mctx.lineTo(ex-Math.cos(ang+.4)*4*DPR,ey-Math.sin(ang+.4)*4*DPR);
    mctx.stroke();
  }
  mctx.globalAlpha=1;
}
function mapPick(e){
  const rect=mcv.getBoundingClientRect();const x=(e.clientX-rect.left),y=(e.clientY-rect.top);
  const{dx,dy,dw,dh}=mapView;
  const ll=mollInv(((x-dx)/dw-0.5)*4, (0.5-(y-dy)/dh)*2);
  if(!ll){closeInfo();return;}
  selectAt(ll[0],ll[1],e);
}
mcv.addEventListener('click',mapPick);

/* ================= selection / info ================= */
/* One projection for both views, so hit-testing and label layout can work in
   screen pixels. Testing in degrees was wrong at any zoom other than the
   default: a 7-degree radius is a handful of pixels zoomed out and half the
   window zoomed in. */
function projectLL(lon,lat,r){
  if(state.view==='globe'){
    const p=ll2v(lon,lat,r||1.02), wp=p.clone().applyMatrix4(globe.matrixWorld);
    const cp=wp.clone().project(cam);
    const nrm=p.clone().applyQuaternion(globe.quaternion).normalize();
    const toCam=cam.position.clone().sub(wp).normalize();
    const vis=!(cp.z>1||nrm.dot(toCam)<0.12);
    return {x:(cp.x*.5+.5)*innerWidth, y:(-cp.y*.5+.5)*innerHeight, vis};
  }
  const{dx,dy,dw,dh}=mapView||{};
  if(!dw)return{x:0,y:0,vis:false};
  const c=ll2map(lon,lat,dx,dy,dw,dh);
  return {x:c[0], y:c[1], vis:true};
}

/* Click priority. This used to lead with the present-day plate lookup gated on
   presentFade()>0.4, which is true all the way out to 24.75 Ma — and because
   PB2002 tiles the whole globe, EVERY click inside that window returned a
   plate and returned early. Craters, erupting provinces and era labels were
   unreachable for the first 25 Myr of the record. Small precise targets now go
   first, and the plate is the fallback for clicks that hit nothing specific. */
function selectAt(lon,lat,ev){
  const px=ev?{x:ev.clientX,y:ev.clientY}:projectLL(lon,lat);
  const fi=curFrame().i, z=elevField(fi);
  // 1. volcanism and impacts: small, precise, and the most interesting thing
  //    on the map when they are there
  if(state.layers.hotspots){
    let he=null,hd=1e9;
    for(const h of hotspotsNow()){
      const fp=featurePos(h);
      const p=projectLL(fp[0],fp[1]); if(!p.vis)continue;
      const d=Math.hypot(p.x-px.x,p.y-px.y);
      if(d<hd){hd=d;he=h;}
    }
    if(he&&hd<18){showEvent(he);return;}
  }
  // 2. a label the click effectively landed on
  const vis=DATA.labels.filter(l=>labelVisible(l));
  const spos=new Map();
  for(const l of vis){
    const sp=snapLabel(l,fi); if(!sp)continue;
    const p=projectLL(sp[0],sp[1]); if(!p.vis)continue;
    spos.set(l,p);
  }
  let best=null,bd=1e9;
  for(const[l,p]of spos){const d=Math.hypot(p.x-px.x,p.y-px.y); if(d<bd){bd=d;best=l;}}
  if(best&&bd<26){showFeature(best,lon,lat);return;}
  // 3. present-day plate, while the present-day layer is still legible
  if(presentFade()>0.4){
    for(const p of DATA.plates){if(pointInRings(lon,lat,p.rings)){showPlate(p,lon,lat);return;}}
  }
  // 4. nearest label of the right kind: clicking water should name the ocean,
  //    not the continent beside it
  const onLand=z?elevAtLL(z,lon,lat)>0:true;
  const LANDY=new Set(['continent','orogen','desert','forest','grassland','tundra','basin','plateau','rift','ice','region']);
  const wanted=[...spos.keys()].filter(l=>LANDY.has(l.t)===onLand);
  const pool=wanted.length?wanted:[...spos.keys()];
  best=null;bd=1e9;
  for(const l of pool){const p=spos.get(l);const d=Math.hypot(p.x-px.x,p.y-px.y); if(d<bd){bd=d;best=l;}}
  if(best&&bd<Math.min(innerWidth,innerHeight)*0.42)showFeature(best,lon,lat);else closeInfo();
}
function showPlate(p,lon,lat){
  state.selPlate=p.code;
  const rows=[];
  if(p.motion){const{speed}=velocityAt(lon,lat,p.motion);
    rows.push(['Motion here',`${speed.toFixed(0)} mm/yr`]);
    rows.push(['Euler pole',`${p.motion.lat.toFixed(1)}°, ${p.motion.lon.toFixed(1)}°`]);
    rows.push(['Rotation rate',`${p.motion.w.toFixed(3)}°/Myr`]);
  }
  const zf=elevField(curFrame().i);
  if(zf){const e=elevAtLL(zf,lon,lat);
    rows.push([e>=0?'Elevation':'Depth', `${Math.abs(Math.round(e)).toLocaleString()} m`]);}
  rows.push(['Clicked','~'+Math.abs(lat).toFixed(0)+'°'+(lat>=0?'N':'S')+' '+Math.abs(lon).toFixed(0)+'°'+(lon>=0?'E':'W')]);
  const reg=regionalAt(p.name,state.age);
  const extra=reg?`<div class="ihead">Fossil record here</div><p class="desc">${esc(reg)}</p>`:'';
  /* The plate polygons are surveyed present-day PB2002. They stay legible for
     the first few tens of millions of years, but the outline is today's — say
     so rather than implying it was measured for the displayed age. */
  openInfo({name:p.name,
    tag:'Tectonic plate · '+(Math.abs(state.age)<1?'present day':'present-day outline'),
    rows,desc:plateDesc(p.name),extra,wide:!!extra});
}
function showEvent(h){
  const rows=[];
  const kind=h.k==='impact'?'Impact structure':h.k==='lip'?'Large igneous province':'Mantle plume';
  let tag, extra='';
  if(h.k==='impact'){
    const since=Math.max(0,h.peak-state.age);
    const sl=h.sl||90, gone=since>sl;
    tag=kind+' · '+(since<1?'just struck':gone?'eroded away':'visible scar');
    rows.push(['Rim diameter',`${h.d} km`]);
    /* Say how well the age is actually known. A quarter of the catalogue has
       no radiometric age at all, and presenting those with the same authority
       as a U-Pb date is the kind of quiet overclaim this app should not make. */
    rows.push(['Impact age',`${h.peak} Ma`+(h.cf&&h.cf!=='precise'?` (${h.cf})`:'')]);
    if(h.cfu)rows.push(['Age constraint',h.cfu]);
    rows.push([since<1?'Status':'Age of scar',
      since<1?'just struck':`${Math.round(since)} Myr old`]);
    rows.push(['Stayed visible',sl>=500?'to the present':`~${sl} Myr`]);
    if(h.slw)extra+=`<div class="ihead">Why that long</div><p class="desc">${esc(h.slw)}</p>`;
    if(h.ge)extra+=`<div class="ihead">${gone?'What outlasted it':'Global signature'}</div>`+
      `<p class="desc">${esc(h.ge)}</p>`;
  }else{
    const e0=Math.min(h.e0!==undefined?h.e0:h.a0,h.e1!==undefined?h.e1:h.a1);
    const e1=Math.max(h.e0!==undefined?h.e0:h.a0,h.e1!==undefined?h.e1:h.a1);
    /* A flood basalt is an eruption for a moment and a landform for a very
       long time. Say which of the two you are looking at. A plume is never
       "erupting" in this sense — it is simply active for its whole life. */
    const erupting=h.k==='lip'&&state.age>=e0-1&&state.age<=e1+1;
    tag=kind+' · '+(h.k==='plume'?'active':erupting?'erupting':'standing');
    if(h.k==='lip'){
      rows.push(['Erupted',`${e1}–${e0} Ma`]);
      if(h.peak!==undefined)rows.push(['Peak',`${h.peak} Ma`]);
      if(h.vu!==undefined){
        rows.push(['A landform until',h.vu===0?'the present day':`${h.vu} Ma`]);
        if(!erupting)rows.push(['Age of province',`${Math.round(h.peak-state.age)} Myr`]);
      }
      if(h.vw)extra+=`<div class="ihead">As a landform</div><p class="desc">${esc(h.vw)}</p>`;
    }else{
      rows.push(['Active',`${Math.max(h.a0,h.a1)}–${Math.min(h.a0,h.a1)} Ma`]);
    }
  }
  const[hlon,hlat]=featurePos(h);   // where it sits at the displayed age
  rows.push(['Position','~'+Math.abs(hlat).toFixed(0)+'°'+(hlat>=0?'N':'S')+' '+
    Math.abs(hlon).toFixed(0)+'°'+(hlon>=0?'E':'W')]);
  if(h.k==='plume')extra+=`<div class="ihead">On position</div><p class="desc">`+
    `Plumes are anchored in the mantle while plates slide over them, so this marker `+
    `stays put and the crust moves past it. That is an approximation: Hawaii is known `+
    `to have drifted about 15° south between 81 and 47 Ma.</p>`;
  openInfo({name:h.n,tag,rows,desc:h.d1||'',extra,wide:!!extra,
    art:artFor(h.k==='impact'?'crater':h.k==='lip'?'volcanism':'plume')});
}
const COMPASS=['north','north-east','east','south-east','south','south-west','west','north-west'];
function bearingName(vx,vy){
  const b=(Math.atan2(vx,vy)*180/Math.PI+360)%360;
  return COMPASS[Math.round(b/45)%8];
}
function showFeature(l,lon,lat){
  const at=snapLabel(l,curFrame().i);
  const useLon=(lon===undefined?at[0]:lon), useLat=(lat===undefined?at[1]:lat);
  $('#infoName').textContent=l.n;
  /* Every type needs an entry. Only four were listed, so the other ten drew the
     card header as "UNDEFINED · 5 MA" — clicking any rift, lake, desert or
     crater in the app hit it. */
  const kind={continent:'Landmass',ocean:'Ocean basin',sea:'Epeiric sea',
    orogen:'Mountain belt',rift:'Rift',lake:'Lake',desert:'Desert',
    island:'Island',ice:'Ice sheet',basin:'Basin',forest:'Forest',tundra:'Tundra',
    region:'Region',plateau:'Plateau',grassland:'Grassland'}[l.t]||'Feature';
  $('#infoTag').textContent=kind+' · '+fmtAge(Math.round(state.age));
  const rows=[];
  // live measurement from the derived motion field, so the panel describes
  // this feature at THIS moment rather than quoting a fixed fact
  const fld=motionField(curFrame().i);
  if(fld){
    const m=motionAt(fld,useLon,useLat);
    if(m.cf>0.22){
      const sp=Math.hypot(m.vx,m.vy);
      rows.push(['Moving',`${sp.toFixed(0)} mm/yr ${bearingName(m.vx,m.vy)}`]);
    }
  }
  const z=elevField(curFrame().i);
  if(z){
    const e=elevAtLL(z,useLon,useLat);
    rows.push([e>=0?'Elevation':'Depth', `${Math.abs(Math.round(e)).toLocaleString()} m`]);
  }
  const span=[Math.min(l.a0,l.a1),Math.max(l.a0,l.a1)];
  rows.push(['On the map',`${fmtAge(span[1])} – ${fmtAge(span[0])}`]);
  rows.push(['Position',`${Math.abs(useLat).toFixed(0)}°${useLat>=0?'N':'S'} ${Math.abs(useLon).toFixed(0)}°${useLon>=0?'E':'W'}`]);
  const m2=nearestMeta();
  rows.push(['World then',`${m2.gmst.toFixed(1)}°C · ${m2.sealevel>=0?'+':''}${m2.sealevel} m seas`]);
  /* Prefer the description written for THIS moment in the feature's life; the
     timeless one is the fallback, not the default. */
  const ph=phaseDesc(l,state.age);
  let extra='';
  if(ph&&l.d)extra+=`<div class="ihead">In general</div><p class="desc">${esc(l.d)}</p>`;
  // What the rocks of this landmass, at this age, actually preserve.
  const reg=regionalAt(l.n,state.age);
  if(reg)extra+=`<div class="ihead">Fossil record here</div><p class="desc">${esc(reg)}</p>`;
  /* Life of the age, for anything big enough to host a biota.

     WIDENED with the province layer. The list used to stop at the biome-ish and
     basin-ish types, so 133 labels -- 40% of them, every mountain belt, basin,
     rift, desert and plateau -- showed no biota at all. That was the right call
     while the only thing on offer was one global interval list: better silence
     than the world's fauna printed under "Ural Mountains". It is the wrong call
     now that the model can name the province 126 of those 133 sat in.

     Still excluded: `ice`, `volcano` and `impact`. An ice sheet is not a habitat
     and a crater is a point, and for those the honest answer is the one the card
     already gives. */
  const BIG=new Set(['continent','ocean','sea','forest','grassland','tundra','island',
                     'region','lake','orogen','basin','rift','desert','plateau',
                     'craton','terrane']);
  if(BIG.has(l.t))extra+=lifeSection(l);
  openInfo({name:l.n,
    tag:kind+' · '+fmtAge(Math.round(state.age)),
    rows, desc:ph||l.d||featureDesc(l.n), extra, wide:!!extra,
    art:artFor(l.t,undefined,l.n)});
}
function closeInfo(){$('#info').classList.remove('show');state.selPlate=null;}
$('#infoClose').onclick=closeInfo;
function plateDesc(n){const d={
  'Pacific':'The largest plate, shrinking as subduction consumes its margins around the Ring of Fire.',
  'North America':'Carries the continent plus the western Atlantic seafloor; diverging from Eurasia at the Mid-Atlantic Ridge.',
  'Africa':'Splitting along the East African Rift, where the Somalia plate is peeling away.',
  'Eurasia':'The largest continental plate; colliding with India and Arabia to raise the Himalaya and Zagros.',
  'India':'Sprinted north from Gondwana and still drives into Asia at ~50 mm/yr.',
  'Antarctica':'Nearly ringed by spreading ridges, leaving it almost stationary over the South Pole.',
  'Australia':'The fastest-moving major continental plate, migrating north toward Asia.',
  'Nazca':'Young oceanic plate subducting beneath South America to build the Andes.',
  'South America':'Drifting west, overriding the Nazca plate along its Pacific margin.'};
  return d[n]||'One of Earth’s present-day lithospheric plates. Toggle motion vectors to see its velocity field.';}
/* ============ intervals, supercontinents, life ============ */
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function fmtSpan(a0,a1){
  const lo=Math.min(a0,a1), hi=Math.max(a0,a1);
  if(hi<=0)return `+${-hi}–${-lo} Myr`;
  if(lo<0)return `+${-lo} Myr – ${hi} Ma`;
  return `${hi}–${lo} Ma`;
}
/* The present is a boundary case: the projected "Near Future" runs (-30, 0]
   and the Quaternary runs [0, 2.58), so age 0 satisfies both. Split on sign
   first — at or after the present you want the real interval, not the
   projection that happens to end there. */
function intervalAt(age){
  const proj=age<0;
  return (DATA.eras.intervals||[]).find(i=>
    (i.rank==='projected')===proj &&
    age>=Math.min(i.a0,i.a1) && age<=Math.max(i.a0,i.a1))||null;
}
function lifeAt(age){
  return (DATA.life.life||[]).find(e=>age>=Math.min(e.a0,e.a1)&&age<=Math.max(e.a0,e.a1))||null;
}
function biomesAt(age){
  const B=DATA.life.biomes||[]; if(!B.length)return [];
  let best=B[0],bd=1e9;
  for(const b of B){const d=Math.abs(b.age-age); if(d<bd){bd=d;best=b;}}
  return best.biomes||[];
}
function regionalAt(name,age){
  const R=(DATA.life.regional||{})[name]; if(!R)return null;
  const hit=R.find(r=>age>=Math.min(r.a0,r.a1)&&age<=Math.max(r.a0,r.a1));
  return hit?hit.text:null;
}
/* A feature that lives for 300 Myr is not doing the same thing throughout, so
   long-lived entries carry a description per phase; fall back to the timeless
   one when nothing matches. */
function phaseDesc(l,age){
  if(l.ph)for(const p of l.ph){
    if(age>=Math.min(p.a0,p.a1)&&age<=Math.max(p.a0,p.a1))return p.d;
  }
  return null;
}
/* A taxon may carry its own age window w=[old,young], tighter than the
   interval it sits in -- Homo sapiens inside the Quaternary, say. Hide it when
   the slider is outside that window, so a species does not appear before it
   evolved or after it died. */
function taxonNow(t){
  if(!t.w) return true;
  return state.age<=t.w[0]+0.001 && state.age>=t.w[1]-0.001;
}
/* How big something was, in the unit a reader would use for it: a 2.5 m
   Arthropleura, a 70 cm Meganeura wingspan, a 3 mm ostracod. Fixed units make
   one of those three unreadable whichever unit is chosen. */
function sizeStr(m){
  if(!(m>0))return '';
  if(m>=1)return (m>=10?Math.round(m):Math.round(m*10)/10)+' m';
  if(m>=0.01)return Math.round(m*100)+' cm';
  return (Math.round(m*10000)/10)+' mm';
}
function lifeHTML(taxa,limit){
  taxa=taxa.filter(taxonNow);
  const I=DATA.life.icons||{};
  return '<div class="life">'+taxa.slice(0,limit||99).map(t=>{
    /* B4. The drawing was always right and the text never said how big the
       animal was or what it ate. Only the fields taxa_db actually has are
       printed, so a taxon it does not cover keeps exactly its old card
       instead of gaining a row of blanks. */
    const bits=[];
    const sz=sizeStr(t.sz); if(sz)bits.push(sz);
    if(t.dt)bits.push(esc(t.dt));
    if(t.hb)bits.push(esc(t.hb));
    const attr=bits.length?`<div class="lattr">${bits.join(' · ')}</div>`:'';
    return `<div class="lifeitem"><div class="lifeicon ${esc(t.realm)}">`+
    `<svg viewBox="0 0 64 40">${I[t.ic]||''}</svg></div>`+
    `<div class="lifetxt"><div class="ln2">${esc(t.n)}</div>`+
    `<div class="lr">${esc(t.r)} · ${esc(t.realm)}</div>`+
    `<div class="lnote">${esc(t.note)}</div>${attr}</div></div>`;
  }).join('')+'</div>';
}
/* Which organisms to show for a clicked feature.

   Two things were wrong here. Realms crossed: the old code filtered the global
   list by realm and then, if fewer than three survived, threw the filter away
   and showed everything — so clicking an ocean listed land animals, which is
   most of the record (16 of 30 intervals have under three marine taxa, and the
   Pliocene and Quaternary have none at all). And every feature drew from that
   one global list, so every plate at a given age showed the same four species.

   Now: a region's own characteristic biota wins where the fossil record
   supports one. Otherwise the global list is filtered by realm and NEVER
   un-filtered — if nothing of the right realm exists, that is stated rather
   than papered over. On a Precambrian continent that is the interesting
   answer, because the land really was bare. */
const MARINE_T=new Set(['ocean','sea']);
function regionTaxaAt(name,age){
  const R=(DATA.life.regionTaxa||{})[name]; if(!R)return null;
  return R.find(r=>age>=Math.min(r.a0,r.a1)&&age<=Math.max(r.a0,r.a1))||null;
}
/* Which biogeographic province this label sat in at this age.

   Built offline by build/provinces.py from Deep Research/modeling/paleobiogeography,
   and shipped as RUNS -- [a_lo, a_hi, id] -- because a province lasts a period
   while the timeline steps every 5 Myr. Returns the province record or null.

   This is what stopped 235 of 336 cards showing one global list. The model
   decides which province a place is in; a curated list, where there is one,
   supplies the organisms inside it; and the ten localities whose whole point is
   being ATYPICAL for their province are flagged so the model never speaks over
   them. See lifeSection below for the order. */
function provinceAt(name,age){
  const R=(DATA.life.labelProvince||{})[name]; if(!R)return null;
  for(const [a0,a1,id] of R){ if(age>=a0-2.5&&age<=a1+2.5) return (DATA.life.provinces||{})[id]||null; }
  return null;
}
function sparseAt(name,age){
  const S=(DATA.life.sparse||{})[name]; if(!S)return null;
  const h=S.find(r=>age>=Math.min(r.a0,r.a1)&&age<=Math.max(r.a0,r.a1));
  return h?h.why:null;
}
function lifeSection(l){
  const age=state.age, when=fmtAge(Math.round(age)), marine=MARINE_T.has(l.t);
  /* Which realms belong on THIS feature. An ocean/sea shows sea life only; land
     features show land/air/fresh; a lake shows freshwater and its shore. This is
     applied to EVERY list below (curated and global alike) so an ocean card can
     never list land animals nor a continent list fish -- the "mixed cards" a
     reader flagged. ("air" rides with the land, since birds/pterosaurs are read
     as over-land here, not marine.) */
  const wantR = marine?['sea']:(l.t==='lake'?['fresh','land','air']:['land','air','fresh']);
  /* THREE TIERS, AND THE HEADING ALWAYS SAYS WHICH ONE YOU ARE READING.

       1. an EXCEPTION locality  - curated, and flagged because the place is
          atypical for its province. Solnhofen, the Zechstein and Nama seas,
          the Muschelkalk, the Messinian salt basin, the Paratethys, Lake
          Pannon, the two ridge-vent faunas, the Beringian steppe-tundra. The
          model must never speak over these; being unusual is the whole point.
       2. the PROVINCE assemblage - named by the model, with the curated taxa
          inside it where we have them and its own marker taxa where we do not.
          This is the tier that did not exist: 235 of 336 labels had nothing
          between a curated list and the whole world.
       3. the GLOBAL interval list - last, and explicitly labelled global, so it
          can never read as a claim that these taxa lived at this spot. */
  const rt=regionTaxaAt(l.n,age), prov=provinceAt(l.n,age);
  const provOK = prov && (prov.r==='marine')===marine;
  if(rt&&rt.taxa&&rt.taxa.length){
    /* B5. A CURATED LIST IS NOT FILTERED BY REALM, because realm-locking is a
       property of the LOCALITY and `wantR` is derived from the label's type,
       which is only a proxy for it. Someone catalogued what lived at this place
       at this age; running that through a guess about the place discards the
       better answer in favour of the worse one.

       Measured before this change: the filter was silently hiding curated taxa
       on 37 label-spans. Solnhofen is the famous case — a marine lagoon whose
       whole significance is the pterosaurs and Archaeopteryx that fell into it,
       all dropped for being 'air' on a 'sea' card — and the Hudson Seaway lost
       Hesperornis the same way. But the bulk of it was the opposite error:
       CONTINENT cards denied their marine fauna. Cambrian Laurentia's curated
       list is four taxa and all four are marine, as the Cambrian must be, so a
       'continent' card kept none of them and fell through to the global list.

       The global list below is STILL filtered, and that is where the filter was
       always meant to live: that list is about the world, not about this place,
       so putting its land animals in an ocean is a real error. */
    const ftx=rt.taxa;
    if(ftx.length){
      let h;
      if(rt.exception){
        h=`<div class="ihead">Life here at ${when}</div>`+lifeHTML(ftx,6)+
          `<p class="desc">A locality that does not fit its region: `+
          (provOK?`the surrounding ${esc(prov.n)} looked nothing like this. `:``)+
          `It is catalogued in its own right rather than taken from the province around it.</p>`;
      }else{
        h=(provOK?`<div class="ihead">${esc(prov.n)} · ${when}</div>`
                 :`<div class="ihead">Life here at ${when}</div>`)+lifeHTML(ftx,6);
      }
      if(rt.shared)h+=`<p class="desc">${esc(rt.shared)}</p>`;
      if(provOK&&!rt.exception&&prov.note)h+=`<p class="desc">${esc(prov.note)}</p>`;
      return h;
    }
    // the curated list held nothing of this feature's realm -> fall through to
    // the province, and only then to the realm-correct global list.
  }
  /* TIER 2. No curated list, but the model can name the province -- so say what
     province this was and give its diagnostic taxa, instead of handing the
     reader the world's biota and hoping the heading carries the caveat. */
  if(provOK&&prov.mk&&prov.mk.length){
    /* Through lifeHTML, exactly like the curated lists: icon, name, rank, realm
       and a sentence. This tier used to render a bullet list of bare names,
       which looked like a lesser kind of card sitting beside the real ones --
       and was: "Lepidodendron" tells a reader nothing they did not already know
       from not knowing it. build/provinces.py resolves every marker the model
       can emit to a full record (taxa_db first, then its own table) and its
       selftest fails if any marker cannot be described. */
    const ftx=prov.mk.filter(t=>wantR.includes(t.realm));
    if(ftx.length){
      return `<div class="ihead">${esc(prov.n)} · ${when}</div>`+
        `<p class="desc">${esc(prov.note)}</p>`+lifeHTML(ftx,6)+
        (prov.c==='moderate'
          ? `<p class="desc">The province is modelled from palaeolatitude and the `+
            `block this sat on; treat its boundary as a gradient, not a line.</p>`:'');
    }
  }
  /* TIER 2b. The model named a province but has no DIAGNOSTIC taxa for it.
     That is the honest state of affairs for the generic latitude bands -- a
     "warm-temperate shelf" exists at every age from the Cambrian on, and naming
     genera for it would be an anachronism at most of them. But falling straight
     through to a bare global card threw away the one thing the model DID know:
     which province this place was in, and what that province was like.

     So keep the province heading and its note, and let the era-correct global
     list run underneath it. The reader gets the place AND the right organisms
     for the age, instead of neither. */
  const bandNote = (provOK && prov.note) ? `<div class="ihead">${esc(prov.n)} · ${when}</div>`+
      `<p class="desc">${esc(prov.note)}</p>` : '';
  const why=sparseAt(l.n,age);
  if(why)return bandNote+`<div class="ihead">Fossil record here</div><p class="desc">${esc(why)}</p>`;
  const L=lifeAt(age);
  if(!L||!L.taxa||!L.taxa.length)return '';
  const want=wantR;
  /* This is the GLOBAL list for the interval, shown because this landmass has
     no biota catalogued of its own. Two things had to change.

     First, drop what plainly did not live here. Taxa carry `en`, a set of
     region tags, when they were restricted -- and if this card's landmass has
     a known region that does not intersect, the animal is not shown. The app
     was listing Proconsul, an African ape, under North America.

     Second, the heading. It used to read "On land at 15 Ma", which on a card
     titled North America reads as a claim about North America however global
     the intent. Say "elsewhere". */
  // The label's own derived tag first (build_labels puts it there from the
  // present-day anchor), then the hand-curated table as a fallback. Without
  // the derived one this filter only ever fired on continents, so Proconsul
  // stayed in the Amazon Rainforest and mammoths stayed with it.
  const reg=l.rg||(DATA.life.labelRegion||{})[l.n]||null;
  const pick=L.taxa.filter(t=>{
    if(!want.includes(t.realm))return false;
    if(reg&&t.en&&!t.en.some(r=>reg.includes(r)))return false;
    return true;
  });
  if(pick.length){
    /* At (and just before) the present the interval's characteristic biota IS
       the real biota, so present it plainly as what lives here today rather than
       with the "nothing catalogued" caveat that made present-day cards read as
       empty. The region filter above already narrows it to this landmass. */
    /* TIER 3, and the heading has to carry the whole caveat by itself.
       "In the sea at 250 Ma" on a card titled Verkhoyansk Belt reads as a claim
       about the Verkhoyansk Belt however global the intent, so the word GLOBAL
       goes in the heading rather than only in the small print underneath. */
    /* "in the present era", not "today". Every frame spans a million years and
       the slider steps in whole Myr, so "today" claims a precision the model
       does not have -- and at 1 or 2 Ma it is simply false. */
    const recent = age<=2.6;
    const head = recent
      ? (marine?`In the sea here in the present era`:`Living here in the present era`)
      : (marine?`Worldwide in the sea at ${when}`:`Worldwide on land at ${when}`);
    const caveat = recent ? '' :
      `<p class="desc">This is the GLOBAL list for the interval — `+
      (provOK?`the model has no taxa diagnostic of this province in particular, `+
              `and nothing`
             :`neither the province model nor the catalogue can place this, and nothing`)+
      ` is catalogued for this spot. Not a claim that these lived here.</p>`;
    /* Lead with the PLACE when the model knows it. bandNote carries the
       province name and its description, so a "warm-temperate shelf" card says
       what a warm-temperate shelf is and then lists the era's organisms, rather
       than opening with a worldwide list and mentioning the province in a
       footnote. */
    return bandNote+`<div class="ihead">${head}</div>`+lifeHTML(pick,5)+caveat;
  }
  if(marine){
    return `<div class="ihead">In the sea at ${when}</div><p class="desc">`+
      `No marine group is catalogued as characteristic of this interval yet — `+
      `which is a gap in this app, not in the ocean.</p>`;
  }
  // Nothing terrestrial: for most of this timeline that is the true answer.
  const sea=L.taxa.filter(t=>t.realm==='sea');
  let h=`<div class="ihead">On land at ${when}</div><p class="desc">`+
    (age>430
      ? `Essentially nothing. Land is bare rock, sand and microbial crust — `+
        `vascular plants do not spread until the Silurian, and everything below `+
        `lived in the sea.`
      : `No land group is catalogued for this interval yet.`)+`</p>`;
  if(sea.length)h+=`<div class="ihead">In the sea instead</div>`+lifeHTML(sea,3);
  return h;
}
function listHTML(title,items){
  if(!items||!items.length)return '';
  return `<div class="ihead">${esc(title)}</div><ul class="evlist">`+
    items.map(x=>`<li>${esc(x)}</li>`).join('')+'</ul>';
}
/* A schematic for a card that has no organism to draw.

   `kind` is a feature type ("rift", "crater", "supercontinent", ...). Returns
   null when nothing is mapped, and the caller simply gets no figure — better a
   text-only card than a picture of the wrong thing. The caption is deliberately
   generic in its wording ("a rift, in cross-section") because that is what the
   drawing is: nobody surveyed THIS rift for it. */
const ART_NOTE='Generic diagram of this kind of feature, not a survey of this one.';
function artFor(kind,note,name){
  const A=DATA.art||{};
  // A named override wins: an Andean arc and a continental collision are both
  // "orogen" but are built by different mechanisms, and the generic diagram
  // would be wrong for one of them.
  const id=(name&&(A.byName||{})[name])||(A.byType||{})[kind];
  const a=id&&(A.art||{})[id];
  if(!a)return null;
  return {svg:a.svg, caption:a.caption+' '+(note===undefined?ART_NOTE:note)};
}
/* A real photograph for this feature, if one exists under a licence this
   project will ship. photos.py fetches from Wikimedia Commons and accepts only
   public domain, CC0 and plain CC-BY -- share-alike is refused for the same
   reason it is for the silhouettes. */
function photoHTML(name){
  const p=(DATA.photos||{})[name];
  if(!p)return '';
  const by=p.artist&&p.artist!=='(unattributed)'?esc(p.artist):'unattributed';
  const link=p.page?`<a href="${esc(p.page)}" target="_blank" rel="noopener">Wikimedia Commons</a>`:'Wikimedia Commons';
  return `<figure class="cardphoto zoomfig" tabindex="0" role="button"`
    +` aria-label="Enlarge photograph: ${esc(p.title)}" title="Click to enlarge">`
    +`<img src="${esc(p.file)}" alt="${esc(p.title)}" loading="lazy">`
    +`<figcaption>${esc(p.caption)}`
    +`<span class="cred">${by} · ${esc(p.licence)} · ${link}</span>`
    +`</figcaption></figure>`;
}
/* MODEL-GENERATED FIGURES.

   Distinct from the schematics in feature_art.py, and the difference is the
   point. A schematic is a drawing of what a KIND of thing looks like; these are
   drawn by "Deep Research/diagrams and illustrations/make_diagrams.py" FROM the
   app's own tables -- the oxygen panel plots climate.py's O2 column, the
   atoll/guyot panel plots the same subsidence law seamounts.py stamps into the
   sea floor -- so they cannot drift away from what the model actually does. If
   the table changes and the figure is not regenerated, the figure is wrong and
   regenerating it is one command.

   Keyed on card name. A card can carry both: the schematic says what this kind
   of thing IS, the figure says what our numbers SAY about it. */
const FIGURES={
  'Emperor Seamounts':['09-atoll-guyot-subsidence.svg',
    'Darwin’s subsidence sequence, drawn from the same half-space law the sea floor uses: island, atoll, guyot.'],
  'Sea of Japan':['10-back-arc-rollback.svg',
    'Slab roll-back opening a back-arc basin behind a subduction zone.'],
  'Glossopteris Flora':['11-glossopteris-gondwana.svg',
    'The five-continent Glossopteris distribution — the evidence Suess used in 1885 to name Gondwana.'],
  'Ontong Java Plateau':['04-lip-to-extinction-cascade.svg',
    'How a large igneous province becomes an ocean anoxic event.'],
  'Caribbean LIP':['04-lip-to-extinction-cascade.svg',
    'How a large igneous province becomes an ocean anoxic event.'],
  'Siberian Traps':['04-lip-to-extinction-cascade.svg',
    'How a large igneous province becomes a mass extinction.'],
  'Oceanic Anoxic Event 1a':['04-lip-to-extinction-cascade.svg',
    'Ontong Java to OAE 1a: the cascade, step by step.'],
  'Oceanic Anoxic Event 2':['04-lip-to-extinction-cascade.svg',
    'The Caribbean plateau to OAE 2: the cascade, step by step.'],
  'Palaeocene–Eocene Thermal Maximum':['07-cenozoic-climate-events.svg',
    'Cenozoic climate events on one axis: warmings above the line, drawdowns below.'],
  'Azolla Event':['07-cenozoic-climate-events.svg',
    'Cenozoic climate events on one axis: warmings above the line, drawdowns below.'],
  'Early Eocene Climatic Optimum':['07-cenozoic-climate-events.svg',
    'Cenozoic climate events on one axis: warmings above the line, drawdowns below.'],
  /* The only climate-event card that had no graphic at all. It also needs one
     more than the others do: every other mass extinction here has a single
     killer, and this one has two running in opposite directions -- a world
     freezing and draining, then the same world thawing and drowning in anoxic
     water. A bar on a timeline cannot say that. */
  'Hirnantian Anoxia':['13-hirnantian-two-pulses.svg',
    'The End-Ordovician in two pulses: ice grows and the shelf seas drain, then the ice melts and anoxic water floods back in.'],
  'Great Oxidation Event':['08-oxygen-through-time.svg',
    'Oxygen through time, with the Lomagundi overshoot and the crash that followed.'],
  'Guadalupian':['08-oxygen-through-time.svg',
    'Oxygen through time. The Permo-Carboniferous peak is near 30%, not 35%.'],
  'Pennsylvanian':['08-oxygen-through-time.svg',
    'Oxygen through time, from this app’s own climate table.']
};
function modelFigHTML(name){
  const f=FIGURES[name]; if(!f)return '';
  /* NOT loading="lazy". These are 5-6 KB and the element is only created when
     a card opens, so deferring buys nothing -- and a lazy image inside a panel
     that has just been written to the DOM does not always get an intersection
     callback, which showed up here as a figure that never appeared. */
  /* CLICKABLE, like the schematic above it. These are CHARTS -- an oxygen
     curve, a Cenozoic event axis -- drawn at card width, which is about 210px
     in the climate-event card. That is wide enough to see there is a graph and
     too narrow to read one, which is exactly the case the zoom overlay exists
     for. It was only ever wired to figHTML's inline SVG, so every model figure
     looked identical to a clickable schematic and did nothing. */
  return `<figure class="modelfig zoomfig" tabindex="0" role="button"`
    +` aria-label="Enlarge chart: ${esc(f[1])}" title="Click to enlarge">`
    +`<img src="figures/${f[0]}" alt="${esc(f[1])}">`
    +`<figcaption>${esc(f[1])}<span class="cred">Generated from this model’s own tables, `
    +`so it cannot disagree with the map.</span></figcaption></figure>`;
}
function figHTML(a){
  if(!a||!a.svg)return '';
  /* "slice" so that anywhere the figure is given a fixed height (the extinction
     card's dropdown is only ~158px tall in total) it crops to a banner instead
     of squashing the drawing. Where height is left to the width, the aspect
     matches the viewBox exactly and slice and meet are the same thing. */
  /* CLICKABLE. In the climate-event dropdown the figure is cropped to a ~50px
     banner, which is enough to say "there is a diagram here" and far too small
     to read one. The same markup now opens full size in an overlay, so the
     small version can stay small without the drawing being wasted. */
  return `<figure class="cardfig zoomfig" tabindex="0" role="button"`+
    ` aria-label="Enlarge: ${esc(a.caption)}" title="Click to enlarge">`+
    `<svg viewBox="0 0 300 118" role="img"`+
    ` preserveAspectRatio="xMidYMid slice" aria-hidden="true">`+
    `${a.svg}</svg><figcaption>${esc(a.caption)}</figcaption></figure>`;
}
function openInfo(o){
  $('#infoName').textContent=o.name;
  $('#infoTag').textContent=o.tag||'';
  $('#infoRows').innerHTML=(o.rows||[]).map(r=>`<div class="row">${r[0]}<b>${r[1]}</b></div>`).join('');
  const fig=$('#infoArt');
  fig.innerHTML=figHTML(o.art)+photoHTML(o.name)+modelFigHTML(o.name);
  fig.hidden=!fig.innerHTML;
  $('#infoDesc').textContent=o.desc||'';
  $('#infoExtra').innerHTML=o.extra||'';
  $('#info').classList.toggle('wide',!!o.wide);
  $('#info').scrollTop=0;
  $('#info').classList.add('show');
}
function jumpTo(age){
  state.age=Math.max(-250,Math.min(1000,age));
  state.playing=false;syncPlay();syncSlider();
  bindTextures();buildBoundaries();buildRivers();buildHotspots();buildVectors();updateReadout();
  markSidebarCurrent();markGlaciationList();markClimateEventList();markInterchangeList();
}
function showInterval(i){
  const mid=(i.a0+i.a1)/2;
  const L=lifeAt(mid), bio=biomesAt(mid);
  let extra='';
  extra+=listHTML('Key events',i.key_events);
  if(bio.length)extra+=`<div class="ihead">Biomes</div><ul class="evlist">`+
    bio.map(b=>`<li><b style="color:#c6d0dd">${esc(b.name)}</b> — ${esc(b.note)}</li>`).join('')+'</ul>';
  if(L&&L.taxa&&L.taxa.length)extra+=`<div class="ihead">Life</div>`+lifeHTML(L.taxa,8);
  openInfo({name:i.name,
    tag:(i.rank==='projected'?'Projected interval · ':'')+fmtSpan(i.a0,i.a1),
    rows:[['Span',fmtSpan(i.a0,i.a1)],['Part of',`${i.era}`]],
    desc:i.summary, extra, wide:true});
  jumpTo(mid);
}
function showSupercontinent(s){
  const rows=[['Assembly',fmtSpan(s.assembly[0],s.assembly[1])],
              ['Coherent',fmtSpan(s.peak[0],s.peak[1])],
              ['Break-up',fmtSpan(s.breakup[0],s.breakup[1])]];
  let extra='';
  if(s.life)extra+=`<div class="ihead">Life it carried</div><p class="desc">${esc(s.life)}</p>`;
  if(s.fate)extra+=`<div class="ihead">What happened to it</div><p class="desc">${esc(s.fate)}</p>`;
  /* Say WHAT is disputed, the way the glaciation cards do. All five of these
     used to print one identical sentence, which told a reader nothing about the
     difference between a supercontinent that may never have assembled and four
     rival forecasts of the next one. */
  if(s.contested)extra+=`<div class="ihead">Still argued over</div><p class="desc">${esc(s.contested)}</p>`;
  else if(s.disputed)extra+=`<div class="ihead">Contested</div><p class="desc">`+
    `This one is not settled. It is shown because it is in the published literature, `+
    `not because the reconstruction is agreed.</p>`;
  openInfo({name:s.name,tag:(s.disputed?'Disputed · ':'')+'Supercontinent',
            rows,desc:s.summary,extra,wide:true,
            art:artFor('supercontinent',
              'Schematic, not a reconstruction — for the real shape of '+
              s.name+', use the map.')});
  jumpTo(s.jump_age);
}
function buildEraList(){
  const iv=(DATA.eras.intervals||[]).slice();
  if(!iv.length)return;
  // far future -> present -> far past, which is how the timeline reads
  iv.sort((a,b)=>((a.a0+a.a1)/2)-((b.a0+b.a1)/2));
  let html='',group=null;
  for(const i of iv){
    if(i.era!==group){group=i.era;html+=`<div class="gh">${esc(group)}</div>`;}
    html+=`<div class="erow${i.rank==='projected'?' proj':''}" data-era="${esc(i.name)}">`+
      `<span class="en">${esc(i.name)}</span><span class="ea">${fmtSpan(i.a0,i.a1)}</span></div>`;
  }
  const box=$('#eraList'); box.innerHTML=html;
  box.querySelectorAll('.erow').forEach(el=>{
    el.onclick=()=>{const i=iv.find(x=>x.name===el.dataset.era); if(i)showInterval(i);};
  });
}
function buildScList(){
  const sc=(DATA.eras.supercontinents||[]).slice();
  if(!sc.length)return;
  sc.sort((a,b)=>a.jump_age-b.jump_age);
  const box=$('#scList');
  box.innerHTML=sc.map(s=>
    `<div class="srow" data-sc="${esc(s.name)}"><div class="sn">${esc(s.name)}</div>`+
    `<div class="sa">${fmtSpan(Math.min(...s.breakup),Math.max(...s.assembly))}</div>`+
    (s.disputed?'<div class="sd">Disputed</div>':'')+`</div>`).join('');
  box.querySelectorAll('.srow').forEach(el=>{
    el.onclick=()=>{const s=sc.find(x=>x.name===el.dataset.sc); if(s)showSupercontinent(s);};
  });
}
let _curEra=null;
function markSidebarCurrent(){
  const i=intervalAt(state.age), n=i?i.name:null;
  if(n===_curEra)return; _curEra=n;
  document.querySelectorAll('.erow').forEach(el=>
    el.classList.toggle('cur',el.dataset.era===n));
  document.querySelectorAll('.srow').forEach(el=>{
    const s=(DATA.eras.supercontinents||[]).find(x=>x.name===el.dataset.sc);
    el.classList.toggle('cur',!!s&&state.age>=Math.min(...s.breakup)&&state.age<=Math.max(...s.assembly));
  });
}
document.querySelectorAll('.panel .ph').forEach(h=>{
  h.onclick=()=>h.parentElement.classList.toggle('open');
});
function showEraPlate(d){
  const p=DATA.plates.find(x=>x.name===d.n);
  if(p&&presentFade()>0.4){showPlate(p,d.lon,d.lat);return;}
  openInfo({name:d.n,tag:'Plate · '+fmtAge(Math.round(state.age)),
    rows:[['Relative size',d.s>2?`${d.s}`:'small'],
          ['Position',`${Math.abs(d.lat).toFixed(0)}°${d.lat>=0?'N':'S'} ${Math.abs(d.lon).toFixed(0)}°${d.lon>=0?'E':'W'}`]],
    desc:'A plate in this reconstruction, tracked back from the surveyed present-day '+
         'plate model and carried along the measured motion field. Plates merge going '+
         'backwards as their relative motion falls to nothing, so there are fewer of '+
         'them the deeper you go.'});
}

function featureDesc(n){const d={
  'Pangaea':'The last supercontinent, assembled ~320 Ma; its arid interior spawned vast red-bed deserts.',
  'Pangaea Proxima':'A projected future supercontinent forming as the Atlantic closes and continents re-fuse around Africa.',
  'Rodinia':'A Precambrian supercontinent (~1000 Ma) at the heart of the Neoproterozoic world.',
  'Gondwana':'The southern supercontinent (South America, Africa, India, Australia, Antarctica) that drifted across the South Pole.',
  'Laurasia':'The northern half of Pangaea (North America + Eurasia) after the Tethys and Atlantic began to open.',
  'Panthalassa':'The world-ocean that surrounded Pangaea — ancestor of the Pacific.',
  'Tethys Ocean':'The tropical seaway between Gondwana and Laurasia, cradle of vast carbonate platforms.',
  'Iapetus Ocean':'The early-Paleozoic ocean that closed to build the Caledonian and Appalachian mountains.',
  'Neo-Panthalassa':'The projected future world-ocean on the far side of Pangaea Proxima.'};
  return d[n]||'An era-specific paleogeographic feature, reconstructed from PALEOMAP data.';}

/* ================= labels =================
   Anchoring every name straight onto its feature reads fine when features are
   spread out and turns into an unreadable pile when they are not: at 325 Ma the
   Appalachian, Alleghanian, Ouachita and Antler belts are four names inside one
   corner of Pangaea. So placement is a layout problem, not a projection
   problem. Names are sorted by importance and placed greedily, each taking the
   nearest free slot to its anchor; a name pushed more than a few pixels gets a
   leader line back to the feature, and one that cannot fit anywhere near its
   anchor is dropped rather than drawn on top of something else. */
const labelEls=new Map();
const plateEls=[];
const PRI={continent:100,ocean:90,sea:72,region:66,orogen:60,ice:58,desert:56,
           forest:55,tundra:53,grassland:52,plateau:50,basin:48,rift:47,island:44,plate:30};
/* A little slack either side stops names strobing on and off as the slider
   crosses a window edge, but 6 Myr was enough to float future-only features
   like Baja Island over the present-day map. Keyframes are 5 Myr apart, so
   half that is all the smoothing this needs -- EXCEPT for the recent lakes,
   whose windows are only thousands of years: a flat 2.5 Myr slack floated
   Pleistocene lakes (Agassiz, Bonneville) onto the present-day map, so cap the
   slack at half the window for anything shorter than 5 Myr. */
/* The slack keeps a name from flickering on and off as the age crosses its
   window edge during playback. It used to be 2.5 Myr, which is half a keyframe
   — long enough for a label to outlive the thing it names: the Western Interior
   Seaway drains out of the terrain by 70 Ma and the name hung on to 67.5.
   0.8 Myr still covers the jitter without claiming a feature exists after the
   map has stopped drawing it. */
function labelVisible(l){const a=state.age,t=Math.min(0.8,Math.abs(l.a1-l.a0)*0.5);
  return a>=Math.min(l.a0,l.a1)-t&&a<=Math.max(l.a0,l.a1)+t;}
function ensureLabels(){
  const box=$('#labels');
  for(const l of DATA.labels){
    if(labelEls.has(l))continue;
    const e=document.createElement('div');
    e.className='plabel '+l.t; e.textContent=l.n;
    e.title=l.n;
    e.addEventListener('click',ev=>{ev.stopPropagation();showFeature(l);});
    box.appendChild(e); labelEls.set(l,e);
  }
}
function measureEl(e){
  const key=e.innerHTML;
  if(e._mk===key)return;
  e._mk=key; e._mw=e.offsetWidth||42; e._mh=e.offsetHeight||14;
}
/* Candidate offsets from the anchor: on it first, then progressively further,
   vertical before horizontal because a name reads best directly above or below
   the thing it names. Horizontal steps are stretched since labels are wide. */
const RINGS=(()=>{
  const o=[[0,0]];
  for(const r of [16,29,44,62,82])
    for(const a of [90,270,50,130,230,310,0,180])
      o.push([Math.cos(a*DEG)*r*1.45, -Math.sin(a*DEG)*r]);
  return o;
})();
/* Panels are opaque, so a name underneath one is simply lost. Read their real
   rects so this stays right as panels collapse, open and resize -- but not
   EVERY frame: layoutLabels writes label styles each frame, so a same-frame
   getBoundingClientRect forces a synchronous reflow against dirty layout.
   Panels move on user actions, not per frame; a 200 ms-stale rect is
   indistinguishable on screen and the forced reflow goes away. */
let _uiRects=null,_uiRectsAt=-1e9;
addEventListener('resize',()=>{_uiRectsAt=-1e9;});
function uiRects(){
  const now=performance.now();
  if(_uiRects&&now-_uiRectsAt<200)return _uiRects;
  const out=[];
  /* Use #title and #readout rather than #topbar: the bar spans the full width
     and stands 210px tall to fit the readout, but it is transparent in
     between, and excluding the whole band cost the upper third of the globe. */
  for(const sel of ['#leftrail','#controls','#title','#readout','#bottom','#info']){
    const el=$(sel); if(!el)continue;
    const cs=getComputedStyle(el);
    if(cs.display==='none'||+cs.opacity<0.05)continue;
    const r=el.getBoundingClientRect();
    if(r.width>0&&r.height>0)out.push(r);
  }
  _uiRects=out;_uiRectsAt=now;
  return out;
}
let _leadStr='';
function drawLeaders(list){
  const s=$('#leaders');
  const str=list.map(l=>`<line x1="${l[0].toFixed(1)}" y1="${l[1].toFixed(1)}" x2="${l[2].toFixed(1)}" y2="${l[3].toFixed(1)}"/>`).join('');
  if(str===_leadStr)return;
  _leadStr=str;
  s.setAttribute('width',innerWidth); s.setAttribute('height',innerHeight);
  s.setAttribute('viewBox',`0 0 ${innerWidth} ${innerHeight}`);
  s.innerHTML=str;
}
function layoutLabels(){
  const fi=curFrame().i;
  const cands=[];
  if(state.layers.labels){
    for(const[l,e]of labelEls){
      if(!labelVisible(l)){e.classList.remove('show');continue;}
      const sp=snapLabel(l,fi);
      if(!sp){e.classList.remove('show');continue;}
      const p=projectLL(sp[0],sp[1]);
      if(!p.vis){e.classList.remove('show');continue;}
      cands.push({e,x:p.x,y:p.y,pri:(PRI[l.t]||40)+(l.w||0)});
    }
  }else for(const[,e]of labelEls)e.classList.remove('show');
  /* Don't print a plate name the era-label layer is already showing —
     "NORTH AMERICA" stacked on "North America" is just noise. */
  const shown=new Set();
  for(const[l,e]of labelEls)if(e.classList.contains('show')||cands.some(c=>c.e===e))shown.add(l.n.toLowerCase());
  const plist=state.layers.boundaries?eraPlates().p.filter(d=>!shown.has(d.n.toLowerCase())):[];
  const box=$('#labels');
  while(plateEls.length<plist.length){
    const e=document.createElement('div'); e.className='plabel plate';
    e.addEventListener('click',ev=>{ev.stopPropagation();if(e._pd)showEraPlate(e._pd);});
    box.appendChild(e); plateEls.push(e);
  }
  for(let i=0;i<plateEls.length;i++){
    const e=plateEls[i], d=plist[i];
    if(!d){e.classList.remove('show');e._pd=null;continue;}
    e._pd=d;
    const html=d.n+(d.s>2?` <span class="sp">${d.s}</span>`:'');
    if(e.innerHTML!==html)e.innerHTML=html;
    const p=projectLL(d.lon,d.lat);
    if(!p.vis){e.classList.remove('show');continue;}
    cands.push({e,x:p.x,y:p.y,pri:PRI.plate});
  }

  cands.sort((a,b)=>b.pri-a.pri);
  /* NO ZOOM DECLUTTER (user round, 2026-08-02). A tiering by zoom shipped on
     2026-08-01 -- only high-priority names survived far out -- and it made the
     map unreadable in a different way: a name that is present at one distance
     and gone at another cannot be checked for, so it became impossible to tell
     a label the model LACKS from one the view is withholding. Everything that
     can be placed is now placed at every zoom, and collision avoidance below is
     the only thing that ever hides a name. */
  const minPri=0, cap=Infinity;
  const panels=uiRects(), placed=[], leaders=[];
  const GAP=3;
  let nplaced=0;
  for(const c of cands){
    if(c.pri<minPri||nplaced>=cap){c.e.classList.remove('show');continue;}
    const e=c.e; measureEl(e);
    const w=e._mw+GAP*2, h=e._mh+GAP*2;
    let put=null;
    for(const[ox,oy]of RINGS){
      const x=c.x+ox, y=c.y+oy;
      if(x-w/2<4||x+w/2>innerWidth-4||y-h/2<4||y+h/2>innerHeight-4)continue;
      let hit=false;
      for(const r of placed)
        if(Math.abs(x-r.x)<(w+r.w)/2+2&&Math.abs(y-r.y)<(h+r.h)/2+2){hit=true;break;}
      if(!hit)for(const r of panels)
        if(x+w/2>r.left-2&&x-w/2<r.right+2&&y+h/2>r.top-2&&y-h/2<r.bottom+2){hit=true;break;}
      if(!hit){put={x,y};break;}
    }
    if(!put){e.classList.remove('show');continue;}
    placed.push({x:put.x,y:put.y,w,h});
    nplaced++;
    e.style.left=put.x+'px'; e.style.top=put.y+'px'; e.classList.add('show');
    if(Math.hypot(put.x-c.x,put.y-c.y)>17)leaders.push([c.x,c.y,put.x,put.y]);
  }
  drawLeaders(leaders);
}

/* ================= time & environment ================= */
function fmtAge(a){if(a===0)return'Present';return a>0?`${a} Ma`:`+${-a} Myr`;}
function presentFade(){const a=state.age;// present-day layers fade out into deep time / future
  if(a<=0)return a<-30?0:1+ a/30*0; // future: fade fast
  return Math.max(0,1-a/45);}
function curFrame(){return frameAt(state.age);}
function nearestMeta(){const A=ages();let bi=0,bd=1e9;A.forEach((v,i)=>{const d=Math.abs(v-state.age);if(d<bd){bd=d;bi=i;}});return DATA.timeline[bi];}
function updateReadout(){
  const m=nearestMeta(); const cf=curFrame();
  $('#age').textContent=fmtAge(Math.round(state.age));
  let epoch=m.epoch,period=m.period;
  if(state.age<-5){ // future: no geologic period
    period='Future projection';
    epoch = state.age<=-170?'Pangaea Proxima':state.age<=-60?'Atlantic closing':'Near future';
  }
  $('#eraName').textContent=epoch;$('#periodName').textContent=period;
  /* What the map DRAWS, not what the table intends. This used to read the
     threshold -- anything warmer than the ice-free sentinel counted as polar
     caps -- and announced ice caps at 41 keyframes that drew none, because an
     interpolated ice line at 88 degrees is a cap five degrees across that
     nothing can render. iceLand/iceSea are measured per keyframe by
     refresh_manifest and describe the picture in front of you. */
  const iceL=m.iceLand||0, iceS=m.iceSea||0;
  const iceWord = iceL>0.06 ? 'continental sheets'
                : iceL>0.01 ? 'polar caps'
                : (iceL>0.002||iceS>0.02) ? 'small polar ice'
                : iceS>0.002 ? 'sea ice only' : 'ice-free';
  /* The climate STATE is named from the same number the readout prints, on
     PhanDA's own thresholds (Judd et al. 2024): icehouse below 18 C, cool
     greenhouse to 24, warm greenhouse to 30, hothouse above.

     It used to be named from `temp`, the -1..+1 anomaly proxy the shader uses,
     which is a different quantity with different breakpoints -- so at 250 Ma the
     readout said "28.5 C" and "Hothouse" side by side, when 28.5 C is a warm
     greenhouse in the scheme being invoked. Naming the state from the
     temperature makes the two halves of the same line agree. */
  /* The vegetation label describes extent, but direction matters: in the past
     a partly-vegetated world is greening, in the projected future it is a
     biosphere in RETREAT as the supercontinent and brightening Sun push life
     to the margins — "spreading forests" would read exactly backwards there. */
  const veg = state.age<0
    ? (m.veg<0.05?'Barren land':m.veg<0.35?'Refugia only':m.veg<0.6?'Retreating to margins':m.veg<0.85?'Thinning, drylands spreading':'Vegetated')
    : (m.veg<0.05?'Barren land':m.veg<0.4?'Sparse land plants':m.veg<0.85?'Spreading forests':'Vegetated');
  const L=(k)=>{const A=DATA.timeline[cf.i],B=DATA.timeline[cf.j];return A[k]+(B[k]-A[k])*cf.t;};
  const gmst=L('gmst'), co2=L('co2'), o2=L('o2'), sol=L('sol');
  const tw = gmst>30 ? 'Hothouse' : gmst>24 ? 'Warm greenhouse'
           : gmst>18 ? 'Cool greenhouse' : 'Icehouse';
  /* Solar luminosity, from the standard solar model — the faint young Sun in
     the deep past (about 8% dimmer at 1000 Ma) brightening to a few percent
     above today in the far future. Only shown once it is large enough to
     matter, so the present sits without a near-zero "+0.0%". */
  const sunStr = (sol===undefined||Math.abs(sol)<0.2) ? ''
    : ` &nbsp;·&nbsp; <b>Sun</b> ${sol>0?'+':''}${sol.toFixed(1)}%`;
  /* Be honest about what is measured and what is not. Proxy CO2 runs out in
     the Ordovician and there is NO published eustatic sea-level curve at all
     before 541 Ma — the standard compilations start at the Cambrian base. Any
     number shown deeper than that is model output with an uncertainty span of
     roughly an order of magnitude, and the readout should say so rather than
     present it with the same authority as a Cenozoic value. The future is
     projection by the same token. */
  const modelled = state.age>540 || state.age<0;
  const tag = modelled
    ? `<span style="color:#7a8494">&nbsp;· ${state.age<0?'projected':'modelled'}</span>` : '';
  /* Biomes are what the world would actually look like to stand in, which the
     scalar readouts above never convey. Names are era-appropriate: there is no
     grassland before the Cenozoic and no land biome at all worth the word
     before plants, so this reads "microbial crust" in the Precambrian rather
     than dressing bare rock up as tundra. */
  const bio=biomesAt(state.age).slice(0,3).map(b=>b.name);
  /* Background extinction rate (extinctions per million species-years), spiking
     when the timeline crosses a mass extinction. Deep-time values are estimates,
     hence the "~". */
  const xr=extinctionInfo(state.age);
  const xrStr=xr.rate<10?xr.rate.toFixed(1):Math.round(xr.rate).toLocaleString();
  $('#env').innerHTML=
     `<b>Avg temp</b> ${gmst.toFixed(1)}&deg;C &nbsp;·&nbsp; <b>Sea level</b> ${m.sealevel>=0?'+':''}${m.sealevel} m<br>`
    +`<b>CO<sub>2</sub></b> ${Math.round(co2).toLocaleString()} ppm &nbsp;·&nbsp; <b>O<sub>2</sub></b> ${o2.toFixed(1)}%${tag}<br>`
    +`<b>Climate</b> ${tw} &nbsp;·&nbsp; <b>Ice</b> ${iceWord}${sunStr}<br>`
    +`<b>Extinction rate</b> ~${xrStr} E/MSY <span style="color:#8790a0">(${xr.label})</span><br>`
    +`<b>Biosphere</b> ${veg}`
    +(bio.length?`<br><b>Biomes</b> ${bio.map(esc).join(' · ')}`:'');
  markSidebarCurrent();
  updateExtinction();updateContextCards();
}

/* Mass-extinction events. Each has phases keyed to age windows: the extinction
   itself plus ~5 Myr (title = the event), then one or more "Aftermath" phases
   that run for as long as the crisis kept reshaping the planet. A phase is
   active when lo <= age <= hi (age decreases toward the present, so a phase's
   younger edge is `lo`). Content: causes, effects, the die-off, and the legacy. */
const MASS_EXTINCTIONS=[
 {name:"End-Ordovician", phases:[
   {hi:445,lo:440,t:"End-Ordovician Mass Extinction",b:`The second-largest extinction of the Phanerozoic, and the only great one driven by <b>cold</b>. As Gondwana drifted over the South Pole, a short, sharp ice age locked water into ice sheets and dropped sea level by roughly 100 m, draining the shallow tropical shelves where almost all life then lived. A few hundred thousand years later the glaciers melted, seas rose, and oxygen-poor water spread back over the shelves — a lethal one-two punch. About <b>85% of marine species</b> vanished: graptolites, brachiopods, trilobites, conodonts and the first reef-builders. Life was still almost wholly marine, so the land came through largely untouched.`},
   {hi:440,lo:432,t:"Aftermath: Silurian Recovery",b:`Recovery was relatively quick. The cold-tolerant survivors — the "<i>Hirnantia</i>" fauna — gave way as warm shelf seas returned and diversity rebuilt through the Early Silurian. But the reef ecosystems took millions of years to reassemble, and the graptolites never recovered their former reach. The event reshuffled which groups would dominate the Silurian seas.`},
 ]},
 {name:"Late Devonian", phases:[
   {hi:372,lo:367,t:"Late Devonian Mass Extinction",b:`A drawn-out crisis of pulses rather than a single blow, centred on the Frasnian–Famennian boundary. Widespread <b>ocean anoxia</b> — recorded in black "Kellwasser" shales — repeatedly starved the seas of oxygen, amplified by cooling and, many argue, by the spread of the first forests: deep-rooted land plants weathered rock and flushed nutrients into the oceans, triggering algal blooms and dead zones. Around <b>75% of species</b> were lost. The great stromatoporoid–coral reefs — the largest the world had yet built — collapsed, and armoured placoderm fish were nearly wiped out.`},
   {hi:367,lo:358,t:"Aftermath: The Reef Gap",b:`The oceans fell into a prolonged "reef gap": metazoan reefs stayed rare through the rest of the Devonian and deep into the Carboniferous, more than 100 million years passing before reef systems of comparable scale returned. A final pulse near the period's end (the Hangenberg event) struck again. On land, the earliest tetrapods kept taking shape, and the survivors set the stage for the coming coal forests.`},
 ]},
 {name:"End-Permian", phases:[
   {hi:252,lo:247,t:"End-Permian Mass Extinction — “The Great Dying”",b:`The largest extinction in Earth's history — the closest complex life has come to ending. The <b>Siberian Traps</b>, one of the greatest volcanic outpourings ever, erupted through coal and salt beds and pumped vast volumes of CO₂, methane and sulphur into the air over tens of thousands of years. Temperatures soared, the oceans acidified, lost their oxygen and turned <b>euxinic</b> — poisoned with hydrogen sulphide — while the land baked and dried. About <b>96% of marine species</b> and some 70% of land-vertebrate families died. Reefs, trilobites and the entire dominant Permian order of life were annihilated.`},
   {hi:247,lo:243,t:"Aftermath: The Dead Zone",b:`For millions of years the Early Triassic was a hot, impoverished dead zone. Coal vanishes from the rock record — a "coal gap" — reefs are absent, and a handful of disaster taxa like the clam <i>Claraia</i> and the burrowing, pig-snouted <i>Lystrosaurus</i> dominated near-empty ecosystems. Repeated pulses of extreme warming kept knocking any recovery back down.`},
   {hi:243,lo:237,t:"Aftermath: The Long Recovery",b:`Full recovery took around <b>8–10 million years</b> — far longer than any other extinction. Only once the climate finally steadied did new groups radiate into the emptied world: the first archosaurs and, from them, the ancestors of the dinosaurs, alongside the earliest marine reptiles and the first modern-style reefs. The Permian world did not return; a new one was built on its ruins.`},
 ]},
 {name:"End-Triassic", phases:[
   {hi:201,lo:196,t:"End-Triassic Mass Extinction",b:`As Pangaea began to tear apart, the <b>Central Atlantic Magmatic Province</b> flooded a region the size of a continent with lava, releasing CO₂ that spiked global warming and acidified the oceans. About <b>76% of species</b> vanished, including many large amphibians, most of the conodonts, and the crurotarsan archosaurs — crocodile-line reptiles that until then had rivalled the early dinosaurs. The event emptied ecological niches on land and at sea alike.`},
   {hi:196,lo:189,t:"Aftermath: The Age of Dinosaurs Begins",b:`With their chief competitors gone, the <b>dinosaurs radiated</b> to dominate terrestrial ecosystems for the next 135 million years. The Jurassic opened with new marine reptiles — ichthyosaurs and plesiosaurs — and fresh ammonoid faunas filling the emptied seas, and with the first truly giant dinosaurs beginning to appear.`},
 ]},
 {name:"End-Cretaceous", phases:[
   {hi:66,lo:61,t:"End-Cretaceous (K–Pg) Mass Extinction",b:`A <b>10-km asteroid</b> struck Chicxulub, in what is now the Yucatán, with the energy of billions of atomic bombs — while the Deccan Traps were already erupting in India. The impact threw a global veil of dust and sulphate aerosols into the sky that blocked sunlight for months to years, collapsing photosynthesis on land and in the surface ocean; wildfires, tsunamis and a brief pulse of searing heat followed. About <b>76% of species</b> died, including <b>all non-avian dinosaurs</b>, the ammonites, the great marine reptiles, and much of the plankton at the base of ocean food webs.`},
   {hi:61,lo:56,t:"Aftermath: The Empty World",b:`The earliest Paleocene was a stunned, low-diversity world. "Disaster" ferns and hardy weeds recolonised scorched ground first; ocean productivity stayed depressed for tens to hundreds of thousands of years — a "Strangelove ocean" nearly emptied of surface life. The survivors were mostly small, generalist and burrowing animals that could shelter and scavenge through the dark.`},
   {hi:56,lo:50,t:"Aftermath: The Rise of Mammals",b:`With the dinosaurs gone, <b>mammals</b> — until then small and nocturnal — radiated explosively into the empty niches, growing larger and more varied within a few million years. Birds (the last surviving dinosaurs) and flowering plants diversified alongside them, assembling the recognisably modern world. A sharp warming spike, the PETM, would soon test that new order.`},
 ]},
 {name:"Holocene (Sixth) Extinction", proposed:true, phases:[
   {hi:0.06,lo:-0.6,t:"Holocene / Anthropocene Extinction (in progress)",b:`A proposed <b>sixth mass extinction</b> — unfolding now, and unique in being driven by a single species. Since the late Pleistocene, habitat loss, overexploitation, invasive species, pollution and rapid climate change have pushed extinction rates to an estimated <b>100–1,000× the natural background</b>. The megafauna went first (mammoths, giant ground sloths, moas); amphibians, reef corals, freshwater life and insects are in steep decline now. <b>The debate:</b> rates are unambiguously and sharply elevated, but cumulative losses so far — a few percent of assessed species — have not yet reached the ~75% threshold that defines the Big Five. Whether Earth has entered a true mass extinction, or is on a trajectory toward one within centuries if trends hold, is genuinely contested (Barnosky et al. 2011, <i>Nature</i>; Ceballos et al. 2015; IUCN Red List). Unlike the ancient events, its scale is still ours to decide.`},
   {hi:-0.6,lo:-8,t:"Aftermath: Projected Recovery",b:`<b>Projection, not record.</b> Should a full sixth extinction run its course, the Big Five suggest what follows: reefs and large-bodied animals lost first, ecosystems simplified and run by weedy generalists, and a rebuilding of biodiversity measured not in human lifetimes but in <b>millions of years</b> — the seas took ~10 Myr to recover after the End-Permian. What actually happens along this stretch of the timeline is unwritten, and depends on choices made now.`},
 ]},
];
let extinctExpanded=false, extinctKey=null, extinctShown=false;
function extinctPhaseAt(age){
  for(const ev of MASS_EXTINCTIONS)for(let i=0;i<ev.phases.length;i++){
    const p=ev.phases[i];
    if(age<=p.hi && age>=p.lo) return {ev,p,i};
  }
  return null;
}
function positionExtinct(){
  const box=$('#extinctBox'); if(!box||box.classList.contains('hidden')) return;
  // Sit just under the controls panel. The CSS top is a good static default;
  // refine it from the panel's real height only when the layout is valid (the
  // in-app preview pane can report a collapsed 0-size layout).
  const c=$('#controls').getBoundingClientRect();
  if(c.bottom>80 && innerHeight>0) box.style.top=(c.bottom+12)+'px';
}
// Called every frame; only touches the DOM when the active phase actually
// changes, so it is cheap to poll.
function updateExtinction(){
  const box=$('#extinctBox'); if(!box) return;
  const cur=extinctPhaseAt(state.age);
  if(!cur){ if(extinctShown){box.classList.add('hidden');extinctShown=false;extinctKey=null;markExtinctList(null);positionContext();} return; }
  const key=cur.ev.name+'|'+cur.p.t;
  if(key!==extinctKey){
    extinctKey=key;
    const after=cur.p.t.indexOf('Aftermath')===0;
    const eb=$('#extinctEyebrow');
    eb.textContent=after?'Aftermath':(cur.ev.proposed?'Proposed Extinction':'Mass Extinction');
    eb.className=after?'after':'';
    $('#extinctTitle').textContent=cur.p.t.replace(/^Aftermath: /,'');
    // The figure goes in the collapsible body, so it costs nothing until the
    // card is opened. Aftermath phases describe recovery, not the boundary
    // itself, so they get no figure rather than a misleading one.
    // Shorter note than ART_NOTE: this card is 210px wide, and the standard
    // three-line disclaimer would outweigh the figure it qualifies.
    const xa=after?null:artFor('extinction',
      cur.ev.proposed
        ? 'This one has no boundary layer yet — it is measured in living '+
          'populations, not read from rock.'
        : 'Generic diagram, not this event’s own section.');
    $('#extinctBody').innerHTML=(xa?figHTML(xa):'')+cur.p.b;
    box.classList.toggle('open', extinctExpanded);
    markExtinctList(cur);
  }
  if(!extinctShown){ box.classList.remove('hidden'); extinctShown=true; positionExtinct(); positionContext(); }
}
$('#extinctHead').addEventListener('click',()=>{
  extinctExpanded=!extinctExpanded;
  $('#extinctBox').classList.toggle('open', extinctExpanded);
});
// Peak extinction rate during each event's main pulse, as a multiple of the
// contemporary background (very rough — these are order-of-magnitude estimates).
const EX_SEV={"End-Ordovician":120,"Late Devonian":70,"End-Permian":500,
              "End-Triassic":90,"End-Cretaceous":250,"Holocene (Sixth) Extinction":300};
function bgRate(age){
  // Background genus extinction rate in E/MSY (extinctions per million
  // species-years). The Phanerozoic background DECLINED — high and volatile in
  // the early Paleozoic, lower and steadier by the Cenozoic (Raup & Sepkoski;
  // Alroy). ~0.3 today rising to ~2 in the early Paleozoic. Shown with "~".
  return 0.3 + 1.7*Math.min(1, Math.max(0,age)/470);
}
function extinctionInfo(age){
  const bg=bgRate(age), cur=extinctPhaseAt(age);
  if(!cur) return {rate:bg, label:'background'};
  if(cur.p.t.indexOf('Aftermath')===0) return {rate:bg*5, label:'elevated · recovering'};
  return {rate:bg*(EX_SEV[cur.ev.name]||60),
          label: cur.ev.proposed?'proposed 6th extinction' : 'mass extinction'};
}
// Jump the timeline to a phase (from the Mass-extinctions panel) and open the card.
function jumpToExtinction(evName, phase){
  const ev=MASS_EXTINCTIONS.find(e=>e.name===evName); if(!ev) return;
  const p=ev.phases[phase]; if(!p) return;
  extinctExpanded=true;
  jumpTo((p.hi+p.lo)/2);
}
function buildExtinctionList(){
  const box=$('#exList'); if(!box) return;
  const evs=MASS_EXTINCTIONS.slice().sort((a,b)=>a.phases[0].hi-b.phases[0].hi); // recent -> deep past
  let html='';
  for(const ev of evs){
    const m=ev.phases[0];
    const date=m.hi<0.1?'now':fmtAge(Math.round(m.hi));
    html+=`<div class="exrow${ev.proposed?' proj':''}" data-ev="${esc(ev.name)}" data-ph="0">`
        +`<span class="exn">${esc(ev.name.replace(' (Sixth) Extinction',''))}`
        +`${ev.proposed?' <span class="exq">proposed</span>':''}</span>`
        +`<span class="exd">${date}</span></div>`;
    for(let k=1;k<ev.phases.length;k++){
      html+=`<div class="exsub" data-ev="${esc(ev.name)}" data-ph="${k}">`
          +`${esc(ev.phases[k].t.replace(/^Aftermath: /,'↳ '))}</div>`;
    }
  }
  box.innerHTML=html;
  box.querySelectorAll('[data-ev]').forEach(el=>{ el.onclick=()=>jumpToExtinction(el.dataset.ev, +el.dataset.ph); });
}
/* Glaciations: the third navigable structure in the left rail, after the
   intervals and the supercontinents. It is deliberately NOT a list of
   intervals -- an ice age cuts across the timescale's divisions -- and not a
   list of features either, because it is a state of the whole system rather
   than a place. Data comes from eras.json; the card reuses openInfo so it
   gets the ice-sheet figure and the same layout as everything else. */
function glaciationsList(){
  return ((DATA.eras&&DATA.eras.glaciations)||[]).slice()
    .sort((a,b)=>a.a1-b.a1);   // recent first, matching the extinctions above
}
function buildGlaciationList(){
  const box=$('#glList'); if(!box) return;
  const gs=glaciationsList();
  box.innerHTML=gs.map((g,i)=>{
    const snow=/snowball/i.test(g.kind||'');
    return `<div class="glrow${snow?' snow':''}" data-gl="${i}">`
      +`<span class="gn">${esc(g.name)}<span class="gk">${esc(g.kind||'')}</span></span>`
      +`<span class="gd">${esc(fmtSpan(g.a0,g.a1))}</span></div>`;
  }).join('');
  box.querySelectorAll('[data-gl]').forEach(el=>{
    el.onclick=()=>{ const g=glaciationsList()[+el.dataset.gl]; if(g) showGlaciation(g); };
  });
}
function glaciationAt(age){
  return glaciationsList().find(g=>age>=Math.min(g.a0,g.a1)&&age<=Math.max(g.a0,g.a1))||null;
}
function markGlaciationList(){
  const cur=glaciationAt(state.age), gs=glaciationsList();
  document.querySelectorAll('#glList [data-gl]').forEach(el=>
    el.classList.toggle('cur', !!cur && gs[+el.dataset.gl]===cur));
}
/* Climate events: the FIFTH navigable structure, and the one whose contents can
   never be drawn. A hyperthermal or an ocean anoxic event lasts between 200,000
   years and about a million; the keyframes are 5 Myr apart, so no field the app
   could ship would resolve one. The card is the only place they can live, and
   without it the app was silent about the PETM — the single best-documented
   rapid warming in the record — while drawing the world it happened in.

   The Great Oxidation Event carries `offmap`: at 2.46–2.06 Ga it is a billion
   years before this map's oldest frame. It is listed, described, and never
   jumped to; saying "off the edge of this map" beats omitting the largest
   change in the history of Earth's surface. */
function climateEventsList(){
  return ((DATA.eras&&DATA.eras.climateEvents)||[]).slice()
    .sort((a,b)=>a.a1-b.a1);
}
function buildClimateEventList(){
  const box=$('#ceList'); if(!box) return;
  const es=climateEventsList();
  box.innerHTML=es.map((e,i)=>
    `<div class="glrow ce${e.offmap?' offmap':''}" data-ce="${i}">`
    +`<span class="gn">${esc(e.short||e.name)}<span class="gk">${esc(e.kind||'')}</span></span>`
    +`<span class="gd">${esc(e.offmap?'before this map':fmtSpan(e.a0,e.a1))}</span></div>`).join('');
  box.querySelectorAll('[data-ce]').forEach(el=>{
    el.onclick=()=>{ const e=climateEventsList()[+el.dataset.ce]; if(e) showClimateEvent(e); };
  });
}
/* BIOTIC INTERCHANGES — the sixth panel, and it exists for the same reason the
   fifth does: the map cannot show this. A land bridge is a few tens of km of
   ground, and Panama and the Bering Strait are both far under what a 20 km grid
   resolves, so the globe can draw two continents approaching and never draw the
   moment they touch — which is the only moment that matters. */
function interchangeList(){
  return ((DATA.eras&&DATA.eras.interchanges)||[]).slice().sort((a,b)=>a.a1-b.a1);
}
function buildInterchangeList(){
  const box=$('#biList'); if(!box) return;
  box.innerHTML=interchangeList().map((e,i)=>
    `<div class="glrow ce" data-bi="${i}">`
    +`<span class="gn">${esc(e.short||e.name)}<span class="gk">${esc(e.kind||'')}</span></span>`
    +`<span class="gd">${esc(fmtSpan(e.a0,e.a1))}</span></div>`).join('');
  box.querySelectorAll('[data-bi]').forEach(el=>{
    el.onclick=()=>{ const e=interchangeList()[+el.dataset.bi]; if(e) showInterchange(e); };
  });
}
function interchangeAt(age){
  return interchangeList().find(e=>
    age>=Math.min(e.a0,e.a1)-2.5 && age<=Math.max(e.a0,e.a1)+2.5)||null;
}
function markInterchangeList(){
  const cur=interchangeAt(state.age), es=interchangeList();
  document.querySelectorAll('#biList [data-bi]').forEach(el=>
    el.classList.toggle('cur', !!cur && es[+el.dataset.bi]===cur));
}
function showInterchange(e){
  const rows=[['Span',fmtSpan(e.a0,e.a1)],['Kind',e.kind||'Biotic interchange']];
  if(e.peak!=null){
    const A=ages(); let bi=0,bd=1e9;
    A.forEach((v,i)=>{const d=Math.abs(v-e.peak);if(d<bd){bd=d;bi=i;}});
    rows.push(['Connection formed',`${fmtAge(e.peak)} — narrower than this map can draw`]);
  }
  let extra='';
  if(e.driver)extra+=`<div class="ihead">What opened the route</div><p class="desc">${esc(e.driver)}</p>`;
  if(e.result)extra+=`<div class="ihead">Who crossed, and who won</div><p class="desc">${esc(e.result)}</p>`;
  if(e.contested)extra+=`<div class="ihead">Still argued over</div><p class="desc">${esc(e.contested)}</p>`;
  openInfo({name:e.name, tag:(e.kind||'Biotic interchange')+' · '+fmtSpan(e.a0,e.a1),
            rows, desc:e.summary, extra, wide:true,
            art:artFor('interchange',undefined,e.name)});
  if(e.jump_age!=null)jumpTo(e.jump_age);
  markInterchangeList();
}
function climateEventAt(age){
  /* Widened to +/- half a keyframe. An event 200 kyr long sits BETWEEN two
     keyframes far more often than on one, so an exact containment test would
     make the card essentially unreachable by scrubbing — which is the same
     resolution problem that put these on cards in the first place. */
  return climateEventsList().find(e=>!e.offmap &&
    age>=Math.min(e.a0,e.a1)-2.5 && age<=Math.max(e.a0,e.a1)+2.5)||null;
}
function markClimateEventList(){
  const cur=climateEventAt(state.age), es=climateEventsList();
  document.querySelectorAll('#ceList [data-ce]').forEach(el=>
    el.classList.toggle('cur', !!cur && es[+el.dataset.ce]===cur));
}
function showClimateEvent(e){
  const rows=[['Span', e.offmap?'2.46–2.06 Ga — before this map begins'
                               :fmtSpan(e.a0,e.a1)],
              ['Kind', e.kind||'Climate event']];
  if(!e.offmap){
    const A=ages(); let bi=0,bd=1e9;
    A.forEach((v,i)=>{const d=Math.abs(v-(e.peak!=null?e.peak:e.a0));if(d<bd){bd=d;bi=i;}});
    const m=DATA.timeline[bi];
    if(m){
      rows.push(['Nearest keyframe',`${fmtAge(A[bi])} — ${m.gmst.toFixed(1)}°C · ${m.co2} ppm CO₂`]);
      rows.push(['Shorter than',`the 5 Myr between keyframes — this cannot be drawn`]);
    }
  }
  let extra='';
  if(e.cause)extra+=`<div class="ihead">What caused it</div><p class="desc">${esc(e.cause)}</p>`;
  if(e.end)extra+=`<div class="ihead">How it ended</div><p class="desc">${esc(e.end)}</p>`;
  if(e.life)extra+=`<div class="ihead">What it did to life</div><p class="desc">${esc(e.life)}</p>`;
  if(e.contested)extra+=`<div class="ihead">Still argued over</div><p class="desc">${esc(e.contested)}</p>`;
  openInfo({name:e.name, tag:(e.kind||'Climate event')
              +' · '+(e.offmap?'2.46–2.06 Ga':fmtSpan(e.a0,e.a1)),
            rows, desc:e.summary, extra, wide:true,
            art:artFor('climate-event',undefined,e.name)});
  if(!e.offmap&&e.jump_age!=null)jumpTo(e.jump_age);
  markClimateEventList();
}
function showGlaciation(g){
  const rows=[['Span',fmtSpan(g.a0,g.a1)],['Kind',g.kind||'Glaciation']];
  /* The measured ice, not the claim: iceLand/iceSea come from the manifest and
     say how much of this world the app actually draws under ice. */
  const A=ages(); let bi=0,bd=1e9;
  A.forEach((v,i)=>{const d=Math.abs(v-g.peak);if(d<bd){bd=d;bi=i;}});
  const m=DATA.timeline[bi];
  if(m){
    rows.push(['Ice at peak',`${((m.iceLand||0)*100).toFixed(0)}% of land`]);
    rows.push(['Sea ice',`${((m.iceSea||0)*100).toFixed(0)}% of ocean`]);
    rows.push(['World then',`${m.gmst.toFixed(1)}°C · ${m.co2} ppm CO₂`]);
  }
  let extra='';
  if(g.cause)extra+=`<div class="ihead">What caused it</div><p class="desc">${esc(g.cause)}</p>`;
  if(g.end)extra+=`<div class="ihead">How it ended</div><p class="desc">${esc(g.end)}</p>`;
  if(g.life)extra+=`<div class="ihead">What it did to life</div><p class="desc">${esc(g.life)}</p>`;
  if(g.contested)extra+=`<div class="ihead">Still argued over</div><p class="desc">${esc(g.contested)}</p>`;
  openInfo({name:g.name, tag:(g.kind||'Glaciation')+' · '+fmtSpan(g.a0,g.a1),
            rows, desc:g.summary, extra, wide:true,
            art:artFor('ice',undefined,g.name)});
  jumpTo(g.jump_age);
  markGlaciationList();
}
/* One template, three kinds of context. Rebuilt only when the SET of things
   true at this age changes -- scrubbing inside one interval touches no DOM --
   and each card remembers whether it was left open, so opening the interval
   card once keeps it open as you travel through the Jurassic. */
const ctxOpen={};
let ctxKey=null;
function ctxItems(){
  const age=state.age, out=[];
  const iv=intervalAt(age);
  if(iv)out.push({k:'interval',cls:'ctx-interval',
    eyebrow:(iv.rank==='projected'?'Projected interval':'Geological interval'),
    title:iv.name, sub:fmtSpan(iv.a0,iv.a1)+' · '+iv.era,
    body:iv.summary, open:()=>showInterval(iv)});
  const sc=(DATA.eras.supercontinents||[]).find(x=>{
    const lo=Math.min(x.assembly[0],x.assembly[1],x.peak[0],x.peak[1],x.breakup[0],x.breakup[1]);
    const hi=Math.max(x.assembly[0],x.assembly[1],x.peak[0],x.peak[1],x.breakup[0],x.breakup[1]);
    return age>=lo&&age<=hi;});
  if(sc){
    const inPeak=age>=Math.min(sc.peak[0],sc.peak[1])&&age<=Math.max(sc.peak[0],sc.peak[1]);
    const assembling=age>Math.max(sc.peak[0],sc.peak[1]);
    out.push({k:'super',cls:'ctx-super',
      eyebrow:(sc.disputed?'Disputed supercontinent':'Supercontinent'),
      title:sc.name, sub:(inPeak?'Coherent':assembling?'Assembling':'Breaking up')
        +' · '+fmtSpan(sc.peak[0],sc.peak[1]),
      body:sc.summary, open:()=>showSupercontinent(sc)});
  }
  const g=glaciationAt(age);
  if(g)out.push({k:'glacial',cls:'ctx-glacial',eyebrow:g.kind||'Glaciation',
    title:g.name, sub:fmtSpan(g.a0,g.a1), body:g.summary, open:()=>showGlaciation(g)});
  /* A climate event is shorter than the gap between keyframes, so the card is
     the ONLY way it can appear. Marked as such in the sub-line rather than
     letting a reader assume the globe behind it is showing the event. */
  const ce=climateEventAt(age);
  if(ce)out.push({k:'climate',cls:'ctx-climate',eyebrow:ce.kind||'Climate event',
    title:ce.short||ce.name, sub:fmtSpan(ce.a0,ce.a1)+' · shorter than a keyframe',
    body:ce.summary, open:()=>showClimateEvent(ce)});
  return out;
}
function updateContextCards(){
  const box=$('#ctxStack'); if(!box||!DATA.eras)return;
  const items=ctxItems();
  const key=items.map(i=>i.k+':'+i.title).join('|');
  if(key===ctxKey){
    // same set: only the sub-line can change (phase of a supercontinent)
    items.forEach((it,n)=>{const el=box.children[n];
      if(el)el.querySelector('.cs').textContent=it.sub;});
    return;
  }
  ctxKey=key;
  box.innerHTML=items.map(it=>
    `<div class="ctxCard ${it.cls}${ctxOpen[it.k]?' open':''}" data-k="${it.k}">`
    +`<div class="ch"><div class="ceb">${esc(it.eyebrow)}</div>`
    +`<div class="ct">${esc(it.title)}</div><div class="cs">${esc(it.sub)}</div>`
    +`<span class="cv">▾</span></div>`
    +`<div class="cb"><p style="margin:0">${esc(it.body||'')}</p>`
    +`<span class="cmore">Full card →</span></div></div>`).join('');
  [...box.children].forEach((el,n)=>{
    const it=items[n];
    el.querySelector('.ch').onclick=()=>{
      ctxOpen[it.k]=!ctxOpen[it.k]; el.classList.toggle('open',ctxOpen[it.k]);
    };
    el.querySelector('.cmore').onclick=e=>{e.stopPropagation(); it.open();};
  });
  positionContext();
}
/* Sit below whatever the extinction card is doing -- it appears and vanishes on
   its own schedule, and two fixed elements at the same top would overlap. */
function positionContext(){
  const box=$('#ctxStack'); if(!box)return;
  const eb=$('#extinctBox');
  const vis=eb&&!eb.classList.contains('hidden');
  const r=vis?eb.getBoundingClientRect():null;
  box.style.top=(vis&&r.bottom>80?r.bottom+10:($('#controls').getBoundingClientRect().bottom+12))+'px';
}
function markExtinctList(cur){
  document.querySelectorAll('#exList [data-ev]').forEach(el=>
    el.classList.toggle('cur', !!cur && el.dataset.ev===cur.ev.name && (+el.dataset.ph)===cur.i));
}

/* ================= render loop ================= */
/* A JUMP MUST NOT PAY EVERY UPLOAD IN ONE FRAME (perf audit P1/P3, WP-09 F4).
   Binding a cold pair used to create ~15 GPU textures inside one bindTextures
   call -- a 150-260 ms freeze. The per-kind gates below already define what a
   partially-arrived frame looks like (they were built for the network case,
   where kinds trickle in), so a cold jump now uses the SAME contract: the two
   kinds that carry the frame's identity -- elevation and rainfall -- upload
   immediately, and the refinement kinds take the queue, one per frame, front
   of the line. Visually identical to loading the age over the network, minus
   the freeze. */
let _texMakeBudget=2;
function bindTex(kind,i,essential){
  const key=kind+i;
  const e=TEXCACHE.get(key);
  if(e&&e.t){_cacheTouch(e);_boundAt.set(key,_frameNo);return e.t;}
  if(_BITMAPS&&(!e||!e.bm)){
    // Not decoded yet: start the off-thread decode now (idempotent) and keep
    // the previous binding this frame -- the same contract a slow network has
    // always had. Essential kinds kick immediately; the rest wait their turn
    // in the queue unless there is budget to spare. The pending caps matter
    // during a fast scrub: every age the slider sweeps past kicks its own
    // essentials, and an unbounded backlog is what delays the age the user
    // actually stopped on.
    if((essential&&_bmPending.size<(_scrubbing?3:10))||(!essential&&_texMakeBudget>0&&_bmPending.size<5))ensureBitmap(kind,i);
    if(!essential&&!_upQ.some(q=>q.k===kind&&q.i===i))_upQ.unshift({k:kind,i});
    return null;
  }
  if(!essential&&_texMakeBudget<=0){
    if(!_upQ.some(q=>q.k===kind&&q.i===i))_upQ.unshift({k:kind,i});
    return null;
  }
  _texMakeBudget--;
  const t=getTex(kind,i);
  if(t)_boundAt.set(key,_frameNo);
  return t;
}
function bindTextures(){
  const f=curFrame();
  /* Ask for whatever this age needs, every frame. loadField is a no-op once a
     file has settled or is already in flight, so the steady-state cost is a
     dozen Map lookups -- and putting it here rather than on each of the many
     paths that can change state.age means none of them can be forgotten. */
  if(!frameSettled(f.i)||!frameSettled(f.j)){ensureFrames(state.age);pumpPrefetch();}
  /* SCRUB STEPPING (2026-07-31). While the slider is being dragged the exact
     pair usually is not decoded yet, and the old behaviour -- keep the last
     bound pair -- froze the crust while the climate tint kept sweeping: the
     user saw colours travel through time over a fossilised world. Instead the
     globe now shows the NEAREST RESIDENT elevation keyframe to wherever the
     slider is, stepping through intermediate states as elevation-only decodes
     land behind the drag (they cannot be cancelled, so they are capped and
     lag-tolerant). One coherent WORLD per step: every per-frame field that is
     resident for that keyframe binds with it, and the interval machinery
     (mixf blending, uWarp) stands down -- a stepped world is a still, not an
     interval. On release the exact pair binds and everything resolves. */
  const bi=_scrubbing?nearestResidentE(f.i):-1;
  const stepping=bi>=0&&_scrubbing;
  if(_scrubbing){
    /* Aim the elevation decodes AHEAD of the drag: a decode takes longer than
       a frame, so one kicked at the slider's position lands behind it. Kicked
       a few keyframes along its direction of travel, it lands on time. */
    const v=f.i-(bindTextures._si===undefined?f.i:bindTextures._si);
    if(v)ensureBitmap('e',Math.max(0,Math.min(DATA.timeline.length-1,f.i+2*Math.sign(v)+3*v)));
  }
  bindTextures._si=f.i;
  const ea=bindTex('e',f.i,true), eb=bindTex('e',f.j,true);
  const ra=bindTex('r',f.i,true), rb=bindTex('r',f.j,true);
  // Outside the Holocene window, the present frame contributes its long-lived
  // lakes only — otherwise the Great Lakes bleed several Myr into the past.
  const P=presentIndex(), swap=youngLakeWeight(state.age)<0.5 && oldLakeTex();
  if(stepping){
    const gT=(k)=>{const e=TEXCACHE.get(k+bi);
      if(!(e&&e.bm))return null;
      const t=getTex(k,bi); if(t)_boundAt.set(k+bi,_frameNo); return t;};
    const es=gT('e');
    if(es){mat.uniforms.elevA.value=es;mat.uniforms.elevB.value=es;_lastBoundE=bi;}
    const rs=gT('r');
    if(rs){mat.uniforms.rainA.value=rs;mat.uniforms.rainB.value=rs;}
    const ws=(swap&&bi===P)?oldLakeTex():gT('w');
    if(ws){mat.uniforms.waterA.value=ws;mat.uniforms.waterB.value=ws;}
    const ds=gT('d');
    if(ds){mat.uniforms.surfA.value=ds;mat.uniforms.surfB.value=ds;}
    const os=gT('o');
    if(os){mat.uniforms.oceanA.value=os;mat.uniforms.oceanB.value=os;}
    mat.uniforms.uWarp.value=0.0;                    // a still, not an interval
    const ps=gT('p'), pr=DATA.platerot&&DATA.platerot.rot[String(DATA.timeline[bi].age)];
    if(ps&&pr){
      mat.uniforms.plateA.value=ps;
      const Q=mat.uniforms.uPlateQ.value;
      for(let k=0;k<Q.length;k++){const q=pr[k]||[0,0,1,0];Q[k].set(q[0],q[1],q[2],q[3]);}
      mat.uniforms.uMat.value=1.0;
    } else mat.uniforms.uMat.value=0.0;
    const S=stackFill(bi,gT);                       // _t _f _q _x: one texture, a still
    bindStacks(mat.uniforms,S,S);
    const ms=gT('m'); if(ms)mat.uniforms.motA.value=ms;
    mat.uniforms.mixf.value=0.0;
    bindClimate(f);
    return f;
  }
  const wa=(swap&&f.i===P)?oldLakeTex():bindTex('w',f.i);
  const wb=(swap&&f.j===P)?oldLakeTex():bindTex('w',f.j);
  if(ea)mat.uniforms.elevA.value=ea;
  if(eb||ea)mat.uniforms.elevB.value=eb||ea;
  if(ea)_lastBoundE=f.i;
  if(ra)mat.uniforms.rainA.value=ra;
  if(rb||ra)mat.uniforms.rainB.value=rb||ra;
  // Lake-depth field, interpolated like elevation so lakes fill and drain smoothly.
  if(wa)mat.uniforms.waterA.value=wa;
  if(wb||wa)mat.uniforms.waterB.value=wb||wa;
  const sa=bindTex('d',f.i), sb=bindTex('d',f.j);
  if(sa)mat.uniforms.surfA.value=sa;
  if(sb||sa)mat.uniforms.surfB.value=sb||sa;
  // Ocean-structure field (crustal age + spreading direction), interpolated
  // like elevation so the abyssal-hill grain drifts and re-orients with the plates.
  const oa=bindTex('o',f.i), ob=bindTex('o',f.j);
  if(oa)mat.uniforms.oceanA.value=oa;
  if(ob||oa)mat.uniforms.oceanB.value=ob||oa;
  /* Displacement, which makes the crust SLIDE between keyframes instead of
     cross-fading. It belongs to the INTERVAL, and is stored on the younger of
     the pair, so only f.i is ever bound. uWarp is the honest gate: the future
     keyframes and the oldest one have no _v, and without it a missing texture
     would read as black -- which decodes to a full-scale displacement to the
     south-west rather than to none. Falls back to the old cross-fade, which is
     exactly what those intervals did before. */
  /* ESSENTIAL, like elevation (coherence fix, 2026-07-31): without _v the
     interval renders as the plain cross-fade H1 replaced, and without _p the
     terrain texture stops riding its plate -- measured 33% / 45% of playback
     frames in that degraded state at 8 fps with these trickled. A late lake
     or surface field is an invisible 0.1-0.4 s; a late motion model is the
     whole look of time passing. */
  const va=(f.i!==f.j)?bindTex('v',f.i,true):null;
  if(va)mat.uniforms.dispA.value=va;
  mat.uniforms.uWarp.value=va?1.0:0.0;
  /* Material coordinates. The slot raster and the rotation table must come
     from the SAME keyframe or the texture rides crust it does not belong to,
     so both are taken from f.i and uMat is off unless both are present. */
  const pa=bindTex('p',f.i,true), prot=DATA.platerot&&DATA.platerot.rot[String(DATA.timeline[f.i].age)];
  if(pa&&prot){
    mat.uniforms.plateA.value=pa;
    const Q=mat.uniforms.uPlateQ.value;
    for(let k=0;k<Q.length;k++){const q=prot[k]||[0,0,1,0];Q[k].set(q[0],q[1],q[2],q[3]);}
    mat.uniforms.uMat.value=1.0;
  } else mat.uniforms.uMat.value=0.0;
  /* Tectonic state: shortening + fold axis, from the same keyframe as the warp.

     FALL BACK TO THE OTHER KEYFRAME OF THE PAIR. Binding from f.i alone means
     one missing file switches the whole fold fabric off, and that is exactly
     what happened at the PRESENT DAY: age 0 interpolates frames 49 and 50, and
     frame 49 is fut_0005, one of only two keyframes in the series that had no
     _t at all. So uTect was 0, gFold was the zero vector, and every attempt to
     comb a mountain range in iterations 51-53 was steering by a direction that
     did not exist. The files are baked now; this makes the binding robust so a
     single gap can never silence the feature again. The fabric changes slowly,
     so the neighbour is a good answer rather than a fudge. */
  /* The tectonic state, the foreland (the moat in front of a belt), and the
     fold and drainage coordinates (interpolated between the pair like the
     terrain itself) ride the small-field stack: one texture per keyframe of
     the pair, and bindStacks() keeps that fallback per band. */
  const SA=stackFill(f.i,k=>bindTex(k,f.i)), SB=(f.j!==f.i)?stackFill(f.j,k=>bindTex(k,f.j)):SA;
  bindStacks(mat.uniforms,SA,SB);
  // Linear in t: the shader interpolates the height field, so this drives the
  // coastline's position. Easing it would make continents accelerate and stall
  // at every keyframe instead of drifting at a steady rate.
  mat.uniforms.mixf.value=f.t;
  bindClimate(f);
  return f;
}
/* The climate/appearance uniforms interpolate straight from the timeline
   table, so they track the slider continuously whatever textures are bound --
   which is why a scrub keeps its sweeping seasons even while the crust steps. */
function bindClimate(f,ageOv,dryOv){
  /* ageOv/dryOv exist for the sheet bake, which binds one keyframe at its own
     age with the Messinian drawdown held off (a sheet is blended across ten
     million years; a basin drained for two of them must not fade in and out). */
  const age=(ageOv===undefined)?state.age:ageOv;
  /* The Messinian lasted 5.97-5.33 Ma: 640 kyr, an eighth of one keyframe gap.
     Gate it to a two-frame window around 5 Ma rather than let a 5 Myr keyframe
     imply the Mediterranean spent ten million years as a desert. */
  mat.uniforms.uDry.value=(dryOv!==undefined)?dryOv:((age>=4.4&&age<=6.6)?1.0:0.0);
  const A=DATA.timeline[f.i], B=DATA.timeline[f.j], t=f.t;
  const L=(k)=>A[k]+(B[k]-A[k])*t;
  mat.uniforms.uTemp.value=L('temp');
  mat.uniforms.uVeg.value=L('veg');
  /* Grasses: present from the Late Cretaceous, ecologically minor until about
     40 Ma, open grassland through the Oligocene and Miocene, C4 savanna from 8.
     Ramped rather than switched, because that is how it happened. The future
     keeps grass, so negative ages clamp to 1. */
  {const a=Math.max(age,0);
   mat.uniforms.uGrass.value = a<=8 ? 1.0
     : a<=40 ? 1.0-0.45*(a-8)/32.0
     : a<=70 ? 0.55*(1.0-(a-40)/30.0)
     : 0.0;}
  mat.uniforms.uIceT.value=L('iceT');
  mat.uniforms.uSeaT.value=L('seaT');
  // Snowball intensity (render.snowball_at): 1 when the era's ice line reaches
  // the equator. Gates the Cryogenian refugia — nothing else in the record does.
  mat.uniforms.uSnowball.value=(A.snowball||0)+(((B.snowball||0)-(A.snowball||0))*t);
  mat.uniforms.uSchem.value=state.shade==='schem'?0.92:0;
  /* Sea colour slides from an ancient green ocean toward the modern blue. The
     research places the shift with the mid-Mesozoic rise of coccolithophores
     and the deep-sea carbonate sink, so blue is fully established by ~150 Ma
     and the sea greens going back into the Palaeozoic and Precambrian. Future
     and recent ages are the modern blue. */
  const ag=age;
  mat.uniforms.uSeaTint.value = ag<=150 ? 1.0 : ag>=680 ? 0.12
     : 1.0 - 0.88*(ag-150.0)/530.0;
  const mtex=bindTex('m',f.i); if(mtex)mat.uniforms.motA.value=mtex;
  mat.uniforms.uBounds.value=0;   // boundaries are drawn as lines, not shaded
  mat.uniforms.uMapProj.value=state.view==='map'?1:0;
}
/* ===================== WORLD SHEETS (WP-10, plan A) =====================
   A sheet is one keyframe's whole shaded world, rendered once by the terrain
   shader into an equirect render target (FRAG with uMapProj 2). The lite
   material draws the globe and the map from two sheets per frame at a few
   texture reads a pixel, so the terrain shader runs once per KEYFRAME instead
   of once per PIXEL PER FRAME. Sheets are baked in strips across several
   frames so a bake never lands as one hitch, the current pair plus the next
   keyframe in the playback direction are kept warm, and a small pool of
   render targets is recycled. ?sheet=N sets the width (2048..8192; default
   4096, 2048 on low-memory devices), ?lite=1|0 forces the path on or off
   (default auto: on once a screen pixel covers most of a sheet texel), and
   ?bakefull=1 renders a whole sheet in one frame (verification only). */
const _sq=new URLSearchParams(location.search);
const SHEET_W=(()=>{const v=+_sq.get('sheet');if(v>=256&&v<=8192)return v;
  return ((navigator.deviceMemory||8)<8)?2048:4096;})();
const SHEET_H=SHEET_W/2;
const SHEET_STRIPS=16, SHEET_STRIPS_PER_FRAME=_sq.has('bakefull')?16:4;
const SHEET_KEEP=4;                 // render targets held: the pair, the next, one spare
const SHEET_TEXEL_KM=40030/SHEET_W; // at the equator
let liteMode=_sq.get('lite')==='1'?'on':_sq.get('lite')==='0'?'off':'auto';
const SHEETS=new Map();             // keyframe index -> {rt|null, tex, w, ready, u}
const _rtPool=[]; let _bakeJob=null, _sheetClock=0, _liteOn=false, _liteFrames=0;
/* SHIPPED SHEETS. build/bake_sheets.py renders every keyframe's sheet on a
   real GPU and encodes it into web/sheets/ with a manifest; when the manifest
   is present the app decodes those instead of baking, which is what makes
   playback free at any speed and what the ambient build runs on. A shipped
   sheet may be any width; the LOD rule reads the width of the sheets in use.
   ?noshipped=1 ignores the manifest (the bake script itself needs that). */
const SHEET_V='20260903';
let SHEET_MANIFEST=null;
const _shippedPending=new Set(), _shippedMissing=new Set();
function _shippedSheet(i){
  if(_sq.has('noshipped')||!SHEET_MANIFEST||!SHEET_MANIFEST.files||_shippedMissing.has(i))return false;
  const file=SHEET_MANIFEST.files[String(DATA.timeline[i].age)];
  if(!file){_shippedMissing.add(i);return false;}
  if(_shippedPending.has(i))return true;
  _shippedPending.add(i);
  fetch((SHEET_BASE||'sheets/')+file+'?v='+SHEET_V).then(r=>{if(!r.ok)throw 0;return r.blob();})
    .then(b=>createImageBitmap(b,{imageOrientation:'flipY',premultiplyAlpha:'none',colorSpaceConversion:'none'}))
    .then(bm=>{
      const t=new THREE.Texture(bm); t.flipY=false; t.colorSpace=THREE.NoColorSpace;
      t.minFilter=THREE.LinearMipmapLinearFilter; t.magFilter=THREE.LinearFilter; t.generateMipmaps=true;
      t.wrapS=THREE.RepeatWrapping; t.wrapT=THREE.ClampToEdgeWrapping;
      t.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy()); t.needsUpdate=true;
      _sheetDrop(i); SHEETS.set(i,{rt:null,tex:t,w:bm.width,ready:true,u:++_sheetClock});
      _shippedPending.delete(i);
    })
    .catch(()=>{_shippedPending.delete(i);_shippedMissing.add(i);});
  return true;
}
function _sheetDrop(i){
  const s=SHEETS.get(i); if(!s)return;
  if(s.rt)_rtPool.push(s.rt); else if(s.tex){if(s.tex.image&&s.tex.image.close)s.tex.image.close();s.tex.dispose();}
  SHEETS.delete(i);
}
/* A slot for keyframe i's sheet, evicting the least recently used one that is
   not in `want` when the pool is full. Returns null if nothing can be freed. */
function _sheetSlot(i,want){
  let s=SHEETS.get(i); if(s)return s;
  if(SHEETS.size>=SHEET_KEEP){
    let vi=-1,vu=1e18;
    for(const [k,v] of SHEETS)if(!want.includes(k)&&v.u<vu){vu=v.u;vi=k;}
    if(vi<0)return null;
    _sheetDrop(vi);
  }
  const rt=_sheetRT();
  s={rt:rt,tex:rt.texture,w:SHEET_W,ready:false,u:++_sheetClock}; SHEETS.set(i,s); return s;
}
function _sheetRT(){
  if(_rtPool.length)return _rtPool.pop();
  const rt=new THREE.WebGLRenderTarget(SHEET_W,SHEET_H,{depthBuffer:false,stencilBuffer:false});
  const t=rt.texture;
  t.minFilter=THREE.LinearMipmapLinearFilter; t.magFilter=THREE.LinearFilter;
  t.generateMipmaps=false; t.wrapS=THREE.RepeatWrapping; t.wrapT=THREE.ClampToEdgeWrapping;
  t.colorSpace=THREE.NoColorSpace;
  t.anisotropy=Math.min(4,renderer.capabilities.getMaxAnisotropy());
  return rt;
}
function sheetReady(i){const s=SHEETS.get(i);return !!(s&&s.ready);}
/* Every field kind of keyframe i decoded (or known absent) -- the bake binds
   the keyframe as a still and must not wait on a texture mid-strip. */
function _sheetKindsResident(i){
  let ok=true;
  for(const [k] of FIELD_KINDS){
    const key=k+i, e=TEXCACHE.get(key);
    if(!(e&&e.bm)&&!_bmMissing.has(key)){ok=false;ensureBitmap(k,i,true);}
  }
  return ok;
}
/* Bind keyframe i into the terrain material as a still: both taps of every
   pair read the same keyframe, mixf 0, no warp, climate at the keyframe's own
   age. The same contract the scrub-stepping branch of bindTextures uses. */
function bindStill(i){
  const u=mat.uniforms;
  const T=(k)=>{const e=TEXCACHE.get(k+i);if(!(e&&e.bm))return null;
    const t=getTex(k,i);if(t)_boundAt.set(k+i,_frameNo);return t;};
  const es=T('e'); if(es){u.elevA.value=es;u.elevB.value=es;}
  const rs=T('r'); if(rs){u.rainA.value=rs;u.rainB.value=rs;}
  const ws=T('w'); if(ws){u.waterA.value=ws;u.waterB.value=ws;}
  const ds=T('d'); if(ds){u.surfA.value=ds;u.surfB.value=ds;}
  const os=T('o'); if(os){u.oceanA.value=os;u.oceanB.value=os;}
  u.uWarp.value=0.0;
  const ps=T('p'), pr=DATA.platerot&&DATA.platerot.rot[String(DATA.timeline[i].age)];
  if(ps&&pr){u.plateA.value=ps;const Q=u.uPlateQ.value;
    for(let k=0;k<Q.length;k++){const q=pr[k]||[0,0,1,0];Q[k].set(q[0],q[1],q[2],q[3]);}
    u.uMat.value=1.0;} else u.uMat.value=0.0;
  const S=stackFill(i,T); bindStacks(u,S,S);      // _t _f _q _x: one texture, a still
  const ms=T('m'); if(ms)u.motA.value=ms;
  u.mixf.value=0.0;
  bindClimate({i:i,j:i,t:0},DATA.timeline[i].age,0.0);
}
/* Render the next few strips of the current bake job. Binds the job's
   keyframe into the terrain material, draws the map quad into the sheet's
   render target with the scissor on a band of rows, and leaves the material
   for bindTextures() to rebind for the live frame -- which is why this runs
   BEFORE bindTextures in loop(). Mipmaps are generated on the last strip only. */
function _bakeStrips(){
  const j=_bakeJob, rt=j.rt, u=mat.uniforms;
  bindStill(j.i);
  u.uMapProj.value=2.0; u.uTime.value=777.0; u.uSchem.value=0.0; u.uDisp.value=0.0;
  const vis=[globe.visible,atmo.visible,starfield.visible,clouds.visible,mapMesh.visible];
  globe.visible=false;atmo.visible=false;starfield.visible=false;clouds.visible=false;mapMesh.visible=true;
  const prevMat=mapMesh.material; mapMesh.material=mat;
  orthoCam.left=-0.5;orthoCam.right=0.5;orthoCam.top=0.5;orthoCam.bottom=-0.5;orthoCam.updateProjectionMatrix();
  mapMesh.scale.set(1,1,1);mapMesh.position.set(0,0,0);
  const prevRT=renderer.getRenderTarget();
  const n=Math.min(SHEET_STRIPS_PER_FRAME,SHEET_STRIPS-j.row);
  for(let k=0;k<n;k++){
    const y0=Math.floor(j.row*SHEET_H/SHEET_STRIPS), y1=Math.floor((j.row+1)*SHEET_H/SHEET_STRIPS);
    rt.scissorTest=true; rt.scissor.set(0,y0,SHEET_W,y1-y0); rt.viewport.set(0,0,SHEET_W,SHEET_H);
    rt.texture.generateMipmaps=(j.row===SHEET_STRIPS-1);
    renderer.setRenderTarget(rt); renderer.render(scene,orthoCam);
    j.row++;
  }
  renderer.setRenderTarget(prevRT);
  rt.scissorTest=false;
  mapMesh.material=prevMat;
  [globe.visible,atmo.visible,starfield.visible,clouds.visible,mapMesh.visible]=vis;
  u.uMapProj.value=state.view==='map'?1:0;
  if(j.row>=SHEET_STRIPS){const s=SHEETS.get(j.i);s.ready=true;s.u=++_sheetClock;_bakeJob=null;}
}
function _sheetWanted(f){
  const n=DATA.timeline.length, w=[f.i,f.j];
  // playback: the keyframe ahead; paused: both neighbours, so a scrub either way lands warm
  if(state.playing){w.push(state.dir<0?f.i-1:f.j+1);}else{w.push(f.i-1,f.j+1);}
  return [...new Set(w.filter(i=>i>=0&&i<n))];
}
function pumpBakes(f){
  if(liteMode==='off'||!DATA.timeline||!renderer)return;
  if(_bakeJob){_bakeStrips();return;}
  const want=_sheetWanted(f);
  for(const i of want){
    if(sheetReady(i))continue;
    if(_shippedSheet(i))continue;       // a shipped sheet is on its way
    if(!_sheetKindsResident(i))continue;
    const s=_sheetSlot(i,want); if(!s)return;   // everything held is wanted; next frame
    _bakeJob={i:i,rt:s.rt,row:0}; _bakeStrips(); return;
  }
}
/* Kilometres per screen pixel at the view centre, the LOD measure. */
function footprintKm(){
  const H=(renderer.domElement.height||innerHeight)||1;
  if(state.view==='map'){const dw=((mapView&&mapView.dw)||innerWidth)*renderer.getPixelRatio();return 40030/dw;}
  return 2*(state.zoom-1)*Math.tan(19*DEG)*6371/H;
}
/* Draw from sheets this frame? Auto switches on once a screen pixel covers
   about half a sheet texel (a 2x magnification the eye forgives at wide zoom,
   where the live path is spending its detail on aliasing anyway) and back off
   with hysteresis, so the threshold never flaps. A scrub keeps the live path:
   its stepping binds one keyframe as a still and the sheets would not match. */
function useLite(f){
  if(liteMode==='off'||_scrubbing)return false;
  // The quality button's "Full" pins the live terrain shader at every zoom;
  // Auto, Balanced and Perf take the sheets whenever the footprint allows.
  if(liteMode==='auto'&&state.quality==='full')return false;
  if(!(sheetReady(f.i)&&sheetReady(f.j)))return false;
  if(liteMode==='on')return true;
  const texel=40030/Math.min(SHEETS.get(f.i).w,SHEETS.get(f.j).w);
  const r=footprintKm()/texel;
  _liteOn = _liteOn ? r>0.35 : r>0.45;
  return _liteOn;
}
/* Quality scale: what setPixelRatio actually gets. Auto starts at full and
   is stepped by the governor in loop(); a pinned choice bypasses it. */
let _autoScale='full';
const QSCALE={full:()=>Math.min(devicePixelRatio||1,2),
              balanced:()=>Math.min(devicePixelRatio||1,1.5),
              perf:()=>1};
function renderScale(){
  const q=state.quality==='auto'?_autoScale:state.quality;
  return (QSCALE[q]||QSCALE.full)();
}
function applyQuality(){
  if(!renderer)return;
  renderer.setPixelRatio(renderScale());
  renderer.setSize(innerWidth,innerHeight);
  const b=$('#qualBtn');
  if(b){const q=state.quality;
    b.textContent = q==='auto' ? ('Auto'+(_autoScale==='full'?'':' \u2193'))
      : q==='full' ? 'Full' : q==='balanced' ? 'Balanced' : 'Perf';}
}
function cycleQuality(){
  const order=['auto','full','balanced','perf'];
  state.quality=order[(order.indexOf(state.quality)+1)%order.length];
  if(state.quality==='auto')_autoScale='full';   // re-measure from the top
  try{localStorage.setItem('te_quality',state.quality);}catch(e){}
  applyQuality();
}
/* The governor: a real-interval EMA (pre-clamp, so a 300 ms frame reads as
   300), stepped with hysteresis so it never flaps. Only ever active in
   'auto'; a pinned quality is exactly what it says. */
let _fEMA=16,_fBad=0,_fGood=0,_fSince=0;
function qualityGovernor(rawMs){
  // Time-based warm-up, NOT frame-based: at 3 fps a 180-frame warm-up is a
  // full minute of slideshow before the governor is even allowed to help.
  if(!_fSince)_fSince=performance.now();
  if(performance.now()-_fSince<8000)return;
  _fEMA=_fEMA*0.95+rawMs*0.05;
  if(state.quality!=='auto')return;
  if(_fEMA>95){_fGood=0;_fBad++;}
  else if(_fEMA<28){_fBad=0;_fGood++;}
  else{_fBad=0;_fGood=0;}
  if(_fBad>25){
    _fBad=0;
    if(_autoScale==='full'){_autoScale='balanced';applyQuality();_fEMA=60;}
    else if(_autoScale==='balanced'){_autoScale='perf';applyQuality();_fEMA=60;}
  }
  if(_fGood>420){
    _fGood=0;
    if(_autoScale==='perf'){_autoScale='balanced';applyQuality();_fEMA=45;}
    else if(_autoScale==='balanced'){_autoScale='full';applyQuality();_fEMA=45;}
  }
}
/* ?perf=1 -- a tiny live meter (perf audit P9). Frame interval measured from
   the loop's own timestamps, so a stall shows as itself rather than being
   clamped away like dt is; upload-queue depth and texture-cache occupancy are
   the two numbers that explain almost every hitch this audit found. */
const PERFHUD=new URLSearchParams(location.search).has('perf');
let _phPrev=0,_phN=0,_phSum=0,_phMax=0,_phEl=null,_phLast='';
function perfHud(now){
  if(!PERFHUD)return;
  if(_phPrev){const iv=now-_phPrev;_phN++;_phSum+=iv;if(iv>_phMax)_phMax=iv;}
  _phPrev=now;
  if(_phN<30)return;
  if(!_phEl){_phEl=document.createElement('div');_phEl.id='perfhud';
    _phEl.style.cssText='position:fixed;left:8px;bottom:8px;z-index:99;font:10px/1.5 ui-monospace,monospace;color:#8fd18f;background:rgba(10,14,18,.72);padding:5px 8px;border-radius:6px;pointer-events:none;white-space:pre';
    document.body.appendChild(_phEl);}
  const ms=_phSum/_phN;
  const txt='frame '+ms.toFixed(1)+' ms ('+(1000/ms).toFixed(0)+' fps)  worst '+_phMax.toFixed(0)+' ms'+
    String.fromCharCode(10)+'uploads q '+_upQ.length+'   tex '+TEXCACHE.size+' / '+Math.round(_texBytes/1048576)+' MB'+
    String.fromCharCode(10)+'scale '+renderScale().toFixed(2)+' ('+(state.quality==='auto'?'auto:'+_autoScale:state.quality)+')'+
    '   warp '+(mat.uniforms.uWarp.value>0.5?'on':'OFF')+'  mat '+(mat.uniforms.uMat.value>0.5?'on':'OFF')+
    String.fromCharCode(10)+'path '+(globe.material===liteMat?'SHEETS':'terrain')+'  sheets '+[...SHEETS].filter(([i,s])=>s.ready).map(([i])=>i).join(',')+
    (_bakeJob?('  baking '+_bakeJob.i+' '+_bakeJob.row+'/'+SHEET_STRIPS):'')+'  '+footprintKm().toFixed(1)+' km/px';
  if(txt!==_phLast){_phEl.textContent=txt;_phLast=txt;}
  _phN=0;_phSum=0;_phMax=0;
}
let last=performance.now();
const _camC=new THREE.Vector3(),_camUp=new THREE.Vector3(),_camN=new THREE.Vector3(),
      _camE=new THREE.Vector3(),_camH=new THREE.Vector3();
function loop(now,force){
  const rawMs=now-last;
  /* TWO CLOCKS (WP-10, A5.1). dt is the per-frame step the camera and the
     drag use, clamped at 50 ms so a stall never throws the view. Time itself
     must not be clamped that way: at 3 fps the "18 Myr/s" slider was advancing
     2.7 Myr/s, unevenly, because a 333 ms frame counted as 50. dtT is real
     elapsed time, capped at half a second so a tab that was hidden resumes
     where it was rather than leaping. */
  const dt=Math.min(.05,rawMs/1000), dtT=Math.min(.5,rawMs/1000);last=now;
  qualityGovernor(rawMs);
  _frameNo++;
  /* IDLE THROTTLE (WP-10, A5.6). requestAnimationFrame used to redraw the
     whole planet sixty times a second while nothing on it changed -- a paused
     app on a laptop is most of what this app is, and it was drawing the same
     frame at full cost. When nothing is moving and no texture is on its way,
     redraw five times a second; the picture is a still, and the sea sheen is
     the only thing that notices. Any input, playback, drag, rotation, scrub,
     resize, or a decode landing puts the loop straight back to full rate, and
     APP.step() always renders (the verification harness depends on it). */
  const idleSig=[state.age,state.rot,state.tilt,state.zoom,state.gtilt,state.head,
                 state.view,state.shade,state.mapLon,state.quality,_autoScale,
                 innerWidth,innerHeight,TEXCACHE.size,_texBytes,_upQ.length,_bmPending.size,
                 state.layers.boundaries,state.layers.vectors,state.layers.hotspots,
                 state.layers.labels,state.selPlate].join('|');
  const moving=state.playing||dragging||state.ambient||_scrubbing||_bakeJob!==null||
               (state.layers.rotate&&state.spin>0)||_upQ.length>0||_bmPending.size>0;
  if(idleSig!==loop._sig){loop._sig=idleSig;loop._sigAt=now;}
  const idle=!force&&!moving&&(now-loop._sigAt)>1000;
  if(idle&&(now-(loop._drawn||0))<200){requestAnimationFrame(loop);return;}
  loop._drawn=now;
  // A scrub moves more than a keyframe per frame; the speculative queue is
  // then aimed at ages already behind the slider. Drop it, it re-fills.
  if(loop._la===undefined)loop._la=state.age;
  const _ad=Math.abs(state.age-loop._la);
  if(_ad>6)_upQ.length=0;
  _scrubN=_ad>6?_scrubN+1:0;
  _scrubbing=_scrubN>=2;
  loop._la=state.age;
  _texMakeBudget=2;   // cold-texture creations this frame; jumps defer the rest
  // Sheet bakes render through the terrain material and leave it bound to a
  // still; bindTextures() below rebinds the live pair, so bakes go first.
  if(DATA.timeline)pumpBakes(curFrame());
  if(state.playing){
    state.age+=state.dir*state.speed*dtT;
    if(state.age>1000){state.age=state.ambient?-250:1000;if(!state.ambient)state.playing=false,syncPlay();}
    if(state.age<-250){state.age=state.ambient?1000:-250;if(!state.ambient)state.playing=false,syncPlay();}
    syncSlider();
  }
  // state.spin scales the manual auto-rotate only. Ambient keeps its own fixed
  // pace on purpose: it is a display mode with a composed rhythm, and having it
  // inherit whatever the slider was left on would make the same mode look
  // different every time it is entered.
  if(_rivWant>=0&&fieldImage('d',_rivWant))buildRivers();
  if((state.layers.rotate&&!dragging)||state.ambient){
    state.rot+=dtT*(state.ambient?0.12:0.05*state.spin);}
  updateExtinction();   // show/update the mass-extinction card as time scrubs past an event
  updateContextCards(); // and the interval / supercontinent / glaciation cards
  // Drives only the sea-surface sheen; nothing about world state depends on it,
  // so scrubbing time and this clock stay independent.
  mat.uniforms.uTime.value=now*0.001;
  const f=bindTextures();
  queueUploads(f);   // warm the next keyframe's textures, one upload a frame
  /* THE PATH DECISION (WP-10, A4). Sheets for the bound pair and a footprint
     wide enough -> the lite material; otherwise the terrain shader as before. */
  const lite=useLite(f);
  const wantMat=lite?liteMat:mat;
  if(globe.material!==wantMat){globe.material=wantMat;mapMesh.material=wantMat;}
  if(lite){
    const sa=SHEETS.get(f.i), sb=SHEETS.get(f.j);
    liteMat.uniforms.sheetA.value=sa.tex; liteMat.uniforms.sheetB.value=sb.tex;
    sa.u=++_sheetClock; sb.u=++_sheetClock; _liteFrames++;
  }
  // overlays visibility & fade
  const fade=presentFade();
  // Hotspots and motion vectors are era-specific, so rebuild them whenever the
  // keyframe changes rather than only once at load.
  if(f.i!==lastOverlayFrame||state.layers.vectors!==lastVecOn||state.layers.hotspots!==lastHotOn
     ||state.layers.boundaries!==lastBndOn){
    lastOverlayFrame=f.i; lastVecOn=state.layers.vectors; lastHotOn=state.layers.hotspots;
    lastBndOn=state.layers.boundaries;
    if(state.layers.hotspots)buildHotspots();
    if(state.layers.vectors)buildVectors();
    if(state.layers.boundaries)buildDerivedBounds();
  }
  const g=state.view==='globe';
  // Only the surveyed present-day boundary set fades out; its derived
  // counterpart in the shader covers the rest of the timeline.
  overlay.boundaries.visible=state.layers.boundaries&&fade>0.02&&g;
  const dfade=Math.min(1,Math.max(0,1-fade*1.25));
  overlay.derived.visible=state.layers.boundaries&&dfade>0.02&&g;
  setOpacity(overlay.derived,dfade);
  overlay.vectors.visible=state.layers.vectors&&g;
  overlay.hotspots.visible=state.layers.hotspots&&g;
  setOpacity(overlay.boundaries,fade);setOpacity(overlay.vectors,0.9);setOpacity(overlay.hotspots,1);
  const isGlobe=state.view==='globe';
  globe.visible=isGlobe; atmo.visible=isGlobe; starfield.visible=isGlobe;
  // clouds only on the globe, and only in the photoreal (satellite) shading
  clouds.visible=isGlobe && state.shade!=='schem';
  mapMesh.visible=!isGlobe;
  if(isGlobe){
    globe.rotation.y=state.rot;overlay.boundaries.rotation.y=0;
    /* Back the camera off so the globe always fits. Two separate squeezes:
       a NARROW viewport (the original case, aspect below 1.15), and a SHORT
       one. The second was missing, and a phone in landscape is the short case
       -- 780x360, where the vertical field at the default zoom is 2.10 against
       a globe 2.00 across, so it filled the frame edge to edge and then ran
       under the control bar. The bar owns about a quarter of the height there,
       so give the globe the rest. */
    const short=innerHeight<560?1.34:1.0;
    const d=state.zoom*Math.max(1,1.15/cam.aspect)*short;
    /* ORBIT ABOUT A POINT ON THE SURFACE, not about the centre of the Earth.
       The old line put the camera on the YZ plane looking at the origin, which
       can express "where on the globe am I above" and nothing else -- there is
       no way to lean over and look at the horizon, which is what tilt means.

       The globe has already been rotated by state.rot, so the point under the
       camera sits on the +Z meridian at latitude state.tilt. Build the local
       frame there and orbit within it:

         up    = the surface normal at C
         north = the tangent pointing at the pole
         east  = north x up
         horiz = the compass direction we are looking TOWARD (heading)

       The camera leans off `up` by gtilt toward the OPPOSITE of horiz -- you
       stand south of a thing to look north at it -- and screenUp is built
       analytically as the perpendicular of the view direction in that same
       plane. That last part matters: the obvious `cam.up = up` degenerates at
       gtilt 0, where up is parallel to the view direction and lookAt has no
       basis to work from. Deriving screenUp instead means tilt 0 is an ordinary
       point on the range rather than a special case that has to be clamped. */
    /* TERRAIN EXAGGERATION, and why it is not a constant.

       Earth's relief is 0.14% of its radius: Everest against 6,371 km is a
       rounding error, and at 1x on a globe that fills the screen it is under a
       pixel. Every 3D globe therefore exaggerates. But exaggeration that is
       always on would deform the one framing this whole model has been verified
       at -- the untilted, zoomed-out globe -- so it ramps from ZERO there and
       only arrives when the user has both come close and leaned over, which is
       the only time relief is visible anyway.

       ZOOM_NEAR/FAR: state.zoom is camera distance, so SMALLER is closer. */
    const ZF=3.05, ZN=1.05;
    const near=Math.min(1,Math.max(0,(ZF-state.zoom)/(ZF-ZN)));
    const lean=Math.min(1,state.gtilt/45);
    const exag=15.0*near*(0.40+0.60*lean);
    mat.uniforms.uDisp.value=exag/6371000.0;
    /* The shells have to clear the mountains. Clouds sat at 1.014 and the
       atmosphere at 1.03; a 15x Everest reaches 1.019, so peaks would have
       erupted through the cloud deck and into the haze. Rather than hard-code
       new radii -- which would thicken the atmosphere on the untilted globe
       where none of this applies -- both shells ride on top of whatever the
       current exaggeration actually needs. */
    const lift=1.0+8000.0*exag/6371000.0;
    clouds.scale.setScalar(lift); atmo.scale.setScalar(lift);
    // Dim and tighten the halo as the camera drops toward the surface, or the
    // tangential path through it washes the whole frame out. See the note on
    // the material itself.
    atmo.material.uniforms.uAtm.value=1.0-0.80*near;
    atmo.material.uniforms.uRim.value=2.2+5.0*near;
    /* Clouds RETIRE as the camera drops, rather than merely thinning. A cloud
       shell is a flat texture on a sphere: looked down on from far away it
       reads as weather, but looked along from low orbit the eye travels through
       its whole tangential thickness and it becomes an opaque white wall lying
       across the terrain -- which is precisely what tilt is for looking at.
       Real clouds would part and show ground between them; this one cannot, so
       the honest move is to take it away once the geometry stops supporting the
       illusion. Gone by the time the camera is 60% of the way in. */
    if(clouds.material.uniforms.uCloud){
      const cf=Math.max(0.0,1.0-near/0.6);
      clouds.material.uniforms.uCloud.value=cf;
      clouds.visible=clouds.visible&&cf>0.01;
    }
    const t=state.gtilt*Math.PI/180, hd=state.head*Math.PI/180;
    const cp=Math.cos(state.tilt), sp=Math.sin(state.tilt);
    // scratch vectors, allocated once -- this block runs every frame
    const C  =_camC.set(0,sp,cp);                      // surface point, r=1
    const up =_camUp.copy(C);
    const north=_camN.set(0,cp,-sp);
    const east=_camE.crossVectors(north,up);
    const horiz=_camH.copy(north).multiplyScalar(Math.cos(hd))
                     .addScaledVector(east,Math.sin(hd));
    // d is measured from the Earth's centre at tilt 0, so the orbit radius is
    // d-1; without that subtraction every view would jump backwards by one
    // Earth radius the moment this code replaced the old two-liner.
    const orb=Math.max(0.05,d-1.0);
    cam.position.copy(C)
       .addScaledVector(up,   orb*Math.cos(t))
       .addScaledVector(horiz,-orb*Math.sin(t));
    cam.up.copy(up).multiplyScalar(Math.sin(t)).addScaledVector(horiz,Math.cos(t));
    cam.lookAt(C);
    globe.rotation.x=0;atmo.rotation.copy(globe.rotation);
    renderer.render(scene,cam);
  }else{
    layoutMap();
    renderer.render(scene,orthoCam);
    drawMapOverlays();
  }
  layoutLabels();
  perfHud(now);
  requestAnimationFrame(loop);
}
function setOpacity(grp,o){grp.traverse(c=>{if(c.material&&c.material.opacity!==undefined){c.material.opacity=(c.userData.baseOp||0.88)*o;}});}

/* ================= UI wiring ================= */
function syncSlider(){$('#slider').value=Math.round(1000-state.age);}
function sliderToAge(v){return 1000-(+v);}
$('#slider').addEventListener('input',e=>{state.age=sliderToAge(e.target.value);updateReadout();});
function syncPlay(){const p=state.playing;$('#playIcon').innerHTML=p?'<path d="M6 5h4v14H6zM14 5h4v14h-4z"/>':'<path d="M8 5v14l11-7z"/>';}
$('#playBtn').onclick=()=>{state.playing=!state.playing;syncPlay();};
/* The arrow points the way the playhead travels along the timeline, which runs
   1000 Ma on the left to +250 Myr on the right. dir<0 counts the age down, so
   that is rightward — the unflipped icon. It used to be the other way round,
   which meant the arrow contradicted the scrubber underneath it. */
function syncDir(){$('#dirIcon').style.transform=state.dir>0?'scaleX(-1)':'none';}
$('#dir').onclick=()=>{state.dir*=-1;syncDir();};
/* Step exactly one million years. jumpTo pauses playback, clamps to the ends of
   the timeline and rebuilds every derived layer, which is what a single step
   needs — scrubbing the slider cannot resolve 1 Myr, since it spans 1250 Myr in
   about as many pixels. Age DECREASES going forward in time. */
function stepAge(d){ jumpTo(Math.round(state.age)+d); }
$('#stepBack').onclick=()=>stepAge(1);
$('#stepFwd').onclick=()=>stepAge(-1);
syncDir();
$('#speed').addEventListener('input',e=>{state.speed=+e.target.value;$('#speedVal').textContent=state.speed+' Myr/s';});

/* ---- spin speed, camera tilt/heading, and map longitude ---- */
// The slider is 0..100 but the RATE is exponential, because a linear speed
// control spends most of its travel in a range that all looks the same. This
// maps to 0.1x .. 10x with 1x at the quarter mark, so slow-and-stately and
// spinning-like-a-top are both reachable without hunting.
function spinRate(v){ return v<=0?0:Math.pow(10,(v-25)/37.5); }
$('#spin').addEventListener('input',e=>{
  state.spin=spinRate(+e.target.value);
  $('#spinVal').textContent=state.spin<0.005?'off'
    :(state.spin<1?state.spin.toFixed(2):state.spin.toFixed(1))+'×';});
function camSync(){
  $('#tiltVal').textContent=Math.round(state.gtilt)+'°';
  $('#headVal').textContent=Math.round(state.head)+'°';
  $('#tiltR').value=state.gtilt; $('#headR').value=state.head;
  /* Heading works at EVERY tilt, including zero. The old reasoning -- that
     looking straight down, every heading shows the same disc -- is wrong about
     what the control is for: it rotates the axis you are viewing along, so at
     tilt 0 it spins the globe's north away from screen-up, which is exactly
     what "shift the axis to align" asks for. The camera already does this
     correctly, because screenUp is built from the heading; the slider was
     disabled for a reason that never applied. */
  $('#headR').disabled=false;
  $('#headR').style.opacity=1;
}
$('#tiltR').addEventListener('input',e=>{state.gtilt=+e.target.value;camSync();});
$('#headR').addEventListener('input',e=>{state.head=+e.target.value;camSync();});
$('#resetNorth').addEventListener('click',()=>{
  // Google Earth resets BOTH -- it is "put the camera back the way it was",
  // not "set one number to zero" -- and it animates, because snapping gives no
  // sense of which way you were facing.
  const t0=state.gtilt,h0=state.head,t=performance.now();
  const h1=state.head>180?360:0;          // unwind the short way round
  (function ease(){
    const k=Math.min(1,(performance.now()-t)/420), s=k*k*(3-2*k);
    state.gtilt=t0*(1-s); state.head=(h0+(h1-h0)*s)%360; camSync();
    if(k<1) requestAnimationFrame(ease); else {state.gtilt=0;state.head=0;camSync();}
  })();
});
function mapLonSync(){
  const v=((state.mapLon%360)+540)%360-180;
  $('#mapLonLbl').textContent=(v>0?'+':'')+Math.round(v)+'°';
  mat.uniforms.uMapLon.value=state.mapLon*Math.PI/180;
}
$('#mapW').addEventListener('click',()=>{state.mapLon-=30;mapLonSync();});
$('#mapE').addEventListener('click',()=>{state.mapLon+=30;mapLonSync();});
document.querySelectorAll('#viewSeg button').forEach(b=>b.onclick=()=>{
  document.querySelectorAll('#viewSeg button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
  state.view=b.dataset.v;const map=state.view==='map';
  // Tilt and heading do not exist on a flat projection, and longitude arrows
  // do not exist on a globe you can already drag. Swap the cluster rather than
  // leave either set present but inert.
  $('#camGlobe').hidden=map; $('#camMap').hidden=!map;
  // #gl draws terrain in BOTH views now; #map2d is a transparent overlay
  $('#map2d').style.display=map?'block':'none';
  $('#hint').textContent=map?'Click a plate or landmass for details':'Drag to rotate · scroll to zoom · click a plate for details';
  resize();
});
document.querySelectorAll('.tog').forEach(t=>t.onclick=()=>{
  const k=t.dataset.layer;state.layers[k]=!state.layers[k];t.classList.toggle('on',state.layers[k]);
});
// One drawer at a time: opening either closes the other, so the globe is never
// sandwiched between two panels on a screen that has no room for one.
// Clicks the real toggle rather than setting state itself: two controls for one
// boolean is how they drift apart, and the drawer's switch has to stay right.
/* Delegated, because cards are rebuilt constantly and binding per figure would
   miss every one drawn after load. Escape and a click on the backdrop both
   close it -- an overlay you can only leave by hitting a small x is a trap. */
function closeFigZoom(){ $('#figZoom').hidden=true; $('#figZoomArt').innerHTML=''; }
document.addEventListener('click',e=>{
  // A credit line can carry a link (CC-BY requires attribution and the licence
  // link is part of it). Swallowing that click to open a lightbox would break
  // the one piece of a photo caption that legally has to work.
  if(e.target.closest && e.target.closest('a')) return;
  const f=e.target.closest && e.target.closest('.zoomfig');
  if(f){
    /* svg OR img. The schematics are inline SVG; the model charts and the
       photographs are <img>, and requiring an <svg> is why they silently did
       nothing -- they carried the cursor and the focus ring and then returned. */
    const gfx=f.querySelector('svg,img'); if(!gfx) return;
    const big=gfx.cloneNode(true);
    big.removeAttribute('aria-hidden');
    big.removeAttribute('loading');          // it is on screen NOW
    // meet, not slice: the point of the overlay is to see ALL of it
    if(big.tagName.toLowerCase()==='svg') big.setAttribute('preserveAspectRatio','xMidYMid meet');
    $('#figZoomArt').innerHTML=''; $('#figZoomArt').appendChild(big);
    const cap=f.querySelector('figcaption');
    // innerHTML, not textContent: keeps the attribution link live in the overlay
    $('#figZoomCap').innerHTML=cap?cap.innerHTML:'';
    $('#figZoom').hidden=false; $('#figZoomX').focus(); return; }
  if(e.target.id==='figZoom'||e.target.id==='figZoomX') closeFigZoom();
});
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'&&!$('#figZoom').hidden) closeFigZoom();
  else if((e.key==='Enter'||e.key===' ')&&document.activeElement
          &&document.activeElement.classList.contains('zoomfig')){
    e.preventDefault(); document.activeElement.click(); }
});
$('#rotBtn').onclick=()=>{
  state.layers.rotate=!state.layers.rotate;
  $('#rotBtn').classList.toggle('on',state.layers.rotate);
  $('#rotBtn').setAttribute('aria-pressed',state.layers.rotate?'true':'false');
  $('#spinwrap').hidden=!state.layers.rotate;};
$('#mLabels').onclick=()=>{
  document.querySelector('.tog[data-layer="labels"]').click();
  $('#mLabels').classList.toggle('on',!!state.layers.labels);};
$('#mLeft').onclick=()=>{document.body.classList.remove('m-right');
  document.body.classList.toggle('m-left');};
$('#mRight').onclick=()=>{document.body.classList.remove('m-left');
  document.body.classList.toggle('m-right');};
$('#stage').addEventListener('pointerdown',()=>{
  document.body.classList.remove('m-left','m-right');});
$('#ambientBtn').onclick=()=>enterAmbient(true);
$('#exitAmbient').onclick=()=>enterAmbient(false);
$('#aboutBtn').onclick=()=>{$('#updatelog').classList.remove('show');
  $('#about').classList.toggle('show');};
/* The update log. Content is DATA (build/updatelog.json), not markup, so adding a
   release is one edit to one file and never a change to the app. Built once, on
   first open -- it is a few dozen entries and nobody needs it before they ask. */
let ulBuilt=false;
async function buildUpdateLog(){
  const box=$('#ulBody'); if(!box) return;
  /* Fetched on FIRST OPEN, not at startup. The loader's whole design is that a
     file is fetched when it is wanted (see loadAll), and nobody needs release
     notes before they ask for them -- so this costs nothing until it is used. */
  if(!DATA.updatelog){
    box.innerHTML='<p class="ulsum">Loading…</p>';
    try{ DATA.updatelog=await fetch('updatelog.json?v='+DATA_V).then(r=>r.json()); }
    catch(e){ box.innerHTML='<p class="ulsum">Could not load the update log.</p>'; return; }
  }
  const rel=(DATA.updatelog&&DATA.updatelog.releases)||[];
  if(!rel.length){ box.innerHTML='<p class="ulsum">No entries yet.</p>'; return; }
  box.innerHTML=rel.map(r=>
    `<div class="ulrel"><div class="ulhead">`
    +`<span class="ulver">v${esc(r.version)}</span>`
    +`<span class="uldate">${esc(r.date)}</span>`
    +`<span class="ultitle">${esc(r.title)}</span></div>`
    +(r.summary?`<p class="ulsum">${esc(r.summary)}</p>`:'')
    +(r.sections||[]).map(sec=>
       (sec.name?`<div class="ulsec">${esc(sec.name)}</div>`:'')
       +(sec.items||[]).map(t=>`<div class="ulitem">${esc(t)}</div>`).join('')
     ).join('')
    +`</div>`).join('');
}
$('#logBtn').onclick=()=>{
  if(!ulBuilt){ulBuilt=true;buildUpdateLog();}
  $('#about').classList.remove('show');
  $('#updatelog').classList.toggle('show');
};
$('#ulClose').onclick=()=>$('#updatelog').classList.remove('show');
$('#aboutClose').onclick=()=>$('#about').classList.remove('show');

/* Full one-pager About overlay. Images are lazy: their src is swapped in from
   data-src on first open, so the viewer's initial load never fetches them. */
const aboutPage=$('#aboutPage');
let aboutImgsLoaded=false, silCreditsBuilt=false;
/* Attribution for the traced silhouettes. Generated from the icon manifest that
   actually shipped, so it can never credit an artist whose image was dropped or
   omit one that was added. CC-BY images require this; CC0 ones do not, but a
   contributor who gave the work away still gets named. */
function buildSilhouetteCredits(){
  const el=$('#apSilhouettes'), C=(DATA.life||{}).credits||{};
  if(!el)return;
  const by=new Map();
  Object.values(C).forEach(c=>{
    const who=(c.attribution||'').trim()||'unattributed';
    if(!by.has(who))by.set(who,new Set());
    by.get(who).add(c.licence||'');
  });
  if(!by.size){el.textContent='No traced silhouettes in this build.';return;}
  const names=[...by.keys()].sort((a,b)=>a.localeCompare(b));
  el.innerHTML=`<span style="width:100%">${Object.keys(C).length} silhouettes `+
    `from ${names.length} contributors:</span>`+
    names.map(n=>`<b>${esc(n)}</b> <span>(${esc([...by.get(n)].join(', '))})</span>`)
      .join('<span>·</span>');
}
function openAboutPage(){
  if(!aboutImgsLoaded){
    aboutPage.querySelectorAll('img[data-src]').forEach(im=>{im.src=im.getAttribute('data-src');});
    aboutImgsLoaded=true;
  }
  if(!silCreditsBuilt){buildSilhouetteCredits();silCreditsBuilt=true;}
  $('#about').classList.remove('show');           // close the little info panel if open
  aboutPage.classList.add('show');
  aboutPage.setAttribute('aria-hidden','false');
  aboutPage.querySelector('.ap-inner').scrollTop=0;
}
function closeAboutPage(){
  aboutPage.classList.remove('show');
  aboutPage.setAttribute('aria-hidden','true');
}
$('#aboutPageBtn').onclick=openAboutPage;
$('#aboutPageClose').onclick=closeAboutPage;
aboutPage.addEventListener('click',e=>{ if(e.target===aboutPage) closeAboutPage(); });   // click backdrop
aboutPage.querySelectorAll('[data-ap-close]').forEach(b=>b.onclick=closeAboutPage);
document.addEventListener('keydown',e=>{ if(e.key==='Escape'&&aboutPage.classList.contains('show')) closeAboutPage(); });
/* Full-screen toggle, offered in ambient mode: hides the browser's own tabs and
   menu bars for a clean, immersive view. Prefixed fallbacks cover Safari, and the
   request can be refused (e.g. inside a sandboxed frame), so it is guarded. */
function fsElement(){return document.fullscreenElement||document.webkitFullscreenElement||null;}
function requestFS(){const el=document.documentElement,fn=el.requestFullscreen||el.webkitRequestFullscreen;
  if(fn){try{const p=fn.call(el);if(p&&p.catch)p.catch(()=>{});}catch(e){}}}
function exitFS(){const fn=document.exitFullscreen||document.webkitExitFullscreen;
  if(fn){try{const p=fn.call(document);if(p&&p.catch)p.catch(()=>{});}catch(e){}}}
function syncFS(){const on=!!fsElement(),b=$('#fullscreenBtn');
  b.textContent=on?'Exit full screen':'Full screen';b.classList.toggle('on',on);}
$('#fullscreenBtn').onclick=()=>{fsElement()?exitFS():requestFS();};
document.addEventListener('fullscreenchange',syncFS);
document.addEventListener('webkitfullscreenchange',syncFS);

function enterAmbient(on){state.ambient=on;document.body.classList.toggle('ambient',on);
  /* The lite build (WP-10, plan C) is the real background mode; offer it from
     here whenever the site ships world sheets, carrying the current age. */
  const ll=$('#liteLink'); if(ll){ll.hidden=!(SHEET_MANIFEST&&SHEET_MANIFEST.files);ll.href='ambient.html?age='+Math.round(state.age);}
  // Ambient is the same view with the chrome hidden: it keeps whatever speed
  // and layer toggles are already set rather than imposing its own.
  if(on){state.playing=true;syncPlay();}
  else if(fsElement()){exitFS();}   // leaving ambient drops back to the normal windowed view
}
document.addEventListener('keydown',e=>{if(e.key===' '){e.preventDefault();state.playing=!state.playing;syncPlay();}
  // In full screen the browser's own Escape exits full screen first; a second
  // Escape then leaves ambient. Outside full screen, Escape leaves ambient.
  if(e.key==='Escape'&&state.ambient&&!fsElement())enterAmbient(false);
  // Arrow keys step one million years. Right is rightward on the timeline,
  // which is FORWARD in time and therefore a DECREASE in age. Ignored while a
  // text field or the range input has focus so it cannot fight them.
  if(e.key==='ArrowLeft'||e.key==='ArrowRight'){
    const t=e.target&&e.target.tagName;
    if(t==='INPUT'||t==='TEXTAREA'||t==='SELECT')return;
    e.preventDefault();
    stepAge(e.key==='ArrowRight'?-1:1);
  }});

/* ---- markers ---- */
const MARKERS=[[1000,'Rodinia'],[720,'Cryogenian'],[541,'Cambrian'],[445,'Ordovician'],[300,'Pangaea'],[252,'End-Permian'],[66,'K–Pg'],[0,'Now'],[-250,'+250 Myr']];
function buildMarkers(){
  // numeric scale, so the era names sit against an absolute time axis
  const srow=$('#scalerow');
  const ticks=[1000,900,800,700,600,500,400,300,200,100,0,-100,-250];
  ticks.forEach(age=>{
    const e=document.createElement('div');
    e.className='tick'+(age===0?' zero':'');
    e.style.left=((1000-age)/1250*100)+'%';
    e.textContent = age>0?age : age===0?'0' : '+'+(-age);
    srow.appendChild(e);
  });
  const u=document.createElement('div');
  u.className='tick'; u.style.left='0%'; u.style.transform='translateX(0)';
  u.style.top='-13px'; u.style.color='#4d5663'; u.textContent='Ma';
  srow.appendChild(u);
  const row=$('#markrow');
  MARKERS.forEach(([age,name])=>{
    const e=document.createElement('div');e.className='mark'+(age===0?' now':'');
    e.style.left=((1000-age)/1250*100)+'%';e.textContent=name;
    e.onclick=()=>{state.age=age;syncSlider();updateReadout();};
    row.appendChild(e);
  });
  // gradient hint on track (deep time warm -> present blue -> future warm)
  $('#trackgrad').style.background='linear-gradient(90deg,#5a3a2a,#7a5a3a 18%,#3a5a6a 55%,#2a4a6a 80%,#5a3a3a)';
}

function resize(){
  renderer.setPixelRatio(renderScale());
  renderer.setSize(innerWidth,innerHeight);cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();
  const dpr=Math.min(devicePixelRatio,2);mcv.width=innerWidth*dpr;mcv.height=innerHeight*dpr;mcv.style.width=innerWidth+'px';mcv.style.height=innerHeight+'px';
  positionExtinct();
}
addEventListener('resize',resize);

function buildLegend(){
  $('#legend').innerHTML=`<div class="li"><span class="ln" style="background:#e8534e"></span>Ridge (spreading)</div>
  <div class="li"><span class="ln" style="background:#59b0d6"></span>Trench (converging)</div>
  <div class="li"><span class="ln" style="background:#e0b23a"></span>Transform fault<span style="color:#5c6675"> · today</span></div>
  <div class="li"><span class="dt" style="background:#ff7d3a"></span>Hotspot / plume</div>
  <div class="li"><span class="dt" style="background:#ffd257"></span>Erupting province</div>
  <div class="li"><span class="dt" style="background:#b08968"></span>Basalt province standing</div>
  <div class="li"><span class="dt" style="background:#c9d6e8"></span>Impact crater</div>
  <div class="li"><span class="dt" style="background:#8792a6"></span>Crater eroded, record remains</div>
  <div class="li" style="margin-top:5px;color:#5c6675;font-size:9.5px;max-width:150px;line-height:1.45">Boundaries and vectors in deep time are derived from the reconstruction's own motion.</div>`;
}

/* ================= boot ================= */
(async function(){
  initGL();
  await loadAll();
  ensureLabels();buildBoundaries();buildRivers();buildHotspots();buildVectors();buildMarkers();buildLegend();
  buildEraList();buildScList();buildExtinctionList();buildGlaciationList();buildClimateEventList();buildInterchangeList();markSidebarCurrent();
  /* A handle on the internals. Everything here is derived — label positions
     are snapped to the elevation field, feature coordinates are back-advected —
     so when something does not appear on screen the only way to find out which
     stage dropped it is to be able to call that stage directly. */
  window.APP={state,DATA,mat,TEXCACHE,snapLabel,projectLL,curFrame,elevField,elevAtLL,   // mat/TEXCACHE: the harness reads uniforms and residency
              loader:()=>({pending:[..._bmPending.keys()],upQ:_upQ.map(q=>q.k+q.i),missing:[..._bmMissing],frame:_frameNo,
                           mb:Math.round(_texBytes/1048576),hidden:document.hidden,scrubbing:_scrubbing}),   // the decode/upload queues, for the harness
              labelVisible,layoutLabels,hotspotsNow,intervalAt,lifeAt,biomesAt,
              selectAt,showFeature,showEvent,jumpTo,featurePos,
              /* step() drives one frame by hand. Needed because a headless or
                 backgrounded tab reports document.hidden, and the browser then
                 never fires requestAnimationFrame — the app looks frozen when
                 it is simply not being asked to draw. */
              step(){loop(performance.now(),true);},
              /* ---- VISUAL-VERIFICATION HARNESS ----------------------------
                 Every "I checked it on screen" claim in this project runs
                 through here, because doing it by hand went wrong in three
                 separate ways and each one produced confident, wrong reports:

                 1. STALE FRAMES. A backgrounded tab gets no requestAnimationFrame,
                    so setting state changed nothing on screen and a screenshot
                    returned the previous frame. step() already existed for this
                    and was simply never used.
                 2. THE CAMERA WAS AIMED BY GUESS. rot was assumed to be minus
                    the centre longitude. It is not: ll2v puts the XZ angle at
                    lon+90, so centre longitude = -rot - 90. Ninety degrees out,
                    which is why asking for the Mediterranean gave the Appalachians.
                 3. NOTHING EVER CHECKED. There was no step between "aim" and
                    "screenshot" that could fail, so a mis-aimed camera was
                    indistinguishable from a correct one until a human looked.

                 lookAt derives the rotation instead of assuming it, forces a
                 frame, and then PROJECTS THE TARGET BACK and reports where it
                 actually landed. If offCentre is not small, the view is wrong
                 and the screenshot must not be believed. */
              lookAt(lon, lat, o){
                o = o || {};
                // exact inverse of ll2v's XZ angle; no assumption involved
                state.rot = -((lon + 90) * DEG);
                state.tilt = lat * DEG;
                /* CLAMP TO WHAT THE UI CAN REACH. The wheel and pinch handlers
                   both clamp to [1.35, 5]; this path wrote state.zoom raw, so a
                   verification shot could render a camera no user can get to.
                   Below about 1.35 the terrain smears into long radial spikes,
                   and a whole round was spent measuring "whole-globe interiors"
                   from shots taken at zoom 1.0 -- which were not globes at all
                   but streaked close-ups. An instrument that can reach states
                   the app cannot will keep reporting defects that do not exist. */
                if (o.zoom != null) state.zoom = Math.max(1.35, Math.min(5, o.zoom));
                if (o.gtilt != null) state.gtilt = o.gtilt;
                if (o.head != null) state.head = o.head;
                if (o.age != null) jumpTo(o.age);
                // A HIDDEN PANE HAS A 0x0 VIEWPORT. innerWidth and innerHeight go
                // to zero, the camera aspect goes to NaN, and projectLL -- which
                // scales NDC by innerWidth -- returns null. That single fact is
                // behind every unreliable visual check in this project: the page
                // was not frozen, it had no size. Give it one explicitly.
                const W = o.w || 1200, H = o.h || 900;
                if (!innerWidth || !innerHeight || o.w) {
                  renderer.setSize(W, H, false);
                  cam.aspect = W / H; cam.updateProjectionMatrix();
                }
                // twice: the first pass updates matrices the projection reads
                loop(performance.now()); loop(performance.now());
                // Measured in NDC, not pixels, so the answer does not depend on
                // a viewport that may not exist. Centre is (0,0); z<1 is in front.
                const v = ll2v(lon, lat, 1.02).applyMatrix4(globe.matrixWorld).project(cam);
                const off = Math.hypot(v.x, v.y);
                return {ok: v.z < 1 && off < 0.10,
                        offNDC: +off.toFixed(4),
                        px: Math.round(off * W / 2),
                        centreLon: -(state.rot / DEG) - 90, centreLat: state.tilt / DEG,
                        viewport: W + 'x' + H, age: state.age};
              },
              /* Full-resolution crop, rendered on demand. The browser pane
                 downsamples to 800x450, which is below the scale of several
                 artefacts this project has chased -- so eyeballing the pane is
                 not a check, it is a vibe. */
              snap(w, h, cx, cy, opts){
                loop(performance.now());
                const c = renderer.domElement, gl = renderer.getContext();
                w = w || 480; h = h || 480;
                const x0 = Math.max(0, Math.round((cx != null ? cx : c.width / 2) - w / 2));
                const y0 = Math.max(0, Math.round((cy != null ? cy : c.height / 2) - h / 2));
                const px = new Uint8Array(w * h * 4);
                gl.readPixels(x0, y0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, px);
                let sum = 0; for (let i = 0; i < px.length; i += 4) sum += px[i] + px[i+1] + px[i+2];
                if (sum === 0) return {error: 'empty framebuffer -- nothing was drawn'};
                const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
                const ctx = cv.getContext('2d'), im = ctx.createImageData(w, h);
                for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
                  const s = ((h - 1 - y) * w + x) * 4, d = (y * w + x) * 4;
                  im.data[d] = px[s]; im.data[d+1] = px[s+1];
                  im.data[d+2] = px[s+2]; im.data[d+3] = 255;
                }
                ctx.putImageData(im, 0, 0);
                /* LABELS, DRAWN IN. They live in a DOM overlay, so a readPixels
                   capture of the WebGL canvas never contained them -- which meant
                   every label bug had to be verified numerically and taken on
                   trust. The DOM positions are no use either: layoutLabels sizes
                   from innerWidth, which is 0 in a hidden pane, so every element
                   reports a rect at the origin.

                   So project them here instead, with the same camera the frame
                   was rendered with. No DOM, no viewport, works headless.

                   Crop mapping: readPixels takes y0 from the BOTTOM, and the loop
                   above flips into a top-down image, so the crop's top edge in
                   top-down canvas coordinates is height - y0 - h. */
                if (opts && opts.labels) {
                  const topY = c.height - y0 - h;
                  const fi = curFrame().i;
                  /* LINE-LAYER COMPOSITOR (iteration 24): GL lines never
                     rasterize in the headless pipeline, so the capture
                     strokes the river segments itself with the same camera
                     -- placement and density verify headlessly; the real
                     rasterization is a real browser's job. */
                  const rsegs = RIVDATA.get(fi);
                  if (rsegs && rsegs.length) {
                    ctx.strokeStyle = 'rgba(31,74,94,0.62)'; ctx.lineWidth = 1;
                    ctx.beginPath();
                    for (const sg of rsegs) {
                      let on = true; const pts = [];
                      for (const [lo, la] of [[sg[0], sg[1]], [sg[2], sg[3]]]) {
                        const lp = ll2v(lo, la, 1.004);
                        const wp = lp.clone().applyMatrix4(globe.matrixWorld);
                        /* Near-side test by DISTANCE, not by normal: the
                           normal-based horizon test rejected every segment
                           (census: 3539 occl, 0 pass) while the same
                           positions provably paint at the right pixels --
                           a point on the near hemisphere is simply closer
                           to the camera than the globe's centre is. */
                        if (wp.distanceTo(cam.position) > cam.position.length()) { on = false; break; }
                        const v = wp.project(cam);
                        pts.push([(v.x * 0.5 + 0.5) * c.width - x0,
                                  (1 - (v.y * 0.5 + 0.5)) * c.height - topY]);
                      }
                      if (on && pts.length === 2 &&
                          Math.abs(pts[0][0] - pts[1][0]) < 60) {
                        ctx.moveTo(pts[0][0], pts[0][1]);
                        ctx.lineTo(pts[1][0], pts[1][1]);
                      }
                    }
                    ctx.stroke();
                  }
                  ctx.font = '600 13px system-ui, sans-serif';
                  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
                  ctx.lineJoin = 'round';
                  let drawn = 0;
                  /* Mirror layoutLabels' zoom declutter (2026-08-01): this
                     capture path projects labels itself, so without the same
                     tiering every verification frame carried dozens of names
                     the LIVE page no longer shows -- the instrument must
                     match the instrumented. */
                  /* ...AND MIRROR ITS PLACEMENT TOO, which for a long time this
                     did not. The sort above was carried across from
                     layoutLabels; the greedy ring placement and the collision
                     test below it were not, so this path drew every name onto
                     its bare anchor and stacked whatever landed together. It
                     produced "TibTibetan Plateaudra" in a Himalaya shot and got
                     reported as a label bug, when the live page at the same
                     framing draws 63 names with zero overlapping pairs (probed
                     via evalq). An instrument that reimplements half a rule
                     reports the half it left out as a defect in the subject. */
                  const placedS=[], leadS=[];
                  const minPriS=0, capS=Infinity;
                  const cand=[];
                  for (const L of (DATA.labels || [])) {
                    if ((PRI[L.t]||40)+(L.w||0) < minPriS) continue;
                    cand.push(L);
                  }
                  cand.sort((a,b)=>((PRI[b.t]||40)+(b.w||0))-((PRI[a.t]||40)+(a.w||0)));
                  for (const L of cand) {
                    if (drawn >= capS) break;
                    if (!labelVisible(L)) continue;
                    const sp = snapLabel(L, fi); if (!sp) continue;
                    /* OCCLUSION IS A NORMAL TEST, NOT A DEPTH TEST. z < 1 only
                       says "inside the far plane", which every point on the far
                       side of the globe also satisfies -- so the first version
                       of this drew Yilgarn Craton and Lachlan Orogen across
                       North America. The globe is opaque: a label is visible
                       only where its own surface normal faces the camera, which
                       is the test projectLL already uses. */
                    const lp = ll2v(sp[0], sp[1], 1.02);
                    const wp = lp.clone().applyMatrix4(globe.matrixWorld);
                    const nrm = lp.clone().applyQuaternion(globe.quaternion).normalize();
                    const toCam = cam.position.clone().sub(wp).normalize();
                    if (nrm.dot(toCam) < 0.12) continue;    // over the horizon
                    const v = wp.clone().project(cam);
                    if (v.z >= 1) continue;
                    const px = (v.x * 0.5 + 0.5) * c.width - x0;
                    const py = (1 - (v.y * 0.5 + 0.5)) * c.height - topY;
                    if (px < -60 || py < -20 || px > w + 60 || py > h + 20) continue;
                    /* Same RINGS, same test, same give-up-and-drop as the live
                       placer. Widths come from measureText rather than a DOM
                       rect, which is the whole reason this path exists. */
                    const tw = ctx.measureText(L.n).width + 6, th = 15;
                    let put = null;
                    for (const [ox, oy] of RINGS) {
                      const x = px + ox, y = py + oy;
                      if (x - tw/2 < 2 || x + tw/2 > w - 2 ||
                          y - th/2 < 2 || y + th/2 > h - 2) continue;
                      let hit = false;
                      for (const r of placedS)
                        if (Math.abs(x - r.x) < (tw + r.w)/2 + 2 &&
                            Math.abs(y - r.y) < (th + r.h)/2 + 2) { hit = true; break; }
                      if (!hit) { put = {x: x, y: y}; break; }
                    }
                    if (!put) continue;              // no room: drop it, as the app does
                    placedS.push({x: put.x, y: put.y, w: tw, h: th});
                    if (Math.hypot(put.x - px, put.y - py) > 17)
                      leadS.push([px, py, put.x, put.y]);
                    ctx.strokeStyle = 'rgba(0,0,0,0.85)'; ctx.lineWidth = 3.5;
                    ctx.strokeText(L.n, put.x, put.y);
                    ctx.fillStyle = (L.t === 'ocean' || L.t === 'sea')
                                    ? '#bcd8ee' : '#ffffff';
                    ctx.fillText(L.n, put.x, put.y);
                    drawn++;
                  }
                  /* A pushed name points at the wrong ground without one. */
                  if (leadS.length) {
                    ctx.strokeStyle = 'rgba(255,255,255,0.38)'; ctx.lineWidth = 1;
                    ctx.beginPath();
                    for (const ld of leadS) { ctx.moveTo(ld[0], ld[1]); ctx.lineTo(ld[2], ld[3]); }
                    ctx.stroke();
                  }
                  return {png: cv.toDataURL('image/png').slice(22), w: w, h: h,
                          labelsDrawn: drawn};
                }
                return {png: cv.toDataURL('image/png').slice(22), w: w, h: h};
              },
              /* Render and POST the pixels to build/verify_server.py, which
                 writes them to build/verify/. This is the only route that works
                 with the pane hidden: an anchor-click download needs a visible
                 document and silently does nothing without one. */
              async shoot(name, size, cx, cy, opts){
                const s = APP.snap(size || 600, size || 600, cx, cy,
                                   opts || {labels: true});
                if (s.error) return s;
                try{
                  const r = await fetch('http://127.0.0.1:8901/' + (name || 'shot'),
                                        {method: 'POST', body: s.png});
                  return {saved: await r.text(), bytes: s.png.length};
                }catch(e){ return {error: 'receiver not running? ' + e.message}; }
              },
              /* WORLD SHEETS (WP-10). status() lists what is baked; bake(i)
                 finishes keyframe i's sheet synchronously (all strips now);
                 png(i) reads a finished sheet back as RGBA (alpha = ocean
                 mask, 0.5 water / 1 land -- see the FRAG note on why not 0)
                 for verification and for build/bake_sheets.py. */
              sheets:{
                status(){return {mode:liteMode,w:SHEET_W,h:SHEET_H,lite:globe.material===liteMat,frames:_liteFrames,
                  job:_bakeJob?{i:_bakeJob.i,row:_bakeJob.row}:null,
                  ready:[...SHEETS].filter(([i,s])=>s.ready).map(([i])=>i)};},
                bake(i){
                  if(!_sheetKindsResident(i))return {pending:true};
                  let s=SHEETS.get(i);
                  if(s&&!s.rt){_sheetDrop(i);s=null;}          // re-bake over a shipped one
                  if(!s){s=_sheetSlot(i,[i]);if(!s)return {error:'no slot'};}
                  _bakeJob={i:i,rt:s.rt,row:0};
                  while(_bakeJob)_bakeStrips();
                  return {ready:true,i:i};
                },
                png(i){
                  const s=SHEETS.get(i); if(!(s&&s.ready&&s.rt))return {error:'sheet '+i+' not baked here'};
                  const w=SHEET_W,h=SHEET_H,px=new Uint8Array(w*h*4);
                  renderer.readRenderTargetPixels(s.rt,0,0,w,h,px);
                  const cv=document.createElement('canvas');cv.width=w;cv.height=h;
                  const ctx=cv.getContext('2d'),im=ctx.createImageData(w,h);
                  // readback row 0 is the bottom of the target (uv.y 0, the south pole); a PNG wants north on top
                  for(let y=0;y<h;y++){im.data.set(px.subarray((h-1-y)*w*4,(h-y)*w*4),y*w*4);}
                  ctx.putImageData(im,0,0);
                  return {png:cv.toDataURL('image/png').slice(22),w:w,h:h};
                }},
              gl:{mat,scene,globe,atmo,clouds,renderer,cam}};
  // Do NOT reset the age here — the opening age is a deliberate choice made in
  // `state`, and hard-coding 0 quietly overrode it.
  syncSlider();updateReadout();syncPlay();syncDir();
  const qb=$('#qualBtn'); if(qb){qb.addEventListener('click',cycleQuality);applyQuality();}
  setInterval(updateReadout,120);
  $('#load').classList.add('done');
  // When the globe first became usable, measured inside the page. The number
  // that matters for this app is not DOMContentLoaded but this: how long until
  // there is an Earth to look at.
  window.__readyAt=performance.now();
  requestAnimationFrame(loop);
  // The globe is on screen and interactive by here; the rest of the timeline
  // fills in behind it, nearest-to-the-viewer first.
  startPrefetch();
})();
