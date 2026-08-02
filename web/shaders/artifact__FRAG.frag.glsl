precision highp float;
uniform sampler2D elevA, elevB, rainA, rainB;
uniform float mixf, uTemp, uVeg, uIceT, uSeaT, uSchem, uDetail;
uniform vec2 uTexel;
varying vec2 vUv;

const float Z_RANGE=8000.0, RF_MAX=1.3, TEMP_REF=-0.55;

float decElev(float e){ float d=e*2.0-1.0; return sign(d)*d*d*Z_RANGE; }

vec3 dirFromUv(vec2 uv){
  float lon=radians(uv.x*360.0-180.0);
  float lat=radians(90.0-uv.y*180.0);
  return vec3(cos(lat)*cos(lon), sin(lat), cos(lat)*sin(lon));
}
float hash3(vec3 p){ return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453); }
float vnoise3(vec3 p){
  vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
  float a=mix(mix(hash3(i),hash3(i+vec3(1,0,0)),f.x),mix(hash3(i+vec3(0,1,0)),hash3(i+vec3(1,1,0)),f.x),f.y);
  float b=mix(mix(hash3(i+vec3(0,0,1)),hash3(i+vec3(1,0,1)),f.x),mix(hash3(i+vec3(0,1,1)),hash3(i+vec3(1,1,1)),f.x),f.y);
  return mix(a,b,f.z);
}
float fbm3(vec3 p){ float s=0.0,a=0.5; for(int i=0;i<5;i++){ s+=a*vnoise3(p); p*=2.07; a*=0.5; } return s; }

// interpolate the two keyframes, then add procedural micro-relief so the
// upsampled field doesn't read as soft
float elevAt(vec2 uv){
  float z=mix(decElev(texture2D(elevA,uv).r), decElev(texture2D(elevB,uv).r), mixf);
  vec3 d=dirFromUv(uv);
  float n=fbm3(d*260.0)-0.5, n2=fbm3(d*70.0+13.7)-0.5;
  float det=(n*250.0+n2*130.0)*uDetail*clamp(max(z,0.0)/900.0,0.15,1.0);
  return z + (z>0.0 ? det : det*0.10);
}
float rainAt(vec2 uv){
  return mix(texture2D(rainA,uv).r, texture2D(rainB,uv).r, mixf)*RF_MAX;
}

vec3 oceanColour(float z){
  vec3 c=vec3(0.039,0.137,0.251);
  c=mix(c,vec3(0.063,0.212,0.361),smoothstep(-6500.0,-4000.0,z));
  c=mix(c,vec3(0.086,0.314,0.478),smoothstep(-4000.0,-2500.0,z));
  c=mix(c,vec3(0.137,0.435,0.600),smoothstep(-2500.0,-1000.0,z));
  c=mix(c,vec3(0.208,0.549,0.710),smoothstep(-1000.0,-350.0,z));
  c=mix(c,vec3(0.455,0.749,0.824),smoothstep(-350.0,-120.0,z));
  c=mix(c,vec3(0.680,0.878,0.910),smoothstep(-120.0,-15.0,z));
  c=mix(c,vec3(0.804,0.933,0.941),smoothstep(-15.0,0.0,z));
  return c;
}

