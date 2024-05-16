import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse, key

from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import GL_TRIANGLES, GL_TRIANGLE_FAN
from pyglet.math import Mat4, Vec3, Vec4
from pyglet.gl import *

import shader
from primitives import CustomGroup, Line, PHONG_TEX, PHONG_NO_TEX, DEFAULT
from model.obj import parse_obj_file

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

        self.wireframe = False
        self.rotate_y = 0
        self.rotate_x = 0

        self.light_rotate_y = 0
        self.light_rotate_x = 0

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

                shape.shader_program['light_intensity'] = 1000.0
                shape.shader_program['ambient_intensity'] = 1.0

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

    def add_shape_from_obj(self, file_name, shader=PHONG_TEX):
        mesh = parse_obj_file(file_name)

        shape = CustomGroup(Mat4(), len(self.shapes), shader)
        count = len(mesh.vertices) // 3
        shape.indexed_vertices_list = shape.shader_program.vertex_list(
            count,
            GL_TRIANGLES,
            batch=self.batch,
            group=shape,
            vertices=('f', mesh.vertices),
            normals=('f', mesh.normals),
            tex_coords=('f', mesh.tex_coords),
        ) if shader == PHONG_TEX else shape.shader_program.vertex_list(
            count,
            GL_TRIANGLES,
            batch=self.batch,
            group=shape,
            vertices=('f', mesh.vertices),
            normals=('f', mesh.normals),
            colors=('f', wht * count),
        )

        self.shapes.append(shape)

        it = iter(mesh.vertices)
        for x1, y1, z1, x2, y2, z2, x3, y3, z3 in zip(it, it, it, it, it, it, it, it, it):
            a = Vec3(x1, y1, z1)
            b = Vec3(x2, y2, z2)
            c = Vec3(x3, y3, z3)

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
