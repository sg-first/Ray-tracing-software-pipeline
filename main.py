import pygame
import math
import threading 
import os
import sys

from Hitable import *
from Material import *
from Camera import *
from Rendering import *

currentWDir = os.getcwd()
print( 'current working directory: {}'.format( str(currentWDir) ) )
fileDir = os.path.dirname(os.path.abspath(__file__)) # det the directory of this file
print( 'current location of self: {}'.format( str(fileDir) ) )
parentDir = os.path.abspath(os.path.join(fileDir, os.pardir)) # get the parent directory of this file
sys.path.insert(0, parentDir)
print( 'insert system directory: {}'.format( str(parentDir) ) )
os.chdir( fileDir )
baseWDir = os.getcwd()
print( 'changed current working directory: {}'.format( str(baseWDir) ) )
print ( '' )

# globals
BLACK = (0, 0, 0)
RED = (255, 0, 0)


###################################################################################################
# write PPM file
def writeFilePPM(surface, name):
    try:
        nx, ny = surface.get_size()
        file = open(name + '.ppm', "w")
    except:
        return 
    file.write("P3\n" + str(nx) + " " + str(ny) + "\n255\n")
    for y in range(ny):
        for x in range(nx):
            c = surface.get_at((x, y))
            file.write(str(c[0]) + " " + str(c[1]) + " " + str(c[2]) + " ")
        file.write("\n")
    file.close()


###################################################################################################
# Main application window and process
class Application:

    #----------------------------------------------------------------------------------------------
    # ctor
    def __init__(self, size = (800, 600), caption = "PyGame window"):

        # state attributes
        self.__run = True

        # PyGame initialization
        pygame.init()
        self.__init_surface(size)
        pygame.display.set_caption(caption)
        
        self.__clock = pygame.time.Clock()

    #----------------------------------------------------------------------------------------------
    # dtor
    def __del__(self):
        pygame.quit()

    #----------------------------------------------------------------------------------------------
    # set the size of the application window
    @property
    def size(self):
        return self.__surface.get_size()

    #----------------------------------------------------------------------------------------------
    # get window surface
    @property
    def surface(self):
        return self.__surface

    #----------------------------------------------------------------------------------------------
    # get and set application 
    @property
    def image(self):
        return self.__image
    @image.setter
    def image(self, image):
        self.__image = image

    #----------------------------------------------------------------------------------------------
    # main loop of the application
    def run(self, render, samples_per_pixel = 100, samples_update_rate = 1, capture_interval_s = 0):
        size = self.__surface.get_size()
        render.start(size, samples_per_pixel, samples_update_rate)
        finished = False
        start_time = None
        capture_i = 0
        while self.__run:
            self.__clock.tick(60)
            self.__handle_events()
            current_time = pygame.time.get_ticks()
            if start_time == None:
                start_time = current_time + 1000
            if not self.__run:
                render.stop()
            elif size != self.__surface.get_size():
                size = self.__surface.get_size()
                render.stop()
                render.start(size, samples_per_pixel, samples_update_rate)   
            capture_frame = capture_interval_s > 0 and current_time >= start_time + capture_i * capture_interval_s * 1000
            frame_img = self.draw(render, capture_frame)
            if frame_img:
                pygame.image.save(frame_img, "capture/img_" + str(capture_i) + ".png")
                capture_i += 1
            if not finished and not render.in_progress():
                finished = True
                print("Render time:", (current_time-start_time)/1000, " seconds" )

        self.__render_image = render.copy()
        writeFilePPM(self.__render_image, "rt_1")
        pygame.image.save(self.__render_image, "rt_1.png")

    #----------------------------------------------------------------------------------------------
    # draw scene
    def draw(self, render = None, capture = False):

        # draw background
        frame_img = None
        progress = 0
        if render and capture:
            frame_img = render.copy()
            self.__surface.blit(frame_img, (0,0))
        elif render:
            progress = render.blit(self.__surface, (0, 0))
        else:
            self.__surface.fill(BLACK)

        # draw red line which indicates the progress of the rendering
        if render and render.in_progress(): 
            progress_len = int(self.__surface.get_width() * progress)
            pygame.draw.line(self.__surface, BLACK, (0, 0), (progress_len, 0), 1) 
            pygame.draw.line(self.__surface, RED, (0, 2), (progress_len, 2), 3) 
            pygame.draw.line(self.__surface, BLACK, (0, 4), (progress_len, 4), 1) 

        # update display
        pygame.display.flip()

        return frame_img

    #----------------------------------------------------------------------------------------------
    # init pygame diesplay surface
    def __init_surface(self, size):
        self.__surface = pygame.display.set_mode(size, pygame.RESIZABLE)

    #----------------------------------------------------------------------------------------------
    # handle events in a loop
    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__run = False
            elif event.type == pygame.VIDEORESIZE:
                self.__init_surface((event.w, event.h))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__run = False

