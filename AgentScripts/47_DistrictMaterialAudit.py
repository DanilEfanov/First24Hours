import unreal as u,pathlib,json
from editor_toolset.toolsets.material import MaterialTools
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();AS=u.get_editor_subsystem(u.EditorActorSubsystem)
a=next(a for a in AS.get_all_level_actors() if a.get_actor_label().startswith('District_House_North'))
data=[]
for s in a.static_mesh_component.static_mesh.get_editor_property('static_materials'):
    mat=s.material_interface;row={'slot':str(s.material_slot_name),'path':mat.get_path_name(),'class':mat.get_class().get_name()}
    if isinstance(mat,u.Material):row['nodes']=[{'name':e.get_name(),'class':e.get_class().get_name(),'texture':e.texture.get_path_name() if isinstance(e,u.MaterialExpressionTextureSample) and e.texture else None} for e in MaterialTools.get_expressions(mat)]
    data.append(row)
(ROOT/'Documentation/district-house-materials.json').write_text(json.dumps(data,indent=2))
u.log('DISTRICT_MATERIAL_AUDIT_READY')
