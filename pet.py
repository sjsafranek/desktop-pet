import time
import tkinter as tk

import conf
from loader import SpriteSheetLoader


class SpriteApp:
    
    def __init__(self, config, root):
        self.config = config
        self.root = root
        self.root.title("Tkinter Sprite Sheet Animation")

        self.text_id = None

        width = config['frameSize']['w']
        height = config['frameSize']['h']

        # Create canvas to draw the sprite
        self.canvas = tk.Canvas(root, width=width*conf.SCALING*2, height=height*conf.SCALING*2, bg='black', bd=0, highlightthickness=0)
        self.canvas.pack()

        # Initialize the sprite loader (Replace with your own filename and frame sizes)
        # Assuming each cell in your sprite sheet is 64x64 pixels
        self._spriteSheet = SpriteSheetLoader(config)
        self._setAnimation(config['defaultAnimation'])

        # Load all frames from row 0 (assuming it has 4 animation frames)
        self.current_frame = 0

        # Draw the initial frame on the canvas
        self.sprite_id = self.canvas.create_image(width*conf.SCALING, height*conf.SCALING, image=self.animation.frames[self.current_frame])

        # Create the context menu (tearoff=0 prevents a separate floating window)
        self.menu = tk.Menu(self.root, tearoff=0)
        shutdownAnimationName = config.get('shutdownAnimation', None)
        for name in self._spriteSheet.animations:
            if shutdownAnimationName == name:
                continue
            self._add_animation_option_to_menu(name)
        self.menu.add_separator()
        # self.menu.add_command(label="Exit", command=root.quit)
        self.menu.add_command(label="Exit", command=self.shutdown)
        self.canvas.bind("<Button-3>", self._onContextMenu)

        # Track window movements
        self.start_x = 0
        self.start_y = 0
        self.canvas.bind('<Button-1>', self._onClick)
        self.canvas.bind("<Double-Button-1>", self._onDoubleClick)
        self.canvas.bind('<B1-Motion>', self._onDrag)

        self._showMessage("Hello!")

        self.mod_x = 1
        self.mod_y = 1

        # Start the animation loop
        self.animate()

    @property
    def stop(self):
        return self.current_animation_name == self.config['shutdownAnimation'] 

    @property
    def _atAnimationEnd(self):
        return self.current_frame == len(self.animation.frames)-1

    def shutdown(self):
        self._setAnimation(self.config['defaultAnimation'])
        self._showMessage("Bye!")
        self.root.after(1500, lambda: self._setAnimation(self.config['shutdownAnimation']))

    def _showMessage(self, message, timeout_in_milliseconds=3000):
        self.canvas.delete(self.text_id)
        text_id = self.canvas.create_text(50, 60, text=message, fill="white", font=("Arial", 24))
        self.root.after(timeout_in_milliseconds, lambda: self.canvas.delete(text_id))
        self.text_id = text_id

    def _add_animation_option_to_menu(self, name):
        self.menu.add_command(label=name, command=lambda: self._setAnimation(name))

    def _onContextMenu(self, event):
        try:
            # Display the context menu at the mouse pointer's exact screen location
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Clean up the focus grab once an option is selected or dismissed
            self.menu.grab_release()

    def _setAnimation(self, name):
        self.current_animation_name = name
        self.animation = self._spriteSheet.getAnimationByName(self.current_animation_name)
        self.current_frame = 0

    def move(self, new_x, new_y):
        _from = self.root.geometry()
        self.root.geometry(f'+{new_x}+{new_y}')
        _to = self.root.geometry()
        print(_from, _to)

    def _onClick(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def _onDoubleClick(self, event):
        # print(event)
        handler = self.config['events'].get("dblclick", None)
        if handler:
            self._setAnimation(handler)

    def _onDrag(self, event):
        new_x = event.x_root - self.start_x
        new_y = event.y_root - self.start_y
        self.move(new_x, new_y)

    def animate(self):
        # Move to the next frame loop index
        self.current_frame = (self.current_frame + 1) % len(self.animation.frames)

        # Update the canvas image item with the new frame
        self.canvas.itemconfig(self.sprite_id, image=self.animation.frames[self.current_frame])
        
        # Schedule the next frame update (100ms delay = 10 frames per second)
        delay = int(1000/self.animation.fps)
        self.root.after(delay, self.animate)

        # Handle movement
        point = [int(i) for i in self.root.geometry().split('+')[1:]]
        new_x = point[0]
        new_y = point[1]
        should_move = False

        if self.animation.dx:
            screen_width = self.root.winfo_screenwidth()
            ratio = ((screen_width-point[0])/screen_width)
            if 0.15 > ratio:
                self.mod_x = -1
            elif 0.90 < ratio:    # Why isnt this centered??
                self.mod_x = 1
            new_x = point[0] + (self.animation.dx * self.mod_x)
            should_move = True

        if self.animation.dy:
            screen_height = self.root.winfo_screenheight()
            ratio = ((screen_height-point[1])/screen_height)
            if 0.15 > ratio:
                self.mod_y = -1
            elif 0.80 < ratio:    # Why isnt this centered??
                self.mod_y = 1
            new_y = point[1] + (self.animation.dy * self.mod_y)
            should_move = True
            
        if should_move:
            self.move(new_x, new_y)

        # Check special conditions at end of animation
        if self._atAnimationEnd:
            if self.stop:
                self.root.quit()
            if not self.animation.loop:
                self._setAnimation(self.config['defaultAnimation'])

