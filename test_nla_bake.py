import bpy
import os

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

# Setup constraints
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

# 4. Arms
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

# Select all pose bones in target armature
bpy.context.view_layer.objects.active = tgt_arm
bpy.ops.object.mode_set(mode='POSE')
for pb in tgt_arm.pose.bones:
    pb.bone.select = True

# Bake
bpy.ops.nla.bake(
    frame_start=1,
    frame_end=10,
    only_selected=False,
    visual_keying=True,
    clear_constraints=True,
    bake_types={'POSE'}
)

print("Bake complete. Checking bone positions at frame 1 without constraints:")
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()

for bname in ['L_UpperArm', 'L_ForeArm', 'L_Hand', 'R_UpperArm', 'R_ForeArm', 'R_Hand']:
    pb = tgt_arm.pose.bones.get(bname)
    head_w = tgt_arm.matrix_world @ pb.head
    tail_w = tgt_arm.matrix_world @ pb.tail
    print(f"Baked {bname:12}: head = ({head_w.x:6.3f}, {head_w.y:6.3f}, {head_w.z:6.3f}), tail = ({tail_w.x:6.3f}, {tail_w.y:6.3f}, {tail_w.z:6.3f})")
