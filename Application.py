import pygame

BLACK = (0, 0, 0)
RED = (255, 0, 0)

class Application:
    def __init__(self, size = (800, 600), caption = "PyGame window"):
        # state attributes
        self.__run = True

        # PyGame initialization
        pygame.init()
        self.__init_surface(size)
        pygame.display.set_caption(caption)

        self.__clock = pygame.time.Clock()

    def __del__(self):
        pygame.quit()

    # ----------------------------------------------------------------------------------------------
    # set the size of the application window
    @property
    def size(self):
        return self.__surface.get_size()

    # ----------------------------------------------------------------------------------------------
    # get window surface
    @property
    def surface(self):
        return self.__surface

    # ----------------------------------------------------------------------------------------------
    # get and set application
    @property
    def image(self):
        return self.__image
    @image.setter
    def image(self, image):
        self.__image = image

    # ----------------------------------------------------------------------------------------------
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
                print("Render time:", (current_time - start_time ) /1000, " seconds" )

        self.__render_image = render.copy()
        pygame.image.save(self.__render_image, "rt_1.png")

    # ----------------------------------------------------------------------------------------------
    # draw scene
    def draw(self, render = None, capture = False):

        # draw background
        frame_img = None
        progress = 0
        if render and capture:
            frame_img = render.copy()
            self.__surface.blit(frame_img, (0 ,0))
        elif render:
            progress = render.blit(self.__surface, (0, 0))
        else:
            self.__surface.fill(BLACK)

        # 红线指示渲染进度
        if render and render.in_progress():
            progress_len = int(self.__surface.get_width() * progress)
            pygame.draw.line(self.__surface, BLACK, (0, 0), (progress_len, 0), 1)
            pygame.draw.line(self.__surface, RED, (0, 2), (progress_len, 2), 3)
            pygame.draw.line(self.__surface, BLACK, (0, 4), (progress_len, 4), 1)

            # update display
        pygame.display.flip()

        return frame_img

    # ----------------------------------------------------------------------------------------------
    # init pygame diesplay surface
    def __init_surface(self, size):
        self.__surface = pygame.display.set_mode(size, pygame.RESIZABLE)

    # ----------------------------------------------------------------------------------------------
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
