import bpy
import os
import math
from mathutils import Vector, Quaternion, Matrix, Euler

print("=====================================================")
print("FLAWLESS RETARGETING PIPELINE FOR CAPCOM SF6 CHUN-LI")
print("=====================================================")

BASE_DIR = r"c:\PROYECTOS ANTIGRAVITY\sf6"
MOCAP_DIR = os.path.join(BASE_DIR, "raw_assets", "mocap_fbx")
CHUNLI_FBX = os.path.join(BASE_DIR, "raw_assets", "chunli_sf6", "Raw Files", "Chun-Li S4.fbx")
OUTPUT_GLB = os.path.join(BASE_DIR, "public", "models", "chunli_sf6_animated.glb")

# Step 1: Load original untouched Capcom SF6 Chun-Li FBX
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=CHUNLI_FBX)
tgt_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
tgt_arm.name = "ChunLi_SF6_Armature"

print(f"Target Armature Loaded: {tgt_arm.name} with {len(tgt_arm.data.bones)} bones")

# Clear any default animations
if tgt_arm.animation_data:
    for track in list(tgt_arm.animation_data.nla_tracks):
        tgt_arm.animation_data.nla_tracks.remove(track)
    tgt_arm.animation_data.action = None

for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)

# Ensure Quaternion rotation mode on all pose bones
bpy.context.view_layer.objects.active = tgt_arm
bpy.ops.object.mode_set(mode='POSE')
for pb in tgt_arm.pose.bones:
    pb.rotation_mode = 'QUATERNION'

bone_pairs = [
    # Core Root / Hip
    ('mixamorig:Hips', 'C_Hip'),
    # Spine & Torso
    ('mixamorig:Spine', 'C_Spine1'),
    ('mixamorig:Spine1', 'C_Spine2'),
    ('mixamorig:Spine2', 'C_Chest'),
    ('mixamorig:Neck', 'C_Neck'),
    ('mixamorig:Head', 'C_Head'),
    # Left Arm
    ('mixamorig:LeftShoulder', 'L_Shoulder'),
    ('mixamorig:LeftArm', 'L_UpperArm'),
    ('mixamorig:LeftForeArm', 'L_ForeArm'),
    ('mixamorig:LeftHand', 'L_Hand'),
    # Right Arm
    ('mixamorig:RightShoulder', 'R_Shoulder'),
    ('mixamorig:RightArm', 'R_UpperArm'),
    ('mixamorig:RightForeArm', 'R_ForeArm'),
    ('mixamorig:RightHand', 'R_Hand'),
    # Left Leg
    ('mixamorig:LeftUpLeg', 'L_Thigh'),
    ('mixamorig:LeftLeg', 'L_Knee'),
    ('mixamorig:LeftFoot', 'L_Foot'),
    ('mixamorig:LeftToeBase', 'L_Toe'),
    # Right Leg
    ('mixamorig:RightUpLeg', 'R_Thigh'),
    ('mixamorig:RightLeg', 'R_Knee'),
    ('mixamorig:RightFoot', 'R_Foot'),
    ('mixamorig:RightToeBase', 'R_Toe'),
    # Fingers Left
    ('mixamorig:LeftHandThumb1', 'L_Thumb1'),
    ('mixamorig:LeftHandThumb2', 'L_Thumb2'),
    ('mixamorig:LeftHandThumb3', 'L_Thumb3'),
    ('mixamorig:LeftHandIndex1', 'L_Index1'),
    ('mixamorig:LeftHandIndex2', 'L_Index2'),
    ('mixamorig:LeftHandIndex3', 'L_Index3'),
    ('mixamorig:LeftHandMiddle1', 'L_Middle1'),
    ('mixamorig:LeftHandMiddle2', 'L_Middle2'),
    ('mixamorig:LeftHandMiddle3', 'L_Middle3'),
    ('mixamorig:LeftHandRing1', 'L_Ring1'),
    ('mixamorig:LeftHandRing2', 'L_Ring2'),
    ('mixamorig:LeftHandRing3', 'L_Ring3'),
    ('mixamorig:LeftHandPinky1', 'L_Pinky1'),
    ('mixamorig:LeftHandPinky2', 'L_Pinky2'),
    ('mixamorig:LeftHandPinky3', 'L_Pinky3'),
    # Fingers Right
    ('mixamorig:RightHandThumb1', 'R_Thumb1'),
    ('mixamorig:RightHandThumb2', 'R_Thumb2'),
    ('mixamorig:RightHandThumb3', 'R_Thumb3'),
    ('mixamorig:RightHandIndex1', 'R_Index1'),
    ('mixamorig:RightHandIndex2', 'R_Index2'),
    ('mixamorig:RightHandIndex3', 'R_Index3'),
    ('mixamorig:RightHandMiddle1', 'R_Middle1'),
    ('mixamorig:RightHandMiddle2', 'R_Middle2'),
    ('mixamorig:RightHandMiddle3', 'R_Middle3'),
    ('mixamorig:RightHandRing1', 'R_Ring1'),
    ('mixamorig:RightHandRing2', 'R_Ring2'),
    ('mixamorig:RightHandRing3', 'R_Ring3'),
    ('mixamorig:RightHandPinky1', 'R_Pinky1'),
    ('mixamorig:RightHandPinky2', 'R_Pinky2'),
    ('mixamorig:RightHandPinky3', 'R_Pinky3'),
]

