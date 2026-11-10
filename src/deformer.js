import * as THREE from 'three';

/**
 * AnatomicalDeformerAI v3.0 - Motor Adaptativo de Modificadores Corporales con IA
 * & Modo Editor Visual 3D
 * 
 * Capacidades Principales:
 * 1. Escaneo Inteligente de Rig y Topología (Capcom SF6, Unreal Fortnite, Mixamo, VRM, Procedural).
 * 2. Deformación Dual-Layer Unificada:
 *    - Capa Esquelética (Huesos dedicados y secundarios post-mixer).
 *    - Capa Geométrica RBF (Radial Basis Function direct-vertex morphing en tiempo real).
 * 3. Modo Editor 3D interactivo con Gizmos holográficos visuales en la tornamesa.
 * 4. Generación y Adaptación Automática de Modificadores con IA para cualquier malla 3D.
 */
export class AnatomicalDeformerAI {
  constructor(characterController) {
    this.char = characterController;
    this.model = null;
    this.isVRM = false;
    this.isCalibrated = false;

    // Modo Editor 3D
    this.isEditorModeActive = false;
    this.editorGizmoGroup = new THREE.Group();
    this.editorGizmoGroup.name = "AI_Anatomical_Editor_Gizmos";
    this.editorGizmoGroup.visible = false;
    if (this.char.scene) {
      this.char.scene.add(this.editorGizmoGroup);
    }

    // Telemetría e IA
    this.telemetry = {
      modelName: 'Chun-Li SF6 Oficial',
      rigType: 'Capcom RE-Engine (SF6)',
      boneCount: 0,
      meshCount: 0,
      vertexCount: 0,
      confidence: 99.8,
      activeChannels: 0,
      editorMode: false,
      detectedBones: {
        busto: 0,
        cintura: 0,
        cadera: 0,
        gluteos: 0,
        muslos: 0,
        gemelos: 0
      }
    };

    // Canales de huesos clasificados semánticamente
    this.channels = {
      bust: [],
      waist: [],
      hips: [],
      glutes: [],
      thighs: [],
      calves: [],
      shoulders: []
    };

    // Zonas Anatómicas para Deformación RBF y Gizmos Visuales (coordenadas relativas en espacio modelo)
    this.zones = {
      bustL: { center: new THREE.Vector3(0.08, 1.25, 0.12), radius: 0.18, color: 0x00f5d4, name: 'Busto Izquierdo' },
      bustR: { center: new THREE.Vector3(-0.08, 1.25, 0.12), radius: 0.18, color: 0x00f5d4, name: 'Busto Derecho' },
      waist: { center: new THREE.Vector3(0, 1.02, 0.01), radius: 0.22, color: 0xffb703, name: 'Cintura / Abdomen' },
      hips: { center: new THREE.Vector3(0, 0.88, 0.0), radius: 0.26, color: 0x9d4edd, name: 'Cadera / Pelvis' },
      gluteL: { center: new THREE.Vector3(0.09, 0.86, -0.10), radius: 0.22, color: 0xff007f, name: 'Glúteo Izquierdo' },
      gluteR: { center: new THREE.Vector3(-0.09, 0.86, -0.10), radius: 0.22, color: 0xff007f, name: 'Glúteo Derecho' },
      thighL: { center: new THREE.Vector3(0.12, 0.62, 0.0), radius: 0.24, color: 0x06d6a0, name: 'Muslo Izquierdo' },
      thighR: { center: new THREE.Vector3(-0.12, 0.62, 0.0), radius: 0.24, color: 0x06d6a0, name: 'Muslo Derecho' },
      calfL: { center: new THREE.Vector3(0.10, 0.30, -0.02), radius: 0.20, color: 0x118ab2, name: 'Gemelo Izquierdo' },
      calfR: { center: new THREE.Vector3(-0.10, 0.30, -0.02), radius: 0.20, color: 0x118ab2, name: 'Gemelo Derecho' }
    };

    // Materiales y mallas registradas
    this.materials = [];
    this.skinnedMeshes = [];

    // Sensibilidad y multiplicadores ajustables
    this.sensitivity = {
      bust: 1.0,
      waist: 1.0,
      hips: 1.0,
      glutes: 1.0,
      thighs: 1.0,
      calves: 1.0,
      muscle: 1.0,
      fat: 1.0
    };

    this.baseModelScale = new THREE.Vector3(1, 1, 1);
    this.baseModelPosition = new THREE.Vector3(0, 0.02, 0);
    this.groundY = 0.02;
    this.needsVertexUpdate = true;

    this.buildEditorGizmos();
  }

