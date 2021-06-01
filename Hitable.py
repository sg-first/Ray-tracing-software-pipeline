import math

class Hitable:
    def __init__(self):
        pass

# hit information
class HitRecord:
    def __init__(self, t, p, normal, material):
        self.t = t
        self.p = p
        self.normal = normal
        self.material = material

class HitableList(Hitable):
    def __init__(self):
        super().__init__()
        self.__list = []
    def __iadd__(self, hitobj):
        if type(hitobj)==list:
            self.__list.extend(hitobj)
        else:
            self.__list.append(hitobj)
        return self
    def append(self, hitobj):
        if type(hitobj)==list:
            self.__list.extend(hitobj)
        else:
            self.__list.append(hitobj)
    def hit(self, r, tmin, tmax):
        hit_anything, closest_so_far = None, tmax
        for hitobj in self.__list: # 可以换八叉树
            rec = hitobj.hit(r, tmin, closest_so_far) # 比现有的近才会返回非None
            if rec:
                hit_anything, closest_so_far = rec, rec.t
        return hit_anything


class Sphere(Hitable):
    def __init__(self, center, radius, material):
        super().__init__()
        self.__center = center
        self.__radius = radius
        self.__material = material

    # ----------------------------------------------------------------------------------------------
    # Ray - Sphere intersection
    #
    # Sphere:         dot(p-C, p-C) = R*R            `C`: center, `p`: point on the sphere, `R`, radius
    # Ray:            p(t) = A + B * t               `A`: origin, `B`: direction
    # Intersection:   dot(A +B*t-C, A+B*t-C) = R*R
    #                 t*t*dot(B,B) + 2*t*dot(B,A-C) + dot(A-C,A-C) - R*R = 0
    def hit(self, r, tmin, tmax):  # 要求深度在tmin, tmax范围内
        oc = r.origin - self.__center
        a = r.direction.dot(r.direction)
        b = 2 * oc.dot(r.direction)
        c = oc.dot(oc) - self.__radius * self.__radius
        discriminant = b * b - 4 * a * c
        if discriminant > 0:
            temp = (-b - math.sqrt(discriminant)) / (2 * a)  # 交点在r这条线的什么位置
            if tmin < temp < tmax:
                p = r.point_at_parameter(temp)  # 交点位置（三维）
                # 第一个参数深度，第二个参数交点位置，第三个参数法线
                return HitRecord(temp, p, (p - self.__center) / self.__radius, self.__material)
            temp = (-b + math.sqrt(discriminant)) / (2 * a)
            if tmin < temp < tmax:
                p = r.point_at_parameter(temp)
                return HitRecord(temp, p, (p - self.__center) / self.__radius, self.__material)

        return None