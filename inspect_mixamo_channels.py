import bpy
import os
from mathutils import Vector, Quaternion, Matrix, Euler

BASE_DIR = r"c:\PROYECTOS ANTIGRAVITY\sf6"
MOCAP_DIR = os.path.join(BASE_DIR, "raw_assets", "mocap_fbx")
IDLE_FBX = os.path.join(MOCAP_DIR, "Bouncing_Fight_Idle.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IDLE_FBX)
src_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

print("Armature:", src_arm.name)
print("Action:", src_arm.animation_data.action.name if src_arm.animation_data else "None")

bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()

for bname in ['mixamorig:Hips', 'mixamorig:Spine', 'mixamorig:Spine2', 'mixamorig:LeftArm', 'mixamorig:LeftForeArm', 'mixamorig:RightArm', 'mixamorig:RightForeArm']:
    pb = src_arm.pose.bones.get(bname)
    if pb:
        print(f"\n{bname}:")
        print(f"  rotation_mode: {pb.rotation_mode}")
        print(f"  rotation_quaternion: {pb.rotation_quaternion}")
        print(f"  rotation_euler: {pb.rotation_euler}")
        print(f"  matrix_basis rot:\n{pb.matrix_basis.to_quaternion()}")
