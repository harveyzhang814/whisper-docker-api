import sys
from src.feature.fea_mic_standard import MicStandardAppHotKey

def main():
    app = MicStandardAppHotKey(duration=60, output_format="json", hotkey=("ctrl", "t"))
    app.start()

if __name__ == "__main__":
    main() 