import os
import sys

from Hitable import *
from Material import *
from Camera import *
from Rendering import *
from Application import *

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

    list.append(Sphere(vec3(0, 1, 0), 1, Dielectric(1.5))) # 全反射
    # list.append(Sphere(vec3(4, 1, 0), 1, Lambertian(vec3(0.4, 0.2, 0.1)))) # 散射
    list.append(Sphere(vec3(-4, 1, 0), 1, Metal(vec3(0.7, 0.6, 0.5), 0.0)))
    return list


app = Application((600, 400), caption = "光线追踪")

image = pygame.Surface(app.size)

create_random_scene = True
if create_random_scene:

    lookfrom = vec3(7, 1.5, 5)
    lookat = vec3(0, 1.5, 0)
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