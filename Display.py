import os
import platform
import moderngl,glm
import sys
import math
import numpy
import json
import numba
from Models import *
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

class window:
    VERSION = "1.0.0"
    MIN_SIZE = (500, 500)
    def __init__(self):
        try:
            print("Loading... Initializing")
            pygame.init()
            print("Loading... Getting Settings")
            if pygame.display.Info().current_h < self.MIN_SIZE[1] or pygame.display.Info().current_w < self.MIN_SIZE[0]:
                raise RuntimeError()

            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)
            self.init_settings = self.read_file("asset/settings.json")
            self.audio = audioengine(self.init_settings["settings"]["volume"])
            self.screen = pygame.display.set_mode(self.MIN_SIZE, pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
            self.game_name = self.init_settings["settings"]["game_name"]
            self.fov = self.init_settings["settings"]["fov"]
            
            print("Loading... Setting up")
            self.camera = Camera(self.fov,self)
            self.light = Light()
            
            self.game_icon = self.init_settings["settings"]["game-icon"]

            pygame.display.set_caption(self.game_name)
            if self.game_icon:
                pygame.display.set_icon(pygame.image.load(self.game_icon))
            else:
                pygame.display.set_icon(pygame.image.load("asset/game-icon.png"))
            self.ctx = moderngl.create_context(require=330)
            self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
            self.fps = self.init_settings["settings"]["fps"]
            self.clock = pygame.time.Clock()
            self.volume = self.init_settings["settings"]["volume"]
            self.mesh = Mesh(self)
            self.scene = Scene(self)
            self.scene_renderer = SceneRenderer(self)
            self.dt = 0

            print("COMPLETE")
            print(f"\nPython {sys.version.strip()}{platform.architecture()[0]}\n{platform.platform(terse=True)} {platform.architecture()[0]}")
            print(f"OpenGL {self.ctx.version_code}\nModernGL {moderngl.__version__}\nPygame {pygame.__version__}\nSDL {'.'.join(str(x) for x in pygame.get_sdl_version())}")
            print(f"GPU Vendor: {self.ctx.info['GL_VENDOR']}")
            print(f"GPU: {self.ctx.info['GL_RENDERER']}")
            print(f"GL DRIVER: {self.ctx.info['GL_VERSION']}\nEngine Version: {self.VERSION}")
            self.run()

        except (SystemError, OSError, RuntimeError, ChildProcessError) as e:
            print(e)
            sys.exit("\nExit Code: \n1\n")

    numba.njit()
    def run(self):
        focus = None
        self.update(focus)  
        while 1:
            self.update(focus) 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_settings("settings.json")
                    self.audio.cleanup()
                    self.mesh.destroy()
                    self.scene_renderer.destroy()
                    pygame.quit()
                    sys.exit("\nExit Code: \n0\n")
                elif event.type == pygame.WINDOWFOCUSLOST:
                    print("Energy Saver: True")
                    focus = False
                elif event.type == pygame.WINDOWFOCUSGAINED:
                    print("Energy Saver: False")
                    focus = True
                elif event.type == pygame.VIDEORESIZE:
                    self.resize(event)

    numba.njit()            
    def event_handler(self):
        key_up = pygame.key.get_just_released()
        key_down = pygame.key.get_just_pressed()
        if key_up[pygame.K_0]:
            print(f"\nDebug\nFPS: {math.ceil(pygame.time.Clock.get_fps(self.clock))}\nRefresh Rate: {pygame.display.get_current_refresh_rate()}")
        if key_down[pygame.K_LSHIFT]:
            self.camera.SPEED = 0.03
        if key_up[pygame.K_LSHIFT]:
            self.camera.SPEED = 0.1

            
    def resize(self,event):
        if pygame.key.get_just_released()[pygame.K_ESCAPE]:
            pygame.time.wait(pygame.display.toggle_fullscreen())
        else:
            h = max(self.MIN_SIZE[1],event.h)
            w = max(self.MIN_SIZE[0],event.w)
            self.screen = pygame.display.set_mode((w,h), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
    numba.njit()
    def update(self,state):
        if state:
            self.event_handler()
            self.camera.update(self.fov)
            self.lastime = self.clock.get_time()
            self.ctx.clear(color=(0.08, 0.16, 0.18))
            self.scene.update()
            self.scene_renderer.render()
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
    def volume_change(self,int):
        self.volume = int

class Camera:
    NEAR = 0.1
    FAR = 100
    SPEED = 0.1
    SENSITIVITY = 1
    def __init__(self, fov, app, position=(0, 0, 0), yaw=-90, pitch=0):
        self.fov = fov
        self.app = app
        self.aspect_ratio = pygame.display.get_surface().get_width()/pygame.display.get_surface().get_height()
        self.position = glm.vec3(position)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        self.yaw = yaw
        self.pitch = pitch
        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()

    def rotate(self):
        if pygame.mouse.get_pressed()[2]:
            rel_x, rel_y = pygame.mouse.get_rel()
            self.yaw += rel_x * self.SENSITIVITY
            self.pitch -= rel_y * self.SENSITIVITY
            self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self):
        yaw, pitch = glm.radians(self.yaw), glm.radians(self.pitch)

        self.forward.x = glm.cos(yaw) * glm.cos(pitch)
        self.forward.y = glm.sin(pitch)
        self.forward.z = glm.sin(yaw) * glm.cos(pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def update(self,fov):
        self.aspect_ratio = pygame.display.get_surface().get_width()/pygame.display.get_surface().get_height()
        self.fov = fov
        self.move()
        self.rotate()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def move(self):
        velocity = self.SPEED * self.app.dt
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.position += self.forward * velocity
        if keys[pygame.K_s]:
            self.position -= self.forward * velocity
        if keys[pygame.K_a]:
            self.position -= self.right * velocity
        if keys[pygame.K_d]:
            self.position += self.right * velocity
        if keys[pygame.K_q]:
            self.position -= self.up * velocity
        if keys[pygame.K_e]:
            self.position += self.up * velocity

    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    def get_projection_matrix(self):
        return glm.perspective(glm.radians(self.fov), self.aspect_ratio, self.NEAR, self.FAR)