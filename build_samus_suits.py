import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix, Euler

print("=====================================================")
print("METROID PRIME -> DREAD: SAMUS ARAN 3D SUIT GENERATOR")
print("=====================================================")

BASE_DIR = r"c:\PROYECTOS ANTIGRAVITY\sf6"
MOCAP_DIR = os.path.join(BASE_DIR, "raw_assets", "mocap_fbx")
OUTPUT_DIR = os.path.join(BASE_DIR, "public", "models")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Helper: Create PBR Material
def create_pbr_material(name, base_color, metallic=0.8, roughness=0.3, emissive_color=(0, 0, 0, 1), emissive_strength=0.0):
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

# Load FBX Rig and Actions
def load_base_rig():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fbx_idle = os.path.join(MOCAP_DIR, "Bouncing_Fight_Idle.fbx")
    bpy.ops.import_scene.fbx(filepath=fbx_idle)
    
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.name = "Samus_Armature"
    
    # Remove dummy meshes from Mixamo import
    for obj in list(bpy.data.objects):
        if obj.type == 'MESH':
            bpy.data.objects.remove(obj, do_unlink=True)
            
    return arm

# Helper: Assign all vertices of an object to a bone with weight 1.0
def bind_mesh_to_bone(obj, arm, bone_name):
    obj.parent = arm
    obj.matrix_parent_inverse = arm.matrix_world.inverted()
    mod = obj.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm
    vg = obj.vertex_groups.new(name=bone_name)
    verts = [v.index for v in obj.data.vertices]
    vg.add(verts, 1.0, 'REPLACE')

