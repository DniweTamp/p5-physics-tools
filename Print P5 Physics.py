import bpy
import yaml
from mathutils import Vector

def calculate_distance(armature_name, bone1_name, bone2_name):
    armature = bpy.data.objects[armature_name]
    mode = armature.mode

    # Switch to pose mode if not already in pose mode
    if mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    bone1_head = armature.pose.bones[bone1_name].head
    bone2_head = armature.pose.bones[bone2_name].head

    # Convert to world coordinates
    bone1_head_world = armature.matrix_world @ bone1_head
    bone2_head_world = armature.matrix_world @ bone2_head

    # Calculate the distance
    distance = (bone1_head_world - bone2_head_world).length

    distance_sqr = distance * distance

    # Switch back to the original mode
    bpy.ops.object.mode_set(mode=mode)

    return distance_sqr

def get_bone_info(bone, selected_bones):
    if bone.parent not in selected_bones:
        # This bone is the first in its chain
        return {
            'Field3C': 1,
            'Field40': 0,
            'Field38': 0,
            'Field34': 1,
            'NodeName': bone.name,
            'Field10': 0,
            'Field08': 0,
            'Field04': 0
        }
    else:
        # The rest of the chain
        return {
            'Field3C': 0.0, # repelling
            'Field40': 5.0, # wind
            'Field38': 0.15, #mass
            'Field34': 1, # radius
            'NodeName': bone.name,
            'Field10': 0,
            'Field08': 0,
            'Field04': 0
        }

def get_bone_relations(armature, selected_bones):
    relations = []
    for i, bone in enumerate(selected_bones):
        for child in bone.children:
            if child in selected_bones:
                child_index = selected_bones.index(child)
                print(calculate_distance(obj.name, selected_bones[i].name, selected_bones[child_index].name))
                relations.append({
                    'Field00': calculate_distance(obj.name, selected_bones[i].name, selected_bones[child_index].name), # length
                    'Field04': 0.0, # angular limit
                    'Field08': 1, # chain thiccness
                    'Field0C': i,
                    'Field0E': child_index
                })
    return relations

# Get the active object
obj = bpy.context.active_object

# Check if the active object is an armature
if obj.type == 'ARMATURE':
    armature = obj.data

    # Get the selected bones
    selected_bones = [bone for bone in armature.bones if bone.select]

    # Get the bone info
    bone_info = [get_bone_info(bone, selected_bones) for bone in selected_bones]

    # Get the bone relations
    bone_relations = get_bone_relations(armature, selected_bones)

    # Write the bone info to a YAML file
    with open('C:/Users/egorb/stuff/bone_info.yml', 'w') as file:
        yaml.dump(bone_info, file)

    # Write the bone relations to a YAML file
    with open('C:/Users/egorb/stuff/bone_relations.yml', 'w') as file:
        yaml.dump(bone_relations, file)
else:
    print("The active object is not an armature.")
