import unreal as u
from editor_toolset.toolsets.material import MaterialTools
mat=u.load_asset('/Game/First24Hours/District/Foliage/M_District_Tree_leaves')
mat.set_editor_property('blend_mode',u.BlendMode.BLEND_MASKED)
mat.set_editor_property('two_sided',True)
mat.set_editor_property('opacity_mask_clip_value',.22)
alpha=next(e for e in MaterialTools.get_expressions(mat) if isinstance(e,u.MaterialExpressionTextureSample) and 'alpha' in e.texture.get_name())
u.MaterialEditingLibrary.connect_material_property(alpha,'R',u.MaterialProperty.MP_OPACITY_MASK)
u.MaterialEditingLibrary.recompile_material(mat)
u.EditorAssetLibrary.save_loaded_asset(mat)
u.log('DISTRICT_LEAF_MASK_FIXED')
