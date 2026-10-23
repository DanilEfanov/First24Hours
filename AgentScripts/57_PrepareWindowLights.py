import bpy,pathlib,json,random
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1];out=ROOT/'ArtSource/Prepared/district/cc0'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'ArtSource/Prepared/district/source/House.fbx'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];o=max(objects,key=lambda o:len(o.data.polygons));bpy.context.view_layer.objects.active=o
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
glass=[i for i,s in enumerate(o.data.materials) if s and s.name.lower().split('.')[0]=='glass'];faces=[p for p in o.data.polygons if p.material_index in glass]
# Shared vertices connect the triangles of each original window pane.
vertex_faces={}
for p in faces:
    for v in p.vertices:vertex_faces.setdefault(v,[]).append(p.index)
face_map={p.index:p for p in faces};pending=set(face_map);islands=[]
while pending:
    start=pending.pop();stack=[start];group=[]
    while stack:
        f=stack.pop();p=face_map[f];group.append(p)
        for v in p.vertices:
            for neighbor in vertex_faces[v]:
                if neighbor in pending:pending.remove(neighbor);stack.append(neighbor)
    islands.append(group)
print('WINDOW_SOURCE',len(faces),'faces',len(islands),'islands', 'dimensions',list(o.dimensions),flush=True)
reports=[]
for variant in range(3):
    rng=random.Random(870+variant);verts=[];polys=[];lit=0
    for group in islands:
        center=sum((p.center for p in group),Vector())/len(group)
        if center.z<3 or rng.random()>.18:continue
        lit+=1
        for p in group:
            ids=[]
            for index in p.vertices:
                ids.append(len(verts));verts.append(o.data.vertices[index].co+p.normal*.005)
            polys.append(ids)
    data=bpy.data.meshes.new('LitWindows');data.from_pydata(verts,[],polys);data.update();a=bpy.data.objects.new('SM_District_LitWindows_'+str(variant),data);bpy.context.collection.objects.link(a)
    bpy.ops.object.select_all(action='DESELECT');a.select_set(True);bpy.context.view_layer.objects.active=a
    bpy.ops.export_scene.fbx(filepath=str(out/(a.name+'.fbx')),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,object_types={'MESH'},path_mode='ABSOLUTE')
    reports.append({'variant':variant,'lit_panes':lit,'faces':len(polys)})
(out/'windows-manifest.json').write_text(json.dumps(reports,indent=2));print('WINDOW_OVERLAYS_READY',reports,flush=True)
