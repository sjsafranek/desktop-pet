import tkinter as tk

import conf
from loader import SpriteSheetLoader


class SpriteApp:
    def __init__(self, config, root):
        self.root = root
        self.root.title("Tkinter Sprite Sheet Animation")

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
        self.sprite_id = self.canvas.create_image(width*conf.SCALING, height*conf.SCALING, image=self.frames[self.current_frame])

        # Create the context menu (tearoff=0 prevents a separate floating window)
        self.menu = tk.Menu(self.root, tearoff=0)
        for name in self._spriteSheet.animations:
            self._add_animation_option_to_menu(name)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=root.quit)
        self.canvas.bind("<Button-3>", self._onContextMenu)

        # Track window movements
        self.start_x = 0
        self.start_y = 0
        self.canvas.bind('<Button-1>', self._onClick)
        self.canvas.bind('<B1-Motion>', self._onDrag)

        self.show_temporary_text("Hello!")

        # Start the animation loop
        self.animate()

    def show_temporary_text(self, message, timeout_in_milliseconds=3000):
        text_id = self.canvas.create_text(50, 60, text=message, fill="white", font=("Arial", 24))
        self.root.after(timeout_in_milliseconds, lambda: self.canvas.delete(text_id))

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
        animation = self._spriteSheet.getAnimationByName(self.current_animation_name)
        self.frames = animation.frames
        self.fps = animation.fps

    def move(self, new_x, new_y):
        self.root.geometry(f'+{new_x}+{new_y}')

    def _onClick(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def _onDrag(self, event):
        new_x = event.x_root - self.start_x
        new_y = event.y_root - self.start_y
        self.move(new_x, new_y)

    def animate(self):
        # Move to the next frame loop index
        self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Update the canvas image item with the new frame
        self.canvas.itemconfig(self.sprite_id, image=self.frames[self.current_frame])
        
        # Schedule the next frame update (100ms delay = 10 frames per second)
        delay = int(1000/self.fps)
        self.root.after(delay, self.animate)
