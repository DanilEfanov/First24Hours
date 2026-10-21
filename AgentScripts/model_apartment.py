"""Build original bevelled apartment meshes and prepare CC0 props in Blender 5."""
import bpy, math, json, pathlib, random
from mathutils import Vector
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT/'ArtSource/Prepared'; OUT.mkdir(exist_ok=True)
random.seed(2026)
manifest = {'materials': {}, 'meshes': []}
PALETTE = {
 'Plaster':([.73,.70,.62],.85,'painted_plaster_wall'),
 'Parquet':([.3,.19,.10],.65,'wood_floor_worn'),
 'Tile':([.55,.58,.56],.55,'floor_tiles_04'),
 'Fabric':([.24,.29,.30],.9,'fabric_pattern_05'),
 'Ceiling':([.78,.77,.71],.9,None), 'Trim':([.64,.59,.48],.5,None),
 'Walnut':([.14,.075,.035],.5,'wood_floor_worn'),
 'Sage':([.23,.30,.24],.57,None), 'Countertop':([.52,.49,.41],.35,None),
 'Porcelain':([.75,.76,.70],.22,None), 'Chrome':([.55,.58,.6],.16,None),
 'Black':([.015,.02,.025],.42,None), 'Brass':([.35,.23,.08],.3,None),
 'Linen':([.55,.48,.35],.95,'fabric_pattern_05'), 'Curtain':([.34,.37,.34],.9,None),
 'Screen':([.035,.11,.19],.3,None), 'WarmGlow':([1,.47,.14],.3,None),
 'Glass':([.13,.21,.25],.08,None), 'Rain':([.35,.55,.65],.15,None),
 'CityConcrete':([.09,.11,.14],.85,None), 'CityWindow':([.28,.18,.075],.3,None)
}
MATS = {}
for name,(color,rough,texture) in PALETTE.items():
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); MATS[name]=m
    manifest['materials'][name]={'color':color,'roughness':rough,'texture_set':texture,
                                'metallic':1 if name in ['Chrome','Brass'] else 0,
                                'emissive':3 if name in ['Screen','WarmGlow','CityWindow'] else 0,
                                'translucent':name in ['Glass','Rain']}
def clear():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def finish(obj, mat):
    obj.data.materials.append(MATS[mat]); return obj
def box(name, pos, size, mat, bevel=.4):
    bpy.ops.mesh.primitive_cube_add(size=1,location=[v/100 for v in pos]); o=bpy.context.object; o.name=name
    o.dimensions=[v/100 for v in size]; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Manufactured_edges','BEVEL'); mod.width=bevel/100; mod.segments=3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return finish(o,mat)
def sphere(name,pos,size,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=[v/100 for v in pos]); o=bpy.context.object; o.name=name
    o.dimensions=[v/100 for v in size]; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in o.data.polygons:p.use_smooth=True
    return finish(o,mat)
def tube(name,pos,radius,depth,mat,axis='Z'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius/100,depth=depth/100,location=[v/100 for v in pos]); o=bpy.context.object;o.name=name
    if axis=='X':o.rotation_euler[1]=math.pi/2
    if axis=='Y':o.rotation_euler[0]=math.pi/2
    mod=o.modifiers.new('Edge','BEVEL'); mod.width=.002;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in o.data.polygons:p.use_smooth=True
    return finish(o,mat)
def ring(name,pos,major,minor,mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=10,location=[v/100 for v in pos],major_radius=major/100,minor_radius=minor/100)
    o=bpy.context.object;o.name=name;return finish(o,mat)
def uv_world(o):
    layer=o.data.uv_layers.active or o.data.uv_layers.new()
    for p in o.data.polygons:
        axis=max(range(3),key=lambda i:abs(p.normal[i])); axes=[i for i in range(3) if i!=axis]
        for li in p.loop_indices:
            v=o.matrix_world @ o.data.vertices[o.data.loops[li].vertex_index].co
            layer.data[li].uv=(v[axes[0]]/2,v[axes[1]]/2)
