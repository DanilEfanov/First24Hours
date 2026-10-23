import unreal as u,pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();AS=u.get_editor_subsystem(u.EditorActorSubsystem)
report=[]
for a in AS.get_all_level_actors():
    if not isinstance(a,u.PCGVolume) and not a.get_actor_label().startswith('District_DistrictGround'):continue
    row={'label':a.get_actor_label(),'location':str(a.get_actor_location()),'components':[]}
    for c in a.get_components_by_class(u.SceneComponent):
        item={'name':c.get_name(),'class':c.get_class().get_name(),'location':str(c.get_world_location())}
        if isinstance(c,u.StaticMeshComponent):
            item['mesh']=c.static_mesh.get_path_name() if c.static_mesh else None;item['material']=c.get_material(0).get_path_name() if c.get_material(0) else None;item['bounds']=str(c.get_local_bounds());item['scale']=str(c.get_world_scale())
        if isinstance(c,u.InstancedStaticMeshComponent):item['count']=c.get_instance_count()
        if isinstance(c,u.SplineComponent):item['points']=[str(c.get_location_at_spline_point(i,u.SplineCoordinateSpace.WORLD)) for i in range(c.get_number_of_spline_points())]
        row['components'].append(item)
    report.append(row)
(ROOT/'Documentation/district-geometry-audit.json').write_text(json.dumps(report,indent=2));u.log('DISTRICT_GEOMETRY_AUDIT_READY')
