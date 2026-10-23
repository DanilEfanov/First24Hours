import unreal as u,pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve()
BASE='/Game/First24Hours/District';MAP='/Game/First24Hours/Maps/L_ProceduralDistrict'
E=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools();ML=u.MaterialEditingLibrary
AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
def ex(mat,cls,**values):
    node=ML.create_material_expression(mat,cls)
    for k,v in values.items():node.set_editor_property(k,v)
    return node
path=BASE+'/Weather/M_District_RainStreak'
mat=u.load_asset(path)
if not mat:mat=AT.create_asset('M_District_RainStreak',BASE+'/Weather',u.Material,u.MaterialFactoryNew())
ML.delete_all_material_expressions(mat)
mat.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT)
mat.set_editor_property('two_sided',True)
mat.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('used_with_niagara_sprites',True)
uv=ex(mat,u.MaterialExpressionTextureCoordinate)
pc=ex(mat,u.MaterialExpressionParticleColor)
node=ex(mat,u.MaterialExpressionCustom)
node.set_editor_property('code','float x=abs(UV.x-0.5)*2; float y=abs(UV.y-0.5)*2; return pow(saturate(1-x),2)*pow(saturate(1-y),0.5)*0.65;')
node.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT1)
inp=u.CustomInput();inp.set_editor_property('input_name','UV');node.set_editor_property('inputs',[inp])
ML.connect_material_expressions(uv,'',node,'UV')
mul=ex(mat,u.MaterialExpressionMultiply)
ML.connect_material_expressions(node,'',mul,'A');ML.connect_material_expressions(pc,'A',mul,'B')
ML.connect_material_property(mul,'',u.MaterialProperty.MP_OPACITY)
ML.connect_material_property(pc,'RGB',u.MaterialProperty.MP_EMISSIVE_COLOR)
ML.layout_material_expressions(mat);ML.recompile_material(mat);E.save_loaded_asset(mat)
actors={a.get_actor_label():a for a in AS.get_all_level_actors()}
fog=actors['District_AutumnMist'].component
fog.set_editor_property('fog_density',.025)
fog.set_editor_property('fog_height_falloff',.4)
fog.set_editor_property('start_distance',900.0)
fog.set_editor_property('enable_volumetric_fog',True)
fog.set_editor_property('volumetric_fog_scattering_distribution',.35)
fog.set_editor_property('volumetric_fog_extinction_scale',.45)
fog.set_editor_property('volumetric_fog_distance',12000.0)
# Cool daylight remains readable under the cloud layer.
pp=actors['District_OvercastPostProcess'];settings=pp.get_editor_property('settings')
settings.set_editor_property('auto_exposure_min_brightness',.0);settings.set_editor_property('auto_exposure_max_brightness',.0)
pp.set_editor_property('settings',settings)
rain=actors.get('District_Rain_Niagara')
if not rain:rain=AS.spawn_actor_from_class(u.NiagaraActor,u.Vector(0,0,1050))
rain.set_actor_label('District_Rain_Niagara');rain.set_folder_path('District/Weather')
comp=rain.get_component_by_class(u.NiagaraComponent)
comp.set_asset(u.load_asset(BASE+'/Weather/NS_District_Rain'))
comp.set_auto_activate(True);comp.activate(True)
sound_path=BASE+'/Weather/S_Rain_Outdoor_Stereo'
if not E.does_asset_exist(sound_path):
    task=u.AssetImportTask();task.filename=str(ROOT/'ArtSource/Audio/Rain_District_Outdoor_Stereo.wav')
    task.destination_path=BASE+'/Weather';task.destination_name='S_Rain_Outdoor_Stereo';task.automated=True;task.save=True
    AT.import_asset_tasks([task])
sound=u.load_asset(sound_path);assert sound
sound.set_editor_property('looping',True);E.save_loaded_asset(sound)
amb=actors.get('District_Rain_Ambience')
if not amb:amb=AS.spawn_actor_from_class(u.AmbientSound,u.Vector(0,0,200))
amb.set_actor_label('District_Rain_Ambience');amb.set_folder_path('District/Weather')
ac=amb.audio_component;ac.set_sound(sound);ac.set_volume_multiplier(.8)
ac.set_editor_property('allow_spatialization',False);ac.set_auto_activate(True)
AS.clear_actor_selection_set()
assert LS.save_current_level()
u.log('DISTRICT_WEATHER_CREATED')
