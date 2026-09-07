precision highp float;
/* THE TIME PREVIEW (the Atlas port, 2026-09-07). A 4096x2048 atlas holds a
   256x128 thumbnail of every keyframe's shipped world sheet, sixteen to a
   row in timeline order. While a seek's full-resolution fields are still
   arriving, the globe and the map draw the requested age from the two
   thumbnails it sits between instead of leaving the previous world on
   screen under a new age. It is loading feedback and nothing more: no
   height, no interval warp, no procedural detail, and it is replaced by the
   terrain shader the moment the requested pair is resident. UVs clamp to
   the cell's texel centres so a bilinear tap can never read the neighbouring
   keyframe, and the texture carries no mip chain for the same reason. The
   terminator, limb and schematic tint are the lite material's own, so the
   handoff to the settled picture changes detail, not light. */
uniform sampler2D uPreview;
uniform vec2 uFrames, uPreviewTexel;
uniform float mixf, uMapProj, uMapLon, uSchem;
varying vec2 vUv; varying vec3 vVN;
const float PI=3.14159265359;
vec3 frameColor(float frame, vec2 uv){
  // the bitmap is decoded pre-flipped, so row 0 of the atlas is the TOP of the texture
  vec2 cell=vec2(mod(frame,16.0), 15.0-floor(frame/16.0));
  vec2 local=clamp(vec2(fract(uv.x),uv.y), uPreviewTexel*8.0, vec2(1.0)-uPreviewTexel*8.0);
  return texture2D(uPreview,(cell+local)/16.0).rgb;
}
void main(){
  vec2 uv=vUv;
  if(uMapProj>0.5){
    float X=(uv.x*2.0-1.0)*2.0, Y=uv.y*2.0-1.0;
    if(X*X*0.25+Y*Y>1.0) discard;
    float th=asin(clamp(Y,-1.0,1.0)), c=cos(th);
    if(abs(c)<0.00001) discard;
    float lon=PI*X/(2.0*c);
    if(abs(lon)>PI) discard;
    float lat=asin(clamp((2.0*th+sin(2.0*th))/PI,-1.0,1.0));
    uv=vec2(fract((lon+uMapLon)/(2.0*PI)+0.5), 0.5+lat/PI);
  }
  vec3 col=mix(frameColor(uFrames.x,uv), frameColor(uFrames.y,uv), mixf);
  if(uSchem>0.001){
    float lum=dot(col,vec3(0.299,0.587,0.114));
    // no height field here: a thumbnail's blue reads as water for the tint
    float land=step(col.b, max(col.r,col.g)*1.05);
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
