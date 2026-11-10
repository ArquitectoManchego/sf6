import * as THREE from 'three';
import { sfx } from './audio.js';

export class AnimationController {
  constructor(characterController, driveImpactFX) {
    this.char = characterController;
    this.driveImpactFX = driveImpactFX;

    this.states = {
      CASUAL: 'casual',
      GUARD: 'guard',
      TAUNT: 'taunt',
      KICK: 'kick'
    };

    this.currentState = this.states.CASUAL;
    this.targetState = this.states.CASUAL;
    this.blendFactor = 1.0;
    this.blendSpeed = 3.5; // Smooth interpolation speed

    this.autoCycle = true;
    this.cycleTimer = 0;
    this.cycleIntervals = [7.0, 7.0, 3.5]; // casual duration, guard duration, taunt duration
    this.cycleIndex = 0;

    this.clock = 0;

    // Cache neutral reference transforms
    this.cacheNeutralPoses();
  }

  cacheNeutralPoses() {
    // Current animated transforms
    this.pose = {
      hipsY: 0.95,
      hipsRot: new THREE.Euler(),
      spineRot: new THREE.Euler(),
      chestRot: new THREE.Euler(),
      headRot: new THREE.Euler(),
      armL_upperRot: new THREE.Euler(),
      armL_forearmRot: new THREE.Euler(),
      armR_upperRot: new THREE.Euler(),
      armR_forearmRot: new THREE.Euler(),
      legL_thighRot: new THREE.Euler(),
      legL_calfRot: new THREE.Euler(),
      legR_thighRot: new THREE.Euler(),
      legR_calfRot: new THREE.Euler()
    };
  }

  setState(stateName, playAudio = true) {
    if (this.currentState === stateName && this.blendFactor >= 0.95) return;
    this.targetState = stateName;
    this.blendFactor = 0.0;

    if (playAudio) {
      if (stateName === this.states.GUARD) {
        sfx.playWhoosh();
      } else if (stateName === this.states.TAUNT) {
        sfx.playWhoosh();
        // Trigger Drive Impact VFX at peak
        setTimeout(() => {
          if (this.driveImpactFX) {
            this.driveImpactFX.trigger(new THREE.Vector3(0, 1.25, 0.45));
            sfx.playDriveImpact();
          }
        }, 400);
      } else if (stateName === this.states.KICK) {
        sfx.playWhoosh();
      }
    }
  }

  toggleAutoCycle(enabled) {
    this.autoCycle = enabled;
    this.cycleTimer = 0;
  }

  update(delta) {
    this.clock += delta;

    // Handle auto-cycle sequence: CASUAL -> GUARD -> TAUNT -> CASUAL
    if (this.autoCycle) {
      this.cycleTimer += delta;
      const threshold = this.cycleIntervals[this.cycleIndex] || 6.0;
      if (this.cycleTimer >= threshold) {
        this.cycleTimer = 0;
        this.cycleIndex = (this.cycleIndex + 1) % 3;
        if (this.cycleIndex === 0) {
          this.setState(this.states.CASUAL, false);
        } else if (this.cycleIndex === 1) {
          this.setState(this.states.GUARD, true);
        } else if (this.cycleIndex === 2) {
          this.setState(this.states.TAUNT, true);
        }
      }
    }

    // Blend between states smoothly
    if (this.blendFactor < 1.0) {
      this.blendFactor = Math.min(1.0, this.blendFactor + delta * this.blendSpeed);
      if (this.blendFactor >= 1.0) {
        this.currentState = this.targetState;
      }
    }

    // Compute active pose targets
    const t = this.clock;
    const poseA = this.computePose(this.currentState, t);
    const poseB = this.computePose(this.targetState, t);

    // Lerp between poseA and poseB
    const activePose = this.interpolatePoses(poseA, poseB, this.blendFactor);

    // Apply active pose to character joints
    this.applyPoseToCharacter(activePose);
  }

