from PIL import Image
from PIL import ImageTk

import conf
from animation import SpriteSheetAnimation


class SpriteSheetLoader:

    def __init__(self, config):
        filename = config.get('image')
        self.sheet = Image.open(filename)
        self._animations = {}
        for name in config['animations']:
            animation = config['animations'][name]
            frames = [frame for frame in self._loadFrames(animation, config['frameSize'])]
            self._animations[name] = SpriteSheetAnimation(name, frames=frames, fps=animation['fps'])

    def _loadFrames(self, animation, size):
        frames = []
        for rect in animation['frames']:
            left = rect['x']
            top = rect['y']
            right = left + rect['w']
            bottom = top + rect['h']
            cropped = self.sheet.crop((left, top, right, bottom))              
            cropped = cropped.resize((size['w']*conf.SCALING, size['h']*conf.SCALING), conf.IMAGE_RESAMPLING_ALGORITHM)
            frame = ImageTk.PhotoImage(cropped)
            yield frame

    @property
    def animations(self):
        return list(self._animations.keys())
    
    def getAnimationByName(self, name):
        return self._animations.get(name)
