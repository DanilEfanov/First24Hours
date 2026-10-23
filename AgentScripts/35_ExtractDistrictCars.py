import bpy,bmesh,pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'ArtSource/Prepared/district/kit'
manifest=json.loads((OUT/'kit-manifest.json').read_text())
manifest['assets']=[a for a in manifest['assets'] if not a['name'].startswith('SM_District_Car_')]
for idx,center_y in enumerate([-6,-3,0,3,6]):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'ArtSource/Prepared/district/source/Cars.fbx'))
    for o in list(bpy.context.scene.objects):
        if o.type=='MESH' and o.name.startswith('UCX_'):bpy.data.objects.remove(o,do_unlink=True)
    o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if abs(v.co.y-center_y)>1.45],context='VERTS')
    bm.to_mesh(o.data);bm.free();o.data.update()
    if not o.data.polygons:continue
    mins=[min(v.co[k] for v in o.data.vertices) for k in range(3)];maxs=[max(v.co[k] for v in o.data.vertices) for k in range(3)]
    for v in o.data.vertices:
        v.co.x-=(mins[0]+maxs[0])*.5;v.co.y-=(mins[1]+maxs[1])*.5;v.co.z-=mins[2]
    name='SM_District_Car_%02d'%idx;o.name=name
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',object_types={'MESH'},bake_anim=False)
    manifest['assets'].append({'name':name,'source':'Cars','materials':[m.name for m in o.data.materials],'dimensions_m':[maxs[k]-mins[k] for k in range(3)]})
    print(name,manifest['assets'][-1]['dimensions_m'],flush=True)
(OUT/'kit-manifest.json').write_text(json.dumps(manifest,indent=2))
