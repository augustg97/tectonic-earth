precision highp float;
/* THE CLOUD LAYER (the Atlas port, 2026-09-07): NASA's Blue Marble cloud
   field, moving. The old shell composed clouds from the rainfall field and
   noise; this one samples a 4096x2048 scalar derivative of NASA's cloud-only
   composite (NASA/Goddard Space Flight Center, image by Reto Stoeckli;
   web/imagery/nasa-clouds.json carries the provenance) as ONE continuous
   field in coherent transport -- 0.004 radians per weather second, a
   bounded latitude shear and gently varying deformation, never accumulated
   strain and never a crossfade between phases, which is what keeps fronts
   connected and storms single. The selected era adapts it: the shared
   elevation and rainfall pair gives a land mask and a broad land-normalised
   wetness that modulates optical depth gently, and uEra shifts the
   arrangement. Rainfall is land-only, so an ocean zero is never read as
   dryness. This is satellite-derived visual structure with illustrative
   climate adaptation, not reconstructed weather for any date.

   Six samplers, separate from the terrain shader's sixteen: the pair's
   elevation and rainfall (the terrain's own uniform objects, so the clouds
   can only ever see the world the ground shows), the noise lattice (uNz,
   shared, injected at the marker below) and the cloud image. uRainReady is
   1 only while the rainfall bound matches the elevation bound; otherwise a
   neutral wetness stands in and no fallback ever reaches the terrain's
   uniforms. uTemp is the era's temperature PARAMETER (-1..1, present -0.55),
   not a temperature in degrees. uCloudDetailBlend fades the image in from
   the noise fallback as it arrives; uCloud is the final visibility (fade and
   close-view attenuation); uShadow selects the shadow pass; uCloudMap maps
   the Mollweide plane. Derivatives (dFdx/dFdy) shape the billows, so the
   material must enable them. */
uniform sampler2D rainA,rainB,elevA,elevB,uNz,uCloudDetail;
uniform float mixf,uWeatherTime,uCloud,uShadow,uCloudMap,uMapLon,uRainReady,uEra,uTemp;
uniform float uSnowball;   // the era's ice line at the equator (1) damps the whole deck: a frozen ocean feeds little cloud
uniform float uCloudDetailBlend;
/* THE WEATHER (3.17): x the wind's speed (0 restores the 3.16 rigid drift,
   ?wind=), y the renewal cycle in weather seconds (?wcyc=), z orographic
   cloud (?orog=), w marine stratocumulus (?scu=). */
uniform vec4 uWind;
varying vec2 vUv;varying vec3 vN;
const float PI=3.14159265359;
/*@cnoise*/
vec3 sphere(float lon,float lat){return vec3(cos(lat)*cos(lon),sin(lat),cos(lat)*sin(lon));}
vec2 climateAt(vec2 q){
  q=vec2(fract(q.x),clamp(q.y,0.001,0.999));
  float a=texture2D(elevA,q).r*2.0-1.0;
  float h=sign(a)*a*a*8000.0,rain=texture2D(rainA,q).r;
  if(mixf>0.00001){
    float b=texture2D(elevB,q).r*2.0-1.0;
    h=mix(h,sign(b)*b*b*8000.0,mixf);
    rain=mix(rain,texture2D(rainB,q).r,mixf);
  }
  float land=smoothstep(-80.0,160.0,h);
  /* rain weighted by land, so the caller's division by the summed land is a
     true normalised average: the field fills the sea from the land around it
     (build/rain_fill.py), and read raw that fill would count a coast's rain
     twice. */
  return vec2(land,rain*land);
}
/* Land for the deck's coast test, on a ramp across the continental slope
   (-2,500 m to +300 m) instead of at the waterline: summed over offsets, a
   sharp land test copies the coastline's every step into the deck's edge. */
