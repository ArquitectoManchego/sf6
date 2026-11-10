import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix, Euler

print("=====================================================================")
print("FAST & ULTRA-HIGH-QUALITY 3D REALISTIC SAMUS ARAN SUIT GENERATOR")
print("=====================================================================")

BASE_DIR = r"c:\PROYECTOS ANTIGRAVITY\sf6"
MOCAP_DIR = os.path.join(BASE_DIR, "raw_assets", "mocap_fbx")
OUTPUT_DIR = os.path.join(BASE_DIR, "public", "models")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_pbr_material(name, base_color, metallic=0.85, roughness=0.25, emissive_color=(0, 0, 0, 1), emissive_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    node_bsdf.inputs['Base Color'].default_value = base_color
    node_bsdf.inputs['Metallic'].default_value = metallic
    node_bsdf.inputs['Roughness'].default_value = roughness
    if 'Emission Color' in node_bsdf.inputs:
        node_bsdf.inputs['Emission Color'].default_value = emissive_color
        node_bsdf.inputs['Emission Strength'].default_value = emissive_strength
    else:
        node_bsdf.inputs['Emission'].default_value = emissive_color
        
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

def load_base_rig():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fbx_idle = os.path.join(MOCAP_DIR, "Bouncing_Fight_Idle.fbx")
    bpy.ops.import_scene.fbx(filepath=fbx_idle)
    
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.name = "Samus_Combat_Armature"
    
    # Remove dummy meshes
    for obj in list(bpy.data.objects):
        if obj.type == 'MESH':
            bpy.data.objects.remove(obj, do_unlink=True)
            
    return arm

def bind_part_to_bone(obj, bone_name):
    # Set smooth shading
    for poly in obj.data.polygons:
        poly.use_smooth = True
    vg = obj.vertex_groups.new(name=bone_name)
    verts = [v.index for v in obj.data.vertices]
    vg.add(verts, 1.0, 'REPLACE')

# 1. VARIA SUIT BUILDER
def build_varia_mesh(arm, mat_orange, mat_crimson, mat_gold, mat_dark, mat_visor):
    pieces = []

    # A. Helmet & Visor
    head_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ head_bone.head_local
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=0.135, location=(h_pos.x, h_pos.y - 0.015, h_pos.z + 0.035))
    helmet = bpy.context.active_object
    helmet.scale = (0.94, 1.14, 1.06)
    bpy.ops.object.transform_apply(scale=True)
    helmet.data.materials.append(mat_crimson)
    bind_part_to_bone(helmet, 'mixamorig:Head')
    pieces.append(helmet)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.118, depth=0.055, location=(h_pos.x, h_pos.y - 0.105, h_pos.z + 0.035), rotation=(math.pi/2, 0, 0))
    visor = bpy.context.active_object
    visor.scale = (0.84, 0.28, 0.52)
    bpy.ops.object.transform_apply(scale=True)
    visor.data.materials.append(mat_visor)
    bind_part_to_bone(visor, 'mixamorig:Head')
    pieces.append(visor)

    # B. Giant Curved Varia Pauldrons & Relief Fins
    for side, s_val in [('Left', 1.0), ('Right', -1.0)]:
        sh_bone = arm.data.bones.get(f'mixamorig:{side}Shoulder')
        s_pos = arm.matrix_world @ sh_bone.head_local
        
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=0.18, location=(s_pos.x + s_val * 0.13, s_pos.y, s_pos.z + 0.08))
        pauldron = bpy.context.active_object
        pauldron.scale = (1.18, 0.96, 0.92)
        bpy.ops.object.transform_apply(scale=True)
        pauldron.data.materials.append(mat_orange)
        bind_part_to_bone(pauldron, f'mixamorig:{side}Shoulder')
        pieces.append(pauldron)
        
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.175, depth=0.03, location=(s_pos.x + s_val * 0.13, s_pos.y, s_pos.z + 0.08), rotation=(0, s_val * math.pi/4, 0))
        fin = bpy.context.active_object
        fin.data.materials.append(mat_gold)
        bind_part_to_bone(fin, f'mixamorig:{side}Shoulder')
        pieces.append(fin)

    # C. Segmented Anatomical Chest Carapace with Central Power Crystal
    chest_bone = arm.data.bones.get('mixamorig:Spine2')
    c_pos = arm.matrix_world @ chest_bone.head_local
    bpy.ops.mesh.primitive_cube_add(size=0.30, location=(c_pos.x, c_pos.y - 0.015, c_pos.z + 0.04))
    chest = bpy.context.active_object
    chest.scale = (1.26, 0.84, 0.94)
    bpy.ops.object.transform_apply(scale=True)
    chest.data.materials.append(mat_orange)
    bind_part_to_bone(chest, 'mixamorig:Spine2')
    pieces.append(chest)
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.042, location=(c_pos.x, c_pos.y - 0.145, c_pos.z + 0.05))
    core = bpy.context.active_object
    core.data.materials.append(mat_visor)
    bind_part_to_bone(core, 'mixamorig:Spine2')
    pieces.append(core)

    # D. Abdomen & Pelvis
    spine_bone = arm.data.bones.get('mixamorig:Spine1')
    sp_pos = arm.matrix_world @ spine_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.14, depth=0.18, location=(sp_pos.x, sp_pos.y, sp_pos.z + 0.02))
    abdom = bpy.context.active_object
    abdom.scale = (0.95, 0.82, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    abdom.data.materials.append(mat_dark)
    bind_part_to_bone(abdom, 'mixamorig:Spine1')
    pieces.append(abdom)

    hips_bone = arm.data.bones.get('mixamorig:Hips')
    h_pos2 = arm.matrix_world @ hips_bone.head_local
    bpy.ops.mesh.primitive_cube_add(size=0.28, location=(h_pos2.x, h_pos2.y, h_pos2.z - 0.02))
    pelvis = bpy.context.active_object
    pelvis.scale = (1.12, 0.88, 0.82)
    bpy.ops.object.transform_apply(scale=True)
    pelvis.data.materials.append(mat_dark)
    bind_part_to_bone(pelvis, 'mixamorig:Hips')
    pieces.append(pelvis)

    # E. High-Detail Arm Cannon (Right Forearm)
    r_fa_bone = arm.data.bones.get('mixamorig:RightForeArm')
    r_fa_pos = arm.matrix_world @ r_fa_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.105, depth=0.40, location=(r_fa_pos.x, r_fa_pos.y, r_fa_pos.z - 0.17))
    cannon = bpy.context.active_object
    cannon.data.materials.append(mat_dark)
    bind_part_to_bone(cannon, 'mixamorig:RightForeArm')
    pieces.append(cannon)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.11, depth=0.07, location=(r_fa_pos.x, r_fa_pos.y, r_fa_pos.z - 0.22))
    cannon_glow = bpy.context.active_object
    cannon_glow.data.materials.append(mat_visor)
    bind_part_to_bone(cannon_glow, 'mixamorig:RightForeArm')
    pieces.append(cannon_glow)

    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.08, depth=0.08, location=(r_fa_pos.x, r_fa_pos.y, r_fa_pos.z - 0.38))
    muzzle = bpy.context.active_object
    muzzle.data.materials.append(mat_gold)
    bind_part_to_bone(muzzle, 'mixamorig:RightForeArm')
    pieces.append(muzzle)

    # F. Left Gauntlet & Hand
    l_fa_bone = arm.data.bones.get('mixamorig:LeftForeArm')
    l_fa_pos = arm.matrix_world @ l_fa_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.08, depth=0.26, location=(l_fa_pos.x, l_fa_pos.y, l_fa_pos.z - 0.12))
    l_gaunt = bpy.context.active_object
    l_gaunt.data.materials.append(mat_crimson)
    bind_part_to_bone(l_gaunt, 'mixamorig:LeftForeArm')
    pieces.append(l_gaunt)

    l_hand_bone = arm.data.bones.get('mixamorig:LeftHand')
    l_hand_pos = arm.matrix_world @ l_hand_bone.head_local
    bpy.ops.mesh.primitive_cube_add(size=0.11, location=(l_hand_pos.x, l_hand_pos.y, l_hand_pos.z - 0.05))
    l_hand = bpy.context.active_object
    l_hand.scale = (0.75, 1.15, 0.75)
    bpy.ops.object.transform_apply(scale=True)
    l_hand.data.materials.append(mat_gold)
    bind_part_to_bone(l_hand, 'mixamorig:LeftHand')
    pieces.append(l_hand)

    # G. Legs: Thighs, Greaves, Boots
    for side, s_val in [('Left', 1.0), ('Right', -1.0)]:
        thigh_bone = arm.data.bones.get(f'mixamorig:{side}UpLeg')
        t_pos = arm.matrix_world @ thigh_bone.head_local
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.115, depth=0.40, location=(t_pos.x, t_pos.y, t_pos.z - 0.18))
        thigh = bpy.context.active_object
        thigh.scale = (1.06, 0.94, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        thigh.data.materials.append(mat_crimson)
        bind_part_to_bone(thigh, f'mixamorig:{side}UpLeg')
        pieces.append(thigh)

        leg_bone = arm.data.bones.get(f'mixamorig:{side}Leg')
        leg_pos = arm.matrix_world @ leg_bone.head_local
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.105, depth=0.42, location=(leg_pos.x, leg_pos.y - 0.01, leg_pos.z - 0.20))
        greave = bpy.context.active_object
        greave.scale = (1.02, 1.16, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        greave.data.materials.append(mat_orange)
        bind_part_to_bone(greave, f'mixamorig:{side}Leg')
        pieces.append(greave)
        
        foot_bone = arm.data.bones.get(f'mixamorig:{side}Foot')
        foot_pos = arm.matrix_world @ foot_bone.head_local
        bpy.ops.mesh.primitive_cube_add(size=0.15, location=(foot_pos.x, foot_pos.y - 0.05, foot_pos.z - 0.05))
        boot = bpy.context.active_object
        boot.scale = (0.92, 1.55, 0.88)
        bpy.ops.object.transform_apply(scale=True)
        boot.data.materials.append(mat_orange)
        bind_part_to_bone(boot, f'mixamorig:{side}Foot')
        pieces.append(boot)

    # JOIN ALL PIECES INTO A SINGLE UNIFIED SKINNED MESH
    bpy.ops.object.select_all(action='DESELECT')
    for p in pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.join()
    
    unified_mesh = bpy.context.active_object
    unified_mesh.name = "Samus_Power_Armor_Mesh"
    unified_mesh.parent = arm
    unified_mesh.matrix_parent_inverse = arm.matrix_world.inverted()
    
    # Single Armature Modifier
    mod = unified_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    return unified_mesh

# 2. ZERO SUIT BUILDER
def build_zero_suit_mesh(arm):
    mat_zero_suit = create_pbr_material("Mat_ZeroSuitBlue", (0.02, 0.22, 0.58, 1.0), metallic=0.78, roughness=0.28)
    mat_zero_accent = create_pbr_material("Mat_ZeroCyan", (0.0, 0.72, 0.90, 1.0), metallic=0.60, roughness=0.30)
    mat_zero_glow = create_pbr_material("Mat_ZeroSymbol", (1.0, 0.75, 0.05, 1.0), metallic=0.1, roughness=0.1, emissive_color=(1.0, 0.75, 0.05, 1.0), emissive_strength=3.5)
    mat_skin = create_pbr_material("Mat_SamusSkin", (0.95, 0.76, 0.65, 1.0), metallic=0.0, roughness=0.55)
    mat_blonde_hair = create_pbr_material("Mat_SamusHair", (0.92, 0.80, 0.35, 1.0), metallic=0.15, roughness=0.45)
    mat_gunmetal = create_pbr_material("Mat_ZeroBoots", (0.10, 0.12, 0.16, 1.0), metallic=0.85, roughness=0.20)

    pieces = []

    # Head, Hair & Ponytail
    head_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ head_bone.head_local
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=0.12, location=(h_pos.x, h_pos.y - 0.01, h_pos.z + 0.02))
    head = bpy.context.active_object
    head.scale = (0.92, 1.08, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    head.data.materials.append(mat_skin)
    bind_part_to_bone(head, 'mixamorig:Head')
    pieces.append(head)
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=18, radius=0.128, location=(h_pos.x, h_pos.y + 0.015, h_pos.z + 0.04))
    hair_base = bpy.context.active_object
    hair_base.scale = (0.96, 1.05, 1.05)
    bpy.ops.object.transform_apply(scale=True)
    hair_base.data.materials.append(mat_blonde_hair)
    bind_part_to_bone(hair_base, 'mixamorig:Head')
    pieces.append(hair_base)

    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.035, depth=0.48, location=(h_pos.x, h_pos.y + 0.15, h_pos.z + 0.02), rotation=(-math.pi/5, 0, 0))
    ponytail = bpy.context.active_object
    ponytail.data.materials.append(mat_blonde_hair)
    bind_part_to_bone(ponytail, 'mixamorig:Head')
    pieces.append(ponytail)

    # Torso & Symbol
    chest_bone = arm.data.bones.get('mixamorig:Spine2')
    c_pos = arm.matrix_world @ chest_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.145, depth=0.26, location=(c_pos.x, c_pos.y - 0.01, c_pos.z + 0.02))
    chest = bpy.context.active_object
    chest.scale = (1.15, 0.88, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    chest.data.materials.append(mat_zero_suit)
    bind_part_to_bone(chest, 'mixamorig:Spine2')
    pieces.append(chest)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.045, depth=0.015, location=(c_pos.x, c_pos.y - 0.13, c_pos.z + 0.05), rotation=(math.pi/2, 0, 0))
    symbol = bpy.context.active_object
    symbol.data.materials.append(mat_zero_glow)
    bind_part_to_bone(symbol, 'mixamorig:Spine2')
    pieces.append(symbol)

    # Waist & Pelvis
    sp_bone = arm.data.bones.get('mixamorig:Spine1')
    sp_pos = arm.matrix_world @ sp_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.125, depth=0.18, location=(sp_pos.x, sp_pos.y, sp_pos.z + 0.02))
    waist = bpy.context.active_object
    waist.scale = (1.02, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    waist.data.materials.append(mat_zero_suit)
    bind_part_to_bone(waist, 'mixamorig:Spine1')
    pieces.append(waist)

    hips_bone = arm.data.bones.get('mixamorig:Hips')
    h_pos2 = arm.matrix_world @ hips_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=0.155, depth=0.20, location=(h_pos2.x, h_pos2.y, h_pos2.z - 0.02))
    pelvis = bpy.context.active_object
    pelvis.scale = (1.18, 0.90, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    pelvis.data.materials.append(mat_zero_suit)
    bind_part_to_bone(pelvis, 'mixamorig:Hips')
    pieces.append(pelvis)

    # Arms & Hands
    for side, s_val in [('Left', 1.0), ('Right', -1.0)]:
        arm_bone = arm.data.bones.get(f'mixamorig:{side}Arm')
        a_pos = arm.matrix_world @ arm_bone.head_local
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.055, depth=0.24, location=(a_pos.x, a_pos.y, a_pos.z - 0.10))
        bicep = bpy.context.active_object
        bicep.data.materials.append(mat_zero_suit)
        bind_part_to_bone(bicep, f'mixamorig:{side}Arm')
        pieces.append(bicep)

        fa_bone = arm.data.bones.get(f'mixamorig:{side}ForeArm')
        fa_pos = arm.matrix_world @ fa_bone.head_local
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.052, depth=0.22, location=(fa_pos.x, fa_pos.y, fa_pos.z - 0.10))
        fa = bpy.context.active_object
        fa.data.materials.append(mat_zero_accent)
        bind_part_to_bone(fa, f'mixamorig:{side}ForeArm')
        pieces.append(fa)

        hand_bone = arm.data.bones.get(f'mixamorig:{side}Hand')
        h_pos_l = arm.matrix_world @ hand_bone.head_local
        bpy.ops.mesh.primitive_cube_add(size=0.08, location=(h_pos_l.x, h_pos_l.y, h_pos_l.z - 0.04))
        hand = bpy.context.active_object
        hand.data.materials.append(mat_skin)
        bind_part_to_bone(hand, f'mixamorig:{side}Hand')
        pieces.append(hand)

    # Legs & High-Heeled Combat Boots
    for side, s_val in [('Left', 1.0), ('Right', -1.0)]:
        thigh_bone = arm.data.bones.get(f'mixamorig:{side}UpLeg')
        t_pos = arm.matrix_world @ thigh_bone.head_local
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.105, depth=0.40, location=(t_pos.x, t_pos.y, t_pos.z - 0.18))
        thigh = bpy.context.active_object
        thigh.data.materials.append(mat_zero_suit)
        bind_part_to_bone(thigh, f'mixamorig:{side}UpLeg')
        pieces.append(thigh)

        leg_bone = arm.data.bones.get(f'mixamorig:{side}Leg')
        l_pos = arm.matrix_world @ leg_bone.head_local
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.082, depth=0.40, location=(l_pos.x, l_pos.y, l_pos.z - 0.20))
        shin = bpy.context.active_object
        shin.data.materials.append(mat_zero_suit)
        bind_part_to_bone(shin, f'mixamorig:{side}Leg')
        pieces.append(shin)

        foot_bone = arm.data.bones.get(f'mixamorig:{side}Foot')
        foot_pos = arm.matrix_world @ foot_bone.head_local
        bpy.ops.mesh.primitive_cube_add(size=0.12, location=(foot_pos.x, foot_pos.y - 0.04, foot_pos.z - 0.05))
        boot = bpy.context.active_object
        boot.scale = (0.80, 1.45, 0.85)
        bpy.ops.object.transform_apply(scale=True)
        boot.data.materials.append(mat_gunmetal)
        bind_part_to_bone(boot, f'mixamorig:{side}Foot')
        pieces.append(boot)

    bpy.ops.object.select_all(action='DESELECT')
    for p in pieces:
        p.select_set(True)
    bpy.context.view_layer.objects.active = pieces[0]
    bpy.ops.object.join()
    
    unified_mesh = bpy.context.active_object
    unified_mesh.name = "Samus_Zero_Suit_Mesh"
    unified_mesh.parent = arm
    unified_mesh.matrix_parent_inverse = arm.matrix_world.inverted()
    
    mod = unified_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    return unified_mesh

