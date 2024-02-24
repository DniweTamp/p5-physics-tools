bl_info = {
    "name": "P5 Physics Maker",
    "author": "DniweTamp",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > P5 Physics",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "category": "3D View",
}

import bpy
import bpy_extras
import yaml
import mathutils

def get_bone_items(self, context):
    items = [(str(i), bone.NodeName, "") for i, bone in enumerate(context.scene.bone_infos)]
    return items

class BoneInfosPropertyGroup(bpy.types.PropertyGroup):
    show_details: bpy.props.BoolProperty(name="Show Details", default=False)
    Field3C: bpy.props.FloatProperty(name="Repelling", min=0.0, max=1.0, default=0.0)
    Field40: bpy.props.FloatProperty(name="Wind", min=0.0, soft_max=1.0, default=5.0)
    Field38: bpy.props.FloatProperty(name="Mass", min=0.0, soft_max=1.0, default=0.15)
    Field34: bpy.props.FloatProperty(name="Radius", min=0.0, soft_max=10, default=1)
    NodeName: bpy.props.StringProperty(name="Node Name")

class BoneRelationsPropertyGroup(bpy.types.PropertyGroup):
    show_details: bpy.props.BoolProperty(name="Show Details", default=False)
    Field00: bpy.props.FloatProperty(name="Length", default=100.0)
    Field04: bpy.props.FloatProperty(name="Angular Limit", min=0.0, max=1.0, default=0.0)
    Field08: bpy.props.FloatProperty(name="Chain Thickness", min=0.0, soft_max=10.0, default=1)
    Field0C: bpy.props.EnumProperty(name="Parent Bone ID", items=get_bone_items)
    Field0E: bpy.props.EnumProperty(name="Child Bone ID", items=get_bone_items)

class AddBoneInfo(bpy.types.Operator):
    bl_idname = "add.bone_info"
    bl_label = "Add Bone Info"

    def execute(self, context):
        bone_info = context.scene.bone_infos.add()
        armature = bpy.context.object
        if armature and armature.type == 'ARMATURE' and armature.mode in {'EDIT', 'POSE'} and bpy.context.selected_bones and len(bpy.context.selected_bones) == 1:
            bone_info.NodeName = bpy.context.active_bone.name
        return {'FINISHED'}

class RemoveBoneInfo(bpy.types.Operator):
    bl_idname = "remove.bone_info"
    bl_label = "Remove Bone Info"
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.bone_infos.remove(self.index)
        return {'FINISHED'}

class AddBoneRelation(bpy.types.Operator):
    bl_idname = "add.bone_relation"
    bl_label = "Add Bone Relation"

    def execute(self, context):
        context.scene.bone_relations.add()
        return {'FINISHED'}

class RemoveBoneRelation(bpy.types.Operator):
    bl_idname = "remove.bone_relation"
    bl_label = "Remove Bone Relation"
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.bone_relations.remove(self.index)
        return {'FINISHED'}

