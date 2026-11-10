import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { VRMLoaderPlugin, VRMUtils } from '@pixiv/three-vrm';
import { createMuscleNormalMap, createToonGradientMap } from './shaders.js';
import { AnatomicalDeformerAI } from './deformer.js';

export class CharacterController {
  constructor(scene, turntableGroup) {
    this.scene = scene;
    this.turntableGroup = turntableGroup;
    this.characterGroup = new THREE.Group();
    this.turntableGroup.add(this.characterGroup);

    // Motor de Deformación Anatómica Adaptativo con IA
    this.deformer = new AnatomicalDeformerAI(this);

    // Initial Customization State (like Street Fighter 6 World Tour Avatar Editor)
    this.params = {
      // Body Proportions
      height: 1.0,
      shoulderWidth: 1.0,
      chestDepth: 1.0,
      bustSize: 1.0,
      bustCup: 1.0,         // Cup projection & shape
      waistWidth: 1.0,
      hipWidth: 1.0,
      bodyFat: 0.15,        // 0.0 (Ultra lean) to 1.0 (Higher body fat)
      gluteSize: 1.1,
      gluteShape: 'heart',  // 'heart', 'teardrop', 'oval', 'round'
      thighWidth: 1.15,     // Chun-Li style athletic thighs
      calfWidth: 1.05,
      muscularity: 0.7,     // Normal map intensity & muscle definition
      
      // Aesthetics
      characterPreset: 'custom', // 'ryu', 'chunli', 'cammy', 'juri', 'custom'
      hairStyle: 'spiky',        // 'spiky', 'buns', 'beret', 'sleek'
      skinColor: '#e0a98b',
      hairColor: '#1a1820',
      outfitType: 'gi',          // 'gi', 'qipao', 'cammy', 'urban', 'cyber'
      shaderMode: 'pbr',         // 'pbr', 'toon'
      outfitPrimary: '#d62828',
      outfitSecondary: '#111318',
      accentColor: '#f77f00'
    };

    // Textures & Shaders
    this.muscleNormalMap = createMuscleNormalMap();
    this.toonGradientMap = createToonGradientMap();

    // Model nodes reference
    this.nodes = {};
    this.materials = {};
    this.outfitMeshes = [];
    this.hairMeshes = [];

    // External model animation mixer & VRM physics
    this.externalMixer = null;
    this.externalModel = null;
    this.currentVRM = null;
    this.isUsingExternalModel = false;

    // Load Official Capcom SF6 Chun-Li Organic PBR 4K Model by default on startup
    this.loadExternalModel('/models/chunli_sf6_animated.glb');
  }

