import unreal as u,pathlib
root=pathlib.Path(u.Paths.project_dir()).resolve();world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
pc=u.GameplayStatics.get_player_controller(world,0);pawn=u.GameplayStatics.get_player_pawn(world,0)
views=[('Living',(280,-480,100),0),('Kitchen',(245,-255,100),45),('Bathroom',(110,-160,100),90),
       ('Sleeping',(630,-280,100),90),('CityWindow',(515,-515,100),-90)]
state={'index':0,'ticks':0};handle=None
def tick(delta):
    if state['index']>=len(views):
        u.unregister_slate_post_tick_callback(handle)
        pawn.set_actor_location(u.Vector(105,-480,100),False,False)
        pc.set_control_rotation(u.Rotator(pitch=0,yaw=0,roll=0))
        u.log('FIRST24_PIE_VIEWS_COMPLETE');return
    label,pos,yaw=views[state['index']]
    if state['ticks']==0:
        pawn.set_actor_location(u.Vector(*pos),False,False)
        pc.set_control_rotation(u.Rotator(pitch=-3,yaw=yaw,roll=0))
    if state['ticks']==4:
        filename=str(root/('Documentation/Apartment_'+label+'.png')).replace('\\','/')
        u.SystemLibrary.execute_console_command(world,'Shot filename="'+filename+'"',pc)
    state['ticks']+=1
    if state['ticks']>=8:state['index']+=1;state['ticks']=0
handle=u.register_slate_post_tick_callback(tick)
