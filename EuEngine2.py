from Display import *
if __name__ == '__main__':
    win = window()
    audio = win.audio
    audio.play_sound_3d("asset/sounds/sound.mp3", (0, 0), (0, 0))