  buildCharacter() {
    this.isUsingExternalModel = false;
    this.currentVRM = null;
    // Clear external model if any
    if (this.externalModel) {
      this.characterGroup.remove(this.externalModel);
      this.externalModel = null;
      this.externalMixer = null;
    }

    // Clear existing
    while (this.characterGroup.children.length > 0) {
      this.characterGroup.remove(this.characterGroup.children[0]);
    }
    this.nodes = {};
    this.outfitMeshes = [];
    this.hairMeshes = [];

    // Base materials
    this.initMaterials();

    // 1. Root and Pelvis/Hips
    const hipsGroup = new THREE.Group();
    hipsGroup.position.set(0, 0.95, 0);
    this.characterGroup.add(hipsGroup);
    this.nodes.hips = hipsGroup;

    // Pelvis core geometry
    const pelvisGeo = new THREE.CylinderGeometry(0.18, 0.16, 0.18, 24);
    const pelvisMesh = new THREE.Mesh(pelvisGeo, this.materials.skin);
    pelvisMesh.castShadow = true;
    pelvisMesh.receiveShadow = true;
    hipsGroup.add(pelvisMesh);
    this.nodes.pelvisMesh = pelvisMesh;

    // 2. Glutes (Parametric high-density meshes for Heart, Teardrop, Oval, Round shapes)
    const gluteLeftGroup = new THREE.Group();
    gluteLeftGroup.position.set(-0.10, -0.04, -0.07);
    hipsGroup.add(gluteLeftGroup);
    this.nodes.gluteLeft = gluteLeftGroup;

    const gluteRightGroup = new THREE.Group();
    gluteRightGroup.position.set(0.10, -0.04, -0.07);
    hipsGroup.add(gluteRightGroup);
    this.nodes.gluteRight = gluteRightGroup;

    // Glute Geometries (subdivided sphere)
    const gluteGeoL = new THREE.SphereGeometry(0.15, 32, 24);
    const gluteMeshL = new THREE.Mesh(gluteGeoL, this.materials.skin);
    gluteMeshL.castShadow = true;
    gluteLeftGroup.add(gluteMeshL);
    this.nodes.gluteMeshL = gluteMeshL;

    const gluteGeoR = new THREE.SphereGeometry(0.15, 32, 24);
    const gluteMeshR = new THREE.Mesh(gluteGeoR, this.materials.skin);
    gluteMeshR.castShadow = true;
    gluteRightGroup.add(gluteMeshR);
    this.nodes.gluteMeshR = gluteMeshR;

    // 3. Spine / Waist / Abdomen
    const spineGroup = new THREE.Group();
    spineGroup.position.set(0, 0.12, 0);
    hipsGroup.add(spineGroup);
    this.nodes.spine = spineGroup;

    const waistGeo = new THREE.CylinderGeometry(0.17, 0.18, 0.2, 24);
    const waistMesh = new THREE.Mesh(waistGeo, this.materials.skin);
    waistMesh.position.set(0, 0.08, 0);
    waistMesh.castShadow = true;
    waistMesh.receiveShadow = true;
    spineGroup.add(waistMesh);
    this.nodes.waistMesh = waistMesh;

    // 4. Chest & Shoulders
    const chestGroup = new THREE.Group();
    chestGroup.position.set(0, 0.22, 0);
    spineGroup.add(chestGroup);
    this.nodes.chest = chestGroup;

    const ribcageGeo = new THREE.CylinderGeometry(0.21, 0.17, 0.24, 24);
    const ribcageMesh = new THREE.Mesh(ribcageGeo, this.materials.skin);
    ribcageMesh.position.set(0, 0.10, 0);
    ribcageMesh.castShadow = true;
    ribcageMesh.receiveShadow = true;
    chestGroup.add(ribcageMesh);
    this.nodes.ribcageMesh = ribcageMesh;

    // Breasts / Bust (Parametric Cup projection & spacing)
    const breastLGroup = new THREE.Group();
    breastLGroup.position.set(-0.09, 0.10, 0.11);
    chestGroup.add(breastLGroup);
    this.nodes.breastL = breastLGroup;

    const breastRGroup = new THREE.Group();
    breastRGroup.position.set(0.09, 0.10, 0.11);
    chestGroup.add(breastRGroup);
    this.nodes.breastR = breastRGroup;

    const breastGeoL = new THREE.SphereGeometry(0.12, 32, 24);
    const breastMeshL = new THREE.Mesh(breastGeoL, this.materials.skin);
    breastMeshL.castShadow = true;
    breastLGroup.add(breastMeshL);
    this.nodes.breastMeshL = breastMeshL;

    const breastGeoR = new THREE.SphereGeometry(0.12, 32, 24);
    const breastMeshR = new THREE.Mesh(breastGeoR, this.materials.skin);
    breastMeshR.castShadow = true;
    breastRGroup.add(breastMeshR);
    this.nodes.breastMeshR = breastMeshR;

    // 5. Neck and Head
    const neckGroup = new THREE.Group();
    neckGroup.position.set(0, 0.25, 0);
    chestGroup.add(neckGroup);
    this.nodes.neck = neckGroup;

    const neckGeo = new THREE.CylinderGeometry(0.075, 0.09, 0.12, 20);
    const neckMesh = new THREE.Mesh(neckGeo, this.materials.skin);
    neckMesh.position.set(0, 0.05, 0);
    neckMesh.castShadow = true;
    neckGroup.add(neckMesh);

    const headGroup = new THREE.Group();
    headGroup.position.set(0, 0.14, 0.02);
    neckGroup.add(headGroup);
    this.nodes.head = headGroup;

    // Stylized Head
    const headGeo = new THREE.SphereGeometry(0.14, 32, 28);
    const headMesh = new THREE.Mesh(headGeo, this.materials.skin);
    headMesh.scale.set(0.9, 1.15, 0.95);
    headMesh.castShadow = true;
    headGroup.add(headMesh);

    // Build Hair / Headwear
    this.buildHair();

    // 6. Arms & Shoulders (Left & Right)
    this.nodes.armL = this.createArm(-1, chestGroup);
    this.nodes.armR = this.createArm(1, chestGroup);

    // 7. Legs (Thighs, Calves, Feet)
    this.nodes.legL = this.createLeg(-1, hipsGroup);
    this.nodes.legR = this.createLeg(1, hipsGroup);

    // 8. Build Outfits
    this.buildOutfits();

    // Calibrar Deformador IA sobre personaje procedural
    this.deformer.calibrate(this.characterGroup, 'Malla Paramétrica SF6', false);
  }

  buildHair() {
    // Clear old hair meshes
    this.hairMeshes.forEach(m => {
      if (m.parent) m.parent.remove(m);
    });
    this.hairMeshes = [];

    const style = this.params.hairStyle;
    const headGroup = this.nodes.head;

    if (style === 'buns') {
      // Chun-Li: Iconic Ox-Horn Hair Buns (Chignons) with Silk Ribbon Wraps
      // Base hair cap
      const capGeo = new THREE.SphereGeometry(0.155, 24, 20);
      const capMesh = new THREE.Mesh(capGeo, this.materials.hair);
      capMesh.scale.set(0.96, 1.1, 1.05);
      capMesh.position.set(0, 0.04, -0.02);
      capMesh.castShadow = true;
      headGroup.add(capMesh);
      this.hairMeshes.push(capMesh);

      // Left Bun
      const bunLGeo = new THREE.SphereGeometry(0.085, 20, 20);
      const bunL = new THREE.Mesh(bunLGeo, this.materials.hair);
      bunL.position.set(-0.16, 0.14, -0.02);
      bunL.castShadow = true;
      headGroup.add(bunL);
      this.hairMeshes.push(bunL);

      // Left Silk Wrap (White ribbon)
      const wrapLGeo = new THREE.TorusGeometry(0.088, 0.02, 12, 24);
      const wrapL = new THREE.Mesh(wrapLGeo, this.materials.accent);
      wrapL.position.copy(bunL.position);
      wrapL.rotation.y = Math.PI / 4;
      headGroup.add(wrapL);
      this.hairMeshes.push(wrapL);

      // Right Bun
      const bunRGeo = new THREE.SphereGeometry(0.085, 20, 20);
      const bunR = new THREE.Mesh(bunRGeo, this.materials.hair);
      bunR.position.set(0.16, 0.14, -0.02);
      bunR.castShadow = true;
      headGroup.add(bunR);
      this.hairMeshes.push(bunR);

      // Right Silk Wrap
      const wrapRGeo = new THREE.TorusGeometry(0.088, 0.02, 12, 24);
      const wrapR = new THREE.Mesh(wrapRGeo, this.materials.accent);
      wrapR.position.copy(bunR.position);
      wrapR.rotation.y = -Math.PI / 4;
      headGroup.add(wrapR);
      this.hairMeshes.push(wrapR);

    } else if (style === 'beret') {
      // Cammy: Delta Red Military Beret & Blonde Braid Ponytail
      const beretGeo = new THREE.CylinderGeometry(0.17, 0.13, 0.08, 24);
      const beret = new THREE.Mesh(beretGeo, this.materials.accent);
      beret.position.set(0.03, 0.15, -0.02);
      beret.rotation.z = -0.3;
      beret.rotation.x = -0.1;
      beret.castShadow = true;
      headGroup.add(beret);
      this.hairMeshes.push(beret);

      // Blonde hair under beret
      const hairGeo = new THREE.SphereGeometry(0.15, 20, 16);
      const hairMesh = new THREE.Mesh(hairGeo, this.materials.hair);
      hairMesh.position.set(0, 0.04, -0.02);
      hairMesh.castShadow = true;
      headGroup.add(hairMesh);
      this.hairMeshes.push(hairMesh);

      // Long Braid Ponytail hanging back
      const braidGeo = new THREE.CylinderGeometry(0.04, 0.02, 0.45, 12);
      const braid = new THREE.Mesh(braidGeo, this.materials.hair);
      braid.position.set(-0.06, -0.08, -0.16);
      braid.rotation.x = -0.25;
      braid.castShadow = true;
      headGroup.add(braid);
      this.hairMeshes.push(braid);

    } else {
      // Ryu / Default Spiky Brawler Cut + Martial Arts Headband
      const hairGeo = new THREE.SphereGeometry(0.155, 24, 20);
      const hairMesh = new THREE.Mesh(hairGeo, this.materials.hair);
      hairMesh.scale.set(0.96, 1.1, 1.05);
      hairMesh.position.set(0, 0.04, -0.02);
      hairMesh.castShadow = true;
      headGroup.add(hairMesh);
      this.hairMeshes.push(hairMesh);

      // Headband
      const bandGeo = new THREE.TorusGeometry(0.15, 0.025, 12, 32);
      const bandMesh = new THREE.Mesh(bandGeo, this.materials.accent);
      bandMesh.rotation.x = Math.PI / 2 + 0.1;
      bandMesh.position.set(0, 0.05, 0.01);
      bandMesh.castShadow = true;
      headGroup.add(bandMesh);
      this.hairMeshes.push(bandMesh);

      // Headband tails (fluttering in the wind)
      const tailGeo = new THREE.BoxGeometry(0.05, 0.28, 0.02);
      const tailMesh = new THREE.Mesh(tailGeo, this.materials.accent);
      tailMesh.position.set(0.04, 0.02, -0.22);
      tailMesh.rotation.x = 0.4;
      headGroup.add(tailMesh);
      this.hairMeshes.push(tailMesh);
    }
  }

