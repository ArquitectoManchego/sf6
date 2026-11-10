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

bpy.ops.import_scene.fbx(filepath=IDLE_FBX)
src_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != tgt_arm][0]

bone_pairs = [
    ('mixamorig:Hips', 'C_Hip'),
    ('mixamorig:Spine', 'C_Spine1'),
    ('mixamorig:Spine1', 'C_Spine2'),
    ('mixamorig:Spine2', 'C_Chest'),
    ('mixamorig:LeftShoulder', 'L_Shoulder'),
    ('mixamorig:LeftArm', 'L_UpperArm'),
    ('mixamorig:LeftForeArm', 'L_ForeArm'),
    ('mixamorig:LeftHand', 'L_Hand'),
    ('mixamorig:RightShoulder', 'R_Shoulder'),
    ('mixamorig:RightArm', 'R_UpperArm'),
    ('mixamorig:RightForeArm', 'R_ForeArm'),
    ('mixamorig:RightHand', 'R_Hand'),
    ('mixamorig:LeftUpLeg', 'L_Thigh'),
    ('mixamorig:LeftLeg', 'L_Knee'),
    ('mixamorig:LeftFoot', 'L_Foot'),
    ('mixamorig:RightUpLeg', 'R_Thigh'),
    ('mixamorig:RightLeg', 'R_Knee'),
    ('mixamorig:RightFoot', 'R_Foot'),
]

print("=== COMPARING REST MATRICES (LOCAL TO PARENT) ===")
for s_name, t_name in bone_pairs:
    sb = src_arm.data.bones.get(s_name)
    tb = tgt_arm.data.bones.get(t_name)
    if not sb or not tb:
        continue
    
    # Bone local matrix in armature space (normalized)
    s_mat = (src_arm.matrix_world @ sb.matrix_local).to_3x3()
    s_x = s_mat.col[0].normalized()
    s_y = s_mat.col[1].normalized()
    s_z = s_mat.col[2].normalized()
    
    t_mat = (tgt_arm.matrix_world @ tb.matrix_local).to_3x3()
    t_x = t_mat.col[0].normalized()
    t_y = t_mat.col[1].normalized()
    t_z = t_mat.col[2].normalized()
    
    print(f"\nPair ({s_name} -> {t_name}):")
    print(f"  Src axes:  X={s_x}, Y={s_y}, Z={s_z}")
    print(f"  Tgt axes:  X={t_x}, Y={t_y}, Z={t_z}")
