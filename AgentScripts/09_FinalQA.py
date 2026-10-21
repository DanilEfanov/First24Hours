import unreal as u, pathlib, json
root = pathlib.Path(u.Paths.project_dir()).resolve()
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert world, 'PIE required'
pc = u.GameplayStatics.get_player_controller(world, 0)
pawn = u.GameplayStatics.get_player_pawn(world, 0)
audio = []
for actor in u.GameplayStatics.get_all_actors_of_class(world, u.AmbientSound):
    component = actor.get_component_by_class(u.AudioComponent)
    audio.append({'actor': actor.get_name(), 'playing': component.is_playing()})
(root/'Documentation/final-pie-audio.json').write_text(json.dumps({'pawn': pawn.get_class().get_path_name(), 'ambient_audio': audio}, indent=2))
pawn.set_actor_location(u.Vector(110,-160,100),False,False)
pc.set_control_rotation(u.Rotator(pitch=-30,yaw=65,roll=0))
state={'ticks':0}
def tick(delta):
    state['ticks']+=1
    if state['ticks']==5:
        filename=str(root/'Documentation/Apartment_Bathroom_Final.png').replace('\\','/')
        u.SystemLibrary.execute_console_command(world,'Shot filename="'+filename+'"',pc)
    if state['ticks']>=10:
        u.unregister_slate_post_tick_callback(handle)
        pawn.set_actor_location(u.Vector(105,-480,100),False,False)
        pc.set_control_rotation(u.Rotator(pitch=0,yaw=0,roll=0))
        u.log('FIRST24_FINAL_QA_COMPLETE')
handle=u.register_slate_post_tick_callback(tick)
