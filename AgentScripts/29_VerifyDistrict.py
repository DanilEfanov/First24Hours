import unreal as u,pathlib,json,hashlib
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();MAP='/Game/First24Hours/Maps/L_ProceduralDistrict'
LS=u.get_editor_subsystem(u.LevelEditorSubsystem);AS=u.get_editor_subsystem(u.EditorActorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
report=json.loads((ROOT/'Documentation/district-build-report.json').read_text())
actors={a.get_actor_label():a for a in AS.get_all_level_actors()}
pcg=[]
for a in actors.values():
    if not isinstance(a,u.PCGVolume):continue
    item={'label':a.get_actor_label(),'instances':[],'splines':[]}
    for c in a.get_components_by_class(u.InstancedStaticMeshComponent):
        item['instances'].append({'mesh':c.static_mesh.get_path_name(),'count':c.get_instance_count()})
    for c in a.get_components_by_class(u.SplineComponent):item['splines'].append({'points':c.get_number_of_spline_points(),'length_cm':c.get_spline_length()})
    pcg.append(item)
report['pcg_actual_components']=pcg
tree_count=sum(i['count'] for p in pcg if 'Trees' in p['label'] for i in p['instances'])
assert tree_count>0,'No actual PCG tree instances'
report['tree_instances']=tree_count
report['missing']=['modular facade kit','street benches, bins and lamps','individual realistic vehicles','surrounding city context']
report['weather']={'niagara':actors['District_Rain_Niagara'].get_component_by_class(u.NiagaraComponent).get_asset().get_path_name(),'stereo_loop':actors['District_Rain_Ambience'].audio_component.sound.get_path_name(),'volumetric_fog':actors['District_AutumnMist'].component.get_editor_property('enable_volumetric_fog')}
for filename,digest in report['existing_map_hashes'].items():assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()==digest
AS.clear_actor_selection_set()
# Save the current world with PCG-generated components, then reload through the level subsystem.
assert LS.save_current_level()
assert LS.load_level(MAP)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
report['reopen_success']=True
report['stage']='Saved and reopened courtyard, trees, fog, Niagara rain and stereo ambience'
(ROOT/'Documentation/district-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(u.Vector(-4200,-4900,3000),u.Rotator(pitch=-23,yaw=48,roll=0))
u.log('DISTRICT_REOPEN_CHECK_OK '+str(tree_count)+' trees')