def export_group(name, category, center=False, uv=True):
    objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
    if uv:
        for o in objs:uv_world(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
    if center:
        points=[o.matrix_world@Vector(c) for c in o.bound_box]
        low=Vector([min(v[i] for v in points) for i in range(3)]); high=Vector([max(v[i] for v in points) for i in range(3)])
        shift=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
        o.location-=shift
    bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    path=OUT/(name+'.fbx')
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,path_mode='ABSOLUTE')
    bounds=[max(v.co[i] for v in o.data.vertices)-min(v.co[i] for v in o.data.vertices) for i in range(3)]
    manifest['meshes'].append({'name':name,'file':str(path),'category':category,'slots':[m.name for m in o.data.materials], 'size_m':bounds})
    print('Exported',name,tuple(round(x,2) for x in bounds),flush=True)
    clear()

clear(); bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
# Floor finish separated by room; continuous slab underneath prevents seams.
box('Slab',(390,290,-9),(804,604,18),'Ceiling',.2)
box('LivingParquet',(490,440,0),(580,280,1.5),'Parquet',.05)
box('SleepingParquet',(630,150,0),(300,300,1.5),'Parquet',.05)
box('KitchenFloor',(340,150,0),(280,300,1.5),'Tile',.05)
box('HallFloor',(100,390,0),(200,380,1.5),'Parquet',.05)
box('BathFloor',(100,100,.5),(200,200,2),'Tile',.05)
export_group('SM_Apartment_Floors','Architecture')
# Solid walls around explicit openings (all dimensions cm).
def wall_y(x0,x1,y,z0=0,z1=270,thick=16):
    if x1>x0:box('Wall',((x0+x1)/2,y,(z0+z1)/2),(x1-x0,thick,z1-z0),'Plaster',.15)
def wall_x(y0,y1,x,z0=0,z1=270,thick=16):
    if y1>y0:box('Wall',(x,(y0+y1)/2,(z0+z1)/2),(thick,y1-y0,z1-z0),'Plaster',.15)
wall_y(-8,380,588);wall_y(650,788,588);wall_y(380,650,588,0,85);wall_y(380,650,588,235,270)
wall_y(-8,260,-8);wall_y(430,788,-8);wall_y(260,430,-8,0,100);wall_y(260,430,-8,235,270)
wall_x(0,395,-8);wall_x(485,580,-8);wall_x(395,485,-8,210,270)
wall_x(0,70,788);wall_x(230,580,788);wall_x(70,230,788,0,85);wall_x(70,230,788,235,270)
wall_x(0,210,200,thick=12);wall_x(295,430,200,thick=12);wall_x(530,580,200,thick=12)
wall_x(210,295,200,210,270,12);wall_x(430,530,200,220,270,12)
wall_y(0,65,200,thick=12);wall_y(155,200,200,thick=12);wall_y(65,155,200,210,270,12)
wall_y(200,480,300,thick=12);wall_y(480,555,300,thick=12);wall_y(705,780,300,thick=12);wall_y(555,705,300,235,270,12)
wall_x(0,300,480,thick=12)
export_group('SM_Apartment_Walls','Architecture')
box('Ceiling',(390,290,279),(804,604,18),'Ceiling',.2);export_group('SM_Apartment_Ceiling','Architecture')
# Skirting, cornices, door casing, brass threshold strips.
for y in [4,576]:box('Skirting',(390,y,4),(776,2,8),'Trim',.3)
for x in [4,776]:box('Skirting',(x,290,4),(2,576,8),'Trim',.3)
for y in [4,576]:box('Cornice',(390,y,261),(776,6,10),'Ceiling',.6)
for x in [4,776]:box('Cornice',(x,290,261),(6,576,10),'Ceiling',.6)
for y0,y1 in [(0,210),(295,430),(530,580)]:
    for x in [192,208]:box('InternalSkirting',(x,(y0+y1)/2,4),(2,y1-y0,8),'Trim',.2)
for x,y,w,axis in [(0,440,90,'X'),(200,252.5,85,'X'),(200,480,100,'X'),(110,200,90,'Y')]:
    for sign in [-1,1]:
        pos=(x,y+sign*(w/2+3),108) if axis=='X' else (x+sign*(w/2+3),y,108)
        box('DoorCasing',pos,(19,7,216) if axis=='X' else (7,19,216),'Trim',.8)
    box('DoorLintel',(x,y,215),(19,w+14,10) if axis=='X' else (w+14,19,10),'Trim',.8)
