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
  vec2 cloud;
  if(uCloudDetailBlend>=1.0)cloud=satelliteWeather(lon,lat,gain,dry);
  else{
    cloud=fallbackWeather(lon,lat,gain);
    if(uCloudDetailBlend>0.001)cloud=mix(cloud,satelliteWeather(lon,lat,gain,dry),uCloudDetailBlend);
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