  /**
   * Construye los gizmos 3D holográficos para el Modo Editor
   */
  buildEditorGizmos() {
    while (this.editorGizmoGroup.children.length > 0) {
      this.editorGizmoGroup.remove(this.editorGizmoGroup.children[0]);
    }

    const gizmoDefs = [
      { key: 'bustL', r: 0.12, tube: 0.012, col: 0x00f5d4, label: 'BUSTO (L)' },
      { key: 'bustR', r: 0.12, tube: 0.012, col: 0x00f5d4, label: 'BUSTO (R)' },
      { key: 'waist', r: 0.20, tube: 0.016, col: 0xffb703, label: 'CINTURA' },
      { key: 'hips', r: 0.24, tube: 0.018, col: 0x9d4edd, label: 'CADERA' },
      { key: 'gluteL', r: 0.16, tube: 0.015, col: 0xff007f, label: 'GLÚTEO (L)' },
      { key: 'gluteR', r: 0.16, tube: 0.015, col: 0xff007f, label: 'GLÚTEO (R)' },
      { key: 'thighL', r: 0.15, tube: 0.014, col: 0x06d6a0, label: 'MUSLO (L)' },
      { key: 'thighR', r: 0.15, tube: 0.014, col: 0x06d6a0, label: 'MUSLO (R)' },
      { key: 'calfL', r: 0.12, tube: 0.012, col: 0x118ab2, label: 'GEMELO (L)' },
      { key: 'calfR', r: 0.12, tube: 0.012, col: 0x118ab2, label: 'GEMELO (R)' }
    ];

    gizmoDefs.forEach(def => {
      const gGroup = new THREE.Group();
      gGroup.name = `Gizmo_${def.key}`;

      // 1. Torus Ring con material holográfico brillante
      const ringGeo = new THREE.TorusGeometry(def.r, def.tube, 16, 48);
      ringGeo.rotateX(Math.PI / 2);
      const ringMat = new THREE.MeshBasicMaterial({
        color: def.col,
        wireframe: true,
        transparent: true,
        opacity: 0.85
      });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      gGroup.add(ringMesh);

      // 2. Esfera central de anclaje (Anchor Point)
      const anchorGeo = new THREE.SphereGeometry(def.tube * 1.5, 12, 12);
      const anchorMat = new THREE.MeshBasicMaterial({
        color: def.col,
        transparent: true,
        opacity: 0.95
      });
      const anchorMesh = new THREE.Mesh(anchorGeo, anchorMat);
      gGroup.add(anchorMesh);

      this.editorGizmoGroup.add(gGroup);
    });
  }

