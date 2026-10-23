import unreal as u,pathlib,json,random,math
from editor_toolset.toolsets.material import MaterialTools
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours/District';MAP='/Game/First24Hours/Maps/L_ProceduralDistrict'
E=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools();ML=u.MaterialEditingLibrary;AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
layout=json.loads((ROOT/'Documentation/district-reference-layout.json').read_text())
def expr(mat,cls,**values):
    e=ML.create_material_expression(mat,cls)
    for k,v in values.items():e.set_editor_property(k,v)
    return e
def plain(name,color,rough=.6,metal=0):
    path=BASE+'/Kit/Materials/M_'+name;mat=u.load_asset(path)
    if not mat:mat=AT.create_asset('M_'+name,BASE+'/Kit/Materials',u.Material,u.MaterialFactoryNew())
    ML.delete_all_material_expressions(mat)
    c=expr(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(*color,1));ML.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
    for value,prop in [(rough,u.MaterialProperty.MP_ROUGHNESS),(metal,u.MaterialProperty.MP_METALLIC)]:
        e=expr(mat,u.MaterialExpressionConstant,r=value);ML.connect_material_property(e,'',prop)
    ML.recompile_material(mat);E.save_loaded_asset(mat);return mat
leaf=plain('District_LeafOchre',(.30,.13,.022),.84)
puddle=plain('District_Puddle',(.014,.019,.023),.055)
worldpos=expr(puddle,u.MaterialExpressionWorldPosition);clock=expr(puddle,u.MaterialExpressionTime)
custom=expr(puddle,u.MaterialExpressionCustom,code='float2 cell=floor(P.xy/90); float2 p=frac(P.xy/90)-0.5; float h=frac(sin(dot(cell,float2(12.9898,78.233)))*43758.5453); float phase=frac(T*1.6+h); float r=length(p); float wave=sin((r-phase*0.55)*80)*exp(-abs(r-phase*0.55)*35)*(1-phase); return normalize(float3(p/(r+0.001)*wave*0.08,1));',output_type=u.CustomMaterialOutputType.CMOT_FLOAT3)
inputs=[]
for name in ['P','T']:
    i=u.CustomInput();i.set_editor_property('input_name',name);inputs.append(i)
custom.set_editor_property('inputs',inputs)
ML.connect_material_expressions(worldpos,'',custom,'P');ML.connect_material_expressions(clock,'',custom,'T');ML.connect_material_property(custom,'',u.MaterialProperty.MP_NORMAL)
ML.recompile_material(puddle);E.save_loaded_asset(puddle)
materials={'District_LeafOchre':leaf,'District_Puddle':puddle}
for name in ['District_FadedYellow','District_FadedRed','District_FadedBlue','District_WornWood']:materials[name]=u.load_asset(BASE+'/Kit/Materials/M_'+name)
meshes={}
for name in ['PlayTowerSlide','Roundabout','LeafPatch','Puddle']:
    asset='SM_District_'+name;path=BASE+'/Kit/Meshes/'+asset
    if not E.does_asset_exist(path):
        task=u.AssetImportTask();task.filename=str(ROOT/'ArtSource/Prepared/district/kit'/(asset+'.fbx'));task.destination_path=BASE+'/Kit/Meshes';task.destination_name=asset;task.automated=True;task.save=True
        opts=u.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.auto_generate_collision=False;task.options=opts;AT.import_asset_tasks([task])
    mesh=u.load_asset(path);assert mesh
    for i,slot in enumerate(mesh.get_editor_property('static_materials')):
        mat=materials.get(str(slot.material_slot_name).split('.')[0])
        if mat:mesh.set_material(i,mat)
    E.save_loaded_asset(mesh);meshes[name]=mesh
