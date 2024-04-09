from window import *
if __name__ == '__main__':
    win = window()
    win.audio.play_sound_3d('sound.mp3',(0,0),(0,0))
    win.run()