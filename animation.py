
class SpriteSheetAnimation():
    
    def __init__(self, name, frames=[], config={}):
        self.name = name
        self.frames = frames
        self.config = config

    def add(frame):
        self.frames.append(frame)

    @property
    def fps(self):
        return self.config.get('fps', 4)

    @property
    def loop(self):
        return self.config.get('loop', True)

    @property
    def dx(self):
        return self.config.get('dx', 0)

    @property
    def dy(self):
        return self.config.get('dy', 0)