export_group('SM_Apartment_Joinery','Architecture')
# Main entrance door: layered panels, hinges, peephole, handle and lock.
box('SecurityDoor',(-6,440,104),(7,86,208),'Walnut',.8)
for y in [417,463]:box('DoorPanel',(-1.8,y,108),(2,34,170),'Walnut',.6)
tube('DoorHandle',(.5,467,100),1,13,'Brass','Y');tube('Peephole',(-.8,440,157),1,8,'Brass','X')
box('Lock',(0,468,85),(3,5,9),'Brass',.5)
export_group('SM_Entry_Door','Architecture')
# PVC windows with reveals, mullions, sills and opening handles.
for x,y,w,h,axis in [(515,588,270,150,'Y'),(345,-8,170,135,'Y'),(788,150,160,150,'X')]:
    sill=85 if axis=='X' or y>0 else 100
    for u in [-w/2,0,w/2]:
        pos=(x+u,y,sill+h/2) if axis=='Y' else (x,y+u,sill+h/2)
        box('PVCMullion',pos,(5,12,h+6) if axis=='Y' else (12,5,h+6),'Porcelain',.45)
    for z in [sill,sill+h]:box('PVCFrame',(x,y,z),(w+8,12,6) if axis=='Y' else (12,w+8,6),'Porcelain',.5)
    box('WindowSill',(x,y-8 if y>0 else y+8,sill-2),(w+26,32,4) if axis=='Y' else (32,w+26,4),'Countertop',.6)
export_group('SM_Apartment_WindowFrames','Architecture')
for pos,size in [((515,588,160),(264,1,144)),((345,-8,167.5),(164,1,129)),((788,150,160),(1,154,144))]:box('Glazing',pos,size,'Glass',0)
export_group('SM_Apartment_Glass','Architecture')
# Radiators, outlets, switches, ceiling fixtures.
for x,y in [(515,568),(345,12)]:
    for j in range(14):box('RadiatorFin',(x-52+j*8,y,40),(6,12,58),'Porcelain',1.8)
    for z in [16,64]:tube('RadiatorPipe',(x,y,z),1.6,125,'Porcelain','X')
for pos,size in [((195,390,110),(3,8,12)),((195,340,28),(3,12,8)),((776,430,28),(3,12,8))]:box('SwitchSocket',pos,size,'Porcelain',.8)
for x,y in [(100,440),(350,170),(480,440),(100,110)]:
    tube('CeilingMount',(x,y,263),13,4,'Chrome');sphere('FrostedShade',(x,y,254),(28,28,15),'Porcelain')
export_group('SM_Apartment_Fixtures','Details')
# Kitchen: manufactured carcasses, framed fronts, plinth and handles.
for x in [240,300,360,420]:
    box('KitchenCarcass',(x,36,46),(58,58,84),'Sage',1)
    box('DoorFront',(x,67,46),(54,3,72),'Sage',.7)
    tube('Pull',(x,70,70),.7,18,'Brass','X')
    box('UpperCabinet',(x,20,199),(58,37,74),'Sage',1)
    box('UpperFront',(x,40,199),(54,3,70),'Sage',.8)
    tube('UpperPull',(x+19,43,183),.65,16,'Brass')
box('Plinth',(330,39,6),(236,44,12),'Black',.4)
box('Counter',(330,36,90),(244,66,5),'Countertop',1)
box('Splashback',(330,4,121),(244,2,60),'Tile',.15)
# Basin represented by metal rim and recessed dark inner bowl.
box('SinkRim',(248,35,93),(49,43,2),'Chrome',4)
box('SinkBowl',(248,35,93.8),(40,34,1),'Black',5)
tube('TapStem',(248,9,107),1.3,30,'Chrome');tube('TapSpout',(248,20,121),1.3,24,'Chrome','Y')
box('Cooker',(364,35,94),(56,53,3),'Black',1)
for x in [351,377]:
    for y in [23,47]:ring('Burner',(x,y,96),8,.7,'Chrome')
