"""Run in the Unreal Editor via MCP Slate console. Creates district assets only."""
import unreal as u
import json, pathlib, hashlib, math

ROOT = pathlib.Path(u.Paths.project_dir()).resolve()
MAP = '/Game/First24Hours/Maps/L_ProceduralDistrict'
BASE = '/Game/First24Hours/District'
E = u.EditorAssetLibrary
AS = u.get_editor_subsystem(u.EditorActorSubsystem)
LS = u.get_editor_subsystem(u.LevelEditorSubsystem)
WORLD = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert WORLD.get_path_name().startswith(MAP + '.'), 'Refusing to modify another map'
assert not any(a.get_actor_label().startswith('District_') for a in AS.get_all_level_actors()), 'Already built'
AT = u.AssetToolsHelpers.get_asset_tools()
ML = u.MaterialEditingLibrary
report = {'map': MAP, 'warnings': [], 'dimensions_cm': {'road_width': 600, 'sidewalk_width': 180, 'parking_bay': [250,500], 'residential_floor_target': 280}, 'created_actors': [], 'missing': ['modular panel-house facade kit', 'autumn deciduous trees', 'street benches, bins, lamps', 'individual realistic parked cars']}
report['existing_map_hashes'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'Content/FirstPerson/Lvl_FirstPerson.umap',ROOT/'Content/First24Hours/Maps/L_Apartment_0400.umap']}

def spawn(cls, label, xyz=(0,0,0), rot=(0,0,0), folder='District'):
    a = AS.spawn_actor_from_class(cls, u.Vector(*xyz), u.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]))
    assert a, label
    a.set_actor_label('District_' + label)
    a.set_folder_path(folder)
    report['created_actors'].append(a.get_path_name())
    return a

def ex(mat, cls, **props):
    e = ML.create_material_expression(mat,cls)
    for k,v in props.items(): e.set_editor_property(k,v)
    return e

def out(e, prop, pin=''):
    assert ML.connect_material_property(e,pin,prop)

def surface(name, color_a, color_b, rough_a, rough_b, frequency):
    mat = AT.create_asset(name,BASE+'/Materials',u.Material,u.MaterialFactoryNew())
    assert mat, name
    pos=ex(mat,u.MaterialExpressionWorldPosition)
    n=ex(mat,u.MaterialExpressionNoise,scale=frequency,levels=3,quality=1)
    ML.connect_material_expressions(pos,'',n,'Position')
    a=ex(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(*color_a,1))
    b=ex(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(*color_b,1))
    blend=ex(mat,u.MaterialExpressionLinearInterpolate)
    for node,pin in [(a,'A'),(b,'B'),(n,'Alpha')]: ML.connect_material_expressions(node,'',blend,pin)
    out(blend,u.MaterialProperty.MP_BASE_COLOR)
    r=ex(mat,u.MaterialExpressionLinearInterpolate,const_a=rough_a,const_b=rough_b)
    ML.connect_material_expressions(n,'',r,'Alpha')
    out(r,u.MaterialProperty.MP_ROUGHNESS)
    spec=ex(mat,u.MaterialExpressionConstant,r=.5)
    out(spec,u.MaterialProperty.MP_SPECULAR)
    ML.layout_material_expressions(mat)
    ML.recompile_material(mat)
    E.save_loaded_asset(mat)
    return mat

asphalt=surface('M_District_WetAsphalt',(.018,.022,.025),(.045,.049,.052),.12,.36,.008)
concrete=surface('M_District_DampConcrete',(.19,.185,.17),(.31,.30,.28),.36,.64,.025)
soil=surface('M_District_AutumnGround',(.045,.039,.024),(.11,.095,.045),.75,.95,.013)
paint=surface('M_District_WornRoadPaint',(.34,.33,.27),(.57,.55,.46),.3,.6,.04)
cube=u.load_asset('/Engine/BasicShapes/Cube')

def slab(label, xyz, size, mat, folder='District/Surfaces'):
    a=spawn(u.StaticMeshActor,label,xyz,folder=folder)
    c=a.static_mesh_component
    c.set_static_mesh(cube)
    c.set_material(0,mat)
    c.set_collision_profile_name('BlockAll')
    a.set_actor_scale3d(u.Vector(*(v/100.0 for v in size)))
    return a

