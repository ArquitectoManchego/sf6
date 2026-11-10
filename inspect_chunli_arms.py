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

print("\n=== INSPECTING CAPCOM CHUN-LI ARM BONES REST POSE ===")
for bname in ['C_Hip', 'C_Spine1', 'C_Spine2', 'C_Chest', 'L_Shoulder', 'L_UpperArm', 'L_ForeArm', 'L_Hand', 'R_Shoulder', 'R_UpperArm', 'R_ForeArm', 'R_Hand']:
    b = tgt_arm.data.bones.get(bname)
    if b:
        head = b.head_local
        tail = b.tail_local
        vec = tail - head
        quat = b.matrix_local.to_quaternion()
        parent_name = b.parent.name if b.parent else "None"
        print(f"Target '{bname}': parent={parent_name}, head={head}, tail={tail}, vec={vec.normalized()}")

print("\n=== INSPECTING MIXAMO ARM BONES REST POSE ===")
for bname in ['mixamorig:Hips', 'mixamorig:Spine', 'mixamorig:Spine1', 'mixamorig:Spine2', 'mixamorig:LeftShoulder', 'mixamorig:LeftArm', 'mixamorig:LeftForeArm', 'mixamorig:LeftHand', 'mixamorig:RightShoulder', 'mixamorig:RightArm', 'mixamorig:RightForeArm', 'mixamorig:RightHand']:
    b = src_arm.data.bones.get(bname)
    if b:
        head = (src_arm.matrix_world @ b.head_local)
        tail = (src_arm.matrix_world @ b.tail_local)
        vec = tail - head
        print(f"Source '{bname}': head={head}, tail={tail}, vec={vec.normalized()}")

# Now check frame 1 of Mixamo animation
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()

print("\n=== MIXAMO FRAME 1 WORLD POSITIONS & VECTORS ===")
for bname in ['mixamorig:LeftArm', 'mixamorig:LeftForeArm', 'mixamorig:LeftHand', 'mixamorig:RightArm', 'mixamorig:RightForeArm', 'mixamorig:RightHand']:
    pb = src_arm.pose.bones.get(bname)
    head = src_arm.matrix_world @ pb.head
    tail = src_arm.matrix_world @ pb.tail
    vec = tail - head
    print(f"Mixamo Pose '{bname}': head={head}, tail={tail}, vec={vec.normalized()}")
