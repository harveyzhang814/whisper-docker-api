from pynput import keyboard
import threading

class HotkeyListener:
    def __init__(self, hotkey=('ctrl', 'r')):
        self.hotkey = hotkey
        self._listener = None
        self._thread = None
        self._hotkey_pressed = False
        self._on_hotkey = None
        self._stop_event = threading.Event()
        print(f"[HotkeyListener] Initialized with hotkey: {self.hotkey}")

    def set_callback(self, callback):
        """Register a callback to be called when hotkey is triggered."""
        self._on_hotkey = callback
        print("[HotkeyListener] Callback set.")

    def _parse_hotkey(self):
        key_map = {
            'ctrl': keyboard.Key.ctrl,
            'shift': keyboard.Key.shift,
            'alt': keyboard.Key.alt,
            'cmd': keyboard.Key.cmd,
            'command': keyboard.Key.cmd,
            'option': keyboard.Key.alt,
            'control': keyboard.Key.ctrl,
        }
        combination = set()
        for key in self.hotkey:
            k = key.lower()
            if k in key_map:
                combination.add(key_map[k])
            elif len(k) == 1:
                combination.add(keyboard.KeyCode.from_char(k))
            else:
                raise ValueError(f"Unsupported hotkey part: {key}")
        return combination

    def _on_activate(self):
        if not self._hotkey_pressed:
            print(f"[HotkeyListener] Hotkey {self.hotkey} detected, listener stopped.")
            self._hotkey_pressed = True
            if self._on_hotkey:
                print("[HotkeyListener] Executing callback...")
                self._on_hotkey()
            self.stop()

    def _run_listener(self):
        print("[HotkeyListener] Listener thread running.")
        combination = self._parse_hotkey()
        current_keys = set()

        def on_press(key):
            print(f"[HotkeyListener] Key pressed: {key}")
            # 处理Key和KeyCode
            if isinstance(key, keyboard.Key):
                current_keys.add(key)
            elif isinstance(key, keyboard.KeyCode):
                current_keys.add(key)
            if combination.issubset(current_keys):
                self._on_activate()

        def on_release(key):
            print(f"[HotkeyListener] Key released: {key}")
            if isinstance(key, keyboard.Key):
                current_keys.discard(key)
            elif isinstance(key, keyboard.KeyCode):
                current_keys.discard(key)
            if self._stop_event.is_set():
                print("[HotkeyListener] Stop event detected in on_release.")
                return False

        self._listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self._listener.start()
        self._listener.join()
        print("[HotkeyListener] Listener thread exiting.")

    def start(self):
        if self._thread and self._thread.is_alive():
            print("[HotkeyListener] Listener thread already running.")
            return
        self._hotkey_pressed = False
        self._stop_event.clear()
        print("[HotkeyListener] Starting listener thread...")
        self._thread = threading.Thread(target=self._run_listener, daemon=True)
        self._thread.start()

    def stop(self):
        print("[HotkeyListener] Stopping listener thread...")
        self._stop_event.set()
        if self._listener:
            self._listener.stop()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        print("[HotkeyListener] Listener thread stopped.") 