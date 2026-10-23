import bpy,pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1];out=ROOT/'ArtSource/Prepared/district/cc0';manifest=[]
for name in ['shrub_01','grass_medium_01']:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'ArtSource/Models/reference_cc0'/name/'model.gltf'))
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    print('FOLIAGE_SOURCE',name,[(o.name,len(o.data.polygons),[round(v,2) for v in o.dimensions]) for o in objects],flush=True)
    # One authored clump only, rather than importing the source presentation grid.
    o=max(objects,key=lambda o:len(o.data.polygons))
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    o.location=(0,0,0);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    pts=[v.co.copy() for v in o.data.vertices];cx=(min(p.x for p in pts)+max(p.x for p in pts))/2;cy=(min(p.y for p in pts)+max(p.y for p in pts))/2;z=min(p.z for p in pts)
    for v in o.data.vertices:v.co.x-=cx;v.co.y-=cy;v.co.z-=z
    asset='SM_PH_'+name
    bpy.ops.export_scene.fbx(filepath=str(out/(asset+'.fbx')),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,object_types={'MESH'},path_mode='ABSOLUTE')
    manifest.append({'id':name,'asset':asset,'dimensions_m':list(o.dimensions),'polygons':len(o.data.polygons),'slots':[m.name for m in o.data.materials]})
(out/'foliage-manifest.json').write_text(json.dumps(manifest,indent=2));print('FOLIAGE_READY',manifest,flush=True)
