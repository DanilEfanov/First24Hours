"""Executed inside Unreal through the connected MCP's Slate console tool.
Only creates/updates assets under /Game/First24Hours and the new apartment map.
"""
import unreal as u, pathlib, json, re, math, traceback
ROOT=pathlib.Path(u.Paths.project_dir()).resolve()
BASE='/Game/First24Hours'; MAP=BASE+'/Maps/L_Apartment_0400'
E=u.EditorAssetLibrary; AT=u.AssetToolsHelpers.get_asset_tools(); ML=u.MaterialEditingLibrary
AS=u.get_editor_subsystem(u.EditorActorSubsystem); LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
DATA=json.loads((ROOT/'ArtSource/Prepared/apartment-manifest.json').read_text())
report={'map':MAP,'meshes':[],'materials':[],'warnings':[],'actors':[]}
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.'), 'Wrong level; refusing changes'
def safe(obj,key,value):
    try:obj.set_editor_property(key,value)
    except Exception as error:report['warnings'].append(str(type(obj).__name__)+'.'+key+': '+str(error))
def name(s):return re.sub('[^a-zA-Z0-9_]','_',s)
def P(x,y,z):return u.Vector(x,-y,z) # FBX Blender->UE conversion reverses Y.
def expr(mat,cls,**properties):
    e=ML.create_material_expression(mat,cls,-400,0)
    for k,v in properties.items():e.set_editor_property(k,v)
    return e
def connect(e,prop,output=''):
    assert ML.connect_material_property(e,output,prop)
def constant(mat,v):return expr(mat,u.MaterialExpressionConstant,r=float(v))
texture_cache={}
def texture(file,normal=False,gl=False,mask=False):
    if not file:return None
    file=str(file);key=(file,normal,gl,mask)
    if key in texture_cache:return texture_cache[key]
    path=BASE+'/Art/Textures/T_'+name(pathlib.Path(file).stem)
    if not E.does_asset_exist(path):
        t=u.AssetImportTask();t.filename=file;t.destination_path=BASE+'/Art/Textures';t.destination_name=path.rsplit('/',1)[1]
        t.automated=True;t.save=True;t.replace_existing=False;AT.import_asset_tasks([t])
    tex=u.load_asset(path);assert tex, 'Texture import failed: '+file
    if normal:
        tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP)
        tex.set_editor_property('srgb',False);tex.set_editor_property('flip_green_channel',gl)
    elif mask:
        tex.set_editor_property('srgb',False);tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_MASKS)
    E.save_loaded_asset(tex);texture_cache[key]=tex;return tex
def texexpr(mat,file,normal=False,gl=False,mask=False):
    tex=texture(file,normal,gl,mask)
    e=expr(mat,u.MaterialExpressionTextureSample,texture=tex)
    e.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL if normal else
                          (u.MaterialSamplerType.SAMPLERTYPE_MASKS if mask else u.MaterialSamplerType.SAMPLERTYPE_COLOR))
    return e
