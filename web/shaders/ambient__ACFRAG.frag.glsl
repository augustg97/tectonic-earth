precision highp float;
/* THE AMBIENT PAGE'S CLOUDS (2026-09-08): the app's cloud layer (index__CFRAG)
   for a page that ships no fields. The same NASA Blue Marble cloud field
   (NASA/Goddard Space Flight Center, image by Reto Stoeckli) in the same
   coherent transport, the same zonal climatology, synoptic gate and snowball
   damping, lit by the same view-space sun as the ambient globe. But the land
   and wetness that arrange the deck come from the SHEETS' OWN COLOURS -- blue
   is water, green is wet land, tan is dry land, white is ice -- read through a
   coarse mip level, because the page has no elevation or rainfall to read.
   An illustrative arrangement, not the modelled climate the app's clouds
   follow; the register (MODEL-GAPS.md) says so. No shadow pass and no map:
   the page has neither. Derivatives shape the billows, so the material
   enables them. uNz is the noise lattice, spliced at the marker below. */
uniform sampler2D sheetA,sheetB,uNz,uCloudDetail;
uniform float mixf,uWeatherTime,uCloud,uEra,uSnowball;
varying vec2 vUv;varying vec3 vN;
const float PI=3.14159265359;
/*@cnoise*/
vec3 sphere(float lon,float lat){return vec3(cos(lat)*cos(lon),sin(lat),cos(lat)*sin(lon));}
vec2 climateAt(vec2 q){
  q=vec2(fract(q.x),clamp(q.y,0.001,0.999));
  vec3 c=texture2D(sheetA,q,3.0).rgb;
  if(mixf>0.00001)c=mix(c,texture2D(sheetB,q,3.0).rgb,mixf);
  float lum=dot(c,vec3(0.30,0.50,0.20));
  float land=max(smoothstep(-0.02,0.10,c.r-c.b),smoothstep(0.62,0.85,lum));
  float wet=0.12+0.88*smoothstep(0.00,0.16,c.g-c.r);
  return vec2(land,wet*land);
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
  vec2 q=vec2((sourceLon+shear+bend)/(2.0*PI)+0.5,(lat+lift)/PI+0.5);
  float raw=texture2D(uCloudDetail,q).r;
  float broad=texture2D(uCloudDetail,q,2.0).r;
  float d=smoothstep(0.025+dry*0.045,0.98,raw);
  float tau=2.8*pow(d,1.25)*gain;
  float height=pow(max(broad,0.0),1.4)*gain;
  return vec2(tau,height);
}
void main(){
  vec2 uv=vUv;
  float t=uWeatherTime,lat=(uv.y-0.5)*PI,al=abs(degrees(lat));
  float lon=(uv.x-0.5)*2.0*PI;
  vec2 off=vec2((3.0/360.0)/max(0.35,cos(lat)),3.0/180.0);
  vec2 climate=climateAt(uv)*0.5+climateAt(uv+off)*0.25+climateAt(uv-off)*0.25;
  float land=smoothstep(0.08,0.92,climate.x);
  float wet=climate.y/max(climate.x,0.12);
  float dry=land*(1.0-wet);
  float gain=mix(0.94,mix(0.50,1.12,wet),land);
  float zonal=0.80+0.30*exp(-pow(lat/0.16,2.0))+0.25*exp(-pow((al-52.0)/13.0,2.0))-0.30*exp(-pow((al-24.0)/9.0,2.0));
  gain*=zonal*(1.0-0.45*uSnowball);
  vec2 cloud=satelliteWeather(lon,lat,gain,dry);
  vec3 ps=sphere(lon,lat)*1.35+vec3(t*0.011,t*0.007,t*0.013)+vec3(31.0,17.0,5.0)+uEra*0.0007;
  float syn=0.65*cn(ps)+0.35*cn(ps*2.1+vec3(9.0,3.0,21.0));
  cloud*=mix(0.30,1.35,smoothstep(0.30,0.72,syn));
  float mu=max(normalize(vN).z,0.0);
  float path=mix(1.0,1.35,1.0-mu);
  float alpha=1.0-exp(-cloud.x*path);
  float lit=smoothstep(-0.06,0.18,dot(normalize(vN),normalize(vec3(0.54,0.22,0.86))));
  float face=smoothstep(-0.05,0.18,vN.z);
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