class ImportBoneInfosYAML(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "import.bone_infos_yaml"
    bl_label = "Import Bone Infos YAML"
    filename_ext = ".yml"
    filter_glob: bpy.props.StringProperty(default="*.yml", options={'HIDDEN'})

    def execute(self, context):
        context.scene.bone_infos.clear()
        with open(self.filepath, 'r') as file:
            data = yaml.safe_load(file)
            for item in data:
                bone_info = context.scene.bone_infos.add()
                for key, value in item.items():
                    setattr(bone_info, key, value)
        return {'FINISHED'}

class ExportBoneInfosYAML(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "export.bone_infos_yaml"
    bl_label = "Export Bone Infos YAML"
    filename_ext = ".yml"
    filter_glob: bpy.props.StringProperty(default="*.yml", options={'HIDDEN'})

    def execute(self, context):
        bone_infos = []
        for item in context.scene.bone_infos:
            info_dict = {prop.identifier: getattr(item, prop.identifier) for prop in item.bl_rna.properties if not prop.is_readonly and prop.identifier != 'name' and prop.identifier != 'show_details'}
            # Add the fields that are always 0
            info_dict['Field04'] = 0
            info_dict['Field08'] = 0
            info_dict['Field10'] = 0
            bone_infos.append(info_dict)
        with open(self.filepath, 'w') as file:
            yaml.dump(bone_infos, file)
        return {'FINISHED'}

class ImportBoneRelationsYAML(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "import.bone_relations_yaml"
    bl_label = "Import Bone Relations YAML"
    filename_ext = ".yml"
    filter_glob: bpy.props.StringProperty(default="*.yml", options={'HIDDEN'})

    def execute(self, context):
        context.scene.bone_relations.clear()
        with open(self.filepath, 'r') as file:
            data = yaml.safe_load(file)
            for item in data:
                bone_relation = context.scene.bone_relations.add()
                for key, value in item.items():
                    if key in ['Field0C', 'Field0E']:
                        value = str(value) 
                    setattr(bone_relation, key, value)
        return {'FINISHED'}


class ExportBoneRelationsYAML(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "export.bone_relations_yaml"
    bl_label = "Export Bone Relations YAML"
    filename_ext = ".yml"
    filter_glob: bpy.props.StringProperty(default="*.yml", options={'HIDDEN'})

    def execute(self, context):
        bone_relations = []
        for item in context.scene.bone_relations:
            relation_dict = {prop.identifier: getattr(item, prop.identifier) for prop in item.bl_rna.properties if not prop.is_readonly and prop.identifier != 'name' and prop.identifier != 'show_details'}
            # Convert the identifiers to integers before exporting
            relation_dict['Field0C'] = int(relation_dict['Field0C'])
            relation_dict['Field0E'] = int(relation_dict['Field0E'])
            # Calculate the squared distance between the parent and child bones
            parent_bone = context.scene.bone_infos[int(item.Field0C)]
            child_bone = context.scene.bone_infos[int(item.Field0E)]
            armature = context.object
            parent_pos = armature.matrix_world @ armature.pose.bones[parent_bone.NodeName].matrix.translation
            child_pos = armature.matrix_world @ armature.pose.bones[child_bone.NodeName].matrix.translation
            relation_dict['Field00'] = (parent_pos - child_pos).length_squared
            bone_relations.append(relation_dict)
        with open(self.filepath, 'w') as file:
            yaml.dump(bone_relations, file)
        return {'FINISHED'}

class YAML_PT_Panel(bpy.types.Panel):
    bl_label = "P5 Physics Editor"
    bl_idname = "YAML_PT_Main_Panel"
    bl_category = "P5 Physics"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

class BoneInfo_Panel(bpy.types.Panel):
    bl_label = "Bone Infos"
    bl_idname = "BoneInfoPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YAML_PT_Main_Panel"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Bone Infos")
        box.operator("import.bone_infos_yaml")
        box.operator("export.bone_infos_yaml")
        for i, item in enumerate(context.scene.bone_infos):
            row = box.row()
            row.prop(item, "show_details", icon="TRIA_DOWN" if item.show_details else "TRIA_RIGHT", icon_only=True, emboss=False)
            split_row = row.split(factor=0.08)
            split_row.label(text=str(i))
            split_row.prop_search(item, "NodeName", context.object.data, "bones", text="")
            op = row.operator("remove.bone_info", text="", icon='X')
            op.index = i

            # Create a collapsible panel for each item

            if item.show_details:
                sub_box = box.box()
                sub_box.prop(item, "Field3C", slider=True)
                sub_box.prop(item, "Field40", slider=True)
                sub_box.prop(item, "Field38", slider=True)
                sub_box.prop(item, "Field34", slider=True)
        box.operator("add.bone_info")


class BoneRelations_Panel(bpy.types.Panel):
    bl_label = "Bone Relations"
    bl_idname = "BoneRelationsPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "YAML_PT_Main_Panel"
    #bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Bone Relations")
        box.operator("import.bone_relations_yaml")
        box.operator("export.bone_relations_yaml")
        for i, item in enumerate(context.scene.bone_relations):
            row = box.row()
            row.prop(item, "show_details", icon="TRIA_DOWN" if item.show_details else "TRIA_RIGHT", icon_only=True, emboss=False)
            row.prop(item, "Field0C", text="Parent Bone ID")
            row.prop(item, "Field0E", text="Child Bone ID")
            op = row.operator("remove.bone_relation", text="", icon='X')
            op.index = i
            if item.show_details:
                sub_box = box.box()
                sub_box.prop(item, "Field04", slider=True)
                sub_box.prop(item, "Field08", slider=True)
        box.operator("add.bone_relation")

def register():
    bpy.utils.register_class(BoneInfosPropertyGroup)
    bpy.utils.register_class(BoneRelationsPropertyGroup)
    bpy.utils.register_class(AddBoneInfo)
    bpy.utils.register_class(RemoveBoneInfo)
    bpy.utils.register_class(AddBoneRelation)
    bpy.utils.register_class(RemoveBoneRelation)
    bpy.utils.register_class(ImportBoneInfosYAML)
    bpy.utils.register_class(ExportBoneInfosYAML)
    bpy.utils.register_class(ImportBoneRelationsYAML)
    bpy.utils.register_class(ExportBoneRelationsYAML)
    bpy.utils.register_class(YAML_PT_Panel)
    bpy.types.Scene.bone_infos = bpy.props.CollectionProperty(type=BoneInfosPropertyGroup)
    bpy.types.Scene.bone_relations = bpy.props.CollectionProperty(type=BoneRelationsPropertyGroup)
    bpy.utils.register_class(BoneInfo_Panel)
    bpy.utils.register_class(BoneRelations_Panel)

def unregister():
    bpy.utils.unregister_class(BoneInfosPropertyGroup)
    bpy.utils.unregister_class(BoneRelationsPropertyGroup)
    bpy.utils.unregister_class(AddBoneInfo)
    bpy.utils.unregister_class(RemoveBoneInfo)
    bpy.utils.unregister_class(AddBoneRelation)
    bpy.utils.unregister_class(RemoveBoneRelation)
    bpy.utils.unregister_class(ImportBoneInfosYAML)
    bpy.utils.unregister_class(ExportBoneInfosYAML)
    bpy.utils.unregister_class(ImportBoneRelationsYAML)
    bpy.utils.unregister_class(ExportBoneRelationsYAML)
    bpy.utils.unregister_class(YAML_PT_Panel)
    del bpy.types.Scene.bone_infos
    del bpy.types.Scene.bone_relations
    bpy.utils.unregister_class(BoneInfo_Panel)
    bpy.utils.unregister_class(BoneRelations_Panel)

if __name__ == "__main__":
    register()
