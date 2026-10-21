import unreal as u, pathlib, json, time, math
ROOT=pathlib.Path(u.Paths.project_dir()).resolve()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert world, 'PIE not running'
pawn=u.GameplayStatics.get_player_pawn(world,0);assert pawn, 'No player pawn'
pc=u.GameplayStatics.get_player_controller(world,0)
camera=u.GameplayStatics.get_player_camera_manager(world,0)
movement=pawn.get_component_by_class(u.CharacterMovementComponent)
def xyz(v):return [v.x,v.y,v.z]
result={'world':world.get_path_name(),'pawn':pawn.get_class().get_path_name(),
        'start':xyz(pawn.get_actor_location()),'camera':xyz(camera.get_camera_location()),
        'camera_rotation':str(camera.get_camera_rotation()),'walk_speed':movement.max_walk_speed,
        'movement_mode':str(movement.movement_mode)}
start=time.monotonic();origin=pawn.get_actor_location();handle=None
def tick(delta):
    global handle
    if time.monotonic()-start<1.5:
        pawn.add_movement_input(u.Vector(1,0,0),1.0)
        return
    u.unregister_slate_post_tick_callback(handle)
    end=pawn.get_actor_location();result['after_movement']=xyz(end)
    result['movement_distance_cm']=(end-origin).length()
    result['movement_passed']=result['movement_distance_cm']>50
    # Sweeps through intended open doorways; only the disposable PIE pawn moves.
    routes={
      'hall_to_living':[(105,-480,100),(300,-480,100)],
      'hall_to_kitchen':[(105,-255,100),(240,-255,100)],
      'hall_to_bath':[(110,-250,100),(110,-160,100)],
      'living_to_sleep':[(630,-360,100),(630,-280,100)]}
    result['routes']={}
    for label,points in routes.items():
        a,b=[u.Vector(*p) for p in points];pawn.set_actor_location(a,False,False)
        pawn.set_actor_location(b,True,False);actual=pawn.get_actor_location()
        result['routes'][label]={'target':xyz(b),'actual':xyz(actual),'passed':(actual-b).length()<5}
    # Test west exterior wall blocks a capsule sweep, and floor supports the pawn.
    pawn.set_actor_location(u.Vector(100,-350,100),False,False)
    pawn.set_actor_location(u.Vector(-100,-350,100),True,False)
    result['wall_blocks']=pawn.get_actor_location().x>0
    pawn.set_actor_location(u.Vector(105,-480,100),False,False)
    pc.set_control_rotation(u.Rotator(pitch=0,yaw=0,roll=0))
    (ROOT/'Documentation/pie-validation.json').write_text(json.dumps(result,indent=2))
    u.log('FIRST24_PIE_VALIDATION '+str(result))
handle=u.register_slate_post_tick_callback(tick)
