import unreal as u,pathlib,json,random,math
from editor_toolset.toolsets.material import MaterialTools
from editor_toolset.toolsets.actor import ActorTools
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours/District';E=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools();ML=u.MaterialEditingLibrary
AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/First24Hours/Maps/L_ProceduralDistrict.')
src=(ROOT/'AgentScripts/45_ApplyReferenceSurfaces.py').read_text();exec(src[src.index('def ex('):src.index('for source,target,')])
meshes={}
for row in json.loads((ROOT/'ArtSource/Prepared/district/cc0/foliage-manifest.json').read_text()):
    name=row['id'];asset=row['asset'];path=BASE+'/Foliage/'+asset
    if not E.does_asset_exist(path):
        t=u.AssetImportTask();t.filename=str(ROOT/'ArtSource/Prepared/district/cc0'/(asset+'.fbx'));t.destination_path=BASE+'/Foliage';t.destination_name=asset;t.automated=True;t.save=True
        o=u.FbxImportUI();o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.import_as_skeletal=False;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;t.options=o;AT.import_asset_tasks([t])
    mesh=u.load_asset(path);mn='M_PH_'+name;mat=u.load_asset(BASE+'/Foliage/'+mn)
    if not mat:mat=AT.create_asset(mn,BASE+'/Foliage',u.Material,u.MaterialFactoryNew())
    ML.delete_all_material_expressions(mat);mat.set_editor_property('two_sided',True);mat.set_editor_property('blend_mode',u.BlendMode.BLEND_MASKED);mat.set_editor_property('opacity_mask_clip_value',.28)
    folder=ROOT/'ArtSource/Models/reference_cc0'/name/'textures';files=list(folder.glob('*dry_diff*.jpg')) or list(folder.glob('*diff*.jpg'))
    color=sample(mat,files[0]);tint=ex(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(.7,.50,.24,1));mul=ex(mat,u.MaterialExpressionMultiply);assert ML.connect_material_expressions(color,'RGB',mul,'A');assert ML.connect_material_expressions(tint,'',mul,'B');ML.connect_material_property(mul,'',u.MaterialProperty.MP_BASE_COLOR)
    alpha=sample(mat,next(folder.glob('*alpha*.png')),linear=True);ML.connect_material_property(alpha,'R',u.MaterialProperty.MP_OPACITY_MASK)
    normal=sample(mat,next(folder.glob('*nor_gl*.jpg')),normal=True);normal.texture.set_editor_property('flip_green_channel',True);E.save_loaded_asset(normal.texture);ML.connect_material_property(normal,'RGB',u.MaterialProperty.MP_NORMAL)
    rough=ex(mat,u.MaterialExpressionConstant,r=.84);ML.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
    MaterialTools.recompile(mat);E.save_loaded_asset(mat)
    for i in range(len(mesh.get_editor_property('static_materials'))):mesh.set_material(i,mat)
    ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',True);ns.set_editor_property('shape_preservation',u.NaniteShapePreservation.PRESERVE_AREA);ns.set_editor_property('fallback_relative_error',0.0);mesh.set_editor_property('nanite_settings',ns);E.save_loaded_asset(mesh);meshes[name]=mesh
rng=random.Random(20261023);layout=json.loads((ROOT/'Documentation/district-reference-layout.json').read_text())
def owner(label,mesh):
    a=next((a for a in AS.get_all_level_actors() if a.get_actor_label()==label),None)
    if not a:a=AS.spawn_actor_from_class(u.StaticMeshActor,u.Vector(),u.Rotator());a.set_actor_label(label);a.set_folder_path('District/GardenUnderstory')
    c=a.get_component_by_class(u.InstancedStaticMeshComponent)
    if not c:c=ActorTools.add_component(a,u.InstancedStaticMeshComponent.static_class(),'GardenInstances')
    c.set_static_mesh(mesh);c.set_collision_profile_name('NoCollision');c.clear_instances();a.set_actor_enable_collision(False);return c
grass=owner('District_GardenGrassInstances',meshes['grass_medium_01']);shrub=owner('District_GardenUnderstoryInstances',meshes['shrub_01'])
def instance(c,x,y,z,scale,yaw):c.add_instance(u.Transform(location=u.Vector(x,y,z),rotation=u.Rotator(pitch=0,yaw=yaw,roll=0),scale=u.Vector(scale,scale,scale)),True)
count=0
# Planted frontage strips sit between the facade and walk; gaps remain at every entrance.
for sign in [-1,1]:
    for axis in ['NS','EW']:
        extent=3450 if axis=='NS' else 2450;entrances=[-2728,-909,909,2728] if axis=='NS' else [-1819,0,1819]
        for p in range(-extent,extent+1,105):
            if any(abs(p-e)<160 for e in entrances):continue
            x,y=(p,sign*2975) if axis=='NS' else (sign*4120,p)
            for j in range(5):instance(grass,x+rng.uniform(-60,60),y+rng.uniform(-105,105),0,rng.uniform(.9,1.6),rng.uniform(0,360));count+=1
        for p in range(-extent+250,extent,480):
            if any(abs(p-e)<220 for e in entrances):continue
            x,y=(p,sign*2980) if axis=='NS' else (sign*4110,p)
            instance(shrub,x,y,0,rng.uniform(.65,.9),0 if axis=='NS' else 90)
# Grass grows below selected canopy anchors, rather than across roads and paved play areas.
for x,y,z in layout['tree_points']:
    if 250<x<2150 and -750<y<850:continue
    for j in range(12):
        angle=rng.random()*math.tau;r=rng.uniform(60,165);instance(grass,x+math.cos(angle)*r,y+math.sin(angle)*r,0,rng.uniform(.8,1.5),rng.uniform(0,360));count+=1
# Tone down repetitive leaf texture using broad world-space variation.
ground=u.load_asset(BASE+'/Materials/M_District_AutumnGround');nodes=MaterialTools.get_expressions(ground);base=MaterialTools.get_property_input(ground,u.MaterialProperty.MP_BASE_COLOR).expression
pos=next(e for e in nodes if isinstance(e,u.MaterialExpressionWorldPosition));noise=ex(ground,u.MaterialExpressionNoise,scale=.0013,levels=2,quality=1,output_min=.45,output_max=.85);ML.connect_material_expressions(pos,'XYZ',noise,'Position')
mul=ex(ground,u.MaterialExpressionMultiply);ML.connect_material_expressions(base,'',mul,'A');ML.connect_material_expressions(noise,'',mul,'B');ML.connect_material_property(mul,'',u.MaterialProperty.MP_BASE_COLOR);MaterialTools.recompile(ground);E.save_loaded_asset(ground)
assert LS.save_current_level();u.log('DISTRICT_GARDENS_READY '+str({'grass':grass.get_instance_count(),'understory':shrub.get_instance_count()}))
