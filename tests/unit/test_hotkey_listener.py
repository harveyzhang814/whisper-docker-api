import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/utils')))
from hotkey_listener import HotkeyListener

if __name__ == "__main__":
    print("Manual test: Please press ctrl+r to trigger the hotkey listener.")
    listener = HotkeyListener()
    listener.start()
    print("Listener exited.") 