  createArm(side, parentChest) {
    const shoulderGroup = new THREE.Group();
    shoulderGroup.position.set(side * 0.24, 0.18, 0);
    parentChest.add(shoulderGroup);

    // Deltoid
    const deltoidGeo = new THREE.SphereGeometry(0.095, 20, 16);
    const deltoidMesh = new THREE.Mesh(deltoidGeo, this.materials.skin);
    deltoidMesh.castShadow = true;
    shoulderGroup.add(deltoidMesh);

    // Upper Arm
    const upperArmGroup = new THREE.Group();
    upperArmGroup.position.set(side * 0.04, -0.04, 0);
    shoulderGroup.add(upperArmGroup);

    const bicepGeo = new THREE.CylinderGeometry(0.075, 0.065, 0.28, 20);
    const bicepMesh = new THREE.Mesh(bicepGeo, this.materials.skin);
    bicepMesh.position.set(0, -0.14, 0);
    bicepMesh.castShadow = true;
    upperArmGroup.add(bicepMesh);

    // Forearm & Hand
    const forearmGroup = new THREE.Group();
    forearmGroup.position.set(0, -0.28, 0);
    upperArmGroup.add(forearmGroup);

    const forearmGeo = new THREE.CylinderGeometry(0.068, 0.055, 0.26, 20);
    const forearmMesh = new THREE.Mesh(forearmGeo, this.materials.skin);
    forearmMesh.position.set(0, -0.13, 0);
    forearmMesh.castShadow = true;
    forearmGroup.add(forearmMesh);

    // Fighting hand fist / wrap
    const handGeo = new THREE.BoxGeometry(0.09, 0.10, 0.07);
    const handMesh = new THREE.Mesh(handGeo, this.materials.accent);
    handMesh.position.set(0, -0.29, 0);
    handMesh.castShadow = true;
    forearmGroup.add(handMesh);

    return {
      shoulderGroup,
      deltoidMesh,
      upperArmGroup,
      bicepMesh,
      forearmGroup,
      forearmMesh,
      handMesh
    };
  }

  createLeg(side, parentHips) {
    const hipJoint = new THREE.Group();
    hipJoint.position.set(side * 0.14, -0.08, 0);
    parentHips.add(hipJoint);

    // Thigh (Athletic Chun-Li / SF6 style)
    const thighGroup = new THREE.Group();
    hipJoint.add(thighGroup);

    const thighGeo = new THREE.CylinderGeometry(0.13, 0.095, 0.44, 24);
    const thighMesh = new THREE.Mesh(thighGeo, this.materials.skin);
    thighMesh.position.set(0, -0.22, 0);
    thighMesh.castShadow = true;
    thighMesh.receiveShadow = true;
    thighGroup.add(thighMesh);

    // Knee & Calf (Gemelos)
    const calfGroup = new THREE.Group();
    calfGroup.position.set(0, -0.44, 0);
    thighGroup.add(calfGroup);

    const calfGeo = new THREE.CylinderGeometry(0.098, 0.062, 0.42, 24);
    const calfMesh = new THREE.Mesh(calfGeo, this.materials.skin);
    calfMesh.position.set(0, -0.21, -0.01);
    calfMesh.castShadow = true;
    calfMesh.receiveShadow = true;
    calfGroup.add(calfMesh);

    // Foot / Sneaker / Combat Boot
    const footGeo = new THREE.BoxGeometry(0.10, 0.08, 0.22);
    const footMesh = new THREE.Mesh(footGeo, this.materials.outfitSecondary);
    footMesh.position.set(0, -0.44, 0.05);
    footMesh.castShadow = true;
    calfGroup.add(footMesh);

    return {
      hipJoint,
      thighGroup,
      thighMesh,
      calfGroup,
      calfMesh,
      footMesh
    };
  }

