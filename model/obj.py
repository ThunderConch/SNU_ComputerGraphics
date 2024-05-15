import os

import pyglet

from pyglet.gl import GL_TRIANGLES
from pyglet.util import asstr

from pyglet.model import Model, Material, MaterialGroup, TexturedMaterialGroup
from pyglet.model.codecs import ModelDecodeException, ModelDecoder


class Mesh:
    def __init__(self, name):
        self.name = name
        self.indices = []
        self.vertices = []
        self.normals = []
        self.tex_coords = []
        self.colors = []


def parse_obj_file(filename, file=None):
    try:
        if file is None:
            with open(filename, 'r') as f:
                file_contents = f.read()
        else:
            file_contents = asstr(file.read())
    except (UnicodeDecodeError, OSError):
        raise ModelDecodeException

    mesh = Mesh(name='')

    vertices = [[0., 0., 0.]]
    normals = [[0., 0., 0.]]
    tex_coords = [[0., 0.]]

    for line in file_contents.splitlines():

        if line.startswith('#'):
            continue
        values = line.split()
        if not values:
            continue

        if values[0] == 'v':
            vertices.append(list(map(float, values[1:4])))
        elif values[0] == 'vn':
            normals.append(list(map(float, values[1:4])))
        elif values[0] == 'vt':
            tex_coords.append(list(map(float, values[1:3])))
        elif values[0] == 'f':
            # For fan triangulation, remember first and latest vertices
            n1 = None
            nlast = None
            t1 = None
            tlast = None
            v1 = None
            vlast = None

            for i, v in enumerate(values[1:]):
                v_i, t_i, n_i = (list(map(int, [j or 0 for j in v.split('/')])) + [0, 0])[:3]
                if v_i < 0:
                    v_i += len(vertices) - 1
                if t_i < 0:
                    t_i += len(tex_coords) - 1
                if n_i < 0:
                    n_i += len(normals) - 1

                mesh.normals += normals[n_i]
                mesh.tex_coords += tex_coords[t_i]
                mesh.vertices += vertices[v_i]

                if i >= 3:
                    # Triangulate
                    mesh.normals += n1 + nlast
                    mesh.tex_coords += t1 + tlast
                    mesh.vertices += v1 + vlast

                if i == 0:
                    n1 = normals[n_i]
                    t1 = tex_coords[t_i]
                    v1 = vertices[v_i]
                nlast = normals[n_i]
                tlast = tex_coords[t_i]
                vlast = vertices[v_i]
    return mesh