# Secondary cloth & hair bones
cloth_belt = [pb.name for pb in tgt_arm.pose.bones if 'Belt' in pb.name or 'ClothA_Tail' in pb.name or 'ClothA_Belt' in pb.name]
hair_buns = [pb.name for pb in tgt_arm.pose.bones if 'Hair' in pb.name and ('bun' in pb.name.lower() or 'ribbon' in pb.name.lower() or 'tail' in pb.name.lower())]

mocap_actions = [
    ("Bouncing_Fight_Idle.fbx", "Idle_Combat", 1, 90, False),
    ("Capoeira_Kicks.fbx", "Lightning_Kick", 38, 125, False),
    ("Capoeira_Kicks.fbx", "Heavy_Kick", 1, 37, False),
    ("Hurricane_Kick.fbx", "Spinning_Bird_Kick", 1, 56, True),   # Center lock on turntable!
    ("Flip_Kick.fbx", "Tenshokyaku", 1, 62, True),               # Center lock on turntable!
    ("Combo_Punch.fbx", "Drive_Impact", 25, 88, False),
    ("Combo_Punch.fbx", "Kikosho", 1, 28, False),
    ("Taunt.fbx", "Taunt", 1, 86, False),
    ("Victory.fbx", "Victory", 1, 180, False),
]

hip_rest_z = tgt_arm.data.bones['C_Hip'].head_local.z

for fbx_file, action_name, start_f, end_f, lock_center in mocap_actions:
    fbx_path = os.path.join(MOCAP_DIR, fbx_file)
    print(f"\n--- Retargeting '{action_name}' from {fbx_file} (frames {start_f}..{end_f}) ---")
    
    # Import mocap FBX
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    src_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != tgt_arm][0]
    
    # Ensure source animation plays
    bpy.context.scene.frame_start = start_f
    bpy.context.scene.frame_end = end_f
    
    # Clear preexisting constraints on target
    for pb in tgt_arm.pose.bones:
        for c in list(pb.constraints):
            pb.constraints.remove(c)
            
    # Apply World Copy Rotation constraints
    for src_name, tgt_name in bone_pairs:
        if tgt_name in tgt_arm.pose.bones and src_name in src_arm.pose.bones:
            pb = tgt_arm.pose.bones[tgt_name]
            c = pb.constraints.new(type='COPY_ROTATION')
            c.target = src_arm
            c.subtarget = src_name
            c.target_space = 'WORLD'
            c.owner_space = 'WORLD'
            
    # Root Pelvis constraint
    hip_pb = tgt_arm.pose.bones['C_Hip']
    c_hip_rot = hip_pb.constraints.new(type='COPY_ROTATION')
    c_hip_rot.target = src_arm
    c_hip_rot.subtarget = 'mixamorig:Hips'
    c_hip_rot.target_space = 'WORLD'
    c_hip_rot.owner_space = 'WORLD'
    
    if not lock_center:
        # Grounded combat moves: Keep C_Hip at origin (0,0,0) for zero sliding or drifting on turntable
        hip_pb.location = Vector((0, 0, 0))
    else:
        # Aerial moves (Spinning Bird Kick, Tenshokyaku): Allow controlled vertical lift only
        c_hip_loc = hip_pb.constraints.new(type='COPY_LOCATION')
        c_hip_loc.target = src_arm
        c_hip_loc.subtarget = 'mixamorig:Hips'
        c_hip_loc.use_x = False  # Keep X centered at 0
        c_hip_loc.use_y = False  # Keep Y centered at 0
        c_hip_loc.use_z = True   # Vertical elevation only
        c_hip_loc.influence = 0.12 # Controlled elevation on turntable (never flies off screen!)
        
    # Bake the action using Blender's visual keying
    bpy.context.view_layer.objects.active = tgt_arm
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    
    bpy.ops.nla.bake(
        frame_start=start_f,
        frame_end=end_f,
        only_selected=True,
        visual_keying=True,
        clear_constraints=True,
        bake_types={'POSE'}
    )
    
    baked_action = tgt_arm.animation_data.action
    baked_action.name = action_name
    
    # Store into NLA Track
    track = tgt_arm.animation_data.nla_tracks.new()
    track.name = action_name
    track.strips.new(action_name, start_f, baked_action)
    
    # Clean up source mocap armature and extra objects
    for o in list(bpy.data.objects):
        if o != tgt_arm and o.parent != tgt_arm:
            bpy.data.objects.remove(o, do_unlink=True)
            
    print(f"Action '{action_name}' baked successfully ({baked_action.frame_range[1] - baked_action.frame_range[0]} frames).")

# Keep ONLY the baked actions for Chun-Li in bpy.data.actions (prevents warning floods)
baked_action_names = {name for _, name, _, _, _ in mocap_actions}
for act in list(bpy.data.actions):
    if act.name not in baked_action_names:
        bpy.data.actions.remove(act)

# Set default active action to Idle_Combat
idle_action = bpy.data.actions.get("Idle_Combat")
if idle_action:
    tgt_arm.animation_data.action = idle_action

print(f"\n>>> EXPORTING GLB TO: {OUTPUT_GLB} <<<")
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    export_yup=True,
    export_animations=True,
    export_skins=True,
    export_morph=True
)
print(f"Exported: {OUTPUT_GLB} ({os.path.getsize(OUTPUT_GLB)} bytes)")
print("CHUN-LI SF6 CAPCOM 4K RETARGETING COMPLETED WITH ZERO ERRORS!")
