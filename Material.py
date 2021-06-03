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
        target = rec.p + rec.normal + random_in_unit_sphere()
        return Ray(rec.p, target-rec.p), self.__albedo # 返回值：反射射线,颜色（三个轴的）


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


class PBR(Material):
    def __init__(self,albedo,metallic,roughness,ao):
        super().__init__()
        self.albedo=albedo
        self.metallic=metallic
        self.roughness=roughness
        self.ao=ao

    @staticmethod
    def DistributionGGX(N, H, roughness):
        a = roughness*roughness
        a2 = a*a
        NdotH = max(N.dot(H), 0.0)
        NdotH2 = NdotH*NdotH
        nom = a2
        denom = (NdotH2*(a2-1.0)+1.0)
        denom = math.pi*denom*denom

        return nom/denom

    @staticmethod
    def GeometrySchlickGGX(NdotV, roughness):
        r = roughness+1.0
        k = (r*r)/8.0

        nom = NdotV
        denom = NdotV*(1.0-k)+k

        return nom/denom

    @staticmethod
    def GeometrySmith(N, V, L, roughness):
        NdotV = max(N.dot(V),0.0)
        NdotL = max(N.dot(L),0.0)
        ggx2 = PBR.GeometrySchlickGGX(NdotV,roughness)
        ggx1 = PBR.GeometrySchlickGGX(NdotL,roughness)

        return ggx1*ggx2

    @staticmethod
    def fresnelSchlick(cosTheta, F0):
        return F0 + (vec3(1,1,1)-F0) * ((1.0-cosTheta)**5.0)

    @staticmethod
    def mix(a,b,c):
        return vec3([a[0]*b[0]*c,a[1]*b[1]*c,a[2]*b[2]*c])

    def scatter(self, r_in, rec):
        N = rec.normal.normalize() # 需要归一化？
        V = r_in.direction # 归一化完的

        F0 = vec3(0.04,0.04,0.04)
        F0 = PBR.mix(F0, self.albedo, self.metallic)  # 本身颜色和金属度混合，形成反射颜色

        Lo = vec3(0,0,0)

        # 计算光照
        lightPositions=vec3(rec.p[0],10,rec.p[2]) # 天光
        L = (lightPositions - rec.p).normalize()
        H = (V + L).normalize()
        distance2 = (lightPositions - rec.p).magnitude_squared()
        attenuation = 1.0 / distance2
        # radiance = lightColors[i]*attenuation # 如果是正向计算，需要让光线的距离反比和光线颜色混合，形成辐射度
        radiance = attenuation  # 如果是反向计算，距离反比就是辐射度（相当于白光）。混合在递归回溯的时候做

        # cook-torrance brdf
        NDF = PBR.DistributionGGX(N, H, self.roughness)
        G = PBR.GeometrySmith(N, V, L, self.roughness)
        F = PBR.fresnelSchlick(max(H.dot(V), 0.0), F0)

        kS = F
        kD = vec3(1,1,1) - kS
        kD *= 1.0 - self.metallic

        nominator = NDF * G * F
        denominator = 4.0 * max(N.dot(V), 0.0) * max(N.dot(L), 0.0) + 0.001
        specular = nominator / denominator

        # add to outgoing radiance Lo
        NdotL = max(N.dot(L), 0.0)
        Lo += (PBR.mix(kD,self.albedo,1) /math.pi + specular) * radiance * NdotL

        ambient = PBR.mix(vec3(0.03,0.03,0.03),self.albedo,1) * self.ao
        color = ambient + Lo

        # color = color / (color + vec3(1,1,1))
        # color2=vec3(1/(color[0]+1), 1/(color[1]+1), 1/(color[2]+1))
        # color=PBR.mix(color,color2,1)
        # color=PBR.mix(color,vec3(1/2.2,1/2.2,1/2.2),1)
        print(color)

        reflected = r_in.direction.reflect(rec.normal)
        return Ray(rec.p, reflected), color