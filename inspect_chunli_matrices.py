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

print("\n--- CAPCOM BONE REST MATRIX LOCAL ---")
for bname in ['C_Hip', 'C_Spine1', 'C_Chest', 'L_UpperArm', 'R_UpperArm']:
    b = tgt_arm.data.bones.get(bname)
    print(f"\nTarget {bname} matrix_local:\n{b.matrix_local.to_3x3()}")
    print(f"Target {bname} rest quat:\n{b.matrix_local.to_quaternion()}")

print("\n--- MIXAMO BONE REST MATRIX LOCAL ---")
for bname in ['mixamorig:Hips', 'mixamorig:Spine', 'mixamorig:Spine2', 'mixamorig:LeftArm', 'mixamorig:RightArm']:
    b = src_arm.data.bones.get(bname)
    m = src_arm.matrix_world @ b.matrix_local
    print(f"\nSource {bname} matrix:\n{m.to_3x3()}")
    print(f"Source {bname} rest quat:\n{m.to_quaternion()}")

# Let's inspect how pose_bone.rotation_quaternion behaves
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()

# Test what happens when we do:
# tgt_pb.rotation_quaternion = quat
pb_l = tgt_arm.pose.bones.get('L_UpperArm')
pb_l.rotation_mode = 'QUATERNION'
print("\n--- TEST POSE BONE L_UpperArm ---")
print("Rest matrix in armature:", pb_l.bone.matrix_local)
print("Pose matrix with rotation_quaternion=(1,0,0,0):", pb_l.matrix)
pb_l.rotation_quaternion = Quaternion((1, 0, 0, 0))
bpy.context.view_layer.update()
print("Evaluated pb_l.matrix after setting identity rot:\n", pb_l.matrix)
print("Compare with bone.matrix_local:\n", pb_l.bone.matrix_local)
