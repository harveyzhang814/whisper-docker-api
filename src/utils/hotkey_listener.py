from pynput import keyboard

class HotkeyListener:
    def __init__(self, hotkey=('ctrl', 'r')):
        self.hotkey = hotkey
        self._listener = None
        self._hotkey_pressed = False

    def _on_activate(self):
        print(f"Hotkey {self.hotkey[0]}+{self.hotkey[1]} detected, listener stopped.")
        self._hotkey_pressed = True
        if self._listener:
            self._listener.stop()

    def start(self):
        # Define the hotkey combination for pynput
        combination = {keyboard.Key.ctrl, keyboard.KeyCode.from_char('r')}
        current_keys = set()

        def on_press(key):
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                current_keys.add(keyboard.Key.ctrl)
            elif hasattr(key, 'char') and key.char == 'r':
                current_keys.add(keyboard.KeyCode.from_char('r'))
            if combination.issubset(current_keys):
                self._on_activate()

        def on_release(key):
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                current_keys.discard(keyboard.Key.ctrl)
            elif hasattr(key, 'char') and key.char == 'r':
                current_keys.discard(keyboard.KeyCode.from_char('r'))

        self._listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self._listener.start()
        self._listener.join() 