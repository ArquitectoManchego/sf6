import * as THREE from 'three';
import { sfx } from './audio.js';

/**
 * CombatInputEngine - Motor de Combate y Control por Teclado Estilo Street Fighter 6
 * Interpreta secuencias de movimiento del teclado (236, 623, 214, cargas [2]8, dashes y golpes),
 * ejecuta las animaciones mocap con transiciones cinemáticas, Inverse Kinematics para pies,
 * hitstop, efectos visuales Drive Impact y sonidos de combate.
 */
export class CombatInputEngine {
  constructor(app, character, driveImpactFX) {
    this.app = app;
    this.char = character;
    this.driveImpactFX = driveImpactFX;

    this.keysDown = {};
    this.inputHistory = [];
    this.recentBuffer = []; // { key, time }
    this.bufferTimeoutMs = 500;

    // Estado del luchador en tiempo real
    this.state = 'idle'; // 'idle', 'walk_fwd', 'walk_back', 'crouch', 'jump', 'attack', 'hitstop'
    this.hitstopTimer = 0;
    this.isAirborne = false;
    this.verticalVelocity = 0;
    this.jumpY = 0;
    this.groundY = 0.20;

    // Mapeo de teclas de Arcade / Fighting Game
    // Movimiento: WASD o Flechas
    // Puñetazos: U / J (LP), I / K (MP), O / L (HP)
    // Patadas: B / N (LK), H / M (MK), Y / Comma (HK)
    // Especiales: Espacio / Shift (Drive Impact), P (Super Art), T (Taunt), V (Victory)
    this.keyMap = {
      // Direcciones
      'KeyW': 'UP',
      'ArrowUp': 'UP',
      'KeyS': 'DOWN',
      'ArrowDown': 'DOWN',
      'KeyA': 'BACK',
      'ArrowLeft': 'BACK',
      'KeyD': 'FORWARD',
      'ArrowRight': 'FORWARD',

      // Botones de Ataque
      'KeyU': 'LP',
      'KeyJ': 'LP',
      'KeyI': 'MP',
      'KeyK': 'MP',
      'KeyO': 'HP',
      'KeyL': 'HP',
      'KeyB': 'LK',
      'KeyN': 'LK',
      'KeyH': 'MK',
      'KeyM': 'MK',
      'KeyY': 'HK',
      'Comma': 'HK',
      'Period': 'HK',

      // Acciones SF6
      'Space': 'DRIVE',
      'ShiftLeft': 'DRIVE',
      'ShiftRight': 'DRIVE',
      'KeyP': 'SUPER',
      'KeyT': 'TAUNT',
      'KeyV': 'VICTORY'
    };

    this.initEventListeners();
    this.createVirtualArcadeHUD();
  }

  initEventListeners() {
    window.addEventListener('keydown', (e) => {
      // Ignorar eventos si el foco está en un input de texto
      if (e.target.tagName === 'INPUT' && e.target.type === 'text') return;

      const code = e.code;
      if (this.keysDown[code]) return; // Evitar repetición por pulsación continua
      this.keysDown[code] = true;

      const mapped = this.keyMap[code];
      if (mapped) {
        this.handleInputPress(mapped, code);
      }
    });

    window.addEventListener('keyup', (e) => {
      if (e.target.tagName === 'INPUT' && e.target.type === 'text') return;

      const code = e.code;
      this.keysDown[code] = false;

      const mapped = this.keyMap[code];
      if (mapped) {
        this.handleInputRelease(mapped, code);
      }
    });
  }

