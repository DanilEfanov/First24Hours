import unreal as u,pathlib
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours/District';AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/First24Hours/Maps/L_ProceduralDistrict.')
meshes=[u.load_asset(BASE+'/Kit/Meshes/SM_CC0_Modern'+kind) for kind in ['Sedan','Wagon']];assert all(meshes)
source=(ROOT/'AgentScripts/49_ImportModernCars.py').read_text();exec(source[source.index('paints=['):])
