import unreal as u, pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours';E=u.EditorAssetLibrary
mesh=u.load_asset(BASE+'/Art/Furniture/SM_Bathroom_Fitted')
original=[s.material_interface for s in mesh.get_editor_property('static_materials')]
t=u.AssetImportTask();t.filename=str(ROOT/'ArtSource/Prepared/SM_Bathroom_Fitted.fbx')
t.destination_path=BASE+'/Art/Furniture';t.destination_name='SM_Bathroom_Fitted'
t.automated=True;t.save=True;t.replace_existing=True
opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.import_as_skeletal=False
opts.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opts.import_materials=False;opts.import_textures=False
opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.convert_scene_unit=True
opts.static_mesh_import_data.auto_generate_collision=False;t.options=opts;t.factory=u.FbxFactory()
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
for i,material in enumerate(original):mesh.set_material(i,material)
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
E.save_loaded_asset(mesh)
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    if a.get_actor_label() in ['APT_City_Backdrop','EXT_ExistingSovietBuilding','APT_Window_Rain']:
        a.static_mesh_component.set_cast_shadow(False)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('FIRST24_BATH_CLEARANCE_AND_SHADOWS_FIXED')
