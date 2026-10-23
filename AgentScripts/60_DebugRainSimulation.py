import unreal as u,pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();w=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_game_world();assert w
c=next(a.get_component_by_class(u.NiagaraComponent) for a in u.GameplayStatics.get_all_actors_of_class(w,u.NiagaraActor) if a.get_component_by_class(u.NiagaraComponent).get_asset() and 'District_Rain' in a.get_component_by_class(u.NiagaraComponent).get_asset().get_name())
cache=u.NiagaraSimCacheFunctionLibrary.create_niagara_sim_cache(w)
p=u.NiagaraSimCacheCreateParameters();p.set_editor_property('attribute_capture_mode',u.NiagaraSimCacheAttributeCaptureMode.ALL)
result=u.NiagaraSimCacheFunctionLibrary.capture_niagara_sim_cache_immediate(cache,p,c,True,.01666)
u.log('RAIN_CACHE_RESULT '+str(result)+' frames '+str(cache.get_num_frames()))
positions=cache.read_position_attribute(emitter_name='DistrictRain')
row={'count':len(positions),'samples':[[p.x,p.y,p.z] for p in list(positions)[:8]]}
if positions:row['bounds']=[[min(getattr(p,axis) for p in positions),max(getattr(p,axis) for p in positions)] for axis in ['x','y','z']]
assert len(positions)>1000,'Rain is active without sufficient live particles'
assert max(abs(v) for pair in row['bounds'][:2] for v in pair)<5000,'Rain spawned outside the courtyard'
assert 900<row['bounds'][2][1]<1250,'Rain spawning height is incorrect'
(ROOT/'Documentation/district-rain-particles.json').write_text(json.dumps(row,indent=2));u.log('RAIN_PARTICLE_AUDIT '+json.dumps(row))
