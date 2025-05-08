from pynput import keyboard
import sys
from src.feature.fea_mic_standard import MicStandardTranscrible

def start_recording():
    feature = MicStandardTranscrible(duration=60, output_format="json")
    print("Start recording... (auto exit after recording ends)")
    formatted_text = feature.run()
    print("Formatted text:", formatted_text)

def main():
    ctrl_pressed = {"left": False, "right": False}
    recording_started = [False]  # 用列表包裹以便闭包修改

    def on_press(key):
        # 记录ctrl按下
        if key == keyboard.Key.ctrl_l:
            ctrl_pressed["left"] = True
        if key == keyboard.Key.ctrl_r:
            ctrl_pressed["right"] = True
        # Ctrl+T 启动录音
        if (ctrl_pressed["left"] or ctrl_pressed["right"]) and key == keyboard.KeyCode.from_char('t'):
            if not recording_started[0]:
                recording_started[0] = True
                print("[Hotkey] Recording started.")
                start_recording()
                print("[Info] Recording finished. Exiting main program.")
                sys.exit(0)

    def on_release(key):
        if key == keyboard.Key.ctrl_l:
            ctrl_pressed["left"] = False
        if key == keyboard.Key.ctrl_r:
            ctrl_pressed["right"] = False

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("[Info] Press Ctrl+T to start recording. Program will exit after recording ends.")
        listener.join()

if __name__ == "__main__":
    main() 