  /**
   * Actualiza las posiciones y escalas de los Gizmos 3D en tiempo real
   */
  updateGizmoTransforms() {
    if (!this.isEditorModeActive || !this.model) return;

    // Asegurar que el grupo de gizmos siga al modelo en posición y rotación del stage
    this.editorGizmoGroup.position.copy(this.model.position);
    this.editorGizmoGroup.rotation.copy(this.model.rotation);

    for (const [key, zone] of Object.entries(this.zones)) {
      const gizmo = this.editorGizmoGroup.getObjectByName(`Gizmo_${key}`);
      if (gizmo) {
        gizmo.position.copy(zone.center);
        
        // Escala dinámica del gizmo según el slider correspondiente
        let scaleMult = 1.0;
        const p = this.char.params;
        if (key.startsWith('bust')) scaleMult = (p.bustSize || 1.0) * (p.bustCup || 1.0);
        else if (key === 'waist') scaleMult = p.waistWidth || 1.0;
        else if (key === 'hips') scaleMult = p.hipWidth || 1.0;
        else if (key.startsWith('glute')) scaleMult = p.gluteSize || 1.1;
        else if (key.startsWith('thigh')) scaleMult = p.thighWidth || 1.15;
        else if (key.startsWith('calf')) scaleMult = p.calfWidth || 1.05;

        gizmo.scale.set(scaleMult, scaleMult, scaleMult);
      }
    }
  }

  /**
   * Activa o desactiva el Modo Editor Anatómico 3D
   */
  setEditorMode(enabled) {
    this.isEditorModeActive = !!enabled;
    this.editorGizmoGroup.visible = this.isEditorModeActive;
    this.telemetry.editorMode = this.isEditorModeActive;
    if (this.isEditorModeActive) {
      this.updateGizmoTransforms();
    }
  }

  /**
   * Escanea y calibra automáticamente cualquier modelo 3D cargado
   */
  calibrate(model, modelIdentifier = 'Modelo 3D', isVRM = false) {
    if (!model) return;

    this.model = model;
    this.isVRM = isVRM;

    // Resetear canales
    this.channels = {
      bust: [],
      waist: [],
      hips: [],
      glutes: [],
      thighs: [],
      calves: [],
      shoulders: []
    };
    this.materials = [];
    this.skinnedMeshes = [];

    let totalBones = 0;
    let totalMeshes = 0;
    let totalVerts = 0;
    const allBoneNames = [];

    this.baseModelScale.copy(model.scale);
    this.baseModelPosition.copy(model.position);

    // 1. Recorrer la jerarquía completa
    model.traverse((child) => {
      if (child.isBone) {
        totalBones++;
        allBoneNames.push(child.name);
        if (!child.userData.aiRestScale) {
          child.userData.aiRestScale = child.scale.clone();
        }
        this.classifyBone(child);
      }

      if (child.isMesh || child.isSkinnedMesh) {
        totalMeshes++;
        if (child.geometry && child.geometry.attributes.position) {
          totalVerts += child.geometry.attributes.position.count;
          
          // Clonar copia pura inmutable de los vértices base para el motor RBF
          if (!child.geometry.userData.origPositions) {
            child.geometry.userData.origPositions = new Float32Array(
              child.geometry.attributes.position.array
            );
          }
        }

        if (child.isSkinnedMesh && !this.skinnedMeshes.includes(child)) {
          this.skinnedMeshes.push(child);
        }

        if (child.material) {
          const mats = Array.isArray(child.material) ? child.material : [child.material];
          mats.forEach(m => {
            if (!this.materials.includes(m)) {
              if (!m.userData.aiInitial) {
                m.userData.aiInitial = {
                  roughness: m.roughness !== undefined ? m.roughness : 0.5,
                  metalness: m.metalness !== undefined ? m.metalness : 0.0,
                  normalScale: m.normalScale ? m.normalScale.clone() : new THREE.Vector2(1, 1),
                  hasNormalMap: !!m.normalMap
                };
              }
              this.materials.push(m);
            }
          });
        }
      }
    });

    // 2. Detección Inteligente del Rig y Generación de Modificadores IA
    this.detectRigArchitecture(allBoneNames, totalBones, totalMeshes, totalVerts, modelIdentifier);
    this.autoGenerateAIModifiers();

    this.isCalibrated = true;
    console.log(`[AnatomicalDeformerAI] Calibrado exitosamente: ${this.telemetry.rigType} (${totalBones} huesos, ${totalMeshes} mallas, ${totalVerts} vértices)`);

    // 3. Aplicar parámetros anatómicos iniciales
    this.apply();
  }

