import unreal, pathlib, json
root=pathlib.Path(unreal.Paths.project_dir()).resolve()
dest='/Game/First24Hours/Art/Architecture/SM_Apartment_Floors'
if not unreal.EditorAssetLibrary.does_asset_exist(dest):
    task=unreal.AssetImportTask();task.filename=str(root/'ArtSource/Prepared/SM_Apartment_Floors.fbx')
    task.destination_path='/Game/First24Hours/Art/Architecture';task.destination_name='SM_Apartment_Floors'
    task.automated=True;task.save=True;task.replace_existing=False
    opts=unreal.FbxImportUI();opts.automated_import_should_detect_type=False;opts.import_as_skeletal=False
    opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opts.import_materials=False;opts.import_textures=False
    opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.convert_scene_unit=True
    opts.static_mesh_import_data.auto_generate_collision=False
    task.options=opts;task.factory=unreal.FbxFactory()
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
mesh=unreal.load_asset(dest);b=mesh.get_bounding_box()
result={'min':[b.min.x,b.min.y,b.min.z],'max':[b.max.x,b.max.y,b.max.z]}
(root/'Documentation/scale-probe.json').write_text(json.dumps(result))
unreal.log('FIRST24_SCALE '+str(result))
