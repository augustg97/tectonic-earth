precision highp float;
/* THE AMBIENT GLOBE (ambient.html, WP-10 plan C; moved here from the page on
   2026-09-08 so check_shader.py validates it). Two sheets carried toward each
   other on the displacement warp -- the same contract as the app's lite
   material, without the height field: a coastline that moves within an
   interval dissolves over that interval, which at ambient speeds is a few
   seconds and below notice -- a terminator fixed in view space, and a limb
   haze. */
uniform sampler2D sheetA, sheetB, dispA; uniform float mixf, uWarp;
varying vec2 vUv; varying vec3 vVN;
const float V_DEG=12.0;
vec2 warpAt(vec2 uv){
  if(uWarp<0.5) return vec2(0.0);
  vec3 d=texture2D(dispA,uv).rgb;
  float dE=(d.r*2.0-1.0)*V_DEG, dN=(d.g*2.0-1.0)*V_DEG;
  float cl=max(cos(radians(uv.y*180.0-90.0)),0.15);
  return vec2(dE/(cl*360.0), dN/180.0);
}
void main(){
  vec2 w=warpAt(vUv);
  vec4 cA=texture2D(sheetA,vUv-mixf*w), cB=texture2D(sheetB,vUv+(1.0-mixf)*w);
  vec3 col=mix(cA.rgb,cB.rgb,mixf);
  float sd=dot(normalize(vVN), normalize(vec3(0.54,0.22,0.86)));
  float lit=smoothstep(-0.15,0.20,sd);
  vec3 nightCol=col*0.10+vec3(0.020,0.030,0.060);
  float dusk=exp(-pow(sd/0.12,2.0))*lit;
  col=mix(nightCol, col, lit);
  col=mix(col, col*vec3(1.20,0.86,0.62), dusk*0.35);
  float limb=pow(1.0-clamp(vVN.z,0.0,1.0),3.0);
  col=mix(col, vec3(0.60,0.71,0.86), limb*0.55*(0.30+0.70*lit));
  gl_FragColor=vec4(col,1.0);
}