  initMaterials() {
    const isToon = this.params.shaderMode === 'toon';

    if (isToon) {
      this.materials.skin = new THREE.MeshToonMaterial({
        color: new THREE.Color(this.params.skinColor),
        gradientMap: this.toonGradientMap,
        normalMap: this.muscleNormalMap,
        normalScale: new THREE.Vector2(this.params.muscularity * 1.5, this.params.muscularity * 1.5)
      });
      this.materials.hair = new THREE.MeshToonMaterial({
        color: new THREE.Color(this.params.hairColor),
        gradientMap: this.toonGradientMap
      });
      this.materials.outfitPrimary = new THREE.MeshToonMaterial({
        color: new THREE.Color(this.params.outfitPrimary),
        gradientMap: this.toonGradientMap
      });
      this.materials.outfitSecondary = new THREE.MeshToonMaterial({
        color: new THREE.Color(this.params.outfitSecondary),
        gradientMap: this.toonGradientMap
      });
      this.materials.accent = new THREE.MeshToonMaterial({
        color: new THREE.Color(this.params.accentColor),
        gradientMap: this.toonGradientMap
      });
    } else {
      // RE Engine Stylized PBR Look
      this.materials.skin = new THREE.MeshStandardMaterial({
        color: new THREE.Color(this.params.skinColor),
        roughness: 0.45,
        metalness: 0.05,
        normalMap: this.muscleNormalMap,
        normalScale: new THREE.Vector2(this.params.muscularity, this.params.muscularity)
      });
      this.materials.hair = new THREE.MeshStandardMaterial({
        color: new THREE.Color(this.params.hairColor),
        roughness: 0.6,
        metalness: 0.1
      });
      this.materials.outfitPrimary = new THREE.MeshStandardMaterial({
        color: new THREE.Color(this.params.outfitPrimary),
        roughness: 0.45,
        metalness: 0.2
      });
      this.materials.outfitSecondary = new THREE.MeshStandardMaterial({
        color: new THREE.Color(this.params.outfitSecondary),
        roughness: 0.35,
        metalness: 0.4
      });
      this.materials.accent = new THREE.MeshStandardMaterial({
        color: new THREE.Color(this.params.accentColor),
        roughness: 0.3,
        metalness: 0.6
      });
    }
  }

