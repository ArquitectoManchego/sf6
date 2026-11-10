import bpy
import bmesh
import math
import os

print("=====================================================")
print("GENERATING SF6 FEMALE FIGHTERS: JURI, MANON, KIMBERLY, MARISA, A.K.I.")
print("=====================================================")

BASE_DIR = r"c:\PROYECTOS ANTIGRAVITY\sf6"
MOCAP_DIR = os.path.join(BASE_DIR, "raw_assets", "mocap_fbx")
OUTPUT_DIR = os.path.join(BASE_DIR, "public", "models")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_pbr_material(name, base_color, metallic=0.2, roughness=0.4, emissive_color=(0, 0, 0, 1), emissive_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Base Color'].default_value = base_color
    node_bsdf.inputs['Metallic'].default_value = metallic
    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Emission Color'].default_value = emissive_color
    node_bsdf.inputs['Emission Strength'].default_value = emissive_strength
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

def load_base_rig():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fbx_idle = os.path.join(MOCAP_DIR, "Bouncing_Fight_Idle.fbx")
    bpy.ops.import_scene.fbx(filepath=fbx_idle)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.name = "Fighter_Armature"
    for obj in list(bpy.data.objects):
        if obj.type == 'MESH':
            bpy.data.objects.remove(obj, do_unlink=True)
    return arm

def bind_mesh_to_bone(obj, arm, bone_name):
    obj.parent = arm
    obj.matrix_parent_inverse = arm.matrix_world.inverted()
    mod = obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    vg = obj.vertex_groups.new(name=bone_name)
    verts = [v.index for v in obj.data.vertices]
    vg.add(verts, 1.0, 'REPLACE')

def attach_combat_actions(arm):
    actions_to_load = [
        ("Idle_Combat", "Bouncing_Fight_Idle.fbx"),
        ("Lightning_Kick", "Capoeira_Kicks.fbx"),
        ("Spinning_Bird_Kick", "Hurricane_Kick.fbx"),
        ("Drive_Impact", "Combo_Punch.fbx"),
        ("Tenshokyaku", "Flip_Kick.fbx"),
        ("Victory", "Victory.fbx"),
        ("Taunt", "Taunt.fbx")
    ]
    if not arm.animation_data:
        arm.animation_data_create()
    for track in list(arm.animation_data.nla_tracks):
        arm.animation_data.nla_tracks.remove(track)
        
    for action_name, fbx_file in actions_to_load:
        path = os.path.join(MOCAP_DIR, fbx_file)
        if not os.path.exists(path):
            continue
        bpy.ops.import_scene.fbx(filepath=path)
        mocap_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
        src_action = mocap_arm.animation_data.action if mocap_arm.animation_data else None
        if src_action:
            new_action = src_action.copy()
            new_action.name = action_name
            track = arm.animation_data.nla_tracks.new()
            track.name = action_name
            start_frame = int(src_action.frame_range[0])
            track.strips.new(action_name, start_frame, new_action)
        bpy.data.objects.remove(mocap_arm, do_unlink=True)
        for obj in list(bpy.data.objects):
            if obj != arm and obj.parent != arm:
                bpy.data.objects.remove(obj, do_unlink=True)
        
    idle_act = bpy.data.actions.get("Idle_Combat")
    if idle_act:
        arm.animation_data.action = idle_act

def build_humanoid_body(arm, skin_mat, outfit_mat, accent_mat, hair_mat, scale_mult=1.0):
    # 1. Head
    h_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ h_bone.head_local
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.115*scale_mult, location=(h_pos.x, h_pos.y, h_pos.z + 0.02*scale_mult))
    head = bpy.context.active_object
    head.scale = (0.9, 1.05, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    head.data.materials.append(skin_mat)
    bind_mesh_to_bone(head, arm, 'mixamorig:Head')

    # 2. Torso / Chest
    c_bone = arm.data.bones.get('mixamorig:Spine2')
    c_pos = arm.matrix_world @ c_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.13*scale_mult, depth=0.24*scale_mult, location=(c_pos.x, c_pos.y, c_pos.z + 0.02*scale_mult))
    chest = bpy.context.active_object
    chest.scale = (1.05, 0.95, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    chest.data.materials.append(outfit_mat)
    bind_mesh_to_bone(chest, arm, 'mixamorig:Spine2')

    # Breasts (Anatomical volumetric breasts)
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.085*scale_mult, location=(c_pos.x + sign*0.075*scale_mult, c_pos.y + 0.10*scale_mult, c_pos.z + 0.03*scale_mult))
        breast = bpy.context.active_object
        breast.scale = (1.0, 1.15, 0.95)
        bpy.ops.object.transform_apply(scale=True)
        breast.data.materials.append(outfit_mat)
        bind_mesh_to_bone(breast, arm, 'mixamorig:Spine2')

    # 3. Waist / Abdomen
    w_bone = arm.data.bones.get('mixamorig:Spine')
    w_pos = arm.matrix_world @ w_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.115*scale_mult, depth=0.18*scale_mult, location=(w_pos.x, w_pos.y, w_pos.z + 0.02*scale_mult))
    waist = bpy.context.active_object
    waist.scale = (0.95, 0.9, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    waist.data.materials.append(skin_mat)
    bind_mesh_to_bone(waist, arm, 'mixamorig:Spine')

    # 4. Pelvis / Hips & Glutes
    p_bone = arm.data.bones.get('mixamorig:Hips')
    p_pos = arm.matrix_world @ p_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.145*scale_mult, depth=0.18*scale_mult, location=(p_pos.x, p_pos.y, p_pos.z))
    pelvis = bpy.context.active_object
    pelvis.scale = (1.15, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    pelvis.data.materials.append(outfit_mat)
    bind_mesh_to_bone(pelvis, arm, 'mixamorig:Hips')

    # Volumetric Glutes
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.105*scale_mult, location=(p_pos.x + sign*0.08*scale_mult, p_pos.y - 0.08*scale_mult, p_pos.z - 0.02*scale_mult))
        glute = bpy.context.active_object
        glute.scale = (1.1, 1.25, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        glute.data.materials.append(outfit_mat)
        bind_mesh_to_bone(glute, arm, 'mixamorig:Hips')

    # 5. Limbs: Arms & Legs
    limbs = [
        ('mixamorig:LeftArm', 'mixamorig:LeftForeArm', -1, outfit_mat, skin_mat),
        ('mixamorig:RightArm', 'mixamorig:RightForeArm', 1, outfit_mat, skin_mat),
        ('mixamorig:LeftUpLeg', 'mixamorig:LeftLeg', -1, outfit_mat, accent_mat),
        ('mixamorig:RightUpLeg', 'mixamorig:RightLeg', 1, outfit_mat, accent_mat)
    ]
    for upper_bone, lower_bone, side, up_mat, low_mat in limbs:
        ub = arm.data.bones.get(upper_bone)
        lb = arm.data.bones.get(lower_bone)
        if ub and lb:
            u_pos = arm.matrix_world @ ub.head_local
            l_pos = arm.matrix_world @ lb.head_local
            
            # Upper limb
            mid_u = (u_pos + l_pos) * 0.5
            rad = 0.085*scale_mult if 'Leg' in upper_bone else 0.05*scale_mult
            bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=0.28*scale_mult, location=mid_u)
            mesh_u = bpy.context.active_object
            mesh_u.data.materials.append(up_mat)
            bind_mesh_to_bone(mesh_u, arm, upper_bone)

            # Lower limb
            rad_l = 0.065*scale_mult if 'Leg' in lower_bone else 0.04*scale_mult
            bpy.ops.mesh.primitive_cylinder_add(radius=rad_l, depth=0.28*scale_mult, location=(l_pos.x, l_pos.y, l_pos.z - 0.14*scale_mult))
            mesh_l = bpy.context.active_object
            mesh_l.data.materials.append(low_mat)
            bind_mesh_to_bone(mesh_l, arm, lower_bone)

