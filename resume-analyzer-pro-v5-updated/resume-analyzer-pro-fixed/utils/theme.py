# ============================================================
# utils/theme.py — Global CSS + Three.js 3D Scene injection
# ============================================================
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

_CSS_PATH = Path(__file__).parent.parent / "assets" / "styles.css"


def load_theme():
    """Inject global CSS into every page."""
    if _CSS_PATH.exists():
        css = _CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ── Three.js Particle Sphere — called on landing + dashboard ──
_THREEJS_HERO = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background: transparent; overflow: hidden; }
  canvas { display: block; width: 100% !important; height: 100% !important; }
  #container {
    position: relative; width: 100%; height: 340px;
    background: linear-gradient(160deg,#03020e 0%,#07051a 50%,#030216 100%);
    border-radius: 20px;
    border: 1px solid rgba(139,92,246,0.2);
    overflow: hidden;
  }
  #overlay {
    position: absolute; inset: 0; z-index: 10;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    pointer-events: none;
    background:
      radial-gradient(ellipse 600px 300px at 50% 50%, rgba(139,92,246,0.06), transparent);
  }
  .title-3d {
    font-family: 'Orbitron', monospace;
    font-size: clamp(1.6rem, 4vw, 3.2rem);
    font-weight: 900;
    background: linear-gradient(135deg, #fff 0%, #c4b5fd 25%, #67e8f9 55%, #e879f9 80%, #fff 100%);
    background-size: 300% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: shimmer 5s linear infinite, dropIn .8s cubic-bezier(.16,1,.3,1) both;
    letter-spacing: 0.04em;
    filter: drop-shadow(0 0 30px rgba(139,92,246,0.6));
    margin-bottom: 0.6rem;
  }
  .subtitle-3d {
    font-family: 'Inter', sans-serif;
    font-size: clamp(0.8rem, 1.5vw, 1rem);
    color: rgba(200,192,255,0.75);
    letter-spacing: 0.12em; text-transform: uppercase;
    animation: dropIn 0.9s .15s cubic-bezier(.16,1,.3,1) both;
  }
  .tag-row {
    display: flex; gap: 10px; margin-top: 1.2rem;
    animation: dropIn 1s .3s cubic-bezier(.16,1,.3,1) both;
  }
  .pill {
    padding: 5px 14px; border-radius: 999px; font-size: 0.7rem; font-weight: 700;
    font-family: 'Orbitron', monospace; letter-spacing: 0.06em; text-transform: uppercase;
  }
  .pill-v { background:rgba(139,92,246,.18); border:1px solid rgba(139,92,246,.5); color:#c4b5fd; }
  .pill-c { background:rgba(34,211,238,.12); border:1px solid rgba(34,211,238,.4); color:#67e8f9; }
  .pill-m { background:rgba(232,121,249,.12); border:1px solid rgba(232,121,249,.4); color:#e879f9; }
  @keyframes shimmer { 0%{background-position:0%} 100%{background-position:300%} }
  @keyframes dropIn  { from{opacity:0;transform:translateY(-16px)} to{opacity:1;transform:none} }
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Inter:wght@400&display=swap');
</style>
</head>
<body>
<div id="container">
  <canvas id="c"></canvas>
  <div id="overlay">
    <div class="title-3d">AI RESUME ANALYZER</div>
    <div class="subtitle-3d">ATS · Rewrite · Optimize · Export</div>
    <div class="tag-row">
      <span class="pill pill-v">⚡ Local NLP</span>
      <span class="pill pill-c">🎯 6D Scoring</span>
      <span class="pill pill-m">🚀 PDF Export</span>
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const canvas = document.getElementById('c');
  const cont   = document.getElementById('container');

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(cont.clientWidth, cont.clientHeight);
  renderer.setClearColor(0x000000, 0);

  const scene  = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, cont.clientWidth / cont.clientHeight, 0.1, 200);
  camera.position.set(0, 0, 28);

  // ── Lights
  scene.add(new THREE.AmbientLight(0xffffff, 0.2));
  const pl1 = new THREE.PointLight(0x8b5cf6, 2, 60); pl1.position.set(-10, 10, 10);
  const pl2 = new THREE.PointLight(0x22d3ee, 1.5, 60); pl2.position.set(10, -8, 8);
  const pl3 = new THREE.PointLight(0xe879f9, 1, 50); pl3.position.set(0, -12, 5);
  scene.add(pl1, pl2, pl3);

  // ── Particle field
  const PARTS = 700;
  const pPos = new Float32Array(PARTS * 3);
  const pCol = new Float32Array(PARTS * 3);
  const COLS = [
    [0.545, 0.361, 0.965],  // violet
    [0.133, 0.827, 0.933],  // cyan
    [0.910, 0.475, 0.976],  // magenta
    [0.984, 0.749, 0.141],  // amber
    [1, 1, 1],               // white
  ];
  for (let i = 0; i < PARTS; i++) {
    const r = 18 + Math.random() * 10;
    const theta = Math.random() * Math.PI * 2;
    const phi   = Math.acos(2 * Math.random() - 1);
    pPos[i*3]   = r * Math.sin(phi) * Math.cos(theta);
    pPos[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
    pPos[i*3+2] = r * Math.cos(phi);
    const c = COLS[Math.floor(Math.random() * COLS.length)];
    pCol[i*3] = c[0]; pCol[i*3+1] = c[1]; pCol[i*3+2] = c[2];
  }
  const pGeo = new THREE.BufferGeometry();
  pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
  pGeo.setAttribute('color', new THREE.BufferAttribute(pCol, 3));
  const pMat = new THREE.PointsMaterial({ size: 0.12, vertexColors: true, transparent: true, opacity: 0.85 });
  const particles = new THREE.Points(pGeo, pMat);
  scene.add(particles);

  // ── Wireframe Icosahedron (large, central)
  function makeWire(geo, color, opacity) {
    const wf = new THREE.WireframeGeometry(geo);
    return new THREE.LineSegments(wf,
      new THREE.LineBasicMaterial({ color, transparent: true, opacity, linewidth: 1 }));
  }
  const ico = makeWire(new THREE.IcosahedronGeometry(6, 1), 0x8b5cf6, 0.22);
  scene.add(ico);

  const oct = makeWire(new THREE.OctahedronGeometry(4, 0), 0x22d3ee, 0.28);
  oct.position.set(10, -3, -5);
  scene.add(oct);

  const tor = makeWire(new THREE.TorusGeometry(3.5, 0.4, 12, 40), 0xe879f9, 0.2);
  tor.position.set(-9, 4, -3);
  scene.add(tor);

  const tet = makeWire(new THREE.TetrahedronGeometry(3, 0), 0xfbbf24, 0.25);
  tet.position.set(0, 9, -8);
  scene.add(tet);

  // ── Inner glowing sphere
  const sphereGeo = new THREE.SphereGeometry(4, 32, 32);
  const sphereMat = new THREE.MeshPhongMaterial({
    color: 0x8b5cf6, transparent: true, opacity: 0.06,
    emissive: 0x4c1d95, emissiveIntensity: 0.4, wireframe: false
  });
  scene.add(new THREE.Mesh(sphereGeo, sphereMat));

  // ── Ring geometry
  const ringGeo = new THREE.TorusGeometry(8, 0.05, 4, 100);
  const ringMat = new THREE.MeshBasicMaterial({ color: 0x8b5cf6, transparent: true, opacity: 0.3 });
  const ring1 = new THREE.Mesh(ringGeo, ringMat);
  ring1.rotation.x = Math.PI / 4;
  const ring2 = new THREE.Mesh(
    new THREE.TorusGeometry(11, 0.04, 4, 120),
    new THREE.MeshBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: 0.18 })
  );
  ring2.rotation.x = -Math.PI / 3; ring2.rotation.y = Math.PI / 6;
  scene.add(ring1, ring2);

  // ── Mouse parallax
  let mx = 0, my = 0;
  document.addEventListener('mousemove', e => {
    mx = (e.clientX / window.innerWidth  - 0.5) * 2;
    my = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  // ── Animate
  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();

    particles.rotation.y = t * 0.03;
    particles.rotation.x = t * 0.01;

    ico.rotation.x = t * 0.18; ico.rotation.y = t * 0.12;
    oct.rotation.x = t * 0.22; oct.rotation.z = t * 0.14;
    tor.rotation.x = t * 0.10; tor.rotation.y = t * 0.20;
    tet.rotation.y = t * 0.28; tet.rotation.z = t * 0.16;

    ring1.rotation.z = t * 0.08;
    ring2.rotation.z = -t * 0.06;

    // Pulse light
    pl1.intensity = 1.5 + Math.sin(t * 1.2) * 0.5;
    pl2.intensity = 1.2 + Math.cos(t * 0.9) * 0.4;
    pl3.intensity = 0.8 + Math.sin(t * 1.5 + 1) * 0.3;

    // Camera parallax
    camera.position.x += (mx * 2 - camera.position.x) * 0.04;
    camera.position.y += (-my * 1.5 - camera.position.y) * 0.04;
    camera.lookAt(0, 0, 0);

    renderer.render(scene, camera);
  }
  animate();

  // Resize
  window.addEventListener('resize', () => {
    const w = cont.clientWidth, h = cont.clientHeight;
    camera.aspect = w / h; camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  });
})();
</script>
</body>
</html>
"""

_THREEJS_MINI = """
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin:0; padding:0; }
  body { background: transparent; overflow: hidden; }
  canvas { display: block; }
  #c { width:100%; height:120px; display:block; }
