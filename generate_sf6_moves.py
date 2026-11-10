import bpy
import math
from mathutils import Euler, Quaternion, Vector

input_glb = r"C:\PROYECTOS ANTIGRAVITY\sf6\public\models\chunli_sf6_animated.glb"
output_glb = r"C:\PROYECTOS ANTIGRAVITY\sf6\public\models\chunli_sf6_animated.glb"

print(f"Loading {input_glb} into Blender...")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=input_glb)

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
bpy.ops.object.mode_set(mode='POSE')

# Remove any old actions and tracks to start clean
if arm.animation_data:
    for t in list(arm.animation_data.nla_tracks):
        arm.animation_data.nla_tracks.remove(t)
    arm.animation_data.action = None

for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)

pose_bones = arm.pose.bones

# Ensure all relevant bones use QUATERNION rotation
for pb in pose_bones:
    pb.rotation_mode = 'QUATERNION'

# Note: The model scale in Blender is ~0.018m (scaled 100x by Three.js to 1.8m).
# Any bone location offset MUST be in model units (0.0001 = 1 cm in Three.js world space).
# We anchor C_Hip at its natural rest location Vector((0, 0, 0)) to prevent flying off screen!

def set_quat(bone_name, eul_deg, frame):
    if bone_name in pose_bones:
        b = pose_bones[bone_name]
        q = Euler((math.radians(eul_deg[0]), math.radians(eul_deg[1]), math.radians(eul_deg[2])), 'XYZ').to_quaternion()
        b.rotation_quaternion = q
        b.keyframe_insert(data_path="rotation_quaternion", frame=frame)

def set_loc(bone_name, offset_xyz, frame):
    if bone_name in pose_bones:
        b = pose_bones[bone_name]
        # In this model's armature: Y is UP, Z is DEPTH, X is LATERAL
        # offset_xyz = (dx, dy_up, dz_depth) in model units
        b.location = Vector((offset_xyz[0], offset_xyz[1], offset_xyz[2]))
        b.keyframe_insert(data_path="location", frame=frame)

# Identify secondary physics bones
pants_r = [pb.name for pb in pose_bones if 'R_Pants' in pb.name]
pants_l = [pb.name for pb in pose_bones if 'L_Pants' in pb.name]
cloth_belt = [pb.name for pb in pose_bones if 'Belt' in pb.name or 'ClothA_Tail' in pb.name or 'ClothA_Belt' in pb.name]
hair_buns = [pb.name for pb in pose_bones if 'Hair' in pb.name and ('bun' in pb.name.lower() or 'ribbon' in pb.name.lower() or 'tail' in pb.name.lower())]

print(f"Found {len(pants_r)} R_Pants, {len(pants_l)} L_Pants, {len(cloth_belt)} belt, {len(hair_buns)} hair bones.")

# =========================================================================
# ACTION 1: Idle_Combat (SF6 Authentic Kung Fu Stance & Breathing Bounce)
# Duration: 60 frames (In-Place Loop, anchored on turntable)
# =========================================================================
print("Generating Action 1: Idle_Combat...")
act_idle = bpy.data.actions.new(name="Idle_Combat")
arm.animation_data_create()
arm.animation_data.action = act_idle

