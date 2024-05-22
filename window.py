import os
import platform
import moderngl
import sys
import math
import numpy
import json
from renderer import *
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

class window:
    def __init__(self):
        try:
            print("Loading... Initializing")
            pygame.init()
            print("Loading... Getting Settings")

            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

            self.init_settings = self.read_file("settings.json")
            self.audio = audioengine(self.init_settings["settings"]["volume"])
            self.screen = pygame.display.set_mode((0, 0), pygame.OPENGLBLIT | pygame.DOUBLEBUF | pygame.FULLSCREEN)
            self.game_name = self.init_settings["settings"]["game_name"]
            self.fov = self.init_settings["settings"]["fov"]

            print("Loading... Setting up")
            self.camera = camera(self.fov)
            self.light = light()
            self.game_icon = self.init_settings["settings"]["game-icon"]

            pygame.display.set_caption(self.game_name)
            if self.game_icon:
                pygame.display.set_icon(pygame.image.load(self.game_icon))
            else:
                pygame.display.set_icon(pygame.image.load("game-icon.png"))
            self.ctx = moderngl.create_context(require=330)
            self.ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE | moderngl.BLEND)
            self.fps = self.init_settings["settings"]["fps"]
            self.clock = pygame.time.Clock()
            self.volume = self.init_settings["settings"]["volume"]
            self.scene = Cube(self, numpy.array([(-0.6, -0.8, 0.0), (0.6, -0.8, 0.0), (0.0, 0.8, 0.0)], dtype="f4"))
            self.dt = 0

            print("COMPLETE")
            print(f"\nPython {sys.version.strip()}{platform.architecture()[0]}\n{platform.platform(terse=True)} {platform.architecture()[0]}")
            print(f"OpenGL {self.ctx.version_code}\nModernGL {moderngl.__version__}\nPygame {pygame.__version__}\nSDL {'.'.join(str(x) for x in pygame.get_sdl_version())}")
            print(f"GPU Vendor: {self.ctx.info['GL_VENDOR']}")
            print(f"GPU: {self.ctx.info['GL_RENDERER']}")
            print(f"GL DRIVER: {self.ctx.info['GL_VERSION']}\n")

        except (SystemError, OSError, RuntimeError, ChildProcessError) as e:
            print(e)
            sys.exit("\nExit Code: \n1")

    def run(self):
        focus = None

        while 1:
            self.update(focus)  
            self.event_handler()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_settings("settings.json")
                    self.audio.cleanup()
                    self.scene.destroy()
                    pygame.quit()
                    sys.exit("\nExit Code: \n0")
                elif event.type == pygame.WINDOWLEAVE:
                    print("Energy Saver: True")
                    focus = False
                elif event.type == pygame.WINDOWENTER:
                    print("Energy Saver: False")
                    focus = True
                    
    def event_handler(self):
        key_up = pygame.key.get_just_released()
        key_down = pygame.key.get_just_pressed()
        if key_up[pygame.K_0]:
            print(f"\nDebug\nFPS: {math.ceil(pygame.time.Clock.get_fps(self.clock))}\n")

    def update(self,state):
        if state:
            self.lastime = self.clock.get_time()
            self.ctx.clear(color=(0.3, 0.7, 0.8))
            self.scene.render()
            self.clock.tick(self.fps)
            pygame.display.flip()
            self.lastime = self.clock.get_time()
            self.dt = (self.clock.get_time() - self.lastime) + 1
        else:
            pygame.time.wait(100)

    def sort(self, list):
        if len(list) <= 1:
            return list
        pivot = list[len(list) // 2]
        left = [i for i in list if i < pivot]
        middle = [j for j in list if j == pivot]
        right = [k for k in list if k > pivot]
        return self.sort(left) + middle + self.sort(right)

    def read_file(self, file):
        with open(file, "r") as f:
            return json.load(f)

    def save_settings(self, file):
        with open(file, "w") as f:
            json.dump(self.init_settings, f, indent=4)

class audioengine:
    def __init__(self, volume):
        pygame.mixer.pre_init(frequency=44100, size=16, buffer=8192)
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
            channel.set_volume(attenuation * (1 - pan) + self.volume, (attenuation * pan) + self.volume)
        else:
            sound = pygame.mixer.Sound(file)
            sound.set_volume(self.volume)
            sound.play()

    def cleanup(self):
        pygame.mixer.stop()
        pygame.mixer.quit()
