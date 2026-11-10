import bpy
import os
import math
from mathutils import Vector, Quaternion, Matrix, Euler

mocap_dir = r"C:\PROYECTOS ANTIGRAVITY\sf6\raw_assets\mocap_fbx"
base_glb = r"C:\PROYECTOS ANTIGRAVITY\sf6\public\models\chunli_sf6_animated.glb"
output_glb = r"C:\PROYECTOS ANTIGRAVITY\sf6\public\models\chunli_sf6_animated.glb"

print("=====================================================")
print("SF6 CHUN-LI REAL MOTION CAPTURE RETARGETING PIPELINE")
print("=====================================================")

# Step 1: Load Capcom SF6 Chun-Li model as base
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=base_glb)
tgt_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"Target Base Armature Loaded: {tgt_arm.name} with {len(tgt_arm.data.bones)} bones")

# Clear any preexisting actions and NLA tracks from the target armature
if tgt_arm.animation_data:
    for track in list(tgt_arm.animation_data.nla_tracks):
        tgt_arm.animation_data.nla_tracks.remove(track)
    tgt_arm.animation_data.action = None

for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)

bpy.context.view_layer.objects.active = tgt_arm
bpy.ops.object.mode_set(mode='POSE')
for pb in tgt_arm.pose.bones:
    pb.rotation_mode = 'QUATERNION'

# Secondary physics bones for inertia sway
pants_r = [pb.name for pb in tgt_arm.pose.bones if 'R_Pants' in pb.name]
pants_l = [pb.name for pb in tgt_arm.pose.bones if 'L_Pants' in pb.name]
cloth_belt = [pb.name for pb in tgt_arm.pose.bones if 'Belt' in pb.name or 'ClothA_Tail' in pb.name or 'ClothA_Belt' in pb.name]
hair_buns = [pb.name for pb in tgt_arm.pose.bones if 'Hair' in pb.name and ('bun' in pb.name.lower() or 'ribbon' in pb.name.lower() or 'tail' in pb.name.lower())]

print(f"Identified secondary physics bones: Pants R({len(pants_r)}), Pants L({len(pants_l)}), Belt({len(cloth_belt)}), Hair({len(hair_buns)})")

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
    # Left Hand Fingers
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
    # Right Hand Fingers
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

# Cache target rest matrices in armature space
tgt_rest_mats = {}
for _, tgt_name in bone_pairs:
    if tgt_name in tgt_arm.data.bones:
        tgt_rest_mats[tgt_name] = tgt_arm.data.bones[tgt_name].matrix_local.copy()

# List of mocap clips to retarget:
# (fbx_file, clip_name, start_frame, end_frame, vertical_scale, lateral_scale)
mocap_clips = [
    ("Bouncing_Fight_Idle.fbx", "Idle_Combat", 1, 90, 0.00008, 0.00003),
    ("Capoeira_Kicks.fbx", "Lightning_Kick", 38, 125, 0.00006, 0.00002),
    ("Capoeira_Kicks.fbx", "Heavy_Kick", 1, 37, 0.00006, 0.00002),
    ("Hurricane_Kick.fbx", "Spinning_Bird_Kick", 1, 56, 0.00010, 0.00002),
    ("Flip_Kick.fbx", "Tenshokyaku", 1, 62, 0.00010, 0.00002),
    ("Combo_Punch.fbx", "Drive_Impact", 25, 88, 0.00006, 0.00003),
    ("Combo_Punch.fbx", "Kikosho", 1, 28, 0.00005, 0.00002),
    ("Taunt.fbx", "Taunt", 1, 86, 0.00006, 0.00003),
    ("Victory.fbx", "Victory", 1, 180, 0.00007, 0.00003),
]

