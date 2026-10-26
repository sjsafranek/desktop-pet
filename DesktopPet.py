import sys
import argparse
import json
import tkinter as tk

from pet import SpriteApp


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Desktop Pet")
    parser.add_argument("config", help="config file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Turn on verbose mode")
    args = parser.parse_args()

    # load config file
    with open(args.config, 'r') as fh:
        config = json.load(fh)

    try:
        # Create desktop application
        root = tk.Tk()
        root.config(highlightbackground='black')
        root.overrideredirect(True)
        root.wm_attributes('-transparentcolor', 'black')
        app = SpriteApp(config, root)
        root.mainloop()

    except KeyboardInterrupt:
        print("Shutdown signal received. Cleaning up resources...")
        # Add your cleanup code here (e.g., closing file handles, saving state)
        
    # except Exception as err:
    #     print(err)

    # finally:
    #     print("Application safely stopped.")
    #     sys.exit(0)

