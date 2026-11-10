import sys
import os
import shutil

addon_dir = r"C:\Users\Alex\AppData\Roaming\Blender Foundation\Blender\4.2\scripts\addons"
if addon_dir not in sys.path:
    sys.path.append(addon_dir)

import bpy
import addon_utils
from mathutils import Vector, Matrix, Euler

addon_utils.enable("re_mesh_editor")
from re_mesh_editor.modules.mesh.blender_re_mesh import importREMeshFile

BASE_DIR = r"c:\PROYECTOS ANTIGRAVITY\sf6"
MOCAP_DIR = os.path.join(BASE_DIR, "raw_assets", "mocap_fbx")
OUTPUT_GLB = os.path.join(BASE_DIR, "public", "models", "cammy_sf6.glb")

base_dir = r"E:\SF6_EXTRACTED\BaseGame_Data\re_chunk_001\natives\ps4\product\model\esf\esf006"

def ensure_mesh(subpath):
    p = os.path.join(base_dir, subpath)
    ps4 = p + ".ps4"
    if not os.path.exists(p) and os.path.exists(ps4):
        shutil.copy2(ps4, p)
    return p

head_mesh = ensure_mesh(r"000\00\esf006_000_00.mesh.230110883")
body_mesh = ensure_mesh(r"001\01\esf006_001_01.mesh.230110883")

print("1. Importing Cammy Head...")
opt_head = {
    "clearScene": True,
    "createCollections": False,
    "loadMaterials": False,
    "loadMDFData": False,
    "loadShellFur": False,
    "loadUnusedTextures": False,
    "loadUnusedProps": False,
    "useBackfaceCulling": False,
    "reloadCachedTextures": False,
    "mdfPath": "",
    "importAllLODs": False,
    "importBlendShapes": False,
    "rotate90": True,
    "mergeArmature": "",
    "importArmatureOnly": False,
    "mergeGroups": False,
    "importShadowMeshes": False,
    "importOcclusionMeshes": False,
    "importBoundingBoxes": False
}
importREMeshFile(head_mesh, opt_head)

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = "Cammy_Capcom_Armature"

print("2. Importing Cammy Costume 1 Body...")
opt_body = dict(opt_head)
opt_body["clearScene"] = False
opt_body["mergeArmature"] = arm.name
importREMeshFile(body_mesh, opt_body)

# 3. Setup Shaders and Materials
palette = {
    "esf_Head00": ((0.93, 0.77, 0.68, 1.0), 0.0, 0.45), # Skin
    "esf_Body00": ((0.93, 0.77, 0.68, 1.0), 0.0, 0.45), # Skin
    "esf_costume00": ((0.14, 0.35, 0.55, 1.0), 0.05, 0.40), # Blue jacket / denim
    "esf_Hair00": ((0.86, 0.78, 0.52, 1.0), 0.0, 0.55), # Blonde hair
    "esf_Hair01": ((0.86, 0.78, 0.52, 1.0), 0.0, 0.55),
    "esf_Hair02": ((0.86, 0.78, 0.52, 1.0), 0.0, 0.55),
    "esf_Boots": ((0.55, 0.12, 0.12, 1.0), 0.15, 0.35), # Crimson boots
    "esf_MetalCuffs": ((0.80, 0.12, 0.12, 1.0), 0.85, 0.22), # Red gauntlets / metal
    "esf_ElbowPads": ((0.15, 0.15, 0.15, 1.0), 0.05, 0.60),
    "esf_Eye00": ((0.20, 0.55, 0.65, 1.0), 0.0, 0.15), # Blue/cyan eyes
    "esf_Mouth00": ((0.75, 0.35, 0.38, 1.0), 0.0, 0.30)
}

