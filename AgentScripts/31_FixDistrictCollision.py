import unreal as u
AS=u.get_editor_subsystem(u.EditorActorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/First24Hours/Maps/L_ProceduralDistrict.')
for a in AS.get_all_level_actors():
    if a.get_actor_label()=='District_OvercastSkyDome':
        a.set_actor_enable_collision(False)
        c=a.static_mesh_component;c.set_collision_profile_name('NoCollision')
        c.set_editor_property('affect_distance_field_lighting',False)
        c.set_editor_property('affect_dynamic_indirect_lighting',False)
        c.set_editor_property('visible_in_ray_tracing',False)
AS.clear_actor_selection_set()
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('DISTRICT_SKYDOME_COLLISION_FIXED')
