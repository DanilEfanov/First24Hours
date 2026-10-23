import bpy,pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'ArtSource/Models/district_tree_small_02/tree.gltf'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
print('TREE_IMPORT',[(o.name,len(o.data.polygons),list(o.dimensions)) for o in meshes],flush=True)
# Use supplied lowest-detail mesh where separate LOD objects exist.
lods=[o for o in meshes if 'LOD' in o.name.upper()]
if lods:
    selected=min(lods,key=lambda o:len(o.data.polygons))
    for o in meshes:
        if o!=selected:bpy.data.objects.remove(o,do_unlink=True)
    meshes=[selected]
# Keep the authored leaf silhouette. UE Nanite handles this dense source mesh.
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
if len(meshes)>1:bpy.ops.object.join()
o=bpy.context.object;o.name='SM_District_TreeSmall02'
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
# Lowest point is the planting pivot; metres in Blender become centimetres in UE.
zs=[(o.matrix_world@v.co).z for v in o.data.vertices]
min_z=min(zs)
for v in o.data.vertices:v.co.z-=min_z
out=ROOT/'ArtSource/Prepared/district';out.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.fbx(filepath=str(out/'SM_District_TreeSmall02.fbx'),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,object_types={'MESH'},path_mode='ABSOLUTE')
print('DISTRICT_TREE_FBX_READY',len(o.data.polygons),list(o.dimensions),flush=True)
