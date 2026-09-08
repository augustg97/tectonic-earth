/* THE AMBIENT CLOUD SHELL (ambient.html): the app's cloud vertex contract. */
varying vec2 vUv; varying vec3 vN;
void main(){ vUv=uv; vN=normalize(normalMatrix*normal); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }
