import unreal as u,pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours/District'
E=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools();ML=u.MaterialEditingLibrary
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/First24Hours/Maps/L_ProceduralDistrict.')
source=ROOT/'ArtSource/Prepared/district/SM_District_TreeSmall02.fbx'
assert source.exists()
path=BASE+'/Foliage/SM_District_TreeSmall02'
if not E.does_asset_exist(path):
    task=u.AssetImportTask();task.filename=str(source);task.destination_path=BASE+'/Foliage';task.destination_name='SM_District_TreeSmall02';task.automated=True;task.save=True
    options=u.FbxImportUI();options.import_mesh=True;options.import_materials=False;options.import_textures=False;options.import_as_skeletal=False
    options.static_mesh_import_data.combine_meshes=True
    options.static_mesh_import_data.auto_generate_collision=False
    task.options=options;AT.import_asset_tasks([task])
mesh=u.load_asset(path);assert mesh
def ex(mat,cls,**values):
    node=ML.create_material_expression(mat,cls)
    for k,v in values.items():node.set_editor_property(k,v)
    return node
def texture(suffix,normal=False,mask=False):
    stem='tree_small_02_'+suffix+'_2k'
    folder=ROOT/'ArtSource/Models/district_tree_small_02/textures'
    file=next(p for p in folder.iterdir() if p.stem==stem)
    path=BASE+'/Foliage/Textures/T_'+stem
    if not E.does_asset_exist(path):
        task=u.AssetImportTask();task.filename=str(file);task.destination_path=BASE+'/Foliage/Textures';task.destination_name='T_'+stem;task.automated=True;task.save=True;AT.import_asset_tasks([task])
    tex=u.load_asset(path)
    if normal:tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP);tex.set_editor_property('srgb',False);tex.set_editor_property('flip_green_channel',True)
    elif mask:tex.set_editor_property('srgb',False);tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_MASKS)
    E.save_loaded_asset(tex)
    return tex
def sample(mat,suffix,normal=False,mask=False):
    return ex(mat,u.MaterialExpressionTextureSample,texture=texture(suffix,normal,mask),sampler_type=u.MaterialSamplerType.SAMPLERTYPE_NORMAL if normal else u.MaterialSamplerType.SAMPLERTYPE_MASKS if mask else u.MaterialSamplerType.SAMPLERTYPE_COLOR)
materials={}
for part,prefix in [('branches','branch_'),('leaves','leaves_'),('trunk','')]:
    name='M_District_Tree_'+part
    mat=u.load_asset(BASE+'/Foliage/'+name)
    if not mat:mat=AT.create_asset(name,BASE+'/Foliage',u.Material,u.MaterialFactoryNew())
    ML.delete_all_material_expressions(mat)
    diff=sample(mat,prefix+'diff');base=diff
    if part=='leaves':
        mat.set_editor_property('blend_mode',u.BlendMode.BLEND_OPAQUE)
        mat.set_editor_property('two_sided',True)
        mat.set_editor_property('opacity_mask_clip_value',.42)
        # Preserve source leaf texture and shift its green reflectance to ochre.
        tint=ex(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(1.35,.72,.22,1))
        mul=ex(mat,u.MaterialExpressionMultiply)
        ML.connect_material_expressions(diff,'RGB',mul,'A');ML.connect_material_expressions(tint,'',mul,'B');base=mul
        alpha=sample(mat,'leaves_alpha',mask=True)
        ML.connect_material_property(alpha,'R',u.MaterialProperty.MP_OPACITY_MASK)
    ML.connect_material_property(base,'RGB' if base==diff else '',u.MaterialProperty.MP_BASE_COLOR)
    normal=sample(mat,prefix+'nor_gl',normal=True)
    ML.connect_material_property(normal,'RGB',u.MaterialProperty.MP_NORMAL)
    arm=sample(mat,prefix+'arm',mask=True)
    for pin,prop in [('R',u.MaterialProperty.MP_AMBIENT_OCCLUSION),('G',u.MaterialProperty.MP_ROUGHNESS),('B',u.MaterialProperty.MP_METALLIC)]:ML.connect_material_property(arm,pin,prop)
    ML.layout_material_expressions(mat);ML.recompile_material(mat);E.save_loaded_asset(mat);materials[part]=mat
slots=mesh.get_editor_property('static_materials')
for i,slot in enumerate(slots):
    name=str(slot.material_slot_name).lower()
    part='leaves' if 'leav' in name else 'branches' if 'branch' in name else 'trunk'
    mesh.set_material(i,materials[part])
SMS=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
nanite=mesh.get_editor_property('nanite_settings');nanite.set_editor_property('enabled',True)
mesh.set_editor_property('nanite_settings',nanite)
E.save_loaded_asset(mesh)
graph=u.load_asset(BASE+'/PCG/PCG_District_Trees')
node=next(n for n in graph.get_editor_property('nodes') if n.get_name()=='AutumnTreeInstances')
settings=node.get_settings();selector=settings.get_editor_property('mesh_selector_parameters')
entry=u.PCGMeshSelectorWeightedEntry()
descriptor=entry.get_editor_property('descriptor');descriptor.set_editor_property('static_mesh',mesh)
entry.set_editor_property('descriptor',descriptor);entry.set_editor_property('weight',1)
selector.set_editor_property('mesh_entries',[entry]);settings.set_editor_property('synchronous_load',True)
E.save_loaded_asset(graph)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('DISTRICT_TREE_IMPORTED '+str([(str(s.material_slot_name)) for s in slots]))
