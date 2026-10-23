import unreal as u,pathlib,json,math
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();MAP='/Game/First24Hours/Maps/L_ProceduralDistrict'
AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
layout=json.loads((ROOT/'Documentation/district-reference-layout.json').read_text())
actors={a.get_actor_label():a for a in AS.get_all_level_actors()}
yaws={'North':-90,'South':90,'West':0,'East':180}
changed=[]
for row in layout['building_rows']:
    name=row['name'];yaw=yaws[name];angle=math.radians(yaw)
    for i,center in enumerate(row['section_centers_cm']):
        label='District_House_'+name+'_Section_%03d'%(i+1);a=actors[label];mesh=a.static_mesh_component.static_mesh
        b=mesh.get_bounding_box();cx=(b.min.x+b.max.x)*.5;cy=(b.min.y+b.max.y)*.5;sc=.8
        ox=sc*(cx*math.cos(angle)-cy*math.sin(angle));oy=sc*(cx*math.sin(angle)+cy*math.cos(angle))
        a.set_actor_rotation(u.Rotator(pitch=0,yaw=yaw,roll=0),False)
        a.set_actor_location(u.Vector(center[0]-ox,center[1]-oy,-b.min.z*sc),False,False)
        changed.append(label)
    row['entrance_facing_yaw']=yaw
layout['entrances_rotated_180_degrees']=True
(ROOT/'Documentation/district-reference-layout.json').write_text(json.dumps(layout,indent=2),encoding='utf-8')
assert LS.save_current_level()
u.log('DISTRICT_ENTRANCES_ROTATED '+str(len(changed)))
