/**
 * CATÁLOGO & COLA DE PROCESAMIENTO DE LUCHADORAS
 * Universos: Metroid, Street Fighter 6, Darkstalkers, KOF, Tekken, Dead or Alive, Fortnite
 */

export const FEMALE_ROSTER = [
  // ==========================================
  // METROID (SAMUS ARAN - TODOS SUS TRAJES)
  // ==========================================
  {
    id: 'samus_aran',
    name: 'Samus Aran',
    title: 'Cazarrecompensas Galáctica Interplanetaria',
    universe: 'metroid',
    universeName: 'Metroid',
    badge: '🚀 METROID PRIME -> DREAD',
    badgeColor: 'sf6-gold',
    combatArchetype: 'Chozo Power Armor & Arm Cannon Artillery',
    desc: 'La cazarrecompensas más legendaria de la galaxia. Equipada con tecnología Chozo ancestral, cañón de brazo multifrecuencia, visor escáner y alta movilidad.',
    modelUrl: '/models/samus_varia_suit.glb',
    neonColor: '#ff9e00',
    currentSuitId: 'varia',
    suits: [
      {
        id: 'varia',
        name: 'Varia Suit (Metroid Prime)',
        badge: '⚡ VARIA SUIT',
        modelUrl: '/models/samus_varia_suit.glb',
        desc: 'La icónica armadura Chozo: blindaje naranja y rojo de alta resistencia térmica, hombreras esféricas masivas y visor esmeralda.',
        neonColor: '#ff9e00'
      },
      {
        id: 'zero',
        name: 'Zero Suit Samus (Bodysuit)',
        badge: '🧬 ZERO SUIT',
        modelUrl: '/models/samus_zero_suit.glb',
        desc: 'Traje de operaciones táctico azul cobalto ceñido al cuerpo, coleta rubia, pistola aturdidora Paralyzer y botas jet con alta agilidad.',
        neonColor: '#00f5d4'
      },
      {
        id: 'dread',
        name: 'Dread Suit (Metroid Dread)',
        badge: '🛡️ METROID DREAD',
        modelUrl: '/models/samus_dread_suit.glb',
        desc: 'Última evolución biomecánica: placas de quitina blanca, tejido muscular cian eléctrico, núcleo carmesí angular y nuevo Arm Cannon.',
        neonColor: '#00ffff'
      },
      {
        id: 'gravity',
        name: 'Gravity Suit (Alta Gravedad)',
        badge: '🔮 GRAVITY SUIT',
        modelUrl: '/models/samus_gravity_suit.glb',
        desc: 'Protección gravitatoria y movimiento subacuático/magma: aleación púrpura y magenta con visor esmeralda.',
        neonColor: '#9d4edd'
      },
      {
        id: 'phazon',
        name: 'Phazon Suit (Corrupción Radiactiva)',
        badge: '☣️ PHAZON SUIT',
        modelUrl: '/models/samus_phazon_suit.glb',
        desc: 'Armadura infundida de Phazon puro: placas de obsidiana negra, ribetes plateados y visor carmesí de haz de plasma letal.',
        neonColor: '#ff0055'
      }
    ],
    moves: [
      { id: 'charge_shot', name: 'Charge Shot (Plasma Blast)', input: 'Hold Arm Cannon + Release', startup: '14f', active: '6f', recovery: '20f', hit: 'KD', block: '+3', damage: 1800, anim: 'Charge_Shot' },
      { id: 'screw_attack', name: 'Screw Attack (360° Energy Spin)', input: 'Jump + 236K', startup: '9f', active: '24f', recovery: '18f', hit: 'Launch', block: '-6', damage: 2100, anim: 'Screw_Attack' },
      { id: 'super_missile', name: 'Super Missile (Payload Launch)', input: '236P', startup: '12f', active: '8f', recovery: '24f', hit: 'Wall Bounce', block: '-4', damage: 1400, anim: 'Missile_Fire' },
      { id: 'scanner_guard', name: 'Guardia de Escáner Chozo', input: '4/Back Guard', startup: '1f', active: 'Hold', recovery: '0f', hit: '-', block: '-', damage: 0, anim: 'Idle_Combat' },
      { id: 'taunt_samus', name: 'Diagnóstico de Visor & Cannon', input: 'Taunt / HP+HK', startup: '25f', active: '10f', recovery: '15f', hit: '-', block: '-', damage: 0, anim: 'Taunt' },
      { id: 'victory_samus', name: 'Misión Cumplida (Victoria Chozo)', input: 'Victory Pose', startup: '1f', active: 'Hold', recovery: '0f', hit: '-', block: '-', damage: 0, anim: 'Victory' }
    ]
  },

  // ==========================================
  // STREET FIGHTER 6
  // ==========================================
  {
    id: 'chunli_sf6',
    name: 'Chun-Li',
    title: 'La Mujer Más Fuerte del Mundo',
    universe: 'sf6',
    universeName: 'Street Fighter 6',
    badge: '👑 CAPCOM RE-ENGINE 4K',
    badgeColor: 'sf6-pink',
    combatArchetype: 'Kung Fu Tradicional Chino & Patadas Relámpago',
    desc: 'Ex-agente de la ICPO y maestra del estilo de patadas chinas. Malla oficial con texturas PBR Capcom 4K y dinámicas de combate avanzadas.',
    modelUrl: '/models/chunli_sf6_animated.glb',
    neonColor: '#00f5d4',
    currentSuitId: 'sf6_official',
    suits: [
      {
        id: 'sf6_official',
        name: 'Chun-Li SF6 Oficial (Mesh Orgánico 4K)',
        badge: '👑 RE-ENGINE 4K',
        modelUrl: '/models/chunli_sf6_animated.glb',
        desc: 'Malla orgánica oficial extraída de SF6 con 19 submallas, 800 huesos y texturas PBR completas.',
        neonColor: '#00f5d4'
      },
      {
        id: 'fn_classic',
        name: 'Chun-Li Qipao Clásico (Crossover HD)',
        badge: '🥋 QIPAO CLÁSICO',
        modelUrl: '/models/chunli_fortnite_classic.glb',
        desc: 'Qipao azul real con bordados dorados, moños de chignon con cintas de seda blanca y muñequeras de púas.',
        neonColor: '#ffb703'
      },
      {
        id: 'fn_nostalgia',
        name: 'Chun-Li Nostalgia (Alpha Bodysuit HD)',
        badge: '⚡ ALPHA BODYSUIT',
        modelUrl: '/models/chunli_fortnite_nostalgia.glb',
        desc: 'Traje atlético de lycra ceñido estilo Street Fighter Alpha, zapatillas deportivas de combate y coleta atlética.',
        neonColor: '#00b4d8'
      }
    ],
    moves: [
      { id: 'lightning_kick', name: 'Patada Relámpago (Hyakuretsukyaku)', input: '236K', startup: '12f', active: '18f', recovery: '22f', hit: '+4', block: '-8', damage: 1200, anim: 'Lightning_Kick' },
      { id: 'spinning_bird_kick', name: 'Spinning Bird Kick (360°)', input: '[2]8K', startup: '10f', active: '22f', recovery: '25f', hit: 'KD', block: '-10', damage: 1500, anim: 'Spinning_Bird_Kick' },
      { id: 'tenshokyaku', name: 'Tenshokyaku (Ascendente)', input: '22K', startup: '6f', active: '14f', recovery: '28f', hit: 'Launch', block: '-18', damage: 1350, anim: 'Tenshokyaku' },
      { id: 'drive_impact', name: 'SF6 Drive Impact (Hitstop)', input: 'HP+HK', startup: '26f', active: '2f', recovery: '35f', hit: 'Crumple', block: '+3', damage: 800, anim: 'Drive_Impact' },
      { id: 'kikosho', name: 'Kikosho (Super Art Nvl 1)', input: '236236P', startup: '9f', active: '30f', recovery: '32f', hit: 'Hard KD', block: '-12', damage: 2400, anim: 'Kikosho' },
      { id: 'guard', name: 'Guardia Kung Fu', input: '4/Back', startup: '1f', active: 'Hold', recovery: '0f', hit: '-', block: '-', damage: 0, anim: 'Idle_Combat' },
      { id: 'taunt_chunli', name: 'Provocación (Gomen ne!)', input: 'Taunt', startup: '20f', active: '15f', recovery: '20f', hit: '-', block: '-', damage: 0, anim: 'Taunt' },
      { id: 'victory_chunli', name: 'Pose de Victoria (Yatta!)', input: 'Victory', startup: '1f', active: 'Hold', recovery: '0f', hit: '-', block: '-', damage: 0, anim: 'Victory' }
    ]
  },
  {
    id: 'cammy_sf6',
    name: 'Cammy White',
    title: 'Delta Red Killer Bee',
    universe: 'sf6',
    universeName: 'Street Fighter 6',
    badge: '🎖️ DELTA RED SF6',
    badgeColor: 'sf6-green',
    combatArchetype: 'Operaciones Especiales & Spiral Arrow',
    desc: 'Agente de operaciones especiales británica de élite. Extremadamente rápida con zancadas bajas, Spiral Arrow y Cannon Spike.',
    modelUrl: '/models/cammy_sf6.glb',
    neonColor: '#2ec4b6',
    moves: [
      { id: 'spiral_arrow', name: 'Spiral Arrow (Taladro de Piernas)', input: '236K', startup: '9f', active: '14f', recovery: '21f', hit: 'KD', block: '-12', damage: 1300, anim: 'Lightning_Kick' },
      { id: 'cannon_spike', name: 'Cannon Spike (Anti-Aéreo)', input: '623K', startup: '5f', active: '10f', recovery: '30f', hit: 'Launch', block: '-22', damage: 1450, anim: 'Tenshokyaku' }
    ]
  },
  {
    id: 'juri_sf6',
    name: 'Juri Han',
    title: 'Sádica del Feng Shui Engine',
    universe: 'sf6',
    universeName: 'Street Fighter 6',
    badge: '👁️ FENG SHUI SF6',
    badgeColor: 'sf6-purple',
    combatArchetype: 'Taekwondo Corrupto & Almacenamiento Fuha',
    desc: 'Luchadora despiadada que disfruta del sufrimiento ajeno. Utiliza el motor cibernético Feng Shui en su ojo izquierdo.',
    modelUrl: '/models/juri_sf6.glb',
    neonColor: '#7209b7',
    moves: [
      { id: 'fuhajin', name: 'Fuhajin (Carga Ki)', input: '214K', startup: '14f', active: '8f', recovery: '16f', hit: '+2', block: '-4', damage: 900, anim: 'Drive_Impact' },
      { id: 'saihasho', name: 'Saihasho (Proyectil Bajo)', input: '236LK', startup: '12f', active: '25f', recovery: '18f', hit: '+3', block: '-2', damage: 1050, anim: 'Lightning_Kick' }
    ]
  },
  {
    id: 'manon_sf6',
    name: 'Manon',
    title: 'Estrella de Judo y Ballet Francés',
    universe: 'sf6',
    universeName: 'Street Fighter 6',
    badge: '🩰 JUDO & BALLET',
    badgeColor: 'sf6-cyan',
    combatArchetype: 'Grappler de Medallas de Nivel 1 a 5',
    desc: 'Bailarina y judoka francesa que incrementa exponencialmente el daño de sus agarres con cada derribo exitoso.',
    modelUrl: '/models/manon_sf6.glb',
    neonColor: '#48cae4',
    moves: [
      { id: 'manege_dore', name: 'Manège Doré (Proyección Judo)', input: '63214P', startup: '8f', active: '3f', recovery: '35f', hit: 'Hard KD', block: 'Throw', damage: 2200, anim: 'Drive_Impact' },
      { id: 'rond_point', name: 'Rond-Point (Salto Ballet)', input: '236K', startup: '11f', active: '16f', recovery: '22f', hit: 'Launch', block: '-8', damage: 1400, anim: 'Tenshokyaku' }
    ]
  },
  {
    id: 'kimberly_sf6',
    name: 'Kimberly',
    title: 'Ninja Bushinryu de Cassette & Graffiti',
    universe: 'sf6',
    universeName: 'Street Fighter 6',
    badge: '🎨 BUSHINRYU SF6',
    badgeColor: 'sf6-gold',
    combatArchetype: 'Ninjutsu Urbano, Shuriken Spray y Carrera Ninja',
    desc: 'Discípula de Guy, combina ninjutsu tradicional con botes de spray y el ritmo ochentero de su walkman.',
    modelUrl: '/models/kimberly_sf6.glb',
    neonColor: '#ffb703',
    moves: [
      { id: 'senpu_kyaku', name: 'Senpu Kyaku (Torbellino Ninja)', input: '214K', startup: '9f', active: '18f', recovery: '24f', hit: 'KD', block: '-10', damage: 1300, anim: 'Spinning_Bird_Kick' },
      { id: 'sprint_kick', name: 'Carrera Bushin & Patada Voladora', input: '236K', startup: '10f', active: '14f', recovery: '20f', hit: '+2', block: '-4', damage: 1100, anim: 'Tenshokyaku' }
    ]
  },
  {
    id: 'marisa_sf6',
    name: 'Marisa',
    title: 'Gladiadora Colosal del Pancracio',
    universe: 'sf6',
    universeName: 'Street Fighter 6',
    badge: '🏛️ PANCRACIO SF6',
    badgeColor: 'sf6-pink',
    combatArchetype: 'Fuerza Bruta Acorazada, Scutum y Gladius',
    desc: 'Escultora y luchadora de pancracio italiana descendiente de guerreros griegos. Posee blindaje pesado en sus ataques cargados.',
    modelUrl: '/models/marisa_sf6.glb',
    neonColor: '#e63946',
    moves: [
      { id: 'gladius', name: 'Gladius (Puño Acorazado)', input: '236P', startup: '15f', active: '4f', recovery: '22f', hit: '+4', block: '-2', damage: 1700, anim: 'Drive_Impact' },
      { id: 'phalanx', name: 'Phalanx (Salto Demoledor)', input: '623P', startup: '18f', active: '12f', recovery: '26f', hit: 'Wall Bounce', block: '+3', damage: 1900, anim: 'Tenshokyaku' }
    ]
  },
  {
    id: 'aki_sf6',
    name: 'A.K.I.',
    title: 'Asesina del Veneno de las Sombras',
    universe: 'sf6',
    universeName: 'Street Fighter 6',
    badge: '🐍 VENENO SHADOW',
    badgeColor: 'sf6-cyan',
    combatArchetype: 'Garras Venenosas, Deslizamiento y Toxic Shock',
    desc: 'Discípula de F.A.N.G., envenena a sus rivales con garras afiladas y movimientos sinuosos de serpiente.',
    modelUrl: '/models/aki_sf6.glb',
    neonColor: '#00f5d4',
    moves: [
      { id: 'serpent_slash', name: 'Serpent Slash (Látigo de Garras)', input: '236P', startup: '13f', active: '6f', recovery: '21f', hit: 'Poison', block: '-4', damage: 1250, anim: 'Lightning_Kick' },
      { id: 'snake_step', name: 'Paso de Serpiente & Zancada', input: '214P', startup: '10f', active: '15f', recovery: '18f', hit: 'KD', block: '+1', damage: 1100, anim: 'Drive_Impact' }
    ]
  },

  // ==========================================
  // DARKSTALKERS
  // ==========================================
  {
    id: 'morrigan',
    name: 'Morrigan Aensland',
    title: 'Princesa Súcubo del Makai',
    universe: 'darkstalkers',
    universeName: 'Darkstalkers',
    badge: '🦇 SÚCUBO MAKAI',
    badgeColor: 'sf6-purple',
    combatArchetype: 'Alas Metamorfas, Soul Fist y Darkness Illusion',
    desc: 'Gobernante del reino demoníaco Makai. Sus alas de murciélago se transforman en guadañas, proyectiles mágicos y escudos.',
    modelUrl: '/models/morrigan_darkstalkers.glb',
    neonColor: '#9d4edd',
    moves: [
      { id: 'soul_fist', name: 'Soul Fist (Proyectil Mágico)', input: '236P', startup: '13f', active: '30f', recovery: '20f', hit: '+1', block: '-3', damage: 1100, anim: 'Drive_Impact' },
      { id: 'shadow_blade', name: 'Shadow Blade (Guadaña Aérea)', input: '623P', startup: '6f', active: '12f', recovery: '26f', hit: 'Launch', block: '-16', damage: 1400, anim: 'Tenshokyaku' }
    ]
  },
  {
    id: 'felicia',
    name: 'Felicia',
    title: 'Gatúbela Cantante y Acróbata',
    universe: 'darkstalkers',
    universeName: 'Darkstalkers',
    badge: '🐾 DARKSTALKERS',
    badgeColor: 'sf6-pink',
    combatArchetype: 'Acrobacias Felinas, Rolling Buckler y Garras Rápidas',
    desc: 'Gatúbela de gran corazón que sueña con ser una estrella de Broadway mientras protege a los huérfanos.',
    modelUrl: '/models/morrigan_darkstalkers.glb',
    neonColor: '#f72585',
    moves: []
  },

  // ==========================================
  // THE KING OF FIGHTERS (KOF)
  // ==========================================
  {
    id: 'mai_shiranui',
    name: 'Mai Shiranui',
    title: 'Kunoichi del Clan Shiranui',
    universe: 'kof',
    universeName: 'The King of Fighters',
    badge: '🪭 SHIRANUI KOF',
    badgeColor: 'sf6-pink',
    combatArchetype: 'Ninjutsu de Fuego y Abanicos Kacho-sen',
    desc: 'Heredera del ninjutsu Shiranui. Domina el elemento fuego y sus abanicos de combate con gracia y velocidad implacable.',
    modelUrl: '/models/mai_shiranui_kof.glb',
    neonColor: '#e63946',
    moves: [
      { id: 'kachosen', name: 'Kacho-sen (Lanzamiento de Abanico)', input: '236P', startup: '11f', active: '25f', recovery: '18f', hit: '+2', block: '-2', damage: 1050, anim: 'Drive_Impact' },
      { id: 'ryuenbu', name: 'Ryuenbu (Danza del Dragón Flamígero)', input: '214P', startup: '8f', active: '12f', recovery: '22f', hit: 'KD', block: '-6', damage: 1350, anim: 'Spinning_Bird_Kick' }
    ]
  },
  {
    id: 'athena_asamiya',
    name: 'Athena Asamiya',
    title: 'Idol Psíquica Psycho Soldier',
    universe: 'kof',
    universeName: 'The King of Fighters',
    badge: '🔮 PSYCHO SOLDIER',
    badgeColor: 'sf6-cyan',
    combatArchetype: 'Teletransportación y Psycho Ball',
    desc: 'Estrella del pop internacional que combate el mal utilizando sus poderes psíquicos y artes marciales chinas.',
    modelUrl: '/models/mai_shiranui_kof.glb',
    neonColor: '#3a86ff',
    moves: []
  },

  // ==========================================
  // TEKKEN
  // ==========================================
  {
    id: 'nina_williams',
    name: 'Nina Williams',
    title: 'Asesina Silenciosa Irlandesa',
    universe: 'tekken',
    universeName: 'Tekken',
    badge: '🔫 KOPPOJUTSU TEKKEN',
    badgeColor: 'sf6-purple',
    combatArchetype: 'Artes Marciales de Asesinato y Llaves Articulares',
    desc: 'Asesina a sueldo despiadada especializada en Koppojutsu y sumisiones letales. Maestra del combate a corta distancia.',
    modelUrl: '/models/nina_tekken.glb',
    neonColor: '#7209b7',
    moves: [
      { id: 'ivory_cutter', name: 'Ivory Cutter (Corte de Marfil)', input: '1+4', startup: '11f', active: '4f', recovery: '18f', hit: '+6', block: '-4', damage: 1250, anim: 'Drive_Impact' }
    ]
  },
  {
    id: 'asuka_kazama',
    name: 'Asuka Kazama',
    title: 'Mediadora de Osaka',
    universe: 'tekken',
    universeName: 'Tekken',
    badge: '🥋 ESTILO KAZAMA',
    badgeColor: 'sf6-gold',
    combatArchetype: 'Koppo Tradicional Kazama y Parries de Defensa',
    desc: 'Pariente de Jin Kazama, dedicada a impartir justicia callejera con poderosos contraataques y proyecciones marciales.',
    modelUrl: '/models/nina_tekken.glb',
    neonColor: '#ffb703',
    moves: []
  },

  // ==========================================
  // DEAD OR ALIVE (DOA)
  // ==========================================
  {
    id: 'kasumi',
    name: 'Kasumi',
    title: 'Shinobi Fugitiva de las Hojas de Cerezo',
    universe: 'doa',
    universeName: 'Dead or Alive',
    badge: '🌸 MUGEN TENSHIN DOA',
    badgeColor: 'sf6-cyan',
    combatArchetype: 'Ninjutsu Mugen Tenshin Tenjinmon',
    desc: 'Líder del clan ninja Mugen Tenshin convertida en fugitiva. Se desvanece en una lluvia de pétalos de cerezo para emboscar al rival.',
    modelUrl: '/models/kasumi_doa.glb',
    neonColor: '#00b4d8',
    moves: [
      { id: 'sakura_teleport', name: 'Danza de Pétalos de Cerezo', input: '236P+K', startup: '8f', active: '16f', recovery: '14f', hit: 'KD', block: '+1', damage: 1400, anim: 'Spinning_Bird_Kick' }
    ]
  },
  {
    id: 'ayane',
    name: 'Ayane',
    title: 'Kunoichi de las Sombras',
    universe: 'doa',
    universeName: 'Dead or Alive',
    badge: '🌑 HAJINMON DOA',
    badgeColor: 'sf6-purple',
    combatArchetype: 'Ninjutsu de Viento y Finta Giratoria',
    desc: 'Hermana de Kasumi y prodigio del clan de las sombras Hajinmon. Ataca con giros rápidos y técnicas aéreas cortantes.',
    modelUrl: '/models/kasumi_doa.glb',
    neonColor: '#5a189a',
    moves: []
  }
];