  computePose(state, t) {
    const p = {
      hipsY: 0.95,
      hipsRot: new THREE.Euler(0, 0, 0),
      spineRot: new THREE.Euler(0, 0, 0),
      chestRot: new THREE.Euler(0, 0, 0),
      headRot: new THREE.Euler(0, 0, 0),
      armL_upperRot: new THREE.Euler(0, 0, 0),
      armL_forearmRot: new THREE.Euler(0, 0, 0),
      armR_upperRot: new THREE.Euler(0, 0, 0),
      armR_forearmRot: new THREE.Euler(0, 0, 0),
      legL_thighRot: new THREE.Euler(0, 0, 0),
      legL_calfRot: new THREE.Euler(0, 0, 0),
      legR_thighRot: new THREE.Euler(0, 0, 0),
      legR_calfRot: new THREE.Euler(0, 0, 0)
    };

    if (state === this.states.CASUAL) {
      // 1. Idle Casual: Relaxed breathing, subtle weight shifting
      const breath = Math.sin(t * 1.8) * 0.03;
      const sway = Math.sin(t * 0.9) * 0.04;

      p.hipsY = 0.95 + breath * 0.3;
      p.hipsRot.set(0, sway * 0.5, sway * 0.3);
      p.spineRot.set(breath * 0.6, 0, -sway * 0.2);
      p.chestRot.set(breath, 0, -sway * 0.2);
      p.headRot.set(-breath * 0.4, Math.sin(t * 0.5) * 0.08, 0);

      // Relaxed arms with subtle sway
      p.armL_upperRot.set(0.1 + breath * 0.3, 0, -0.15 - sway * 0.2);
      p.armL_forearmRot.set(0.2, 0, -0.1);
      p.armR_upperRot.set(0.1 + breath * 0.3, 0, 0.15 + sway * 0.2);
      p.armR_forearmRot.set(0.2, 0, 0.1);

      // Relaxed standing legs
      p.legL_thighRot.set(-0.05 + sway * 0.1, 0, -0.05);
      p.legR_thighRot.set(0.05 - sway * 0.1, 0, 0.05);

    } else if (state === this.states.GUARD) {
      // 2. Street Fighter 6 Combat Stance (Guardia de combate)
      // Athletic low bounce, raised boxing/martial arts fists, angled torso
      const bounce = Math.abs(Math.sin(t * 3.5)) * 0.04;
      const combatRhythm = Math.sin(t * 3.5) * 0.06;

      p.hipsY = 0.88 - bounce;
      p.hipsRot.set(0.08, 0.35, 0); // Angled 45 deg fight stance
      p.spineRot.set(0.05, -0.15, 0);
      p.chestRot.set(0.08, -0.12, combatRhythm * 0.4);
      p.headRot.set(0.02, -0.08, 0); // Eyes locked on opponent

      // Left lead hand / guard fist (raised high)
      p.armL_upperRot.set(-1.15 + combatRhythm * 0.5, 0.25, 0.45);
      p.armL_forearmRot.set(1.5, 0.2, -0.3);

      // Right rear hand (protecting chin)
      p.armR_upperRot.set(-1.25 + combatRhythm * 0.4, -0.3, -0.45);
      p.armR_forearmRot.set(1.6, -0.3, 0.35);

      // Combat stance bent legs (boxer stance)
      p.legL_thighRot.set(-0.35 + bounce * 0.5, 0.2, -0.1);
      p.legL_calfRot.set(0.45, 0, 0);
      p.legR_thighRot.set(0.25 - bounce * 0.5, -0.1, 0.15);
      p.legR_calfRot.set(0.35, 0, 0);

    } else if (state === this.states.TAUNT) {
      // 3. Signature Attitude Move (SF6 Drive Strike / Flex Pose)
      const pulse = Math.sin(t * 4.0) * 0.03;
      p.hipsY = 0.90;
      p.hipsRot.set(0, -0.2, 0);
      p.spineRot.set(-0.12, 0.15, 0);
      p.chestRot.set(-0.18 + pulse, 0.15, 0); // Proud flexed chest
      p.headRot.set(-0.15, -0.1, 0); // Confident chin lift

      // Power flex arms / martial arts strike pose
      p.armL_upperRot.set(-1.4, 0.4, 0.9);
      p.armL_forearmRot.set(1.8, 0, 0);
      p.armR_upperRot.set(-1.6, -0.6, -0.8);
      p.armR_forearmRot.set(1.9, 0, 0);

      // Solid wide warrior stance
      p.legL_thighRot.set(-0.2, 0.15, -0.25);
      p.legL_calfRot.set(0.25, 0, 0);
      p.legR_thighRot.set(0.15, -0.2, 0.25);
      p.legR_calfRot.set(0.2, 0, 0);

    } else if (state === this.states.KICK) {
      // 4. Combat High Kick pose (showcasing legs morph)
      p.hipsY = 0.92;
      p.hipsRot.set(0, 0.4, -0.2);
      p.spineRot.set(0, 0, 0.2);
      p.chestRot.set(0, 0, 0.2);
      p.headRot.set(0, -0.3, 0);

      // Guard arms while kicking
      p.armL_upperRot.set(-0.9, 0.3, 0.6);
      p.armL_forearmRot.set(1.4, 0, 0);
      p.armR_upperRot.set(0.4, 0, -0.8);
      p.armR_forearmRot.set(0.5, 0, 0);

      // Support Leg
      p.legR_thighRot.set(0.1, 0, 0.1);
      p.legR_calfRot.set(0.15, 0, 0);

      // Kick Leg (Extended High)
      p.legL_thighRot.set(-1.6, 0.3, -0.5);
      p.legL_calfRot.set(0.15, 0, 0);
    }

    return p;
  }

