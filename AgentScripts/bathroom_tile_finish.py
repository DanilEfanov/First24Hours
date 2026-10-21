"""Blender: an original inset tile lining for the bathroom wet zone."""
import bpy,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Tile')
def panel(pos,size):
    bpy.ops.mesh.primitive_cube_add(size=1,location=[x/100 for x in pos]);o=bpy.context.object
    o.dimensions=[x/100 for x in size];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    uv=o.data.uv_layers.active or o.data.uv_layers.new()
    for face in o.data.polygons:
        axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(face.normal[i]))]
        for li in face.loop_indices:
            p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv=(p[axes[0]]/2,p[axes[1]]/2)
for pos,size in [((100,1,110),(197,1,220)),((1,100,110),(1,197,220)),((193,100,110),(1,197,220)),
                 ((31,193,110),(60,1,220)),((177,193,110),(40,1,220))]:panel(pos,size)
bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=bpy.context.selected_objects[0];bpy.ops.object.join()
o=bpy.context.object;o.name='SM_Bathroom_TileLining';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(ROOT/'ArtSource/Prepared/SM_Bathroom_TileLining.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',bake_anim=False)