for f in range(1, 61, 2):
    t = (f - 1) / 59.0
    phase = t * math.pi * 2.0
    
    # Microscopic breathing bounce: 0.00015 = 1.5 cm in world space
    bob_y = math.sin(phase) * 0.00015
    sway_x = math.cos(phase) * 0.00006
    breath = math.sin(phase) * 0.02
    
    # Hip stays firmly rooted on the turntable!
    set_loc("C_Hip", (sway_x, bob_y, 0), f)
    set_quat("C_Hip", (4.0 + math.sin(phase)*2.0, -18.0 + math.cos(phase)*3.0, 0), f)
    
    # Spine & Chest: natural breathing expansion
    set_quat("C_Spine1", (-3.0 - breath*15.0, 10.0, 0), f)
    set_quat("C_Spine2", (-2.0 - breath*10.0, 5.0, 0), f)
    set_quat("C_Chest", (3.0 + breath*25.0, 4.0, 0), f)
    set_quat("C_Neck", (-2.0, -2.0, 0), f)
    set_quat("C_Head", (1.0 - math.sin(phase)*1.5, 5.0, 0), f)
    
    # Arms: Chun-Li Kung Fu Wing Chun open palm guard
    l_pulse = math.sin(phase + 0.5) * 6.0
    set_quat("L_Shoulder", (5.0, -10.0, 15.0), f)
    set_quat("L_UpperArm", (-25.0 + l_pulse, -20.0, 42.0 + l_pulse*0.5), f)
    set_quat("L_ForeArm", (-75.0 - l_pulse*1.2, 25.0, -30.0), f)
    set_quat("L_Hand", (-10.0 + l_pulse, 15.0, -15.0), f)
    
    r_pulse = math.sin(phase - 0.5) * 4.0
    set_quat("R_Shoulder", (-2.0, 5.0, -10.0), f)
    set_quat("R_UpperArm", (20.0 + r_pulse, 15.0, -32.0), f)
    set_quat("R_ForeArm", (-60.0 + r_pulse, -15.0, 20.0), f)
    set_quat("R_Hand", (-15.0, -10.0, 10.0), f)
    
    # Legs: Kung Fu stance absorbing the vertical bounce
    set_quat("R_Thigh", (-18.0 - math.sin(phase)*2.0, -8.0, 14.0), f)
    set_quat("R_Knee", (26.0 + math.sin(phase)*3.0, 0, 0), f)
    set_quat("R_Shin_1", (-4.0, 0, 0), f)
    set_quat("R_Foot", (-6.0, 0, -4.0), f)
    
    set_quat("L_Thigh", (12.0 - math.sin(phase)*1.5, 14.0, -10.0), f)
    set_quat("L_Knee", (22.0 + math.sin(phase)*2.5, 0, 0), f)
    set_quat("L_Shin_1", (-2.0, 0, 0), f)
    set_quat("L_Foot", (-8.0, 0, 4.0), f)
    
    # Secondary Cloth & Hair Inertia
    inertia = math.cos(phase) * 8.0
    for pb_name in pants_r:
        set_quat(pb_name, (inertia * 0.8, 0, inertia * 0.3), f)
    for pb_name in pants_l:
        set_quat(pb_name, (inertia * 0.8, 0, -inertia * 0.3), f)
    for pb_name in cloth_belt:
        set_quat(pb_name, (inertia * 1.2, 0, 0), f)
    for pb_name in hair_buns:
        set_quat(pb_name, (-inertia * 0.9, 0, 0), f)

tr_idle = arm.animation_data.nla_tracks.new()
tr_idle.strips.new("Idle_Combat", 1, act_idle)

# =========================================================================
# ACTION 2: Lightning_Kick (SF6 Hyakuretsukyaku / Hundred Burst Kicks)
# 60 frames high-speed flurry of 8 alternating kicks!
# =========================================================================
print("Generating Action 2: Lightning_Kick...")
act_kick = bpy.data.actions.new(name="Lightning_Kick")
arm.animation_data.action = act_kick

kick_cycles = [
    (6, 9, 12, -75.0, 80.0, 15.0),     # Kick 1: Mid thrust
    (12, 15, 18, -95.0, 95.0, 25.0),   # Kick 2: High chin kick
    (18, 21, 24, -65.0, 75.0, 10.0),   # Kick 3: Low shin sweep
    (24, 27, 30, -105.0, 105.0, 30.0), # Kick 4: Extreme high head snap
    (30, 33, 36, -80.0, 85.0, 15.0),   # Kick 5: Driving mid kick
    (36, 39, 42, -90.0, 95.0, 20.0),   # Kick 6: High strike
    (42, 45, 48, -100.0, 100.0, 25.0), # Kick 7: Overhead snap
    (48, 51, 55, -85.0, 90.0, 15.0)    # Kick 8: Finisher thrust
]