materials={}
for label,definition in DATA['materials'].items():
    path=BASE+'/Art/Materials/M_'+name(label)
    if E.does_asset_exist(path) and label!='Rain':materials[label]=u.load_asset(path);continue
    if E.does_asset_exist(path):
        mat=u.load_asset(path);ML.delete_all_material_expressions(mat)
    else:
        mat=AT.create_asset(path.rsplit('/',1)[1],BASE+'/Art/Materials',u.Material,u.MaterialFactoryNew())
    assert mat,path
    texset=definition.get('texture_set')
    diffuse=definition.get('diffuse');normal=definition.get('normal');rough=None
    if texset:
        folder=ROOT/'ArtSource/Textures'/texset
        diffuse=str(next(p for p in folder.iterdir() if '_diff_' in p.name or '_col_' in p.name))
        normal=str(next(p for p in folder.iterdir() if '_nor_dx_' in p.name))
        rough=str(next(p for p in folder.iterdir() if '_rough_' in p.name))
    color=expr(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(*definition.get('color',[.5,.5,.5]),1))
    base=texexpr(mat,diffuse) if diffuse else color
    connect(base,u.MaterialProperty.MP_BASE_COLOR,'RGB' if diffuse else '')
    if normal:connect(texexpr(mat,normal,True,definition.get('normal_gl',False)),u.MaterialProperty.MP_NORMAL,'RGB')
    if definition.get('arm'):
        arm=texexpr(mat,definition['arm'],mask=True)
        connect(arm,u.MaterialProperty.MP_AMBIENT_OCCLUSION,'R');connect(arm,u.MaterialProperty.MP_ROUGHNESS,'G');connect(arm,u.MaterialProperty.MP_METALLIC,'B')
    else:
        connect(texexpr(mat,rough,mask=True) if rough else constant(mat,definition.get('roughness',.6)),u.MaterialProperty.MP_ROUGHNESS,'R' if rough else '')
        connect(constant(mat,definition.get('metallic',0)),u.MaterialProperty.MP_METALLIC)
    if definition.get('emissive'):
        mul=expr(mat,u.MaterialExpressionMultiply)
        ML.connect_material_expressions(color,'',mul,'A');ML.connect_material_expressions(constant(mat,definition['emissive']),'',mul,'B')
        connect(mul,u.MaterialProperty.MP_EMISSIVE_COLOR)
    if definition.get('translucent'):
        mat.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT)
        mat.set_editor_property('two_sided',True)
        safe(mat,'translucency_lighting_mode',u.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
        opacity=constant(mat,.10)
        if label=='Rain':
            uv=expr(mat,u.MaterialExpressionTextureCoordinate)
            clock=expr(mat,u.MaterialExpressionTime)
            custom=expr(mat,u.MaterialExpressionCustom)
            custom.set_editor_property('code','float2 q=UV*float2(30,2); float h=frac(sin(floor(q.x)*127.1)*43758.5453); float xx=frac(q.x)-.5; float yy=frac(q.y+T*2.8+h); return (1-smoothstep(.01,.055,abs(xx)))*(1-smoothstep(.04,.30,yy))*step(.25,h)*.35;')
            custom.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT1)
            uv_input=u.CustomInput();uv_input.set_editor_property('input_name','UV')
            time_input=u.CustomInput();time_input.set_editor_property('input_name','T')
            custom.set_editor_property('inputs',[uv_input,time_input])
            ML.connect_material_expressions(uv,'',custom,'UV');ML.connect_material_expressions(clock,'',custom,'T');opacity=custom
            connect(color,u.MaterialProperty.MP_EMISSIVE_COLOR)
        connect(opacity,u.MaterialProperty.MP_OPACITY)
    ML.recompile_material(mat);E.save_loaded_asset(mat);materials[label]=mat;report['materials'].append(path)
    u.log('FIRST24_MATERIAL '+label)
mesh_assets={}
for item in DATA['meshes']:
    path=BASE+'/Art/'+item['category']+'/'+item['name']
    if not E.does_asset_exist(path):
        t=u.AssetImportTask();t.filename=item['file'];t.destination_path=path.rsplit('/',1)[0];t.destination_name=item['name']
        t.automated=True;t.save=True;t.replace_existing=False
        opts=u.FbxImportUI();opts.automated_import_should_detect_type=False;opts.import_as_skeletal=False
        opts.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH;opts.import_materials=False;opts.import_textures=False
        opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.convert_scene_unit=True
        opts.static_mesh_import_data.auto_generate_collision=False
        t.options=opts;t.factory=u.FbxFactory();AT.import_asset_tasks([t])
    mesh=u.load_asset(path);assert mesh,path
    for index,slot in enumerate(mesh.get_editor_property('static_materials')):
        key=str(slot.material_slot_name)
        if key not in materials and index<len(item['slots']):key=item['slots'][index]
        if key not in materials:key=re.sub(r'\.\d+$','',key)
        assert key in materials, 'Missing material '+key+' for '+item['name']
        mesh.set_material(index,materials[key])
    body=mesh.get_editor_property('body_setup')
    if body:body.set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    E.save_loaded_asset(mesh);mesh_assets[item['name']]=mesh
    bounds=mesh.get_bounding_box()
    report['meshes'].append({'path':path,'min':[bounds.min.x,bounds.min.y,bounds.min.z],'max':[bounds.max.x,bounds.max.y,bounds.max.z]})
    u.log('FIRST24_IMPORTED '+item['name'])
