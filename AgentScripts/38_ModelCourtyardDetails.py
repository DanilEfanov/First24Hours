import bpy,pathlib,json,math,random
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'ArtSource/Prepared/district/kit'
def clear():bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,rgb):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);return m
def cube(loc,size,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
def tube(a,b,r,mat):
    a=Vector(a);b=Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat)
def geometry(name,verts,faces,mat):
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);m.materials.append(mat);return o
def save(name):
    bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='MESH')
    if len([o for o in bpy.context.scene.objects if o.type=='MESH'])>1:bpy.ops.object.join()
    o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',object_types={'MESH'},bake_anim=False)
    clear()
clear();yellow=material('District_FadedYellow',(.46,.34,.07));red=material('District_FadedRed',(.35,.07,.045));blue=material('District_FadedBlue',(.06,.15,.23));wood=material('District_WornWood',(.22,.12,.055))
for x in [-.55,.55]:
    for y in [-.55,.55]:tube((x,y,0),(x,y,2.35),.045,blue)
cube((0,0,1.25),(1.25,1.25,.09),wood)
for x in [-.58,.58]:tube((x,-.58,1.9),(x,.58,1.9),.025,yellow)
for y in [-.58,.58]:
    for x in [-.35,0,.35]:tube((x,y,1.30),(x,y,1.95),.015,yellow)
geometry('Roof',[(-.8,-.8,2.35),(.8,-.8,2.35),(0,-.8,2.95),(-.8,.8,2.35),(.8,.8,2.35),(0,.8,2.95)],[(0,2,5,3),(2,1,4,5),(0,1,2),(3,5,4)],red)
for x in [-.4,.4]:tube((x,-1.8,0),(x,-.58,1.25),.028,blue)
for i in range(6):
    t=(i+.5)/6;tube((-.4,-1.8+t*1.22,t*1.25),(.4,-1.8+t*1.22,t*1.25),.022,yellow)
track=[(.62,1.25),(1.0,1.15),(2.2,.35),(2.65,.15),(3.05,.15)]
verts=[]
for y,z in track:verts.extend([(-.34,y,z),(.34,y,z)])
geometry('SlideChute',verts,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(4)],yellow)
for x in [-.36,.36]:
    for i in range(4):tube((x,track[i][0],track[i][1]+.08),(x,track[i+1][0],track[i+1][1]+.08),.025,red)
save('SM_District_PlayTowerSlide')
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=1.05,depth=.12,location=(0,0,.25));bpy.context.object.data.materials.append(blue)
tube((0,0,0),(0,0,.9),.07,red)
for i in range(4):
    a=i*math.pi/2;x=.85*math.cos(a);y=.85*math.sin(a);tube((x,y,.3),(x,y,.9),.025,yellow);tube((0,0,.9),(x,y,.9),.025,yellow)
save('SM_District_Roundabout')
rng=random.Random(45);verts=[];faces=[]
for i in range(100):
    a=rng.uniform(0,2*math.pi);r=1.6*math.sqrt(rng.random());x=r*math.cos(a);y=r*math.sin(a);ang=rng.uniform(0,2*math.pi);length=rng.uniform(.06,.14);width=length*.45
    start=len(verts)
    for px,py,pz in [(0,0,.004),(length*.5,width,.007),(length,0,.004),(length*.5,-width,.007),(length*.5,0,.018)]:
        verts.append((x+px*math.cos(ang)-py*math.sin(ang),y+px*math.sin(ang)+py*math.cos(ang),pz))
    faces.extend([(start,start+1,start+4),(start+1,start+2,start+4),(start+2,start+3,start+4),(start+3,start,start+4)])
geometry('LeafPatch',verts,faces,material('District_LeafOchre',(.30,.13,.022)));save('SM_District_LeafPatch')
verts=[(0,0,0)]
for i in range(24):
    a=i*2*math.pi/24;r=1+rng.uniform(-.16,.16);verts.append((r*math.cos(a),r*.6*math.sin(a),0))
geometry('Puddle',verts,[(0,i+1,(i+1)%24+1) for i in range(24)],material('District_Puddle',(.016,.021,.025)));save('SM_District_Puddle')
print('COURTYARD_DETAIL_MESHES_READY')
