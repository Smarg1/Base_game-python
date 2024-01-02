from window import *
if __name__ == '__main__':
    win = window()
    audio = audioengine()
    audio.play_sound_3d('song.mp3',(0,0),(0,0))
    win.run()