void main(){
  vec2 uv=vUv;
  float lat=90.0-uv.y*180.0;
  float s2=sin(radians(lat)); s2*=s2;

  float z=elevAt(uv);
  float zp=max(z,0.0);
  float T=(26.0-24.0*s2-26.0*s2*s2*s2)+(uTemp-TEMP_REF)*(4.0+15.0*s2)-zp*0.0058;
  float Rf=rainAt(uv);

  vec3 col;
  if(z<0.0){
    col=oceanColour(z);
  }else{
    float w=clamp((T+6.0)/30.0,0.0,1.0);
    float pet=clamp((T+12.0)/34.0,0.16,1.35);
    float h=clamp(Rf/(0.46*pet),0.0,1.0);
    vec3 dry=mix(vec3(0.592,0.612,0.506), vec3(0.796,0.690,0.514), w);
    vec3 mid=mix(vec3(0.565,0.608,0.322), vec3(0.753,0.659,0.396), w);
    vec3 wet = (w<0.5) ? mix(vec3(0.255,0.333,0.226), vec3(0.298,0.453,0.251), clamp(w*2.0,0.0,1.0))
                       : mix(vec3(0.298,0.453,0.251), vec3(0.169,0.396,0.192), clamp((w-0.5)*2.0,0.0,1.0));
    col = (h<0.45) ? mix(dry,mid,clamp(h/0.45,0.0,1.0))
                   : mix(mid,wet,clamp((h-0.45)/0.55,0.0,1.0));
    float core=clamp((0.30-h)/0.30,0.0,1.0)*clamp((w-0.45)*2.2,0.0,1.0);
    col=mix(col, vec3(0.710,0.604,0.404), core*0.5);
    if(uVeg<0.999){
      vec3 barren=mix(vec3(0.612,0.561,0.482), vec3(0.494,0.447,0.388), clamp(zp/2400.0,0.0,1.0));
      float bf=pow(1.0-uVeg,0.5)*clamp(0.92+0.08*(1.0-h)+zp/9000.0,0.0,1.0);
      col=mix(col,barren,clamp(bf,0.0,1.0));
    }
    float rock=clamp((zp-1700.0)/1500.0,0.0,1.0);
    col=mix(col, mix(vec3(0.545,0.502,0.451), vec3(0.427,0.392,0.345), clamp((zp-2600.0)/1800.0,0.0,1.0)), rock*0.85);
    float snowline=2600.0+190.0*clamp(T,-20.0,30.0);
    col=mix(col, vec3(0.965,0.976,0.988), clamp((zp-snowline)/420.0,0.0,1.0));
  }

  // ice: a continuous ramp so sheets advance and retreat instead of popping
  vec3 d=dirFromUv(uv);
  float lobe=(fbm3(d*9.0)-0.5)*3.4;
  float packn=fbm3(d*16.0+31.7);
  if(z>=0.0){
    col=mix(col, vec3(0.906,0.941,0.965), clamp((uIceT-(T+lobe))/4.5,0.0,1.0));
  }else{
    float sa=clamp((uSeaT-(T+lobe*2.6+(packn-0.5)*5.0))/3.5,0.0,1.0)*clamp((packn-0.30)/0.14,0.0,1.0);
    col=mix(col, vec3(0.812,0.878,0.910)*(0.94+0.10*packn), sa);
  }

  // per-pixel relief from the elevation gradient
  vec2 st=uTexel*0.75;
  float ex1=elevAt(uv+vec2(st.x,0.0)), ex0=elevAt(uv-vec2(st.x,0.0));
  float ey1=elevAt(uv+vec2(0.0,st.y)), ey0=elevAt(uv-vec2(0.0,st.y));
  float coslat=max(cos(radians(lat)),0.08);
  vec3 nrm=normalize(vec3(-(ex1-ex0)/coslat, -(ey1-ey0), 320.0));
  float hs=clamp(dot(nrm, normalize(vec3(-0.55,0.55,0.63))),0.0,1.0);
  float shade=0.70+0.62*hs;
  // Shelves keep their relief, but damp shading toward the abyss: there is no
  // real detail down there and it would only amplify compression blocking.
  float hw=(z<0.0)? mix(0.30,0.04,clamp(-z/2200.0,0.0,1.0)) : 1.0;
  col*=((1.0-hw)+hw*shade);

  if(uSchem>0.001){
    float lum=dot(col,vec3(0.299,0.587,0.114));
    vec3 s=(z<0.0)?vec3(0.16,0.28,0.40):vec3(0.86,0.83,0.74);
    s*=(0.82+0.36*lum);
    col=mix(col,s,uSchem);
  }
  gl_FragColor=vec4(col,1.0);
}
