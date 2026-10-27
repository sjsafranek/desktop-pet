import time
import tkinter as tk

import conf
import path
from loader import SpriteSheetLoader



import threading
from pynput import mouse

# Function called whenever a mouse click happens anywhere on the screen
def make_on_click_handler(callback):
    def build(x, y, button, pressed):
        if pressed:
            callback({'x': x, 'y': y, 'button': button})
    return build


# Run the pynput mouse listener in a background thread so it doesn't block Tkinter
def start_mouse_listener(callback):
    handler = make_on_click_handler(callback)
    with mouse.Listener(on_click=handler) as listener:
        listener.join()

def make_mouse_listener(callback):
    def build():
        return start_mouse_listener(callback)
    return build

def registerOutsideClickHandler(callback):
    # Start the listener thread
    start_mouse_listener = make_mouse_listener(callback)
    listener_thread = threading.Thread(target=start_mouse_listener, daemon=True)
    listener_thread.start()



class SpriteApp:
    
    def __init__(self, config, root):
        self.config = config
        self.root = root
        self.root.title("Tkinter Sprite Sheet Animation")

        self.selected = True
        self.trajectory = []

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
        self.move_start_x = 0
        self.move_start_y = 0
        self.canvas.bind('<Button-1>', self._onClick)
        self.canvas.bind("<Double-Button-1>", self._onDoubleClick)
        self.canvas.bind('<B1-Motion>', self._onDrag)

        # # Handle sprite movement
        self.root.bind("<FocusOut>", self._onOutSideClick)

        self._showMessage("Hello!")

        self.mod_x = 1
        self.mod_y = 1

        # Start the animation loop
        self.animate()

        # listen to outside clicks
        registerOutsideClickHandler(self.travel)

    def travel(self, event):
        if self.is_selected:
            self.unselect()
            # print("travel", event)
            # x1 = self.canvas.winfo_rootx()
            # y1 = self.canvas.winfo_rooty()
            # print((x1,y1), (event['x'], event['y']))
            # origin = [int(i) for i in self.root.geometry().split('+')[1:]]
            # origin = [self.move_start_x, self.move_start_y]
            origin = [self.canvas.winfo_rootx(), self.canvas.winfo_rooty()]
            destination = [event['x'], event['y']]
            print(origin, destination)
            # self.trajectory = path.generate_constant_speed_trajectory([x1,y1], [event['x'], event['y']], 5, 0
            self.trajectory = path.generate_constant_speed_trajectory(origin, destination, 10, 1)
            self._setAnimation(self.config['events']['move'])

    def select(self):
        self.selected = True

    def unselect(self):
        self.selected = False

    @property
    def is_selected(self):
        return self.selected

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

    def _onOutSideClick(self, event):
        self.root.after(2500, lambda: self.unselect()) 

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
        # print(_from, _to)

    def _onClick(self, event):
        self.select()
        self.move_start_x = event.x
        self.move_start_y = event.y
        print(self.move_start_x, self.move_start_y)

    def _onDoubleClick(self, event):
        # print(event)
        handler = self.config['events'].get("dblclick", None)
        if handler:
            self._setAnimation(handler)

    def _onDrag(self, event):
        self.trajectory = []
        self._setAnimation(self.config['defaultAnimation'])
        new_x = event.x_root - self.move_start_x
        new_y = event.y_root - self.move_start_y
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
        if 0 != len(self.trajectory):
            point = self.trajectory.pop(0)
            # print(point)
            self.move(point[0], point[1])
        else:
            self._setAnimation(self.config['defaultAnimation'])

        # Check special conditions at end of animation
        if self._atAnimationEnd:
            if self.stop:
                self.root.quit()
            if not self.animation.loop:
                self._setAnimation(self.config['defaultAnimation'])