for f in range(1, 61, 2):
    # Anchored firmly on turntable floor!
    set_loc("C_Hip", (0, 0, 0), f)
    
    # Body leans back 35 degrees on left support leg
    set_quat("C_Hip", (20.0, 28.0, -22.0), f)
    set_quat("C_Spine1", (-18.0, -18.0, 18.0), f)
    set_quat("C_Spine2", (-10.0, -10.0, 10.0), f)
    set_quat("C_Chest", (12.0, -8.0, 8.0), f)
    set_quat("C_Head", (-14.0, 15.0, -12.0), f)
    
    # Left support leg (firmly planted, knee bent)
    set_quat("L_Thigh", (-16.0, 14.0, -6.0), f)
    set_quat("L_Knee", (32.0, 0, 0), f)
    set_quat("L_Foot", (10.0, 0, 0), f)
    
    # Defensive guard arms
    arm_jitter = math.sin(f * 0.8) * 4.0
    set_quat("L_UpperArm", (35.0 + arm_jitter, -35.0, 48.0), f)
    set_quat("L_ForeArm", (-85.0, 20.0, -20.0), f)
    set_quat("R_UpperArm", (-25.0 + arm_jitter, 42.0, -48.0), f)
    set_quat("R_ForeArm", (-75.0, -20.0, 20.0), f)

# Keyframe each explosive kick on the right leg
for start_f, apex_f, end_f, pitch, knee_ext, yaw in kick_cycles:
    # Retract / chamber
    set_quat("R_Thigh", (-40.0, 5.0, yaw - 10.0), start_f)
    set_quat("R_Knee", (20.0, 0, 0), start_f)
    set_quat("R_Foot", (-15.0, 0, 0), start_f)
    
    # Apex extension
    set_quat("R_Thigh", (pitch, -12.0, yaw), apex_f)
    set_quat("R_Knee", (knee_ext, 0, 0), apex_f)
    set_quat("R_Foot", (25.0, 0, 0), apex_f)
    
    for pb_name in pants_r:
        set_quat(pb_name, (-pitch * 0.3, 0, 25.0), apex_f)
    
    # Retract
    set_quat("R_Thigh", (-45.0, 0.0, yaw - 5.0), end_f)
    set_quat("R_Knee", (25.0, 0, 0), end_f)
    set_quat("R_Foot", (-10.0, 0, 0), end_f)

set_quat("R_Thigh", (-25.0, -5.0, 10.0), 60)
set_quat("R_Knee", (25.0, 0, 0), 60)

tr_kick = arm.animation_data.nla_tracks.new()
tr_kick.strips.new("Lightning_Kick", 1, act_kick)

# =========================================================================
# ACTION 3: Spinning_Bird_Kick (SF6 Legendary Inverted Helicopter Spin)
# 60 frames: Crouch -> Invert 180° -> 720° Helicopter Spin -> Land!
# =========================================================================
print("Generating Action 3: Spinning_Bird_Kick...")
act_sbk = bpy.data.actions.new(name="Spinning_Bird_Kick")
arm.animation_data.action = act_sbk

