import unreal as u,pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours/District';E=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools();ML=u.MaterialEditingLibrary
AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem);SMS=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/First24Hours/Maps/L_ProceduralDistrict.')
src=(ROOT/'AgentScripts/45_ApplyReferenceSurfaces.py').read_text();exec(src[src.index('def ex('):src.index('for source,target,')])
folder=ROOT/'ArtSource/Prepared/district/cc0';meshes=[]
def constant(mat,value,prop):
    e=ex(mat,u.MaterialExpressionConstant,r=value);ML.connect_material_property(e,'',prop)
for kind in ['Sedan','Wagon']:
    asset='SM_CC0_Modern'+kind;path=BASE+'/Kit/Meshes/'+asset
    if not E.does_asset_exist(path):
        task=u.AssetImportTask();task.filename=str(folder/(asset+'.fbx'));task.destination_path=BASE+'/Kit/Meshes';task.destination_name=asset;task.automated=True;task.save=True
        opts=u.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.auto_generate_collision=False;task.options=opts;AT.import_asset_tasks([task])
    mesh=u.load_asset(path);info=json.loads((folder/(kind.lower()+'-manifest.json')).read_text());mapping={r['name'].replace('.','_'):r for r in info['materials']}
    for index,slot in enumerate(mesh.get_editor_property('static_materials')):
        key=str(slot.material_slot_name).replace('.','_');row=mapping[key];mn='M_CC0_'+kind+'_'+key;mat=u.load_asset(BASE+'/Kit/Materials/'+mn)
        if not mat:mat=AT.create_asset(mn,BASE+'/Kit/Materials',u.Material,u.MaterialFactoryNew())
        ML.delete_all_material_expressions(mat)
        color=sample(mat,folder/row['textures'][0]) if row['textures'] else ex(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(*row['color']))
        ML.connect_material_property(color,'RGB' if row['textures'] else '',u.MaterialProperty.MP_BASE_COLOR)
        constant(mat,row['roughness'],u.MaterialProperty.MP_ROUGHNESS);constant(mat,row['metallic'],u.MaterialProperty.MP_METALLIC)
        ML.recompile_material(mat);E.save_loaded_asset(mat);mesh.set_material(index,mat)
    ns=mesh.get_editor_property('nanite_settings');ns.set_editor_property('enabled',True);mesh.set_editor_property('nanite_settings',ns)
    assert SMS.set_convex_decomposition_collisions(mesh,4,16,50000)
    E.save_loaded_asset(mesh);meshes.append(mesh)
paints=[u.load_asset(BASE+'/Kit/Materials/M_District_CarPaint_'+str(i)) for i in range(6)]
vehicles=sorted([a for a in AS.get_all_level_actors() if a.get_actor_label().startswith('District_ParkedVehicle')],key=lambda a:a.get_actor_label())
for i,a in enumerate(vehicles):
    c=a.static_mesh_component;c.set_editor_property('override_materials',[]);m=meshes[i%2];c.set_static_mesh(m);a.set_actor_scale3d(u.Vector(1,1,1));c.set_collision_profile_name('BlockAll');a.set_actor_enable_collision(True)
    for index,slot in enumerate(m.get_editor_property('static_materials')):
        if str(slot.material_slot_name).startswith('paint'):c.set_material(index,paints[i%6])
assert LS.save_current_level();u.log('DISTRICT_MODERN_VEHICLES_READY '+str(len(vehicles)))