  buildOutfits() {
    // Clear old outfit meshes
    this.outfitMeshes.forEach(mesh => {
      if (mesh.parent) mesh.parent.remove(mesh);
    });
    this.outfitMeshes = [];

    const type = this.params.outfitType;

    if (type === 'gi') {
      // 1. Street Fighter Martial Arts Gi (Ryu/Ken style)
      const giTopGeo = new THREE.CylinderGeometry(0.24, 0.20, 0.32, 24, 1, true);
      const giTop = new THREE.Mesh(giTopGeo, this.materials.outfitPrimary);
      giTop.position.set(0, 0.08, 0);
      giTop.castShadow = true;
      this.nodes.chest.add(giTop);
      this.outfitMeshes.push(giTop);

      // Black Belt (Cinturón Negro)
      const beltGeo = new THREE.TorusGeometry(0.21, 0.035, 12, 32);
      const belt = new THREE.Mesh(beltGeo, this.materials.outfitSecondary);
      belt.rotation.x = Math.PI / 2;
      belt.position.set(0, 0.02, 0);
      this.nodes.spine.add(belt);
      this.outfitMeshes.push(belt);

      // Belt knot ribbon
      const knotGeo = new THREE.BoxGeometry(0.06, 0.22, 0.04);
      const knot = new THREE.Mesh(knotGeo, this.materials.outfitSecondary);
      knot.position.set(0.05, -0.1, 0.21);
      knot.rotation.z = -0.2;
      this.nodes.spine.add(knot);
      this.outfitMeshes.push(knot);

      // Gi Pants
      const pantLGeo = new THREE.CylinderGeometry(0.15, 0.12, 0.50, 24);
      const pantL = new THREE.Mesh(pantLGeo, this.materials.outfitPrimary);
      pantL.position.set(0, -0.23, 0);
      this.nodes.legL.thighGroup.add(pantL);
      this.outfitMeshes.push(pantL);

      const pantRGeo = new THREE.CylinderGeometry(0.15, 0.12, 0.50, 24);
      const pantR = new THREE.Mesh(pantRGeo, this.materials.outfitPrimary);
      pantR.position.set(0, -0.23, 0);
      this.nodes.legR.thighGroup.add(pantR);
      this.outfitMeshes.push(pantR);

    } else if (type === 'qipao') {
      // 2. Chun-Li Iconic Blue Qipao Dress / Leotard with Gold Trim
      const qipaoTopGeo = new THREE.CylinderGeometry(0.23, 0.18, 0.28, 24);
      const qipaoTop = new THREE.Mesh(qipaoTopGeo, this.materials.outfitPrimary);
      qipaoTop.position.set(0, 0.10, 0);
      qipaoTop.castShadow = true;
      this.nodes.chest.add(qipaoTop);
      this.outfitMeshes.push(qipaoTop);

      // Golden Sash / Obi Belt
      const sashGeo = new THREE.TorusGeometry(0.19, 0.03, 12, 32);
      const sash = new THREE.Mesh(sashGeo, this.materials.accent);
      sash.rotation.x = Math.PI / 2;
      sash.position.set(0, 0.02, 0);
      this.nodes.spine.add(sash);
      this.outfitMeshes.push(sash);

      // Qipao side flaps
      const flapLGeo = new THREE.BoxGeometry(0.04, 0.32, 0.24);
      const flapL = new THREE.Mesh(flapLGeo, this.materials.outfitPrimary);
      flapL.position.set(-0.16, -0.06, 0);
      this.nodes.hips.add(flapL);
      this.outfitMeshes.push(flapL);

      const flapRGeo = new THREE.BoxGeometry(0.04, 0.32, 0.24);
      const flapR = new THREE.Mesh(flapRGeo, this.materials.outfitPrimary);
      flapR.position.set(0.16, -0.06, 0);
      this.nodes.hips.add(flapR);
      this.outfitMeshes.push(flapR);

      // Spiked Wrist Cuffs (Chun-Li signature bracelets)
      const cuffLGeo = new THREE.TorusGeometry(0.08, 0.025, 8, 16);
      const cuffL = new THREE.Mesh(cuffLGeo, this.materials.outfitSecondary);
      cuffL.rotation.x = Math.PI / 2;
      cuffL.position.set(0, -0.24, 0);
      this.nodes.armL.forearmGroup.add(cuffL);
      this.outfitMeshes.push(cuffL);

      const cuffRGeo = new THREE.TorusGeometry(0.08, 0.025, 8, 16);
      const cuffR = new THREE.Mesh(cuffRGeo, this.materials.outfitSecondary);
      cuffR.rotation.x = Math.PI / 2;
      cuffR.position.set(0, -0.24, 0);
      this.nodes.armR.forearmGroup.add(cuffR);
      this.outfitMeshes.push(cuffR);

    } else if (type === 'cammy') {
      // 3. Cammy Delta Red Combat Leotard & Gauntlets
      const leotardGeo = new THREE.CylinderGeometry(0.22, 0.17, 0.32, 24);
      const leotard = new THREE.Mesh(leotardGeo, this.materials.outfitPrimary);
      leotard.position.set(0, 0.08, 0);
      leotard.castShadow = true;
      this.nodes.chest.add(leotard);
      this.outfitMeshes.push(leotard);

      // Red Combat Gauntlets on Forearms
      const gauntletLGeo = new THREE.CylinderGeometry(0.075, 0.065, 0.22, 16);
      const gauntletL = new THREE.Mesh(gauntletLGeo, this.materials.accent);
      gauntletL.position.set(0, -0.16, 0);
      this.nodes.armL.forearmGroup.add(gauntletL);
      this.outfitMeshes.push(gauntletL);

      const gauntletRGeo = new THREE.CylinderGeometry(0.075, 0.065, 0.22, 16);
      const gauntletR = new THREE.Mesh(gauntletRGeo, this.materials.accent);
      gauntletR.position.set(0, -0.16, 0);
      this.nodes.armR.forearmGroup.add(gauntletR);
      this.outfitMeshes.push(gauntletR);

    } else if (type === 'urban') {
      // 4. Fortnite Tactical / SF6 World Tour Urban Wear
      const cropGeo = new THREE.CylinderGeometry(0.22, 0.18, 0.18, 24);
      const crop = new THREE.Mesh(cropGeo, this.materials.outfitSecondary);
      crop.position.set(0, 0.14, 0);
      this.nodes.chest.add(crop);
      this.outfitMeshes.push(crop);

      const cargoLGeo = new THREE.CylinderGeometry(0.155, 0.11, 0.46, 24);
      const cargoL = new THREE.Mesh(cargoLGeo, this.materials.outfitPrimary);
      cargoL.position.set(0, -0.22, 0);
      this.nodes.legL.thighGroup.add(cargoL);
      this.outfitMeshes.push(cargoL);

      const cargoRGeo = new THREE.CylinderGeometry(0.155, 0.11, 0.46, 24);
      const cargoR = new THREE.Mesh(cargoRGeo, this.materials.outfitPrimary);
      cargoR.position.set(0, -0.22, 0);
      this.nodes.legR.thighGroup.add(cargoR);
      this.outfitMeshes.push(cargoR);

      const strapGeo = new THREE.TorusGeometry(0.14, 0.02, 8, 24);
      const strap = new THREE.Mesh(strapGeo, this.materials.outfitSecondary);
      strap.rotation.x = Math.PI / 2;
      strap.position.set(0, -0.2, 0);
      this.nodes.legR.thighGroup.add(strap);
      this.outfitMeshes.push(strap);

    } else if (type === 'cyber') {
      // 5. Cyber Battle Suit
      const plateGeo = new THREE.BoxGeometry(0.36, 0.26, 0.18);
      const plate = new THREE.Mesh(plateGeo, this.materials.outfitSecondary);
      plate.position.set(0, 0.12, 0.05);
      this.nodes.chest.add(plate);
      this.outfitMeshes.push(plate);

      const padLGeo = new THREE.BoxGeometry(0.16, 0.12, 0.16);
      const padL = new THREE.Mesh(padLGeo, this.materials.outfitPrimary);
      padL.position.set(-0.02, 0.06, 0);
      this.nodes.armL.shoulderGroup.add(padL);
      this.outfitMeshes.push(padL);

      const padRGeo = new THREE.BoxGeometry(0.16, 0.12, 0.16);
      const padR = new THREE.Mesh(padRGeo, this.materials.outfitPrimary);
      padR.position.set(0.02, 0.06, 0);
      this.nodes.armR.shoulderGroup.add(padR);
      this.outfitMeshes.push(padR);

      const visorGeo = new THREE.BoxGeometry(0.24, 0.06, 0.12);
      const visor = new THREE.Mesh(visorGeo, this.materials.accent);
      visor.position.set(0, 0.02, 0.13);
      this.nodes.head.add(visor);
      this.outfitMeshes.push(visor);
    }
  }

