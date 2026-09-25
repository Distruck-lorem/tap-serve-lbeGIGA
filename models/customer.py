import pygame
import random
from config import (
    WHITE, BLACK, GOLD, STATE_PLAYING, STAGE_SERVED,
    CUSTOMER_TARGET_X, CUSTOMER_START_X, CUSTOMER_ANIM_DURATION, CUSTOMER_EXIT_DURATION
)

class Customer:
    def __init__(self, asset_files, font_sub, cookie_done_img, bottom_y):
        self.font_sub = font_sub
        self.cookie_done_img = cookie_done_img
        self.bottom_y = bottom_y
        
        self.pelanggan_imgs = [
            pygame.transform.scale(pygame.image.load(f).convert_alpha(), (180, 180))
            for f in asset_files
        ]
        self.pelanggan_img = random.choice(self.pelanggan_imgs)
        self.rect = self.pelanggan_img.get_rect()
        self.rect.bottomleft = (CUSTOMER_START_X, self.bottom_y)
        
        self.anim_timer = 0.0
        self.is_entering = True
        self.is_leaving = False
        self.exit_timer = 0.0

    def reset(self):
        """Randomize new customer and start entrance animation"""
        self.pelanggan_img = random.choice(self.pelanggan_imgs)
        self.anim_timer = 0.0
        self.is_entering = True
        self.is_leaving = False
        self.exit_timer = 0.0
        self.rect.bottomleft = (CUSTOMER_START_X, self.bottom_y)

    def start_leaving(self):
        """Starts 1.5s ease-out exit animation back off-screen"""
        self.is_leaving = True
        self.is_entering = False
        self.exit_timer = 0.0

    def update(self, dt, current_state):
        """Returns True when customer has finished leaving so new customer can spawn"""
        if current_state != STATE_PLAYING:
            return False

        if self.is_entering:
            self.anim_timer += dt
            t = min(1.0, self.anim_timer / CUSTOMER_ANIM_DURATION)
            # Ease-out cubic formula for entrance
            ease_t = 1.0 - (1.0 - t) ** 3
            cur_x = CUSTOMER_START_X + (CUSTOMER_TARGET_X - CUSTOMER_START_X) * ease_t
            self.rect.bottomleft = (int(cur_x), self.bottom_y)
            
            if t >= 1.0:
                self.is_entering = False
                self.rect.bottomleft = (CUSTOMER_TARGET_X, self.bottom_y)

        elif self.is_leaving:
            self.exit_timer += dt
            t = min(1.0, self.exit_timer / CUSTOMER_EXIT_DURATION)
            # Ease-out cubic formula for exit back to offscreen
            ease_t = 1.0 - (1.0 - t) ** 3
            cur_x = CUSTOMER_TARGET_X + (CUSTOMER_START_X - CUSTOMER_TARGET_X) * ease_t
            self.rect.bottomleft = (int(cur_x), self.bottom_y)

            if t >= 1.0:
                self.is_leaving = False
                return True

        return False

    def draw(self, screen, cookie_stage):
        screen.blit(self.pelanggan_img, self.rect)
        
        # Render speech bubble when customer is present (not entering)
        if not self.is_entering:
            bubble_rect = pygame.Rect(self.rect.right - 50, self.rect.bottom - 140, 54, 46)
            pygame.draw.rect(screen, WHITE, bubble_rect, border_radius=10)
            pygame.draw.rect(screen, BLACK, bubble_rect, width=2, border_radius=10)

            if cookie_stage == STAGE_SERVED or self.is_leaving:
                happy_surf = self.font_sub.render("THX!", True, GOLD)
                screen.blit(happy_surf, happy_surf.get_rect(center=bubble_rect.center))
            else:
                order_icon = pygame.transform.scale(self.cookie_done_img, (32, 32))
                screen.blit(order_icon, order_icon.get_rect(center=bubble_rect.center))

    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)
