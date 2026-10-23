import bpy,pathlib,json,hashlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];wagon='--wagon' in sys.argv
src=ROOT/('ArtSource/Models/reference_cc0/generic-station-wagon.glb' if wagon else 'ArtSource/Models/reference_cc0/graphite-four-door-sedan.glb');out=ROOT/'ArtSource/Prepared/district/cc0'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(src))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];info={'source':'https://www.innerscene.com/tools/library/3d-parts/graphite-four-door-sedan-eed96d12','license':'CC0','sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'objects':[{'name':o.name,'dimensions':list(o.dimensions),'polygons':len(o.data.polygons)} for o in meshes]}
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
if len(meshes)>1:bpy.ops.object.join()
o=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
pts=[v.co.copy() for v in o.data.vertices];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
for v in o.data.vertices:v.co.x-=(lo[0]+hi[0])/2;v.co.y-=(lo[1]+hi[1])/2;v.co.z-=lo[2]
# Existing parking actors use longitudinal X. Rotate source if its longest axis is Y.
if hi[1]-lo[1]>hi[0]-lo[0]:
    o.rotation_euler.z=1.5707963267948966;bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
info['dimensions_m']=[hi[i]-lo[i] for i in range(3)]
if wagon:info['source']='https://www.innerscene.com/tools/library/3d-parts/generic-station-wagon-estate-car-dec07098'
info['materials']=[]
for m in o.data.materials:
    p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) if m.use_nodes else None
    row={'name':m.name,'color':list(p.inputs['Base Color'].default_value) if p else list(m.diffuse_color),'metallic':p.inputs['Metallic'].default_value if p else 0,'roughness':p.inputs['Roughness'].default_value if p else .5,'textures':[]}
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image:
                image=n.image;file=out/(image.name.replace('/','_')+'.png');image.filepath_raw=str(file);image.file_format='PNG';image.save();row['textures'].append(str(file.name))
    info['materials'].append(row)
asset='SM_CC0_ModernWagon' if wagon else 'SM_CC0_ModernSedan'
bpy.ops.export_scene.fbx(filepath=str(out/(asset+'.fbx')),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,object_types={'MESH'},path_mode='ABSOLUTE')
(out/('wagon-manifest.json' if wagon else 'sedan-manifest.json')).write_text(json.dumps(info,indent=2));print('VEHICLE_READY',asset,len(o.data.polygons),info['dimensions_m'],flush=True)