existing={a.get_actor_label():a for a in AS.get_all_level_actors()}
def spawn(cls,label,pos=(0,0,0),yaw=0,folder=''):
    a=existing.get(label)
    if not a:a=AS.spawn_actor_from_class(cls,P(*pos),u.Rotator(pitch=0,yaw=-yaw,roll=0));a.set_actor_label(label);existing[label]=a
    a.set_actor_location(P(*pos),False,False)
    a.set_actor_rotation(u.Rotator(pitch=0,yaw=-yaw,roll=0),False)
    if folder:a.set_folder_path(u.Name(folder))
    report['actors'].append(label);return a
def mesh_actor(key,label,pos=(0,0,0),yaw=0,scale=(1,1,1),folder='02_Interiors'):
    a=spawn(u.StaticMeshActor,label,pos,yaw,folder)
    comp=a.static_mesh_component;comp.set_static_mesh(mesh_assets[key]);a.set_actor_scale3d(u.Vector(*scale))
    if key in ['SM_Window_Rain','SM_Apartment_Textiles']:
        comp.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
    if key in ['SM_City_Backdrop','SM_Window_Rain']:
        comp.set_cast_shadow(False)
    return a
for item in DATA['meshes']:
    if item['category']=='PolyHaven':continue
    folder={'Architecture':'01_Architecture','Furniture':'02_Interiors','Details':'03_Dressing','Exterior':'05_Exterior'}[item['category']]
    mesh_actor(item['name'],item['name'].replace('SM_','APT_'),folder=folder)
# Normalized scanned furniture in cm, built for this specific layout.
mesh_actor('SM_PH_sofa_02','PROP_LivingSofa',(350,355,1),yaw=180)
mesh_actor('SM_PH_SchoolDesk_01','PROP_StudentDesk',(688,538,1),scale=(1.45,1, .85))
mesh_actor('SM_PH_painted_wooden_chair_02','PROP_DeskChair',(686,474,1),yaw=180,scale=(.72,.72,.72))
mesh_actor('SM_PH_painted_wooden_chair_02','PROP_KitchenChair',(282,198,1),yaw=80,scale=(.75,.75,.75))
mesh_actor('SM_PH_desk_lamp_arm_01','PROP_DeskLamp',(645,535,78),yaw=90,scale=(.65,.65,.65))
mesh_actor('SM_PH_book_encyclopedia_set_01','PROP_StudyBooks',(744,535,78),yaw=90,scale=(.65,.65,.65))
mesh_actor('SM_PH_alarm_clock_01','PROP_BedsideClock',(739,65,61),yaw=180)
mesh_actor('SM_PH_vintage_electric_kettle','PROP_KitchenKettle',(298,35,93),scale=(.75,.75,.75))
# Already imported CC BY 4.0 building; no changes to the source asset/materials.
building_path='/Game/Assets/Environment/SovietApartmentBuilding/nine_story_building_of_the_post_soviet/StaticMeshes/nine_story_building_of_the_post_soviet'
building=u.load_asset(building_path)
if building:
    a=spawn(u.StaticMeshActor,'EXT_ExistingSovietBuilding',(900,2850,-1750),folder='05_Exterior')
    a.static_mesh_component.set_static_mesh(building)
    a.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
    a.static_mesh_component.set_cast_shadow(False)
    report['existing_building']=building_path
