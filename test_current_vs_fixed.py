import bpy
import os
from mathutils import Vector, Quaternion, Matrix, Euler

BASE_DIR = r"c:\PROYECTOS ANTIGRAVITY\sf6"
RAW_DIR = os.path.join(BASE_DIR, "raw_assets", "chunli_sf6", "Raw Files")
CHUNLI_FBX = os.path.join(RAW_DIR, "Chun-Li S4.fbx")
MOCAP_DIR = os.path.join(BASE_DIR, "raw_assets", "mocap_fbx")
IDLE_FBX = os.path.join(MOCAP_DIR, "Bouncing_Fight_Idle.fbx")

# Check existing exported GLB: public/models/chunli_sf6_animated.glb
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(BASE_DIR, "public", "models", "chunli_sf6_animated.glb"))
glb_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

print("=== CHECKING CURRENT EXPORTED GLB (public/models/chunli_sf6_animated.glb) ===")
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()

for bname in ['C_Hip', 'C_Spine1', 'C_Chest', 'L_Shoulder', 'L_UpperArm', 'L_ForeArm', 'L_Hand', 'R_Shoulder', 'R_UpperArm', 'R_ForeArm', 'R_Hand']:
    pb = glb_arm.pose.bones.get(bname)
    if pb:
        head_w = glb_arm.matrix_world @ pb.head
        tail_w = glb_arm.matrix_world @ pb.tail
        print(f"GLB {bname:12}: head = ({head_w.x:6.3f}, {head_w.y:6.3f}, {head_w.z:6.3f}), tail = ({tail_w.x:6.3f}, {tail_w.y:6.3f}, {tail_w.z:6.3f})")

# Now check Mixamo FBX at frame 1:
bpy.ops.import_scene.fbx(filepath=IDLE_FBX)
mix_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != glb_arm][0]
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()

print("\n=== CHECKING MIXAMO FBX AT FRAME 1 ===")
for bname in ['mixamorig:Hips', 'mixamorig:Spine', 'mixamorig:Spine2', 'mixamorig:LeftShoulder', 'mixamorig:LeftArm', 'mixamorig:LeftForeArm', 'mixamorig:LeftHand', 'mixamorig:RightShoulder', 'mixamorig:RightArm', 'mixamorig:RightForeArm', 'mixamorig:RightHand']:
    pb = mix_arm.pose.bones.get(bname)
    if pb:
        head_w = mix_arm.matrix_world @ pb.head
        tail_w = mix_arm.matrix_world @ pb.tail
        print(f"Mixamo {bname:24}: head = ({head_w.x:6.3f}, {head_w.y:6.3f}, {head_w.z:6.3f}), tail = ({tail_w.x:6.3f}, {tail_w.y:6.3f}, {tail_w.z:6.3f})")