for f in range(1, 61, 2):
    if f <= 10:
        # Phase 1: Deep crouch launch (frames 1-10)
        crouch = (f - 1) / 9.0
        set_loc("C_Hip", (0, -0.0006 * crouch, 0), f)
        set_quat("C_Hip", (25.0 * crouch, 0, 0), f)
        set_quat("C_Spine1", (15.0 * crouch, 0, 0), f)
        set_quat("L_Thigh", (-35.0 * crouch, 10.0, -10.0), f)
        set_quat("L_Knee", (60.0 * crouch, 0, 0), f)
        set_quat("R_Thigh", (-35.0 * crouch, -10.0, 10.0), f)
        set_quat("R_Knee", (60.0 * crouch, 0, 0), f)
        set_quat("L_UpperArm", (-20.0 * crouch, 0, 20.0), f)
        set_quat("R_UpperArm", (-20.0 * crouch, 0, -20.0), f)
    
    elif f <= 50:
        # Phase 2: Inverted Helicopter Spin! (frames 11-50)
        spin_t = (f - 11) / 39.0
        spin_angle = spin_t * 720.0
        
        # Lifted gracefully by ~15 cm above turntable floor (0.0015 model units)
        height = 0.0015 * math.sin(spin_t * math.pi)
        set_loc("C_Hip", (0, height, 0), f)
        
        # Inverted on X, spinning on Y
        set_quat("C_Hip", (180.0, spin_angle, 0), f)
        set_quat("C_Spine1", (0, 0, 0), f)
        set_quat("C_Spine2", (0, 0, 0), f)
        set_quat("C_Chest", (0, 0, 0), f)
        set_quat("C_Head", (0, 0, 0), f)
        
        # 180° horizontal split blades!
        set_quat("R_Thigh", (0, 0, 85.0), f)
        set_quat("R_Knee", (8.0, 0, 0), f)
        set_quat("R_Foot", (15.0, 0, 0), f)
        
        set_quat("L_Thigh", (0, 0, -85.0), f)
        set_quat("L_Knee", (8.0, 0, 0), f)
        set_quat("L_Foot", (15.0, 0, 0), f)
        
        # Arms tucked close to chest
        set_quat("R_UpperArm", (-15.0, 0, -15.0), f)
        set_quat("R_ForeArm", (-85.0, 0, 0), f)
        set_quat("L_UpperArm", (-15.0, 0, 15.0), f)
        set_quat("L_ForeArm", (-85.0, 0, 0), f)
    
    else:
        # Phase 3: Land and recover (frames 51-60)
        land_t = (f - 51) / 9.0
        set_loc("C_Hip", (0, 0, 0), f)
        set_quat("C_Hip", (15.0 * (1.0 - land_t), 0, 0), f)
        set_quat("R_Thigh", (-20.0 * (1.0 - land_t), -10.0, 10.0), f)
        set_quat("R_Knee", (30.0 * (1.0 - land_t), 0, 0), f)
        set_quat("L_Thigh", (10.0 * (1.0 - land_t), 10.0, -10.0), f)
        set_quat("L_Knee", (25.0 * (1.0 - land_t), 0, 0), f)
        set_quat("R_UpperArm", (20.0, 15.0, -30.0), f)
        set_quat("L_UpperArm", (-20.0, -15.0, 35.0), f)

tr_sbk = arm.animation_data.nla_tracks.new()
tr_sbk.strips.new("Spinning_Bird_Kick", 1, act_sbk)

# =========================================================================
# ACTION 4: Drive_Impact (SF6 Heavy Drive Strike with Hitstop)
# 45 frames
# =========================================================================
print("Generating Action 4: Drive_Impact...")
act_drive = bpy.data.actions.new(name="Drive_Impact")
arm.animation_data.action = act_drive

for f in range(1, 46, 2):
    if f <= 15:
        # Windup: Deep coil & draw right palm back
        w = (f - 1) / 14.0
        set_loc("C_Hip", (0, -0.0002 * w, -0.0003 * w), f)
        set_quat("C_Hip", (8.0 * w, -38.0 * w, 5.0 * w), f)
        set_quat("C_Spine1", (-6.0 * w, -25.0 * w, 0), f)
        set_quat("C_Chest", (-4.0 * w, -15.0 * w, 0), f)
        set_quat("R_UpperArm", (45.0 * w, 35.0 * w, -65.0 * w), f)
        set_quat("R_ForeArm", (-95.0 * w, 0, 0), f)
        set_quat("R_Hand", (25.0 * w, 0, 0), f)
        set_quat("L_UpperArm", (-25.0 * w, -20.0 * w, 35.0 * w), f)
        set_quat("L_ForeArm", (-45.0 * w, 0, 0), f)
        set_quat("R_Thigh", (-25.0 * w, -15.0 * w, 15.0 * w), f)
        set_quat("R_Knee", (35.0 * w, 0, 0), f)
        set_quat("L_Thigh", (15.0 * w, 10.0 * w, -10.0 * w), f)
    
    elif f <= 24:
        # EXPLOSIVE Forward Palm Thrust!
        strike_t = (f - 16) / 8.0
        set_loc("C_Hip", (0, 0, 0.0008 * strike_t), f) # slight 8 cm forward step
        set_quat("C_Hip", (-16.0, 24.0, 0), f)
        set_quat("C_Spine1", (16.0, 22.0, 0), f)
        set_quat("C_Chest", (14.0, 15.0, 0), f)
        set_quat("R_UpperArm", (-40.0, -22.0, 22.0), f)
        set_quat("R_ForeArm", (-8.0, 0, 0), f)
        set_quat("R_Hand", (-35.0, 0, 0), f)
        set_quat("L_UpperArm", (30.0, -30.0, 45.0), f)
        set_quat("L_ForeArm", (-70.0, 0, 0), f)
        set_quat("R_Thigh", (32.0, -12.0, 0), f)
        set_quat("R_Knee", (20.0, 0, 0), f)
        set_quat("L_Thigh", (-42.0, 14.0, 0), f)
        set_quat("L_Knee", (40.0, 0, 0), f)
    
    elif f <= 34:
        # Hitstop muscle lock
        set_loc("C_Hip", (0, 0, 0.0008), f)
        set_quat("C_Hip", (-16.0, 24.0, 0), f)
        set_quat("R_UpperArm", (-40.0, -22.0, 22.0), f)
        set_quat("R_ForeArm", (-8.0, 0, 0), f)
        set_quat("R_Hand", (-35.0, 0, 0), f)
    
    else:
        # Recovery back to guard
        rec_t = (f - 35) / 10.0
        set_loc("C_Hip", (0, 0, 0.0008 * (1.0 - rec_t)), f)
        set_quat("C_Hip", (5.0, -15.0, 0), f)
        set_quat("R_UpperArm", (25.0 * rec_t, 20.0 * rec_t, -35.0 * rec_t), f)
        set_quat("R_ForeArm", (-55.0 * rec_t, -20.0 * rec_t, 15.0 * rec_t), f)