float deckLand(vec2 q){
  q=vec2(fract(q.x),clamp(q.y,0.001,0.999));
  float a=texture2D(elevA,q).r*2.0-1.0;
  float h=sign(a)*a*a*8000.0;
  if(mixf>0.00001){ float b=texture2D(elevB,q).r*2.0-1.0; h=mix(h,sign(b)*b*b*8000.0,mixf); }
  return smoothstep(-2500.0,300.0,h);
}
vec2 satelliteWeather(float lon,float lat,float gain,float lo0){
  // One unbroken observed cloud field preserves real fronts, spirals and
  // clear slots. Only bounded residual flow deforms it; strain cannot grow.
  float t=uWeatherTime;
  float sourceLon=lon-mod(t*0.0040,2.0*PI)+sin(uEra*0.003)*0.9;
  vec3 p=sphere(sourceLon,lat);
  vec3 seed=vec3(7.0,19.0,11.0)+uEra*0.001;
  float n0=cn(p*2.0+seed)-0.5;
  float n1=cn(p*2.0+seed+vec3(11.0,7.0,19.0))-0.5;
  float belt=smoothstep(0.384,0.785,abs(lat));
  float shear=mix(-1.0,1.0,belt)*0.060*sin(t*0.017);
  float bend=0.045*n0*sin(t*0.023+1.4);
  float lift=0.045*cos(lat)*n1*sin(t*0.019+0.7);
  // Keep longitude unwrapped for continuous mip derivatives at the dateline.
  vec2 q=vec2((sourceLon+shear+bend)/(2.0*PI)+0.5,(lat+lift)/PI+0.5);
  float raw=texture2D(uCloudDetail,q).r;
  float broad=texture2D(uCloudDetail,q,2.0).r;
  float d=smoothstep(lo0,0.98,raw);
  float tau=2.8*pow(d,1.25)*gain;
  float height=pow(max(broad,0.0),1.4)*gain;
  return vec2(tau,height);
}
/* THE WIND THE DECK RIDES (3.17), east and north in radians of arc per
   weather second. Until 3.16 the whole field turned east as one rigid shell,
   so tropical cloud ran with the westerlies and nothing ever sheared, swirled
   or converged. The surface circulation of a rotating planet has three
   bands -- the trades blowing west and converging on the equatorial trough,
   the westerlies peaking near 45 degrees, weak polar easterlies -- and the
   storms of the westerly belt turn inside them. The eddies are the curl of a
   drifting stream function, so they swirl without piling cloud up. */
float whash(float n){return fract(sin(n*12.9898+78.233)*43758.5453);}
/* THE STREAM FUNCTION IS ANALYTIC (3.19). It was the lattice noise cn()
   differenced over 0.03 rad -- and cn interpolates inside the texture unit,
   whose bilinear weights carry 8 bits of sub-texel position, so the noise is
   a fine staircase and a short difference of it is a spike train. Scaled by
   a whole renewal cycle of travel, neighbouring pixels read winds that moved
   their cloud tens of kilometres apart: the brickwork of short dashes over
   the eastern United States. Value noise evaluated in arithmetic, with its
   exact gradient (xyz) beside its value (w), has no staircase to amplify. */
