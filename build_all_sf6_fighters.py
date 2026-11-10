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
OUTPUT_DIR = os.path.join(BASE_DIR, "public", "models")
ESF_BASE = r"E:\SF6_EXTRACTED\BaseGame_Data\re_chunk_001\natives\ps4\product\model\esf"

fighters = [
    {
        "id": "esf006",
        "name": "cammy",
        "glb": "cammy_sf6.glb",
        "head": r"000\00\esf006_000_00.mesh.230110883",
        "body": r"001\01\esf006_001_01.mesh.230110883",
        "extras": [],
        "palette": {
            "Head": ((0.93, 0.77, 0.68, 1.0), 0.0, 0.45),
            "Body": ((0.93, 0.77, 0.68, 1.0), 0.0, 0.45),
            "costume": ((0.14, 0.35, 0.55, 1.0), 0.05, 0.40),
            "Hair": ((0.86, 0.78, 0.52, 1.0), 0.0, 0.55),
            "Boots": ((0.55, 0.12, 0.12, 1.0), 0.15, 0.35),
            "MetalCuffs": ((0.80, 0.12, 0.12, 1.0), 0.85, 0.22)
        }
    },
    {
        "id": "esf010",
        "name": "juri",
        "glb": "juri_sf6.glb",
        "head": r"000\00\esf010_000_00.mesh.230110883",
        "body": r"001\01\esf010_001_01.mesh.230110883",
        "extras": [r"001\02\esf010_001_02.mesh.230110883"],
        "palette": {
            "Head": ((0.94, 0.78, 0.72, 1.0), 0.0, 0.45),
            "Body": ((0.94, 0.78, 0.72, 1.0), 0.0, 0.45),
            "costume": ((0.55, 0.12, 0.58, 1.0), 0.15, 0.35), # Purple spider
            "Hair": ((0.12, 0.10, 0.12, 1.0), 0.0, 0.60), # Dark hair horns
            "Eye": ((0.85, 0.10, 0.75, 1.0), 0.0, 0.15), # Feng Shui Engine eye
            "Metal": ((0.85, 0.85, 0.85, 1.0), 0.90, 0.20)
        }
    },
    {
        "id": "esf007",
        "name": "kimberly",
        "glb": "kimberly_sf6.glb",
        "head": r"000\00\esf007_000_00.mesh.230110883",
        "body": r"001\01\esf007_001_01.mesh.230110883",
        "extras": [r"001\02\esf007_001_02.mesh.230110883"],
        "palette": {
            "Head": ((0.52, 0.35, 0.25, 1.0), 0.0, 0.45), # Dark skin
            "Body": ((0.52, 0.35, 0.25, 1.0), 0.0, 0.45),
            "costume": ((0.92, 0.52, 0.15, 1.0), 0.05, 0.40), # Vibrant orange ninja
            "Hair": ((0.15, 0.12, 0.15, 1.0), 0.0, 0.60),
            "Shoe": ((0.20, 0.65, 0.85, 1.0), 0.1, 0.35)
        }
    },
    {
        "id": "esf011",
        "name": "marisa",
        "glb": "marisa_sf6.glb",
        "head": r"001\00\esf011_001_00.mesh.230110883",
        "body": r"001\01\esf011_001_01.mesh.230110883",
        "extras": [r"001\02\esf011_001_02.mesh.230110883"],
        "palette": {
            "Head": ((0.90, 0.74, 0.65, 1.0), 0.0, 0.45),
            "Body": ((0.90, 0.74, 0.65, 1.0), 0.0, 0.45),
            "costume": ((0.62, 0.18, 0.16, 1.0), 0.05, 0.40), # Gladiator red
            "Hair": ((0.75, 0.25, 0.18, 1.0), 0.0, 0.55), # Red helmet hair
            "Metal": ((0.85, 0.70, 0.20, 1.0), 0.85, 0.25) # Gold ornaments
        }
    },
    {
        "id": "esf009",
        "name": "manon",
        "glb": "manon_sf6.glb",
        "head": r"000\00\esf009_000_00.mesh.230110883",
        "body": r"001\01\esf009_001_01.mesh.230110883",
        "extras": [r"001\02\esf009_001_02.mesh.230110883"],
        "palette": {
            "Head": ((0.94, 0.79, 0.72, 1.0), 0.0, 0.45),
            "Body": ((0.94, 0.79, 0.72, 1.0), 0.0, 0.45),
            "costume": ((0.95, 0.95, 0.95, 1.0), 0.05, 0.35), # White judogi
            "Hair": ((0.95, 0.65, 0.75, 1.0), 0.0, 0.55), # French pink
            "Belt": ((0.85, 0.75, 0.20, 1.0), 0.70, 0.30)
        }
    },
    {
        "id": "esf021",
        "name": "aki",
        "glb": "aki_sf6.glb",
        "head": r"000\00\esf021_000_00.mesh.230110883",
        "body": r"001\01\esf021_001_01.mesh.230110883",
        "extras": [],
        "palette": {
            "Head": ((0.92, 0.82, 0.80, 1.0), 0.0, 0.45), # Pale
            "Body": ((0.92, 0.82, 0.80, 1.0), 0.0, 0.45),
            "costume": ((0.18, 0.24, 0.32, 1.0), 0.15, 0.35), # Dark snake robe
            "Hair": ((0.10, 0.10, 0.12, 1.0), 0.0, 0.60),
            "Claws": ((0.75, 0.80, 0.85, 1.0), 0.92, 0.18) # Silver poison claws
        }
    }
]

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
    ("Combo_Punch.fbx", "Drive_Impact", 25, 88, False)
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