  interpolatePoses(a, b, alpha) {
    const res = {};
    res.hipsY = THREE.MathUtils.lerp(a.hipsY, b.hipsY, alpha);

    const lerpEuler = (eA, eB) => {
      return new THREE.Euler(
        THREE.MathUtils.lerp(eA.x, eB.x, alpha),
        THREE.MathUtils.lerp(eA.y, eB.y, alpha),
        THREE.MathUtils.lerp(eA.z, eB.z, alpha)
      );
    };

    res.hipsRot = lerpEuler(a.hipsRot, b.hipsRot);
    res.spineRot = lerpEuler(a.spineRot, b.spineRot);
    res.chestRot = lerpEuler(a.chestRot, b.chestRot);
    res.headRot = lerpEuler(a.headRot, b.headRot);
    res.armL_upperRot = lerpEuler(a.armL_upperRot, b.armL_upperRot);
    res.armL_forearmRot = lerpEuler(a.armL_forearmRot, b.armL_forearmRot);
    res.armR_upperRot = lerpEuler(a.armR_upperRot, b.armR_upperRot);
    res.armR_forearmRot = lerpEuler(a.armR_forearmRot, b.armR_forearmRot);
    res.legL_thighRot = lerpEuler(a.legL_thighRot, b.legL_thighRot);
    res.legL_calfRot = lerpEuler(a.legL_calfRot, b.legL_calfRot);
    res.legR_thighRot = lerpEuler(a.legR_thighRot, b.legR_thighRot);
    res.legR_calfRot = lerpEuler(a.legR_calfRot, b.legR_calfRot);

    return res;
  }

  applyPoseToCharacter(p) {
    if (this.char.isUsingExternalModel) return;
    const n = this.char.nodes;
    if (!n.hips) return;

    n.hips.position.y = p.hipsY;
    n.hips.rotation.copy(p.hipsRot);
    if (n.spine) n.spine.rotation.copy(p.spineRot);
    if (n.chest) n.chest.rotation.copy(p.chestRot);
    if (n.head) n.head.rotation.copy(p.headRot);

    if (n.armL) {
      n.armL.upperArmGroup.rotation.copy(p.armL_upperRot);
      n.armL.forearmGroup.rotation.copy(p.armL_forearmRot);
    }
    if (n.armR) {
      n.armR.upperArmGroup.rotation.copy(p.armR_upperRot);
      n.armR.forearmGroup.rotation.copy(p.armR_forearmRot);
    }

    if (n.legL) {
      n.legL.thighGroup.rotation.copy(p.legL_thighRot);
      n.legL.calfGroup.rotation.copy(p.legL_calfRot);
    }
    if (n.legR) {
      n.legR.thighGroup.rotation.copy(p.legR_thighRot);
      n.legR.calfGroup.rotation.copy(p.legR_calfRot);
    }
  }
}