  // Street Fighter 6 Icon Presets
  loadFighterPreset(fighter) {
    if (fighter === 'ryu') {
      this.params = {
        ...this.params,
        characterPreset: 'ryu',
        hairStyle: 'spiky',
        skinColor: '#dca587',
        hairColor: '#2b231c',
        outfitType: 'gi',
        outfitPrimary: '#eae8e4',    // White Gi
        outfitSecondary: '#111318',  // Black Belt
        accentColor: '#d62828',      // Red Headband & Gloves
        shoulderWidth: 1.35,
        chestDepth: 1.25,
        waistWidth: 1.05,
        hipWidth: 1.0,
        bodyFat: 0.10,
        gluteSize: 1.05,
        gluteShape: 'oval',
        thighWidth: 1.25,
        calfWidth: 1.20,
        muscularity: 0.90,
        height: 1.05
      };
    } else if (fighter === 'chunli') {
      this.params = {
        ...this.params,
        characterPreset: 'chunli',
        hairStyle: 'buns',           // Ox-Horn Buns with white silk
        skinColor: '#f3cbb5',
        hairColor: '#1a1820',
        outfitType: 'qipao',         // Blue Qipao
        outfitPrimary: '#0d47a1',    // Royal Blue
        outfitSecondary: '#111318',  // Black tights / spiked cuffs
        accentColor: '#ffd700',      // Golden silk embroidery
        shoulderWidth: 0.95,
        chestDepth: 1.05,
        bustSize: 1.25,
        bustCup: 1.20,
        waistWidth: 0.82,            // Hourglass wasp waist
        hipWidth: 1.35,
        bodyFat: 0.14,
        gluteSize: 1.45,             // Famous Chun-Li glutes
        gluteShape: 'heart',         // Heart shape silhouette
        thighWidth: 1.62,            // Thunder thighs
        calfWidth: 1.28,
        muscularity: 0.75,
        height: 1.0
      };
    } else if (fighter === 'cammy') {
      this.params = {
        ...this.params,
        characterPreset: 'cammy',
        hairStyle: 'beret',          // Delta Red Beret & Blonde Braid
        skinColor: '#f6d5c2',
        hairColor: '#eed782',        // Blonde
        outfitType: 'cammy',         // Delta Red Leotard
        outfitPrimary: '#2e7d32',    // Combat Green
        outfitSecondary: '#1b1f24',
        accentColor: '#b71c1c',      // Crimson Beret & Gauntlets
        shoulderWidth: 1.05,
        chestDepth: 1.0,
        bustSize: 1.10,
        bustCup: 1.15,
        waistWidth: 0.85,
        hipWidth: 1.18,
        bodyFat: 0.08,               // Ultra athletic
        gluteSize: 1.35,
        gluteShape: 'teardrop',      // Athletic teardrop
        thighWidth: 1.35,
        calfWidth: 1.15,
        muscularity: 0.85,
        height: 0.98
      };
    } else if (fighter === 'juri') {
      this.params = {
        ...this.params,
        characterPreset: 'juri',
        hairStyle: 'buns',
        skinColor: '#ebd0be',
        hairColor: '#121116',
        outfitType: 'urban',
        outfitPrimary: '#ff007f',    // Hot Pink Spider Accent
        outfitSecondary: '#12141c',  // Black Harness
        accentColor: '#7b2cbf',      // Purple
        shoulderWidth: 0.95,
        chestDepth: 0.98,
        bustSize: 1.05,
        bustCup: 1.10,
        waistWidth: 0.82,
        hipWidth: 1.20,
        bodyFat: 0.10,
        gluteSize: 1.25,
        gluteShape: 'heart',
        thighWidth: 1.28,
        calfWidth: 1.10,
        muscularity: 0.65,
        height: 1.0
      };
    }

    this.buildCharacter();
    this.applyCustomization();
  }