for fbx_file, action_name, start_f, end_f, vert_scale, lat_scale in mocap_clips:
    fbx_path = os.path.join(mocap_dir, fbx_file)
    print(f"\n--- Retargeting '{action_name}' from {fbx_file} (frames {start_f}..{end_f}) ---")
    
    base_objs = set(bpy.data.objects)
    # Import the FBX into the current scene
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    src_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != tgt_arm][0]
    
    # Cache source rest quats and rest hip translation
    src_rest_quats = {}
    valid_pairs = []
    for src_name, tgt_name in bone_pairs:
        if src_name in src_arm.data.bones and tgt_name in tgt_rest_mats:
            src_rest_quats[src_name] = src_arm.data.bones[src_name].matrix_local.to_quaternion()
            valid_pairs.append((src_name, tgt_name))
    
    src_hip_rest_pos = src_arm.data.bones['mixamorig:Hips'].matrix_local.to_translation()
    
    # Create new action for target armature
    tgt_arm.animation_data_create()
    new_act = bpy.data.actions.new(name=action_name)
    tgt_arm.animation_data.action = new_act
    
    total_frames = end_f - start_f + 1
    
    # Iterate through frames
    for out_f_idx, src_f in enumerate(range(start_f, end_f + 1), start=1):
        bpy.context.scene.frame_set(src_f)
        bpy.context.view_layer.update()
        
        # 1. Root hip translation: vertical bob/jump and lateral shift
        src_hip_p = src_arm.pose.bones['mixamorig:Hips'].matrix.to_translation()
        d_pos = src_hip_p - src_hip_rest_pos
        
        # In Capcom armature, Y is UP, X is LATERAL, Z is DEPTH
        model_dy = d_pos.z * vert_scale
        model_dx = d_pos.x * lat_scale
        model_dz = d_pos.y * lat_scale
        
        tgt_hip_pb = tgt_arm.pose.bones['C_Hip']
        tgt_hip_pb.location = Vector((model_dx, model_dy, model_dz))
        tgt_hip_pb.keyframe_insert(data_path="location", frame=out_f_idx)
        
        # 2. Retarget all mapped human joints
        for src_name, tgt_name in valid_pairs:
            src_pb = src_arm.pose.bones[src_name]
            tgt_pb = tgt_arm.pose.bones[tgt_name]
            
            # Relative angular deformation delta in armature space
            delta_rot = src_pb.matrix.to_quaternion() @ src_rest_quats[src_name].inverted()
            
            tgt_rest = tgt_rest_mats[tgt_name]
            new_mat = delta_rot.to_matrix().to_4x4() @ tgt_rest
            new_mat.translation = tgt_pb.matrix.translation
            tgt_pb.matrix = new_mat
            tgt_pb.keyframe_insert(data_path="rotation_quaternion", frame=out_f_idx)
        
        # 3. Secondary physics bones (cloth, hair, belt) inertia
        # Natural sway driven by hip and spine movement
        spine_pb = tgt_arm.pose.bones.get('C_Spine1')
        hip_pb = tgt_arm.pose.bones.get('C_Hip')
        if spine_pb and hip_pb:
            spine_euler = spine_pb.rotation_quaternion.to_euler('XYZ')
            hip_euler = hip_pb.rotation_quaternion.to_euler('XYZ')
            
            # Belt/Sash secondary sway
            belt_rot = Euler((-hip_euler.x * 0.4, hip_euler.y * 0.3, -hip_euler.z * 0.5), 'XYZ').to_quaternion()
            for b_name in cloth_belt[:12]:
                pb = tgt_arm.pose.bones[b_name]
                pb.rotation_quaternion = belt_rot
                pb.keyframe_insert(data_path="rotation_quaternion", frame=out_f_idx)
                
            # Hair buns & ribbons dynamic inertia
            hair_rot = Euler((-spine_euler.x * 0.3, -spine_euler.y * 0.3, spine_euler.z * 0.2), 'XYZ').to_quaternion()
            for h_name in hair_buns[:10]:
                pb = tgt_arm.pose.bones[h_name]
                pb.rotation_quaternion = hair_rot
                pb.keyframe_insert(data_path="rotation_quaternion", frame=out_f_idx)

    print(f"Action '{action_name}' generated: {len(new_act.fcurves)} curves, {total_frames} frames.")
    
    # Push action to NLA track so glTF exporter bundles all actions!
    track = tgt_arm.animation_data.nla_tracks.new()
    track.name = action_name
    track.strips.new(action_name, 1, new_act)
    
    # Delete temporary source armature and its meshes from scene
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for o in list(bpy.data.objects):
        if o not in base_objs:
            bpy.data.objects.remove(o, do_unlink=True)
    for a in list(bpy.data.actions):
        if a != new_act and not any(t.name == a.name for t in tgt_arm.animation_data.nla_tracks):
            bpy.data.actions.remove(a)
    
    bpy.context.view_layer.objects.active = tgt_arm
    tgt_arm.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')

print("\nAll 9 real motion capture actions successfully generated and pushed to NLA tracks!")

# Step 3: Export final GLB
bpy.ops.object.mode_set(mode='OBJECT')
print(f"Exporting to {output_glb}...")
bpy.ops.export_scene.gltf(
    filepath=output_glb,
    export_format='GLB',
    export_animations=True,
    export_nla_strips=True,
    export_apply=False
)
print("GLB export complete!")