start=spawn(u.PlayerStart,'START_Apartment_Hall',(105,480,100),folder='06_Gameplay')
# Moonlight and captured skylight establish a cold, restrained 04:00 exterior.
moon=spawn(u.DirectionalLight,'LIGHT_Moon',(1000,1000,1800),folder='04_Lighting')
moon.set_actor_rotation(u.Rotator(pitch=-28,yaw=-125,roll=0),False);mc=moon.get_component_by_class(u.DirectionalLightComponent)
mc.set_intensity(.12);mc.set_light_color(u.LinearColor(.45,.60,1,1));mc.set_mobility(u.ComponentMobility.MOVABLE)
sky=spawn(u.SkyLight,'LIGHT_NightSky',(400,300,600),folder='04_Lighting');sc=sky.get_component_by_class(u.SkyLightComponent)
sc.set_intensity(.10);sc.set_light_color(u.LinearColor(.28,.39,.65,1));sc.set_mobility(u.ComponentMobility.MOVABLE)
sc.set_editor_property('real_time_capture',False)
fog=spawn(u.ExponentialHeightFog,'ATM_NightMist',(0,0,-1500),folder='05_Exterior')
fc=fog.get_component_by_class(u.ExponentialHeightFogComponent)
safe(fc,'fog_density',.018);safe(fc,'fog_height_falloff',.15);safe(fc,'fog_inscattering_luminance',u.LinearColor(.006,.009,.018,1));safe(fc,'enable_volumetric_fog',True)
def point(label,pos,lumens,temp,radius):
    a=spawn(u.PointLight,label,pos,folder='04_Lighting');c=a.get_component_by_class(u.PointLightComponent)
    c.set_mobility(u.ComponentMobility.MOVABLE);c.set_editor_property('intensity_units',u.LightUnits.LUMENS)
    c.set_intensity(lumens);c.set_attenuation_radius(radius);c.set_editor_property('use_temperature',True);c.set_editor_property('temperature',temp)
    c.set_editor_property('source_radius',5);return a
point('LIGHT_Hall_Dim',(100,440,246),110,2800,380)
point('LIGHT_Kitchen_Ceiling',(350,155,249),460,3100,430)
point('LIGHT_Bathroom',(100,112,247),200,3800,250)
point('LIGHT_Desk_Warm',(648,524,119),135,2700,320)
point('LIGHT_Bedside',(739,65,110),55,2400,250)
point('LIGHT_Window_ColdBounce',(515,555,180),80,8500,330)
point('LIGHT_Kitchen_UnderCabinet',(300,55,150),100,3000,180)
post=spawn(u.PostProcessVolume,'GRADE_0400',(390,290,150),folder='04_Lighting');post.set_editor_property('unbound',True)
settings=post.get_editor_property('settings')
for key,value in {'override_auto_exposure_min_brightness':True,'override_auto_exposure_max_brightness':True,
                  'auto_exposure_min_brightness':2.0,'auto_exposure_max_brightness':2.0,
                  'override_auto_exposure_bias':True,'auto_exposure_bias':0.0,
                  'override_bloom_intensity':True,'bloom_intensity':.22,
                  'override_vignette_intensity':True,'vignette_intensity':.28}.items():safe(settings,key,value)
post.set_editor_property('settings',settings)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
gm=u.load_class(None,BASE+'/Blueprints/BP_ApartmentGameMode.BP_ApartmentGameMode_C')
world.get_world_settings().set_editor_property('default_game_mode',gm)
AS.clear_actor_selection_set()
u.EditorLevelLibrary.set_level_viewport_camera_info(P(270,520,162),u.Rotator(pitch=-7,yaw=15,roll=0))
for asset in E.list_assets(BASE,recursive=True,include_folder=False):E.save_asset(asset,only_if_is_dirty=True)
LS.save_current_level()
(ROOT/'Documentation/apartment-build-report.json').write_text(json.dumps(report,indent=2))
u.log('FIRST24_APARTMENT_BUILD_COMPLETE '+str(len(report['actors']))+' actors')
