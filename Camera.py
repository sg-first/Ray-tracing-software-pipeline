import math
from Ray import *

class Camera:
    def __init__(self, lookfrom, lookat, vup, vfov, aspect, aperture, focus_dist):
        self.__lens_radius = aperture/2
        self.__focus_dist = focus_dist
        self.__origin = lookfrom
        self.__direction = lookat -lookfrom
        self.__vup = vup
        self.__vfov = vfov * math.pi / 180
        self.__aspect = aspect
        self.update()
    @property
    def aspect(self):
        return self.__aspect
    @aspect.setter
    def aspect(self, aspect):
        self.__aspect = aspect
        self.update()
    @property
    def vfov_degree(self):
        return self.__vfov * 180/math.PI
    @vfov_degree.setter
    def vfov_degree(self, vfov):
        self.__vfov = vfov * math.pi/180
        self.update()
    def update(self):
        half_height = math.tan(self.__vfov/2)
        half_width = self.__aspect * half_height
        self.__w = -self.__direction.normalize()
        self.__u = self.__vup.cross(self.__w).normalize()
        self.__v = self.__w.cross(self.__u)
        self.__lower_left_corner = self.__origin - half_width*self.__focus_dist*self.__u - half_height*self.__focus_dist*self.__v - self.__focus_dist*self.__w
        self.__horizontal = 2*half_width*self.__focus_dist*self.__u
        self.__vertical = 2*half_height*self.__focus_dist*self.__v
    def get_ray(self, s, t):
        rd = self.__lens_radius*random_in_unit_disk()
        offset = self.__u*rd.x + self.__v*rd.y # dot(rd.xy, (u, v))
        return Ray(
            self.__origin + offset,
            self.__lower_left_corner + s*self.__horizontal + t*self.__vertical - self.__origin - offset)
