"""Reference-led four-sided housing block. Run only in L_ProceduralDistrict via MCP."""
import unreal as u,pathlib,json,math,random
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();MAP='/Game/First24Hours/Maps/L_ProceduralDistrict';BASE='/Game/First24Hours/District'
AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem);E=u.EditorAssetLibrary
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith(MAP+'.'),'Wrong map'
keep={'District_OvercastSun','District_OvercastSkylight','District_SkyAtmosphere','District_OvercastClouds','District_AutumnMist','District_OvercastPostProcess','District_Rain_Niagara','District_Rain_Ambience','District_OvercastSkyDome','District_PlayerStart'}
for a in AS.get_all_level_actors():
    if a.get_actor_label().startswith('District_') and a.get_actor_label() not in keep and not isinstance(a,u.PCGVolume):AS.destroy_actor(a)
actors={a.get_actor_label():a for a in AS.get_all_level_actors()}
count={};report={'reference':'ArtSource/References/Soviet Courtyard Architectural Reference Map.png','building_rows':[],'parking_bays':[],'tree_points':[],'bench_points':[],'bin_points':[],'lamp_points':[],'created':[]}
materials={name:u.load_asset(BASE+'/Materials/M_District_'+name) for name in ['WetAsphalt','DampConcrete','AutumnGround','WornRoadPaint']}
cube=u.load_asset('/Engine/BasicShapes/Cube')
house=u.load_asset('/Game/Assets/Environment/SovietApartmentBuilding/nine_story_building_of_the_post_soviet/StaticMeshes/nine_story_building_of_the_post_soviet')
def V(x,y,z=0):return u.Vector(x,y,z)
def spawn(cls,label,xyz=(0,0,0),yaw=0,folder='District'):
    count[label]=count.get(label,0)+1;name='District_'+label+'_%03d'%count[label]
    a=AS.spawn_actor_from_class(cls,V(*xyz),u.Rotator(pitch=0,yaw=yaw,roll=0));assert a,name
    a.set_actor_label(name);a.set_folder_path(folder);report['created'].append(name);return a
def mesh(label,asset,xyz,yaw=0,scale=1,folder='District/StreetFurniture',collision=False):
    a=spawn(u.StaticMeshActor,label,xyz,yaw,folder);c=a.static_mesh_component;c.set_static_mesh(asset)
    a.set_actor_scale3d(V(scale,scale,scale))
    c.set_collision_profile_name('BlockAll' if collision else 'NoCollision')
    if not collision:a.set_actor_enable_collision(False)
    return a
def slab(label,xyz,size,material,yaw=0,folder='District/Surfaces',collision=True):
    a=mesh(label,cube,xyz,yaw,1,folder,collision);a.set_actor_scale3d(V(*(n/100 for n in size)));a.static_mesh_component.set_material(0,material);return a
def kit(name):
    result=u.load_asset(BASE+'/Kit/Meshes/SM_District_'+name);assert result,name;return result
def rect_walk(label,x,y,length,width=180,yaw=0):return slab(label,(x,y,7),(length,width,16),materials['DampConcrete'],yaw,'District/PedestrianNetwork')
def segment(label,a,b,width=150,material=None,z=7):
    dx=b[0]-a[0];dy=b[1]-a[1]
    return slab(label,((a[0]+b[0])*.5,(a[1]+b[1])*.5,z),(math.hypot(dx,dy),width,16),material or materials['DampConcrete'],math.degrees(math.atan2(dy,dx)),'District/PedestrianNetwork')
def fence_line(a,b,gaps=()):
    dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);n=int(length/200);yaw=math.degrees(math.atan2(dy,dx))
    for i in range(n):
        t=(i+.5)/n;x=a[0]+dx*t;y=a[1]+dy*t
        if any(math.hypot(x-g[0],y-g[1])<g[2] for g in gaps):continue
        mesh('GardenFence',kit('GardenFence_2m'),(x,y,15),yaw,1,'District/GardenFences')