</style>
</head>
<body>
<canvas id="c"></canvas>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const canvas = document.getElementById('c');
  const W = window.innerWidth, H = 120;
  const renderer = new THREE.WebGLRenderer({canvas, antialias:true, alpha:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  renderer.setSize(W, H); renderer.setClearColor(0,0);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, W/H, 0.1, 100);
  camera.position.z = 12;

  // mini particle ring
  const N = 200;
  const pos = new Float32Array(N*3), col = new Float32Array(N*3);
  const COLS=[[0.545,0.361,0.965],[0.133,0.827,0.933],[0.910,0.475,0.976]];
  for(let i=0;i<N;i++){
    const a=Math.random()*Math.PI*2, r=6+Math.random()*6;
    pos[i*3]=r*Math.cos(a); pos[i*3+1]=(Math.random()-.5)*4; pos[i*3+2]=r*Math.sin(a);
    const c=COLS[i%3]; col[i*3]=c[0];col[i*3+1]=c[1];col[i*3+2]=c[2];
  }
  const geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.BufferAttribute(pos,3));
  geo.setAttribute('color',new THREE.BufferAttribute(col,3));
  const pts=new THREE.Points(geo,new THREE.PointsMaterial({size:0.1,vertexColors:true,transparent:true,opacity:.8}));
  scene.add(pts);

  const wire=new THREE.LineSegments(
    new THREE.WireframeGeometry(new THREE.IcosahedronGeometry(2,0)),
    new THREE.LineBasicMaterial({color:0x8b5cf6,transparent:true,opacity:.3})
  );
  scene.add(wire);

  const clock=new THREE.Clock();
  function animate(){ requestAnimationFrame(animate);
    const t=clock.getElapsedTime();
    pts.rotation.y=t*.04; wire.rotation.x=t*.2; wire.rotation.y=t*.15;
    renderer.render(scene,camera);
  }
  animate();
})();
</script>
</body>
</html>
"""


def render_3d_hero():
    """Full 3D Three.js hero — use on landing page and logged-in home."""
    components.html(_THREEJS_HERO, height=340, scrolling=False)


def render_3d_mini_banner():
    """Compact 3D banner — use as page header accent."""
    components.html(_THREEJS_MINI, height=120, scrolling=False)
