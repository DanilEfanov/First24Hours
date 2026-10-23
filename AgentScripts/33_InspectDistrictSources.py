import bpy,pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
source=ROOT/'ArtSource/Prepared/district/source'
for name in ['House','Cars']:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(source/(name+'.fbx')))
    rows=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        rows.append({'name':o.name,'dims':list(o.dimensions),'location':list(o.location),'faces':len(o.data.polygons),'materials':[m.name for m in o.data.materials]})
    print(name,json.dumps(rows),flush=True)
