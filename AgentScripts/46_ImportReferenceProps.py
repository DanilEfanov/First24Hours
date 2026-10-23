import unreal as u,pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours/District';E=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools();ML=u.MaterialEditingLibrary
AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/First24Hours/Maps/L_ProceduralDistrict.')
src=(ROOT/'AgentScripts/45_ApplyReferenceSurfaces.py').read_text();exec(src[src.index('def ex('):src.index('for source,target,')])
for row in json.loads((ROOT/'ArtSource/Prepared/district/cc0/manifest.json').read_text()):
    name=row['id'];asset=row['asset'];path=BASE+'/Kit/Meshes/'+asset
    if not E.does_asset_exist(path):
        task=u.AssetImportTask();task.filename=str(ROOT/'ArtSource/Prepared/district/cc0'/(asset+'.fbx'));task.destination_path=BASE+'/Kit/Meshes';task.destination_name=asset;task.automated=True;task.save=True
        opts=u.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.auto_generate_collision=False;task.options=opts;AT.import_asset_tasks([task])
    mesh=u.load_asset(path);folder=ROOT/'ArtSource/Models/reference_cc0'/name/'textures'
    for index,slot in enumerate(mesh.get_editor_property('static_materials')):
        special='bulb' if 'bulb' in str(slot.material_slot_name) else 'glass' if 'glass' in str(slot.material_slot_name) else 'body'
        mn='M_PH_'+name+'_'+special;mat=u.load_asset(BASE+'/Kit/Materials/'+mn)
        if not mat:mat=AT.create_asset(mn,BASE+'/Kit/Materials',u.Material,u.MaterialFactoryNew())
        ML.delete_all_material_expressions(mat)
        if special=='body':
            diff=sample(mat,next(folder.glob('*diff*.jpg')));normal=sample(mat,next(folder.glob('*nor_gl*.jpg')),normal=True);normal.texture.set_editor_property('flip_green_channel',True);E.save_loaded_asset(normal.texture)
            arm=sample(mat,next(folder.glob('*arm*.jpg')),linear=True)
            ML.connect_material_property(diff,'RGB',u.MaterialProperty.MP_BASE_COLOR);ML.connect_material_property(normal,'RGB',u.MaterialProperty.MP_NORMAL)
            for pin,prop in [('R',u.MaterialProperty.MP_AMBIENT_OCCLUSION),('G',u.MaterialProperty.MP_ROUGHNESS),('B',u.MaterialProperty.MP_METALLIC)]:ML.connect_material_property(arm,pin,prop)
        else:
            c=ex(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(1,.52,.18,1));mul=ex(mat,u.MaterialExpressionMultiply,const_b=3 if special=='bulb' else .8);ML.connect_material_expressions(c,'',mul,'A');ML.connect_material_property(mul,'',u.MaterialProperty.MP_EMISSIVE_COLOR);ML.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
        ML.recompile_material(mat);E.save_loaded_asset(mat);mesh.set_material(index,mat)
    E.save_loaded_asset(mesh)
    if name=='street_lamp_01':
        for a in AS.get_all_level_actors():
            if a.get_actor_label().startswith('District_StreetLamp_') and isinstance(a,u.StaticMeshActor):
                a.static_mesh_component.set_static_mesh(mesh);a.set_actor_scale3d(u.Vector(1.1,1.1,1.1))
        for a in AS.get_all_level_actors():
            if a.get_actor_label().startswith('District_StreetLight') and isinstance(a,u.PointLight):
                loc=a.get_actor_location();loc.z=380;a.set_actor_location(loc,False,False);a.light_component.set_editor_property('source_radius',15)
    else:
        for i,(x,y,yaw) in enumerate([(-1800,2800,0),(1800,-2800,180)]):
            label='District_WeatheredEntranceBench_%02d'%i
            a=next((a for a in AS.get_all_level_actors() if a.get_actor_label()==label),None)
            if not a:a=AS.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,y,15),u.Rotator(pitch=0,yaw=yaw,roll=0));a.set_actor_label(label);a.set_folder_path('District/StreetFurniture')
            a.static_mesh_component.set_static_mesh(mesh);a.set_actor_scale3d(u.Vector(.75,.75,.75));a.static_mesh_component.set_collision_profile_name('NoCollision');a.set_actor_enable_collision(False)
assert LS.save_current_level()
u.log('DISTRICT_CC0_PROPS_READY')