  // Real-Time Parametric Morphing Engine
  applyCustomization() {
    if (this.isUsingExternalModel && this.deformer) {
      this.deformer.apply();
      return;
    }
    const p = this.params;

    // 1. Overall Height
    this.characterGroup.scale.set(1.0, p.height, 1.0);

    // 2. Shoulders & Deltoids Width
    if (this.nodes.armL && this.nodes.armR) {
      this.nodes.armL.shoulderGroup.position.x = -0.24 * p.shoulderWidth;
      this.nodes.armR.shoulderGroup.position.x = 0.24 * p.shoulderWidth;
      
      const deltScale = 0.8 + p.shoulderWidth * 0.3;
      this.nodes.armL.deltoidMesh.scale.set(deltScale, 1.0, deltScale);
      this.nodes.armR.deltoidMesh.scale.set(deltScale, 1.0, deltScale);
    }

    // 3. Chest Depth & Ribcage
    if (this.nodes.ribcageMesh) {
      this.nodes.ribcageMesh.scale.set(p.shoulderWidth * 0.95, 1.0, p.chestDepth);
    }

    // 4. Bust Size, Spacing & Cup Projection (Morph deformation)
    if (this.nodes.breastL && this.nodes.breastR) {
      const bustScale = p.bustSize;
      const cupProj = p.bustCup;

      this.nodes.breastMeshL.scale.set(bustScale, bustScale * 0.95, bustScale * cupProj);
      this.nodes.breastMeshR.scale.set(bustScale, bustScale * 0.95, bustScale * cupProj);

      const spacing = 0.09 + (bustScale - 1.0) * 0.03;
      this.nodes.breastL.position.x = -spacing;
      this.nodes.breastR.position.x = spacing;
      this.nodes.breastL.rotation.y = 0.15;
      this.nodes.breastR.rotation.y = -0.15;
    }

    // 5. Waist Width & Body Fat %
    if (this.nodes.waistMesh) {
      const fatFactor = 1.0 + p.bodyFat * 0.4;
      this.nodes.waistMesh.scale.set(p.waistWidth * fatFactor, 1.0, (p.waistWidth * 0.9) * fatFactor);
    }

    // 6. Hip Width
    if (this.nodes.pelvisMesh) {
      this.nodes.pelvisMesh.scale.set(p.hipWidth, 1.0, p.hipWidth * 0.95);
      this.nodes.legL.hipJoint.position.x = -0.14 * p.hipWidth;
      this.nodes.legR.hipJoint.position.x = 0.14 * p.hipWidth;
    }

    // 7. Glutes Size & Advanced Shape Morphs (Oval, Teardrop, Heart, Round)
    if (this.nodes.gluteMeshL && this.nodes.gluteMeshR) {
      const gSize = p.gluteSize;
      let scaleX = gSize;
      let scaleY = gSize;
      let scaleZ = gSize * 1.15;
      let rotZ = 0;
      let offsetY = -0.04;
      let offsetX = 0.10 * p.hipWidth;

      if (p.gluteShape === 'oval') {
        scaleX *= 0.88;
        scaleY *= 1.25;
        scaleZ *= 1.05;
        rotZ = 0.05;
      } else if (p.gluteShape === 'teardrop') {
        scaleX *= 1.05;
        scaleY *= 1.15;
        scaleZ *= 1.25;
        offsetY = -0.06;
        rotZ = 0.12;
      } else if (p.gluteShape === 'heart') {
        scaleX *= 1.22;
        scaleY *= 1.05;
        scaleZ *= 1.18;
        offsetY = -0.02;
        rotZ = 0.22;
      } else {
        scaleX *= 1.1;
        scaleY *= 1.1;
        scaleZ *= 1.2;
        rotZ = 0.0;
      }

      this.nodes.gluteLeft.position.x = -offsetX;
      this.nodes.gluteRight.position.x = offsetX;
      this.nodes.gluteLeft.position.y = offsetY;
      this.nodes.gluteRight.position.y = offsetY;

      this.nodes.gluteMeshL.scale.set(scaleX, scaleY, scaleZ);
      this.nodes.gluteMeshR.scale.set(scaleX, scaleY, scaleZ);

      this.nodes.gluteMeshL.rotation.z = rotZ;
      this.nodes.gluteMeshR.rotation.z = -rotZ;
    }

    // 8. Thigh Width & Calves (Gemelos)
    if (this.nodes.legL && this.nodes.legR) {
      const thighS = p.thighWidth;
      this.nodes.legL.thighMesh.scale.set(thighS, 1.0, thighS * 1.08);
      this.nodes.legR.thighMesh.scale.set(thighS, 1.0, thighS * 1.08);

      const calfS = p.calfWidth;
      this.nodes.legL.calfMesh.scale.set(calfS, 1.0, calfS * 1.12);
      this.nodes.legR.calfMesh.scale.set(calfS, 1.0, calfS * 1.12);
    }

    // 9. Muscularity Shader Normal Scale & Body Fat Abdomen
    if (this.materials.skin && this.materials.skin.normalScale) {
      const effectiveMuscularity = Math.max(0.1, p.muscularity * (1.2 - p.bodyFat * 0.8));
      this.materials.skin.normalScale.set(effectiveMuscularity, effectiveMuscularity);
    }

    // 10. Update Material Colors
    if (this.materials.skin) this.materials.skin.color.set(p.skinColor);
    if (this.materials.hair) this.materials.hair.color.set(p.hairColor);
    if (this.materials.outfitPrimary) this.materials.outfitPrimary.color.set(p.outfitPrimary);
    if (this.materials.outfitSecondary) this.materials.outfitSecondary.color.set(p.outfitSecondary);
    if (this.materials.accent) this.materials.accent.color.set(p.accentColor);
  }

  setParam(key, value) {
    this.params[key] = value;
    if (this.deformer) {
      this.deformer.needsVertexUpdate = true;
    }
    if (key === 'outfitType') {
      this.buildOutfits();
    } else if (key === 'hairStyle') {
      this.buildHair();
    } else if (key === 'shaderMode') {
      this.initMaterials();
      this.buildHair();
      this.buildOutfits();
    }
    this.applyCustomization();
  }

