import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse, key
from pyglet.math import Mat4, Vec3


class Control:
    """
    Control class controls keyboard & mouse inputs.
    """

    def __init__(self, window):
        window.on_key_press = self.on_key_press
        window.on_key_release = self.on_key_release
        window.on_mouse_motion = self.on_mouse_motion
        window.on_mouse_drag = self.on_mouse_drag
        window.on_mouse_press = self.on_mouse_press
        window.on_mouse_release = self.on_mouse_release
        window.on_mouse_scroll = self.on_mouse_scroll
        self.window = window
        self.setup()

    def setup(self):
        pass

    def update(self, vector):
        pass

    def on_key_press(self, symbol, modifier):
        if symbol == pyglet.window.key.LEFT:
            self.window.rotate_y = -1
        elif symbol == pyglet.window.key.RIGHT:
            self.window.rotate_y = 1
        elif symbol == pyglet.window.key.UP:
            self.window.rotate_x = -1
        elif symbol == pyglet.window.key.DOWN:
            self.window.rotate_x = 1

    def on_key_release(self, symbol, modifier):
        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()
        elif symbol == pyglet.window.key.SPACE:
            self.window.wireframe = not self.window.wireframe
        elif symbol == pyglet.window.key.LEFT or symbol == pyglet.window.key.RIGHT:
            self.window.rotate_y = 0
        elif symbol == pyglet.window.key.UP or symbol == pyglet.window.key.DOWN:
            self.window.rotate_x = 0

    def on_mouse_motion(self, x, y, dx, dy):
        # TODO:
        pass

    def on_mouse_press(self, x, y, button, modifier):
        # TODO:
        pass

    def on_mouse_release(self, x, y, button, modifier):
        # TODO:
        pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifier):
        # TODO:
        pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # TODO:
        pass