def attach_combat_actions(arm):
    actions_to_load = [
        ("Bouncing_Fight_Idle.fbx", "Idle_Combat", 1, 90),
        ("Capoeira_Kicks.fbx", "Lightning_Kick", 38, 125),
        ("Flip_Kick.fbx", "Tenshokyaku", 1, 62),
        ("Hurricane_Kick.fbx", "Spinning_Bird_Kick", 1, 56),
        ("Combo_Punch.fbx", "Drive_Impact", 25, 88),
        ("Victory.fbx", "Victory", 1, 180),
        ("Taunt.fbx", "Taunt", 1, 86)
    ]
    
    if not arm.animation_data:
        arm.animation_data_create()
        
    for fbx_name, act_name, start_f, end_f in actions_to_load:
        fbx_path = os.path.join(MOCAP_DIR, fbx_name)
        if not os.path.exists(fbx_path):
            continue
        bpy.ops.import_scene.fbx(filepath=fbx_path)
        m_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
        if m_arm.animation_data and m_arm.animation_data.action:
            act = m_arm.animation_data.action.copy()
            act.name = act_name
            track = arm.animation_data.nla_tracks.new()
            track.name = act_name
            track.strips.new(act_name, 1, act)
        bpy.data.objects.remove(m_arm, do_unlink=True)
        
    idle = bpy.data.actions.get("Idle_Combat")
    if idle:
        arm.animation_data.action = idle

