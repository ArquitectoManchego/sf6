import bpy
import bmesh
import math
import os

print("=====================================================")
print("FEMALE FIGHTERS ROSTER 3D GENERATOR (SF6, KOF, TEKKEN, DOA, DARKSTALKERS)")
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
        
    idle_act = bpy.data.actions.get("Idle_Combat")
    if idle_act:
        arm.animation_data.action = idle_act

def build_humanoid_body(arm, skin_mat, outfit_mat, accent_mat, hair_mat):
    # 1. Head
    h_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ h_bone.head_local
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.115, location=(h_pos.x, h_pos.y, h_pos.z + 0.02))
    head = bpy.context.active_object
    head.scale = (0.9, 1.05, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    head.data.materials.append(skin_mat)
    bind_mesh_to_bone(head, arm, 'mixamorig:Head')

    # 2. Torso / Chest
    c_bone = arm.data.bones.get('mixamorig:Spine2')
    c_pos = arm.matrix_world @ c_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.13, depth=0.24, location=(c_pos.x, c_pos.y, c_pos.z + 0.02))
    chest = bpy.context.active_object
    chest.scale = (1.1, 0.82, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    chest.data.materials.append(outfit_mat)
    bind_mesh_to_bone(chest, arm, 'mixamorig:Spine2')

    # 3. Abdomen & Hips
    s_bone = arm.data.bones.get('mixamorig:Spine')
    s_pos = arm.matrix_world @ s_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.115, depth=0.18, location=(s_pos.x, s_pos.y, s_pos.z + 0.04))
    ab = bpy.context.active_object
    ab.scale = (0.92, 0.78, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    ab.data.materials.append(skin_mat)
    bind_mesh_to_bone(ab, arm, 'mixamorig:Spine')

    hip_bone = arm.data.bones.get('mixamorig:Hips')
    hip_pos = arm.matrix_world @ hip_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.16, location=(hip_pos.x, hip_pos.y, hip_pos.z))
    hips = bpy.context.active_object
    hips.scale = (1.12, 0.88, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    hips.data.materials.append(outfit_mat)
    bind_mesh_to_bone(hips, arm, 'mixamorig:Hips')

    # 4. Limbs
    for side in ['Left', 'Right']:
        # Arm
        arm_b = arm.data.bones.get(f'mixamorig:{side}Arm')
        arm_p = arm.matrix_world @ arm_b.head_local
        bpy.ops.mesh.primitive_cylinder_add(radius=0.048, depth=0.22, location=(arm_p.x, arm_p.y, arm_p.z - 0.1))
        bicep = bpy.context.active_object
        bicep.data.materials.append(skin_mat)
        bind_mesh_to_bone(bicep, arm, f'mixamorig:{side}Arm')

        fa_b = arm.data.bones.get(f'mixamorig:{side}ForeArm')
        fa_p = arm.matrix_world @ fa_b.head_local
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.22, location=(fa_p.x, fa_p.y, fa_p.z - 0.1))
        fa = bpy.context.active_object
        fa.data.materials.append(accent_mat)
        bind_mesh_to_bone(fa, arm, f'mixamorig:{side}ForeArm')

        # Thigh
        t_b = arm.data.bones.get(f'mixamorig:{side}UpLeg')
        t_p = arm.matrix_world @ t_b.head_local
        bpy.ops.mesh.primitive_cylinder_add(radius=0.098, depth=0.38, location=(t_p.x, t_p.y, t_p.z - 0.18))
        thigh = bpy.context.active_object
        thigh.data.materials.append(skin_mat)
        bind_mesh_to_bone(thigh, arm, f'mixamorig:{side}UpLeg')

        # Calf
        l_b = arm.data.bones.get(f'mixamorig:{side}Leg')
        l_p = arm.matrix_world @ l_b.head_local
        bpy.ops.mesh.primitive_cylinder_add(radius=0.076, depth=0.38, location=(l_p.x, l_p.y, l_p.z - 0.18))
        calf = bpy.context.active_object
        calf.data.materials.append(skin_mat)
        bind_mesh_to_bone(calf, arm, f'mixamorig:{side}Leg')

        # Boot
        f_b = arm.data.bones.get(f'mixamorig:{side}Foot')
        f_p = arm.matrix_world @ f_b.head_local
        bpy.ops.mesh.primitive_cube_add(size=0.12, location=(f_p.x, f_p.y - 0.04, f_p.z - 0.05))
        boot = bpy.context.active_object
        boot.scale = (0.75, 1.7, 0.7)
        bpy.ops.object.transform_apply(scale=True)
        boot.data.materials.append(outfit_mat)
        bind_mesh_to_bone(boot, arm, f'mixamorig:{side}Foot')

