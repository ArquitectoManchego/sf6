import * as THREE from 'three';

export class TurntableStage {
  constructor(scene) {
    this.scene = scene;
    this.rotationSpeed = 0.5; // rad/sec
    this.isRotating = true;
    this.turntableGroup = new THREE.Group();
    this.scene.add(this.turntableGroup);

    this.initStage();
    this.initLighting();
    this.initAmbience();
  }

  initStage() {
    // 1. Stationary Base Platform
    const baseGeo = new THREE.CylinderGeometry(1.65, 1.75, 0.12, 64);
    const baseMat = new THREE.MeshStandardMaterial({
      color: 0x111318,
      metalness: 0.9,
      roughness: 0.3
    });
    this.baseMesh = new THREE.Mesh(baseGeo, baseMat);
    this.baseMesh.position.y = 0.06;
    this.baseMesh.receiveShadow = true;
    this.scene.add(this.baseMesh);

    // 2. Rotating Turntable Disc
    const discGeo = new THREE.CylinderGeometry(1.5, 1.5, 0.08, 64);
    const discMat = new THREE.MeshStandardMaterial({
      color: 0x181c24,
      metalness: 0.85,
      roughness: 0.25
    });
    this.discMesh = new THREE.Mesh(discGeo, discMat);
    this.discMesh.position.y = 0.16;
    this.discMesh.receiveShadow = true;
    this.turntableGroup.add(this.discMesh);

    // 3. Glowing Neon Rim Ring on Turntable (SF6 Cyan & Magenta)
    const rimGeo = new THREE.TorusGeometry(1.48, 0.02, 16, 64);
    this.neonMaterial = new THREE.MeshBasicMaterial({
      color: 0x00f5d4,
      transparent: true,
      opacity: 0.95
    });
    const rimMesh = new THREE.Mesh(rimGeo, this.neonMaterial);
    rimMesh.rotation.x = Math.PI / 2;
    rimMesh.position.y = 0.201;
    this.turntableGroup.add(rimMesh);

    // 4. Center Emissive Combat Logo / Circle
    const innerRingGeo = new THREE.RingGeometry(0.3, 0.34, 32);
    const innerRingMat = new THREE.MeshBasicMaterial({
      color: 0xff006e,
      side: THREE.DoubleSide
    });
    const innerRing = new THREE.Mesh(innerRingGeo, innerRingMat);
    innerRing.rotation.x = -Math.PI / 2;
    innerRing.position.y = 0.202;
    this.turntableGroup.add(innerRing);

    // 5. Floor Hologram Grid (Underneath)
    const floorGeo = new THREE.PlaneGeometry(16, 16);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0x07090e,
      roughness: 0.6,
      metalness: 0.4
    });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = 0;
    floor.receiveShadow = true;
    this.scene.add(floor);

    // Grid Helper
    const grid = new THREE.GridHelper(16, 32, 0x00f5d4, 0x1f2430);
    grid.position.y = 0.005;
    this.scene.add(grid);

    // Concentric holographic circles
    const holoRingGeo = new THREE.RingGeometry(2.2, 2.22, 64);
    const holoRingMat = new THREE.MeshBasicMaterial({
      color: 0x00f5d4,
      transparent: true,
      opacity: 0.25,
      side: THREE.DoubleSide
    });
    const holoRing = new THREE.Mesh(holoRingGeo, holoRingMat);
    holoRing.rotation.x = -Math.PI / 2;
    holoRing.position.y = 0.01;
    this.scene.add(holoRing);

    const outerHoloGeo = new THREE.RingGeometry(3.5, 3.52, 64);
    const outerHoloMat = new THREE.MeshBasicMaterial({
      color: 0xff006e,
      transparent: true,
      opacity: 0.2,
      side: THREE.DoubleSide
    });
    const outerHolo = new THREE.Mesh(outerHoloGeo, outerHoloMat);
    outerHolo.rotation.x = -Math.PI / 2;
    outerHolo.position.y = 0.01;
    this.scene.add(outerHolo);
  }

  initLighting() {
    // Key Light (Warm high-intensity studio spotlight)
    this.keyLight = new THREE.SpotLight(0xffffff, 4.5);
    this.keyLight.position.set(3, 5, 4);
    this.keyLight.angle = Math.PI / 4;
    this.keyLight.penumbra = 0.5;
    this.keyLight.castShadow = true;
    this.keyLight.shadow.mapSize.width = 2048;
    this.keyLight.shadow.mapSize.height = 2048;
    this.keyLight.shadow.camera.near = 1;
    this.keyLight.shadow.camera.far = 12;
    this.keyLight.shadow.bias = -0.0008;
    this.scene.add(this.keyLight);

    // Fill Light (Soft cool light)
    this.fillLight = new THREE.DirectionalLight(0xa0c4ff, 1.8);
    this.fillLight.position.set(-4, 3, 2);
    this.scene.add(this.fillLight);

    // Back / Rim Light 1 (Street Fighter 6 Vibrant Magenta Rim)
    this.rimLight1 = new THREE.SpotLight(0xff007f, 6.0);
    this.rimLight1.position.set(-3, 3.5, -4);
    this.rimLight1.angle = Math.PI / 3;
    this.rimLight1.penumbra = 0.4;
    this.scene.add(this.rimLight1);

    // Back / Rim Light 2 (Street Fighter 6 Electric Cyan Rim)
    this.rimLight2 = new THREE.SpotLight(0x00f5d4, 6.0);
    this.rimLight2.position.set(3.5, 3.5, -3.5);
    this.rimLight2.angle = Math.PI / 3;
    this.rimLight2.penumbra = 0.4;
    this.scene.add(this.rimLight2);

    // Underlight from turntable
    this.stageUpLight = new THREE.PointLight(0x00f5d4, 1.8, 4);
    this.stageUpLight.position.set(0, 0.25, 0);
    this.scene.add(this.stageUpLight);

    // Ambient light
    const ambient = new THREE.AmbientLight(0x1a1e28, 0.8);
    this.scene.add(ambient);
  }

  initAmbience() {
    // Floating dust/ember particles in the locker spotlight
    const particleCount = 70;
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const speeds = new Float32Array(particleCount);

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3 + 0] = (Math.random() - 0.5) * 4.5;
      positions[i * 3 + 1] = Math.random() * 3.5 + 0.2;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 4.5;
      speeds[i] = 0.2 + Math.random() * 0.4;
    }

    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.dustSpeeds = speeds;

    const mat = new THREE.PointsMaterial({
      color: 0x00f5d4,
      size: 0.035,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending
    });

    this.dustParticles = new THREE.Points(geo, mat);
    this.scene.add(this.dustParticles);
  }

  setNeonColor(hexColor) {
    this.neonMaterial.color.set(hexColor);
    this.stageUpLight.color.set(hexColor);
  }

  update(delta) {
    // Rotate turntable if active
    if (this.isRotating) {
      this.turntableGroup.rotation.y += this.rotationSpeed * delta;
    }

    // Animate ambient dust particles floating
    if (this.dustParticles) {
      const positions = this.dustParticles.geometry.attributes.position.array;
      for (let i = 0; i < this.dustSpeeds.length; i++) {
        positions[i * 3 + 1] += this.dustSpeeds[i] * delta * 0.3;
        if (positions[i * 3 + 1] > 3.8) {
          positions[i * 3 + 1] = 0.2;
        }
      }
      this.dustParticles.geometry.attributes.position.needsUpdate = true;
    }
  }
}