for mat in bpy.data.materials:
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        continue
    found = False
    for key, (color, metallic, roughness) in palette.items():
        if key in mat.name:
            bsdf.inputs['Base Color'].default_value = color
            bsdf.inputs['Metallic'].default_value = metallic
            bsdf.inputs['Roughness'].default_value = roughness
            found = True
            break
    if not found:
        # Default smart leather/fabric
        bsdf.inputs['Base Color'].default_value = (0.2, 0.2, 0.2, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.1
        bsdf.inputs['Roughness'].default_value = 0.5

# 4. Retarget Mocap Combat Actions onto RE-Engine Armature
# We map Mixamo mocap bone rotations to Capcom RE-Engine bones
re_bone_map = {
    'mixamorig:Hips': 'C_Hip',
    'mixamorig:Spine': 'C_Spine1',
    'mixamorig:Spine1': 'C_Spine2',
    'mixamorig:Spine2': 'C_Chest',
    'mixamorig:Neck': 'C_Neck',
    'mixamorig:Head': 'C_Head',
    'mixamorig:LeftShoulder': 'L_Clavicle',
    'mixamorig:LeftArm': 'L_Shoulder',
    'mixamorig:LeftForeArm': 'L_Forearm',
    'mixamorig:LeftHand': 'L_Hand',
    'mixamorig:RightShoulder': 'R_Clavicle',
    'mixamorig:RightArm': 'R_Shoulder',
    'mixamorig:RightForeArm': 'R_Forearm',
    'mixamorig:RightHand': 'R_Hand',
    'mixamorig:LeftUpLeg': 'L_Thigh',
    'mixamorig:LeftLeg': 'L_Knee',
    'mixamorig:LeftFoot': 'L_Foot',
    'mixamorig:RightUpLeg': 'R_Thigh',
    'mixamorig:RightLeg': 'R_Knee',
    'mixamorig:RightFoot': 'R_Foot'
}

mocap_actions = [
    ("Bouncing_Fight_Idle.fbx", "Idle_Combat", 1, 90, False),
    ("Capoeira_Kicks.fbx", "Lightning_Kick", 38, 125, False),
    ("Capoeira_Kicks.fbx", "Heavy_Kick", 1, 37, False),
    ("Hurricane_Kick.fbx", "Spinning_Bird_Kick", 1, 56, True),
    ("Flip_Kick.fbx", "Tenshokyaku", 1, 62, True),
    ("Combo_Punch.fbx", "Drive_Impact", 25, 88, False),
    ("Standing_Taunt.fbx", "Taunt", 1, 75, False),
    ("Victory_Pose.fbx", "Victory", 1, 90, False)
]

def get_action_fcurves(act):
    if hasattr(act, 'fcurves') and len(act.fcurves) > 0:
        return act.fcurves
    fcurves = []
    if hasattr(act, 'layers'):
        for layer in act.layers:
            for strip in layer.strips:
                if hasattr(strip, 'channelbags'):
                    for cb in strip.channelbags:
                        fcurves.extend(cb.fcurves)
    return fcurves

for pb in arm.pose.bones:
    pb.rotation_mode = 'QUATERNION'

for fbx_name, act_name, start_f, end_f, lock_center in mocap_actions:
    fbx_path = os.path.join(MOCAP_DIR, fbx_name)
    if not os.path.exists(fbx_path):
        continue
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    src_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
    src_act = src_arm.animation_data.action
    
    new_act = bpy.data.actions.new(name=act_name)
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = new_act
    
    for frame_idx in range(start_f, end_f + 1):
        rel_f = frame_idx - start_f + 1
        bpy.context.scene.frame_set(frame_idx)
        for mix_name, cap_name in re_bone_map.items():
            pb = arm.pose.bones.get(cap_name)
            src_pb = src_arm.pose.bones.get(mix_name)
            if pb and src_pb:
                pb.rotation_quaternion = src_pb.rotation_quaternion.copy()
                pb.keyframe_insert(data_path="rotation_quaternion", frame=rel_f)
                if cap_name == 'C_Hip':
                    pb.location = src_pb.location.copy()
                    pb.keyframe_insert(data_path="location", frame=rel_f)
                    
    if lock_center:
        fc_list = get_action_fcurves(new_act)
        for fc in fc_list:
            if 'C_Hip' in fc.data_path and fc.array_index in (0, 1):
                for kp in fc.keyframe_points:
                    kp.co[1] = 0.0
                    
    new_act.use_fake_user = True
    bpy.data.objects.remove(src_arm, do_unlink=True)
    if src_act:
        bpy.data.actions.remove(src_act)
        
    print(f"Baked Action: {act_name}")

idle_act = bpy.data.actions.get("Idle_Combat")
if idle_act:
    arm.animation_data.action = idle_act

# 5. Export official Cammy GLB
print(f"Exporting official Cammy SF6 to {OUTPUT_GLB}...")
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    use_selection=False,
    export_animations=True,
    export_apply=False,
    export_materials='EXPORT'
)

print(f"SUCCESS: Exported {OUTPUT_GLB} ({os.path.getsize(OUTPUT_GLB)} bytes)!")