# 1. CAMMY WHITE (SF6 / Delta Red)
def generate_cammy():
    print(">>> Generating Cammy White (SF6)...")
    arm = load_base_rig()
    mat_skin = create_pbr_material("Cammy_Skin", (0.94, 0.76, 0.65, 1.0), metallic=0.0, roughness=0.50)
    mat_suit = create_pbr_material("Cammy_Leotard", (0.12, 0.35, 0.22, 1.0), metallic=0.20, roughness=0.35)
    mat_red = create_pbr_material("Cammy_RedBeret", (0.85, 0.08, 0.12, 1.0), metallic=0.15, roughness=0.45)
    mat_hair = create_pbr_material("Cammy_Blonde", (0.95, 0.85, 0.40, 1.0), metallic=0.05, roughness=0.55)
    
    build_humanoid_body(arm, mat_skin, mat_suit, mat_red, mat_hair)
    
    # Cammy Crimson Beret
    h_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ h_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.05, location=(h_pos.x + 0.02, h_pos.y, h_pos.z + 0.12), rotation=(0, 0.2, 0))
    beret = bpy.context.active_object
    beret.data.materials.append(mat_red)
    bind_mesh_to_bone(beret, arm, 'mixamorig:Head')

    # Twin Braids
    for side, sign in [('Left', 1), ('Right', -1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.50, location=(h_pos.x + sign*0.09, h_pos.y + 0.08, h_pos.z - 0.15))
        braid = bpy.context.active_object
        braid.data.materials.append(mat_hair)
        bind_mesh_to_bone(braid, arm, 'mixamorig:Head')

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "cammy_sf6.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

# 2. MORRIGAN AENSLAND (Darkstalkers)
def generate_morrigan():
    print(">>> Generating Morrigan Aensland (Darkstalkers)...")
    arm = load_base_rig()
    mat_skin = create_pbr_material("Morrigan_Skin", (0.96, 0.80, 0.72, 1.0), metallic=0.0, roughness=0.45)
    mat_leotard = create_pbr_material("Morrigan_Black", (0.08, 0.08, 0.10, 1.0), metallic=0.40, roughness=0.25)
    mat_wings = create_pbr_material("Morrigan_PurpleWings", (0.45, 0.08, 0.55, 1.0), metallic=0.30, roughness=0.30)
    mat_green_hair = create_pbr_material("Morrigan_GreenHair", (0.20, 0.85, 0.55, 1.0), metallic=0.10, roughness=0.50)

    build_humanoid_body(arm, mat_skin, mat_leotard, mat_leotard, mat_green_hair)

    # Long Cyan-Green Hair
    h_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ h_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.75, location=(h_pos.x, h_pos.y + 0.10, h_pos.z - 0.25))
    hair = bpy.context.active_object
    hair.data.materials.append(mat_green_hair)
    bind_mesh_to_bone(hair, arm, 'mixamorig:Head')

    # Head Bat Wings
    for side, sign in [('Left', 1), ('Right', -1)]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.08, depth=0.24, location=(h_pos.x + sign*0.14, h_pos.y, h_pos.z + 0.10), rotation=(0, sign*0.8, 0))
        wing = bpy.context.active_object
        wing.data.materials.append(mat_wings)
        bind_mesh_to_bone(wing, arm, 'mixamorig:Head')

    # Back Bat Wings (mixamorig:Spine2)
    c_bone = arm.data.bones.get('mixamorig:Spine2')
    c_pos = arm.matrix_world @ c_bone.head_local
    for side, sign in [('Left', 1), ('Right', -1)]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.18, depth=0.45, location=(c_pos.x + sign*0.25, c_pos.y + 0.15, c_pos.z + 0.10), rotation=(0.5, sign*1.2, 0))
        bwing = bpy.context.active_object
        bwing.data.materials.append(mat_wings)
        bind_mesh_to_bone(bwing, arm, 'mixamorig:Spine2')

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "morrigan_darkstalkers.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

