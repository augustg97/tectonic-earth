varying vec2 vUv; varying vec3 vVN;
void main(){ vUv=uv; vVN=normalize(normalMatrix*normal);
  gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}
