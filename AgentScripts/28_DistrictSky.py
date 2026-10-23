import unreal as u
BASE='/Game/First24Hours/District';E=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools();ML=u.MaterialEditingLibrary
AS=u.get_editor_subsystem(u.EditorActorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/First24Hours/Maps/L_ProceduralDistrict.')
mat=u.load_asset(BASE+'/Weather/M_OvercastSkyDome')
if not mat:mat=AT.create_asset('M_OvercastSkyDome',BASE+'/Weather',u.Material,u.MaterialFactoryNew())
ML.delete_all_material_expressions(mat);mat.set_editor_property('two_sided',True);mat.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
color=ML.create_material_expression(mat,u.MaterialExpressionConstant3Vector);color.set_editor_property('constant',u.LinearColor(.19,.215,.24,1))
ML.connect_material_property(color,'',u.MaterialProperty.MP_EMISSIVE_COLOR);ML.recompile_material(mat);E.save_loaded_asset(mat)
actors={a.get_actor_label():a for a in AS.get_all_level_actors()}
a=actors.get('District_OvercastSkyDome')
if not a:a=AS.spawn_actor_from_class(u.StaticMeshActor,u.Vector())
a.set_actor_label('District_OvercastSkyDome');a.set_folder_path('District/Atmosphere')
a.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Sphere'))
a.static_mesh_component.set_material(0,mat);a.static_mesh_component.set_collision_profile_name('NoCollision')
a.set_actor_enable_collision(False)
a.static_mesh_component.set_cast_shadow(False);a.set_actor_scale3d(u.Vector(1800,1800,1800))
actors['District_AutumnMist'].component.set_editor_property('fog_inscattering_luminance',u.LinearColor(.21,.235,.26,1))
# Let the neutral dome provide the overcast background; clouds remain available for later art direction.
actors['District_OvercastClouds'].set_actor_hidden_in_game(True);actors['District_OvercastClouds'].set_is_temporarily_hidden_in_editor(True)
AS.clear_actor_selection_set();u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('DISTRICT_OVERCAST_SKY_READY')