float wh(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
vec4 wnoise(vec3 x){
  vec3 i=floor(x),f=fract(x),u=f*f*(3.0-2.0*f),du=6.0*f*(1.0-f);
  float a=wh(i),b=wh(i+vec3(1.0,0.0,0.0)),c=wh(i+vec3(0.0,1.0,0.0)),d=wh(i+vec3(1.0,1.0,0.0));
  float e=wh(i+vec3(0.0,0.0,1.0)),g=wh(i+vec3(1.0,0.0,1.0)),h=wh(i+vec3(0.0,1.0,1.0)),m=wh(i+vec3(1.0,1.0,1.0));
  float k1=b-a,k2=c-a,k3=e-a,k4=a-b-c+d,k5=a-c-e+h,k6=a-b-e+g,k7=-a+b+c-d+e-g-h+m;
  float v=a+k1*u.x+k2*u.y+k3*u.z+k4*u.x*u.y+k5*u.y*u.z+k6*u.z*u.x+k7*u.x*u.y*u.z;
  vec3 dv=du*vec3(k1+k4*u.y+k6*u.z+k7*u.y*u.z,k2+k5*u.z+k4*u.x+k7*u.z*u.x,k3+k6*u.x+k5*u.y+k7*u.x*u.y);
  return vec4(dv,v);
}
vec2 windAt(float lon,float lat,float t){
  float d=abs(degrees(lat));
  float u=mix(-0.42,1.0,smoothstep(16.0,30.0,d));
  u=mix(u,-0.22,smoothstep(58.0,72.0,d));
  float v=-sign(lat)*0.16*smoothstep(1.0,7.0,d)*(1.0-smoothstep(14.0,28.0,d));
  float storm=0.35+0.65*exp(-pow((d-48.0)/16.0,2.0));
  float lp=lon-t*0.0035;
  vec4 n=wnoise(sphere(lp,lat)*2.4+vec3(5.3,11.7,2.9));
  // the stream function's gradient per radian of arc, east and north
  vec2 g=2.4*vec2(dot(n.xyz,vec3(-sin(lp),0.0,cos(lp))),
                  dot(n.xyz,vec3(-sin(lat)*cos(lp),cos(lat),-sin(lat)*sin(lp))));
  vec2 eddy=vec2(-g.y,g.x)*0.30*storm;
  return (vec2(u,v)+eddy)*0.0042*uWind.x;
}
/* CLOUD CARRIED BY THAT WIND, RENEWED AS IT GOES (3.17). A field advected
   without end stretches into threads, so the satellite structure is carried
   for one renewal cycle and then replaced: two phases half a cycle apart,
   each forming, drifting with the local wind and dissipating. Each new cycle
   draws its cloud from a different stretch of the observed field (the same
   latitude band, so storm tracks stay storm tracks), and the cycle's phase
   varies slowly across the globe, so systems form and dissipate region by
   region instead of the sky pulsing at once.

   FORM AND DISSIPATE, NEVER FADE (3.19). The phases used to be cross-faded:
   optical depth times a triangular weight, summed. Half of every cycle the
   sky was two unrelated cloud fields at half strength each -- a translucent
   double exposure, the grey haze over the Canaries. A cloud does not fade
   as a whole; it grows from its thickest core and evaporates from its thin
   edges. So a phase's life raises and lowers its density THRESHOLD: young,
   only the cores of its field show; mature, the whole field; dying, the cores
   again, then nothing. The two phases combine as a union, so what is visible
   is always cloud at a cloud's own opacity. Calibrated on the observed field
   itself (a numpy replica over random pairs of its longitudes): the sky's
   mean opacity within 7% of the cross-fade's over open ocean, with the
   translucent share (alpha 0.1-0.5) down from 37% of the sky to 18%, and over
   the subtropical deserts from 34% to 7%. */
vec2 renewalAt(float t,float ph,int i){
  float s=t/max(uWind.y,5.0)+0.5*float(i)+ph;
  float cyc=floor(s);
  return vec2(s-cyc,cyc*2.0+float(i));        // life fraction, cycle key
}
float renewalPhase(float lon,float lat){
  return 0.45*wnoise(sphere(lon,lat)*1.3+vec3(19.0,2.0,7.0)).w;
}
vec2 flowWeather(float lon,float lat,float t,float gain,float lo0,vec2 W){
  float T=max(uWind.y,5.0);
  float ph=renewalPhase(lon,lat);
  float cl=max(cos(lat),0.2);
  float dU=0.0,hU=0.0;
  for(int i=0;i<2;i++){
    vec2 r=renewalAt(t,ph,i);
    float w=1.0-abs(2.0*r.x-1.0);
    float oLon=whash(r.y*1.13+3.7)*6.2831853+sin(uEra*0.003)*0.9;
    float oLat=(whash(r.y*2.71+9.1)-0.5)*0.10;
    float age=r.x*T;
    float sLon=lon-W.x*age/cl+oLon;
    float sLat=clamp(lat-W.y*age+oLat,-1.55,1.55);
    vec2 q=vec2(sLon/(2.0*PI)+0.5,sLat/PI+0.5);
    float raw=texture2D(uCloudDetail,q).r;
    float broad=texture2D(uCloudDetail,q,2.0).r;
    float lo=min(lo0+(1.0-w)*0.45,0.90);
    float d=smoothstep(lo,0.98,raw)*smoothstep(0.0,0.22,w);
    dU=1.0-(1.0-dU)*(1.0-d);
    hU+=w*pow(max(broad,0.0),1.4);
  }
  return vec2(3.4*pow(dU,1.25),hU)*gain;
}
/* THE DECKS ARE THE OBSERVED DECKS (3.19). Wherever the era puts the eastern
   edge of an open subtropical ocean, its deck is drawn with the stratocumulus
   the satellite field actually recorded off Peru and Chile (south of the
   equator) or California and Baja (north of it): the same closed cells,
   rifts and pockets of open cells, at the same latitude. Two noise sheets
   tried before this read as a crackle glaze (3.17) and as soft blotches
   (3.19's first attempt); a deck's texture is its own, so borrow it.

   The source is a fixed band of longitude off each coast, tiled along
   longitude by two copies half a tile apart, each dissolving toward its own
   seam by the same union the renewal phases use -- so no seam and no mirror
   line is ever drawn; latitude folds back at the band's ends (6 and 34
   degrees), where the deck is thin anyway. The band is FIXED, not traced
   along the coast: the Peruvian coast swings 7 degrees east between 11 and
   18 S, and a band that followed it sheared the borrowed texture into
   diagonal streaks. 92-78 W south of the equator (clear of the Andes at 5 S,
   inside the deck at 30 S), 137-123 W north of it. */
vec2 deckField(float lon,float lat,float t,vec2 W,float lo0){
  float T=max(uWind.y,5.0);
  float ph=renewalPhase(lon,lat);
  float cl=max(cos(lat),0.2);
  float dlon=degrees(lon),dlat=degrees(lat),south=step(dlat,0.0);
  float dU=0.0,hU=0.0;
  for(int i=0;i<2;i++){
    vec2 r=renewalAt(t,ph,i);
    float w=1.0-abs(2.0*r.x-1.0);
    float age=r.x*T;
    float x=dlon-degrees(W.x*age/cl)+whash(r.y*4.3+1.0)*97.0;
    float y=abs(dlat-degrees(W.y*age))+(whash(r.y*6.1+2.0)-0.5)*4.0;
    float sy=y<6.0 ? 12.0-y : (y>34.0 ? 68.0-y : y);
    float sLat=mix(sy,-sy,south);
    float c=mix(-121.0,-76.0,south);          // the band's east edge, degrees
    for(int j=0;j<2;j++){
      float f=fract(x/14.0+0.5*float(j));
      float tw=1.0-abs(2.0*f-1.0);            // this copy's share of its tile
      vec2 q=vec2((c-16.0+14.0*f)/360.0+0.5,sLat/180.0+0.5);
      float raw=texture2D(uCloudDetail,q).r;
      float broad=texture2D(uCloudDetail,q,2.0).r;
      // a deck persists, so its phases erode half as deep as the weather's;
      // the tile only gently, or two half-eroded copies of a thin deck would
      // leave next to nothing
      float lo=min(lo0+(1.0-w)*0.36+(1.0-tw)*0.30,0.92);
      float d=smoothstep(lo,0.98,raw)*smoothstep(0.0,0.22,w)*smoothstep(0.0,0.20,tw);
      dU=1.0-(1.0-dU)*(1.0-d);
      hU+=w*tw*pow(max(broad,0.0),1.4);
    }
  }
  return vec2(dU,hU);
}
float elevAtUv(vec2 q){
  q=vec2(fract(q.x),clamp(q.y,0.001,0.999));
  float a=texture2D(elevA,q).r*2.0-1.0;
  float h=sign(a)*a*a*8000.0;
  if(mixf>0.00001){float b=texture2D(elevB,q).r*2.0-1.0;h=mix(h,sign(b)*b*b*8000.0,mixf);}
  return h;
}
vec2 fallbackWeather(float lon,float lat,float gain){
  vec3 p=sphere(lon-uWeatherTime*0.004,lat);
  float n=cn(p*3.5+vec3(17.0,5.0,29.0)+uEra*0.01);
  float f=cn(p*17.0+vec3(3.0,23.0,11.0));
  float density=smoothstep(0.54,0.78,n)*(0.4+0.6*f);
  return vec2(density*2.0*gain,density);
}
void main(){
  vec2 uv=vUv;
  if(uCloudMap>0.5){
    float X=(uv.x*2.0-1.0)*2.0,Y=uv.y*2.0-1.0;
    if(X*X*0.25+Y*Y>1.0)discard;
    float th=asin(clamp(Y,-1.0,1.0)),c=cos(th);
    if(abs(c)<0.00001)discard;
    float lon=PI*X/(2.0*c);
    if(abs(lon)>PI)discard;
    float lat=asin(clamp((2.0*th+sin(2.0*th))/PI,-1.0,1.0));
    uv=vec2((lon+uMapLon)/(2.0*PI)+0.5,0.5+lat/PI);
  }
  float t=uWeatherTime,lat=(uv.y-0.5)*PI,al=abs(degrees(lat));
  float lon=(uv.x-0.5)*2.0*PI;
  // Land-only rainfall is averaged over a broad neighborhood. Climate
  // modulates optical depth gently; it never chops fronts into noise puffs.
  vec2 off=vec2((3.0/360.0)/max(0.35,cos(lat)),3.0/180.0);
  vec2 climate=climateAt(uv)*0.5+climateAt(uv+off)*0.25+climateAt(uv-off)*0.25;
  float land=smoothstep(0.08,0.92,climate.x);
  float rain=climate.y/max(climate.x,0.12);
  float wet=mix(0.30,smoothstep(0.025,0.52,rain),uRainReady);
  float dry=land*(1.0-wet);
  /* COVER, NOT HAZE (3.19). Everything below that makes a sky clearer -- dry
     land, the subtropical highs, a quiet synoptic spell, the lee of a range,
     a cold or frozen world -- used to multiply optical depth, and a cloud at a
     third of its depth is a grey veil, not a smaller cloud: the haze over the
     Sahara and the Canaries. Most of each now raises the density threshold
     (lo0) instead, so a clearer sky has fewer clouds, each still a cloud; a
     gentle share stays on optical depth so thin weather still reads thinner. */
  float cold=smoothstep(-5.0,-1.5,uTemp);
  float gain=mix(0.96,mix(0.72,1.10,wet),land)*mix(0.75,1.0,cold);
  float lo0=0.025+dry*0.18+(1.0-cold)*0.08;
  /* THE ERA'S LIKELY WEATHER (round 2, 2026-09-07). A soft zonal
     climatology under the satellite structure: the tropical convergence
     band, the mid-latitude storm tracks, the clear subtropical highs --
     the same three bands the original procedural clouds were built from --
     as gentle gains, never as masks that would cut a front in two. The
     era's land and rainfall above already move the deck with the
     continents; a snowball world loses most of it. */
  float zonal=0.80+0.30*exp(-pow(lat/0.16,2.0))+0.25*exp(-pow((al-52.0)/13.0,2.0))-0.30*exp(-pow((al-24.0)/9.0,2.0));
  gain*=mix(1.0,zonal,0.5)*(1.0-0.30*uSnowball);
  lo0+=max(0.0,1.0-zonal)*0.30+0.15*uSnowball;
  /* SLOW SYNOPTIC EVOLUTION (round 2). The satellite field is one frozen
     day in transport; on its own nothing ever forms or dies. A smooth
     three-dimensional lattice noise drifting through the weather clock
     (about a minute from clear to overcast at a point) gates the optical
     depth, so masses thicken, merge across a clearing and dissolve while
     the fine structure inside them keeps its fronts and spirals. The era
     moves the pattern too, gently, so a running timeline sees the weather
     reorganise rather than jump. A gate, broad -- not a second cloud field,
     and not a crossfade between two; since 3.19 it gates cover more than
     depth (above). */
  vec3 ps=sphere(lon,lat)*1.35+vec3(t*0.011,t*0.007,t*0.013)+vec3(31.0,17.0,5.0)+uEra*0.0007;
  float syn=smoothstep(0.30,0.72,0.65*cn(ps)+0.35*cn(ps*2.1+vec3(9.0,3.0,21.0)));
  gain*=mix(0.80,1.30,syn);
  lo0+=(1.0-syn)*0.10;
  /* THE AIR MEETS THE GROUND (3.17). Wind driven up a range lifts and
     cools and clouds over the windward slopes; the same air sinks down the
     lee and clears -- the rain shadow's cloud. And off the subtropical west
     coasts of whatever continents the era has, cold upwelled water under
     the subsiding air of the highs holds a bright low deck of stratocumulus:
     California, Peru, Namibia today. */
  vec2 W=windAt(lon,lat,t);
  float up=0.0;
  if(uWind.x>0.0&&uWind.z>0.0){
    vec2 Wd=W/max(length(W),1e-6);
    float dx=(1.2/360.0)/max(0.35,cos(lat)),dy=1.2/180.0;
    vec2 gh=vec2(elevAtUv(uv+vec2(dx,0.0))-elevAtUv(uv-vec2(dx,0.0)),
                 elevAtUv(uv+vec2(0.0,dy))-elevAtUv(uv-vec2(0.0,dy)))/(2.0*1.2*111.0);
    up=dot(Wd,gh)*land;                             // metres of climb per km along the wind
    gain*=1.0+uWind.z*0.95*smoothstep(0.4,5.0,up);  // windward: lifted air thickens what is there
    lo0+=uWind.z*0.30*smoothstep(0.4,5.0,-up);      // lee: sinking air clears it
  }
  lo0=min(lo0,0.85);
  vec2 cloud;
  if(uWind.x<=0.0){
    if(uCloudDetailBlend>=1.0)cloud=satelliteWeather(lon,lat,gain,lo0);
    else{
      cloud=fallbackWeather(lon,lat,gain);
      if(uCloudDetailBlend>0.001)cloud=mix(cloud,satelliteWeather(lon,lat,gain,lo0),uCloudDetailBlend);
    }
  } else {
    if(uCloudDetailBlend>=1.0)cloud=flowWeather(lon,lat,t,gain,lo0,W);
    else{
      cloud=fallbackWeather(lon,lat,gain);
      if(uCloudDetailBlend>0.001)cloud=mix(cloud,flowWeather(lon,lat,t,gain,lo0,W),uCloudDetailBlend);
    }
  }
  /* ...and the ranges hold cloud of their own: a cap over the windward crest
     and a belt along the slope, as thick as the air is wet -- the cloud
     forest on the Andes' Amazon flank, the caps on the Cascades and the
     Southern Alps in the westerlies. ANCHORED TO THE GROUND (3.19): it forms
     where the slope lifts the air, so it stays there while its cells form and
     dissolve (the noise volume drifts through the shell). It used to ride the
     wind for the whole weather clock, and a wind that varies from place to
     place, applied for minutes, sheared it into fine parallel threads. */
  if(uWind.x>0.0&&uWind.z>0.0&&up>0.3){
    vec3 po=sphere(lon,lat);
    vec3 ev=vec3(0.021,0.013,-0.017)*t;
    float cu=smoothstep(0.35,0.80,0.6*cn(po*60.0+vec3(4.0,1.0,6.0)+ev)+0.4*cn(po*160.0+vec3(2.0,8.0,3.0)+2.3*ev));
    float oc=smoothstep(0.3,4.0,up)*mix(0.25,1.0,wet)*(1.0-0.5*uSnowball);
    cloud.x+=uWind.z*oc*(0.05+2.6*cu)*gain;
    cloud.y=max(cloud.y,0.4*oc*cu);
  }
  /* The deck's latitudes, ragged: it breaks into trade cumulus along an
     irregular edge, never along a parallel (a clean band edge read as a ruled
     line from a hemisphere away). */
  float fl=(cn(sphere(lon,lat)*4.0+vec3(7.0,3.0,9.0))-0.5)*9.0+(cn(sphere(lon,lat)*11.0+vec3(2.0,6.0,1.0))-0.5)*4.0;
  float sub=smoothstep(5.0,17.0,al+fl)*(1.0-smoothstep(27.0,42.0,al+0.7*fl));
  if(uWind.x>0.0&&uWind.w>0.0&&sub*(1.0-land)>0.001){
    /* WHERE A DECK REALLY FORMS (3.17, revised). Marine stratocumulus sits
       over the cold current along the EASTERN edge of an OPEN ocean -- Peru,
       Namibia, California -- under the subsiding air of the subtropical high.
       The first version asked only for land to the east, so it laid decks in
       every gulf, bay, seaway and shelf sea of every age, drawn with a mesh of
       cells along a hard coastal edge: a white shape that rode the continents
       and read as part of the land. Now it needs open ocean to the WEST (the
       fetch the trades cross) and a coast upwind. (3.18 also asked for deep
       water beneath; read at the pixel, that punched a hole in the deck over
       every seamount and island shelf, and open water to the west already
       keeps decks out of gulfs, bays and shelf seas, so 3.19 dropped it.) */
    float cs=1.0/max(0.35,cos(lat));
    float jit=(cn(sphere(lon,lat)*55.0+vec3(8.0,2.0,6.0))-0.5)*2.6+(cn(sphere(lon,lat)*140.0+vec3(1.0,9.0,4.0))-0.5)*1.2;
    float lW=0.0;
    for(int k=0;k<6;k++){
      float fk=float(k);
      lW+=deckLand(uv-vec2((8.0+6.0*fk+jit)/360.0*cs,(fract(fk*0.618)-0.5)*3.0/180.0));
    }
    float openW=1.0-smoothstep(0.06,0.30,lW/6.0);
    float lE=0.0;
    if(openW>0.001){
      for(int k=0;k<10;k++){
        float fk=float(k);
        lE+=deckLand(uv+vec2((1.5+2.0*fk+jit)/360.0*cs,(fract(fk*0.618)-0.5)*1.6/180.0));
      }
      lE*=0.1;
    }
    float shore=1.0-smoothstep(0.20,0.75,deckLand(uv+vec2(0.9/360.0*cs,0.0)));
    float fray=0.65*(cn(sphere(lon,lat)*3.0+vec3(5.0,9.0,2.0))-0.5)+0.35*(cn(sphere(lon,lat)*8.0+vec3(1.0,3.0,7.0))-0.5);
    float sc=(1.0-land)*sub*openW*smoothstep(0.03,0.45,lE+0.30*fray)*shore*(1.0-0.45*uSnowball);
    if(sc>0.001){
      /* THE DECK IS CLOUD LIKE THE REST: the observed deck (deckField),
         on the same renewal clock as everything around it (3.19) -- no mesh
         of cells, no edge of its own, nothing carried by the whole weather
         clock (the 3.18 sheet was, and sheared into radial threads), and no
         translucent veil. It takes over from the borrowed weather where it is
         thick, as a real deck owns its sky; a passing front still shows. Its
         threshold keeps the deck's own clear-sky rule only: the subtropical
         high that clears the sky around it is what holds the deck down. */
      float core=smoothstep(0.10,0.60,lE+0.20*fray);
      float body=sc*mix(0.55,1.0,core);
      vec2 D=deckField(lon,lat,t,W,0.025+(1.0-syn)*0.10);
      cloud.x=cloud.x*(1.0-0.5*body)+uWind.w*body*2.8*pow(D.x,1.25)*mix(0.85,1.15,syn);
      cloud.y=mix(cloud.y,max(cloud.y,D.y),body);
    }
  }
  float mu=uCloudMap>0.5?1.0:max(normalize(vN).z,0.0);
  float path=mix(1.0,1.35,1.0-mu);
  float alpha=1.0-exp(-cloud.x*path);
  float lit=uCloudMap>0.5?1.0:smoothstep(-0.06,0.18,dot(normalize(vN),normalize(vec3(0.54,0.22,0.86))));
  float face=uCloudMap>0.5?1.0:smoothstep(-0.05,0.18,vN.z);
  if(uShadow>0.5){gl_FragColor=vec4(0.012,0.025,0.045,(1.0-exp(-cloud.x*0.30))*0.26*uCloud*face*lit);return;}
  // A smooth height proxy gives billows relief; use the geographic footprint
  // to keep it stable between the globe, Map and different pixel densities.
  vec3 geo=sphere(lon,lat);
  float footprint=max(length(dFdx(geo))+length(dFdy(geo)),0.0001);
  float relief=min(18.0,0.025/footprint);
  vec3 bumpN=normalize(vec3(-dFdx(cloud.y)*relief,-dFdy(cloud.y)*relief,1.0));
  vec3 L=normalize(vec3(0.54,0.22,0.86));
  float shade=0.70+0.30*max(dot(bumpN,L),0.0);
  float rim=0.08*pow(1.0-max(bumpN.z,0.0),3.0);
  vec3 daylight=vec3(0.95,0.975,1.0)*(shade+rim);
  vec3 linear=mix(vec3(0.002,0.004,0.009),daylight,lit);
  vec3 color=pow(max(linear,vec3(0.0)),vec3(1.0/2.2));
  gl_FragColor=vec4(color,alpha*uCloud*face);
}
