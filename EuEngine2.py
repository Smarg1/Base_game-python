from Display import *
from threading import Thread

def audio_management():
    audio.play_sound_3d("asset/sounds/sound.mp3", (0, 0), (0, 0))

if __name__ == '__main__':
    win = window()
    audio = win.audio
    audio_thread = Thread(target=audio_management)
    audio_thread.start()
    win.run()
    audio_thread.join()
