import unreal as u,pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();MAP='/Game/First24Hours/Maps/L_ProceduralDistrict';BASE='/Game/First24Hours/District';LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert not u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world(),'Stop PIE before final save'
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
assert u.EditorAssetLibrary.save_directory(BASE,only_if_is_dirty=True,recursive=True)
assert LS.save_current_level();assert LS.load_level(MAP)
report=json.loads((ROOT/'Documentation/district-build-report.json').read_text());report['pie']=json.loads((ROOT/'Documentation/district-pie-check.json').read_text());report['rain_particles']=json.loads((ROOT/'Documentation/district-rain-particles.json').read_text())
assert report['pie']['rain_active'] and report['pie']['rain_audio_playing'] and report['rain_particles']['count']>1000
assert max(abs(v) for pair in report['rain_particles']['bounds'][:2] for v in pair)<5000
report['weather']['rain_coverage_cm']=[8000,6500];report['weather']['rain_spawn_z_cm']=1050;report['final_saved_and_reopened']=True
(ROOT/'Documentation/district-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.get_editor_subsystem(u.EditorActorSubsystem).clear_actor_selection_set()
LS.editor_set_game_view(True)
u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(u.Vector(0,8000,8000),u.Rotator(pitch=-53,yaw=-90,roll=0))
u.log('DISTRICT_FINAL_SAVED_AND_REOPENED')
