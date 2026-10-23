import unreal as u, pathlib, json, math
ROOT=pathlib.Path(u.Paths.project_dir()).resolve()
OUT=ROOT/'Saved'/'CityCinematic'
OUT.mkdir(parents=True,exist_ok=True)
AS=u.get_editor_subsystem(u.EditorActorSubsystem)
assert 'L_ProceduralDistrict' in u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name()
seq=u.AssetToolsHelpers.get_asset_tools().create_asset('LS_CityFlyover_60fps','/Game/First24Hours/Cinematics',u.LevelSequence,u.LevelSequenceFactoryNew())
assert seq
seq.set_display_rate(u.FrameRate(60,1)); seq.set_playback_start(0); seq.set_playback_end(1440)
cuts=seq.add_track(u.MovieSceneCameraCutTrack)
shots=[('Overview',(-8500,-10000,10000),(-6500,-6500,7800),(0,0,900)),('Courtyard',(-2600,-2100,2300),(2200,-1200,1700),(0,700,250)),('Final', (4500,-2500,4700),(9000,6500,9500),(0,0,900))]
for idx,(name,start,end,target) in enumerate(shots):
    camera=AS.spawn_actor_from_class(u.CineCameraActor,u.Vector(*start))
    camera.set_actor_label('Cinematic_'+name)
    comp=camera.get_cine_camera_component()
    film=comp.get_editor_property('filmback');film.sensor_width=36;film.sensor_height=20.25;comp.set_editor_property('filmback',film)
    comp.set_editor_property('current_focal_length',24.0 if idx!=1 else 22.0)
    focus=comp.get_editor_property('focus_settings');focus.focus_method=u.CameraFocusMethod.DISABLE;comp.set_editor_property('focus_settings',focus)
    comp.set_editor_property('current_aperture',8.0)
    binding=seq.add_spawnable_from_instance(camera)
    AS.destroy_actor(camera)
    track=binding.add_track(u.MovieScene3DTransformTrack);section=track.add_section();section.set_range(idx*480,(idx+1)*480)
    channels=section.get_all_channels()
    for k in range(17):
        t=k/16; smooth=t*t*(3-2*t)
        pos=[a+(b-a)*smooth for a,b in zip(start,end)]
        rot=u.MathLibrary.find_look_at_rotation(u.Vector(*pos),u.Vector(*target))
        vals=pos+[rot.roll,rot.pitch,rot.yaw]+[1,1,1]
        frame=idx*480+round(t*479)
        for ch,value in zip(channels,vals):ch.add_key(u.FrameNumber(frame),value,interpolation=u.MovieSceneKeyInterpolation.LINEAR)
    cut=cuts.add_section();cut.set_range(idx*480,(idx+1)*480)
    bid=u.MovieSceneObjectBindingID();bid.set_editor_property('guid',binding.get_id());cut.set_camera_binding_id(bid)
u.EditorAssetLibrary.save_loaded_asset(seq)
capture=u.AutomatedLevelSequenceCapture()
capture.level_sequence_asset=u.SoftObjectPath(seq.get_path_name())
capture.use_separate_process=True
capture.additional_command_line_arguments='-windowed -ForceRes -NoScreenMessages -ExecCmds="r.ScreenPercentage 100,r.AntiAliasingMethod 2,r.TemporalAA.Upsampling 1"'
capture.warm_up_frame_count=60
capture.delay_before_warm_up=3
capture.delay_before_shot_warm_up=1
settings=capture.settings
settings.output_directory=u.DirectoryPath(str(OUT/'FramesStandalone'))
settings.output_format='City_{frame}'
settings.resolution=u.CaptureResolution(1920,1080)
settings.use_custom_frame_rate=True;settings.custom_frame_rate=u.FrameRate(60,1)
settings.cinematic_mode=True;settings.show_hud=False;settings.show_player=False
settings.game_mode_override=u.GameModeBase
settings.cinematic_engine_scalability=True
settings.overwrite_existing=False
settings.zero_pad_frame_numbers=6
capture.settings=settings
capture.set_image_capture_protocol_type(u.ImageSequenceProtocol_PNG)
capture.use_custom_start_frame=True;capture.custom_start_frame=u.FrameNumber(0)
capture.use_custom_end_frame=True;capture.custom_end_frame=u.FrameNumber(1439)
def finished(success):
    (OUT/'render-result.json').write_text(json.dumps({'success':success,'sequence':seq.get_path_name(),'fps':60,'frames':1440}))
callback=u.OnRenderMovieStopped();callback.bind_callable(finished)
STARTED=u.SequencerTools.render_movie(capture,callback)
(OUT/'started.json').write_text(json.dumps({'started':STARTED,'sequence':seq.get_path_name()}))
u.log('CITY_CINEMATIC_RENDER_STARTED '+str(STARTED))
