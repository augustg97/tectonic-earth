varying vec2 vUv; varying vec3 vVN;
uniform sampler2D elevA, elevB, dispA;
uniform float mixf, uDisp, uMapProj, uWarp;
float vDec(float e){ float d=e*2.0-1.0; return sign(d)*d*d*8000.0; }
void main(){
  vUv=uv; vVN=normalize(normalMatrix*normal);
  vec3 p=position;
  if(uDisp>0.0 && uMapProj<0.5){
    vec2 w=vec2(0.0);
    if(uWarp>0.5){
      vec3 d=texture2D(dispA,uv).rgb;
      float cl=max(cos(radians(uv.y*180.0-90.0)),0.15);
      w=vec2((d.r*2.0-1.0)*12.0/(cl*360.0), (d.g*2.0-1.0)*12.0/180.0);
    }
    float z=mix(vDec(texture2D(elevA,uv-mixf*w).r),
                vDec(texture2D(elevB,uv+(1.0-mixf)*w).r), mixf);
    p+=normal*z*uDisp;
  }
  gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);
} 