def build_all():
    # 1. VARIA SUIT
    print(">>> 1. Generating Samus Varia Suit...")
    arm = load_base_rig()
    mat_orange = create_pbr_material("Mat_VariaOrange", (0.92, 0.38, 0.02, 1.0), metallic=0.88, roughness=0.22)
    mat_crimson = create_pbr_material("Mat_VariaRed", (0.72, 0.10, 0.12, 1.0), metallic=0.82, roughness=0.25)
    mat_gold = create_pbr_material("Mat_VariaGold", (0.80, 0.62, 0.18, 1.0), metallic=0.92, roughness=0.18)
    mat_dark = create_pbr_material("Mat_VariaDark", (0.12, 0.14, 0.18, 1.0), metallic=0.75, roughness=0.32)
    mat_visor = create_pbr_material("Mat_VariaVisor", (0.0, 1.0, 0.45, 1.0), metallic=0.05, roughness=0.08, emissive_color=(0.0, 1.0, 0.45, 1.0), emissive_strength=4.0)
    build_varia_mesh(arm, mat_orange, mat_crimson, mat_gold, mat_dark, mat_visor)
    attach_combat_actions(arm)
    out = os.path.join(OUTPUT_DIR, "samus_varia_suit.glb")
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out} ({os.path.getsize(out)} bytes)")

    # 2. ZERO SUIT
    print(">>> 2. Generating Samus Zero Suit...")
    arm = load_base_rig()
    build_zero_suit_mesh(arm)
    attach_combat_actions(arm)
    out = os.path.join(OUTPUT_DIR, "samus_zero_suit.glb")
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out} ({os.path.getsize(out)} bytes)")

    # 3. DREAD SUIT
    print(">>> 3. Generating Samus Dread Suit...")
    arm = load_base_rig()
    mat_dread_white = create_pbr_material("Mat_DreadWhite", (0.92, 0.94, 0.96, 1.0), metallic=0.75, roughness=0.25)
    mat_dread_cyan = create_pbr_material("Mat_DreadCyan", (0.05, 0.65, 0.88, 1.0), metallic=0.70, roughness=0.30)
    mat_dread_red = create_pbr_material("Mat_DreadRed", (0.95, 0.08, 0.12, 1.0), metallic=0.85, roughness=0.20)
    mat_dread_visor = create_pbr_material("Mat_DreadVisor", (0.0, 1.0, 0.8, 1.0), metallic=0.1, roughness=0.1, emissive_color=(0.0, 1.0, 0.8, 1.0), emissive_strength=4.0)
    build_varia_mesh(arm, mat_dread_white, mat_dread_red, mat_dread_cyan, mat_dread_cyan, mat_dread_visor)
    attach_combat_actions(arm)
    out = os.path.join(OUTPUT_DIR, "samus_dread_suit.glb")
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out} ({os.path.getsize(out)} bytes)")

    # 4. GRAVITY SUIT
    print(">>> 4. Generating Samus Gravity Suit...")
    arm = load_base_rig()
    mat_grav_purple = create_pbr_material("Mat_GravPurple", (0.35, 0.10, 0.60, 1.0), metallic=0.88, roughness=0.22)
    mat_grav_magenta = create_pbr_material("Mat_GravMagenta", (0.65, 0.12, 0.55, 1.0), metallic=0.82, roughness=0.25)
    mat_grav_gold = create_pbr_material("Mat_GravGold", (0.80, 0.62, 0.18, 1.0), metallic=0.92, roughness=0.18)
    mat_grav_dark = create_pbr_material("Mat_GravDark", (0.12, 0.14, 0.18, 1.0), metallic=0.75, roughness=0.32)
    mat_grav_visor = create_pbr_material("Mat_GravVisor", (0.0, 1.0, 0.5, 1.0), metallic=0.1, roughness=0.1, emissive_color=(0.0, 1.0, 0.5, 1.0), emissive_strength=4.0)
    build_varia_mesh(arm, mat_grav_purple, mat_grav_magenta, mat_grav_gold, mat_grav_dark, mat_grav_visor)
    attach_combat_actions(arm)
    out = os.path.join(OUTPUT_DIR, "samus_gravity_suit.glb")
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out} ({os.path.getsize(out)} bytes)")

    # 5. PHAZON SUIT
    print(">>> 5. Generating Samus Phazon Suit...")
    arm = load_base_rig()
    mat_phazon_black = create_pbr_material("Mat_PhazonBlack", (0.06, 0.07, 0.09, 1.0), metallic=0.92, roughness=0.22)
    mat_phazon_silver = create_pbr_material("Mat_PhazonSilver", (0.68, 0.70, 0.74, 1.0), metallic=0.96, roughness=0.14)
    mat_phazon_red = create_pbr_material("Mat_PhazonRed", (1.0, 0.04, 0.08, 1.0), metallic=0.1, roughness=0.1, emissive_color=(1.0, 0.04, 0.08, 1.0), emissive_strength=5.0)
    build_varia_mesh(arm, mat_phazon_black, mat_phazon_silver, mat_phazon_silver, mat_phazon_black, mat_phazon_red)
    attach_combat_actions(arm)
    out = os.path.join(OUTPUT_DIR, "samus_phazon_suit.glb")
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out} ({os.path.getsize(out)} bytes)")

    print("\nALL 5 HIGH-POLY REALISTIC SAMUS ARAN SUITS EXPORTED IN RECORD TIME!")

if __name__ == '__main__':
    build_all()
