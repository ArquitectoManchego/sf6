import bpy
import os
from mathutils import Vector, Quaternion, Matrix, Euler

BASE_DIR = r"c:\PROYECTOS ANTIGRAVITY\sf6"
RAW_DIR = os.path.join(BASE_DIR, "raw_assets", "chunli_sf6", "Raw Files")
CHUNLI_FBX = os.path.join(RAW_DIR, "Chun-Li S4.fbx")
MOCAP_DIR = os.path.join(BASE_DIR, "raw_assets", "mocap_fbx")
IDLE_FBX = os.path.join(MOCAP_DIR, "Bouncing_Fight_Idle.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=CHUNLI_FBX)
tgt_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
tgt_arm.name = "ChunLi_Armature"

bpy.ops.import_scene.fbx(filepath=IDLE_FBX)
src_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != tgt_arm][0]
src_arm.name = "Mixamo_Armature"

# Test retargeting by constraint mapping
# 1. Hips
pb_hip = tgt_arm.pose.bones.get('C_Hip')
c_loc = pb_hip.constraints.new('COPY_LOCATION')
c_loc.target = src_arm
c_loc.subtarget = 'mixamorig:Hips'

c_rot = pb_hip.constraints.new('COPY_ROTATION')
c_rot.target = src_arm
c_rot.subtarget = 'mixamorig:Hips'

# 2. Spines
for s_bone, t_bone in [('mixamorig:Spine', 'C_Spine1'), ('mixamorig:Spine1', 'C_Spine2'), ('mixamorig:Spine2', 'C_Chest'), ('mixamorig:Neck', 'C_Neck'), ('mixamorig:Head', 'C_Head')]:
    pb = tgt_arm.pose.bones.get(t_bone)
    if pb:
        c = pb.constraints.new('COPY_ROTATION')
        c.target = src_arm
        c.subtarget = s_bone

# 3. Legs
# In legs, Capcom rest is pointing up (+Z), Mixamo rest is pointing down (-Z).
# Let's check how Copy Rotation or IK works on legs!
for side, s_side, t_side in [('L', 'Left', 'L'), ('R', 'Right', 'R')]:
    pb_knee = tgt_arm.pose.bones.get(f'{t_side}_Knee')
    c_ik = pb_knee.constraints.new('IK')
    c_ik.target = src_arm
    c_ik.subtarget = f'mixamorig:{s_side}Foot'
    c_ik.chain_count = 2

    pb_foot = tgt_arm.pose.bones.get(f'{t_side}_Foot')
    c_rot_foot = pb_foot.constraints.new('COPY_ROTATION')
    c_rot_foot.target = src_arm
    c_rot_foot.subtarget = f'mixamorig:{s_side}Foot'

# 4. Arms (using IK for flawless positioning without axis twisting)
for side, s_side, t_side in [('L', 'Left', 'L'), ('R', 'Right', 'R')]:
    pb_forearm = tgt_arm.pose.bones.get(f'{t_side}_ForeArm')
    c_ik_arm = pb_forearm.constraints.new('IK')
    c_ik_arm.target = src_arm
    c_ik_arm.subtarget = f'mixamorig:{s_side}Hand'
    c_ik_arm.chain_count = 2
    
    pb_hand = tgt_arm.pose.bones.get(f'{t_side}_Hand')
    c_rot_hand = pb_hand.constraints.new('COPY_ROTATION')
    c_rot_hand.target = src_arm
    c_rot_hand.subtarget = f'mixamorig:{s_side}Hand'

bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()

print("\n--- EVALUATING CONSTRAINT POSE AT FRAME 1 ---")
for bname in ['C_Hip', 'C_Spine1', 'C_Chest', 'L_UpperArm', 'L_ForeArm', 'L_Hand', 'R_UpperArm', 'R_ForeArm', 'R_Hand', 'L_Thigh', 'L_Knee', 'L_Foot', 'R_Thigh', 'R_Knee', 'R_Foot']:
    pb = tgt_arm.pose.bones.get(bname)
    head_w = tgt_arm.matrix_world @ pb.head
    tail_w = tgt_arm.matrix_world @ pb.tail
    print(f"Chun-Li {bname:12}: head = ({head_w.x:6.3f}, {head_w.y:6.3f}, {head_w.z:6.3f}), tail = ({tail_w.x:6.3f}, {tail_w.y:6.3f}, {tail_w.z:6.3f})")