box('OvenGlass',(364,69,43),(47,2,44),'Black',2);tube('OvenHandle',(364,72,65),.8,41,'Chrome','X')
for x in [347,359,371,383]:tube('ControlKnob',(x,71,78),2.2,2,'Black','Y')
# Fridge against eastern kitchen partition, door towards room.
box('Fridge',(442,171,91),(60,65,182),'Porcelain',2)
for z,h in [(59,107),(146,60)]:
    box('FridgeFront',(442,205,z),(56,3,h),'Porcelain',1)
    tube('FridgeHandle',(465,209,z+10),1,24,'Chrome')
export_group('SM_Kitchen_Fitted','Furniture')
# Bathroom: tub shell, toilet bowl/tank, sink vanity, mirror, towel rail.
box('BathApron',(105,43,27),(170,77,54),'Porcelain',8)
box('TubRecess',(105,43,54),(150,60,2),'Sage',14)
for x in [19,191]:box('TubEnd',(x,43,57),(8,78,8),'Porcelain',3)
for y in [7,79]:box('TubRim',(105,y,57),(174,7,8),'Porcelain',2)
tube('ShowerPipe',(177,5,150),1,145,'Chrome');tube('ShowerHead',(177,18,220),8,2,'Chrome')
sphere('ToiletBowl',(48,140,36),(44,64,38),'Porcelain');sphere('ToiletSeat',(48,145,51),(45,59,7),'Porcelain')
sphere('ToiletInset',(48,150,54),(29,40,2),'Black');box('Tank',(48,112,67),(43,19,40),'Porcelain',3)
box('Vanity',(175,145,39),(42,60,77),'Sage',1.5)
sphere('Washbasin',(175,145,81),(45,55,12),'Porcelain');sphere('BasinInset',(175,145,85),(32,36,2),'Sage')
tube('BasinTap',(187,150,91),1.1,25,'Chrome');tube('BasinSpout',(180,150,103),1.1,18,'Chrome','X')
box('MirrorFrame',(194,149,155),(3,66,86),'Walnut',2);box('Mirror',(191.8,149,155),(1,58,78),'Chrome',.5)
for z in [90,110,130]:tube('TowelRail',(5,125,z),1.1,60,'Chrome','Y')
box('Towel',(9,128,104),(3,42,50),'Linen',1)
export_group('SM_Bathroom_Fitted','Furniture')
# A believable low bed with upholstered headboard, mattress and layered bedding.
box('BedBase',(630,137,25),(154,213,34),'Walnut',3)
box('Headboard',(630,29,62),(160,10,100),'Fabric',4)
box('Mattress',(630,137,49),(148,200,22),'Linen',8)
box('Duvet',(630,161,63),(145,151,15),'Fabric',7)
for x in [594,665]:box('Pillow',(x,61,68),(62,43,16),'Linen',7)
box('FoldedThrow',(630,218,72),(150,35,7),'Linen',3)
for x in [563,697]:
    for y in [47,226]:tube('BedLeg',(x,y,9),3,18,'Black')
box('Nightstand',(739,65,30),(42,43,60),'Walnut',1.5)
box('NightDrawer',(739,88,42),(37,3,26),'Walnut',.6);tube('DrawerPull',(739,91,42),.65,13,'Brass','X')
export_group('SM_Bed_and_Nightstand','Furniture')
# Hall storage, student desk equipment and domestic clutter.
box('ShoeCabinet',(33,300,48),(48,100,96),'Walnut',1.2)
for z in [25,57,88]:box('ShoeFront',(59,300,z),(3,94,27),'Walnut',.4)
box('HallMirror',(9,310,162),(3,63,96),'Chrome',1)
box('CoatBoard',(190,365,170),(4,60,12),'Walnut',1)
for y in [345,365,385]:tube('CoatHook',(185,y,166),1,12,'Brass','X')
box('Wardrobe',(737,369,115),(70,105,230),'Walnut',2)
for y in [343,395]:box('WardrobeDoor',(700,y,115),(3,49,222),'Walnut',1);tube('WardrobePull',(696,y,113),.7,26,'Brass')
# Laptop/monitor/work objects can be moved independently by editing this source later.
box('MonitorStand',(690,541,79),(24,18,2),'Black',1);tube('MonitorArm',(690,548,96),2,35,'Black')
box('Monitor',(690,548,112),(52,4,32),'Black',1.4);box('Display',(690,545.7,112),(48,1,28),'Screen',.4)
box('Keyboard',(690,523,80),(40,15,2),'Black',.6)
for i in range(12):
    for j in range(3):box('Key',(673+i*3,519+j*4,81.2),(2.3,2.8,.7),'Black',.18)