###################################################################################################
# main
def random_scene():
    list = HitableList()
    list.append(Sphere(vec3(0, -1000, 0), 1000, Lambertian(vec3(0.5, 0.5, 0.5))))

    for a in range(-11, 11):
        for b in range(-11, 11):
            choose_mat = rand01()
            center = vec3(a+0.9*rand01(), 0.2, b+0.9*rand01())
            if (center-vec3(4, 0.2, 0)).magnitude() > 0.9:
                if choose_mat < 0.8:
                    # diffuse
                    mat = Lambertian(vec3(rand01()*rand01(), rand01()*rand01(), rand01()*rand01()))
                    list.append(Sphere(center, 0.2, mat))  
                elif choose_mat < 0.95:
                    # metal
                    mat = Metal(vec3(0.5*(1+rand01()), 0.5*(1+rand01()), 0.5*(1+rand01())), 0.5*rand01())
                    list.append(Sphere(center, 0.2, mat))
                else:
                    # glass
                    mat = Dielectric(1.5)
                    list.append(Sphere(center, 0.2, mat))

    list.append(Sphere(vec3(0, 1, 0), 1, Dielectric(1.5)))
    list.append(Sphere(vec3(-4, 1, 0), 1, Lambertian(vec3(0.4, 0.2, 0.1))))
    list.append(Sphere(vec3(4, 1, 0), 1, Metal(vec3(0.7, 0.6, 0.5), 0.0)))
    return list


app = Application((600, 400), caption = "光线追踪")

image = pygame.Surface(app.size)

create_random_scene = True
if create_random_scene:

    lookfrom = vec3(12, 2, 3)
    lookat = vec3(0, 0, 0)
    dist_to_focus = 10
    #dist_to_focus = (lookat-lookfrom).magnitude()
    aperture = 0.1
    cam = Camera(lookfrom, lookat, vec3(0, 1, 0), 20, app.size[0]/app.size[1], aperture, dist_to_focus)
    world = random_scene()

else:

    lookfrom = vec3(3, 3, 2)
    lookat = vec3(0, 0, -1)
    dist_to_focus = (lookat-lookfrom).magnitude()
    aperture = 0.5
    cam = Camera(lookfrom, lookat, vec3(0, 1, 0), 20, app.size[0]/app.size[1], aperture, dist_to_focus)

    world = HitableList()
    world += [
        Sphere(vec3(0, 0, -1), 0.5,      Lambertian(vec3(0.1, 0.2, 0.5))),
        Sphere(vec3(0, -100.5, -1), 100, Lambertian(vec3(0.8, 0.8, 0))),
        Sphere(vec3(1, 0, -1), 0.5,      Metal(vec3(0.8, 0.6, 0.2), 0.2)),
        Sphere(vec3(-1, 0, -1), 0.5,     Dielectric(1.5)),
        Sphere(vec3(-1, 0, -1), -0.45,   Dielectric(1.5))
    ] 

render = Rendering(world, cam, app.size)
app.run(render, 100, 1, 0)