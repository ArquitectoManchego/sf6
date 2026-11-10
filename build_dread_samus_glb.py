import sys
sys.path.append(r"C:\Users\Alex\AppData\Roaming\Python\Python313\site-packages")

import bpy
import bmesh
import ssbh_data_py
from mathutils import Vector, Matrix, Euler
import os
import math

print("=====================================================================")
print("BUILDING REALISTIC SAMUS DREAD SUIT (OFFICIAL HIGH-POLY MESH & PBR)")
print("=====================================================================")

BASE_DIR = r"c:\PROYECTOS ANTIGRAVITY\sf6"
MOCAP_DIR = os.path.join(BASE_DIR, "raw_assets", "mocap_fbx")
BODY_DIR = os.path.join(BASE_DIR, r"raw_assets\dread_suit_samus\Dread Suit Samus\Samus Dread Suit\fighter\samus\model\body\c00")
OUTPUT_GLB = os.path.join(BASE_DIR, "public", "models", "samus_dread_suit.glb")

# 1. Reset scene and import base combat mocap rig
bpy.ops.wm.read_factory_settings(use_empty=True)
fbx_idle = os.path.join(MOCAP_DIR, "Bouncing_Fight_Idle.fbx")
bpy.ops.import_scene.fbx(filepath=fbx_idle)

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = "Samus_Armature"

# Remove default dummy meshes
for obj in list(bpy.data.objects):
    if obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)

# 2. Setup PBR Material with official textures
mat = bpy.data.materials.new(name="Samus_Dread_Suit_PBR")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
bsdf = nodes.get("Principled BSDF")

# Albedo
col_path = os.path.join(BODY_DIR, "samus_col.png")
if os.path.exists(col_path):
    img_col = bpy.data.images.load(col_path)
    tex_col = nodes.new('ShaderNodeTexImage')
    tex_col.image = img_col
    links.new(tex_col.outputs['Color'], bsdf.inputs['Base Color'])

# Normal
nor_path = os.path.join(BODY_DIR, "samus_nor.png")
if os.path.exists(nor_path):
    img_nor = bpy.data.images.load(nor_path)
    img_nor.colorspace_settings.name = 'Non-Color'
    tex_nor = nodes.new('ShaderNodeTexImage')
    tex_nor.image = img_nor
    node_nmap = nodes.new('ShaderNodeNormalMap')
    links.new(tex_nor.outputs['Color'], node_nmap.inputs['Color'])
    links.new(node_nmap.outputs['Normal'], bsdf.inputs['Normal'])