opt_base = {
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

def ensure_file(f_dir, subpath):
    p = os.path.join(f_dir, subpath)
    ps4 = p + ".ps4"
    if not os.path.exists(p) and os.path.exists(ps4):
        shutil.copy2(ps4, p)
    return p

for f in fighters:
    f_dir = os.path.join(ESF_BASE, f["id"])
    out_glb = os.path.join(OUTPUT_DIR, f["glb"])
    
    print(f"\n=======================================================")
    print(f"PROCESSING OFFICIAL SF6 FIGHTER: {f['name'].upper()} ({f['id']})")
    print(f"=======================================================")
    
    head_path = ensure_file(f_dir, f["head"])
    body_path = ensure_file(f_dir, f["body"])
    
    if not os.path.exists(head_path) or not os.path.exists(body_path):
        print(f"Skipping {f['name']}: files not found.")
        continue
        
    # 1. Reset scene & import head
    bpy.ops.wm.read_factory_settings(use_empty=True)
    importREMeshFile(head_path, opt_base)
    
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    head_arm_name = arm.name
    
    # 2. Import body merging armature
    opt_merge = dict(opt_base)
    opt_merge["clearScene"] = False
    opt_merge["mergeArmature"] = head_arm_name
    importREMeshFile(body_path, opt_merge)
    
    # 3. Import extras if present
    for extra in f["extras"]:
        extra_path = ensure_file(f_dir, extra)
        if os.path.exists(extra_path):
            importREMeshFile(extra_path, opt_merge)
            
    # 4. Apply Materials Palette
    for mat in bpy.data.materials:
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if not bsdf:
            continue
        found = False
        for key, (color, metallic, roughness) in f["palette"].items():
            if key.lower() in mat.name.lower():
                bsdf.inputs['Base Color'].default_value = color
                bsdf.inputs['Metallic'].default_value = metallic
                bsdf.inputs['Roughness'].default_value = roughness
                found = True
                break
        if not found:
            bsdf.inputs['Base Color'].default_value = (0.2, 0.2, 0.2, 1.0)
            bsdf.inputs['Metallic'].default_value = 0.1
            bsdf.inputs['Roughness'].default_value = 0.5
            
    # 5. Bake Combat Mocap
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
            
    idle_act = bpy.data.actions.get("Idle_Combat")
    if idle_act:
        arm.animation_data.action = idle_act
        
    # 6. Export GLB
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        export_format='GLB',
        use_selection=False,
        export_animations=True,
        export_apply=False,
        export_materials='EXPORT'
    )
    print(f"SUCCESS: Exported {out_glb} ({os.path.getsize(out_glb)} bytes)!")

print("\n=======================================================")
print("ALL OFFICIAL SF6 FEMALE FIGHTERS EXPORTED SUCCESSFULLY!")
print("=======================================================")