def light(label,xyz,intensity=900,radius=750):
    a=spawn(u.PointLight,label,xyz,folder='District/Lights');c=a.light_component
    c.set_mobility(u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS);c.set_editor_property('intensity',intensity)
    c.set_editor_property('light_color',u.Color(255,188,112,255));c.set_editor_property('attenuation_radius',radius);c.set_cast_shadows(False)
    return a
# The core follows the reference's approximately 120 x 90 m block. Ground extends under adjoining streets.
slab('DistrictGround',(0,0,-31),(23500,22000,60),materials['AutumnGround'])
footprint=house.get_bounding_box();cx=(footprint.min.x+footprint.max.x)/2;cy=(footprint.min.y+footprint.max.y)/2
scale=.8;section_length=(footprint.max.y-footprint.min.y)*scale-6
for row,n,center,yaw in [('North',4,(0,3800),90),('South',4,(0,-3800),-90),('West',3,(-4900,0),180),('East',3,(4900,0),0)]:
    positions=[]
    for i in range(n):
        offset=(i-(n-1)*.5)*section_length
        x=center[0]+(offset if row in ['North','South'] else 0);y=center[1]+(offset if row in ['West','East'] else 0)
        angle=math.radians(yaw);ox=scale*(cx*math.cos(angle)-cy*math.sin(angle));oy=scale*(cx*math.sin(angle)+cy*math.cos(angle))
        mesh('House_'+row+'_Section',house,(x-ox,y-oy,-footprint.min.z*scale),yaw,scale,'District/Buildings/'+row,True)
        positions.append([x,y])
        # Frontage path and entrance light connect every building section to the perimeter walk.
        if row in ['North','South']:
            sign=1 if row=='North' else -1
            segment('EntranceWalk',(x,sign*3200),(x,sign*2630),180)
            light('EntranceLight',(x,sign*3180,270),180,380)
        else:
            sign=1 if row=='East' else -1
            segment('EntranceWalk',(sign*4300,y),(sign*3930,y),180)
            light('EntranceLight',(sign*4280,y,270),180,380)
    report['building_rows'].append({'name':row,'sections':n,'section_centers_cm':positions,'height_cm':(footprint.max.z-footprint.min.z)*scale,'length_cm':section_length*n})
# Two neighbouring rows provide depth through the corner openings, with planned alignments.
for x,y,yaw in [(-8200,6500,0),(-8200,8300,0),(8200,6500,180),(8200,8300,180),(-1800,8200,90),(0,8200,90),(1800,8200,90)]:
    theta=math.radians(yaw);ox=scale*(cx*math.cos(theta)-cy*math.sin(theta));oy=scale*(cx*math.sin(theta)+cy*math.cos(theta))
    mesh('NeighbouringBlock',house,(x-ox,y-oy,-footprint.min.z*scale),yaw,scale,'District/Buildings/NeighbouringBlocks',True)
# Outer frontage sidewalks and the inner pedestrian rectangle are continuous networks.
for y in [-2630,2630]:rect_walk('FrontageSidewalk',0,y,7700,180)
for x in [-3930,3930]:rect_walk('FrontageSidewalk',x,0,5480,180,90)
for y in [-1130,1130]:rect_walk('InnerGardenWalk',0,y,4880,160)
for x in [-2440,2440]:rect_walk('InnerGardenWalk',x,0,2260,160,90)
rect_walk('CentralWalk_NS',-300,0,2260,160,90)
rect_walk('CentralWalk_EW',0,-900,4880,160)
for y in [-1570,1570]:segment('PedestrianRoadCrossing',(0,y),(0,math.copysign(2630,y)),180)
for x in [-3140,3140]:segment('PedestrianRoadCrossing',(x,0),(math.copysign(3930,x),0),180)
# Parking is on the inner side of the ring, leaving the driving lane clear.
for sign in [-1,1]:
    slab('ParkingNorthSouth',(0,sign*1540,-3),(5400,500,8),materials['WetAsphalt'])
    for i in range(22):
        x=-2625+i*250
        report['parking_bays'].append({'center':[x,sign*1540],'yaw':90 if sign<0 else -90})
    for i in range(23):
        x=-2750+i*250
        slab('ParkingBayStripe',(x,sign*1540,2),(7,490,1),materials['WornRoadPaint'],folder='District/RoadMarkings',collision=False)
