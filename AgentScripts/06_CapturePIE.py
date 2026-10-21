import unreal as u,pathlib
root=pathlib.Path(u.Paths.project_dir()).resolve()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world()
assert world
pc=u.GameplayStatics.get_player_controller(world,0)
u.SystemLibrary.execute_console_command(world,'Shot filename="'+str(root/'Documentation/Apartment_PIE_Hall.png').replace('\\','/')+'"',pc)
u.log('FIRST24_GAME_SCREENSHOT_REQUESTED')