  handleInputPress(action, rawCode) {
    const now = performance.now();

    // Actualizar HUD visual de botones
    this.highlightHUDButton(action, true);

    // Añadir al buffer con timestamp
    this.recentBuffer.push({ action, time: now });
    this.cleanBuffer(now);

    // 1. Detectar secuencias complejas de juego de lucha (Motions)
    const detectedSpecial = this.detectSpecialMoveSequence();
    if (detectedSpecial) {
      this.executeSpecialMove(detectedSpecial);
      return;
    }

    // 2. Acciones individuales directas
    switch (action) {
      case 'LP':
        this.triggerNormalAttack('LP', 'jab', 0.12, 400);
        break;
      case 'MP':
        this.triggerNormalAttack('MP', 'mid_strike', 0.18, 700);
        break;
      case 'HP':
        this.triggerNormalAttack('HP', 'heavy_strike', 0.25, 1000);
        break;
      case 'LK':
        this.triggerNormalAttack('LK', 'light_kick', 0.14, 500);
        break;
      case 'MK':
        this.triggerNormalAttack('MK', 'mid_kick', 0.20, 800);
        break;
      case 'HK':
        this.triggerNormalAttack('HK', 'heavy_kick', 0.28, 1100);
        break;
      case 'DRIVE':
        this.triggerDriveImpact();
        break;
      case 'SUPER':
        this.triggerSuperArt();
        break;
      case 'TAUNT':
        this.triggerTaunt();
        break;
      case 'VICTORY':
        this.triggerVictory();
        break;
      case 'UP':
        this.triggerJump();
        break;
      case 'DOWN':
        this.setStance('crouch');
        break;
      case 'FORWARD':
        this.setStance('walk_fwd');
        break;
      case 'BACK':
        this.setStance('walk_back');
        break;
    }
  }

  handleInputRelease(action, rawCode) {
    this.highlightHUDButton(action, false);

    if (action === 'DOWN' || action === 'FORWARD' || action === 'BACK') {
      // Si no hay más teclas de movimiento presionadas, regresar a guardia
      if (!this.keysDown['KeyW'] && !this.keysDown['KeyS'] && !this.keysDown['KeyA'] && !this.keysDown['KeyD'] &&
          !this.keysDown['ArrowUp'] && !this.keysDown['ArrowDown'] && !this.keysDown['ArrowLeft'] && !this.keysDown['ArrowRight']) {
        this.setStance('idle');
      }
    }
  }

  cleanBuffer(now) {
    this.recentBuffer = this.recentBuffer.filter(b => now - b.time <= this.bufferTimeoutMs);
  }

  /**
   * Reconoce comandos de cruceta y secuencias especiales en el buffer (236, 623, 214, [2]8)
   */
  detectSpecialMoveSequence() {
    const actions = this.recentBuffer.map(b => b.action);
    const len = actions.length;
    if (len < 2) return null;

    const last = actions[len - 1];
    const isAttack = ['LP', 'MP', 'HP', 'LK', 'MK', 'HK'].includes(last);

    if (!isAttack) return null;

    // Detectar 236 + Attack (Hadoken / Hyakuretsukyaku / Spiral Arrow / Charge Shot)
    // Secuencia: DOWN -> FORWARD -> Attack
    for (let i = 0; i < len - 1; i++) {
      if (actions[i] === 'DOWN') {
        for (let j = i + 1; j < len - 1; j++) {
          if (actions[j] === 'FORWARD') {
            return { name: '236_MOTION', type: last };
          }
        }
      }
    }

    // Detectar 623 + Attack (Shoryuken / Tenshokyaku / Cannon Spike / Flip Kick)
    // Secuencia: FORWARD -> DOWN -> FORWARD -> Attack
    for (let i = 0; i < len - 2; i++) {
      if (actions[i] === 'FORWARD') {
        for (let j = i + 1; j < len - 1; j++) {
          if (actions[j] === 'DOWN') {
            for (let k = j + 1; k < len - 1; k++) {
              if (actions[k] === 'FORWARD') {
                return { name: '623_MOTION', type: last };
              }
            }
          }
        }
      }
    }

    // Detectar 214 + Attack (Tatsumaki / Senpu Kyaku / Fuhajin)
    // Secuencia: DOWN -> BACK -> Attack
    for (let i = 0; i < len - 1; i++) {
      if (actions[i] === 'DOWN') {
        for (let j = i + 1; j < len - 1; j++) {
          if (actions[j] === 'BACK') {
            return { name: '214_MOTION', type: last };
          }
        }
      }
    }

    // Detectar Carga [2]8 + Attack (Spinning Bird Kick / Screw Attack)
    // Secuencia: DOWN (mantenido) -> UP -> Attack
    for (let i = 0; i < len - 1; i++) {
      if (actions[i] === 'DOWN') {
        for (let j = i + 1; j < len - 1; j++) {
          if (actions[j] === 'UP') {
            return { name: 'CHARGE_UP_MOTION', type: last };
          }
        }
      }
    }

    return null;
  }