slab('Ground_110x100m',(0,0,-26),(11000,10000,50),soil)
# Real imported nine-storey building, no primitive facade substitutions.
house=u.load_asset('/Game/Assets/Environment/SovietApartmentBuilding/nine_story_building_of_the_post_soviet/StaticMeshes/nine_story_building_of_the_post_soviet')
b=house.get_bounding_box()
report['building_source_bounds']={'min':[b.min.x,b.min.y,b.min.z],'max':[b.max.x,b.max.y,b.max.z]}
factor=.8
cx=(b.min.x+b.max.x)*.5; cy=(b.min.y+b.max.y)*.5
for label,center,yaw in [('House_A_9Floors',(-2000,0),0),('House_B_9Floors',(2000,900),180)]:
    theta=math.radians(yaw)
    ox=factor*(cx*math.cos(theta)-cy*math.sin(theta))
    oy=factor*(cx*math.sin(theta)+cy*math.cos(theta))
    a=spawn(u.StaticMeshActor,label,(center[0]-ox,center[1]-oy,-factor*b.min.z),rot=(0,yaw,0),folder='District/Buildings')
    a.static_mesh_component.set_static_mesh(house)
    a.set_actor_scale3d(u.Vector(factor,factor,factor))
    # Separate simple collision envelope avoids modifying the shared imported mesh.
    box=slab(label+'_Collision',(center[0],center[1],1250),(1050,1600,2500),concrete,'District/Collision')
    box.set_actor_hidden_in_game(True)
    box.set_is_temporarily_hidden_in_editor(True)
report['building_scale']=factor
report['building_total_height_cm']=(b.max.z-b.min.z)*factor

# South parking: 12 bays, 2.5 x 5 m; open through lane south of the bays.
slab('Parking_12Bays',(-300,-1950,-4),(3000,500,10),asphalt)
for i in range(13):
    slab('ParkingStripe_%02d'%i,(-1800+i*250,-1950,2),(8,490,1),paint,'District/Markings')
slab('SouthSidewalk_1_8m',(0,-1610,7),(7100,180,16),concrete)
slab('WestSidewalk_1_8m',(-3410,200,7),(180,5500,16),concrete)
slab('EastWalk_1_8m',(3260,600,7),(180,6000,16),concrete)
slab('CourtyardWalk_NS_2m',(0,450,7),(200,3940,16),concrete)
slab('CourtyardWalk_WestDoor',(-1000,100,7),(1800,180,16),concrete)
slab('CourtyardWalk_EastDoor',(1000,1000,7),(1800,180,16),concrete)
slab('NorthWalk_1_8m',(0,2510,7),(6700,180,16),concrete)
# Curbs stop at walk entrances rather than blocking pedestrian routes.
for i,(x,length) in enumerate([(-2650,1800),(1850,3100)]):
    slab('SouthCurb_%d'%i,(x,-1708,6),(length,16,14),concrete)
for i in range(5):
    slab('CrossingStripe_%d'%i,(-3800,-1540+i*65,2),(580,35,1),paint,'District/Markings')

sun=spawn(u.DirectionalLight,'OvercastSun',(0,0,4000),(-52,-35,0),'District/Atmosphere')
sun.light_component.set_editor_property('intensity',3.0)
sun.light_component.set_editor_property('light_color',u.Color(205,216,230,255))
sun.light_component.set_editor_property('light_source_angle',6.0)
sun.light_component.set_mobility(u.ComponentMobility.MOVABLE)
sky=spawn(u.SkyLight,'OvercastSkylight',(0,0,1500),folder='District/Atmosphere')
sky.light_component.set_mobility(u.ComponentMobility.MOVABLE)
sky.light_component.set_editor_property('real_time_capture',True)
sky.light_component.set_editor_property('intensity',1.1)
spawn(u.SkyAtmosphere,'SkyAtmosphere',folder='District/Atmosphere')
spawn(u.VolumetricCloud,'OvercastClouds',(0,0,0),folder='District/Atmosphere')
fog=spawn(u.ExponentialHeightFog,'AutumnMist',folder='District/Atmosphere')
fog.component.set_editor_property('fog_density',.014)
fog.component.set_editor_property('fog_height_falloff',.2)
fog.component.set_editor_property('start_distance',1800.0)
pp=spawn(u.PostProcessVolume,'OvercastPostProcess',folder='District/Atmosphere')
pp.set_editor_property('unbound',True)
s=pp.get_editor_property('settings')
for key,value in [('override_auto_exposure_min_brightness',True),('override_auto_exposure_max_brightness',True),('auto_exposure_min_brightness',1.0),('auto_exposure_max_brightness',1.0),('override_bloom_intensity',True),('bloom_intensity',.15),('override_vignette_intensity',True),('vignette_intensity',.22)]:
    s.set_editor_property(key,value)
pp.set_editor_property('settings',s)
start=spawn(u.PlayerStart,'PlayerStart',(0,-1260,115),(0,90,0),'District/Gameplay')
gm=u.load_class(None,'/Game/FirstPerson/Blueprints/BP_FirstPersonGameMode.BP_FirstPersonGameMode_C')
WORLD.get_world_settings().set_editor_property('default_game_mode',gm)
u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(u.Vector(-6500,-7500,5200),u.Rotator(-27,49,0))
assert LS.save_current_level()
(ROOT/'Documentation').mkdir(exist_ok=True)
(ROOT/'Documentation/district-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('DISTRICT_BASE_COMPLETE '+json.dumps({'actors':len(report['created_actors']),'height_cm':report['building_total_height_cm']}))