  // Load external custom GLB/GLTF/VRM model (e.g. VRM avatars, Soldier, Michelle, Xbot)
  loadExternalModel(fileUrl, onLoaded, onError) {
    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));

    // Cache-buster to bypass any browser HTTP cache and immediately load the fresh 3D mesh
    const finalUrl = (fileUrl.startsWith('blob:') || fileUrl.includes('?')) ? fileUrl : `${fileUrl}?v=sf6_mesh_v2`;

    loader.load(
      finalUrl,
      (gltf) => {
        // Clear procedural character & previous models
        while (this.characterGroup.children.length > 0) {
          this.characterGroup.remove(this.characterGroup.children[0]);
        }
        this.nodes = {};
        this.isUsingExternalModel = true;

        // 1. Check if this is a VRM Avatar (with SpringBones, Colliders, and Expressions)
        if (gltf.userData.vrm) {
          const vrm = gltf.userData.vrm;
          this.currentVRM = vrm;
          this.externalModel = vrm.scene;

          VRMUtils.removeUnnecessaryVertices(gltf.scene);
          VRMUtils.removeUnnecessaryJoints(gltf.scene);

          // VRM models face +Z, rotate 180 degrees to face the turntable camera
          vrm.scene.rotation.y = Math.PI;

          vrm.scene.traverse((child) => {
            if (child.isMesh) {
              child.castShadow = true;
              child.receiveShadow = true;
            }
          });

          // Fit scale on turntable
          const box = new THREE.Box3().setFromObject(vrm.scene);
          const size = box.getSize(new THREE.Vector3());
          const maxDim = Math.max(size.x, size.y, size.z);
          const targetHeight = 1.75;
          const scale = targetHeight / (maxDim || 1);
          vrm.scene.scale.set(scale, scale, scale);

          box.setFromObject(vrm.scene);
          vrm.scene.position.y = -box.min.y + 0.20;

          this.characterGroup.add(vrm.scene);

          this.externalAnimations = gltf.animations || [];
          this.externalMixer = null;

          // Calibrar Deformador IA sobre avatar VRM
          this.deformer.calibrate(vrm.scene, fileUrl, true);

          if (onLoaded) onLoaded(gltf, vrm);
          return;
        }

        // 2. Standard GLB / GLTF (Soldier, Michelle, Xbot, etc.)
        this.currentVRM = null;
        this.externalModel = gltf.scene;

        this.externalModel.traverse((child) => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
            if (child.material) {
              const mats = Array.isArray(child.material) ? child.material : [child.material];
              mats.forEach(m => {
                m.envMapIntensity = 1.2;
                if (m.transparent || m.opacity < 1.0) {
                  m.alphaTest = 0.5;
                  m.depthWrite = true;
                }
              });
            }
          }
        });
        
        // Auto-fit scale and position on turntable (Mesh-based bounding box)
        const box = new THREE.Box3();
        let meshCount = 0;
        this.externalModel.traverse((child) => {
          if (child.isMesh && child.geometry) {
            box.expandByObject(child);
            meshCount++;
          }
        });
        if (meshCount === 0) box.setFromObject(this.externalModel);

        const size = box.getSize(new THREE.Vector3());
        const modelHeight = size.y > 0.1 ? size.y : Math.max(size.x, size.y, size.z);
        const targetHeight = 1.78;
        const scale = modelHeight > 0.05 ? targetHeight / modelHeight : 1.0;
        this.externalModel.scale.set(scale, scale, scale);

        // Center on turntable floor
        box.setFromObject(this.externalModel);
        this.baseGroundY = -box.min.y + 0.02;
        this.externalModel.position.set(0, this.baseGroundY, 0);

        this.characterGroup.add(this.externalModel);

        // Setup AnimationMixer
        this.externalAnimations = gltf.animations || [];
        this.currentAction = null;
        this.isActionLooping = true;

        if (this.externalAnimations.length > 0) {
          this.externalMixer = new THREE.AnimationMixer(this.externalModel);

          // Unified mixer event listener for combo chaining and returning to idle
          this.externalMixer.addEventListener('finished', (e) => {
            if (e.action === this.currentAction && !this.isActionLooping) {
              // Smoothly return to combat stance
              this.playAnimation('idle', true, 0.25);
            }
          });

          // Cache foot bones for floor grounding IK
          this.footBones = [];
          this.externalModel.traverse((child) => {
            if (child.isBone && (child.name === 'L_Foot' || child.name === 'R_Foot' || child.name === 'L_Toe' || child.name === 'R_Toe')) {
              this.footBones.push(child);
            }
          });

          const idleClip = this.externalAnimations.find(a => 
            a.name.toLowerCase().includes('idle') || a.name.toLowerCase().includes('dance')
          ) || this.externalAnimations[0];

          this.currentAction = this.externalMixer.clipAction(idleClip);
          this.currentAction.setLoop(THREE.LoopRepeat);
          this.currentAction.play();
        } else {
          this.externalMixer = null;
        }

        // Calibrar Deformador IA sobre el modelo 3D estándar
        this.deformer.calibrate(this.externalModel, fileUrl, false);

        if (onLoaded) onLoaded(gltf);
      },
      undefined,
      onError
    );
  }

  playAnimation(clipQuery, loop = true, blendDuration = 0.16) {
    if (!this.externalMixer || !this.externalAnimations || this.externalAnimations.length === 0) return;
    
    const q = clipQuery.toLowerCase();
    const clip = this.externalAnimations.find(a => {
      const n = a.name.toLowerCase();
      return n === q || n.includes(q);
    }) || this.externalAnimations.find(a => a.name.toLowerCase().includes('idle')) || this.externalAnimations[0];

    if (!clip) return;

    const nextAction = this.externalMixer.clipAction(clip);
    this.isActionLooping = loop;

    if (!loop) {
      nextAction.setLoop(THREE.LoopOnce, 1);
      nextAction.clampWhenFinished = true;
    } else {
      nextAction.setLoop(THREE.LoopRepeat);
      nextAction.clampWhenFinished = false;
    }

    if (this.currentAction && this.currentAction !== nextAction) {
      // Dynamic Cross-Fade (Slerp) with time warp for seamless real-time combo cancels
      nextAction.enabled = true;
      nextAction.setEffectiveTimeScale(1);
      nextAction.setEffectiveWeight(1);
      nextAction.reset();
      this.currentAction.crossFadeTo(nextAction, blendDuration, true);
      nextAction.play();
    } else {
      nextAction.reset().play();
    }

    this.currentAction = nextAction;
  }

  setVRMExpression(name, weight = 1.0) {
    if (this.currentVRM && this.currentVRM.expressionManager) {
      // Clear other expressions
      const expressions = ['neutral', 'happy', 'angry', 'sad', 'relaxed', 'surprised', 'blink', 'joy', 'sorrow', 'fun'];
      expressions.forEach(e => {
        try { this.currentVRM.expressionManager.setValue(e, 0.0); } catch(err){}
      });
      try {
        this.currentVRM.expressionManager.setValue(name, weight);
        this.currentVRM.expressionManager.update();
      } catch(err){}
    }
  }

  getAvailableAnimationNames() {
    if (!this.externalAnimations) return [];
    return this.externalAnimations.map(a => a.name);
  }

  update(delta) {
    // 1. Update VRM SpringBones Physics and Collider Groups in real time!
    if (this.currentVRM) {
      this.currentVRM.update(delta);
    }
    // 2. Update skeletal animations
    if (this.externalMixer) {
      this.externalMixer.update(delta);
    }
    // 3. Real-Time Adaptive AI Anatomical Deformations post-mixer
    if (this.deformer && this.isUsingExternalModel) {
      this.deformer.apply();
    }
  }
}
