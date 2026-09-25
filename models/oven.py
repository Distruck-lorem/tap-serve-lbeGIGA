import pygame
from config import (
    OVEN_SIZE, NUM_OVEN_FRAMES, OVEN_FRAME_WIDTH, OVEN_FRAME_HEIGHT, OVEN_FRAME_DURATION, STAGE_BAKING
)

class Oven:
    def __init__(self, idle_path, proses_path, topright_pos):
        oven_idle_raw = pygame.image.load(idle_path).convert_alpha()
        self.idle_img = pygame.transform.scale(oven_idle_raw, OVEN_SIZE)
        
        oven_proses_raw = pygame.image.load(proses_path).convert_alpha()
        self.frames = []
        for i in range(NUM_OVEN_FRAMES):
            frame_surf = oven_proses_raw.subsurface(
                pygame.Rect(i * OVEN_FRAME_WIDTH, 0, OVEN_FRAME_WIDTH, OVEN_FRAME_HEIGHT)
            )
            scaled_frame = pygame.transform.scale(frame_surf, OVEN_SIZE)
            self.frames.append(scaled_frame)
            
        self.rect = self.idle_img.get_rect()
        self.rect.topright = topright_pos
        
        self.is_animating = False
        self.current_frame = 0
        self.timer = 0.0

    def start_baking(self):
        self.is_animating = True
        self.current_frame = 0
        self.timer = 0.0

    def stop_baking(self):
        self.is_animating = False
        self.current_frame = 0
        self.timer = 0.0

    def update(self, dt, cookie_stage):
        """Returns updated cookie_stage if baking completes via frame timer"""
        if self.is_animating:
            self.timer += dt
            if self.timer >= OVEN_FRAME_DURATION:
                self.timer -= OVEN_FRAME_DURATION
                self.current_frame += 1
                if self.current_frame >= len(self.frames):
                    self.stop_baking()
                    if cookie_stage == STAGE_BAKING:
                        print("Cookie selesai dipanggang!")
                        return "COOKIE_DONE"
        return cookie_stage

    def draw(self, screen):
        if self.is_animating:
            current_img = self.frames[self.current_frame]
        else:
            current_img = self.idle_img
        screen.blit(current_img, self.rect)

    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)