tr_drive = arm.animation_data.nla_tracks.new()
tr_drive.strips.new("Drive_Impact", 1, act_drive)

# =========================================================================
# ACTION 5: Tenshokyaku (SF6 Rising Vertical Aerial Kicks)
# 45 frames
# =========================================================================
print("Generating Action 5: Tenshokyaku...")
act_ten = bpy.data.actions.new(name="Tenshokyaku")
arm.animation_data.action = act_ten

for f in range(1, 46, 2):
    if f <= 10:
        c = (f - 1) / 9.0
        set_loc("C_Hip", (0, -0.0005 * c, 0), f)
        set_quat("C_Hip", (20.0 * c, 0, 0), f)
        set_quat("R_Thigh", (-30.0 * c, 0, 10.0), f)
        set_quat("R_Knee", (55.0 * c, 0, 0), f)
        set_quat("L_Thigh", (-30.0 * c, 0, -10.0), f)
        set_quat("L_Knee", (55.0 * c, 0, 0), f)
    
    elif f <= 34:
        air_t = (f - 11) / 23.0
        height = 0.0025 * math.sin(air_t * math.pi) # ~25 cm jump, staying in screen!
        kick_alt = math.sin(air_t * math.pi * 6.0)
        
        set_loc("C_Hip", (0, height, 0), f)
        set_quat("C_Hip", (-15.0, 0, 0), f)
        
        if kick_alt > 0:
            set_quat("R_Thigh", (-115.0, -5.0, 15.0), f)
            set_quat("R_Knee", (95.0, 0, 0), f)
            set_quat("L_Thigh", (10.0, 5.0, -5.0), f)
            set_quat("L_Knee", (40.0, 0, 0), f)
        else:
            set_quat("R_Thigh", (10.0, -5.0, 5.0), f)
            set_quat("R_Knee", (40.0, 0, 0), f)
            set_quat("L_Thigh", (-115.0, 5.0, -15.0), f)
            set_quat("L_Knee", (95.0, 0, 0), f)
        
        set_quat("R_UpperArm", (45.0, 0, -45.0), f)
        set_quat("L_UpperArm", (45.0, 0, 45.0), f)
    
    else:
        set_loc("C_Hip", (0, 0, 0), f)
        set_quat("C_Hip", (5.0, -15.0, 0), f)
        set_quat("R_Thigh", (-18.0, -8.0, 14.0), f)
        set_quat("R_Knee", (26.0, 0, 0), f)
        set_quat("L_Thigh", (12.0, 14.0, -10.0), f)
        set_quat("L_Knee", (22.0, 0, 0), f)

