import unreal as u,pathlib,json
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours/District';OUT=ROOT/'ArtSource/Prepared/district/kit'
E=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools();ML=u.MaterialEditingLibrary
manifest=json.loads((OUT/'kit-manifest.json').read_text());sources=json.loads((ROOT/'ArtSource/Prepared/district/source/manifest.json').read_text())
palette={'District_PaintedSteel':((.055,.085,.065),.55,.52),'District_RustedSteel':((.12,.062,.027),.6,.7),'District_WornWood':((.19,.105,.045),0,.73),'District_FadedYellow':((.42,.30,.055),.25,.6),'District_FadedRed':((.28,.05,.025),.2,.55),'District_FadedBlue':((.035,.105,.17),.25,.55),'District_Concrete':((.25,.25,.23),0,.8),'District_LampGlass':((.95,.60,.26),0,.3),'District_BinInterior':((.012,.014,.012),0,.9),'District_Sand':((.28,.23,.13),0,.91),'District_Rubber':((.016,.018,.017),0,.8)}
materials={}
for name,(rgb,metal,rough) in palette.items():
    path=BASE+'/Kit/Materials/M_'+name
    mat=u.load_asset(path)
    if not mat:mat=AT.create_asset('M_'+name,BASE+'/Kit/Materials',u.Material,u.MaterialFactoryNew())
    ML.delete_all_material_expressions(mat)
    c=ML.create_material_expression(mat,u.MaterialExpressionConstant3Vector);c.set_editor_property('constant',u.LinearColor(*rgb,1));ML.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
    for value,prop in [(metal,u.MaterialProperty.MP_METALLIC),(rough,u.MaterialProperty.MP_ROUGHNESS)]:
        e=ML.create_material_expression(mat,u.MaterialExpressionConstant);e.set_editor_property('r',value);ML.connect_material_property(e,'',prop)
    if name=='District_LampGlass':
        em=ML.create_material_expression(mat,u.MaterialExpressionConstant3Vector);em.set_editor_property('constant',u.LinearColor(3.5,1.6,.45,1));ML.connect_material_property(em,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
    ML.recompile_material(mat);E.save_loaded_asset(mat);materials[name]=mat
for definition in manifest['assets']:
    name=definition['name']
    if name=='SM_District_LowriseSection':continue
    path=BASE+'/Kit/Meshes/'+name
    if not E.does_asset_exist(path):
        task=u.AssetImportTask();task.filename=str(OUT/(name+'.fbx'));task.destination_path=BASE+'/Kit/Meshes';task.destination_name=name;task.automated=True;task.save=True
        opts=u.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False;opts.static_mesh_import_data.combine_meshes=True;opts.static_mesh_import_data.auto_generate_collision=False;task.options=opts
        AT.import_asset_tasks([task])
    mesh=u.load_asset(path);assert mesh,name
    mapping={s['name']:s['material'] for s in sources.get(definition['source'],{}).get('slots',[])}
    for index,slot in enumerate(mesh.get_editor_property('static_materials')):
        slotname=str(slot.material_slot_name).split('.')[0]
        mat=materials.get(slotname) or (u.load_asset(mapping[slotname]) if slotname in mapping else None)
        if mat:mesh.set_material(index,mat)
    E.save_loaded_asset(mesh)
u.log('DISTRICT_COURTYARD_KIT_IMPORTED')
