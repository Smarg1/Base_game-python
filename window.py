import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame,moderngl,sys,math,numpy,json
from renderer import *

class window:
    def __init__(self):
        print(f"OpenGL 3.3\nModernGL {moderngl.__version__}")
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        self.init_settings = self.read_file("settings.json")
        self.audio = audioengine(self.init_settings["settings"]["volume"])
        self.screen = pygame.display.set_mode((0,0),pygame.OPENGL|pygame.DOUBLEBUF|pygame.FULLSCREEN)
        self.game_name = self.init_settings["settings"]["game_name"]
        self.fov = self.init_settings["settings"]["fov"]
        self.camera = camera(self.fov)
        self.light = light()
        #pygame.display.set_icon(pygame.image.load('game_logo.png'))
        pygame.display.set_caption(self.game_name)
        self.ctx = moderngl.create_context(require=330)
        self.ctx.enable(moderngl.DEPTH_TEST|moderngl.CULL_FACE|moderngl.BLEND)
        self.fps = self.init_settings["settings"]["fps"]
        self.clock = pygame.time.Clock()
        self.volume = self.init_settings["settings"]["volume"]
        self.scene = Cube(self,numpy.array([(-0.6,-0.8,0.0),(0.6,-0.8,0.0),(0.0,0.8,0.0)],dtype="f4"))
        self.dt = 0
    def run(self):
        while 1:
            self.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_settings("settings.json")
                    self.audio.cleanup()
                    self.scene.destroy()
                    pygame.quit()
                    sys.exit()
    def update(self):
        self.lastime = self.clock.get_time()
        self.ctx.clear(color=(0.3, 0.7, 0.8))
        self.scene.render()
        self.clock.tick(self.fps * self.dt)
        pygame.display.flip()
        self.lastime = self.clock.get_time()
        self.dt = (self.clock.get_time() - self.lastime)+1
    def sort(self,list):
        if len(list)<=1:
            return list
        pivot = list[len(list)//2]
        left = [i for i  in list if i < pivot]
        middle = [j for j in list if j == pivot]
        right = [k for k in list if k > pivot]
        return self.sort(left)+middle+self.sort(right)
    def read_file(self,file):
       with open(file,"r") as f:
           return json.load(f)
    def save_settings(self,file):
        with open(file,"w") as f:
            json.dump(self.init_settings, f, indent=4)

class audioengine:
    def __init__(self,volume):
        pygame.mixer.pre_init(frequency=44100, size=16,buffer=8192)
        pygame.init()
        pygame.mixer.set_num_channels(32)
        self.volume = volume
    def play_sound_3d(self, file, position, listener_position):
        default_output = pygame.mixer.get_init()[1]
        if default_output in (None, 'built-in'):
            sound = pygame.mixer.Sound(file)
            dx = listener_position[0] - position[0]
            dy = listener_position[1] - position[1]
            distance = math.sqrt(dx**2 + dy**2)
            max_distance = 500.0
            attenuation = max(1.0 - distance / max_distance, 0.0)
            pan = dx / max_distance
            channel = sound.play()
            channel.set_volume(attenuation * (1 - pan) + self.volume, (attenuation * pan)+ self.volume)
        else:
            sound = pygame.mixer.Sound(file)
            sound.set_volume(self.volume)
            sound.play()
    def cleanup(self):
        pygame.mixer.stop()
        pygame.mixer.quit()