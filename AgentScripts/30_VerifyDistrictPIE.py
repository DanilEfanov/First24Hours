import unreal as u,pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert world,'PIE world missing'
rain=[a for a in u.GameplayStatics.get_all_actors_of_class(world,u.NiagaraActor) if a.get_component_by_class(u.NiagaraComponent).get_asset() and 'NS_District_Rain' in a.get_component_by_class(u.NiagaraComponent).get_asset().get_path_name()]
audio=[a for a in u.GameplayStatics.get_all_actors_of_class(world,u.AmbientSound) if a.audio_component.sound and 'S_Rain_Outdoor' in a.audio_component.sound.get_path_name()]
pawn=u.GameplayStatics.get_player_pawn(world,0)
report={'world':world.get_path_name(),'rain_actors':len(rain),'rain_active':bool(rain and rain[0].get_component_by_class(u.NiagaraComponent).is_active()),'rain_audio_playing':bool(audio and audio[0].audio_component.is_playing()),'player':pawn.get_path_name() if pawn else None}
if pawn:
    loc=pawn.get_actor_location();report['player_location_cm']=[loc.x,loc.y,loc.z]
    assert abs(loc.x)<5000 and abs(loc.y)<5000 and 50<loc.z<250,'Player fell or spawned outside courtyard'
assert report['rain_active'] and report['rain_audio_playing'] and pawn
(ROOT/'Documentation/district-pie-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('DISTRICT_PIE_WEATHER_OK '+json.dumps(report))