tr_ten = arm.animation_data.nla_tracks.new()
tr_ten.strips.new("Tenshokyaku", 1, act_ten)

# =========================================================================
# ACTION 6: Kikosho (SF6 Super Art / Chi Energy Double Palm Blast)
# 50 frames
# =========================================================================
print("Generating Action 6: Kikosho...")
act_kiko = bpy.data.actions.new(name="Kikosho")
arm.animation_data.action = act_kiko

for f in range(1, 51, 2):
    if f <= 18:
        g = (f - 1) / 17.0
        set_loc("C_Hip", (0, -0.0006 * g, 0), f) # Sinks 6 cm into horse stance
        set_quat("C_Hip", (10.0 * g, 0, 0), f)
        set_quat("C_Spine1", (-8.0 * g, 0, 0), f)
        
        set_quat("R_Thigh", (-25.0 * g, -15.0 * g, 20.0 * g), f)
        set_quat("R_Knee", (45.0 * g, 0, 0), f)
        set_quat("L_Thigh", (-25.0 * g, 15.0 * g, -20.0 * g), f)
        set_quat("L_Knee", (45.0 * g, 0, 0), f)
        
        set_quat("R_UpperArm", (25.0 * g, 30.0 * g, -45.0 * g), f)
        set_quat("R_ForeArm", (-95.0 * g, 0, 0), f)
        set_quat("L_UpperArm", (25.0 * g, -30.0 * g, 45.0 * g), f)
        set_quat("L_ForeArm", (-95.0 * g, 0, 0), f)
    
    elif f <= 35:
        set_loc("C_Hip", (0, -0.0006, 0.0004), f)
        set_quat("C_Hip", (-12.0, 0, 0), f)
        set_quat("C_Chest", (18.0, 0, 0), f)
        
        set_quat("R_UpperArm", (-35.0, 10.0, -12.0), f)
        set_quat("R_ForeArm", (-5.0, 0, 0), f)
        set_quat("R_Hand", (-45.0, 0, 0), f)
        
        set_quat("L_UpperArm", (-35.0, -10.0, 12.0), f)
        set_quat("L_ForeArm", (-5.0, 0, 0), f)
        set_quat("L_Hand", (-45.0, 0, 0), f)
    
    else:
        rec_t = (f - 36) / 14.0
        set_loc("C_Hip", (0, 0, 0), f)
        set_quat("C_Hip", (4.0, -18.0, 0), f)
        set_quat("R_UpperArm", (20.0, 15.0, -32.0), f)
        set_quat("L_UpperArm", (-25.0, -20.0, 42.0), f)

tr_kiko = arm.animation_data.nla_tracks.new()
tr_kiko.strips.new("Kikosho", 1, act_kiko)

# =========================================================================
# ACTION 7: Victory (SF6 Joyous Hops & Peace Sign "Yatta!")
# 60 frames
# =========================================================================
print("Generating Action 7: Victory...")
act_vic = bpy.data.actions.new(name="Victory")
arm.animation_data.action = act_vic