  executeSpecialMove(spec) {
    this.recentBuffer = []; // Consumir buffer

    if (spec.name === '236_MOTION') {
      // Hyakuretsukyaku / Spiral Arrow / Charge Shot
      sfx.playLightningKick();
      sfx.playChunLiKiai();
      this.playActionWithFeedback('Lightning_Kick', '236 + K: PATADA RELÁMPAGO', 1400);
      this.app.punchCamera(0.28);
      this.app.showMoveTelemetry(this.app.currentFighterKey, 'lightning');

    } else if (spec.name === 'CHARGE_UP_MOTION') {
      // Spinning Bird Kick / Screw Attack
      sfx.playSpinningBirdKick();
      this.playActionWithFeedback('Spinning_Bird_Kick', '[2]8 + K: SPINNING BIRD KICK', 1600);
      this.app.shakeCamera(0.32);
      this.app.showMoveTelemetry(this.app.currentFighterKey, 'spinning-bird');

    } else if (spec.name === '623_MOTION') {
      // Tenshokyaku / Cannon Spike
      sfx.playTenshokyaku();
      this.playActionWithFeedback('Tenshokyaku', '623 + K: TENSHOKYAKU ASCENDENTE', 1350);
      this.app.punchCamera(0.35);
      this.app.showMoveTelemetry(this.app.currentFighterKey, 'tensho');

    } else if (spec.name === '214_MOTION') {
      // Kikosho / Fuhajin / Senpu Kyaku
      sfx.playKikosho();
      const pos = new THREE.Vector3(0, 1.25, 0.5);
      this.driveImpactFX.trigger(pos);
      this.playActionWithFeedback('Drive_Impact', '214 + P: SPECIAL CHI STRIKE', 1500);
      this.app.shakeCamera(0.40);
      this.app.showMoveTelemetry(this.app.currentFighterKey, 'kikosho');
    }
  }

  triggerNormalAttack(button, type, punchIntensity, damage) {
    sfx.playWhoosh();
    const isKick = button.includes('K');
    const animName = isKick ? 'Lightning_Kick' : 'Drive_Impact';

    this.playActionWithFeedback(animName, `${button}: GOLPE ${type.toUpperCase()}`, damage);
    this.app.punchCamera(punchIntensity);
    this.app.showMoveTelemetry(this.app.currentFighterKey, isKick ? 'stand-heavy-kick' : 'stand-heavy-punch');
  }

  triggerDriveImpact() {
    sfx.playDriveImpact();
    sfx.playChunLiKiai();
    const impactPos = new THREE.Vector3(0, 1.25, 0.45);
    this.driveImpactFX.trigger(impactPos);

    this.playActionWithFeedback('Drive_Impact', '💥 SF6 DRIVE IMPACT (HITSTOP)', 2000);
    this.app.shakeCamera(0.45);
    this.triggerHitstop(8); // Congelar 8 fotogramas para impacto cinemático SF6
    this.app.showMoveTelemetry(this.app.currentFighterKey, 'stand-heavy-punch');
  }

  triggerSuperArt() {
    sfx.playKikosho();
    const impactPos = new THREE.Vector3(0, 1.25, 0.55);
    this.driveImpactFX.trigger(impactPos);

    this.playActionWithFeedback('Drive_Impact', '🔮 SUPER ART NIVEL 3: KIKOSHO', 2800);
    this.app.shakeCamera(0.5);
    this.app.showMoveTelemetry(this.app.currentFighterKey, 'kikosho');
  }

  triggerTaunt() {
    sfx.playTaunt();
    this.playActionWithFeedback('Taunt', '😏 PROVOCACIÓN: GOMEN NE!', 0);
    this.char.setVRMExpression('blink', 1.0);
  }

