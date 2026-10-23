import unreal as u,pathlib
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours/District';E=u.EditorAssetLibrary;AT=u.AssetToolsHelpers.get_asset_tools();ML=u.MaterialEditingLibrary
AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith('/Game/First24Hours/Maps/L_ProceduralDistrict.')
src=(ROOT/'AgentScripts/45_ApplyReferenceSurfaces.py').read_text();exec(src[src.index('def ex('):src.index('for source,target,')])
overrides={}
for actor in AS.get_all_level_actors():
    if not isinstance(actor,u.StaticMeshActor) or not actor.get_actor_label().startswith(('District_House_','District_NeighbouringBlock')):continue
    for i,slot in enumerate(actor.static_mesh_component.static_mesh.get_editor_property('static_materials')):
        key=str(slot.material_slot_name)
        if not key.startswith(('concrate','green_metal')):continue
        if key not in overrides:
            mn='M_District_Facade_'+key;mat=u.load_asset(BASE+'/Materials/'+mn)
            if not mat:mat=AT.create_asset(mn,BASE+'/Materials',u.Material,u.MaterialFactoryNew())
            ML.delete_all_material_expressions(mat)
            params={str(p.parameter_info.name):p.parameter_value for p in slot.material_interface.get_editor_property('texture_parameter_values')}
            texture=params.get('BaseColorTexture')
            if texture:
                color=ex(mat,u.MaterialExpressionTextureSample,texture=texture,sampler_type=u.MaterialSamplerType.SAMPLERTYPE_COLOR)
                desat=ex(mat,u.MaterialExpressionDesaturation);amount=ex(mat,u.MaterialExpressionConstant,r=.9);ML.connect_material_expressions(amount,'',desat,'Fraction');assert ML.connect_material_expressions(color,'RGB',desat,'')
                boost=ex(mat,u.MaterialExpressionMultiply,const_b=1.35 if key.startswith('concrate') else .85);ML.connect_material_expressions(desat,'',boost,'A');ML.connect_material_property(boost,'',u.MaterialProperty.MP_BASE_COLOR)
            else:
                color=ex(mat,u.MaterialExpressionConstant3Vector,constant=u.LinearColor(.29,.28,.255,1));ML.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
            normal=params.get('NormalTexture')
            if normal:
                n=ex(mat,u.MaterialExpressionTextureSample,texture=normal,sampler_type=u.MaterialSamplerType.SAMPLERTYPE_NORMAL);ML.connect_material_property(n,'RGB',u.MaterialProperty.MP_NORMAL)
            rough=ex(mat,u.MaterialExpressionConstant,r=.78);ML.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
            ML.recompile_material(mat);E.save_loaded_asset(mat);overrides[key]=mat
        actor.static_mesh_component.set_material(i,overrides[key])
# Flat horizontal surfaces sample normals in world XY, independent of individual spline tangents.
for key in ['WetAsphalt','DampConcrete','AutumnGround']:
    mat=u.load_asset(BASE+'/Materials/M_District_'+key);mat.set_editor_property('tangent_space_normal',False);ML.recompile_material(mat);E.save_loaded_asset(mat)
assert LS.save_current_level();u.log('DISTRICT_REFERENCE_FACADE_PALETTE_READY')
