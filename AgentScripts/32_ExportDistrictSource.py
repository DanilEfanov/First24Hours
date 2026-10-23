import unreal as u,pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();folder=ROOT/'ArtSource/Prepared/district/source';folder.mkdir(parents=True,exist_ok=True)
paths={'House':'/Game/Assets/Environment/SovietApartmentBuilding/nine_story_building_of_the_post_soviet/StaticMeshes/nine_story_building_of_the_post_soviet','Cars':'/Game/Assets/Vehicles/SovietCars/low_poly_soviet_cars/StaticMeshes/low_poly_soviet_cars'}
manifest={}
for name,path in paths.items():
    mesh=u.load_asset(path);assert mesh
    task=u.AssetExportTask();task.object=mesh;task.filename=str(folder/(name+'.fbx'));task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=u.StaticMeshExporterFBX()
    assert u.Exporter.run_asset_export_task(task)
    manifest[name]={'source':path,'slots':[{'name':str(s.material_slot_name),'material':s.material_interface.get_path_name() if s.material_interface else None} for s in mesh.get_editor_property('static_materials')]}
(folder/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
u.log('DISTRICT_SOURCES_EXPORTED')