box('Mouse',(722,525,81),(7,11,3),'Black',2)
for i in range(3):box('Notebook',(663+i*2,520-i*3,83+i*2),(18,25,1.5),'Linen',.2)
for x,y,z in [(290,45,98),(675,530,86)]:
    tube('Mug',(x,y,z),4,9,'Porcelain');ring('MugHandle',(x+5,y,z),3,.7,'Porcelain')
for y in [42,48]:tube('Plate',(315,y,95),11,1,'Porcelain')
export_group('SM_Apartment_LivedIn_Details','Details')
# Curtains and a rug: thin folded mesh, not blocking walking space.
for x0 in [374,650]:
    for i in range(8):
        x=x0+i*3.5
        box('CurtainFold',(x,574+math.sin(i*1.7)*3,138),(5,2,242),'Curtain',1)
tube('CurtainRod',(530,566,263),1.3,330,'Brass','X')
box('LivingRug',(444,438,1.7),(200,160,1),'Fabric',.5)
box('EntryMat',(78,439,1.8),(62,100,1.5),'Fabric',.5)
export_group('SM_Apartment_Textiles','Details')
# Original distant buildings: no dependency on unverified third-party licenses.
for bx,by,w,depth,height in [(-400,2800,900,500,2900),(900,3400,1500,600,3000),(2200,800,700,1100,2700),(-700,-2400,1300,550,2900)]:
    box('PanelBuilding',(bx,by,height/2-1700),(w,depth,height),'CityConcrete',1)
    for floor in range(9):
        for col in range(int(w/150)):
            x=bx-w/2+80+col*150;z=-1600+floor*300
            box('Window',(x,by-depth/2-2,z),(65,3,100),'CityWindow' if random.random()<.13 else 'Black',0)
    for floor in range(9):box('PanelSeam',(bx,by-depth/2-4,-1700+floor*300),(w,2,4),'Black',0)
export_group('SM_City_Backdrop','Exterior')
# Moving rain is shaded in Unreal; cards are outside all three windows.
for pos,size in [((515,615,153),(290,.2,300)),((345,-35,153),(190,.2,300)),((815,150,153),(.2,190,300))]:box('RainCurtain',pos,size,'Rain',0)
export_group('SM_Window_Rain','Exterior')
# Convert downloaded, texture-preserving glTF props to normalized FBX meshes.
for asset in ['sofa_02','SchoolDesk_01','painted_wooden_chair_02','desk_lamp_arm_01','book_encyclopedia_set_01','alarm_clock_01','vintage_electric_kettle']:
    gltf=ROOT/'ArtSource/Models'/asset/(asset+'.gltf')
    data=json.loads(gltf.read_text());bpy.ops.import_scene.gltf(filepath=str(gltf))
    for index,desc in enumerate(data.get('materials',[])):
        name=desc.get('name',asset+'_'+str(index));definition={'color':[.5,.5,.5],'roughness':.6,'metallic':0}
        def image_path(info):
            if not info:return None
            tex=data['textures'][info['index']];uri=data['images'][tex['source']]['uri']
            return str(gltf.parent/uri)
        pbr=desc.get('pbrMetallicRoughness',{})
        definition['diffuse']=image_path(pbr.get('baseColorTexture'))
        definition['normal']=image_path(desc.get('normalTexture'))
        definition['arm']=image_path(pbr.get('metallicRoughnessTexture'))
        definition['normal_gl']=True
        manifest['materials'][name]=definition
    export_group('SM_PH_'+asset,'PolyHaven',center=True,uv=False)
(OUT/'apartment-manifest.json').write_text(json.dumps(manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Apartment_Source.blend'))
print('FIRST24_BLENDER_COMPLETE',len(manifest['meshes']),flush=True)
