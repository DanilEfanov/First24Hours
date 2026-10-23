import unreal as u,pathlib
from editor_toolset.toolsets.material import MaterialTools
BASE='/Game/First24Hours/District';ML=u.MaterialEditingLibrary;E=u.EditorAssetLibrary
for key in ['WetAsphalt','DampConcrete','AutumnGround']:
    mat=u.load_asset(BASE+'/Materials/M_District_'+key);nodes=MaterialTools.get_expressions(mat)
    pos=next(e for e in nodes if isinstance(e,u.MaterialExpressionWorldPosition));mask=next(e for e in nodes if isinstance(e,u.MaterialExpressionComponentMask))
    assert ML.connect_material_expressions(pos,'XYZ',mask,'')
    ML.recompile_material(mat);E.save_loaded_asset(mat)
for kind in ['Sedan','Wagon']:
    mesh=u.load_asset(BASE+'/Kit/Meshes/SM_CC0_Modern'+kind)
    for s in mesh.get_editor_property('static_materials'):
        if not str(s.material_slot_name).startswith('glass'):continue
        mat=s.material_interface;ML.delete_all_material_expressions(mat)
        c=ML.create_material_expression(mat,u.MaterialExpressionConstant3Vector);c.set_editor_property('constant',u.LinearColor(.022,.035,.044,1));ML.connect_material_property(c,'',u.MaterialProperty.MP_BASE_COLOR)
        for value,prop in [(.13,u.MaterialProperty.MP_ROUGHNESS),(.35,u.MaterialProperty.MP_METALLIC)]:
            n=ML.create_material_expression(mat,u.MaterialExpressionConstant);n.set_editor_property('r',value);ML.connect_material_property(n,'',prop)
        ML.recompile_material(mat);E.save_loaded_asset(mat)
u.log('DISTRICT_SURFACE_CONNECTIONS_FIXED')
