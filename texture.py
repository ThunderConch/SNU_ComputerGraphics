from pyglet.gl import *
import pyglet


def load_texture(image_path):
    texture = pyglet.image.load(image_path).get_texture()
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture.id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return texture


ambient_tex = load_texture('model/Free_rock/Free_rock_tex/Free_rock_Mixed_AO.jpg')
diffuse_tex = load_texture('model/Free_rock/Free_rock_tex/Free_rock_Base_Color.jpg')
specular_tex = load_texture('model/Free_rock/Free_rock_tex/Free_rock_Specular.jpg')
roughness_tex = load_texture('model/Free_rock/Free_rock_tex/Free_rock_Roughness.jpg')
normal_tex = load_texture('model/Free_rock/Free_rock_tex/Free_rock_Normal_OpenGL.jpg')



