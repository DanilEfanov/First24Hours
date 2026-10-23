"""Original street furniture, source-derived housing sections, individual cars."""
import bpy,bmesh,pathlib,json,math
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'ArtSource/Prepared/district/kit';OUT.mkdir(parents=True,exist_ok=True)
MANIFEST={'assets':[],'car_parts':[],'building_derivation':'Adapted from existing CC BY 4.0 source; lower body retained, roof lowered, adjoining sections form a continuous row.'}
def clear():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,rgb,metal=0,rough=.6):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    return m
steel=mat('District_PaintedSteel',(.08,.13,.10),.65,.45)
rust=mat('District_RustedSteel',(.14,.08,.04),.65,.7)
wood=mat('District_WornWood',(.22,.12,.055),0,.73)
yellow=mat('District_FadedYellow',(.46,.34,.07),.25,.6)
red=mat('District_FadedRed',(.35,.07,.045),.2,.55)
blue=mat('District_FadedBlue',(.06,.15,.23),.25,.55)
stone=mat('District_Concrete',(.27,.27,.25),0,.8)
glow=mat('District_LampGlass',(.95,.60,.26),0,.3)
def box(name,loc,size,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('SmallEdgeBevel','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(m);return o
def tube(name,a,b,r,m,vertices=12):
    a=Vector(a);b=Vector(b);d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)*.5)
    o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def finish(name,origin=(0,0,0),source='authored'):
    bpy.ops.object.select_all(action='DESELECT')
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    if len(objects)>1:bpy.ops.object.join()
    o=bpy.context.object;o.name=name
    bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',object_types={'MESH'},bake_anim=False)
    MANIFEST['assets'].append({'name':name,'materials':[m.name for m in o.data.materials],'source':source,'dimensions_m':list(o.dimensions)})
    clear()
clear()
# 2m garden fence: posts and diagonals; appropriate to the reference photos.
for x in [-1,1]:tube('Post',(x,0,0),(x,0,.85),.025,steel)
for z in [.23,.75]:tube('Rail',(-1,0,z),(1,0,z),.02,steel)
tube('Diagonal',(-1,0,.23),(0,0,.75),.012,yellow);tube('Diagonal',(0,0,.75),(1,0,.23),.012,yellow)
finish('SM_District_GardenFence_2m')
# Bench with wooden slats and steel feet, backrest facing local +Y.
for x in [-.66,.66]:
    for y in [-.20,.20]:tube('Leg',(x,y,0),(x,y,.47),.025,steel)
    tube('Support',(x,-.25,.43),(x,.27,.43),.025,steel)
    tube('BackFrame',(x,.23,.4),(x,.36,.95),.025,steel)
for y in [-.20,-.10,0,.10,.20]:box('SeatSlat',(0,y,.48),(1.8,.085,.035),wood,.009)
for z in [.65,.79,.93]:
    o=box('BackSlat',(0,.25+(z-.48)*.24,z),(1.8,.035,.105),wood,.009);o.rotation_euler.x=math.radians(-13)
finish('SM_District_Bench_180cm')
# Open steel litter bin with lip and recessed mouth.
bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.23,depth=.58,location=(0,0,.44));o=bpy.context.object;o.data.materials.append(steel)
bpy.ops.mesh.primitive_torus_add(major_radius=.23,minor_radius=.022,major_segments=20,minor_segments=8,location=(0,0,.75));bpy.context.object.data.materials.append(rust)
box('DarkMouth',(0,0,.743),(.34,.34,.015),mat('District_BinInterior',(.012,.014,.012),0,.9),.04)
for x in [-.27,.27]:tube('BinStand',(x,0,0),(x,0,.63),.022,steel)
finish('SM_District_LitterBin')
# 5m lamp, flanged base, curved arm approximated with short continuous tubes.
bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.075,radius2=.04,depth=5,location=(0,0,2.5));bpy.context.object.data.materials.append(steel)
box('BaseFlange',(0,0,.035),(.30,.30,.07),steel,.015)
for x in [-.10,.10]:
    for y in [-.10,.10]:tube('AnchorBolt',(x,y,.05),(x,y,.09),.014,rust,8)