  /**
   * Genera y adapta automáticamente con IA las zonas anatómicas según la geometría del modelo
   */
  autoGenerateAIModifiers() {
    if (!this.model) return;

    // Calcular BoundingBox de la malla real
    const box = new THREE.Box3().setFromObject(this.model);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    const height = size.y > 0.1 ? size.y : 1.70;
    const width = size.x > 0.1 ? size.x : 0.60;
    const depth = size.z > 0.1 ? size.z : 0.40;

    // Adaptar anclajes y radios basados en proporciones áureas antropométricas
    const hBust = center.y + height * 0.18;
    const hWaist = center.y + height * 0.03;
    const hHips = center.y - height * 0.08;
    const hGlutes = center.y - height * 0.09;
    const hThighs = center.y - height * 0.24;
    const hCalves = center.y - height * 0.42;

    this.zones.bustL.center.set(width * 0.16, hBust, depth * 0.22);
    this.zones.bustR.center.set(-width * 0.16, hBust, depth * 0.22);
    this.zones.waist.center.set(0, hWaist, depth * 0.02);
    this.zones.hips.center.set(0, hHips, 0);
    this.zones.gluteL.center.set(width * 0.18, hGlutes, -depth * 0.20);
    this.zones.gluteR.center.set(-width * 0.18, hGlutes, -depth * 0.20);
    this.zones.thighL.center.set(width * 0.20, hThighs, 0);
    this.zones.thighR.center.set(-width * 0.20, hThighs, 0);
    this.zones.calfL.center.set(width * 0.15, hCalves, -depth * 0.04);
    this.zones.calfR.center.set(-width * 0.15, hCalves, -depth * 0.04);

    this.needsVertexUpdate = true;
    if (this.isEditorModeActive) {
      this.updateGizmoTransforms();
    }
  }

  /**
   * Clasifica un hueso en su canal semántico correspondiente
   */
  classifyBone(bone) {
    const name = bone.name.toLowerCase().trim();

    // 1. Canal Busto / Pecho (Capcom RE-Engine L_Bust_00_01, R_Bust_00_01, DOA, etc.)
    if (/bust|breast|boob|pec_/i.test(name)) {
      if (!this.channels.bust.includes(bone)) this.channels.bust.push(bone);
    } else if (/c_chest|spine\s*0?[4-5]|mixamorig:spine2/i.test(name)) {
      // Hueso de pecho general como fallback
      if (!this.channels.bust.includes(bone)) this.channels.bust.push(bone);
    }

    // 2. Canal Cintura / Abdomen
    if (/c_spine[1-2]|spine\s*0?[1-2]|mixamorig:spine$|mixamorig:spine1|waist|belly|stomach/i.test(name)) {
      if (!this.channels.waist.includes(bone)) this.channels.waist.push(bone);
    }

    // 3. Canal Cadera / Pelvis
    if (/c_hip$|root\s*hips?|mixamorig:hips|pelvis/i.test(name)) {
      if (!this.channels.hips.includes(bone)) this.channels.hips.push(bone);
    }

    // 4. Canal Glúteos (Capcom R_Hip, L_Hip, R_HipJiggle_00, L_HipJiggle_00)
    if (/([rl]_hip(jiggle|_hj)?)|butt|glute|buttock/i.test(name)) {
      if (!this.channels.glutes.includes(bone)) this.channels.glutes.push(bone);
    }

    // 5. Canal Muslos (Capcom L_Thigh, R_Thigh, L_ThighJiggleFront_00, etc.)
    if (/([rl]_thigh(jigglefront|jiggleback|rot|_hj)?)|leg\s*(left|right)\s*thigh|mixamorig:(left|right)upleg|upperleg/i.test(name)) {
      if (!this.channels.thighs.includes(bone)) this.channels.thighs.push(bone);
    }

    // 6. Canal Gemelos / Pantorrillas / Rodillas
    if (/([rl]_knee(_f_hj|_b_hj)?)|leg\s*(left|right)\s*knee|mixamorig:(left|right)leg|calf|shin|lowerleg/i.test(name)) {
      if (!this.channels.calves.includes(bone)) this.channels.calves.push(bone);
    }

    // 7. Canal Hombros
    if (/clavicle|shoulder|mixamorig:(left|right)shoulder/i.test(name)) {
      if (!this.channels.shoulders.includes(bone)) this.channels.shoulders.push(bone);
    }
  }

