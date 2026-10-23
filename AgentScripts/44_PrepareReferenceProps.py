import bpy,pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1];out=ROOT/'ArtSource/Prepared/district/cc0';out.mkdir(parents=True,exist_ok=True)
manifest=[]
for name in ['street_lamp_01','painted_wooden_sofa']:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'ArtSource/Models/reference_cc0'/name/'model.gltf'))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:o.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    if len(meshes)>1:bpy.ops.object.join()
    o=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    points=[v.co.copy() for v in o.data.vertices];cx=(min(p.x for p in points)+max(p.x for p in points))/2;cy=(min(p.y for p in points)+max(p.y for p in points))/2;z=min(p.z for p in points)
    for v in o.data.vertices:v.co.x-=cx;v.co.y-=cy;v.co.z-=z
    asset='SM_PH_'+name
    bpy.ops.export_scene.fbx(filepath=str(out/(asset+'.fbx')),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,object_types={'MESH'},path_mode='ABSOLUTE')
    manifest.append({'id':name,'asset':asset,'dimensions_m':list(o.dimensions),'slots':[s.name for s in o.data.materials]})
print(json.dumps(manifest),flush=True)
(out/'manifest.json').write_text(json.dumps(manifest,indent=2))
