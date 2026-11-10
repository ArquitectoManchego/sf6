import bpy
from mathutils import Vector, Quaternion, Matrix, Euler

bpy.ops.wm.read_factory_settings(use_empty=True)
arm_data = bpy.data.armatures.new("TestArm")
arm_obj = bpy.data.objects.new("TestArmObj", arm_data)
bpy.context.scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

b_root = arm_data.edit_bones.new("Root")
b_root.head = (0, 0, 0)
b_root.tail = (0, 0, 1)

b_child = arm_data.edit_bones.new("Child")
b_child.head = (0, 0, 1)
b_child.tail = (1, 0, 1)
b_child.parent = b_root

bpy.ops.object.mode_set(mode='POSE')

pb_root = arm_obj.pose.bones["Root"]
pb_child = arm_obj.pose.bones["Child"]

# Set random rotations
rot_root = Euler((0.3, 0.5, 0.2)).to_quaternion()
rot_child = Euler((0.1, -0.4, 0.6)).to_quaternion()

pb_root.rotation_quaternion = rot_root
pb_child.rotation_quaternion = rot_child
bpy.context.view_layer.update()

# Let's inspect formulas
# In rest pose:
# rest_local = parent.bone.matrix_local.inverted() @ child.bone.matrix_local
rest_local = pb_child.bone.matrix_local if not pb_child.parent else pb_child.parent.bone.matrix_local.inverted() @ pb_child.bone.matrix_local

# Formula 1: pb_child.matrix = pb_child.parent.matrix @ rest_local @ rot_child.to_matrix().to_4x4()
test_m1 = pb_child.parent.matrix @ rest_local @ rot_child.to_matrix().to_4x4()

# Formula 2: pb_child.matrix = pb_child.parent.matrix @ rot_child.to_matrix().to_4x4() @ rest_local
test_m2 = pb_child.parent.matrix @ rot_child.to_matrix().to_4x4() @ rest_local

print("Actual child matrix:\n", pb_child.matrix)
print("Formula 1 diff:\n", (pb_child.matrix - test_m1))
print("Formula 2 diff:\n", (pb_child.matrix - test_m2))

# How to solve for rot_child given desired child matrix M_child_desired and evaluated parent matrix M_parent:
# M_child_desired = M_parent @ rest_local @ rot_child.to_matrix().to_4x4()
# => (rest_local.inverted() @ M_parent.inverted() @ M_child_desired) = rot_child.to_matrix().to_4x4()
rot_solved = (rest_local.inverted() @ pb_child.parent.matrix.inverted() @ pb_child.matrix).to_quaternion()
print("Original rot_child:", rot_child)
print("Solved rot_child:", rot_solved)
