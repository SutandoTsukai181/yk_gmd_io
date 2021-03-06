import argparse
import math
import random
from pathlib import Path

from yk_gmd_blender.yk_gmd.abstract.submesh import GMDSubmesh
from yk_gmd_blender.yk_gmd.abstract.vector import Quat, Vec3, Mat4
from yk_gmd_blender.yk_gmd.file import GMDFile, GMDFileIOAbstraction, GMDArray


def quaternion_to_euler_angle(q: Quat):
    ysqr = q.y * q.y

    t0 = +2.0 * (q.w * q.x + q.y * q.z)
    t1 = +1.0 - 2.0 * (q.x * q.x + ysqr)
    X = math.degrees(math.atan2(t0, t1))

    t2 = +2.0 * (q.w * q.y - q.z * q.x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    Y = math.degrees(math.asin(t2))

    t3 = +2.0 * (q.w * q.z + q.x * q.y)
    t4 = +1.0 - 2.0 * (ysqr + q.z * q.z)
    Z = math.degrees(math.atan2(t3, t4))

    return X, Y, Z

def csv_str(iter):
    return ", ".join(str(x) for x in iter)

def print_each(iter):
    for x in iter:
        print(x)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("GMD Poker")

    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--output_dir", type=Path)
    parser.add_argument("file_to_poke", type=Path)

    args = parser.parse_args()

    #if os.path.isdir(args.output_dir):
    #    shutil.rmtree(args.output_dir)
    #shutil.copytree(args.input_dir, args.output_dir)

    with open(args.input_dir / args.file_to_poke, "rb") as in_file:
        data = in_file.read()
    original_gmd_file = GMDFile(data)

    gmd_file = GMDFileIOAbstraction(GMDFile(data).structs)

    #mat_floats_val = 10000.0
    #for material in gmd_file.structs.materials:
    #    material.texture_diffuse = PaddedTextureIndexStruct(16)
    #    material.floats[0:16] = [mat_floats_val] * 16
    #    pass

    #for unk in gmd_file.structs.unk12:
    #    unk.data_hidden[0:32] = [mat_floats_val] * 32

    # for submesh in gmd_file.submeshes:
    #     #submesh.linked_l0_number_maybe = 0
    #     #submesh.linked_l0_bone_maybe = 0
    #     #submesh.unk1 = 0
    #     #submesh.unk2 = 216
    #     #print(f"submesh unk2 = {submesh.unk2}, points to byte {gmd_file.structs.unk11[submesh.unk2].data}")
    #     #gmd_file.structs.unk11[submesh.unk2].data = 0
    #     #submesh.unk1 = 0
    #
    #     #submesh.unk1 = 121
    #     #submesh.unk2 = 0
    #     if len(submesh.vertices) == 26:
    #         mid = Vec3(0, 1.755, 0.065)
    #         print(Mat4.rotation(Quat(0, 0, 1, 0)))
    #         # s = sin(2*angle)
    #         # c = cos(2*angle)
    #         # q = (axis.x*s, axis.y*s, axis.z*s, c) for axis,angle
    #         mat = Mat4.translation(mid) * Mat4.rotation(Quat(0, 0, 1, 0)) * Mat4.translation(-mid)
    #         for v in submesh.vertices:
    #             #print(v.pos)
    #             print(v.pos)
    #             v.pos = (mat * v.pos).xyz
    #             print(f"{v.pos}\n")
    #             #v.pos.z += 0.1
    #
    #             #v.pos.z += 0.1
    #             #v.pos.y += 0.1
    #             #v.pos.x = -v.pos.x
    #             #v.normal.x = 1-v.normal.x
    #             #v.normal.y = -v.normal.y
    #             #v.normal.z = -v.normal.z
    #     pass

    new_submeshes = gmd_file.submeshes

    # Swap submeshes around
    #temp = new_submeshes[5]
    #new_submeshes[5] = new_submeshes[24]
    #new_submeshes[24] = temp
    #random.shuffle(new_submeshes)

    # for i in range(len(new_submeshes)):
    #     submesh = new_submeshes[i]
    #     new_submeshes[i] = Submesh(
    #         material=submesh.material,
    #         relevant_bones=submesh.relevant_bones,
    #         vertices=submesh.vertices,
    #         triangle_indices=submesh.triangle_indices,
    #         triangle_strip_indices1=submesh.triangle_strip_indices1,
    #         triangle_strip_indices2=submesh.triangle_strip_indices2,
    #     )

    # [:22] works, [:1] doesn't, [:15] works, [:5] doesn't, [:10] does but looks weird
    # NEW: [:5] works if different order of meshes is used?
    gmd_file.submeshes = new_submeshes[:1]
    #gmd_file.structs.parts = GMDArray(gmd_file.structs.parts.items[:10])

    #gmd_file.structs.unk11[0] = bytes(list(range(121)))

    #original_reexported_data = original_gmd_file.structs.make_bytes()
    #original_reexported_file = GMDFile(original_reexported_data)

    #l0_count = 0
    #for name in gmd_file.structs.bone_names.items:
    #    if "[l0]" in name.text:
    #        name.text_internal = f"[l0]{l0_count}".encode("ascii")
    #        l0_count += 1

    new_data = gmd_file.repack_into_bytes()
    new_gmd_file = GMDFile(new_data)

    # find diff between original_reexported and new_data
    #equal_bytes = [new_data[i] == original_reexported_data[i] for i in range(len(new_data))]
    #unequal_ranges = false_ranges_in(equal_bytes)
    #for (ra, rb) in unequal_ranges:
    #    print(f"[0x{ra:06x}...0x{rb:06x})")

    #uncovered = set()
    #for (covered, val) in zip(equal_bytes, new_data, original_reexported_data):
    #    if not covered:
    #        uncovered.add(val)
    #print(f"Values in uncovered areas: {uncovered}")

    if args.output_dir:
        with open(args.output_dir / args.file_to_poke, "wb") as out_file:
            out_file.write(new_data)

