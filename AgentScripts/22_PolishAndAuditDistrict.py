import unreal as u, json, pathlib, hashlib
from editor_toolset.toolsets.material import MaterialTools
ROOT=pathlib.Path(u.Paths.project_dir()).resolve()
MAP='/Game/First24Hours/Maps/L_ProceduralDistrict'
BASE='/Game/First24Hours/District'
AS=u.get_editor_subsystem(u.EditorActorSubsystem)
LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
W=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert W.get_path_name().startswith(MAP+'.')
actors={a.get_actor_label():a for a in AS.get_all_level_actors()}
house=actors['District_House_B_9Floors']
house.set_actor_location(u.Vector(1560.870569,1524.109143,41.768628),False,False)
house.set_actor_scale3d(u.Vector(.8,.8,.8))
house.set_actor_rotation(u.Rotator(pitch=0,yaw=180,roll=0),False)
sun=actors['District_OvercastSun']
sun.set_actor_rotation(u.Rotator(pitch=-65,yaw=-35,roll=0),False)
sun.light_component.set_editor_property('intensity',.6)
sun.light_component.set_editor_property('light_source_angle',20.0)
sky=actors['District_OvercastSkylight'].light_component
sky.set_editor_property('real_time_capture',False)
sky.set_editor_property('source_type',u.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
sky.set_editor_property('cubemap',u.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap'))
sky.set_editor_property('intensity',1.7)
sky.set_editor_property('light_color',u.Color(214,223,232,255))
for name,colors,freq in [
 ('M_District_WetAsphalt',[(.022,.026,.029),(.032,.036,.039)],.003),
 ('M_District_DampConcrete',[(.20,.20,.19),(.26,.26,.25)],.025),
 ('M_District_AutumnGround',[(.045,.044,.032),(.062,.060,.040)],.009),
 ('M_District_WornRoadPaint',[(.40,.39,.33),(.48,.47,.40)],.03)]:
    mat=u.load_asset(BASE+'/Materials/'+name)
    color_nodes=[]
    for obj in MaterialTools.get_expressions(mat):
        if isinstance(obj,u.MaterialExpressionConstant3Vector):color_nodes.append(obj)
        if isinstance(obj,u.MaterialExpressionNoise):
            obj.set_editor_property('scale',freq)
            obj.set_editor_property('output_min',0.0);obj.set_editor_property('output_max',1.0)
    for obj,rgb in zip(color_nodes,colors):obj.set_editor_property('constant',u.LinearColor(*rgb,1))
    u.MaterialEditingLibrary.recompile_material(mat)
    u.EditorAssetLibrary.save_loaded_asset(mat)
AS.clear_actor_selection_set()
ground=actors.get('District_Ground_110x100m') or actors['District_Ground_90x85m']
ground.set_actor_location(u.Vector(0,700,-26),False,False)
ground.set_actor_scale3d(u.Vector(90,85,.5))
ground.set_actor_label('District_Ground_90x85m')
actors['District_PlayerStart'].set_actor_rotation(u.Rotator(pitch=0,yaw=90,roll=0),False)
u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(u.Vector(-4500,-5200,3300),u.Rotator(pitch=-23,yaw=48,roll=0))
AR=u.AssetRegistryHelpers.get_asset_registry()
inventory=[]
for data in AR.get_assets_by_path('/Game',recursive=True):
    cls=str(data.asset_class_path.asset_name)
    row={'path':str(data.package_name),'class':cls}
    if cls=='StaticMesh':
        mesh=data.get_asset();b=mesh.get_bounding_box()
        row['bounds_cm']={'min':[b.min.x,b.min.y,b.min.z],'max':[b.max.x,b.max.y,b.max.z]}
        row['material_slots']=[str(v.material_slot_name) for v in mesh.get_editor_property('static_materials')]
    if cls in ['StaticMesh','Material','MaterialInstanceConstant','Texture2D','TextureCube','PCGGraph','World','Blueprint']:inventory.append(row)
(ROOT/'Documentation/district-asset-inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
assert LS.save_current_level()
report=json.loads((ROOT/'Documentation/district-build-report.json').read_text())
report['stage']='Saved stage-one district with spline road and PCG point-output foundations'
report['inventory_count']=len(inventory)
report['actor_count']=len(actors)
report['pcg']={'road':'Create Points -> Create Spline (component) -> Spawn Spline Mesh','trees':'12 explicit safe anchors -> Transform Points -> Self Pruning -> Output; mesh assets missing','decor':'6 explicit anchors -> Transform Points -> Self Pruning -> Output; mesh assets missing'}
report['building_bounds']={}
for label in ['District_House_A_9Floors','District_House_B_9Floors']:
    origin,extent=actors[label].get_actor_bounds(False)
    report['building_bounds'][label]={'origin':[origin.x,origin.y,origin.z],'extent':[extent.x,extent.y,extent.z]}
    assert origin.z-extent.z > -1 and origin.z+extent.z >2700
for filename,digest in report['existing_map_hashes'].items():assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()==digest
(ROOT/'Documentation/district-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('DISTRICT_POLISH_AUDIT_OK')
