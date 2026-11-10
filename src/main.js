import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { TurntableStage } from './stage.js';
import { CharacterController } from './character.js';
import { AnimationController } from './animator.js';
import { DriveImpactFX } from './shaders.js';
import { sfx } from './audio.js';
import { SF6_MOVE_DATA } from './data/sf6Moves.js';
import { FEMALE_ROSTER, FemaleRosterQueueManager } from './data/femaleRoster.js';
import { CombatInputEngine } from './combatEngine.js';

class App {
  constructor() {
    this.container = document.getElementById('canvas-container');
    this.currentFighterKey = 'chunli';
    this.currentCategory = 'all';
    this.searchQuery = '';
    this.initThree();
    this.initSceneObjects();
    this.initUI();
    this.initFrameDataModal();
    this.initDragAndDrop();
    this.animate();
    setTimeout(() => this.updateAITelemetryUI(), 1000);
  }

  initThree() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0a0c10);
    this.scene.fog = new THREE.FogExp2(0x0a0c10, 0.08);

    this.camera = new THREE.PerspectiveCamera(
      42,
      window.innerWidth / window.innerHeight,
      0.1,
      50
    );
    this.camera.position.set(0, 1.25, 3.8);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;
    this.container.appendChild(this.renderer.domElement);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.06;
    this.controls.target.set(0, 1.05, 0);
    this.controls.minDistance = 1.0;
    this.controls.maxDistance = 6.5;
    this.controls.maxPolarAngle = Math.PI / 2 + 0.05;

    this.clock = new THREE.Clock();

    window.addEventListener('resize', () => this.onWindowResize());

    this.targetCamPos = this.camera.position.clone();
    this.targetLookAt = this.controls.target.clone();
    this.isTransitioningCam = false;
  }

  initSceneObjects() {
    this.stage = new TurntableStage(this.scene);
    this.driveImpactFX = new DriveImpactFX(this.scene);
    this.character = new CharacterController(this.scene, this.stage.turntableGroup);
    this.animator = new AnimationController(this.character, this.driveImpactFX);
    this.combatEngine = new CombatInputEngine(this, this.character, this.driveImpactFX);
  }

  initUI() {
    // 1. Navigation Tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sfx.playClick();
        tabBtns.forEach(b => b.classList.remove('active'));
        tabPanels.forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        const tabId = btn.getAttribute('data-tab');
        const panel = document.getElementById(`panel-${tabId}`);
        if (panel) panel.classList.add('active');

        // Auto-load 3D character when switching tabs
        if (tabId === 'samus') {
          // Immediately load Samus Varia Suit on turntable if not already on Samus
          if (this.currentFighterKey !== 'samus') {
            const activeSuitBtn = document.querySelector('.suit-chip-btn.active') || document.getElementById('btn-samus-varia');
            if (activeSuitBtn) activeSuitBtn.click();
          }
        } else if (tabId === 'chunli') {
          // Immediately restore Chun-Li on turntable
          if (this.currentFighterKey !== 'chunli') {
            const activeChunLiCard = document.querySelector('.chunli-card.active') || document.getElementById('btn-load-chunli-sf6');
            if (activeChunLiCard) activeChunLiCard.click();
          }
        } else if (tabId === 'roster') {
          // Ensure female roster grid is refreshed and visible
          this.renderFemaleRosterGrid(this.currentCategory || 'all');
        }
      });
    });

    // 2. Turntable Controls
    const btnTurntableToggle = document.getElementById('btn-turntable-toggle');
    const sliderTurntableSpeed = document.getElementById('slider-turntable-speed');

    btnTurntableToggle.addEventListener('click', () => {
      sfx.playClick();
      this.stage.isRotating = !this.stage.isRotating;
      btnTurntableToggle.classList.toggle('active', this.stage.isRotating);
      btnTurntableToggle.textContent = this.stage.isRotating ? '⏸ Pausar Giro' : '▶ Reanudar Giro';
    });

    sliderTurntableSpeed.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      this.stage.rotationSpeed = val;
    });

    // 3. SF6 Drive Impact Trigger
    const btnDriveImpact = document.getElementById('btn-drive-impact');
    if (btnDriveImpact) {
      btnDriveImpact.addEventListener('click', () => {
        this.animator.setState('taunt', true);
      });
    }

    // 4. Chun-Li Hub Variants (Exclusively the 3 Official Variants)
    const btnLoadChunLiSF6 = document.getElementById('btn-load-chunli-sf6');
    const btnLoadChunLiFNClassic = document.getElementById('btn-load-chunli-fn-classic');
    const btnLoadChunLiFNNostalgia = document.getElementById('btn-load-chunli-fn-nostalgia');

    const markActiveFighterCard = (activeEl) => {
      document.querySelectorAll('.fighter-card').forEach(c => c.classList.remove('active'));
      if (activeEl) activeEl.classList.add('active');
    };

    // Variant 1: Official Capcom SF6 Chun-Li Organic PBR (4K Textures & Native Animations)
    if (btnLoadChunLiSF6) {
      btnLoadChunLiSF6.addEventListener('click', () => {
        sfx.playWhoosh();
        markActiveFighterCard(btnLoadChunLiSF6);
        this.currentFighterKey = 'chunli';
        this.character.currentModelName = 'Chun-Li SF6 Oficial (Capcom RE-Engine 4K)';
        this.character.loadExternalModel('/models/chunli_sf6_animated.glb', () => {
          this.stage.setNeonColor('#00f5d4');
          this.character.playAnimation('Idle_Combat', true);
          this.updateAITelemetryUI();
          this.character.applyCustomization();
        });
      });
    }

    // Variant 2: Fortnite Chun-Li Classic (Qipao, Spiked Wristbands)
    if (btnLoadChunLiFNClassic) {
      btnLoadChunLiFNClassic.addEventListener('click', () => {
        sfx.playWhoosh();
        markActiveFighterCard(btnLoadChunLiFNClassic);
        this.currentFighterKey = 'chunli';
        this.character.currentModelName = 'Chun-Li Qipao Clásico (Fortnite HD)';
        this.character.loadExternalModel('/models/chunli_fortnite_classic.glb', () => {
          this.stage.setNeonColor('#ffb703');
          this.character.playAnimation('Idle_Combat', true);
          this.updateAITelemetryUI();
          this.character.applyCustomization();
        });
      });
    }

    // Variant 3: Fortnite Chun-Li Nostalgia (Alpha Bodysuit, Sneakers)
    if (btnLoadChunLiFNNostalgia) {
      btnLoadChunLiFNNostalgia.addEventListener('click', () => {
        sfx.playWhoosh();
        markActiveFighterCard(btnLoadChunLiFNNostalgia);
        this.currentFighterKey = 'chunli';
        this.character.currentModelName = 'Chun-Li Nostalgia (Alpha Bodysuit HD)';
        this.character.loadExternalModel('/models/chunli_fortnite_nostalgia.glb', () => {
          this.stage.setNeonColor('#00b4d8');
          this.character.playAnimation('Idle_Combat', true);
          this.updateAITelemetryUI();
          this.character.applyCustomization();
        });
      });
    }

    // 4B. Samus Aran Locker Hub (Metroid Prime -> Dread: All 5 Suits)
    const samusSuits = [
      { id: 'btn-samus-varia', model: '/models/samus_varia_suit.glb', neon: '#ff9e00', name: 'Samus Aran (Varia Suit Chozo)' },
      { id: 'btn-samus-zero', model: '/models/samus_zero_suit.glb', neon: '#00f5d4', name: 'Zero Suit Samus (Bodysuit)' },
      { id: 'btn-samus-dread', model: '/models/samus_dread_suit.glb', neon: '#00ffff', name: 'Samus Aran (Metroid Dread)' },
      { id: 'btn-samus-gravity', model: '/models/samus_gravity_suit.glb', neon: '#9d4edd', name: 'Samus Aran (Gravity Suit)' },
      { id: 'btn-samus-phazon', model: '/models/samus_phazon_suit.glb', neon: '#ff0055', name: 'Samus Aran (Phazon Suit)' }
    ];

    const markActiveSuitChip = (btnEl) => {
      document.querySelectorAll('.suit-chip-btn').forEach(c => c.classList.remove('active'));
      if (btnEl) btnEl.classList.add('active');
    };

    samusSuits.forEach(s => {
      const btn = document.getElementById(s.id);
      if (btn) {
        btn.addEventListener('click', () => {
          sfx.playWhoosh();
          markActiveSuitChip(btn);
          this.currentFighterKey = 'samus';
          this.character.currentModelName = s.name;
          this.character.loadExternalModel(s.model, () => {
            this.stage.setNeonColor(s.neon);
            this.character.playAnimation('Idle_Combat', true);
            this.updateAITelemetryUI();
            this.character.applyCustomization();
          });
        });
      }
    });

    // Samus Combat Actions
    const btnSamusCharge = document.getElementById('btn-samus-charge');
    const btnSamusScrew = document.getElementById('btn-samus-screw');
    const btnSamusMissile = document.getElementById('btn-samus-missile');
    const btnSamusGuard = document.getElementById('btn-samus-guard');
    const btnSamusVictory = document.getElementById('btn-samus-victory');
    const btnSamusTaunt = document.getElementById('btn-samus-taunt');

    if (btnSamusCharge) {
      btnSamusCharge.addEventListener('click', () => {
        sfx.playDriveImpact();
        const impactPos = new THREE.Vector3(0, 1.25, 0.6);
        this.driveImpactFX.trigger(impactPos);
        this.character.playAnimation('Charge_Shot', false);
        this.punchCamera(0.35);
        this.showMoveTelemetry('samus', 'charge');
      });
    }

    if (btnSamusScrew) {
      btnSamusScrew.addEventListener('click', () => {
        sfx.playSpinningBirdKick();
        this.character.playAnimation('Screw_Attack', false);
        this.shakeCamera(0.3);
        this.showMoveTelemetry('samus', 'screw');
      });
    }

    if (btnSamusMissile) {
      btnSamusMissile.addEventListener('click', () => {
        sfx.playTenshokyaku();
        this.character.playAnimation('Missile_Fire', false);
        this.punchCamera(0.25);
        this.showMoveTelemetry('samus', 'missile');
      });
    }

    if (btnSamusGuard) {
      btnSamusGuard.addEventListener('click', () => {
        sfx.playClick();
        this.character.playAnimation('Idle_Combat', true);
        this.showMoveTelemetry('samus', 'guard');
      });
    }

    if (btnSamusVictory) {
      btnSamusVictory.addEventListener('click', () => {
        sfx.playChunLiVictory();
        this.character.playAnimation('Victory', false);
        this.showMoveTelemetry('samus', 'victory');
      });
    }

    if (btnSamusTaunt) {
      btnSamusTaunt.addEventListener('click', () => {
        sfx.playTaunt();
        this.character.playAnimation('Taunt', false);
        this.showMoveTelemetry('samus', 'taunt');
      });
    }

    // Initialize Female Roster UI
    this.initFemaleRosterUI();

    // 4B. Combat Move Actions (Playable directly on the turntable)
    // 1. Patada Relámpago (Hyakuretsukyaku)
    const triggerLightningKick = () => {
      sfx.playLightningKick();
      sfx.playChunLiKiai();
      if (this.character.isUsingExternalModel) {
        this.character.playAnimation('Lightning_Kick', false);
      } else {
        this.animator.setState('kick', true);
      }
      this.punchCamera(0.25);
      this.showMoveTelemetry(this.currentFighterKey, 'lightning');
    };

    // 2. Spinning Bird Kick (Helicóptero 360°)
    const triggerSpinningBirdKick = () => {
      sfx.playSpinningBirdKick();
      if (this.character.isUsingExternalModel) {
        this.character.playAnimation('Spinning_Bird_Kick', false);
      } else {
        this.animator.setState('kick', true);
      }
      this.shakeCamera(0.25);
      this.showMoveTelemetry(this.currentFighterKey, 'spinning-bird');
    };

    // 3. SF6 Drive Impact
    const triggerDriveImpact = () => {
      sfx.playDriveImpact();
      sfx.playChunLiKiai();
      const impactPos = new THREE.Vector3(0, 1.2, 0.4);
      this.driveImpactFX.trigger(impactPos);
      if (this.character.isUsingExternalModel) {
        this.character.playAnimation('Drive_Impact', false);
      } else {
        this.animator.setState('taunt', true);
      }
      this.shakeCamera(0.35);
      this.showMoveTelemetry(this.currentFighterKey, 'stand-heavy-punch');
    };

    // 4. Tenshokyaku (Patadas Aéreas Ascendentes)
    const triggerTenshokyaku = () => {
      sfx.playTenshokyaku();
      if (this.character.isUsingExternalModel) {
        this.character.playAnimation('Tenshokyaku', false);
      } else {
        this.animator.setState('kick', true);
      }
      this.punchCamera(0.2);
      this.showMoveTelemetry(this.currentFighterKey, 'tensho');
    };

    // 5. Kikosho (Super Art Chi Blast)
    const triggerKikosho = () => {
      sfx.playKikosho();
      const impactPos = new THREE.Vector3(0, 1.2, 0.5);
      this.driveImpactFX.trigger(impactPos);
      if (this.character.isUsingExternalModel) {
        this.character.playAnimation('Kikosho', false);
      } else {
        this.animator.setState('taunt', true);
      }
      this.shakeCamera(0.4);
      this.showMoveTelemetry(this.currentFighterKey, 'kikosho');
    };

    // 6. Guardia Kung Fu
    const triggerCombatGuard = () => {
      sfx.playClick();
      if (this.character.isUsingExternalModel) {
        this.character.playAnimation('Idle_Combat', true);
      } else {
        this.animator.setState('guard', true);
      }
      this.showMoveTelemetry(this.currentFighterKey, 'stand-light-punch');
    };

    // 7. Pose de Victoria
    const triggerVictory = () => {
      sfx.playChunLiVictory();
      if (this.character.isUsingExternalModel) {
        this.character.playAnimation('Victory', false);
      } else {
        this.animator.setState('taunt', true);
      }
      this.character.setVRMExpression('happy', 1.0);
    };

    // 8. Provocación (Taunt)
    const triggerTaunt = () => {
      sfx.playTaunt();
      if (this.character.isUsingExternalModel) {
        this.character.playAnimation('Taunt', false);
      } else {
        this.animator.setState('taunt', true);
      }
      this.character.setVRMExpression('blink', 1.0);
    };

    // Connect Sidebar Combat Buttons
    const btnCombatKick = document.getElementById('btn-combat-kick');
    const btnCombatSbk = document.getElementById('btn-combat-sbk');
    const btnCombatDrive = document.getElementById('btn-combat-drive');
    const btnCombatTensho = document.getElementById('btn-combat-tensho');
    const btnCombatKiko = document.getElementById('btn-combat-kiko');
    const btnCombatGuard = document.getElementById('btn-combat-guard');
    const btnCombatVictory = document.getElementById('btn-combat-victory');
    const btnCombatTaunt = document.getElementById('btn-combat-taunt');
    const btnOpenFrameData = document.getElementById('btn-open-framedata');

    if (btnOpenFrameData) {
      btnOpenFrameData.addEventListener('click', () => {
        sfx.playClick();
        this.openFrameDataModal();
      });
    }

    if (btnCombatKick) btnCombatKick.addEventListener('click', triggerLightningKick);
    if (btnCombatSbk) btnCombatSbk.addEventListener('click', triggerSpinningBirdKick);
    if (btnCombatDrive) btnCombatDrive.addEventListener('click', triggerDriveImpact);
    if (btnCombatTensho) btnCombatTensho.addEventListener('click', triggerTenshokyaku);
    if (btnCombatKiko) btnCombatKiko.addEventListener('click', triggerKikosho);
    if (btnCombatGuard) btnCombatGuard.addEventListener('click', triggerCombatGuard);
    if (btnCombatVictory) btnCombatVictory.addEventListener('click', triggerVictory);
    if (btnCombatTaunt) btnCombatTaunt.addEventListener('click', triggerTaunt);

    // Connect Floating Dock Combat Buttons
    const btnHudKick = document.getElementById('btn-hud-kick');
    const btnHudSbk = document.getElementById('btn-hud-sbk');
    const btnHudDrive = document.getElementById('btn-hud-drive');
    const btnHudTensho = document.getElementById('btn-hud-tensho');
    const btnHudKiko = document.getElementById('btn-hud-kiko');
    const btnHudGuard = document.getElementById('btn-hud-guard');
    const btnHudVictory = document.getElementById('btn-hud-victory');
    const btnHudTaunt = document.getElementById('btn-hud-taunt');

    if (btnHudKick) btnHudKick.addEventListener('click', triggerLightningKick);
    if (btnHudSbk) btnHudSbk.addEventListener('click', triggerSpinningBirdKick);
    if (btnHudDrive) btnHudDrive.addEventListener('click', triggerDriveImpact);
    if (btnHudTensho) btnHudTensho.addEventListener('click', triggerTenshokyaku);
    if (btnHudKiko) btnHudKiko.addEventListener('click', triggerKikosho);
    if (btnHudGuard) btnHudGuard.addEventListener('click', triggerCombatGuard);
    if (btnHudVictory) btnHudVictory.addEventListener('click', triggerVictory);
    if (btnHudTaunt) btnHudTaunt.addEventListener('click', triggerTaunt);

    // 5. VRM Facial Expressions & Morphs
    const exprBtns = document.querySelectorAll('.vrm-expr-btn');
    exprBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sfx.playClick();
        exprBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const expr = btn.getAttribute('data-expr');
        this.character.setVRMExpression(expr, 1.0);
      });
    });

    // 6. Animation Clips for 3D Models
    const animBtns = document.querySelectorAll('.anim-clip-btn');
    animBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sfx.playClick();
        animBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const anim = btn.getAttribute('data-anim');
        this.character.playAnimation(anim);
      });
    });

    const btnResetProcedural = document.getElementById('btn-reset-procedural');
    if (btnResetProcedural) {
      btnResetProcedural.addEventListener('click', () => {
        sfx.playClick();
        markActiveFighterCard(null);
        this.character.buildCharacter();
        this.character.applyCustomization();
        
        // Switch to Body & Morphs tab
        const tabBodyBtn = document.querySelector('[data-tab="morphs"]') || document.querySelector('[data-tab="body"]');
        if (tabBodyBtn) tabBodyBtn.click();
      });
    }

    // 6. Body Customization Sliders
    this.sliderDefs = [
      { id: 'slider-shoulder', key: 'shoulderWidth', valId: 'val-shoulder', factor: 1 },
      { id: 'slider-chest', key: 'chestDepth', valId: 'val-chest', factor: 1 },
      { id: 'slider-bust-size', key: 'bustSize', valId: 'val-bust-size', factor: 1 },
      { id: 'slider-bust-cup', key: 'bustCup', valId: 'val-bust-cup', factor: 1 },
      { id: 'slider-waist', key: 'waistWidth', valId: 'val-waist', factor: 1 },
      { id: 'slider-hip', key: 'hipWidth', valId: 'val-hip', factor: 1 },
      { id: 'slider-fat', key: 'bodyFat', valId: 'val-fat', factor: 100, suffix: '%' },
      { id: 'slider-glute-size', key: 'gluteSize', valId: 'val-glute-size', factor: 1 },
      { id: 'slider-thigh', key: 'thighWidth', valId: 'val-thigh', factor: 1 },
      { id: 'slider-calf', key: 'calfWidth', valId: 'val-calf', factor: 1 },
      { id: 'slider-muscle', key: 'muscularity', valId: 'val-muscle', factor: 100, suffix: '%' },
      { id: 'slider-height', key: 'height', valId: 'val-height', factor: 1 }
    ];

    this.sliderDefs.forEach(s => {
      const el = document.getElementById(s.id);
      const valDisplay = document.getElementById(s.valId);
      if (el) {
        el.addEventListener('input', (e) => {
          const val = parseFloat(e.target.value);
          this.character.setParam(s.key, val);
          sfx.playSliderTick();
          if (valDisplay) {
            valDisplay.textContent = s.suffix ? `${Math.round(val * s.factor)}${s.suffix}` : val.toFixed(2);
          }
        });
      }
    });

    // Glute Shape Selector Buttons
    const shapeBtns = document.querySelectorAll('.shape-btn');
    shapeBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sfx.playClick();
        shapeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const shape = btn.getAttribute('data-shape');
        this.character.setParam('gluteShape', shape);
      });
    });

    // Smart AI Morph Presets (Chun-Li, Samus, Hourglass, Muscular, Neutral)
    const presetBtns = document.querySelectorAll('.preset-chip');
    presetBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sfx.playClick();
        presetBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const preset = btn.getAttribute('data-preset');
        this.applySmartMorphPreset(preset);
      });
    });

    // Reset Morphs Button
    const btnResetMorphs = document.getElementById('btn-reset-morphs');
    if (btnResetMorphs) {
      btnResetMorphs.addEventListener('click', () => {
        sfx.playClick();
        this.applySmartMorphPreset('neutral');
        if (this.character.deformer) this.character.deformer.resetSensitivity();
        document.querySelectorAll('.sens-slider').forEach(s => s.value = 1.0);
      });
    }

    // Recalibrate AI Button
    const btnRecalibrateAI = document.getElementById('btn-recalibrate-ai');
    if (btnRecalibrateAI) {
      btnRecalibrateAI.addEventListener('click', () => {
        sfx.playWhoosh();
        if (this.character.isUsingExternalModel && this.character.externalModel) {
          this.character.deformer.calibrate(
            this.character.externalModel,
            this.character.currentModelName || 'Chun-Li SF6 Oficial',
            this.character.isVRM
          );
        } else {
          this.character.deformer.calibrate(this.character.characterGroup, 'Malla Paramétrica SF6', false);
        }
        this.updateAITelemetryUI();
        this.character.applyCustomization();
      });
    }

    // Fine-Tuning Sensitivity Sliders (Modo Editor)
    const sensSliders = document.querySelectorAll('.sens-slider');
    sensSliders.forEach(slider => {
      slider.addEventListener('input', (e) => {
        const ch = e.target.getAttribute('data-channel');
        const val = parseFloat(e.target.value);
        if (this.character.deformer) {
          this.character.deformer.setSensitivity(ch, val);
        }
      });
    });

    // 7. Outfit Selector
    const outfitBtns = document.querySelectorAll('.outfit-btn');
    outfitBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sfx.playClick();
        outfitBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const outfit = btn.getAttribute('data-outfit');
        this.character.setParam('outfitType', outfit);
      });
    });

    // Color Pickers
    const pickerSkin = document.getElementById('picker-skin');
    const pickerPrimary = document.getElementById('picker-outfit-primary');
    const pickerSecondary = document.getElementById('picker-outfit-secondary');
    const pickerAccent = document.getElementById('picker-outfit-accent');

    if (pickerSkin) pickerSkin.addEventListener('input', (e) => this.character.setParam('skinColor', e.target.value));
    if (pickerPrimary) pickerPrimary.addEventListener('input', (e) => this.character.setParam('outfitPrimary', e.target.value));
    if (pickerSecondary) pickerSecondary.addEventListener('input', (e) => this.character.setParam('outfitSecondary', e.target.value));
    if (pickerAccent) pickerAccent.addEventListener('input', (e) => this.character.setParam('accentColor', e.target.value));

    // 8. Animation Poses Buttons
    const poseBtns = document.querySelectorAll('.pose-btn');
    poseBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sfx.playClick();
        poseBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const pose = btn.getAttribute('data-pose');
        this.animator.setState(pose, true);
      });
    });

    const checkAutoCycle = document.getElementById('check-autocycle');
    if (checkAutoCycle) {
      checkAutoCycle.addEventListener('change', (e) => {
        sfx.playClick();
        this.animator.toggleAutoCycle(e.target.checked);
      });
    }

    // 9. Shaders Mode
    const shaderBtns = document.querySelectorAll('.shader-btn');
    shaderBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sfx.playClick();
        shaderBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const mode = btn.getAttribute('data-shader');
        this.character.setParam('shaderMode', mode);
      });
    });

    // 10. Camera Quick Presets
    const camBtns = document.querySelectorAll('.cam-btn');
    camBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sfx.playClick();
        camBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const view = btn.getAttribute('data-view');
        this.setCameraPreset(view);
      });
    });
  }

  syncSlidersFromParams() {
    const p = this.character.params;
    this.sliderDefs.forEach(s => {
      const el = document.getElementById(s.id);
      const valDisplay = document.getElementById(s.valId);
      if (el && p[s.key] !== undefined) {
        el.value = p[s.key];
        if (valDisplay) {
          valDisplay.textContent = s.suffix ? `${Math.round(p[s.key] * s.factor)}${s.suffix}` : p[s.key].toFixed(2);
        }
      }
    });

    // Sync glute shape button
    const shapeBtns = document.querySelectorAll('.shape-btn');
    shapeBtns.forEach(b => {
      b.classList.toggle('active', b.getAttribute('data-shape') === p.gluteShape);
    });

    // Sync color pickers
    const pickerSkin = document.getElementById('picker-skin');
    const pickerPrimary = document.getElementById('picker-outfit-primary');
    const pickerSecondary = document.getElementById('picker-outfit-secondary');
    const pickerAccent = document.getElementById('picker-outfit-accent');

    if (pickerSkin) pickerSkin.value = p.skinColor;
    if (pickerPrimary) pickerPrimary.value = p.outfitPrimary;
    if (pickerSecondary) pickerSecondary.value = p.outfitSecondary;
    if (pickerAccent) pickerAccent.value = p.accentColor;
  }

  updateAITelemetryUI() {
    if (!this.character || !this.character.deformer) return;
    const t = this.character.deformer.getTelemetry();
    if (!t) return;

    const elConf = document.getElementById('ai-telemetry-confidence');
    const elModel = document.getElementById('ai-telemetry-model');
    const elRig = document.getElementById('ai-telemetry-rig');
    const elBones = document.getElementById('ai-telemetry-bones');
    const elChannels = document.getElementById('ai-telemetry-channels');

    if (elConf) elConf.textContent = `${t.confidence.toFixed(1)}% EXACTITUD`;
    if (elModel) elModel.textContent = this.character.currentModelName || t.modelName || 'Chun-Li SF6 Oficial';
    if (elRig) elRig.textContent = t.rigType;
    if (elBones) elBones.textContent = `${t.boneCount} huesos / ${t.meshCount} mallas`;
    if (elChannels && t.detectedBones) {
      elChannels.innerHTML = `
        <span class="ai-pill">👙 Busto: ${t.detectedBones.busto || 0}</span>
        <span class="ai-pill">⏳ Cintura: ${t.detectedBones.cintura || 0}</span>
        <span class="ai-pill">📐 Cadera: ${t.detectedBones.cadera || 0}</span>
        <span class="ai-pill">🍑 Glúteos: ${t.detectedBones.gluteos || 0}</span>
        <span class="ai-pill">🦵 Muslos: ${t.detectedBones.muslos || 0}</span>
        <span class="ai-pill">🦶 Gemelos: ${t.detectedBones.gemelos || 0}</span>
      `;
    }
  }

  applySmartMorphPreset(preset) {
    let p = {};
    if (preset === 'chunli') {
      p = {
        bustSize: 1.25,
        bustCup: 1.20,
        waistWidth: 0.82,
        hipWidth: 1.35,
        gluteSize: 1.45,
        gluteShape: 'heart',
        thighWidth: 1.62,
        calfWidth: 1.28,
        height: 1.0,
        muscularity: 0.75,
        bodyFat: 0.14
      };
    } else if (preset === 'samus') {
      p = {
        bustSize: 1.15,
        bustCup: 1.10,
        waistWidth: 0.88,
        hipWidth: 1.18,
        gluteSize: 1.25,
        gluteShape: 'teardrop',
        thighWidth: 1.25,
        calfWidth: 1.15,
        height: 1.05,
        muscularity: 0.85,
        bodyFat: 0.08
      };
    } else if (preset === 'hourglass') {
      p = {
        bustSize: 1.35,
        bustCup: 1.30,
        waistWidth: 0.75,
        hipWidth: 1.45,
        gluteSize: 1.40,
        gluteShape: 'heart',
        thighWidth: 1.35,
        calfWidth: 1.10,
        height: 1.0,
        muscularity: 0.60,
        bodyFat: 0.16
      };
    } else if (preset === 'muscular') {
      p = {
        bustSize: 1.10,
        bustCup: 1.05,
        waistWidth: 0.90,
        hipWidth: 1.10,
        gluteSize: 1.30,
        gluteShape: 'oval',
        thighWidth: 1.45,
        calfWidth: 1.30,
        height: 1.02,
        muscularity: 1.0,
        bodyFat: 0.05
      };
    } else { // neutral
      p = {
        bustSize: 1.0,
        bustCup: 1.0,
        waistWidth: 1.0,
        hipWidth: 1.0,
        gluteSize: 1.0,
        gluteShape: 'round',
        thighWidth: 1.0,
        calfWidth: 1.0,
        height: 1.0,
        muscularity: 0.5,
        bodyFat: 0.15
      };
    }

    Object.assign(this.character.params, p);
    this.character.applyCustomization();
    this.syncSlidersFromParams();
  }

  setCameraPreset(view) {
    if (view === 'full') {
      this.animateCameraTo(new THREE.Vector3(0, 1.25, 3.8), new THREE.Vector3(0, 1.05, 0));
    } else if (view === 'bust') {
      this.animateCameraTo(new THREE.Vector3(0, 1.45, 1.6), new THREE.Vector3(0, 1.35, 0));
    } else if (view === 'glutes') {
      this.animateCameraTo(new THREE.Vector3(0, 0.95, -1.8), new THREE.Vector3(0, 0.9, 0));
    } else if (view === 'legs') {
      this.animateCameraTo(new THREE.Vector3(0, 0.6, 2.1), new THREE.Vector3(0, 0.5, 0));
    } else if (view === 'face') {
      this.animateCameraTo(new THREE.Vector3(0, 1.7, 1.0), new THREE.Vector3(0, 1.62, 0));
    }
  }

  animateCameraTo(targetPos, targetLookAt) {
    this.targetCamPos = targetPos;
    this.targetLookAt = targetLookAt;
    this.isTransitioningCam = true;
  }

  punchCamera(intensity = 0.25) {
    const dir = new THREE.Vector3().subVectors(this.controls.target, this.camera.position).normalize();
    const originalPos = this.camera.position.clone();
    this.camera.position.addScaledVector(dir, intensity);
    setTimeout(() => {
      this.animateCameraTo(originalPos, this.controls.target);
    }, 140);
  }

  shakeCamera(duration = 0.35) {
    const originalPos = this.camera.position.clone();
    const startTime = performance.now();
    const shake = () => {
      const elapsed = (performance.now() - startTime) / 1000;
      if (elapsed < duration) {
        const factor = (1 - elapsed / duration) * 0.12;
        this.camera.position.x = originalPos.x + (Math.random() - 0.5) * factor;
        this.camera.position.y = originalPos.y + (Math.random() - 0.5) * factor;
        this.camera.position.z = originalPos.z + (Math.random() - 0.5) * factor;
        requestAnimationFrame(shake);
      } else {
        this.camera.position.copy(originalPos);
      }
    };
    shake();
  }

  initDragAndDrop() {
    const dropOverlay = document.getElementById('drop-overlay');

    window.addEventListener('dragover', (e) => {
      e.preventDefault();
      if (dropOverlay) dropOverlay.classList.add('active');
    });

    window.addEventListener('dragleave', (e) => {
      if (e.relatedTarget === null && dropOverlay) {
        dropOverlay.classList.remove('active');
      }
    });

    window.addEventListener('drop', (e) => {
      e.preventDefault();
      if (dropOverlay) dropOverlay.classList.remove('active');

      const file = e.dataTransfer.files[0];
      if (file && (file.name.endsWith('.glb') || file.name.endsWith('.gltf') || file.name.endsWith('.vrm'))) {
        const url = URL.createObjectURL(file);
        sfx.playWhoosh();
        this.character.currentModelName = file.name;
        this.character.loadExternalModel(url, () => {
          console.log(`Modelo ${file.name} cargado exitosamente en la tornamesa.`);
          this.updateAITelemetryUI();
          this.character.applyCustomization();
        }, (err) => {
          console.error("Error al cargar modelo:", err);
        });
      }
    });
  }

  initFemaleRosterUI() {
    const grid = document.getElementById('roster-fighters-grid');
    if (!grid) return;

    this.queueManager = new FemaleRosterQueueManager(FEMALE_ROSTER, (fighterId, status) => {
      this.updateRosterCardStatus(fighterId, status);
    });

    const filterBtns = document.querySelectorAll('.universe-filter-btn');
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sfx.playClick();
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.getAttribute('data-filter');
        this.renderFemaleRosterGrid(filter);
      });
    });

    this.renderFemaleRosterGrid('all');
  }

  renderFemaleRosterGrid(filter = 'all') {
    const grid = document.getElementById('roster-fighters-grid');
    if (!grid) return;

    const filtered = filter === 'all' 
      ? FEMALE_ROSTER 
      : FEMALE_ROSTER.filter(f => f.universe === filter);

    grid.innerHTML = filtered.map(f => {
      const status = this.queueManager ? this.queueManager.getStatus(f.id) : { status: 'ready' };
      const statusClass = status.status === 'ready' ? 'ready' : (status.status === 'loading' ? 'queued' : 'retry');
      const statusLabel = status.status === 'ready' ? 'DISPONIBLE 3D' : (status.status === 'loading' ? 'CARGANDO...' : 'REINTENTO EN COLA');

      return `
        <div class="roster-card fighter-card" data-fighter-id="${f.id}" id="card-roster-${f.id}">
          <div class="roster-card-header">
            <span class="fighter-badge ${f.badgeColor || 'sf6-pink'}">${f.badge}</span>
            <span class="roster-queue-badge ${statusClass}" id="badge-status-${f.id}">[${statusLabel}]</span>
          </div>
          <div class="fighter-title">${f.name}</div>
          <div class="fighter-sub" style="color: var(--neon-cyan); font-weight: 600; font-size: 11px;">${f.title}</div>
          <div class="fighter-sub">${f.desc}</div>
        </div>
      `;
    }).join('');

    // Connect clicks on roster cards
    grid.querySelectorAll('.roster-card').forEach(card => {
      card.addEventListener('click', () => {
        const fighterId = card.getAttribute('data-fighter-id');
        const fighter = FEMALE_ROSTER.find(f => f.id === fighterId);
        if (!fighter) return;

        sfx.playWhoosh();
        document.querySelectorAll('.roster-card').forEach(c => c.classList.remove('active'));
        card.classList.add('active');

        this.currentFighterKey = fighter.id === 'samus_aran' ? 'samus' : 'chunli';

        if (this.queueManager) this.queueManager.markProcessing(fighter.id);

        this.character.currentModelName = `${fighter.name} (${fighter.universeName})`;
        this.character.loadExternalModel(fighter.modelUrl, () => {
          if (this.queueManager) this.queueManager.markReady(fighter.id);
          this.stage.setNeonColor(fighter.neonColor || '#00f5d4');
          this.character.playAnimation('Idle_Combat', true);
          this.updateAITelemetryUI();
          this.character.applyCustomization();
        }, (err) => {
          if (this.queueManager) this.queueManager.checkTimeoutFallback(fighter.id, 0);
        });
      });
    });
  }

  updateRosterCardStatus(fighterId, status) {
    const badge = document.getElementById(`badge-status-${fighterId}`);
    if (!badge) return;
    badge.className = `roster-queue-badge ${status.status === 'ready' ? 'ready' : (status.status === 'loading' ? 'queued' : 'retry')}`;
    badge.textContent = `[${status.status === 'ready' ? 'DISPONIBLE 3D' : (status.status === 'loading' ? 'CARGANDO...' : 'REINTENTO EN COLA')}]`;
  }

  showMoveTelemetry(fighterKey, moveQuery) {
    const hud = document.getElementById('combat-telemetry-hud');
    if (!hud) return;

    if (fighterKey === 'samus') {
      const samusMoves = {
        'charge': { name: 'CHARGE SHOT', name_ja: 'プラズマブラスト', input: 'HOLD + RELEASE', startup: '14', active: '6', recovery: '20', hitAdvantage: 'KD', blockAdvantage: '+3', damage: '1800', cancel: 'SUPER' },
        'screw': { name: 'SCREW ATTACK', name_ja: 'スクリューアタック', input: 'JUMP + 236K', startup: '9', active: '24', recovery: '18', hitAdvantage: 'LAUNCH', blockAdvantage: '-6', damage: '2100', cancel: '-' },
        'missile': { name: 'SUPER MISSILE', name_ja: 'スーパーミサイル', input: '236P', startup: '12', active: '8', recovery: '24', hitAdvantage: 'WALL BOUNCE', blockAdvantage: '-4', damage: '1400', cancel: '-' },
        'guard': { name: 'GUARDIA CHOZO', name_ja: 'チョウゾガード', input: '4/BACK', startup: '1', active: 'HOLD', recovery: '0', hitAdvantage: '-', blockAdvantage: '-', damage: '0', cancel: '-' },
        'victory': { name: 'MISIÓN CUMPLIDA', name_ja: 'ミッションクリア', input: 'VICTORY', startup: '1', active: 'HOLD', recovery: '0', hitAdvantage: '-', blockAdvantage: '-', damage: '0', cancel: '-' },
        'taunt': { name: 'DIAGNÓSTICO VISOR', name_ja: 'バイザーチェック', input: 'TAUNT', startup: '25', active: '10', recovery: '15', hitAdvantage: '-', blockAdvantage: '-', damage: '0', cancel: '-' }
      };
      const move = samusMoves[moveQuery.toLowerCase()] || samusMoves['charge'];
      document.getElementById('telemetry-fighter').textContent = 'SAMUS ARAN';
      document.getElementById('telemetry-move-name').textContent = move.name;
      document.getElementById('telemetry-move-ja').textContent = move.name_ja;
      document.getElementById('telemetry-move-input').textContent = move.input;
      document.getElementById('telemetry-startup').textContent = `${move.startup}f`;
      document.getElementById('telemetry-active').textContent = `${move.active}f`;
      document.getElementById('telemetry-recovery').textContent = `${move.recovery}f`;
      document.getElementById('telemetry-onhit').textContent = move.hitAdvantage;
      document.getElementById('telemetry-onblock').textContent = move.blockAdvantage;
      document.getElementById('telemetry-damage').textContent = move.damage;
      document.getElementById('telemetry-cancel').textContent = move.cancel;
      hud.classList.remove('hidden');
      if (this.telemetryTimeout) clearTimeout(this.telemetryTimeout);
      this.telemetryTimeout = setTimeout(() => { hud.classList.add('hidden'); }, 4500);
      return;
    }

    const moves = SF6_MOVE_DATA[fighterKey] || SF6_MOVE_DATA['chunli'];
    const q = moveQuery.toLowerCase();
    const move = moves.find(m => 
      m.slug.toLowerCase().includes(q) || 
      m.name.toLowerCase().includes(q) ||
      m.abbreviation.toLowerCase().includes(q)
    ) || moves[0];

    if (!move) return;

    document.getElementById('telemetry-fighter').textContent = fighterKey.toUpperCase();
    document.getElementById('telemetry-move-name').textContent = move.name.toUpperCase();
    document.getElementById('telemetry-move-ja').textContent = move.name_ja || '';
    document.getElementById('telemetry-move-input').textContent = move.input ? move.input.toUpperCase() : 'NORMAL';
    document.getElementById('telemetry-startup').textContent = `${move.startup}f`;
    document.getElementById('telemetry-active').textContent = `${move.active}f`;
    document.getElementById('telemetry-recovery').textContent = `${move.recovery}f`;
    document.getElementById('telemetry-onhit').textContent = move.hitAdvantage;
    document.getElementById('telemetry-onblock').textContent = move.blockAdvantage;
    document.getElementById('telemetry-damage').textContent = move.damage || '-';
    document.getElementById('telemetry-cancel').textContent = move.cancel || '-';

    hud.classList.remove('hidden');

    if (this.telemetryTimeout) clearTimeout(this.telemetryTimeout);
    this.telemetryTimeout = setTimeout(() => {
      hud.classList.add('hidden');
    }, 4500);
  }

  initFrameDataModal() {
    const modal = document.getElementById('framedata-modal');
    const btnClose = document.getElementById('btn-close-framedata');
    const backdrop = document.getElementById('fd-modal-backdrop');
    const searchInput = document.getElementById('fd-search-input');
    const fighterTabs = document.querySelectorAll('.fd-fighter-tab');
    const catBtns = document.querySelectorAll('.fd-cat-btn');

    if (btnClose) btnClose.addEventListener('click', () => this.closeFrameDataModal());
    if (backdrop) backdrop.addEventListener('click', () => this.closeFrameDataModal());

    fighterTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        fighterTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        this.currentFighterKey = tab.getAttribute('data-fighter');
        this.renderMovesList();
      });
    });

    catBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        catBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentCategory = btn.getAttribute('data-cat');
        this.renderMovesList();
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value.toLowerCase().trim();
        this.renderMovesList();
      });
    }
  }

  openFrameDataModal() {
    const modal = document.getElementById('framedata-modal');
    if (!modal) return;
    this.renderMovesList();
    modal.classList.remove('hidden');
  }

  closeFrameDataModal() {
    const modal = document.getElementById('framedata-modal');
    if (modal) modal.classList.add('hidden');
  }

  renderMovesList() {
    const container = document.getElementById('fd-moves-list');
    if (!container) return;

    const moves = SF6_MOVE_DATA[this.currentFighterKey] || [];
    const filtered = moves.filter(m => {
      // Category filter
      if (this.currentCategory !== 'all') {
        if (this.currentCategory === 'super') {
          if (!m.type.startsWith('super')) return false;
        } else if (m.type !== this.currentCategory) {
          return false;
        }
      }
      // Search filter
      if (this.searchQuery) {
        const matchesName = m.name.toLowerCase().includes(this.searchQuery);
        const matchesSlug = m.slug.toLowerCase().includes(this.searchQuery);
        const matchesInput = m.input.toLowerCase().includes(this.searchQuery);
        const matchesAbbr = m.abbreviation.toLowerCase().includes(this.searchQuery);
        if (!matchesName && !matchesSlug && !matchesInput && !matchesAbbr) return false;
      }
      return true;
    });

    if (filtered.length === 0) {
      container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted); font-size: 1.1rem;">No se encontraron movimientos coincidentes.</div>`;
      return;
    }

    container.innerHTML = filtered.map(m => `
      <div class="fd-card">
        <div class="fd-card-header">
          <div>
            <div class="fd-card-name">${m.name}</div>
            <div class="fd-card-ja">${m.name_ja || ''}</div>
          </div>
          <div class="fd-card-input">${m.input ? m.input.toUpperCase() : 'NORMAL'}</div>
        </div>
        <div class="fd-stats-table">
          <div class="fd-stat-item">
            <span class="s-lbl">STARTUP</span>
            <span class="s-val t-green">${m.startup}f</span>
          </div>
          <div class="fd-stat-item">
            <span class="s-lbl">ACTIVE</span>
            <span class="s-val t-yellow">${m.active}f</span>
          </div>
          <div class="fd-stat-item">
            <span class="s-lbl">HIT ADV</span>
            <span class="s-val t-cyan">${m.hitAdvantage}</span>
          </div>
          <div class="fd-stat-item">
            <span class="s-lbl">BLK ADV</span>
            <span class="s-val t-pink">${m.blockAdvantage}</span>
          </div>
        </div>
        <div class="fd-card-footer">
          <span class="fd-card-type">${m.type} • DMG ${m.damage || 0}</span>
          <button class="fd-exec-btn" data-slug="${m.slug}">
            <span>▶</span> Ejecutar en 3D
          </button>
        </div>
      </div>
    `).join('');

    // Connect execute buttons
    container.querySelectorAll('.fd-exec-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const slug = btn.getAttribute('data-slug');
        const move = moves.find(m => m.slug === slug);
        if (move) this.executeMoveFromData(move, this.currentFighterKey);
      });
    });
  }

  executeMoveFromData(move, fighterKey) {
    sfx.playClick();

    // 1. Play animation on character
    if (this.character.isUsingExternalModel) {
      const animName = move.anim || 'Drive_Impact';
      this.character.playAnimation(animName, false);
    } else {
      if (move.type === 'special' || move.type.includes('super')) {
        this.animator.setState('kick', true);
      } else {
        this.animator.setState('taunt', true);
      }
    }

    // 2. Play sound effects
    if (move.slug.includes('lightning') || move.slug.includes('hyakuretsu')) {
      sfx.playLightningKick();
      sfx.playChunLiKiai();
    } else if (move.slug.includes('spinning')) {
      sfx.playSpinningBirdKick();
    } else if (move.slug.includes('tensho')) {
      sfx.playTenshokyaku();
    } else if (move.slug.includes('kiko') || move.type.includes('super')) {
      sfx.playKikosho();
      const impactPos = new THREE.Vector3(0, 1.2, 0.4);
      this.driveImpactFX.trigger(impactPos);
    } else {
      sfx.playDriveImpact();
      sfx.playChunLiKiai();
    }

    // 3. Camera punch / shake
    this.punchCamera(0.25);

    // 4. Show telemetry HUD
    this.showMoveTelemetry(fighterKey, move.slug);

    // 5. Close modal
    this.closeFrameDataModal();
  }

  onWindowResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();

    this.stage.update(delta);
    this.character.update(delta);
    this.animator.update(delta);
    if (this.combatEngine) this.combatEngine.update(delta);
    this.driveImpactFX.update(delta);

    if (this.isTransitioningCam) {
      this.camera.position.lerp(this.targetCamPos, 0.08);
      this.controls.target.lerp(this.targetLookAt, 0.08);
      if (this.camera.position.distanceTo(this.targetCamPos) < 0.01) {
        this.camera.position.copy(this.targetCamPos);
        this.controls.target.copy(this.targetLookAt);
        this.isTransitioningCam = false;
      }
    }

    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  new App();
});
