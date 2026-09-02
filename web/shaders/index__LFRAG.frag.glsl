precision highp float;
uniform sampler2D sheetA, sheetB, elevA, elevB, dispA;
uniform float mixf, uWarp, uMapProj, uMapLon, uSchem;
varying vec2 vUv; varying vec3 vVN;
const float PI=3.14159265359, Z_RANGE=8000.0, V_DEG=12.0;
float decElev(float e){ float d=e*2.0-1.0; return sign(d)*d*d*Z_RANGE; }
bool mollweideInv(vec2 p, out vec2 lonlat){
  float X=(p.x*2.0-1.0)*2.0;
  float Y=(p.y*2.0-1.0);
  if(X*X*0.25 + Y*Y > 1.0) return false;
  float th=asin(clamp(Y,-1.0,1.0));
  float lat=asin(clamp((2.0*th+sin(2.0*th))/PI,-1.0,1.0));
  float c=cos(th);
  if(abs(c)<1e-5) return false;
  float lon=PI*X/(2.0*c);
  if(abs(lon)>PI) return false;
  lonlat=vec2(lon, lat);
  return true;
}
vec2 warpAt(vec2 uv){
  if(uWarp<0.5) return vec2(0.0);
  vec3 d=texture2D(dispA,uv).rgb;
  float dE=(d.r*2.0-1.0)*V_DEG;
  float dN=(d.g*2.0-1.0)*V_DEG;
  float tlat=uv.y*180.0-90.0;
  float cl=max(cos(radians(tlat)),0.15);
  return vec2(dE/(cl*360.0), dN/180.0);
}
void main(){
  vec2 uv=vUv;
  if(uMapProj>0.5){
    vec2 ll;
    if(!mollweideInv(vUv, ll)){ discard; }
    float mlon=mod(ll.x+uMapLon+PI, 2.0*PI)-PI;
    uv=vec2(mlon/(2.0*PI)+0.5, 0.5+ll.y/PI);
  }
  vec2 w=warpAt(uv);
  vec2 ua=uv-mixf*w, ub=uv+(1.0-mixf)*w;
  float h=mix(decElev(texture2D(elevA,ua).r), decElev(texture2D(elevB,ub).r), mixf);
  vec4 cA=texture2D(sheetA,ua), cB=texture2D(sheetB,ub);
  /* THE COASTLINE STAYS SHARP. Where the two sheets disagree about a pixel
     (land in one keyframe, sea in the other) a plain blend would dissolve the
     shoreline across the whole interval. The interpolated height says which
     state the pixel is in NOW; blend only the sheet(s) that agree with it, and
     fall back to the plain blend where neither does (lakes, dry basins). */
  float land = h<0.0 ? 0.0 : 1.0;
  float mA = abs((cA.a>0.75?1.0:0.0)-land)<0.5 ? 1.0 : 0.0;   // sheet alpha: 0.5 water, 1 land
  float mB = abs((cB.a>0.75?1.0:0.0)-land)<0.5 ? 1.0 : 0.0;
  float wA=(1.0-mixf)*mA, wB=mixf*mB, ws=wA+wB;
  vec3 col = ws>1e-4 ? (cA.rgb*wA+cB.rgb*wB)/ws : mix(cA.rgb,cB.rgb,mixf);
  if(uSchem>0.001){
    float lum=dot(col,vec3(0.299,0.587,0.114));
    vec3 sc=(land<0.5)?vec3(0.16,0.28,0.40):vec3(0.86,0.83,0.74);
    sc*=(0.82+0.36*lum);
    col=mix(col,sc,uSchem);
  }
  if(uSchem<0.5 && uMapProj<0.5){
    float sd=dot(normalize(vVN), normalize(vec3(0.54,0.22,0.86)));
    float lit=smoothstep(-0.15,0.20,sd);
    vec3 nightCol=col*0.10+vec3(0.020,0.030,0.060);
    float dusk=exp(-pow(sd/0.12,2.0))*lit;
    col=mix(nightCol, col, lit);
    col=mix(col, col*vec3(1.20,0.86,0.62), dusk*0.35);
    float limb=pow(1.0-clamp(vVN.z,0.0,1.0),3.0);
    col=mix(col, vec3(0.60,0.71,0.86), limb*0.55*(0.30+0.70*lit));
  }
  gl_FragColor=vec4(col,1.0);
}
