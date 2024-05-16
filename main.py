from render import RenderWindow
from primitives import PHONG_NO_TEX, PHONG_TEX, GOURAUD_NO_TEX
from control import Control

if __name__ == '__main__':
    width = 1280
    height = 720

    # Render window.
    renderer = RenderWindow(width, height, "PA3", resizable=True)
    renderer.set_location(200, 200)

    # Keyboard/Mouse control. Not implemented yet.
    controller = Control(renderer)

    renderer.add_shape_from_obj('model/Free_rock/Free_rock.obj', shader=GOURAUD_NO_TEX)

    #draw shapes
    renderer.run()
