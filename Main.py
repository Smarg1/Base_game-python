from window import *
from threading import Thread

def play_audio(audio_engine):
    audio_engine.play_sound_3d('sound.mp3', (0, 0), (0, 0))

if __name__ == '__main__':
    win = window()
    audio_thread = Thread(target=play_audio, args=(win.audio,))
    audio_thread.start()
    win.run()
    audio_thread.join()
