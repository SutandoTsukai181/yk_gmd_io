from dataclasses import dataclassfrom enum import Enumfrom typing import Optional, Tuple, List, Sizedfrom mathutils import Vectorfrom yk_gmd_blender.structurelib.base import StructureUnpacker, BasePrimitive, FixedSizeArrayUnpacker, ValueAdaptor, \    BaseUnpackerfrom yk_gmd_blender.structurelib.primitives import c_float32, c_float16, c_unorm8, c_uint8, RangeConverterPrimitivefrom yk_gmd_blender.yk_gmd.v2.structure.common.vector import Vec3Unpacker, Vec4Unpacker, Vec3Unpacker_of, \    Vec4Unpacker_of# TODO: Rename to HLSL-style (ubyte4, float2, float3, float4, half2 etc.)class VecStorage(Enum):    Vec4Fixed = 1    Vec2Full = 2    Vec3Full = 3    Vec4Full = 4    Vec2Half = 5    Vec3Half = 6    Vec4Half = 7class FixedConvertMethod(Enum):    To0_1 = 0    ToMinus1_1 = 1    ToByte = 2def list2_to_tuple2(list2: List):    return (list2[0], list2[1])def make_vector_unpacker(vec_type: VecStorage, byte_convert: Optional[FixedConvertMethod] = None) -> BaseUnpacker:    if vec_type == VecStorage.Vec2Full:        return ValueAdaptor(tuple, base_unpacker=FixedSizeArrayUnpacker(c_float32, 2), forwards=tuple, backwards=list)    elif vec_type == VecStorage.Vec3Full:        return Vec3Unpacker_of(c_float32)    elif vec_type == VecStorage.Vec4Full:        return Vec4Unpacker_of(c_float32)    elif vec_type == VecStorage.Vec2Half:        return ValueAdaptor(tuple, base_unpacker=FixedSizeArrayUnpacker(c_float16, 2), forwards=tuple, backwards=list)    elif vec_type == VecStorage.Vec3Half:        return Vec3Unpacker_of(c_float16)    elif vec_type == VecStorage.Vec4Half:        return Vec4Unpacker_of(c_float16)    elif vec_type == VecStorage.Vec4Fixed:        if not byte_convert:            print(f"Field had vec_type = Vec4Fixed but gave no byte_convert, assuming ToByte")            byte_convert = FixedConvertMethod.ToByte        if byte_convert == FixedConvertMethod.To0_1:            return Vec4Unpacker_of(c_unorm8)        elif byte_convert == FixedConvertMethod.ToMinus1_1:            return Vec4Unpacker_of(RangeConverterPrimitive(base_unpack=c_uint8, from_range=(0, 255), to_range=(-1.0, 1.0)))        elif byte_convert == FixedConvertMethod.ToByte:            return Vec4Unpacker_of(c_uint8)    raise TypeError(f"Couldn't generate vector unpacker for {vec_type}/{byte_convert}")@dataclassclass BoneWeight:    bone: int    weight: floatBoneWeight4 = Tuple[BoneWeight, BoneWeight, BoneWeight, BoneWeight]@dataclass(repr=False)class GMDVertexBuffer(Sized):    layout: 'GMDVertexBufferLayout'    pos: List[Vector]    bone_weights: Optional[List[BoneWeight4]]    normal: Optional[List[Vector]]    tangent: Optional[List[Vector]]    unk: Optional[List[Vector]]    col0: Optional[List[Vector]]    col1: Optional[List[Vector]]    uvs: List[List[Vector]]    @staticmethod    def build_empty(layout: 'GMDVertexBufferLayout', count: int):        alloc_for_type = lambda field_type: [None] * count if field_type else None        return GMDVertexBuffer(            layout=layout,            # TODO: How to deal with "incomplete" vertex buffers?            pos = [None] * count,            bone_weights = alloc_for_type(layout.weights_unpacker),            normal = alloc_for_type(layout.normal_unpacker),            tangent = alloc_for_type(layout.tangent_unpacker),            unk = alloc_for_type(layout.unk_unpacker),            col0 = alloc_for_type(layout.col0_unpacker),            col1 = alloc_for_type(layout.col1_unpacker),            uvs = [                [None] * count                for t in layout.uv_unpackers            ],        )    def vertex_count(self):        return len(self.pos)    def __len__(self):        return self.vertex_count()    def __getitem__(self, item) -> 'GMDVertexBuffer':        if not isinstance(item, slice):            raise IndexError(f"GMDVertexBuffer __getitem__ got {item} but expected slice")        return GMDVertexBuffer(            layout=self.layout,            pos=self.pos[item],            bone_weights=self.bone_weights[item] if self.bone_weights else None,            normal=self.normal[item] if self.normal else None,            tangent=self.tangent[item] if self.tangent else None,            unk=self.unk[item] if self.unk else None,            col0=self.col0[item] if self.col0 else None,            col1=self.col1[item] if self.col1 else None,            uvs=[                uv[item]                for uv in self.uvs            ],        )# VertexBufferLayouts are external dependencies (shaders have a fixed layout, which we can't control) so they are frozen@dataclass(frozen=True, init=True)class GMDVertexBufferLayout:    # TODO: weights_type can unpack to Vector, but bones_type maybe shouldn't    pos_unpacker: BaseUnpacker[Vector]    weights_unpacker: Optional[BaseUnpacker[Vector]]    bones_unpacker: Optional[BaseUnpacker[Vector]]    normal_unpacker: Optional[BaseUnpacker[Vector]]    tangent_unpacker: Optional[BaseUnpacker[Vector]]    unk_unpacker: Optional[BaseUnpacker[Vector]]    col0_unpacker: Optional[BaseUnpacker[Vector]]    col1_unpacker: Optional[BaseUnpacker[Vector]]    uv_unpackers: Tuple[BaseUnpacker[Vector], ...]    pos_storage: VecStorage    weights_storage: Optional[VecStorage]    bones_storage: Optional[VecStorage]    normal_storage: Optional[VecStorage]    tangent_storage: Optional[VecStorage]    unk_storage: Optional[VecStorage]    col0_storage: Optional[VecStorage]    col1_storage: Optional[VecStorage]    uv_storages: Tuple[VecStorage, ...]    def __post_init__(self):        if not self.pos_unpacker:            raise TypeError(f"VertexBufferLayout claims to not have vertex positions!")        if bool(self.weights_unpacker) != bool(self.bones_unpacker):            raise TypeError(f"VertexBufferLayout has weights/bones mismatch: weights {bool(self.weights_unpacker)} bones {bool(self.bones_unpacker)}")    @staticmethod    def make_vertex_buffer_layout(                                 pos_storage: VecStorage,                                 weights_storage: Optional[VecStorage],                                 bones_storage: Optional[VecStorage],                                 normal_storage: Optional[VecStorage],                                 tangent_storage: Optional[VecStorage],                                 unk_storage: Optional[VecStorage],                                 col0_storage: Optional[VecStorage],                                 col1_storage: Optional[VecStorage],                                 uv_storages: List[VecStorage],                                 ):        return GMDVertexBufferLayout(            pos_unpacker=make_vector_unpacker(pos_storage),            weights_unpacker=make_vector_unpacker(weights_storage, FixedConvertMethod.To0_1) if weights_storage else None,            bones_unpacker=make_vector_unpacker(bones_storage, FixedConvertMethod.ToByte) if bones_storage else None,            normal_unpacker=make_vector_unpacker(normal_storage, FixedConvertMethod.ToMinus1_1) if normal_storage else None,            tangent_unpacker=make_vector_unpacker(tangent_storage, FixedConvertMethod.ToMinus1_1) if tangent_storage else None,            unk_unpacker=make_vector_unpacker(unk_storage) if unk_storage else None,            col0_unpacker=make_vector_unpacker(col0_storage, FixedConvertMethod.To0_1) if col0_storage else None,            col1_unpacker=make_vector_unpacker(col1_storage, FixedConvertMethod.To0_1) if col1_storage else None,            uv_unpackers=tuple([make_vector_unpacker(s, FixedConvertMethod.ToMinus1_1) for s in uv_storages]),            pos_storage=pos_storage,            weights_storage=weights_storage,            bones_storage=bones_storage,            normal_storage=normal_storage,            tangent_storage=tangent_storage,            unk_storage=unk_storage,            col0_storage=col0_storage,            col1_storage=col1_storage,            uv_storages=tuple(uv_storages),        )    def bytes_per_vertex(self) -> int:        size = 0        size += self.pos_unpacker.sizeof()        if self.weights_unpacker:            size += self.weights_unpacker.sizeof()            size += self.bones_unpacker.sizeof()        if self.normal_unpacker:            size += self.normal_unpacker.sizeof()        if self.tangent_unpacker:            size += self.tangent_unpacker.sizeof()        if self.unk_unpacker:            size += self.unk_unpacker.sizeof()        if self.col0_unpacker:            size += self.col0_unpacker.sizeof()        if self.col1_unpacker:            size += self.col1_unpacker.sizeof()        for uv_unpacker in self.uv_unpackers:            size += uv_unpacker.sizeof()        return size    def unpack_from(self, big_endian: bool, vertex_count: int, data: bytes, offset: int) -> Tuple[GMDVertexBuffer, int]:        vertices: GMDVertexBuffer = GMDVertexBuffer.build_empty(self, vertex_count)        for i in range(vertex_count):            # unpack() returns the unpacked value and offset + size, so incrementing offset is done in one line            vertices.pos[i], offset = self.pos_unpacker.unpack(big_endian, data, offset)            if self.weights_unpacker:                weights, offset = self.weights_unpacker.unpack(big_endian, data, offset)                bones, offset = self.bones_unpacker.unpack(big_endian, data, offset)                vertices.bone_weights[i] = (                    BoneWeight(bone=int(bones[0]), weight=weights[0]),                    BoneWeight(bone=int(bones[1]), weight=weights[1]),                    BoneWeight(bone=int(bones[2]), weight=weights[2]),                    BoneWeight(bone=int(bones[3]), weight=weights[3]),                )            if self.normal_unpacker:                vertices.normal[i], offset = self.normal_unpacker.unpack(big_endian, data, offset)            if self.tangent_unpacker:                vertices.tangent[i], offset = self.tangent_unpacker.unpack(big_endian, data, offset)            if self.unk_unpacker:                vertices.unk[i], offset = self.unk_unpacker.unpack(big_endian, data, offset)            if self.col0_unpacker:                vertices.col0[i], offset = self.col0_unpacker.unpack(big_endian, data, offset)            if self.col1_unpacker:                vertices.col1[i], offset = self.col1_unpacker.unpack(big_endian, data, offset)            for uv_idx, uv_unpacker in enumerate(self.uv_unpackers):                vertices.uvs[uv_idx][i], offset = uv_unpacker.unpack(big_endian, data, offset)        return vertices, offset    # def check_verts(self, vertices: List[GMDVertex]):    #     for vertex in vertices:    #         if not all(vertex.pos, vertex.bone_weights):    def pack_into(self, big_endian: bool, vertices: GMDVertexBuffer, append_to: bytearray):        # TODO: Validate that all ranges exist for what we want        # TODO: Fill in default data if stuff is missing?        for i in range(vertices.vertex_count()):            self.pos_unpacker.pack(big_endian, vertices.pos[i], append_to=append_to)            if self.weights_unpacker:                # The actual packers want Vectors, not lists, but they work with lists                self.weights_unpacker.pack(big_endian, [b.weight for b in vertices.bone_weights[i]], append_to=append_to)                self.bones_unpacker.pack(big_endian, [b.bone for b in vertices.bone_weights[i]], append_to=append_to)            if self.normal_unpacker:                self.normal_unpacker.pack(big_endian, vertices.normal[i], append_to=append_to)            if self.tangent_unpacker:                self.tangent_unpacker.pack(big_endian, vertices.tangent[i], append_to=append_to)            if self.unk_unpacker:                self.unk_unpacker.pack(big_endian, vertices.unk[i], append_to=append_to)            if self.col0_unpacker:                self.col0_unpacker.pack(big_endian, vertices.col0[i], append_to=append_to)            if self.col1_unpacker:                self.col1_unpacker.pack(big_endian, vertices.col1[i], append_to=append_to)            for uv_data, uv_packer in zip(vertices.uvs, self.uv_unpackers):                uv_packer.pack(big_endian, uv_data[i], append_to=append_to)# Shaders are external dependencies, so they are frozen. You can't change the name of a shader, for example.@dataclass(frozen=True)class GMDShader:    name: str    vertex_buffer_layout: GMDVertexBufferLayout