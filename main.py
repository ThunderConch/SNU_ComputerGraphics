import pyglet
from pyglet.math import Mat4, Vec3

from render import RenderWindow
from primitives import Cube, Sphere, NON_TEXTURED
from control import Control

if __name__ == '__main__':
    width = 1280
    height = 720

    # Render window.
    renderer = RenderWindow(width, height, "Hello Pyglet", resizable = True)
    renderer.set_location(200, 200)

    # Keyboard/Mouse control. Not implemented yet.
    controller = Control(renderer)

    renderer.add_shape_from_obj('model/Free_rock/Free_rock.obj', textured=NON_TEXTURED)

    #draw shapes
    renderer.run()
