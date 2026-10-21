import unreal as u, pathlib, json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours'
AS=u.get_editor_subsystem(u.EditorActorSubsystem);E=u.EditorAssetLibrary
actors={a.get_actor_label():a for a in AS.get_all_level_actors()}
assert 'APT_Apartment_Walls' in actors
if 'PROP_KitchenTable' not in actors:
    a=AS.spawn_actor_from_class(u.StaticMeshActor,u.Vector(335,-225,1));a.set_actor_label('PROP_KitchenTable')
    a.static_mesh_component.set_static_mesh(u.load_asset(BASE+'/Art/PolyHaven/SM_PH_SchoolDesk_01'))
    a.set_actor_scale3d(u.Vector(1,1,.85));a.set_folder_path('02_Interiors')
path=BASE+'/Audio/S_Rain_Interior_Loop'
if not E.does_asset_exist(path):
    t=u.AssetImportTask();t.filename=str(ROOT/'ArtSource/Audio/Rain_Interior_Loop.wav')
    t.destination_path=BASE+'/Audio';t.destination_name='S_Rain_Interior_Loop';t.automated=True;t.save=True
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
sound=u.load_asset(path);sound.set_editor_property('looping',True);E.save_loaded_asset(sound)
if 'AUDIO_Rain_Outside' not in actors:
    a=AS.spawn_actor_from_class(u.AmbientSound,u.Vector(515,-588,160));a.set_actor_label('AUDIO_Rain_Outside');a.set_folder_path('05_Exterior')
    c=a.get_component_by_class(u.AudioComponent);c.set_sound(sound);c.set_volume_multiplier(.35)
    c.set_editor_property('allow_spatialization',False);c.set_editor_property('auto_activate',True)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('FIRST24_DRESSING_AUDIO_COMPLETE')