# =========================================================
# 1. JURI HAN (SF6)
# =========================================================
def generate_juri():
    print(">>> Generating Juri Han (SF6)...")
    arm = load_base_rig()
    mat_skin = create_pbr_material("Juri_Skin", (0.93, 0.76, 0.68, 1.0), metallic=0.0, roughness=0.42)
    mat_black = create_pbr_material("Juri_LeatherBlack", (0.07, 0.07, 0.09, 1.0), metallic=0.55, roughness=0.22)
    mat_pink = create_pbr_material("Juri_HotPink", (1.0, 0.0, 0.50, 1.0), metallic=0.20, roughness=0.35, emissive_color=(1.0, 0.0, 0.50, 1.0), emissive_strength=0.8)
    mat_purple = create_pbr_material("Juri_Purple", (0.48, 0.17, 0.75, 1.0), metallic=0.30, roughness=0.30)
    mat_hair = create_pbr_material("Juri_HairDark", (0.07, 0.06, 0.08, 1.0), metallic=0.05, roughness=0.55)

    build_humanoid_body(arm, mat_skin, mat_black, mat_purple, mat_hair)

    # Iconic Juri Spider Horn Buns on Head
    h_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ h_bone.head_local
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.055, depth=0.18, location=(h_pos.x + side*0.13, h_pos.y - 0.02, h_pos.z + 0.12), rotation=(0.2, side*0.4, 0))
        bun = bpy.context.active_object
        bun.data.materials.append(mat_hair)
        bind_mesh_to_bone(bun, arm, 'mixamorig:Head')

        # Pink ribbon trim on horns
        bpy.ops.mesh.primitive_torus_add(major_radius=0.06, minor_radius=0.012, location=(h_pos.x + side*0.13, h_pos.y - 0.02, h_pos.z + 0.07))
        rib = bpy.context.active_object
        rib.data.materials.append(mat_pink)
        bind_mesh_to_bone(rib, arm, 'mixamorig:Head')

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "juri_sf6.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

