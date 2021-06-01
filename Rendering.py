import math
import threading
from Ray import *

def fToColor(c):
    # gc = c;
    gc = (math.sqrt(c[0]), math.sqrt(c[1]), math.sqrt(c[2])) # gamma 2
    return (int(gc[0]*255.5), int(gc[1]*255.5), int(gc[2]*255.5))

def surfaceSetXYWHi(s, x, y, w, h, c):
    if c[0] > 255 or c[1] > 255 or c[2] > 255:
        c = (max(0, min(255, c[0])), max(0, min(255, c[1])), max(0, min(255, c[2])))
    if w > 1 or h > 1:
        s.fill(c, (x, s.get_height()-y-h, w, h))
    else:
        s.set_at((x, s.get_height()-y-1), c)

def surfaceSetXYWHf(s, x, y, w, h, c):
    surfaceSetXYWHi(s, x, y, w, h, fToColor(c))

class Rendering:
    def __init__(self, world, cam, size):
        self.__world = world
        self.__cam = cam
        self.size = size
    #----------------------------------------------------------------------------------------------
    def start(self, size, no_sample, update_rate):
        self.__size = size
        self.__cam.aspect = self.__size[0]/self.__size[1]
        self.__no_samples = no_sample
        self.__update_rate = update_rate
        self.__pixel_count = 0
        self.__progress = 0
        self.__image = pygame.Surface(self.__size)
        self._stopped = False
        self.__thread = threading.Thread(target = self.run)
        self.__thread_lock = threading.Lock()
        self.__thread.start()
    #----------------------------------------------------------------------------------------------
    # check if thread is "running"
    def in_progress(self):
        return self.__thread.is_alive()
    #----------------------------------------------------------------------------------------------
    # wait for thread to end
    def wait(self, timeout = None):
        self.__thread.join(timeout)
    #----------------------------------------------------------------------------------------------
    # terminate
    def stop(self):
        self.__thread_lock.acquire()
        self._stopped = True
        self.__thread_lock.release()
        self.__thread.join()
    #----------------------------------------------------------------------------------------------
    # blit to surface
    def blit(self, surface, pos):
        self.__thread_lock.acquire()
        surface.blit(self.__image, pos)
        progress = self.__progress
        self.__thread_lock.release()
        return progress
    #----------------------------------------------------------------------------------------------
    # copy render surface
    def copy(self):
        self.__thread_lock.acquire()
        image = self.__image.copy()
        self.__thread_lock.release()
        return image
    #----------------------------------------------------------------------------------------------
    def coord_iterator(self):
        max_s = max(self.size)
        p2 = 0
        while max_s > 0:
            p2, max_s = p2 + 1, max_s >> 1
        tile_size = 1 << p2 -1
        yield (0, 0, *self.__size)
        self.__pixel_count = 1
        while tile_size > 0:
            no = (self.__size[0]-1) // tile_size + 1, (self.__size[1]-1) // tile_size + 1
            mx = (no[0]-1) // 2
            ix = [(mx - i//2) if i%2==0 else (mx+1+i//2) for i in range(no[0])]
            my = no[1] // 2
            iy = [(my + j//2) if j%2==0 else (my-1-j//2) for j in range(no[1])]
            for j in iy:
                for i in ix:
                    if i % 2 != 0 or j % 2 != 0:
                       self.__pixel_count += 1
                    if tile_size >= 128 or i % 2 != 0 or j % 2 != 0:
                        x, y = i*tile_size, j*tile_size
                        w, h = min(tile_size, self.__size[0]-x), min(tile_size, self.__size[1]-y)
                        yield (x, y, w, h)
            tile_size >>= 1
    #----------------------------------------------------------------------------------------------
    def run(self):
        no_samples = self.__no_samples
        no_samples_outer = max(1, int(no_samples * self.__update_rate + 0.5))
        no_samples_inner = (no_samples + no_samples_outer - 1) // no_samples_outer
        outer_i = 0
        count = 0
        colarr = [0] * (self.__size[0] * self.__size[1] * 3)
        while outer_i * no_samples_inner < no_samples:
            iter = self.coord_iterator()
            for x, y, w, h in iter:
                no_start = no_samples_inner * outer_i
                no_end = min(no_samples, no_start + no_samples_inner)
                col = vec3()
                for s in range(no_start, no_end):
                    u, v = (x + rand01())/self.__size[0], (y + rand01())/self.__size[1]
                    r = self.__cam.get_ray(u, v)
                    col += Rendering.rToColor(r, self.__world, 0)
                arri = y * self.__size[0] * 3 + x * 3
                colarr[arri+0] += col[0]
                colarr[arri+1] += col[1]
                colarr[arri+2] += col[2]
                col = vec3(colarr[arri+0], colarr[arri+1], colarr[arri+2])

                self.__thread_lock.acquire()
                if no_start == 0:
                    surfaceSetXYWHf(self.__image, x, y, w, h, col / no_end)
                else:
                    surfaceSetXYWHf(self.__image, x, y, 1, 1, col / no_end)
                self.__thread_lock.release()
                count += 1
                self.__progress = count / (no_samples * self.__size[0] * self.__size[1])
                if self._stopped:
                    break
            outer_i += 1
    #----------------------------------------------------------------------------------------------
    max_dist = 1e20
    @staticmethod
    def rToColor(r, world, depth):
        rec = world.hit(r, 0.001, Rendering.max_dist) # 求交。min=0.001去除阴影失真
        if rec:
            if depth >= 50: # 递归深度
                return vec3(0, 0, 0)
            sc_at = rec.material.scatter(r, rec)
            if not sc_at: # 没有反射光
                return vec3(0, 0, 0)
            return multiply_components(sc_at[1], Rendering.rToColor(sc_at[0], world, depth+1)) # 混合中递归
            # return 0.5*vec3(rec.normal.x+1, rec.normal.y+1, rec.normal.z+1)
        else: # 没找到交点
            # fix:应该支持自定义天空
            unit_direction = r.direction.normalize()
            t = 0.5 * (unit_direction.y + 1) # y轴深度？
            return (1-t)*vec3(1, 1, 1) + t*vec3(0.5, 0.7, 1) # y接近1就是天空白色，接近0就是地面灰色
