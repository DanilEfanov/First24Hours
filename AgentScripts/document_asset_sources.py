import pathlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
models=json.loads((ROOT/'ArtSource/Metadata/models.json').read_text('utf-8-sig'))
textures=json.loads((ROOT/'ArtSource/Metadata/textures.json').read_text('utf-8-sig'))
model_ids=['sofa_02','SchoolDesk_01','painted_wooden_chair_02','desk_lamp_arm_01','book_encyclopedia_set_01','alarm_clock_01','vintage_electric_kettle']
texture_ids=['wood_floor_worn','painted_plaster_wall','floor_tiles_04','fabric_pattern_05']
lines=['# Asset sources — First24Hours apartment, 21 October 2026','',
       '## Downloaded and used — Poly Haven CC0','',
       'License verified at https://polyhaven.com/license . CC0 permits commercial games and modification; attribution is not required. No login, checkout, payment or license-acceptance dialog was used.',
       'Official public API metadata and per-file MD5 verification are stored in ArtSource/Metadata and ArtSource/download-manifest.json. Models/textures are 2K. Models were converted glTF -> FBX, pivots normalized, and OpenGL normal maps flipped on the green channel for Unreal.',
       '', '| Asset | Author(s) | Original page | License | Status |','|---|---|---|---|---|']
for category,ids in [(models,model_ids),(textures,texture_ids)]:
    for asset in ids:
        meta=category[asset];authors=', '.join(meta.get('authors',{}).keys())
        lines.append(f"| {meta['name']} ({asset}) | {authors} | https://polyhaven.com/a/{asset} | CC0; no attribution required | Downloaded, verified, imported and used |")
lines += ['', '## Existing project assets used','',
 '| Asset | Author/source | Link | License / attribution | Status |','|---|---|---|---|---|',
 '| nine-story building of the post soviet | vladySLAVE (Sketchfab); ITG Models (Fab listing) | https://sketchfab.com/3d-models/nine-story-building-of-the-post-soviet-33a2b2901adc4b38ab83021b0837cd10 ; https://www.fab.com/listings/bc387245-1687-44b9-a37f-05a3bbabc327 | CC BY 4.0 verified through the original Sketchfab API. Commercial use permitted with attribution. Credit text below. | Existing imported mesh used in exterior; original asset not changed |',
 '| First Person character, controller, camera, input and mannequin dependencies | Epic Games | Unreal Engine First Person template, installed with this project | Existing Epic template content under applicable Unreal Engine EULA; no new legal terms accepted | Character and GameMode duplicated under /Game/First24Hours/Blueprints; originals retained |',
 '', 'Required credit for the building:', '',
 '> "nine-story building of the post soviet" by vladySLAVE, https://sketchfab.com/3d-models/33a2b2901adc4b38ab83021b0837cd10 , licensed under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Placed as exterior scenery; transform changed, source geometry and materials unchanged.',
 '', 'Primary license evidence: ArtSource/Metadata/existing-building-license.json; field license.requirements explicitly states author credit and commercial-use permission.',
 '', '## Original project work', '',
 'Apartment shell, floor layout, joinery, entry door, windows, radiator, kitchen cabinets and appliances, bathroom fixtures, bed, wardrobe, monitor and keyboard, textiles and distant skyline were authored for First24Hours by the production scripts in AgentScripts/model_apartment.py. No third-party model was used for these shapes. They are stage-one original meshes, not a purchased furniture pack.',
 'Rain-card shader and generated rain audio are original project work (AgentScripts/02_BuildApartment.py and make_rain_audio.py). No external recordings or generative-image assets were used.',
 '', '## Fab: manual acquisition only — NOT downloaded or imported', '',
 '| Asset | Author | Link | Verified public information | Required manual step |','|---|---|---|---|---|',
 '| Free Furniture Pack | Next Level 3D | https://www.fab.com/listings/baece383-bc75-4de8-971d-25110a169a36 | Public page says Free, 37 models, Unreal Engine format. Public License terms field is blank; applicable account-specific license and UE 5.8 support could not be verified. | User must sign in personally, inspect commercial-use rights/license, add to library only if free and acceptable, and add to project through Epic Games Launcher/Fab. Any checkout, legal acceptance or order must be completed by the user. Do not pay or use saved payment methods. If only an older UE version is supported, add to a separate compatible project and migrate after checking. |',
 '', 'This optional Fab pack is NOT required to open or play the current apartment. It can improve furniture and bathroom details after manual acquisition.',
 '', '## Already imported but not used in this new map', '',
 '- Panel House / Tile Texture, CATholic: original project content retained. Its commercial license has not been independently confirmed here; no new copy or modified material was introduced.',
 '- Low Poly Soviet Cars, Anadolu Saykodeli: https://www.fab.com/listings/cab1012b-3315-4f5e-a9d3-5ddf3dca1d2f . Public page says Free but license terms are not exposed. Retained in project, not used in this map; verify acquisition/license manually before release.',
 '', 'No assets were purchased, no checkout was automated, no account was logged in, and no new legal agreement was accepted on the user\'s behalf.']
(ROOT/'ASSET_SOURCES.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('ASSET_SOURCES.md written with eleven CC0 source entries and building attribution')
