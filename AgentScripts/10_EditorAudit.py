import unreal as u, pathlib, json, hashlib
root=pathlib.Path(u.Paths.project_dir()).resolve()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/First24Hours/Maps/L_Apartment_0400'),world.get_path_name()
assets=u.EditorAssetLibrary.list_assets('/Game/First24Hours',recursive=True,include_folder=False)
for asset in assets:
    u.EditorAssetLibrary.save_asset(asset,only_if_is_dirty=True)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
missing=[]
for actor in actors:
    for component in actor.get_components_by_class(u.StaticMeshComponent):
        if not component.static_mesh:missing.append(actor.get_actor_label())
original=root/'Content/FirstPerson/Lvl_FirstPerson.umap'
digest=hashlib.sha256(original.read_bytes()).hexdigest().upper()
report={'map':world.get_path_name(),'actor_count':len(actors),'asset_count':len(assets),
        'missing_static_meshes':missing,'original_map_sha256':digest,
        'original_map_unchanged':digest=='3D476154BF4CAC39A59EC91B88F5ED6889AF113A1ECF9690A01C89D8BC32D258',
        'assets':list(assets)}
(root/'Documentation/final-editor-audit.json').write_text(json.dumps(report,indent=2))
assert not missing,missing
assert report['original_map_unchanged'],'Original map changed'
u.log('FIRST24_EDITOR_AUDIT_COMPLETE '+str(len(actors)))
