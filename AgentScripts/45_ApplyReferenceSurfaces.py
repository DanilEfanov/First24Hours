import unreal as u,pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours/District';E=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools();ML=u.MaterialEditingLibrary
AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/First24Hours/Maps/L_ProceduralDistrict.')
def ex(mat,cls,**kw):
    e=ML.create_material_expression(mat,cls)
    for k,v in kw.items():e.set_editor_property(k,v)
    return e
def tex(file,normal=False,linear=False):
    name='T_PH_'+file.stem;path=BASE+'/Textures/'+name
    if not E.does_asset_exist(path):
        t=u.AssetImportTask();t.filename=str(file);t.destination_path=BASE+'/Textures';t.destination_name=name;t.automated=True;t.save=True;AT.import_asset_tasks([t])
    a=u.load_asset(path)
    if normal:a.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP);a.set_editor_property('srgb',False)
    elif linear:a.set_editor_property('srgb',False);a.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_MASKS)
    E.save_loaded_asset(a);return a
def sample(mat,file,uv=None,normal=False,linear=False):
    e=ex(mat,u.MaterialExpressionTextureSample,texture=tex(file,normal,linear),sampler_type=u.MaterialSamplerType.SAMPLERTYPE_NORMAL if normal else u.MaterialSamplerType.SAMPLERTYPE_MASKS if linear else u.MaterialSamplerType.SAMPLERTYPE_COLOR)
    if uv:ML.connect_material_expressions(uv,'',e,'UVs')
    return e
for source,target,size,dark,wet in [('asphalt_03','WetAsphalt',300,.42,.25),('concrete_pavement','DampConcrete',300,.65,.62),('forest_leaves_02','AutumnGround',300,.8,.74)]:
    mat=u.load_asset(BASE+'/Materials/M_District_'+target);ML.delete_all_material_expressions(mat)
    pos=ex(mat,u.MaterialExpressionWorldPosition);xy=ex(mat,u.MaterialExpressionComponentMask,r=True,g=True,b=False,a=False);assert ML.connect_material_expressions(pos,'XYZ',xy,'')
    uv=ex(mat,u.MaterialExpressionMultiply,const_b=1/size);ML.connect_material_expressions(xy,'',uv,'A')
    folder=ROOT/'ArtSource/Models/reference_cc0'/source
    diffuse=sample(mat,next(folder.glob('*diff*.jpg')),uv);normal=sample(mat,next(folder.glob('*nor_dx*.jpg')),uv,normal=True);rough=sample(mat,next(folder.glob('*rough*.jpg')),uv,linear=True)
    color=ex(mat,u.MaterialExpressionMultiply,const_b=dark);ML.connect_material_expressions(diffuse,'RGB',color,'A');ML.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
    r=ex(mat,u.MaterialExpressionMultiply,const_b=wet);ML.connect_material_expressions(rough,'R',r,'A');ML.connect_material_property(r,'',u.MaterialProperty.MP_ROUGHNESS);ML.connect_material_property(normal,'RGB',u.MaterialProperty.MP_NORMAL)
    ML.layout_material_expressions(mat);ML.recompile_material(mat);E.save_loaded_asset(mat)
# Source leaf geometry must never be reduced to the tiny default fallback silhouette.
tree=u.load_asset(BASE+'/Foliage/SM_District_TreeSmall02');ns=tree.get_editor_property('nanite_settings')
u.log('DISTRICT_TREE_NANITE '+str(ns))
u.log('DISTRICT_TREE_SLOTS '+str([(str(s.material_slot_name),s.material_interface.get_path_name() if s.material_interface else None) for s in tree.get_editor_property('static_materials')]))
ns.set_editor_property('fallback_percent_triangles',1.0);ns.set_editor_property('fallback_relative_error',0.0)
tree.set_editor_property('nanite_settings',ns);E.save_loaded_asset(tree)
for a in AS.get_all_level_actors():
    if a.get_actor_label()=='District_OvercastSkylight':a.light_component.set_editor_property('intensity',2.4)
assert LS.save_current_level()
u.log('DISTRICT_PBR_SURFACES_READY')
