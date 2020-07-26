import math
from typing import Tuple, Collection, Iterable

from mathutils import Vector
from yk_gmd_blender.yk_gmd.abstract.material import GMDMaterial
from yk_gmd_blender.yk_gmd.abstract.vector import Vec3, Vec4
from yk_gmd_blender.yk_gmd.file import GMDFileIOAbstraction


def yk_to_blender_space(vec: Vec3):
    return (vec.x, vec.z, vec.y)


def blender_to_yk_space(vec: Vector):
    return Vec3(vec[0], vec[2], vec[1])

def blender_to_yk_space_vec4(vec: Vector, w: float):
    return Vec4(vec[0], vec[2], vec[1], w)

def blender_to_yk_color(vec: Vector):
    return Vec4(vec[0], vec[1], vec[2], vec[3])

def uv_yk_to_blender_space(uv: Tuple[float, float]):
    return (uv[0], 1 - uv[1])

def uv_make_01(x):
    # Could be done with math.fmod(x, 1.0) but IDK if that would work right with negative numbers
    while x < 0.0:
        x += 1.0
    while x > 1.0:
        x -= 1.0
    return x

def uv_blender_to_yk_space(uv: Tuple[float, float]):
    return (uv_make_01(uv[0]), uv_make_01(1 - uv[1]))

def root_name_for_gmd_file(gmd_file: GMDFileIOAbstraction):
    return f"{gmd_file.name}"

def armature_name_for_gmd_file(gmd_file: GMDFileIOAbstraction):
    return f"{gmd_file.name}_armature"

def material_name(material: GMDMaterial):
    return f"yakuza{material.id:02d}_{material.shader_name}"

def arithmetic_mean(items: Iterable, sum_start=0):
    count = 0
    s = sum_start
    for i in items:
        s += i
        count += 1
    return s / count