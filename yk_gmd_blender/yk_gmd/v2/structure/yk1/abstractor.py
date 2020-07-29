from yk_gmd_blender.yk_gmd.v2.abstract.gmd_node import GMDNode
from yk_gmd_blender.yk_gmd.v2.abstract.gmd_scene import GMDScene, HierarchyData
from yk_gmd_blender.yk_gmd.v2.structure.common.abstractor import build_vertex_buffers_from_structs, \
    build_shaders_from_structs, build_materials_from_structs, build_index_mapping, \
    build_meshes_from_structs, build_object_nodes, build_skeleton_bones_from_structs
from yk_gmd_blender.yk_gmd.v2.structure.version import VersionProperties
from yk_gmd_blender.yk_gmd.v2.structure.yk1.file import FileData_YK1


def read_abstract_contents_YK1(version_properties: VersionProperties, file_data: FileData_YK1) -> GMDScene:
    abstract_vertex_buffers = build_vertex_buffers_from_structs(version_properties,
                                                                file_data.vertex_buffer_arr, file_data.vertex_data)
    abstract_shaders = build_shaders_from_structs(version_properties,

                                                  abstract_vertex_buffers,

                                                  file_data.mesh_arr, file_data.attribute_arr,
                                                  file_data.shader_arr)
    abstract_attributes = build_materials_from_structs(version_properties,

                                                      abstract_shaders,

                                                      file_data.attribute_arr, file_data.material_arr,
                                                      file_data.unk12, file_data.unk14,
                                                      file_data.texture_arr)
    abstract_skeleton_bones, remaining_nodes = build_skeleton_bones_from_structs(version_properties,

                                                                                 file_data.node_arr,
                                                                                 file_data.node_name_arr,
                                                                                 file_data.matrix_arr)
    abstract_meshes = build_meshes_from_structs(version_properties,

                                                abstract_attributes, abstract_vertex_buffers, abstract_skeleton_bones,

                                                file_data.mesh_arr, file_data.index_data)

    skinned_abstract_objects, unskinned_abstract_objects = build_object_nodes(version_properties,

                                                                              abstract_meshes,

                                                                              remaining_nodes, file_data.matrix_arr,
                                                                              file_data.mesh_matrix_bytestrings)


    abstract_bones_roots = [b for b in abstract_skeleton_bones if not b.parent]
    skinned_roots = [s for s in skinned_abstract_objects if not s.parent]
    unskinned_roots = [s for s in unskinned_abstract_objects if not s.parent]

    overall_roots = abstract_bones_roots + skinned_roots + unskinned_roots

    return GMDScene(
        name=file_data.name.text,

        overall_heirarchy=HierarchyData[GMDNode](overall_roots),

        skeleton=HierarchyData(abstract_bones_roots) if abstract_bones_roots else None,
        skinned_objects=HierarchyData(skinned_roots) if skinned_roots else None,
        unskinned_objects=HierarchyData(unskinned_roots) if unskinned_roots else None,
    )