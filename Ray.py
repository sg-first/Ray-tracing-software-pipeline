import pygame
import random
import math

vec3 = pygame.Vector3
rand01 = random.random

class Ray:
    def __init__(self, a, b):
        self.A = a
        self.B = b
    @property
    def origin(self):
        return self.A
    @origin.setter
    def origin(self, o):
        self.A = o
    @property
    def direction(self):
        return self.B
    @direction.setter
    def direction(self, d):
        self.B = d
    def point_at_parameter(self, t):
        return self.A + self.B * t

def multiply_components(a, b):
    return vec3(a[0]*b[0],a[1]*b[1],a[2]*b[2])

def random_in_unit_sphere():
    while True:
        # random vector x, y, z in [-1, 1]
        p = 2*vec3(rand01(), rand01(), rand01()) - vec3(1, 1, 1)
        if p.magnitude_squared() < 1: # magnitude of vector has to be less than 1
            break
    return p

def random_in_unit_disk():
    while True:
        # random vector x, y, z in [-1, 1]
        p = 2*vec3(rand01(), rand01(), 0) - vec3(1, 1, 0)
        if p.magnitude_squared() < 1: # magnitude of vector has to be less than 1
            break
    return p

def reflect(v, n):
    return v - 2*v.dot(n)*n

def refract(v, n, ni_over_nt):
    # Snell's law: n*sin(theta) = n'*sin(theta')
    uv = v.normalize()
    dt = uv.dot(n)
    discriminant = 1 - ni_over_nt*ni_over_nt*(1-dt*dt)
    if discriminant > 0:
        return ni_over_nt*(uv-n*dt) - n*math.sqrt(discriminant)
    return None

def schlick(cosine, ref_idx):
    r0 = (1-ref_idx) / (1+ref_idx)
    r0 = r0*r0
    return r0 + (1-r0)*math.pow(1-cosine, 5)