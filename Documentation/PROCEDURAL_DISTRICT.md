# L_ProceduralDistrict — reference courtyard

Map: `/Game/First24Hours/Maps/L_ProceduralDistrict`.
Unreal scene changes were executed through the running UE 5.8 MCP, including editor Python entered through its Slate console. Source preparation used Blender and workspace scripts. Existing scenes were preserved; original map hashes are checked in `district-build-report.json`.

## Actual result

The two uploaded PNG references guide the composition. Four nine-storey housing rows enclose the courtyard: 14 contiguous existing building sections, plus seven sections in neighbouring blocks. All 14 main sections were rotated 180 degrees around the vertical axis at their footprint centres, with entrances facing the courtyard. Height is approximately 27.44 m at uniform scale 0.8. Building footprint is roughly 110 × 88 m; outer circulation is roughly 130 × 106 m.

This approximates the reference layout. It is not an exact architectural reconstruction: the existing whole tower model is repeated into rows, rather than using an exact modular slab-house kit. Facades, roof seams and entrance spacing differ. Buildings were not substituted with cube assemblies.

Three real PCG spline routes generate 27 spline-mesh road segments: inner ring, outer street loop and entrance connection. Widths are 6 m and 4 m. Frontage sidewalks are 1.8 m, inner walks 1.6 m. There are 60 marked 2.5 × 5 m parking bays and 42 detailed parked cars using two modern models and six paint colours.

The centre contains a fenced playground, slide tower, swings, roundabout, sandpit, benches, bins, paths and a utility structure with a container enclosure. Warm lamps and selected occupied windows establish evening lighting. Playground models are authored meshes; the utility block uses simple structural geometry. Both need a higher-detail weathering pass.

## Procedural placement

- `PCG_District_Road`: three Create Points → Create Spline → Spawn Spline Mesh branches.
- `PCG_District_Trees`: 58 authored anchors → seeded variation → Self Pruning → Static Mesh Spawner; **51 actual tree instances**.
- `PCG_District_Decor`: separate anchors and spawners; **10 benches and 10 bins**.
- Garden understory: two saved instanced mesh components with **1,606 grass clumps and 34 planting strips**. These are authored placement, not another PCG graph.

Anchors follow this layout; automatic building/road exclusion is not implemented. Foliage uses masked leaves, Nanite preservation and a full-silhouette fallback mesh.

## Weather

Wet asphalt, concrete paving and leaf-covered soil use 2K PBR textures at world-space scale. Puddles have animated ripple normals. Volumetric height fog and an overcast sky provide the autumn atmosphere.

`NS_District_Rain` produces Niagara streaks over an 80 × 65 m courtyard area at a spawn height around 10.5 m. A runtime simulation-cache check verifies more than 26,000 live particles actually occupy the courtyard. The Box Midpoint parameter is normalized, correctly set to (0.5, 0.5, 0.5).

`S_Rain_Outdoor_Stereo` is an original synthesized 32-second looping rain wash, played automatically by AmbientSound. It is not a field recording. Rain remains fixed in position; roof occlusion, splash collisions, player following and interior audio transitions remain unfinished. New window overlays are emissive glazing, not new interiors.

## Free assets actually imported

Poly Haven assets are CC0, with provider MD5 checks and source manifests in `ArtSource/Metadata`. Powered by Poly Haven.

- [Tree Small 02](https://polyhaven.com/a/tree_small_02), [Shrub 01](https://polyhaven.com/a/shrub_01), [Grass Medium 01](https://polyhaven.com/a/grass_medium_01) — autumn adaptations.
- [Street Lamp 01](https://polyhaven.com/a/street_lamp_01), [Painted Wooden Sofa](https://polyhaven.com/a/painted_wooden_sofa) — textured lamps and two entrance seats.
- [Asphalt 03](https://polyhaven.com/a/asphalt_03), [Concrete Pavement](https://polyhaven.com/a/concrete_pavement), [Forest Leaves 02](https://polyhaven.com/a/forest_leaves_02) — surface textures.
- [Graphite sedan](https://www.innerscene.com/tools/library/3d-parts/graphite-four-door-sedan-eed96d12), [station wagon](https://www.innerscene.com/tools/library/3d-parts/generic-station-wagon-estate-car-dec07098) — Innerscene original models, CC0; source SHA-256 hashes in the prepared manifests.

Existing building: “nine-story building of the post soviet” by vladySLAVE, CC BY 4.0. Source/license evidence is retained in `ASSET_SOURCES.md` and `ArtSource/Metadata/existing-building-license.json`. [Fab listing](https://www.fab.com/listings/bc387245-1687-44b9-a37f-05a3bbabc327).

Free Fab candidates researched but not acquired: [additional Soviet building](https://www.fab.com/listings/4556488e-4998-4630-862f-e3d0d007d0f9), [European Black Alder](https://www.fab.com/listings/9de7ce19-5813-42d2-a5f0-5e6447006f72), [Modern Street Props](https://www.fab.com/listings/7c886031-bd5c-410c-8fb5-5fee015abafd). No paid downloads, purchases or orders were used.

## Validation and next work

`district-build-report.json` records 64 successfully compiled materials, actual PCG counts, saved/reopened map checks and unchanged original scene hashes. `district-pie-check.json` verifies player spawn, active rain and playing audio. `district-rain-particles.json` verifies particle count and spatial bounds. `Screenshots/District_Courtyard_PIE.png` is an actual gameplay screenshot.

Closer matching still requires the exact modular panel facade/entrance kit, varied mature autumn trees, detailed weathered playground/utility models, curb details and surrounding city context. Then complete rain occlusion/splashes and profile performance on the target hardware. No packaged-build or performance certification was performed.