for a,b in [((0,0,4.6),(0,.12,4.92)),((0,.12,4.92),(0,.38,5.08)),((0,.38,5.08),(0,.78,5.08))]:tube('LampArm',a,b,.035,steel)
box('LampHood',(0,.92,5.04),(.34,.55,.12),steel,.045)
box('LampLens',(0,.92,4.969),(.27,.44,.018),glow,.025)
finish('SM_District_StreetLamp_5m')
# Sandpit and swing are distinct purpose-made assets, not building substitutes.
for x in [-1.5,1.5]:box('SandpitEdge',(x,0,.18),(.16,3.1,.27),wood,.02)
for y in [-1.5,1.5]:box('SandpitEdge',(0,y,.18),(3.1,.16,.27),wood,.02)
box('Sand',(0,0,.08),(2.9,2.9,.12),mat('District_Sand',(.38,.32,.19)),.01)
finish('SM_District_Sandpit')
for x in [-1.5,1.5]:
    tube('SwingAFrame',(x,-.85,0),(x,0,2.4),.045,yellow)
    tube('SwingAFrame',(x,.85,0),(x,0,2.4),.045,yellow)
    tube('Brace',(x,-.65,.55),(x,.65,.55),.025,red)
tube('TopBar',(-1.7,0,2.4),(1.7,0,2.4),.045,red)
for x in [-.65,.65]:
    for dx in [-.23,.23]:tube('Chain',(x+dx,0,2.35),(x+dx,0,.55),.008,rust,6)
    box('Seat',(x,0,.55),(.60,.30,.06),wood,.018)
finish('SM_District_Swing')
# Utility service enclosure with two green waste containers.
for x in [-1.4,1.4]:box('Screen',(x,0,1),(.08,2.6,2),steel,.012)
box('Screen',(0,1.3,1),(2.9,.08,2),steel,.012)
for x in [-.65,.65]:
    box('WasteContainer',(x,0,.62),(1.05,.85,1.05),steel,.06)
    box('ContainerLid',(x,0,1.18),(1.10,.91,.09),steel,.025)
    for y in [-.35,.35]:tube('Wheel',(x-.4,y,.12),(x+.4,y,.12),.10,mat('District_Rubber',(.016,.018,.017)),10)
finish('SM_District_BinEnclosure')
# Source-derived lower building section. Preserve original slots/UVs; no stretching of floors.
bpy.ops.import_scene.fbx(filepath=str(ROOT/'ArtSource/Prepared/district/source/House.fbx'))
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and o.name.startswith('UCX_'):bpy.data.objects.remove(o,do_unlink=True)
o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.context.view_layer.objects.active=o;o.select_set(True)
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
bm=bmesh.new();bm.from_mesh(o.data)
# Flat cut above the fifth residential tier; remove upper floors and add a new roof slab later in UE.
cut=17.5
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=(0,0,cut),plane_no=(0,0,1),clear_outer=True,clear_inner=False)
bm.to_mesh(o.data);bm.free();o.data.update()
minimum=Vector((min(v.co.x for v in o.data.vertices),min(v.co.y for v in o.data.vertices),min(v.co.z for v in o.data.vertices)))
maximum=Vector((max(v.co.x for v in o.data.vertices),max(v.co.y for v in o.data.vertices),max(v.co.z for v in o.data.vertices)))
center=(minimum+maximum)*.5
for v in o.data.vertices:v.co.x-=center.x;v.co.y-=center.y;v.co.z-=minimum.z
finish('SM_District_LowriseSection',source='House')
# Split the vehicle pack by spatial placement. Disconnected wheels/glass stay with their car.
bpy.ops.import_scene.fbx(filepath=str(ROOT/'ArtSource/Prepared/district/source/Cars.fbx'))
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and o.name.startswith('UCX_'):bpy.data.objects.remove(o,do_unlink=True)
o=next(o for o in bpy.context.scene.objects if o.type=='MESH')
coords=[v.co for v in o.data.vertices]
MANIFEST['car_bounds']={'min':[min(v[k] for v in coords) for k in range(3)],'max':[max(v[k] for v in coords) for k in range(3)]}
# Inspect connected components in a sidecar; extraction is driven by component bounding boxes.
bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
seen=set();groups=[]
for v in bm.verts:
    if v.index in seen:continue
    stack=[v];seen.add(v.index);group=[]
    while stack:
        cur=stack.pop();group.append(cur.index)
        for e in cur.link_edges:
            other=e.other_vert(cur)
            if other.index not in seen:seen.add(other.index);stack.append(other)
    points=[bm.verts[i].co for i in group]
    groups.append({'indices':group,'count':len(group),'min':[min(p[k] for p in points) for k in range(3)],'max':[max(p[k] for p in points) for k in range(3)]})
bm.free()
(OUT/'car-components.json').write_text(json.dumps(groups))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Cars_Extraction.blend'))
(OUT/'kit-manifest.json').write_text(json.dumps(MANIFEST,indent=2))
print('COURTYARD_KIT_READY',len(MANIFEST['assets']),'car components',len(groups),flush=True)
