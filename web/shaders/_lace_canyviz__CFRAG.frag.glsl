precision highp float;
    uniform sampler2D rainA, rainB; uniform float mixf, uTime, uCloud;
    varying vec2 vUv; varying vec3 vN;
    uniform sampler2D uNz;
    ${NZOLD?CN_OLD:CN_NEW}
    float cfb(vec3 p){float s=0.0,a=0.5;for(int i=0;i<5;i++){s+=a*cn(p);p*=2.03;a*=0.5;}return s;}
    void main(){
      float lat=90.0-vUv.y*180.0;
      float al=abs(lat);
      float rain=mix(texture2D(rainA,vUv).r, texture2D(rainB,vUv).r, mixf);
      float itcz=exp(-pow(lat/9.0,2.0));                 // tropical convection band
      float storm=exp(-pow((al-52.0)/13.0,2.0));         // mid-latitude storm tracks
      float subtrop=1.0-0.75*exp(-pow((al-25.0)/10.0,2.0)); // clear subtropical highs
      // Rainfall drives cloudiness, but with a soft CEILING: orographic and
      // monsoon coasts spike the rain field, and feeding that in raw piled the
      // cloud into a solid bright-white glow. This rolls off so heavy rain adds
      // little more than moderate rain.
      float rn=rain/(rain+0.55);                          // 0..~0.9, saturating
      float base=(rn*1.0+itcz*0.42+storm*0.38)*subtrop*uCloud;
      // weather cells, drifting slowly westward. Weight the fBm heavily so the
      // latitude bands read as broken cloud fields, not painted stripes.
      float lon=vUv.x*360.0-180.0+uTime*0.6;
      float cl=cos(radians(lat));
      vec3 d=vec3(cl*cos(radians(lon)), sin(radians(lat)), cl*sin(radians(lon)));
      float tex=cfb(d*3.2)*0.5+cfb(d*7.5+5.0)*0.32+cfb(d*17.0+13.0)*0.18;
      float dens=smoothstep(0.5,1.14, base*0.5+tex*0.9);
      // Self-shadow: an offset noise darkens parts of the deck so the cloud has
      // relief and volume instead of reading as a flat glowing sheet.
      float shade=0.72+0.28*smoothstep(0.25,0.85, cfb(d*10.0+30.0));
      // soften at the limb so the shell has no hard silhouette ring
      float face=smoothstep(0.12,0.5,vN.z);
      gl_FragColor=vec4(vec3(0.90,0.92,0.95)*shade, clamp(dens,0.0,1.0)*0.62*face);
    }