# =========================================================
# 2. MANON (SF6)
# =========================================================
def generate_manon():
    print(">>> Generating Manon (SF6)...")
    arm = load_base_rig()
    mat_skin = create_pbr_material("Manon_Skin", (0.95, 0.82, 0.76, 1.0), metallic=0.0, roughness=0.45)
    mat_navy = create_pbr_material("Manon_JudogiNavy", (0.10, 0.15, 0.28, 1.0), metallic=0.15, roughness=0.45)
    mat_pink = create_pbr_material("Manon_BalletPink", (1.0, 0.79, 0.83, 1.0), metallic=0.10, roughness=0.35)
    mat_gold = create_pbr_material("Manon_MedalGold", (0.95, 0.75, 0.20, 1.0), metallic=0.85, roughness=0.20)
    mat_blonde = create_pbr_material("Manon_BlondeHair", (0.92, 0.80, 0.55, 1.0), metallic=0.05, roughness=0.50)

    build_humanoid_body(arm, mat_skin, mat_navy, mat_pink, mat_blonde)

    # French Chic Ballet Chignon Hair
    h_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ h_bone.head_local
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(h_pos.x, h_pos.y - 0.08, h_pos.z + 0.08))
    bun = bpy.context.active_object
    bun.data.materials.append(mat_blonde)
    bind_mesh_to_bone(bun, arm, 'mixamorig:Head')

    # Golden Judo Medal around neck
    c_bone = arm.data.bones.get('mixamorig:Spine2')
    c_pos = arm.matrix_world @ c_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.015, location=(c_pos.x, c_pos.y + 0.13, c_pos.z + 0.08), rotation=(math.pi/2, 0, 0))
    medal = bpy.context.active_object
    medal.data.materials.append(mat_gold)
    bind_mesh_to_bone(medal, arm, 'mixamorig:Spine2')

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "manon_sf6.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

# =========================================================
# 3. KIMBERLY (SF6)
# =========================================================
def generate_kimberly():
    print(">>> Generating Kimberly (SF6)...")
    arm = load_base_rig()
    mat_skin = create_pbr_material("Kimberly_Skin", (0.42, 0.24, 0.16, 1.0), metallic=0.0, roughness=0.40)
    mat_yellow = create_pbr_material("Kimberly_YellowCrop", (0.98, 0.64, 0.07, 1.0), metallic=0.10, roughness=0.40)
    mat_purple = create_pbr_material("Kimberly_PurplePants", (0.35, 0.10, 0.50, 1.0), metallic=0.20, roughness=0.45)
    mat_spray_teal = create_pbr_material("Kimberly_SprayTeal", (0.02, 0.84, 0.63, 1.0), metallic=0.75, roughness=0.25)
    mat_hair = create_pbr_material("Kimberly_BraidsDark", (0.08, 0.07, 0.08, 1.0), metallic=0.05, roughness=0.60)

    build_humanoid_body(arm, mat_skin, mat_yellow, mat_purple, mat_hair)

    # 80s Walkman Cassette Player & Holster on Hip
    p_bone = arm.data.bones.get('mixamorig:Hips')
    p_pos = arm.matrix_world @ p_bone.head_local
    bpy.ops.mesh.primitive_cube_add(size=0.10, location=(p_pos.x - 0.16, p_pos.y, p_pos.z - 0.02))
    walkman = bpy.context.active_object
    walkman.scale = (0.5, 0.9, 1.1)
    bpy.ops.object.transform_apply(scale=True)
    walkman.data.materials.append(mat_spray_teal)
    bind_mesh_to_bone(walkman, arm, 'mixamorig:Hips')

    # Spray Cans on right hip
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.14, location=(p_pos.x + 0.16, p_pos.y, p_pos.z - 0.02))
    spray = bpy.context.active_object
    spray.data.materials.append(mat_spray_teal)
    bind_mesh_to_bone(spray, arm, 'mixamorig:Hips')

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "kimberly_sf6.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