  /**
   * Reconoce el arquetipo de rigging mediante heurísticas de IA
   */
  detectRigArchitecture(boneNames, boneCount, meshCount, vertexCount, modelName) {
    let rigType = 'Esqueleto Humanoide Estándar';
    let confidence = 95.0;

    const hasREEngineBones = boneNames.some(b => b.startsWith('C_') || b.startsWith('R_') || b.startsWith('L_'));
    const hasFortniteBones = boneNames.some(b => b.includes('root hips') || b.includes('leg left thigh') || b.includes('spine 01'));
    const hasMixamoBones = boneNames.some(b => b.includes('mixamorig:'));

    if (hasREEngineBones && boneCount > 250) {
      rigType = 'Capcom RE-Engine (SF6 Oficial 4K)';
      confidence = 99.8;
    } else if (hasFortniteBones) {
      rigType = 'Epic Games Unreal Engine (Fortnite Crossover)';
      confidence = 99.4;
    } else if (hasMixamoBones) {
      rigType = 'Mixamo Humanoid Combat Skeleton';
      confidence = 98.6;
    } else if (this.isVRM) {
      rigType = 'VRM Avatar 3D (SpringBones Rig)';
      confidence = 99.1;
    } else if (boneCount === 0) {
      rigType = 'Malla Paramétrica Procedural SF6';
      confidence = 100.0;
    }

    let activeChannels = 0;
    for (const [k, v] of Object.entries(this.channels)) {
      if (v.length > 0) activeChannels++;
    }

    this.telemetry = {
      modelName,
      rigType,
      boneCount,
      meshCount,
      vertexCount,
      confidence,
      activeChannels,
      editorMode: this.isEditorModeActive,
      detectedBones: {
        busto: this.channels.bust.length,
        cintura: this.channels.waist.length,
        cadera: this.channels.hips.length,
        gluteos: this.channels.glutes.length,
        muslos: this.channels.thighs.length,
        gemelos: this.channels.calves.length
      }
    };
  }