def create_varia_suit_meshes(arm):
    created_objects = []
    
    # Materials
    mat_orange = create_pbr_material("Mat_VariaOrange", (0.90, 0.36, 0.0, 1.0), metallic=0.85, roughness=0.28)
    mat_crimson = create_pbr_material("Mat_VariaRed", (0.70, 0.11, 0.11, 1.0), metallic=0.80, roughness=0.30)
    mat_gold = create_pbr_material("Mat_VariaGold", (0.76, 0.60, 0.22, 1.0), metallic=0.90, roughness=0.20)
    mat_dark = create_pbr_material("Mat_VariaDark", (0.15, 0.16, 0.20, 1.0), metallic=0.80, roughness=0.35)
    mat_visor = create_pbr_material("Mat_VariaVisor", (0.0, 1.0, 0.4, 1.0), metallic=0.1, roughness=0.1, emissive_color=(0.0, 1.0, 0.4, 1.0), emissive_strength=3.5)

    # 1. Helmet (mixamorig:Head)
    head_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ head_bone.head_local
    
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(h_pos.x, h_pos.y - 0.02, h_pos.z + 0.04))
    helmet = bpy.context.active_object
    helmet.name = "Samus_Helmet"
    helmet.scale = (0.95, 1.15, 1.05)
    bpy.ops.object.transform_apply(scale=True)
    helmet.data.materials.append(mat_crimson)
    bind_mesh_to_bone(helmet, arm, 'mixamorig:Head')
    created_objects.append(helmet)
    
    # Visor (T-Visor)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.115, depth=0.06, location=(h_pos.x, h_pos.y - 0.11, h_pos.z + 0.04), rotation=(math.pi/2, 0, 0))
    visor = bpy.context.active_object
    visor.name = "Samus_Visor"
    visor.scale = (0.85, 0.3, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    visor.data.materials.append(mat_visor)
    bind_mesh_to_bone(visor, arm, 'mixamorig:Head')
    created_objects.append(visor)

    # 2. Chestplate & Torso (mixamorig:Spine2)
    chest_bone = arm.data.bones.get('mixamorig:Spine2')
    c_pos = arm.matrix_world @ chest_bone.head_local
    bpy.ops.mesh.primitive_cube_add(size=0.28, location=(c_pos.x, c_pos.y - 0.02, c_pos.z + 0.05))
    chest = bpy.context.active_object
    chest.name = "Samus_Chest"
    chest.scale = (1.25, 0.85, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    chest.data.materials.append(mat_orange)
    bind_mesh_to_bone(chest, arm, 'mixamorig:Spine2')
    created_objects.append(chest)
    
    # Abdomen / Midsection (mixamorig:Spine)
    spine_bone = arm.data.bones.get('mixamorig:Spine')
    s_pos = arm.matrix_world @ spine_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.18, location=(s_pos.x, s_pos.y, s_pos.z + 0.05))
    ab = bpy.context.active_object
    ab.name = "Samus_Abdomen"
    ab.scale = (0.9, 0.75, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    ab.data.materials.append(mat_dark)
    bind_mesh_to_bone(ab, arm, 'mixamorig:Spine')
    created_objects.append(ab)

    # 3. Pelvis & Hip Armor (mixamorig:Hips)
    hip_bone = arm.data.bones.get('mixamorig:Hips')
    hip_pos = arm.matrix_world @ hip_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.17, depth=0.16, location=(hip_pos.x, hip_pos.y, hip_pos.z))
    pelvis = bpy.context.active_object
    pelvis.name = "Samus_Pelvis"
    pelvis.scale = (1.1, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    pelvis.data.materials.append(mat_orange)
    bind_mesh_to_bone(pelvis, arm, 'mixamorig:Hips')
    created_objects.append(pelvis)

    # 4. Giant Spherical Pauldrons (Left & Right Shoulders)
    # Right Pauldron
    r_sh_bone = arm.data.bones.get('mixamorig:RightShoulder')
    r_sh_pos = arm.matrix_world @ r_sh_bone.tail_local
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, location=(r_sh_pos.x, r_sh_pos.y, r_sh_pos.z + 0.05))
    r_paul = bpy.context.active_object
    r_paul.name = "Samus_Pauldron_R"
    r_paul.data.materials.append(mat_orange)
    bind_mesh_to_bone(r_paul, arm, 'mixamorig:RightShoulder')
    created_objects.append(r_paul)

    # Left Pauldron
    l_sh_bone = arm.data.bones.get('mixamorig:LeftShoulder')
    l_sh_pos = arm.matrix_world @ l_sh_bone.tail_local
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17, location=(l_sh_pos.x, l_sh_pos.y, l_sh_pos.z + 0.05))
    l_paul = bpy.context.active_object
    l_paul.name = "Samus_Pauldron_L"
    l_paul.data.materials.append(mat_orange)
    bind_mesh_to_bone(l_paul, arm, 'mixamorig:LeftShoulder')
    created_objects.append(l_paul)

    # 5. Right Arm: Bicep & THE ICONIC ARM CANNON!
    r_arm_bone = arm.data.bones.get('mixamorig:RightArm')
    r_arm_pos = arm.matrix_world @ r_arm_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.22, location=(r_arm_pos.x, r_arm_pos.y, r_arm_pos.z - 0.1))
    r_bicep = bpy.context.active_object
    r_bicep.name = "Samus_Bicep_R"
    r_bicep.data.materials.append(mat_crimson)
    bind_mesh_to_bone(r_bicep, arm, 'mixamorig:RightArm')
    created_objects.append(r_bicep)

    # Arm Cannon (mixamorig:RightForeArm)
    r_fa_bone = arm.data.bones.get('mixamorig:RightForeArm')
    r_fa_pos = arm.matrix_world @ r_fa_bone.head_local
    
    # Main Cannon Barrel
    bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.38, location=(r_fa_pos.x, r_fa_pos.y, r_fa_pos.z - 0.16))
    cannon = bpy.context.active_object
    cannon.name = "Samus_ArmCannon_Body"
    cannon.data.materials.append(mat_dark)
    bind_mesh_to_bone(cannon, arm, 'mixamorig:RightForeArm')
    created_objects.append(cannon)
    
    # Cannon Emitter Ring (Glowing Green Energy Core)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.105, depth=0.06, location=(r_fa_pos.x, r_fa_pos.y, r_fa_pos.z - 0.22))
    cannon_ring = bpy.context.active_object
    cannon_ring.name = "Samus_ArmCannon_Ring"
    cannon_ring.data.materials.append(mat_visor)
    bind_mesh_to_bone(cannon_ring, arm, 'mixamorig:RightForeArm')
    created_objects.append(cannon_ring)

    # Cannon Muzzle Cap
    bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.08, location=(r_fa_pos.x, r_fa_pos.y, r_fa_pos.z - 0.36))
    cannon_tip = bpy.context.active_object
    cannon_tip.name = "Samus_ArmCannon_Muzzle"
    cannon_tip.data.materials.append(mat_dark)
    bind_mesh_to_bone(cannon_tip, arm, 'mixamorig:RightForeArm')
    created_objects.append(cannon_tip)

    # 6. Left Arm: Gauntlet & Hand
    l_arm_bone = arm.data.bones.get('mixamorig:LeftArm')
    l_arm_pos = arm.matrix_world @ l_arm_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.22, location=(l_arm_pos.x, l_arm_pos.y, l_arm_pos.z - 0.1))
    l_bicep = bpy.context.active_object
    l_bicep.name = "Samus_Bicep_L"
    l_bicep.data.materials.append(mat_crimson)
    bind_mesh_to_bone(l_bicep, arm, 'mixamorig:LeftArm')
    created_objects.append(l_bicep)

    l_fa_bone = arm.data.bones.get('mixamorig:LeftForeArm')
    l_fa_pos = arm.matrix_world @ l_fa_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.24, location=(l_fa_pos.x, l_fa_pos.y, l_fa_pos.z - 0.12))
    l_gaunt = bpy.context.active_object
    l_gaunt.name = "Samus_Gauntlet_L"
    l_gaunt.data.materials.append(mat_crimson)
    bind_mesh_to_bone(l_gaunt, arm, 'mixamorig:LeftForeArm')
    created_objects.append(l_gaunt)

    l_hand_bone = arm.data.bones.get('mixamorig:LeftHand')
    l_hand_pos = arm.matrix_world @ l_hand_bone.head_local
    bpy.ops.mesh.primitive_cube_add(size=0.10, location=(l_hand_pos.x, l_hand_pos.y, l_hand_pos.z - 0.05))
    l_hand = bpy.context.active_object
    l_hand.name = "Samus_Hand_L"
    l_hand.scale = (0.7, 1.1, 0.7)
    bpy.ops.object.transform_apply(scale=True)
    l_hand.data.materials.append(mat_gold)
    bind_mesh_to_bone(l_hand, arm, 'mixamorig:LeftHand')
    created_objects.append(l_hand)

    # 7. Legs: Thighs, Greaves, Power Boots
    for side in ['Left', 'Right']:
        # Thigh
        thigh_bone = arm.data.bones.get(f'mixamorig:{side}UpLeg')
        t_pos = arm.matrix_world @ thigh_bone.head_local
        bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.38, location=(t_pos.x, t_pos.y, t_pos.z - 0.18))
        thigh = bpy.context.active_object
        thigh.name = f"Samus_Thigh_{side}"
        thigh.scale = (1.05, 0.95, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        thigh.data.materials.append(mat_crimson)
        bind_mesh_to_bone(thigh, arm, f'mixamorig:{side}UpLeg')
        created_objects.append(thigh)

        # Knee / Shin Greave
        leg_bone = arm.data.bones.get(f'mixamorig:{side}Leg')
        leg_pos = arm.matrix_world @ leg_bone.head_local
        bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.40, location=(leg_pos.x, leg_pos.y - 0.01, leg_pos.z - 0.20))
        shin = bpy.context.active_object
        shin.name = f"Samus_Greave_{side}"
        shin.scale = (1.0, 1.15, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        shin.data.materials.append(mat_orange)
        bind_mesh_to_bone(shin, arm, f'mixamorig:{side}Leg')
        created_objects.append(shin)

        # Power Boot
        foot_bone = arm.data.bones.get(f'mixamorig:{side}Foot')
        foot_pos = arm.matrix_world @ foot_bone.head_local
        bpy.ops.mesh.primitive_cube_add(size=0.14, location=(foot_pos.x, foot_pos.y - 0.05, foot_pos.z - 0.05))
        boot = bpy.context.active_object
        boot.name = f"Samus_Boot_{side}"
        boot.scale = (1.0, 1.8, 0.8)
        bpy.ops.object.transform_apply(scale=True)
        boot.data.materials.append(mat_gold)
        bind_mesh_to_bone(boot, arm, f'mixamorig:{side}Foot')
        created_objects.append(boot)

    return created_objects

# Bake Mocap Actions to Armature
def attach_combat_actions(arm):
    actions_to_load = [
        ("Idle_Combat", "Bouncing_Fight_Idle.fbx"),
        ("Charge_Shot", "Combo_Punch.fbx"),
        ("Screw_Attack", "Hurricane_Kick.fbx"),
        ("Missile_Fire", "Flip_Kick.fbx"),
        ("Taunt", "Taunt.fbx"),
        ("Victory", "Victory.fbx")
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
        # Clean up any stray meshes from FBX import
        for obj in list(bpy.data.objects):
            if obj != arm and obj.parent != arm:
                bpy.data.objects.remove(obj, do_unlink=True)
        
    # Set default action to Idle_Combat
    idle_act = bpy.data.actions.get("Idle_Combat")
    if idle_act:
        arm.animation_data.action = idle_act

# Build and Export Suits
def build_and_export_suits():
    # 1. VARIA SUIT
    print(">>> Generating Samus Varia Suit (Metroid Prime)...")
    arm = load_base_rig()
    create_varia_suit_meshes(arm)
    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "samus_varia_suit.glb")
    # Clean up stray meshes
    for o in list(bpy.data.objects):
        if "Icosphere" in o.name or o.name.startswith("Cube.") or o.name.startswith("Cylinder."):
            if o.parent != arm:
                bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

    # 2. ZERO SUIT SAMUS
    print(">>> Generating Zero Suit Samus...")
    arm = load_base_rig()
    # Materials for Zero Suit
    mat_zero_blue = create_pbr_material("Mat_ZeroBlue", (0.04, 0.22, 0.62, 1.0), metallic=0.25, roughness=0.35)
    mat_zero_cyan = create_pbr_material("Mat_ZeroCyan", (0.0, 0.95, 0.85, 1.0), metallic=0.1, roughness=0.2, emissive_color=(0.0, 0.95, 0.85, 1.0), emissive_strength=2.5)
    mat_hair_blonde = create_pbr_material("Mat_HairBlonde", (0.95, 0.82, 0.35, 1.0), metallic=0.05, roughness=0.55)
    mat_skin = create_pbr_material("Mat_ZeroSkin", (0.92, 0.72, 0.60, 1.0), metallic=0.0, roughness=0.50)
    mat_paralyzer = create_pbr_material("Mat_Paralyzer", (0.2, 0.22, 0.25, 1.0), metallic=0.85, roughness=0.25, emissive_color=(1.0, 0.9, 0.1, 1.0), emissive_strength=1.5)

    # Head & Ponytail
    h_bone = arm.data.bones.get('mixamorig:Head')
    h_pos = arm.matrix_world @ h_bone.head_local
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(h_pos.x, h_pos.y, h_pos.z + 0.02))
    head = bpy.context.active_object
    head.scale = (0.9, 1.05, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    head.data.materials.append(mat_skin)
    bind_mesh_to_bone(head, arm, 'mixamorig:Head')
    
    # Hair Ponytail
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.35, location=(h_pos.x, h_pos.y + 0.14, h_pos.z - 0.05), rotation=(0.4, 0, 0))
    hair = bpy.context.active_object
    hair.data.materials.append(mat_hair_blonde)
    bind_mesh_to_bone(hair, arm, 'mixamorig:Head')

    # Athletic Torso & Body
    c_bone = arm.data.bones.get('mixamorig:Spine2')
    c_pos = arm.matrix_world @ c_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.25, location=(c_pos.x, c_pos.y, c_pos.z + 0.03))
    torso = bpy.context.active_object
    torso.scale = (1.1, 0.8, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(mat_zero_blue)
    bind_mesh_to_bone(torso, arm, 'mixamorig:Spine2')

    # Insignia Core
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.03, location=(c_pos.x - 0.04, c_pos.y - 0.11, c_pos.z + 0.05), rotation=(math.pi/2, 0, 0))
    core = bpy.context.active_object
    core.data.materials.append(mat_zero_cyan)
    bind_mesh_to_bone(core, arm, 'mixamorig:Spine2')

    # Waist & Pelvis
    hip_bone = arm.data.bones.get('mixamorig:Hips')
    hip_pos = arm.matrix_world @ hip_bone.head_local
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.18, location=(hip_pos.x, hip_pos.y, hip_pos.z))
    hips = bpy.context.active_object
    hips.scale = (1.05, 0.85, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    hips.data.materials.append(mat_zero_blue)
    bind_mesh_to_bone(hips, arm, 'mixamorig:Hips')

    # Arms & Paralyzer Gun in Right Hand
    for side in ['Left', 'Right']:
        # Arm
        arm_b = arm.data.bones.get(f'mixamorig:{side}Arm')
        arm_p = arm.matrix_world @ arm_b.head_local
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.22, location=(arm_p.x, arm_p.y, arm_p.z - 0.1))
        bicep = bpy.context.active_object
        bicep.data.materials.append(mat_zero_blue)
        bind_mesh_to_bone(bicep, arm, f'mixamorig:{side}Arm')

        # Forearm
        fa_b = arm.data.bones.get(f'mixamorig:{side}ForeArm')
        fa_p = arm.matrix_world @ fa_b.head_local
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.22, location=(fa_p.x, fa_p.y, fa_p.z - 0.1))
        fa = bpy.context.active_object
        fa.data.materials.append(mat_zero_blue)
        bind_mesh_to_bone(fa, arm, f'mixamorig:{side}ForeArm')

    # Paralyzer Gun (Right Hand)
    rh_b = arm.data.bones.get('mixamorig:RightHand')
    rh_p = arm.matrix_world @ rh_b.head_local
    bpy.ops.mesh.primitive_cube_add(size=0.12, location=(rh_p.x, rh_p.y - 0.08, rh_p.z - 0.05))
    gun = bpy.context.active_object
    gun.scale = (0.4, 1.8, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    gun.data.materials.append(mat_paralyzer)
    bind_mesh_to_bone(gun, arm, 'mixamorig:RightHand')

    # Athletic Legs & Jet Boots
    for side in ['Left', 'Right']:
        t_b = arm.data.bones.get(f'mixamorig:{side}UpLeg')
        t_p = arm.matrix_world @ t_b.head_local
        bpy.ops.mesh.primitive_cylinder_add(radius=0.095, depth=0.38, location=(t_p.x, t_p.y, t_p.z - 0.18))
        thigh = bpy.context.active_object
        thigh.data.materials.append(mat_zero_blue)
        bind_mesh_to_bone(thigh, arm, f'mixamorig:{side}UpLeg')

        l_b = arm.data.bones.get(f'mixamorig:{side}Leg')
        l_p = arm.matrix_world @ l_b.head_local
        bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.38, location=(l_p.x, l_p.y, l_p.z - 0.18))
        calf = bpy.context.active_object
        calf.data.materials.append(mat_zero_blue)
        bind_mesh_to_bone(calf, arm, f'mixamorig:{side}Leg')

        f_b = arm.data.bones.get(f'mixamorig:{side}Foot')
        f_p = arm.matrix_world @ f_b.head_local
        bpy.ops.mesh.primitive_cube_add(size=0.12, location=(f_p.x, f_p.y - 0.04, f_p.z - 0.05))
        boot = bpy.context.active_object
        boot.scale = (0.8, 1.7, 0.6)
        bpy.ops.object.transform_apply(scale=True)
        boot.data.materials.append(mat_zero_cyan)
        bind_mesh_to_bone(boot, arm, f'mixamorig:{side}Foot')

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "samus_zero_suit.glb")
    # Clean up stray meshes
    for o in list(bpy.data.objects):
        if "Icosphere" in o.name or o.name.startswith("Cube.") or o.name.startswith("Cylinder."):
            if o.parent != arm:
                bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

    # 3. METROID DREAD SUIT
    print(">>> Generating Samus Dread Suit (Metroid Dread)...")
    arm = load_base_rig()
    mat_dread_white = create_pbr_material("Mat_DreadWhite", (0.92, 0.94, 0.96, 1.0), metallic=0.75, roughness=0.25)
    mat_dread_cyan = create_pbr_material("Mat_DreadCyan", (0.02, 0.45, 0.72, 1.0), metallic=0.40, roughness=0.35)
    mat_dread_red = create_pbr_material("Mat_DreadRed", (0.85, 0.08, 0.15, 1.0), metallic=0.85, roughness=0.22)
    mat_dread_visor = create_pbr_material("Mat_DreadVisor", (0.0, 1.0, 0.95, 1.0), metallic=0.1, roughness=0.1, emissive_color=(0.0, 1.0, 0.95, 1.0), emissive_strength=4.0)

    # Re-use mesh structure with Dread styling
    create_varia_suit_meshes(arm)
    # Apply Dread color theme to objects
    for o in arm.children:
        if "Helmet" in o.name:
            o.data.materials[0] = mat_dread_red
        elif "Visor" in o.name or "Ring" in o.name:
            o.data.materials[0] = mat_dread_visor
        elif "Chest" in o.name or "Pauldron" in o.name:
            o.data.materials[0] = mat_dread_white
        elif "Thigh" in o.name or "Abdomen" in o.name:
            o.data.materials[0] = mat_dread_cyan

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "samus_dread_suit.glb")
    # Clean up stray meshes
    for o in list(bpy.data.objects):
        if "Icosphere" in o.name or o.name.startswith("Cube.") or o.name.startswith("Cylinder."):
            if o.parent != arm:
                bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

    # 4. GRAVITY SUIT
    print(">>> Generating Samus Gravity Suit...")
    arm = load_base_rig()
    mat_grav_purple = create_pbr_material("Mat_GravPurple", (0.35, 0.10, 0.60, 1.0), metallic=0.85, roughness=0.25)
    mat_grav_magenta = create_pbr_material("Mat_GravMagenta", (0.60, 0.12, 0.55, 1.0), metallic=0.80, roughness=0.28)
    mat_grav_visor = create_pbr_material("Mat_GravVisor", (0.0, 1.0, 0.5, 1.0), metallic=0.1, roughness=0.1, emissive_color=(0.0, 1.0, 0.5, 1.0), emissive_strength=3.5)
    create_varia_suit_meshes(arm)
    for o in arm.children:
        if "Chest" in o.name or "Pauldron" in o.name or "Greave" in o.name:
            o.data.materials[0] = mat_grav_purple
        elif "Helmet" in o.name or "Thigh" in o.name:
            o.data.materials[0] = mat_grav_magenta
        elif "Visor" in o.name:
            o.data.materials[0] = mat_grav_visor

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "samus_gravity_suit.glb")
    # Clean up stray meshes
    for o in list(bpy.data.objects):
        if "Icosphere" in o.name or o.name.startswith("Cube.") or o.name.startswith("Cylinder."):
            if o.parent != arm:
                bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

    # 5. PHAZON SUIT
    print(">>> Generating Samus Phazon Suit...")
    arm = load_base_rig()
    mat_phazon_black = create_pbr_material("Mat_PhazonBlack", (0.08, 0.09, 0.11, 1.0), metallic=0.90, roughness=0.25)
    mat_phazon_silver = create_pbr_material("Mat_PhazonSilver", (0.65, 0.68, 0.72, 1.0), metallic=0.95, roughness=0.15)
    mat_phazon_red = create_pbr_material("Mat_PhazonRed", (1.0, 0.05, 0.1, 1.0), metallic=0.1, roughness=0.1, emissive_color=(1.0, 0.05, 0.1, 1.0), emissive_strength=4.5)
    create_varia_suit_meshes(arm)
    for o in arm.children:
        if "Chest" in o.name or "Pauldron" in o.name or "ArmCannon" in o.name or "Greave" in o.name:
            o.data.materials[0] = mat_phazon_black
        elif "Helmet" in o.name or "Thigh" in o.name or "Boot" in o.name:
            o.data.materials[0] = mat_phazon_silver
        elif "Visor" in o.name or "Ring" in o.name:
            o.data.materials[0] = mat_phazon_red

    attach_combat_actions(arm)
    out_path = os.path.join(OUTPUT_DIR, "samus_phazon_suit.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', export_yup=True, export_animations=True)
    print(f"Exported: {out_path} ({os.path.getsize(out_path)} bytes)")

    print("\n>>> ALL 5 SAMUS ARAN SUITS GENERATED AND EXPORTED SUCCESSFULLY! <<<")

if __name__ == '__main__':
    build_and_export_suits()
