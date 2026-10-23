import unreal as u,pathlib,json,hashlib,collections
from editor_toolset.toolsets.material import MaterialTools
ROOT=pathlib.Path(u.Paths.project_dir()).resolve();BASE='/Game/First24Hours/District';MAP='/Game/First24Hours/Maps/L_ProceduralDistrict'
AS=u.get_editor_subsystem(u.EditorActorSubsystem);LS=u.get_editor_subsystem(u.LevelEditorSubsystem);E=u.EditorAssetLibrary
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.')
old=json.loads((ROOT/'Documentation/district-build-report.json').read_text());layout=json.loads((ROOT/'Documentation/district-reference-layout.json').read_text())
report={'map':MAP,'reference':layout['reference'],'stage':'Reference courtyard: four housing rows, furnished gardens, wet streets and weather','existing_map_hashes':old['existing_map_hashes'],'dimensions_cm':{'road_width':600,'secondary_road_width':400,'frontage_sidewalk':180,'inner_walk':160,'parking_bay':[250,500],'building_height':2744.17},'missing':['Exact modular slab-house facade from the reference','High-detail weathered playground and utility-building kit','Varied mature tree species and continuous surrounding city','Rain roof occlusion, splashes and interior audio transitions']}
materials=[]
u.log('DISTRICT_FINAL_MATERIAL_CHECK_BEGIN')
for path in E.list_assets(BASE,recursive=True,include_folder=False):
    data=E.find_asset_data(path)
    if str(data.asset_class_path.asset_name)=='Material':
        mat=u.load_asset(path);MaterialTools.recompile(mat);E.save_loaded_asset(mat);materials.append(path)
report['compiled_materials']=len(materials)
u.log('DISTRICT_FINAL_MATERIAL_CHECK_END '+str(len(materials)))
def inspect():
    actors=AS.get_all_level_actors();pcg=[]
    for a in actors:
        if not isinstance(a,u.PCGVolume):continue
        row={'label':a.get_actor_label(),'instances':[],'splines':[],'spline_meshes':[]}
        for c in a.get_components_by_class(u.InstancedStaticMeshComponent):row['instances'].append({'mesh':c.static_mesh.get_path_name(),'count':c.get_instance_count()})
        for c in a.get_components_by_class(u.SplineComponent):row['splines'].append({'points':c.get_number_of_spline_points(),'length_cm':c.get_spline_length()})
        for c in a.get_components_by_class(u.SplineMeshComponent):row['spline_meshes'].append({'width_cm':c.get_start_scale().x*100,'thickness_cm':c.get_start_scale().y*100})
        pcg.append(row)
    return actors,pcg
actors,pcg=inspect();report['pcg_actual_components']=pcg
report['tree_instances']=sum(i['count'] for p in pcg if 'Trees' in p['label'] for i in p['instances']);assert report['tree_instances']>40
roads=next(p for p in pcg if 'Road' in p['label']);assert len(roads['splines'])==3 and len(roads['spline_meshes'])>=27
assert all(round(c['width_cm']) in [400,600] for c in roads['spline_meshes'])
report['road_spline_meshes']=len(roads['spline_meshes']);report['parking_bays']=len(layout['parking_bays'])
houses=[a for a in actors if a.get_actor_label().startswith('District_House_') and not a.get_actor_label().endswith('_LitWindows')];assert len(houses)==14
report['housing_rows']=4;report['housing_sections']=len(houses);report['modular_building_kit']=False;report['entrances_rotated_180_degrees']=layout['entrances_rotated_180_degrees']
for row in layout['building_rows']:
    for a in houses:
        if a.get_actor_label().startswith('District_House_'+row['name']+'_'):
            assert abs(u.MathLibrary.normalized_delta_rotator(a.get_actor_rotation(),u.Rotator(pitch=0,yaw=row['entrance_facing_yaw'],roll=0)).yaw)<.01
            center,extent=a.get_actor_bounds(False);assert center.z-extent.z>-.1
report['parked_cars']=sum(a.get_actor_label().startswith('District_ParkedVehicle') for a in actors)
report['understory']={a.get_actor_label():sum(c.get_instance_count() for c in a.get_components_by_class(u.InstancedStaticMeshComponent)) for a in actors if a.get_actor_label() in ['District_GardenGrassInstances','District_GardenUnderstoryInstances']}
for filename,digest in report['existing_map_hashes'].items():assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest()==digest
AS.clear_actor_selection_set();assert LS.save_current_level();assert LS.load_level(MAP)
actors,after=inspect();assert sum(i['count'] for p in after if 'Trees' in p['label'] for i in p['instances'])==report['tree_instances']
report['reopen_success']=True;report['actor_count_after_reopen']=len(actors)
report['weather']={'rain':'NS_District_Rain','sound':'S_Rain_Outdoor_Stereo','volumetric_fog':True,'fixed_area_rain':True}
inventory=[]
for data in u.AssetRegistryHelpers.get_asset_registry().get_assets_by_path('/Game',recursive=True):
    cls=str(data.asset_class_path.asset_name)
    if cls in ['StaticMesh','Material','MaterialInstanceConstant','Texture2D','TextureCube','PCGGraph','World','Blueprint','NiagaraSystem','SoundWave']:inventory.append({'path':str(data.package_name),'class':cls})
(ROOT/'Documentation/district-asset-inventory.json').write_text(json.dumps(inventory,indent=2));report['inventory_count']=len(inventory)
(ROOT/'Documentation/district-build-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.get_editor_subsystem(u.UnrealEditorSubsystem).set_level_viewport_camera_info(u.Vector(-300,-850,180),u.Rotator(pitch=5,yaw=45,roll=0))
u.log('DISTRICT_REFERENCE_REOPEN_VERIFIED '+json.dumps({k:report[k] for k in ['tree_instances','road_spline_meshes','housing_sections','parked_cars','understory','reopen_success']}))