# =========================================================
# 4. MARISA (SF6)
# =========================================================
def generate_marisa():
    print(">>> Generating Marisa (SF6)...")
    arm = load_base_rig()
    mat_skin = create_pbr_material("Marisa_Skin", (0.92, 0.74, 0.62, 1.0), metallic=0.0, roughness=0.35)
    mat_crimson = create_pbr_material("Marisa_GladiatorRed", (0.75, 0.07, 0.12, 1.0), metallic=0.65, roughness=0.25)
    mat_gold = create_pbr_material("Marisa_SpartanGold", (0.88, 0.66, 0.22, 1.0), metallic=0.85, roughness=0.22)
    mat_redhair = create_pbr_material("Marisa_SpartanHair", (0.64, 0.09, 0.10, 1.0), metallic=0.10, roughness=0.50)

    # Marisa is colossal and powerhouse muscular: scale 1.25x
    build_humanoid_body(arm, mat_skin, mat_crimson, mat_gold, mat_redhair, scale_mult=1.25)

    # Spartan Helmet Crest Hair
    h_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ h_bone.head_local
    bpy.ops.mesh.primitive_cube_add(size=0.14, location=(h_pos.x, h_pos.y, h_pos.z + 0.14))
    crest = bpy.context.active_object
    crest.scale = (0.45, 1.4, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    crest.data.materials.append(mat_redhair)
    bind_mesh_to_bone(crest, arm, 'mixamorig:Head')

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "marisa_sf6.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

# =========================================================
# 5. A.K.I. (SF6)
# =========================================================
def generate_aki():
    print(">>> Generating A.K.I. (SF6)...")
    arm = load_base_rig()
    mat_skin = create_pbr_material("AKI_Skin", (0.94, 0.84, 0.80, 1.0), metallic=0.0, roughness=0.45)
    mat_white_silk = create_pbr_material("AKI_WhiteSerpent", (0.95, 0.95, 0.96, 1.0), metallic=0.20, roughness=0.25)
    mat_emerald = create_pbr_material("AKI_PoisonEmerald", (0.0, 0.96, 0.65, 1.0), metallic=0.60, roughness=0.20, emissive_color=(0.0, 0.96, 0.65, 1.0), emissive_strength=0.9)
    mat_hair_dark = create_pbr_material("AKI_HairDark", (0.05, 0.05, 0.06, 1.0), metallic=0.05, roughness=0.55)

    build_humanoid_body(arm, mat_skin, mat_white_silk, mat_emerald, mat_hair_dark)

    # Poison Serpent Claws on Forearms
    for arm_bone_name, side in [('mixamorig:LeftForeArm', -1), ('mixamorig:RightForeArm', 1)]:
        fa_bone = arm.data.bones.get(arm_bone_name)
        fa_pos = arm.matrix_world @ fa_bone.head_local
        bpy.ops.mesh.primitive_cone_add(radius1=0.035, depth=0.18, location=(fa_pos.x + side*0.06, fa_pos.y - 0.16, fa_pos.z - 0.02), rotation=(0, math.pi, 0))
        claw = bpy.context.active_object
        claw.data.materials.append(mat_emerald)
        bind_mesh_to_bone(claw, arm, arm_bone_name)

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "aki_sf6.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    generate_juri()
    generate_manon()
    generate_kimberly()
    generate_marisa()
    generate_aki()
    print("\n>>> ALL SF6 FEMALE FIGHTERS EXPORTED WITH COMBAT MOCAP! <<<")