  triggerVictory() {
    sfx.playChunLiVictory();
    this.playActionWithFeedback('Victory', '🏆 VICTORIA: YATTA!', 0);
    this.char.setVRMExpression('happy', 1.0);
  }

  triggerJump() {
    if (this.isAirborne) return;
    this.isAirborne = true;
    this.verticalVelocity = 4.5;
    sfx.playWhoosh();
    this.playActionWithFeedback('Tenshokyaku', 'SALTO COMBATE VERTICAL', 0);
  }

  setStance(stance) {
    this.state = stance;
    if (stance === 'idle') {
      this.char.playAnimation('Idle_Combat', true, 0.2);
    } else if (stance === 'crouch') {
      this.char.playAnimation('Idle_Combat', true, 0.15);
      // Inclinar ligeramente el grupo del personaje
      if (this.char.characterGroup) {
        this.char.characterGroup.position.y = -0.15;
      }
    } else if (stance === 'walk_fwd') {
      this.char.playAnimation('Idle_Combat', true, 0.15);
      this.appendInputHistory('▶ AVANZAR');
    } else if (stance === 'walk_back') {
      this.char.playAnimation('Idle_Combat', true, 0.15);
      this.appendInputHistory('◀ RETROCEDER (GUARDIA)');
    }
  }

  playActionWithFeedback(animName, label, damage) {
    this.appendInputHistory(label);
    if (this.char.isUsingExternalModel) {
      this.char.playAnimation(animName, false, 0.12);
    } else if (this.app.animator) {
      this.app.animator.setState(animName.includes('Kick') ? 'kick' : 'taunt', true);
    }
  }

  triggerHitstop(frames = 6) {
    this.hitstopTimer = frames;
  }

  /**
   * Actualización por cada frame en el bucle principal de renderizado
   */
  update(delta) {
    // 1. Hitstop congelante de impacto
    if (this.hitstopTimer > 0) {
      this.hitstopTimer--;
      return; // Pausa breve el movimiento para sensación de impacto real
    }

    // 2. Física e Inverse Kinematics para Salto y Suelo
    if (this.isAirborne && this.char.externalModel) {
      this.jumpY += this.verticalVelocity * delta;
      this.verticalVelocity -= 14.0 * delta; // Gravedad

      if (this.jumpY <= 0) {
        this.jumpY = 0;
        this.isAirborne = false;
        this.verticalVelocity = 0;
        sfx.playSliderTick();
        this.setStance('idle');
      }

      // Desplazamiento vertical respetando piso
      this.char.externalModel.position.y = this.groundY + this.jumpY;
    } else if (this.char.externalModel && !this.isAirborne) {
      // Grounding IK para asegurar pies pegados al piso a y = 0.20
      if (this.state === 'crouch') {
        this.char.externalModel.position.y = this.groundY - 0.12;
      } else {
        this.char.externalModel.position.y = this.groundY;
      }
    }
  }

