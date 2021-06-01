from Ray import *

class Material:
    def __init__(self):
        pass

class Lambertian(Material):
    def __init__(self, albedo):
        super().__init__()
        self.__albedo = albedo
    def scatter(self, r_in, rec):
        # target is a point outside the sphere but "near" to `rec.p`:
        # target = p + nv + random_direction
        target = rec.p - rec.normal + random_in_unit_sphere()
        return Ray(rec.p, target-rec.p), self.__albedo

class Metal(Material):
    def __init__(self, albedo, fuzz=0):
        super().__init__()
        self.__albedo = albedo
        self.__fuzz = min(fuzz, 1)
    def scatter(self, r_in, rec):
        # reflection
        # reflected = reflect(r_in.direction.normalize(), rec.normal)
        reflected = r_in.direction.normalize().reflect(rec.normal)
        # fuzzy
        scattered = Ray(rec.p, reflected + self.__fuzz*random_in_unit_sphere())
        attenuation = self.__albedo
        return (scattered, attenuation) if scattered.direction.dot(rec.normal) > 0 else None

class Dielectric(Material):
    def __init__(self, ri):
        super().__init__()
        self.__ref_idx = ri
    def scatter(self, r_in, rec):
        reflected = r_in.direction.reflect(rec.normal)
        if r_in.direction.dot(rec.normal) > 0:
            outward_normal = -rec.normal
            ni_over_nt = self.__ref_idx
            cosine = self.__ref_idx * r_in.direction.dot(rec.normal) / r_in.direction.magnitude()
        else:
            outward_normal = rec.normal
            ni_over_nt = 1/self.__ref_idx
            cosine = -r_in.direction.dot(rec.normal) / r_in.direction.magnitude()
        refracted = refract(r_in.direction, outward_normal, ni_over_nt)
        reflect_probe = schlick(cosine, self.__ref_idx) if refracted else 1
        if rand01() < reflect_probe:
            scattered = Ray(rec.p, reflected)
        else:
            scattered = Ray(rec.p, refracted)
        return scattered, vec3(1, 1, 1)