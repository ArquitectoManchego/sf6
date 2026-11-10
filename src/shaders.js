import * as THREE from 'three';

// Procedural Normal Map for Muscle Definition and Vascularity
export function createMuscleNormalMap() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  // Neutral normal map base: RGB (128, 128, 255)
  ctx.fillStyle = 'rgb(128, 128, 255)';
  ctx.fillRect(0, 0, 512, 512);

  // Draw abdominal 6-pack cuts
  ctx.strokeStyle = 'rgb(100, 110, 220)';
  ctx.lineWidth = 6;
  ctx.lineCap = 'round';

  // Center linea alba
  ctx.beginPath();
  ctx.moveTo(256, 120);
  ctx.lineTo(256, 380);
  ctx.stroke();

  // Horizontal rectus intersections
  for (let y of [180, 240, 300]) {
    ctx.beginPath();
    ctx.moveTo(200, y);
    ctx.quadraticCurveTo(256, y + 10, 312, y);
    ctx.stroke();
  }

  // Oblique / serratus cuts
  for (let i = 0; i < 4; i++) {
    const y = 160 + i * 35;
    ctx.beginPath();
    ctx.moveTo(170, y);
    ctx.lineTo(210, y + 25);
    ctx.moveTo(342, y);
    ctx.lineTo(302, y + 25);
    ctx.stroke();
  }

  // Pec lines
  ctx.beginPath();
  ctx.arc(210, 140, 45, 0.2 * Math.PI, 0.8 * Math.PI);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(302, 140, 45, 0.2 * Math.PI, 0.8 * Math.PI);
  ctx.stroke();

  // Vascular veins (biceps / forearms)
  ctx.strokeStyle = 'rgb(140, 140, 245)';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(80, 200);
  ctx.bezierCurveTo(95, 230, 85, 260, 100, 300);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(432, 200);
  ctx.bezierCurveTo(417, 230, 427, 260, 412, 300);
  ctx.stroke();

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  return texture;
}

// 3-Tone Gradient Map for Cel-Shading (Toon look)
export function createToonGradientMap() {
  const canvas = document.createElement('canvas');
  canvas.width = 4;
  canvas.height = 1;
  const ctx = canvas.getContext('2d');
  
  // 4 steps of lighting quantization
  const colors = ['#2b2b36', '#686882', '#b8b8cc', '#ffffff'];
  colors.forEach((col, idx) => {
    ctx.fillStyle = col;
    ctx.fillRect(idx, 0, 1, 1);
  });

  const gradientMap = new THREE.CanvasTexture(canvas);
  gradientMap.minFilter = THREE.NearestFilter;
  gradientMap.magFilter = THREE.NearestFilter;
  return gradientMap;
}

// Drive Impact VFX Particle System (SF6 signature paint explosion)
export class DriveImpactFX {
  constructor(scene) {
    this.scene = scene;
    this.particles = [];
    this.active = false;
    this.group = new THREE.Group();
    this.scene.add(this.group);

    // SF6 color palette: Hot Pink, Electric Cyan, Neon Yellow, Royal Violet
    this.colors = [
      new THREE.Color('#ff006e'),
      new THREE.Color('#00f5d4'),
      new THREE.Color('#fee440'),
      new THREE.Color('#7b2cbf'),
      new THREE.Color('#ff5400')
    ];

    // Splatter texture generated dynamically
    this.splatterTex = this.createSplatterTexture();
  }

  createSplatterTexture() {
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = 'rgba(0,0,0,0)';
    ctx.fillRect(0, 0, 128, 128);

    // Ink splash shape
    ctx.fillStyle = '#ffffff';
    ctx.beginPath();
    ctx.arc(64, 64, 28, 0, Math.PI * 2);
    ctx.fill();

    // Spikes / drips
    for (let i = 0; i < 12; i++) {
      const angle = (i / 12) * Math.PI * 2 + Math.random() * 0.2;
      const len = 35 + Math.random() * 25;
      const rad = 6 + Math.random() * 8;
      const x = 64 + Math.cos(angle) * len;
      const y = 64 + Math.sin(angle) * len;
      ctx.beginPath();
      ctx.arc(x, y, rad, 0, Math.PI * 2);
      ctx.fill();

      // Connecting stroke
      ctx.lineWidth = 7;
      ctx.strokeStyle = '#ffffff';
      ctx.beginPath();
      ctx.moveTo(64, 64);
      ctx.lineTo(x, y);
      ctx.stroke();
    }

    const tex = new THREE.CanvasTexture(canvas);
    return tex;
  }

  trigger(position = new THREE.Vector3(0, 1.2, 0.4)) {
    // Clear any remaining
    this.clear();

    const count = 45;
    for (let i = 0; i < count; i++) {
      const mat = new THREE.SpriteMaterial({
        map: this.splatterTex,
        color: this.colors[Math.floor(Math.random() * this.colors.length)],
        transparent: true,
        opacity: 0.95,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      });

      const sprite = new THREE.Sprite(mat);
      sprite.position.copy(position);
      
      const scale = 0.3 + Math.random() * 0.6;
      sprite.scale.set(scale, scale, 1);

      // Random spherical velocity with outward blast
      const phi = Math.random() * Math.PI * 2;
      const theta = Math.random() * Math.PI;
      const speed = 2.5 + Math.random() * 4.0;
      
      const velocity = new THREE.Vector3(
        Math.sin(theta) * Math.cos(phi) * speed,
        Math.cos(theta) * speed * 0.8 + 1.2,
        Math.sin(theta) * Math.sin(phi) * speed
      );

      this.particles.push({
        mesh: sprite,
        velocity: velocity,
        life: 1.0,
        decay: 0.8 + Math.random() * 0.6,
        rotSpeed: (Math.random() - 0.5) * 8
      });

      this.group.add(sprite);
    }

    // Add a shockwave ring
    const ringGeo = new THREE.RingGeometry(0.1, 0.4, 32);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x00f5d4,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.position.copy(position);
    ring.rotation.x = -Math.PI / 2;
    this.group.add(ring);
    this.shockwave = { mesh: ring, scale: 0.2, life: 1.0 };

    this.active = true;
  }

  update(delta) {
    if (!this.active) return;

    let aliveCount = 0;

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      if (p.life > 0) {
        aliveCount++;
        p.life -= p.decay * delta;
        p.mesh.position.addScaledVector(p.velocity, delta);
        p.velocity.y -= 3.5 * delta; // Gravity
        p.mesh.material.opacity = Math.max(0, p.life);
        p.mesh.material.rotation += p.rotSpeed * delta;
        const currentScale = (1.0 + (1.0 - p.life) * 0.8) * (p.mesh.scale.x);
      } else {
        p.mesh.visible = false;
      }
    }

    if (this.shockwave && this.shockwave.life > 0) {
      this.shockwave.life -= 2.0 * delta;
      this.shockwave.scale += 8.0 * delta;
      this.shockwave.mesh.scale.set(this.shockwave.scale, this.shockwave.scale, 1);
      this.shockwave.mesh.material.opacity = Math.max(0, this.shockwave.life);
      aliveCount++;
    }

    if (aliveCount === 0) {
      this.clear();
      this.active = false;
    }
  }

  clear() {
    while (this.group.children.length > 0) {
      const child = this.group.children[0];
      this.group.remove(child);
      if (child.geometry) child.geometry.dispose();
      if (child.material) child.material.dispose();
    }
    this.particles = [];
    this.shockwave = null;
  }
}