# Emission
emi_path = os.path.join(BODY_DIR, "samus_emi.png")
if os.path.exists(emi_path):
    img_emi = bpy.data.images.load(emi_path)
    tex_emi = nodes.new('ShaderNodeTexImage')
    tex_emi.image = img_emi
    if 'Emission Color' in bsdf.inputs:
        links.new(tex_emi.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 2.0
    else:
        links.new(tex_emi.outputs['Color'], bsdf.inputs['Emission'])

# PBR properties
bsdf.inputs['Metallic'].default_value = 0.80
bsdf.inputs['Roughness'].default_value = 0.28

# 3. Read official numshb and construct mesh
numshb_path = os.path.join(BODY_DIR, "model.numshb")
print(f"Reading {numshb_path}...")
mesh_file = ssbh_data_py.mesh_data.read_mesh(numshb_path)

# Bone mapping from SSBU to Mixamo
bone_map = {
    'Hip': 'mixamorig:Hips',
    'Spine1': 'mixamorig:Spine',
    'Spine2': 'mixamorig:Spine1',
    'Bust': 'mixamorig:Spine2',
    'Neck': 'mixamorig:Neck',
    'Head': 'mixamorig:Head',
    'ClavicleL': 'mixamorig:LeftShoulder',
    'ArmL': 'mixamorig:LeftArm',
    'HandL': 'mixamorig:LeftHand',
    'ClavicleR': 'mixamorig:RightShoulder',
    'ArmR': 'mixamorig:RightArm',
    'HandR': 'mixamorig:RightHand',
    'LegL': 'mixamorig:LeftUpLeg',
    'KneeL': 'mixamorig:LeftLeg',
    'FootL': 'mixamorig:LeftFoot',
    'LegR': 'mixamorig:RightUpLeg',
    'KneeR': 'mixamorig:RightLeg',
    'FootR': 'mixamorig:RightFoot'
}

samus_meshes = []
SCALE_FACTOR = 0.082 # Puts Samus at 1.88m canon height

for sub_idx, obj in enumerate(mesh_file.objects):
    # Skip morph ball submesh in standard combat pose
    if "ball" in obj.name.lower():
        continue
        
    mesh_data = bpy.data.meshes.new(name=obj.name)
    
    # SSBU positions are Y up. In Blender with armature, X=X, Y=Z (up), Z=-Y (forward)
    raw_positions = [p[:3] for p in obj.positions[0].data]
    transformed_positions = [
        (p[0] * SCALE_FACTOR, -p[2] * SCALE_FACTOR, (p[1] + 1.5) * SCALE_FACTOR)
        for p in raw_positions
    ]
    
    indices = obj.vertex_indices
    faces = [indices[i:i+3] for i in range(0, len(indices), 3)]
    mesh_data.from_pydata(transformed_positions, [], faces)
    mesh_data.update()
    
    # UV Map
    if obj.texture_coordinates:
        uv_layer = mesh_data.uv_layers.new(name="UVMap")
        uv_data = obj.texture_coordinates[0].data
        for loop in mesh_data.loops:
            v_idx = loop.vertex_index
            u, v = uv_data[v_idx][:2]
            uv_layer.data[loop.index].uv = (u, 1.0 - v)
            
    # Normals
    if obj.normals:
        try:
            normals = [
                Vector((n[0], -n[2], n[1])).normalized()
                for n in obj.normals[0].data
            ]
            mesh_data.normals_split_custom_set_from_vertices(normals)
        except Exception:
            pass
            
    mesh_obj = bpy.data.objects.new(name=f"{obj.name}_{sub_idx}", object_data=mesh_data)
    bpy.context.collection.objects.link(mesh_obj)
    mesh_obj.data.materials.append(mat)
    
    # Vertex Groups & Bone Influences
    if obj.bone_influences:
        for bone_inf in obj.bone_influences:
            target_bone = bone_map.get(bone_inf.bone_name, None)
            if not target_bone:
                # Fallback to closest parent or prefix match
                if 'Arm' in bone_inf.bone_name:
                    target_bone = 'mixamorig:LeftArm' if 'L' in bone_inf.bone_name else 'mixamorig:RightArm'
                elif 'Leg' in bone_inf.bone_name:
                    target_bone = 'mixamorig:LeftUpLeg' if 'L' in bone_inf.bone_name else 'mixamorig:RightUpLeg'
                elif 'Finger' in bone_inf.bone_name:
                    target_bone = 'mixamorig:LeftHand' if 'L' in bone_inf.bone_name else 'mixamorig:RightHand'
                else:
                    target_bone = 'mixamorig:Spine1'
                    
            vg = mesh_obj.vertex_groups.get(target_bone)
            if not vg:
                vg = mesh_obj.vertex_groups.new(name=target_bone)
            for vw in bone_inf.vertex_weights:
                vg.add([vw.vertex_index], vw.vertex_weight, 'ADD')
    else:
        # Default rigid binding for cannon / accessories
        if 'cannon' in obj.name.lower():
            vg = mesh_obj.vertex_groups.new(name='mixamorig:RightHand')
            vg.add(list(range(len(mesh_obj.data.vertices))), 1.0, 'REPLACE')
        else:
            vg = mesh_obj.vertex_groups.new(name='mixamorig:Spine1')
            vg.add(list(range(len(mesh_obj.data.vertices))), 1.0, 'REPLACE')
            
    # Parent to armature
    mesh_obj.parent = arm
    mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    
    # Set smooth shading
    for poly in mesh_obj.data.polygons:
        poly.use_smooth = True
        
    samus_meshes.append(mesh_obj)

print(f"Created {len(samus_meshes)} Samus body parts!")

# 4. Bake Combat Actions into Samus Armature
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

for fbx_name, act_name, start_f, end_f, lock_center in mocap_actions:
    fbx_path = os.path.join(MOCAP_DIR, fbx_name)
    if not os.path.exists(fbx_path):
        continue
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    src_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
    src_act = src_arm.animation_data.action
    
    # Retarget animation
    new_act = bpy.data.actions.new(name=act_name)
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = new_act
    
    total_frames = end_f - start_f + 1
    for frame_idx in range(start_f, end_f + 1):
        rel_f = frame_idx - start_f + 1
        bpy.context.scene.frame_set(frame_idx)
        for pb in arm.pose.bones:
            src_pb = src_arm.pose.bones.get(pb.name)
            if src_pb:
                pb.rotation_quaternion = src_pb.rotation_quaternion.copy()
                pb.location = src_pb.location.copy()
                pb.keyframe_insert(data_path="rotation_quaternion", frame=rel_f)
                if pb.name == 'mixamorig:Hips':
                    pb.keyframe_insert(data_path="location", frame=rel_f)
                    
    # Center lock if needed
    if lock_center:
        fc_list = get_action_fcurves(new_act)
        for fc in fc_list:
            if 'mixamorig:Hips' in fc.data_path and fc.array_index in (0, 1): # X and Y translation
                for kp in fc.keyframe_points:
                    kp.co[1] = 0.0
                    
    new_act.use_fake_user = True
    bpy.data.objects.remove(src_arm, do_unlink=True)
    if src_act:
        bpy.data.actions.remove(src_act)
        
    print(f"Baked Action: {act_name} ({total_frames} frames)")

# Set default action to Idle_Combat
idle_act = bpy.data.actions.get("Idle_Combat")
if idle_act:
    arm.animation_data.action = idle_act

# 5. Export high-quality GLB
print(f"Exporting GLB to {OUTPUT_GLB}...")
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    use_selection=False,
    export_animations=True,
    export_apply=False,
    export_materials='EXPORT'
)

print(f"SUCCESS: Exported {OUTPUT_GLB} ({os.path.getsize(OUTPUT_GLB)} bytes)!")