def place(name,asset,xyz,yaw=0,scale=1):
    a=AS.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*xyz),u.Rotator(pitch=0,yaw=yaw,roll=0));a.set_actor_label('District_'+name);a.set_folder_path('District/SurfaceDetails' if name.startswith(('Leaves','Puddle')) else 'District/Recreation')
    a.static_mesh_component.set_static_mesh(asset);a.static_mesh_component.set_collision_profile_name('NoCollision');a.set_actor_enable_collision(False);a.set_actor_scale3d(u.Vector(scale,scale,scale));return a
place('PlayTowerSlide',meshes['PlayTowerSlide'],(650,80,12),0)
place('PlaygroundRoundabout',meshes['Roundabout'],(1750,-230,12))
rng=random.Random(101)
for i,(x,y,z) in enumerate(layout['tree_points']):
    for side in [-1,1]:place('Leaves_%02d_%d'%(i,side),meshes['LeafPatch'],(x+side*85,y+35,1.5),rng.uniform(0,360),rng.uniform(.8,1.4))
for i,(x,y,sc,yaw) in enumerate([(-2400,-2150,1.9,13),(1700,-2180,1.5,20),(3450,-950,1.3,90),(-3450,900,1.5,90),(2100,2150,1.7,5),(-1500,2170,1.4,0),(-4300,-2950,1.6,10),(-2500,-1540,.9,80),(1200,1540,.9,90),(2850,750,.8,10)]):place('Puddle_%02d'%i,meshes['Puddle'],(x,y,5.5),yaw,sc)
# Leaf cards are unnecessary for this source's modelled leaves; opaque material preserves the crown.
mat=u.load_asset(BASE+'/Foliage/M_District_Tree_leaves')
mat.set_editor_property('blend_mode',u.BlendMode.BLEND_OPAQUE);mat.set_editor_property('two_sided',True)
texture=next(e for e in MaterialTools.get_expressions(mat) if isinstance(e,u.MaterialExpressionTextureSample))
a=expr(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(.24,.085,.012,1));b=expr(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(.65,.36,.045,1))
blend=expr(mat,u.MaterialExpressionLinearInterpolate)
ML.connect_material_expressions(a,'',blend,'A');ML.connect_material_expressions(b,'',blend,'B');ML.connect_material_expressions(texture,'G',blend,'Alpha');ML.connect_material_property(blend,'',u.MaterialProperty.MP_BASE_COLOR)
ML.recompile_material(mat);E.save_loaded_asset(mat)
tree=u.load_asset(BASE+'/Foliage/SM_District_TreeSmall02');nanite=tree.get_editor_property('nanite_settings');nanite.set_editor_property('shape_preservation',u.NaniteShapePreservation.PRESERVE_AREA);tree.set_editor_property('nanite_settings',nanite);E.save_loaded_asset(tree)
colors=[(.038,.045,.05),(.16,.18,.18),(.40,.39,.34),(.07,.12,.15),(.13,.035,.026),(.10,.12,.08)]
paints=[plain('District_CarPaint_%d'%i,rgb,.26,.25) for i,rgb in enumerate(colors)]
for i,actor in enumerate(a for a in AS.get_all_level_actors() if a.get_actor_label().startswith('District_ParkedVehicle')):
    c=actor.static_mesh_component
    for index,slot in enumerate(c.static_mesh.get_editor_property('static_materials')):
        if str(slot.material_slot_name) in ['Car_Color','White_Sore']:c.set_material(index,paints[i%len(paints)])
for a in AS.get_all_level_actors():
    if isinstance(a,u.PointLight):a.light_component.set_light_color(u.LinearColor(1,.55,.24,1))
    if a.get_actor_label()=='District_OvercastPostProcess':
        s=a.get_editor_property('settings');s.set_editor_property('auto_exposure_min_brightness',.4);s.set_editor_property('auto_exposure_max_brightness',.4);s.set_editor_property('override_motion_blur_amount',True);s.set_editor_property('motion_blur_amount',0.0);a.set_editor_property('settings',s)
AS.clear_actor_selection_set();assert LS.save_current_level()
u.log('DISTRICT_REFERENCE_DETAILS_READY')
