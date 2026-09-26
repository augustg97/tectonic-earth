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
  return vec2(land,rain);
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
vec2 satelliteWeather(float lon,float lat,float gain,float dry){
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
  float d=smoothstep(0.025+dry*0.045,0.98,raw);
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
vec2 windAt(float lon,float lat,float t){
  float d=abs(degrees(lat));
  float u=mix(-0.42,1.0,smoothstep(16.0,30.0,d));
  u=mix(u,-0.22,smoothstep(58.0,72.0,d));
  float v=-sign(lat)*0.16*smoothstep(1.0,7.0,d)*(1.0-smoothstep(14.0,28.0,d));
  float storm=0.35+0.65*exp(-pow((d-48.0)/16.0,2.0));
  vec3 base=vec3(5.3,11.7,2.9);
  float drift=t*0.0035,e=0.03;
  float p0=cn(sphere(lon-drift,lat)*2.4+base);
  float pE=cn(sphere(lon-drift+e/max(cos(lat),0.2),lat)*2.4+base);
  float pN=cn(sphere(lon-drift,lat+e)*2.4+base);
  vec2 g=vec2(pE-p0,pN-p0)/e;
  vec2 eddy=vec2(-g.y,g.x)*0.30*storm;
  return (vec2(u,v)+eddy)*0.0042*uWind.x;
}
/* CLOUD CARRIED BY THAT WIND, RENEWED AS IT GOES (3.17). A field advected
   without end stretches into threads, so the satellite structure is carried
   for one renewal cycle and then replaced: two phases half a cycle apart,
   each fading in, drifting with the local wind and fading out, their weights
   summing to one. Each new cycle draws its cloud from a different stretch of
   the observed field (the same latitude band, so storm tracks stay storm
   tracks), and the cycle's phase varies slowly across the globe, so systems
   form and dissipate region by region instead of the sky pulsing at once. */
/* Closed convective cells, F2-F1 of a jittered point lattice (Worley): the
   bright polygons with dark rims a stratocumulus sheet shows from orbit. 2-D
   in the local (east, north) plane -- the decks lie between 10 and 40 degrees,
   where that plane is undistorted enough. Returns 0 on a rim, 1 mid-cell. */
vec2 whash2(vec2 p){return fract(sin(vec2(dot(p,vec2(127.1,311.7)),dot(p,vec2(269.5,183.3))))*43758.5453);}
float cellsAt(vec2 x){
  vec2 i=floor(x),f=fract(x);
  float d1=8.0,d2=8.0;
  for(int yy=-1;yy<=1;yy++)for(int xx=-1;xx<=1;xx++){
    vec2 o=vec2(float(xx),float(yy));
    vec2 r=o+0.15+0.7*whash2(i+o)-f;
    float d=dot(r,r);
    if(d<d1){d2=d1;d1=d;}else if(d<d2){d2=d;}
  }
  return smoothstep(0.0,0.35,sqrt(d2)-sqrt(d1));
}
vec2 flowWeather(float lon,float lat,float t,float gain,float dry,vec2 W){
  float T=max(uWind.y,5.0);
  float ph=0.45*cn(sphere(lon,lat)*1.3+vec3(19.0,2.0,7.0));
  float cl=max(cos(lat),0.2);
  vec2 acc=vec2(0.0);
  for(int i=0;i<2;i++){
    float s=t/T+0.5*float(i)+ph;
    float cyc=floor(s);
    float tau=s-cyc;
    float w=1.0-abs(2.0*tau-1.0);
    float k=cyc*2.0+float(i);
    float oLon=whash(k*1.13+3.7)*6.2831853+sin(uEra*0.003)*0.9;
    float oLat=(whash(k*2.71+9.1)-0.5)*0.10;
    float age=tau*T;
    float sLon=lon-W.x*age/cl+oLon;
    float sLat=clamp(lat-W.y*age+oLat,-1.55,1.55);
    vec2 q=vec2(sLon/(2.0*PI)+0.5,sLat/PI+0.5);
    float raw=texture2D(uCloudDetail,q).r;
    float broad=texture2D(uCloudDetail,q,2.0).r;
    float dd=smoothstep(0.025+dry*0.045,0.98,raw);
    acc+=w*vec2(2.8*pow(dd,1.25),pow(max(broad,0.0),1.4));
  }
  return acc*gain;
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
  float gain=mix(0.94,mix(0.50,1.12,wet),land);
  gain*=0.60+0.40*smoothstep(-5.0,-1.5,uTemp);
  /* THE ERA'S LIKELY WEATHER (round 2, 2026-09-07). A soft zonal
     climatology under the satellite structure: the tropical convergence
     band, the mid-latitude storm tracks, the clear subtropical highs --
     the same three bands the original procedural clouds were built from --
     as gentle gains, never as masks that would cut a front in two. The
     era's land and rainfall above already move the deck with the
     continents; a snowball world loses most of it. */
  float zonal=0.80+0.30*exp(-pow(lat/0.16,2.0))+0.25*exp(-pow((al-52.0)/13.0,2.0))-0.30*exp(-pow((al-24.0)/9.0,2.0));
  gain*=zonal*(1.0-0.45*uSnowball);
  /* THE AIR MEETS THE GROUND (3.17). Wind driven up a range lifts and
     cools and clouds over the windward slopes; the same air sinks down the
     lee and clears -- the rain shadow's cloud. And off the subtropical west
     coasts of whatever continents the era has, cold upwelled water under
     the subsiding air of the highs holds a bright low deck of stratocumulus:
     California, Peru, Namibia today. */
  vec2 W=windAt(lon,lat,t);
  float orog=1.0,up=0.0;
  if(uWind.x>0.0&&uWind.z>0.0){
    vec2 Wd=W/max(length(W),1e-6);
    float dx=(1.2/360.0)/max(0.35,cos(lat)),dy=1.2/180.0;
    vec2 gh=vec2(elevAtUv(uv+vec2(dx,0.0))-elevAtUv(uv-vec2(dx,0.0)),
                 elevAtUv(uv+vec2(0.0,dy))-elevAtUv(uv-vec2(0.0,dy)))/(2.0*1.2*111.0);
    up=dot(Wd,gh)*land;                             // metres of climb per km along the wind
    orog=clamp(1.0+uWind.z*(0.95*smoothstep(0.4,5.0,up)-0.60*smoothstep(0.4,5.0,-up)),0.35,2.0);
  }
  vec2 cloud;
  if(uWind.x<=0.0){
    if(uCloudDetailBlend>=1.0)cloud=satelliteWeather(lon,lat,gain,dry);
    else{
      cloud=fallbackWeather(lon,lat,gain);
      if(uCloudDetailBlend>0.001)cloud=mix(cloud,satelliteWeather(lon,lat,gain,dry),uCloudDetailBlend);
    }
  } else {
    if(uCloudDetailBlend>=1.0)cloud=flowWeather(lon,lat,t,gain,dry,W);
    else{
      cloud=fallbackWeather(lon,lat,gain);
      if(uCloudDetailBlend>0.001)cloud=mix(cloud,flowWeather(lon,lat,t,gain,dry,W),uCloudDetailBlend);
    }
  }
  cloud.x*=orog;
  /* ...and the ranges hold cloud of their own: a cap over the windward crest
     and a belt along the slope, as thick as the air is wet -- the cloud
     forest on the Andes' Amazon flank, the caps on the Cascades and the
     Southern Alps in the westerlies. Its own cumulus texture, carried with
     the wind, so it seethes rather than sits. */
  if(uWind.x>0.0&&uWind.z>0.0&&up>0.3){
    vec3 po=sphere(lon-W.x*t*0.4/max(cos(lat),0.3),lat-W.y*t*0.4);
    float cu=smoothstep(0.35,0.80,0.6*cn(po*60.0+vec3(4.0,1.0,6.0))+0.4*cn(po*160.0+vec3(2.0,8.0,3.0)));
    float oc=smoothstep(0.3,4.0,up)*mix(0.25,1.0,wet)*(1.0-0.5*uSnowball);
    cloud.x+=uWind.z*oc*(0.1+2.4*cu)*gain;
    cloud.y=max(cloud.y,0.4*oc*cu);
  }
  /* The deck's latitudes, ragged: it breaks into trade cumulus along an
     irregular edge, never along a parallel (a clean band edge read as a ruled
     line from a hemisphere away). */
  float fl=(cn(sphere(lon,lat)*4.0+vec3(7.0,3.0,9.0))-0.5)*9.0+(cn(sphere(lon,lat)*11.0+vec3(2.0,6.0,1.0))-0.5)*4.0;
  float sub=smoothstep(5.0,17.0,al+fl)*(1.0-smoothstep(27.0,42.0,al+0.7*fl));
  if(uWind.x>0.0&&uWind.w>0.0&&sub*(1.0-land)>0.001){
    /* How near the coast upwind of the trades -- land to the EAST -- as a
       smooth falloff over ~20 degrees; the water right at the shore is kept
       clear (the deck forms a little offshore). Skipped wherever no deck is
       possible, which is most of the globe. */
    float cs=1.0/max(0.35,cos(lat));
    // the share of eight points 2.5-20 degrees to the east that are land: a
    // continuous measure of how near (and how big) the upwind coast is
    // (the distances are jittered by a smooth noise of half a step, so the
    // eight thresholds interleave into one gradient instead of drawing eight
    // terraces parallel to the coast)
    float jit=(cn(sphere(lon,lat)*55.0+vec3(8.0,2.0,6.0))-0.5)*2.6+(cn(sphere(lon,lat)*140.0+vec3(1.0,9.0,4.0))-0.5)*1.2;
    // ten points 1.5-19.5 degrees east, spread +-0.8 degrees in latitude too,
    // on a land ramp across the slope: the deck's edge follows the coast's
    // trend, not its every headland (eight sharp samples drew it as a stair)
    float lE=0.0;
    for(int k=0;k<10;k++){
      float fk=float(k);
      lE+=deckLand(uv+vec2((1.5+2.0*fk+jit)/360.0*cs,(fract(fk*0.618)-0.5)*1.6/180.0));
    }
    lE*=0.1;
    float shore=1.0-smoothstep(0.30,0.80,deckLand(uv+vec2(0.6/360.0*cs,0.0)));
    // an irregular outer edge: the deck frays into the open ocean, it is not cut
    float fray=0.65*(cn(sphere(lon,lat)*3.0+vec3(5.0,9.0,2.0))-0.5)+0.35*(cn(sphere(lon,lat)*8.0+vec3(1.0,3.0,7.0))-0.5);
    float sc=(1.0-land)*sub*smoothstep(0.03,0.45,lE+0.30*fray)*shore*(1.0-0.45*uSnowball);
    if(sc>0.001){
      /* Closed cells some 30-50 km across, drifting with the trades that
         carry the deck toward the equator, and thinning to open cells and
         clear rifts toward its outer edge -- the texture a stratocumulus
         sheet has from orbit. */
      vec2 xy=vec2((lon-W.x*t*0.3/max(cos(lat),0.3))*cos(lat),lat-W.y*t*0.3)*270.0;
      float cells=mix(0.62,1.0,cellsAt(xy))*mix(0.80,1.0,cellsAt(xy*0.31+vec2(17.0,5.0)));
      // cells under a pixel are their mean, not a shimmer
      float cfw=max(fwidth(xy.x),fwidth(xy.y));
      cells=mix(cells,0.74,smoothstep(0.35,1.2,cfw));
      float thin=smoothstep(0.20,0.65,cn(sphere(lon,lat)*9.0+vec3(2.0,4.0,8.0)));
      // dense near the coast, breaking into open cells and rifts offshore
      float core=smoothstep(0.10,0.60,lE+0.20*fray);
      cloud.x+=uWind.w*sc*cells*mix(0.6,2.0,core)*mix(0.35,1.0,max(thin,core));
      cloud.y=max(cloud.y,0.25*sc*cells);
    }
  }
  /* SLOW SYNOPTIC EVOLUTION (round 2). The satellite field is one frozen
     day in transport; on its own nothing ever forms or dies. A smooth
     three-dimensional lattice noise drifting through the weather clock
     (about a minute from clear to overcast at a point) gates the optical
     depth, so masses thicken, merge across a clearing and dissolve while
     the fine structure inside them keeps its fronts and spirals. The era
     moves the pattern too, gently, so a running timeline sees the weather
     reorganise rather than jump. A gate, multiplicative and broad -- not a
     second cloud field, and not a crossfade between two. */
  vec3 ps=sphere(lon,lat)*1.35+vec3(t*0.011,t*0.007,t*0.013)+vec3(31.0,17.0,5.0)+uEra*0.0007;
  float syn=0.65*cn(ps)+0.35*cn(ps*2.1+vec3(9.0,3.0,21.0));
  cloud*=mix(0.30,1.35,smoothstep(0.30,0.72,syn));
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