for sign in [-1,1]:
    for i in range(9):
        y=-1000+i*250
        if abs(y)<160:continue
        slab('ParkingEastWest',(sign*2850,y,-3),(500,250,8),materials['WetAsphalt'])
        report['parking_bays'].append({'center':[sign*2850,y],'yaw':0 if sign<0 else 180})
        slab('ParkingBayStripe',(sign*2850,y-125,2),(490,7,1),materials['WornRoadPaint'],folder='District/RoadMarkings',collision=False)
# Deliberately leave every fourth bay vacant, with a few imperfectly parked cars.
rng=random.Random(20261026)
for i,bay in enumerate(report['parking_bays']):
    if i%4==0 or (abs(bay['center'][0])<200 and abs(bay['center'][1])>1300):continue
    model=[0,1,0,2,1,0,1][i%7];x,y=bay['center']
    mesh('ParkedVehicle',kit('Car_%02d'%model),(x+rng.uniform(-12,12),y+rng.uniform(-18,18),2),bay['yaw']+rng.uniform(-2,2),1,'District/Parking/Vehicles',True)
# Utility bay is separated from recreation and the main pedestrian route.
slab('UtilityBay',(-1700,100,5),(1100,1300,12),materials['DampConcrete'])
slab('UtilityBuilding',(-1700,350,155),(650,750,300),materials['DampConcrete'],folder='District/UtilityZone')
slab('UtilityRoof',(-1700,350,312),(690,790,20),materials['WetAsphalt'],folder='District/UtilityZone')
door_mat=u.load_asset(BASE+'/Kit/Materials/M_District_PaintedSteel')
slab('UtilityDoor',(-1700,-29,125),(105,5,220),door_mat,folder='District/UtilityZone')
for x in [-1940,-1870,-1800]:slab('UtilityVent',(x,-29,230),(45,5,35),door_mat,folder='District/UtilityZone')
mesh('WasteContainerBay',kit('BinEnclosure'),(-1800,-650,15),180,1,'District/UtilityZone',True)
# Recreation court is a purpose-built 17 x 15 m space with connected access paths.
slab('PlaygroundBase',(1200,50,3),(1850,1550,8),materials['AutumnGround'],folder='District/Recreation')
mesh('PlaygroundSwing',kit('Swing'),(1300,430,9),0,1,'District/Recreation',True)
mesh('PlaygroundSandpit',kit('Sandpit'),(1050,-380,9),0,1,'District/Recreation',True)
segment('PlaygroundAccess',(-300,-900),(500,-650),150)
segment('PlaygroundAccess',(1600,900),(1600,1130),150)
for p,yaw in [((350,780),0),((2100,780),0),((2100,-720),180),((450,-720),180),((-800,-900),90),((-800,950),-90),((-2200,-850),0),((-2200,1000),180),((-3500,1800),90),((3500,1800),-90)]:
    report['bench_points'].append([p[0],p[1],15,yaw])
    report['bin_points'].append([p[0]+130,p[1],15,0])
# Front gardens have openings aligned to entrances; the play court has two gates.
for sign in [-1,1]:
    fence_line((-3550,sign*2840),(3550,sign*2840),[(x,sign*2840,130) for x in [-2728,-909,909,2728]])
    fence_line((sign*4100,-2500),(sign*4100,2500),[(sign*4100,y,130) for y in [-1819,0,1819]])
