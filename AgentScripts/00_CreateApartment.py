import unreal, json, pathlib, hashlib

ROOT = pathlib.Path(unreal.Paths.project_dir()).resolve()
MAP = '/Game/First24Hours/Maps/L_Apartment_0400'
eal = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
original = ROOT / 'Content/FirstPerson/Lvl_FirstPerson.umap'
baseline = {'original_map_sha256': hashlib.sha256(original.read_bytes()).hexdigest()}
if not eal.does_asset_exist(MAP):
    assert les.new_level(MAP), 'Could not create apartment level'
else:
    assert les.load_level(MAP)
for name in ['Character', 'GameMode']:
    src = '/Game/FirstPerson/Blueprints/BP_FirstPerson' + name
    dst = '/Game/First24Hours/Blueprints/BP_Apartment' + name
    if not eal.does_asset_exist(dst):
        assert eal.duplicate_asset(src, dst)
char_class = unreal.load_class(None, '/Game/First24Hours/Blueprints/BP_ApartmentCharacter.BP_ApartmentCharacter_C')
gm_class = unreal.load_class(None, '/Game/First24Hours/Blueprints/BP_ApartmentGameMode.BP_ApartmentGameMode_C')
char = unreal.get_default_object(char_class)
char.get_component_by_class(unreal.CharacterMovementComponent).set_editor_property('max_walk_speed', 185.0)
unreal.get_default_object(gm_class).set_editor_property('default_pawn_class', char_class)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property('default_game_mode', gm_class)
for p in [MAP, '/Game/First24Hours/Blueprints/BP_ApartmentCharacter', '/Game/First24Hours/Blueprints/BP_ApartmentGameMode']:
    eal.save_asset(p)
les.save_current_level()
baseline['map'] = MAP
(ROOT / 'Documentation/apartment-baseline.json').write_text(json.dumps(baseline, indent=2))
unreal.log('FIRST24_APARTMENT_LEVEL_CREATED ' + MAP)