/**
 * Gestor Asíncrono de Cola de Carga y Descarga (> 1 min Timeout Fallback)
 */
export class FemaleRosterQueueManager {
  constructor(roster, onStatusUpdate) {
    this.roster = roster;
    this.queue = [...roster];
    this.statusMap = new Map();
    this.onStatusUpdate = onStatusUpdate;
    this.initStatus();
  }

  initStatus() {
    this.roster.forEach(f => {
      this.statusMap.set(f.id, {
        status: f.modelUrl ? 'ready' : 'queued',
        progress: f.modelUrl ? 100 : 0,
        startTime: null,
        error: null
      });
    });
  }

  getStatus(fighterId) {
    return this.statusMap.get(fighterId) || { status: 'unknown', progress: 0 };
  }

  markProcessing(fighterId) {
    const s = this.statusMap.get(fighterId);
    if (s) {
      s.status = 'loading';
      s.startTime = Date.now();
      if (this.onStatusUpdate) this.onStatusUpdate(fighterId, s);
    }
  }

  markReady(fighterId) {
    const s = this.statusMap.get(fighterId);
    if (s) {
      s.status = 'ready';
      s.progress = 100;
      if (this.onStatusUpdate) this.onStatusUpdate(fighterId, s);
    }
  }

  // Fallback si tarda más de 1 minuto (60 segundos): pasa al final de la cola
  checkTimeoutFallback(fighterId, maxMs = 60000) {
    const s = this.statusMap.get(fighterId);
    if (s && s.status === 'loading' && s.startTime) {
      const elapsed = Date.now() - s.startTime;
      if (elapsed > maxMs) {
        console.warn(`[QueueManager] Fighter ${fighterId} timed out (${(elapsed/1000).toFixed(1)}s > 60s). Pushed to end of queue.`);
        s.status = 'retry_queued';
        s.startTime = null;
        // Mover al final de la cola
        const idx = this.queue.findIndex(f => f.id === fighterId);
        if (idx !== -1) {
          const [item] = this.queue.splice(idx, 1);
          this.queue.push(item);
        }
        if (this.onStatusUpdate) this.onStatusUpdate(fighterId, s);
        return true;
      }
    }
    return false;
  }
}
