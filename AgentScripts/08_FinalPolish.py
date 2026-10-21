import unreal as u,pathlib
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours';E=u.EditorAssetLibrary
path=BASE+'/Art/Architecture/SM_Bathroom_TileLining'
if not E.does_asset_exist(path):
    t=u.AssetImportTask();t.filename=str(ROOT/'ArtSource/Prepared/SM_Bathroom_TileLining.fbx')
    t.destination_path=BASE+'/Art/Architecture';t.destination_name='SM_Bathroom_TileLining';t.automated=True;t.save=True
    opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.import_as_skeletal=False
    opts.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opts.import_materials=False;opts.import_textures=False
    opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.convert_scene_unit=True;opts.static_mesh_import_data.auto_generate_collision=False
    t.options=opts;t.factory=u.FbxFactory();u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
mesh=u.load_asset(path);mesh.set_material(0,u.load_asset(BASE+'/Art/Materials/M_Tile'));E.save_loaded_asset(mesh)
AS=u.get_editor_subsystem(u.EditorActorSubsystem)
if not any(a.get_actor_label()=='APT_Bathroom_TileLining' for a in AS.get_all_level_actors()):
    a=AS.spawn_actor_from_class(u.StaticMeshActor,u.Vector());a.set_actor_label('APT_Bathroom_TileLining')
    a.static_mesh_component.set_static_mesh(mesh);a.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
    a.set_folder_path('01_Architecture')
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('FIRST24_FINAL_TILE_FINISH_SAVED')
