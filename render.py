import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse, key

from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import GL_TRIANGLES, GL_TRIANGLE_FAN
from pyglet.math import Mat4, Vec3, Vec4, Vec2
from pyglet.gl import *

from primitives import CustomGroup, Line, TEX, PHONG, DEFAULT, NORMAL, GOURAUD
from model.obj import parse_obj_file
from texture import ambient_tex, diffuse_tex, specular_tex, roughness_tex, normal_tex

wht = (1.0, 1., 1., 1.0)


class RenderWindow(pyglet.window.Window):
    '''
    inherits pyglet.window.Window which is the default render window of Pyglet
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch = pyglet.graphics.Batch()
        self.batch2 = pyglet.graphics.Batch()
        '''
        View (camera) parameters
        '''
        self.cam_eye = Vec3(0, 0, 30)
        self.cam_target = Vec3(0, 0, 0)
        self.cam_vup = Vec3(0, 1, 0)
        self.view_mat = None
        '''
        Projection parameters
        '''
        self.z_near = 0.1
        self.z_far = 100
        self.fov = 60
        self.proj_mat = None

        self.shapes = []
        self.shapes2 = []

        self.light_src = Vec3(100, 100, 100)
        self.setup()

        self.using_texture = False

        self.wireframe = False
        self.rotate_y = 0
        self.rotate_x = 0

        self.light_rotate_y = 0
        self.light_rotate_x = 0

        self.mode = PHONG

    def setup(self) -> None:
        self.set_minimum_size(width=400, height=300)
        self.set_mouse_visible(True)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        # 1. Create a view matrix
        self.view_mat = Mat4.look_at(
            self.cam_eye, target=self.cam_target, up=self.cam_vup)

        # 2. Create a projection matrix
        self.proj_mat = Mat4.perspective_projection(
            aspect=self.width / self.height,
            z_near=self.z_near,
            z_far=self.z_far,
            fov=self.fov)

    def on_draw(self) -> None:
        self.clear()
        self.batch.draw()
        if self.wireframe:
            self.batch2.draw()

    def update(self, dt) -> None:
        light_src = Mat4.from_rotation(self.light_rotate_y * dt, Vec3(0, 1, 0)) @ Vec4(self.light_src.x, self.light_src.y, self.light_src.z, 1.)
        light_src = Mat4.from_rotation(self.light_rotate_x * dt, Vec3(1, 0, 0)) @ light_src
        self.light_src = light_src.xyz

        for i, shape in enumerate(self.shapes + self.shapes2):
            shape.transform_mat = Mat4.from_rotation(self.rotate_y * dt, Vec3(0, 1, 0)) @ shape.transform_mat
            shape.transform_mat = Mat4.from_rotation(self.rotate_x * dt, Vec3(1, 0, 0)) @ shape.transform_mat

            shape.shader_program['view'] = self.view_mat
            shape.shader_program['projection'] = self.proj_mat

            if i < len(self.shapes):
                shape.shader_program['camera_position'] = self.cam_eye
                shape.shader_program['light_position'] = self.light_src

                if i+1 == self.mode:
                    shape.visible = True
                else:
                    shape.visible = False


    def on_resize(self, width, height):
        glViewport(0, 0, *self.get_framebuffer_size())
        self.proj_mat = Mat4.perspective_projection(
            aspect=width / height, z_near=self.z_near, z_far=self.z_far, fov=self.fov)
        return pyglet.event.EVENT_HANDLED

    def add_shape(self, transform, vertice, indice, color):

        '''
        Assign a group for each shape
        '''
        shape = CustomGroup(transform, len(self.shapes2), mode=DEFAULT)
        shape.indexed_vertices_list = shape.shader_program.vertex_list_indexed(len(vertice) // 3, GL_TRIANGLES,
                                                                               batch=self.batch2,
                                                                               group=shape,
                                                                               indices=indice,
                                                                               vertices=('f', vertice),
                                                                               colors=('f', color))
        self.shapes2.append(shape)

    def add_shape_from_obj(self, file_name, wireframe=True):
        mesh = parse_obj_file(file_name)

        for shader in [PHONG, GOURAUD, TEX, NORMAL]:
            shape = CustomGroup(Mat4(), len(self.shapes), shader)
            count = len(mesh.vertices) // 3
            if shader == TEX:
                shape.indexed_vertices_list = shape.shader_program.vertex_list(
                    count,
                    GL_TRIANGLES,
                    batch=self.batch,
                    group=shape,
                    vertices=('f', mesh.vertices),
                    normals=('f', mesh.normals),
                    tex_coords=('f', mesh.tex_coords),
                )
            elif shader == NORMAL:
                tangents = []
                bitangents = []
                for i in range(len(mesh.vertices) // 9):
                    p0 = Vec3(*mesh.vertices[i*3:i*3+3])
                    p1 = Vec3(*mesh.vertices[i*3+3:i*3+6])
                    p2 = Vec3(*mesh.vertices[i*3+6:i*3+9])

                    u0 = Vec3(*mesh.tex_coords[i*2:i*2+2])
                    u1 = Vec3(*mesh.tex_coords[i*2+2:i*2+4])
                    u2 = Vec3(*mesh.tex_coords[i*2+4:i*2+6])

                    for j in range(3):
                        edge1 = p1 - p0
                        edge2 = p2 - p0
                        deltaUV1 = u1 - u0
                        deltaUV2 = u2 - u0

                        if deltaUV1.x*deltaUV2.y - deltaUV2.x*deltaUV1.y == 0:
                            tangent = [1.0, 0.0, 0.0]
                            bitangent = [0.0, 1.0, 0.0]
                        else:
                            f = 1.0 / (deltaUV1.x * deltaUV2.y - deltaUV2.x * deltaUV1.y)
                            tangent = [
                                f * (deltaUV2.y * edge1.x - deltaUV1.y * edge2.x),
                                f * (deltaUV2.y * edge1.y - deltaUV1.y * edge2.y),
                                f * (deltaUV2.y * edge1.z - deltaUV1.y * edge2.z),
                            ]
                            bitangent = [
                                f * (-deltaUV2.x * edge1.x + deltaUV1.x * edge2.x),
                                f * (-deltaUV2.x * edge1.y + deltaUV1.x * edge2.y),
                                f * (-deltaUV2.x * edge1.z + deltaUV1.x * edge2.z),
                            ]

                        tangents.extend(tangent)
                        bitangents.extend(bitangent)

                        p0, p1, p2 = p1, p2, p0
                        u0, u1, u2 = u1, u2, u0

                shape.indexed_vertices_list = shape.shader_program.vertex_list(
                    count,
                    GL_TRIANGLES,
                    batch=self.batch,
                    group=shape,
                    vertices=('f', mesh.vertices),
                    normals=('f', mesh.normals),
                    tangents=('f', tangents),
                    bitangents=('f', bitangents),
                    tex_coords=('f', mesh.tex_coords),
                )
            else:   # PHONG/GOURAUD
                shape.shader_program.vertex_list(
                    count,
                    GL_TRIANGLES,
                    batch=self.batch,
                    group=shape,
                    vertices=('f', mesh.vertices),
                    normals=('f', mesh.normals),
                    colors=('f', wht * count),
                )

            if shader == TEX or shader == NORMAL:
                shape.shader_program['light_intensity'] = 2000.0
                shape.shader_program['ambient_intensity'] = .1
                shape.shader_program['ambient_map'] = ambient_tex.id
                shape.shader_program['diffuse_map'] = diffuse_tex.id
                shape.shader_program['specular_map'] = specular_tex.id
                shape.shader_program['roughness_map'] = roughness_tex.id

                glActiveTexture(GL_TEXTURE0+ambient_tex.id)
                glBindTexture(ambient_tex.target, ambient_tex.id)
                glActiveTexture(GL_TEXTURE0+diffuse_tex.id)
                glBindTexture(diffuse_tex.target, diffuse_tex.id)
                glActiveTexture(GL_TEXTURE0+specular_tex.id)
                glBindTexture(specular_tex.target, specular_tex.id)
                glActiveTexture(GL_TEXTURE0+roughness_tex.id)
                glBindTexture(roughness_tex.target, roughness_tex.id)

                if shader == NORMAL:
                    shape.shader_program['normal_map'] = normal_tex.id
                    glActiveTexture(GL_TEXTURE0+normal_tex.id)
                    glBindTexture(normal_tex.target, normal_tex.id)
            else:
                shape.shader_program['light_intensity'] = 1000.0
                shape.shader_program['ambient_intensity'] = 1

            self.shapes.append(shape)

        if wireframe:
            for i in range(len(mesh.vertices) // 3):
                a = Vec3(*mesh.vertices[i*3:i*3+3])
                b = Vec3(*mesh.vertices[i*3+3:i*3+6])
                c = Vec3(*mesh.vertices[i*3+6:i*3+9])

                l1 = Line(a, b)
                l2 = Line(b, c)
                l3 = Line(c, a)
                self.add_shape(Mat4(), l1.vertices, l1.indices, l1.colors)
                self.add_shape(Mat4(), l2.vertices, l2.indices, l2.colors)
                self.add_shape(Mat4(), l3.vertices, l3.indices, l3.colors)

    def run(self):
        #pyglet.gl.glClearColor(1, 1, 1, 1)
        pyglet.clock.schedule_interval(self.update, 1 / 60)
        pyglet.app.run()