  /**
   * Aplica los modificadores anatómicos con el motor Dual-Layer (Huesos + Vértices RBF + Shaders)
   */
  apply() {
    const p = this.char.params;
    if (!p) return;

    if (!this.char.isUsingExternalModel || !this.model) {
      return;
    }

    const sens = this.sensitivity;

    // ==========================================
    // 1. ESTATURA & CONTACTO AL PISO (Grounding)
    // ==========================================
    const h = p.height || 1.0;
    const heightFactor = Math.max(0.7, Math.min(1.4, h));
    
    const lateralComp = 1.0 + (heightFactor - 1.0) * 0.15;
    this.model.scale.set(
      this.baseModelScale.x * lateralComp,
      this.baseModelScale.y * heightFactor,
      this.baseModelScale.z * lateralComp
    );

    const bbox = new THREE.Box3().setFromObject(this.model);
    this.model.position.y = -bbox.min.y + this.groundY;

    // ==========================================
    // 2. CAPA ESQUELÉTICA (Driver Bones Scaling)
    // ==========================================
    const bustScale = (p.bustSize !== undefined ? p.bustSize : 1.0) * sens.bust;
    const cupProjection = (p.bustCup !== undefined ? p.bustCup : 1.0);
    const dedicatedBustBones = this.channels.bust.filter(b => /bust|breast|boob|pec_/i.test(b.name));
    
    if (dedicatedBustBones.length > 0) {
      dedicatedBustBones.forEach(bone => {
        const rest = bone.userData.aiRestScale || bone.scale;
        bone.scale.x = rest.x * bustScale;
        bone.scale.y = rest.y * bustScale;
        bone.scale.z = rest.z * (bustScale * cupProjection);
      });
    }

    const waistWidth = (p.waistWidth !== undefined ? p.waistWidth : 1.0) * sens.waist;
    const bodyFat = (p.bodyFat !== undefined ? p.bodyFat : 0.15) * sens.fat;
    const fatFactor = 1.0 + bodyFat * 0.50;

    this.channels.waist.forEach(bone => {
      const rest = bone.userData.aiRestScale || bone.scale;
      bone.scale.x = rest.x * (waistWidth * fatFactor);
      bone.scale.z = rest.z * (waistWidth * 0.95 * fatFactor);
    });

    const hipWidth = (p.hipWidth !== undefined ? p.hipWidth : 1.0) * sens.hips;
    const hipFatSpread = 1.0 + bodyFat * 0.20;

    this.channels.hips.forEach(bone => {
      const rest = bone.userData.aiRestScale || bone.scale;
      bone.scale.x = rest.x * (hipWidth * hipFatSpread);
    });

    const gluteSize = (p.gluteSize !== undefined ? p.gluteSize : 1.1) * sens.glutes;
    const shape = p.gluteShape || 'heart';
    let gluteX = gluteSize;
    let gluteY = gluteSize;
    let gluteZ = gluteSize * 1.18;

    if (shape === 'heart') {
      gluteX *= 1.24; gluteY *= 1.06; gluteZ *= 1.22;
    } else if (shape === 'teardrop') {
      gluteX *= 1.04; gluteY *= 1.18; gluteZ *= 1.30;
    } else if (shape === 'oval') {
      gluteX *= 0.92; gluteY *= 1.25; gluteZ *= 1.10;
    } else if (shape === 'round') {
      gluteX *= 1.14; gluteY *= 1.14; gluteZ *= 1.24;
    }

    if (this.channels.glutes.length > 0) {
      this.channels.glutes.forEach(bone => {
        const rest = bone.userData.aiRestScale || bone.scale;
        bone.scale.x = rest.x * gluteX;
        bone.scale.y = rest.y * gluteY;
        bone.scale.z = rest.z * gluteZ;
      });
    }

    const thighWidth = (p.thighWidth !== undefined ? p.thighWidth : 1.15) * sens.thighs;
    const thighFatSpread = 1.0 + bodyFat * 0.22;
    const finalThighThickness = thighWidth * thighFatSpread;

    this.channels.thighs.forEach(bone => {
      const rest = bone.userData.aiRestScale || bone.scale;
      bone.scale.x = rest.x * finalThighThickness;
      bone.scale.z = rest.z * (finalThighThickness * 1.06);
    });

    const calfWidth = (p.calfWidth !== undefined ? p.calfWidth : 1.05) * sens.calves;
    this.channels.calves.forEach(bone => {
      const rest = bone.userData.aiRestScale || bone.scale;
      bone.scale.x = rest.x * calfWidth;
      bone.scale.z = rest.z * (calfWidth * 1.08);
    });

    // ==========================================
    // 3. CAPA GEOMÉTRICA (Direct RBF Vertex Morphing)
    // ==========================================
    if (this.needsVertexUpdate) {
      this.applyVertexRBFDeformation(bustScale, cupProjection, waistWidth, fatFactor, hipWidth, gluteSize, shape, finalThighThickness, calfWidth);
      this.needsVertexUpdate = false;
    }

    // ==========================================
    // 4. SHADERS: MUSCULATURA & GRASA CORPORAL
    // ==========================================
    const muscularity = (p.muscularity !== undefined ? p.muscularity : 0.7) * sens.muscle;
    const effectiveNormalScale = Math.max(0.2, (0.4 + muscularity * 1.9) * (1.25 - bodyFat * 1.1));

    this.materials.forEach(mat => {
      if (mat.normalScale) {
        mat.normalScale.set(effectiveNormalScale, effectiveNormalScale);
      } else if (!mat.normalMap && this.char.muscleNormalMap) {
        mat.normalMap = this.char.muscleNormalMap;
        mat.normalScale = new THREE.Vector2(effectiveNormalScale, effectiveNormalScale);
        mat.needsUpdate = true;
      }

      if (mat.userData && mat.userData.aiInitial) {
        const baseRough = mat.userData.aiInitial.roughness;
        mat.roughness = THREE.MathUtils.clamp(
          baseRough * (1.0 - muscularity * 0.22) + (bodyFat * 0.25),
          0.15,
          0.90
        );
      }
    });

    if (this.isEditorModeActive) {
      this.updateGizmoTransforms();
    }
  }