for f in range(1, 61, 2):
    if f <= 24:
        hop_t = (f - 1) / 11.0
        hop_y = abs(math.sin(hop_t * math.pi)) * 0.0006 # ~6 cm joyous hops
        set_loc("C_Hip", (0, hop_y, 0), f)
        set_quat("C_Hip", (0, math.sin(hop_t*math.pi)*10.0, 0), f)
        set_quat("R_Thigh", (-15.0, 0, 0), f)
        set_quat("R_Knee", (20.0, 0, 0), f)
        set_quat("L_Thigh", (-15.0, 0, 0), f)
        set_quat("L_Knee", (20.0, 0, 0), f)
        set_quat("R_UpperArm", (-45.0, 0, -25.0), f)
        set_quat("L_UpperArm", (-45.0, 0, 25.0), f)
    
    else:
        p_t = min(1.0, (f - 25) / 15.0)
        sway = math.sin((f - 25) * 0.15) * 3.0
        
        set_loc("C_Hip", (0, 0, 0), f)
        set_quat("C_Hip", (0, 15.0 * p_t, -6.0 * p_t), f)
        set_quat("C_Spine1", (0, -10.0 * p_t, 8.0 * p_t), f)
        set_quat("C_Head", (-8.0 * p_t, -12.0 * p_t + sway, 10.0 * p_t), f)
        
        set_quat("R_Shoulder", (0, 15.0 * p_t, -10.0 * p_t), f)
        set_quat("R_UpperArm", (-125.0 * p_t, -15.0 * p_t, -25.0 * p_t), f)
        set_quat("R_ForeArm", (-55.0 * p_t, 25.0 * p_t, 0), f)
        set_quat("R_Hand", (20.0 * p_t, 10.0 * p_t, 0), f)
        
        set_quat("L_Shoulder", (0, -10.0 * p_t, 10.0 * p_t), f)
        set_quat("L_UpperArm", (25.0 * p_t, -20.0 * p_t, 42.0 * p_t), f)
        set_quat("L_ForeArm", (-95.0 * p_t, 0, 0), f)
        set_quat("L_Hand", (15.0 * p_t, 0, 0), f)
        
        set_quat("R_Thigh", (15.0 * p_t, -10.0 * p_t, 8.0 * p_t), f)
        set_quat("R_Knee", (12.0 * p_t, 0, 0), f)
        set_quat("L_Thigh", (-10.0 * p_t, 10.0 * p_t, -8.0 * p_t), f)
        set_quat("L_Knee", (22.0 * p_t, 0, 0), f)

tr_vic = arm.animation_data.nla_tracks.new()
tr_vic.strips.new("Victory", 1, act_vic)

# =========================================================================
# ACTION 8: Taunt (SF6 Playful Bow & Beckon "Gomen ne!")
# 45 frames
# =========================================================================
print("Generating Action 8: Taunt...")
act_taunt = bpy.data.actions.new(name="Taunt")
arm.animation_data.action = act_taunt

for f in range(1, 46, 2):
    set_loc("C_Hip", (0, 0, 0), f)
    if f <= 20:
        bow_t = (f - 1) / 19.0
        set_quat("C_Hip", (15.0 * bow_t, 0, 0), f)
        set_quat("C_Spine1", (15.0 * bow_t, 0, 0), f)
        set_quat("C_Head", (10.0 * bow_t, 0, 0), f)
        set_quat("R_UpperArm", (-20.0 * bow_t, 25.0 * bow_t, -30.0 * bow_t), f)
        set_quat("R_ForeArm", (-90.0 * bow_t, 0, 0), f)
        set_quat("L_UpperArm", (-20.0 * bow_t, -25.0 * bow_t, 30.0 * bow_t), f)
        set_quat("L_ForeArm", (-90.0 * bow_t, 0, 0), f)
    else:
        beckon_t = (f - 21) / 24.0
        wave = math.sin(beckon_t * math.pi * 4.0) * 15.0
        set_quat("C_Hip", (0, 0, 0), f)
        set_quat("C_Spine1", (-5.0, 10.0 * beckon_t, 0), f)
        set_quat("C_Head", (-5.0, 5.0, -8.0), f)
        set_quat("R_UpperArm", (-30.0, 10.0, -15.0), f)
        set_quat("R_ForeArm", (-45.0 + wave, 0, 0), f)
        set_quat("R_Hand", (-30.0 + wave * 0.8, 0, 0), f)
        set_quat("L_UpperArm", (20.0, -15.0, 30.0), f)
        set_quat("L_ForeArm", (-85.0, 0, 0), f)

tr_taunt = arm.animation_data.nla_tracks.new()
tr_taunt.strips.new("Taunt", 1, act_taunt)

bpy.ops.object.mode_set(mode='OBJECT')

print(f"Exporting in-place animated GLB to {output_glb}...")
bpy.ops.export_scene.gltf(
    filepath=output_glb,
    export_format='GLB',
    export_image_format='JPEG',
    export_jpeg_quality=85,
    export_skins=True,
    export_morph=True,
    export_animations=True,
    export_nla_strips=True,
    export_apply=False
)

print("Export completed successfully!")
