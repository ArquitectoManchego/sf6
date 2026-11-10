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

bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()

# Let's inspect where mixamorig arm bones are at frame 1:
for bname in ['mixamorig:LeftArm', 'mixamorig:LeftForeArm', 'mixamorig:LeftHand', 'mixamorig:RightArm', 'mixamorig:RightForeArm', 'mixamorig:RightHand']:
    pb = src_arm.pose.bones.get(bname)
    print(f"Mixamo {bname:22} head={src_arm.matrix_world @ pb.head}, tail={src_arm.matrix_world @ pb.tail}")

# Now test IK on Chun-Li's L_ForeArm:
pb_l_forearm = tgt_arm.pose.bones.get('L_ForeArm')
c_ik_l = pb_l_forearm.constraints.new('IK')
c_ik_l.target = src_arm
c_ik_l.subtarget = 'mixamorig:LeftHand'
c_ik_l.chain_count = 2

pb_r_forearm = tgt_arm.pose.bones.get('R_ForeArm')
c_ik_r = pb_r_forearm.constraints.new('IK')
c_ik_r.target = src_arm
c_ik_r.subtarget = 'mixamorig:RightHand'
c_ik_r.chain_count = 2

bpy.context.view_layer.update()

print("\n--- AFTER IK CONSTRAINTS ON CHUN-LI FOREARMS ---")
for bname in ['L_UpperArm', 'L_ForeArm', 'L_Hand', 'R_UpperArm', 'R_ForeArm', 'R_Hand']:
    pb = tgt_arm.pose.bones.get(bname)
    print(f"Chun-Li {bname:12} head={tgt_arm.matrix_world @ pb.head}, tail={tgt_arm.matrix_world @ pb.tail}")