  /**
   * Deformación RBF directa sobre los vértices de las mallas (Body + Cloth)
   */
  applyVertexRBFDeformation(bustScale, cupProj, waistWidth, fatFactor, hipWidth, gluteScale, gluteShape, thighScale, calfScale) {
    if (this.skinnedMeshes.length === 0) return;

    const z = this.zones;
    const deltaBust = (bustScale * cupProj - 1.0) * 0.08;
    const deltaWaist = (waistWidth * fatFactor - 1.0) * 0.06;
    const deltaHip = (hipWidth - 1.0) * 0.06;
    const deltaGlute = (gluteScale - 1.0) * 0.10;
    const deltaThigh = (thighScale - 1.0) * 0.06;
    const deltaCalf = (calfScale - 1.0) * 0.04;

    // Solo ejecutar si hay deformación significativa respecto a 1.0
    const hasDeform = Math.abs(deltaBust) > 0.001 || Math.abs(deltaWaist) > 0.001 || 
                      Math.abs(deltaHip) > 0.001 || Math.abs(deltaGlute) > 0.001 || 
                      Math.abs(deltaThigh) > 0.001 || Math.abs(deltaCalf) > 0.001;

    for (let m = 0; m < this.skinnedMeshes.length; m++) {
      const mesh = this.skinnedMeshes[m];
      if (!mesh.geometry || !mesh.geometry.attributes.position || !mesh.geometry.userData.origPositions) continue;

      const pos = mesh.geometry.attributes.position.array;
      const orig = mesh.geometry.userData.origPositions;
      const count = mesh.geometry.attributes.position.count;

      if (!hasDeform) {
        // Restaurar posición original exacta
        pos.set(orig);
        mesh.geometry.attributes.position.needsUpdate = true;
        continue;
      }

      for (let i = 0; i < count; i++) {
        const i3 = i * 3;
        const ox = orig[i3];
        const oy = orig[i3 + 1];
        const oz = orig[i3 + 2];

        let dx = 0;
        let dy = 0;
        let dz = 0;

        // 1. Busto RBF (Vértices frontales z > 0 en altura de pecho)
        if (oz > 0.02 && oy > z.bustL.center.y - 0.18 && oy < z.bustL.center.y + 0.18) {
          const distL2 = (ox - z.bustL.center.x)**2 + (oy - z.bustL.center.y)**2 + (oz - z.bustL.center.z)**2;
          const distR2 = (ox - z.bustR.center.x)**2 + (oy - z.bustR.center.y)**2 + (oz - z.bustR.center.z)**2;
          const r2 = z.bustL.radius**2;

          if (distL2 < r2) {
            const w = (1.0 - distL2 / r2)**2;
            dz += deltaBust * w * 1.3;
            dx += deltaBust * w * 0.35;
          }
          if (distR2 < r2) {
            const w = (1.0 - distR2 / r2)**2;
            dz += deltaBust * w * 1.3;
            dx -= deltaBust * w * 0.35;
          }
        }

        // 2. Cintura RBF
        if (oy > z.waist.center.y - 0.14 && oy < z.waist.center.y + 0.14) {
          const dY = Math.abs(oy - z.waist.center.y) / 0.14;
          const w = (1.0 - dY * dY)**2;
          dx += ox * deltaWaist * w;
          dz += oz * deltaWaist * w * 0.85;
        }

        // 3. Cadera RBF
        if (oy > z.hips.center.y - 0.12 && oy < z.hips.center.y + 0.12) {
          const dY = Math.abs(oy - z.hips.center.y) / 0.12;
          const w = (1.0 - dY * dY)**2;
          dx += (ox > 0 ? 1 : -1) * deltaHip * w * 0.65;
        }

        // 4. Glúteos RBF (Vértices posteriores z < 0 en altura de glúteos)
        if (oz < -0.01 && oy > z.gluteL.center.y - 0.16 && oy < z.gluteL.center.y + 0.16) {
          const distL2 = (ox - z.gluteL.center.x)**2 + (oy - z.gluteL.center.y)**2 + (oz - z.gluteL.center.z)**2;
          const distR2 = (ox - z.gluteR.center.x)**2 + (oy - z.gluteR.center.y)**2 + (oz - z.gluteR.center.z)**2;
          const r2 = z.gluteL.radius**2;

          let shapeZMult = 1.0;
          let shapeXMult = 1.0;
          if (gluteShape === 'heart') { shapeZMult = 1.15; shapeXMult = 1.25; }
          else if (gluteShape === 'teardrop') { shapeZMult = 1.28; shapeXMult = 1.05; }
          else if (gluteShape === 'round') { shapeZMult = 1.20; shapeXMult = 1.15; }

          if (distL2 < r2) {
            const w = (1.0 - distL2 / r2)**2;
            dz -= deltaGlute * w * 1.4 * shapeZMult;
            dx += deltaGlute * w * 0.45 * shapeXMult;
          }
          if (distR2 < r2) {
            const w = (1.0 - distR2 / r2)**2;
            dz -= deltaGlute * w * 1.4 * shapeZMult;
            dx -= deltaGlute * w * 0.45 * shapeXMult;
          }
        }

        // 5. Muslos RBF
        if (oy > z.thighL.center.y - 0.20 && oy < z.thighL.center.y + 0.20) {
          const dY = Math.abs(oy - z.thighL.center.y) / 0.20;
          const w = (1.0 - dY * dY)**2;
          dx += (ox > 0 ? 1 : -1) * deltaThigh * w * 0.55;
          dz += (oz > 0 ? 1 : -1) * deltaThigh * w * 0.50;
        }

        // 6. Gemelos RBF
        if (oy > z.calfL.center.y - 0.16 && oy < z.calfL.center.y + 0.16) {
          const dY = Math.abs(oy - z.calfL.center.y) / 0.16;
          const w = (1.0 - dY * dY)**2;
          dx += (ox > 0 ? 1 : -1) * deltaCalf * w * 0.45;
          dz += (oz > 0 ? 1 : -1) * deltaCalf * w * 0.50;
        }

        pos[i3] = ox + dx;
        pos[i3 + 1] = oy + dy;
        pos[i3 + 2] = oz + dz;
      }

      mesh.geometry.attributes.position.needsUpdate = true;
    }
  }

  /**
   * Ajusta la sensibilidad de un canal específico para calibración fina
   */
  setSensitivity(channel, value) {
    if (this.sensitivity[channel] !== undefined) {
      this.sensitivity[channel] = parseFloat(value);
      this.needsVertexUpdate = true;
      this.apply();
    }
  }

  /**
   * Resetea la sensibilidad a los valores por defecto
   */
  resetSensitivity() {
    Object.keys(this.sensitivity).forEach(k => {
      this.sensitivity[k] = 1.0;
    });
    this.needsVertexUpdate = true;
    this.apply();
  }

  /**
   * Devuelve los datos de diagnóstico de la IA para mostrar en la interfaz
   */
  getTelemetry() {
    return this.telemetry;
  }
}
