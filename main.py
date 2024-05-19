from render import RenderWindow
from control import Control

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Example script for parameter branching")
    parser.add_argument('--wireframe', type=bool, help='draw wireframe. default: False')

    args = parser.parse_args()

    wireframe = True if args.wireframe else False
    width = 1280
    height = 720

    # Render window.
    renderer = RenderWindow(width, height, "PA3", resizable=True)
    renderer.set_location(200, 200)

    # Keyboard/Mouse control. Not implemented yet.
    controller = Control(renderer)

    renderer.add_shape_from_obj('model/Free_rock/Free_rock.obj', wireframe=wireframe)

    #draw shapes
    renderer.run()
