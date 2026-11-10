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

# Look at bone names in ChunLi:
print("Total bones in Chun-Li:", len(tgt_arm.data.bones))
print("Sample bone names:", [b.name for b in tgt_arm.data.bones if 'Arm' in b.name or 'Leg' in b.name or 'Thigh' in b.name or 'Spine' in b.name or 'Hip' in b.name or 'Hand' in b.name])