fence_line((250,-750),(2150,-750),[(550,-750,150)])
fence_line((250,850),(2150,850),[(1600,850,150)])
fence_line((2200,-750),(2200,850));fence_line((200,-750),(200,850))
# Crossings sit on the road, with narrow interruptions in curbs.
for sign in [-1,1]:
    for i in range(6):
        slab('ZebraStripe',(0,sign*2150+(i-2.5)*75,2),(220,35,1),materials['WornRoadPaint'],folder='District/RoadMarkings',collision=False)
        slab('ZebraStripe',(sign*3450+(i-2.5)*75,0,2),(35,220,1),materials['WornRoadPaint'],folder='District/RoadMarkings',collision=False)
    for x,length in [(-2025,3750),(2025,3750)]:slab('OuterCurb',(x,sign*2490,7),(length,18,15),materials['DampConcrete'],folder='District/Curbs')
    for y,length in [(-1450,2600),(1450,2600)]:slab('OuterCurb',(sign*3790,y,7),(18,length,15),materials['DampConcrete'],folder='District/Curbs')
# Lamp positions follow circulation and playground edges.
for x,y in [(-3650,-2450),(-3650,800),(-3650,2450),(3650,-2450),(3650,800),(3650,2450),(-1800,-2550),(1800,-2550),(-1800,2550),(1800,2550),(-600,-800),(-600,900),(2250,-800),(2250,900)]:
    report['lamp_points'].append([x,y,15,180 if x>0 else 0])
    mesh('StreetLamp',kit('StreetLamp_5m'),(x,y,15),180 if x>0 else 0,1,'District/StreetLights',True)
    light('StreetLightPool',(x,y+(-92 if x>0 else 92),510),900,850)
# Canopies form frontage rows and shade the recreation court. No uniform random field.
for sign in [-1,1]:
    for x in [-3300,-2100,-1000,1000,2100,3300]:report['tree_points'].append([x,sign*2970,8])
    for y in [-2300,-1200,1000,2300]:report['tree_points'].append([sign*4120,y,8])
for x,y in [(-2200,940),(-1100,960),(-1100,-850),(-2200,-950),(-650,450),(-650,-400),(2250,300),(2200,-500),(1650,1000),(500,1000),(500,-1050),(1750,-1050),(-3000,2900),(3000,2900)]:report['tree_points'].append([x,y,8])
for sign in [-1,1]:
    for y in [-3900,-2400,-800,900,2500,3900]:report['tree_points'].append([sign*5600,y,8])
    for x in [-3800,-2400,-900,900,2400,3800]:report['tree_points'].append([x,sign*4600,8])
# Save spline control data for the MCP PCG pass.
road=[]
for cxr,cyr,a0 in [(2900,1600,0),(-2900,1600,90),(-2900,-1600,180),(2900,-1600,270)]:
    for step in range(5):
        a=math.radians(a0+step*22.5);road.append([cxr+550*math.cos(a),cyr+550*math.sin(a),0])
report['road_points']=road
report['outer_road_points']=[[-6200,-5000,0],[6200,-5000,0],[6200,5000,0],[-6200,5000,0]]
report['entry_road_points']=[[-6600,-2950,0],[-4300,-2950,0],[-3850,-2600,0],[-3450,-1600,0]]
actors['District_PlayerStart'].set_actor_location(V(-300,-900,125),False,False)
actors['District_PlayerStart'].set_actor_rotation(u.Rotator(pitch=0,yaw=65,roll=0),False)
actors['District_Rain_Niagara'].set_actor_location(V(0,0,1050),False,False)
for a in AS.get_all_level_actors():
    if isinstance(a,u.PCGVolume):a.set_folder_path('District/Procedural')
AS.clear_actor_selection_set()
assert LS.save_current_level()
(ROOT/'Documentation/district-reference-layout.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(V(0,-10200,9500),u.Rotator(pitch=-48,yaw=90,roll=0))
u.log('DISTRICT_REFERENCE_LAYOUT_BUILT '+json.dumps({'housing_sections':14,'parking_bays':len(report['parking_bays']),'tree_anchors':len(report['tree_points']),'created':len(report['created'])}))
