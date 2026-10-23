import unreal as u,pathlib,json,math
from editor_toolset.toolsets.material import MaterialTools
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours/District';E=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools();ML=u.MaterialEditingLibrary
AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/First24Hours/Maps/L_ProceduralDistrict.')
src=(ROOT/'AgentScripts/45_ApplyReferenceSurfaces.py').read_text();exec(src[src.index('def ex('):src.index('for source,target,')])
mn='M_District_OccupiedWindow';mat=u.load_asset(BASE+'/Materials/'+mn)
if not mat:mat=AT.create_asset(mn,BASE+'/Materials',u.Material,u.MaterialFactoryNew())
ML.delete_all_material_expressions(mat);mat.set_editor_property('two_sided',True)
color=ex(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(1.6,.68,.22,1));pos=ex(mat,u.MaterialExpressionWorldPosition)
n=ex(mat,u.MaterialExpressionNoise,scale=.045,levels=2,quality=1,output_min=.35,output_max=1.0);ML.connect_material_expressions(pos,'XYZ',n,'Position')
mul=ex(mat,u.MaterialExpressionMultiply);ML.connect_material_expressions(color,'',mul,'A');ML.connect_material_expressions(n,'',mul,'B');ML.connect_material_property(mul,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
base=ex(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(.08,.045,.018,1));ML.connect_material_property(base,'',u.MaterialProperty.MP_BASE_COLOR);MaterialTools.recompile(mat);E.save_loaded_asset(mat)
overlays=[]
for variant in range(3):
    name='SM_District_LitWindows_'+str(variant);path=BASE+'/Kit/Meshes/'+name
    if not E.does_asset_exist(path):
        t=u.AssetImportTask();t.filename=str(ROOT/'ArtSource/Prepared/district/cc0'/(name+'.fbx'));t.destination_path=BASE+'/Kit/Meshes';t.destination_name=name;t.automated=True;t.save=True
        opts=u.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.auto_generate_collision=False;t.options=opts;AT.import_asset_tasks([t])
    mesh=u.load_asset(path);mesh.set_material(0,mat);E.save_loaded_asset(mesh);overlays.append(mesh)
actors={a.get_actor_label():a for a in AS.get_all_level_actors()}
for i,house in enumerate(sorted([a for a in actors.values() if a.get_actor_label().startswith(('District_House_','District_NeighbouringBlock')) and not a.get_actor_label().endswith('_LitWindows')],key=lambda a:a.get_actor_label())):
    label=house.get_actor_label()+'_LitWindows';a=actors.get(label)
    if not a:a=AS.spawn_actor_from_class(u.StaticMeshActor,house.get_actor_location(),house.get_actor_rotation());a.set_actor_label(label);a.set_folder_path('District/OccupiedWindows')
    a.static_mesh_component.set_static_mesh(overlays[i%3]);a.set_actor_scale3d(house.get_actor_scale3d());a.static_mesh_component.set_collision_profile_name('NoCollision');a.set_actor_enable_collision(False);a.static_mesh_component.set_cast_shadow(False)
cube=u.load_asset('/Engine/BasicShapes/Cube');walk=u.load_asset(BASE+'/Materials/M_District_DampConcrete');paint=u.load_asset(BASE+'/Materials/M_District_WornRoadPaint')
def slab(label,x,y,z,sx,sy,sz,material,yaw=0):
    a=actors.get(label)
    if not a:a=AS.spawn_actor_from_class(u.StaticMeshActor,u.Vector(x,y,z),u.Rotator(pitch=0,yaw=yaw,roll=0));a.set_actor_label(label);a.set_folder_path('District/ExteriorStreets')
    a.static_mesh_component.set_static_mesh(cube);a.static_mesh_component.set_material(0,material);a.set_actor_scale3d(u.Vector(sx/100,sy/100,sz/100));a.static_mesh_component.set_collision_profile_name('BlockAll' if sz>2 else 'NoCollision');return a
for sign in [-1,1]:
    slab('District_OuterSidewalk_NS_'+str(sign),0,sign*5480,7,13600,180,16,walk)
    slab('District_OuterSidewalk_EW_'+str(sign),sign*6680,0,7,180,11140,16,walk)
    for i in range(8):
        slab('District_Zebra_NS_%d_%d'%(sign,i),sign*4500,-5000+sign*0+(i-3.5)*70,4.5,240,35,1,paint)
        slab('District_Zebra_North_%d_%d'%(sign,i),sign*4500,5000+(i-3.5)*70,4.5,240,35,1,paint)
# A grey-blue overcast fill keeps the shadowed side readable; practical lights stay warm.
sky=actors['District_OvercastSkylight'].light_component;sky.set_editor_property('intensity',2.8)
for a in AS.get_all_level_actors():
    if a.get_actor_label().startswith('District_StreetLightPool') and isinstance(a,u.PointLight):a.light_component.set_editor_property('intensity',550)
AS.clear_actor_selection_set();assert LS.save_current_level();u.log('DISTRICT_STREET_DETAILS_READY')