# 3. MAI SHIRANUI (KOF)
def generate_mai():
    print(">>> Generating Mai Shiranui (King of Fighters)...")
    arm = load_base_rig()
    mat_skin = create_pbr_material("Mai_Skin", (0.96, 0.78, 0.68, 1.0), metallic=0.0, roughness=0.48)
    mat_red = create_pbr_material("Mai_RedKimono", (0.90, 0.08, 0.10, 1.0), metallic=0.10, roughness=0.40)
    mat_white = create_pbr_material("Mai_WhiteSash", (0.95, 0.95, 0.95, 1.0), metallic=0.05, roughness=0.45)
    mat_hair = create_pbr_material("Mai_BrownHair", (0.18, 0.12, 0.08, 1.0), metallic=0.05, roughness=0.55)
    mat_fan = create_pbr_material("Mai_GoldFan", (0.85, 0.70, 0.25, 1.0), metallic=0.60, roughness=0.30)

    build_humanoid_body(arm, mat_skin, mat_red, mat_white, mat_hair)

    # High Ponytail & White Hair Ribbon
    h_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ h_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.45, location=(h_pos.x, h_pos.y + 0.12, h_pos.z - 0.10), rotation=(0.35, 0, 0))
    ponytail = bpy.context.active_object
    ponytail.data.materials.append(mat_hair)
    bind_mesh_to_bone(ponytail, arm, 'mixamorig:Head')

    # Shiranui Battle Fan (Right Hand)
    rh_bone = arm.data.bones.get('mixamorig:RightHand')
    rh_pos = arm.matrix_world @ rh_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.02, location=(rh_pos.x, rh_pos.y - 0.08, rh_pos.z - 0.02), rotation=(0, math.pi/2, 0))
    fan = bpy.context.active_object
    fan.scale = (0.2, 1.2, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    fan.data.materials.append(mat_fan)
    bind_mesh_to_bone(fan, arm, 'mixamorig:RightHand')

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "mai_shiranui_kof.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

# 4. KASUMI (Dead or Alive)
def generate_kasumi():
    print(">>> Generating Kasumi (Dead or Alive)...")
    arm = load_base_rig()
    mat_skin = create_pbr_material("Kasumi_Skin", (0.95, 0.78, 0.68, 1.0), metallic=0.0, roughness=0.48)
    mat_blue = create_pbr_material("Kasumi_BlueNinja", (0.05, 0.25, 0.75, 1.0), metallic=0.25, roughness=0.35)
    mat_white = create_pbr_material("Kasumi_WhiteArm", (0.94, 0.94, 0.94, 1.0), metallic=0.05, roughness=0.45)
    mat_hair = create_pbr_material("Kasumi_AuburnHair", (0.45, 0.20, 0.12, 1.0), metallic=0.05, roughness=0.55)

    build_humanoid_body(arm, mat_skin, mat_blue, mat_white, mat_hair)

    # Long Auburn Hair with Ribbon
    h_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ h_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.60, location=(h_pos.x, h_pos.y + 0.10, h_pos.z - 0.20), rotation=(0.25, 0, 0))
    hair = bpy.context.active_object
    hair.data.materials.append(mat_hair)
    bind_mesh_to_bone(hair, arm, 'mixamorig:Head')

    # Katana Sheath on Hip
    hip_bone = arm.data.bones.get('mixamorig:Hips')
    hip_pos = arm.matrix_world @ hip_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.65, location=(hip_pos.x - 0.16, hip_pos.y, hip_pos.z - 0.10), rotation=(0.4, 0.2, 0))
    katana = bpy.context.active_object
    katana.data.materials.append(mat_white)
    bind_mesh_to_bone(katana, arm, 'mixamorig:Hips')

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "kasumi_doa.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

# 5. NINA WILLIAMS (Tekken)
def generate_nina():
    print(">>> Generating Nina Williams (Tekken)...")
    arm = load_base_rig()
    mat_skin = create_pbr_material("Nina_Skin", (0.93, 0.75, 0.64, 1.0), metallic=0.0, roughness=0.48)
    mat_purple = create_pbr_material("Nina_StealthPurple", (0.28, 0.08, 0.45, 1.0), metallic=0.40, roughness=0.30)
    mat_camo = create_pbr_material("Nina_DarkCamo", (0.14, 0.15, 0.18, 1.0), metallic=0.35, roughness=0.35)
    mat_hair = create_pbr_material("Nina_Blonde", (0.92, 0.82, 0.42, 1.0), metallic=0.05, roughness=0.55)

    build_humanoid_body(arm, mat_skin, mat_purple, mat_camo, mat_hair)

    h_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ h_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.35, location=(h_pos.x, h_pos.y + 0.10, h_pos.z - 0.08), rotation=(0.2, 0, 0))
    ponytail = bpy.context.active_object
    ponytail.data.materials.append(mat_hair)
    bind_mesh_to_bone(ponytail, arm, 'mixamorig:Head')

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "nina_tekken.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    generate_cammy()
    generate_morrigan()
    generate_mai()
    generate_kasumi()
    generate_nina()
    print("\n>>> ALL ICONIC FEMALE FIGHTERS EXPORTED! <<<")