  /**
   * Crea el HUD visual interactivo estilo Arcade FightStick en pantalla
   */
  createVirtualArcadeHUD() {
    const existing = document.getElementById('arcade-fightstick-hud');
    if (existing) existing.remove();

    const hud = document.createElement('div');
    hud.id = 'arcade-fightstick-hud';
    hud.className = 'arcade-fightstick-hud';
    hud.innerHTML = `
      <div class="fightstick-inner">
        <div class="fightstick-header">
          <span class="fs-title">🎮 CONTROLES DE COMBATE SF6 (TECLADO)</span>
          <span class="fs-status">TECLADO ACTIVO</span>
        </div>
        
        <div class="fightstick-body">
          <!-- Stick Direccional -->
          <div class="fs-dpad">
            <div class="dpad-btn dpad-up" id="btn-fs-UP" title="W / Flecha Arriba (Salto)">▲</div>
            <div class="dpad-middle-row">
              <div class="dpad-btn dpad-left" id="btn-fs-BACK" title="A / Flecha Izq (Atrás/Guardia)">◀</div>
              <div class="dpad-center">●</div>
              <div class="dpad-btn dpad-right" id="btn-fs-FORWARD" title="D / Flecha Der (Avanzar)">▶</div>
            </div>
            <div class="dpad-btn dpad-down" id="btn-fs-DOWN" title="S / Flecha Abajo (Agacharse)">▼</div>
          </div>

          <!-- Botones de Acción -->
          <div class="fs-action-buttons">
            <div class="fs-btn-row">
              <button class="fs-arcade-btn btn-lp" id="btn-fs-LP" title="Tecla J / U">
                <span class="fs-key">J</span>
                <span class="fs-lbl">LP</span>
              </button>
              <button class="fs-arcade-btn btn-mp" id="btn-fs-MP" title="Tecla K / I">
                <span class="fs-key">K</span>
                <span class="fs-lbl">MP</span>
              </button>
              <button class="fs-arcade-btn btn-hp" id="btn-fs-HP" title="Tecla L / O">
                <span class="fs-key">L</span>
                <span class="fs-lbl">HP</span>
              </button>
            </div>
            <div class="fs-btn-row">
              <button class="fs-arcade-btn btn-lk" id="btn-fs-LK" title="Tecla B / N">
                <span class="fs-key">B</span>
                <span class="fs-lbl">LK</span>
              </button>
              <button class="fs-arcade-btn btn-mk" id="btn-fs-MK" title="Tecla M / H">
                <span class="fs-key">M</span>
                <span class="fs-lbl">MK</span>
              </button>
              <button class="fs-arcade-btn btn-hk" id="btn-fs-HK" title="Tecla , / Y">
                <span class="fs-key">,</span>
                <span class="fs-lbl">HK</span>
              </button>
            </div>
          </div>

          <!-- Botones Rápidos Especiales -->
          <div class="fs-specials-col">
            <button class="fs-special-btn btn-drive" id="btn-fs-DRIVE" title="Barra Espaciadora o Shift">
              <span class="sp-icon">💥</span>
              <span>DRIVE IMPACT [ESPACIO]</span>
            </button>
            <button class="fs-special-btn btn-super" id="btn-fs-SUPER" title="Tecla P">
              <span class="sp-icon">🔮</span>
              <span>SUPER ART [P]</span>
            </button>
          </div>
        </div>

        <!-- Registro de Inputs (Input History) -->
        <div class="fs-input-feed-wrap">
          <span class="fs-feed-label">HISTORIAL DE COMBATE:</span>
          <div class="fs-input-feed" id="fs-input-feed">
            <span class="fs-feed-item highlight">¡Motor Listo! Presiona WASD + J, K, L para pelear en la tornamesa</span>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(hud);

    // Conectar eventos click en botones virtuales del HUD para pantallas táctiles o móviles
    this.connectHUDTouchEvents();
  }

  connectHUDTouchEvents() {
    const actions = ['UP', 'DOWN', 'BACK', 'FORWARD', 'LP', 'MP', 'HP', 'LK', 'MK', 'HK', 'DRIVE', 'SUPER'];
    actions.forEach(act => {
      const el = document.getElementById(`btn-fs-${act}`);
      if (el) {
        el.addEventListener('mousedown', (e) => {
          e.preventDefault();
          this.handleInputPress(act, act);
        });
        el.addEventListener('mouseup', (e) => {
          e.preventDefault();
          this.handleInputRelease(act, act);
        });
        el.addEventListener('touchstart', (e) => {
          e.preventDefault();
          this.handleInputPress(act, act);
        });
        el.addEventListener('touchend', (e) => {
          e.preventDefault();
          this.handleInputRelease(act, act);
        });
      }
    });
  }

  highlightHUDButton(action, isPressed) {
    const el = document.getElementById(`btn-fs-${action}`);
    if (el) {
      el.classList.toggle('active', isPressed);
    }
  }

  appendInputHistory(text) {
    const feed = document.getElementById('fs-input-feed');
    if (!feed) return;

    const item = document.createElement('span');
    item.className = 'fs-feed-item';
    item.textContent = `▶ ${text}`;
    feed.appendChild(item);

    // Mantener sólo los últimos 5
    while (feed.children.length > 5) {
      feed.removeChild(feed.children[0]);
    }
  }
}
