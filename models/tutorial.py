import pygame
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GOLD, DARK_GRAY,
    STAGE_IDLE, STAGE_BOWL_CENTER, STAGE_HAS_FLOUR, STAGE_HAS_EGG,
    STAGE_HAS_BUTTER, STAGE_HAS_SUGAR, STAGE_WHISKING, STAGE_MIXED, STAGE_DOUGH_READY,
    STAGE_CUT_DOUGH, STAGE_HAS_CHOCOCHIP, STAGE_BAKING, STAGE_COOKIE_DONE, STAGE_SERVED
)

class TutorialGuide:
    def __init__(self, font_sub, font_small):
        self.font_sub = font_sub
        self.font_small = font_small
        self.is_enabled = True
        self.anim_timer = 0.0

    def toggle(self):
        self.is_enabled = not self.is_enabled

    def update(self, dt):
        self.anim_timer += dt

    def get_step_info(self, kitchen, oven, customer):
        stage = kitchen.cookie_stage
        
        if stage == STAGE_IDLE:
            bowl_x = kitchen.bowl_pos[0] + 40
            bowl_y = kitchen.bowl_pos[1] - 10
            return "1/10", "Klik Mangkuk (Bowl) untuk ke meja!", (bowl_x, bowl_y)
        
        elif stage == STAGE_BOWL_CENTER:
            return "2/10", "Klik Tepung (Flour)!", (kitchen.flour.centerx, kitchen.flour.top - 10)
        
        elif stage == STAGE_HAS_FLOUR:
            return "3/10", "Klik Telur (Egg)!", (kitchen.egg.centerx, kitchen.egg.top - 10)
        
        elif stage == STAGE_HAS_EGG:
            return "4/10", "Klik Mentega (Butter)!", (kitchen.butter.centerx, kitchen.butter.top - 10)
        
        elif stage == STAGE_HAS_BUTTER:
            return "5/10", "Klik Gula (Sugar)!", (kitchen.sugar.centerx, kitchen.sugar.top - 10)
        
        elif stage == STAGE_HAS_SUGAR:
            return "6/10", "Klik Pengocok (Whisk)!", (kitchen.whisker.centerx, kitchen.whisker.top - 10)
        
        elif stage == STAGE_WHISKING:
            return "6b/10", "Klik cepat layar sampai pengocok penuh!", (SCREEN_WIDTH // 2, kitchen.half_bottom_top + 215)
        
        elif stage == STAGE_MIXED:
            bowl_x = kitchen.bowl_pos[0] + 40
            bowl_y = kitchen.bowl_pos[1] - 10
            return "6c/10", "Klik Mangkuk lagi untuk ambil adonan!", (bowl_x, bowl_y)
        
        elif stage == STAGE_DOUGH_READY:
            return "7/10", "Klik Cetakan (Cutter) potong adonan!", (kitchen.cookieCutter.centerx, kitchen.cookieCutter.top - 10)
        
        elif stage == STAGE_CUT_DOUGH:
            return "7b/10", "Klik Chocochip untuk beri topping!", (kitchen.chocochip.centerx, kitchen.chocochip.top - 10)
        
        elif stage == STAGE_HAS_CHOCOCHIP:
            return "8/10", "Klik Oven untuk memanggang adonan!", (oven.rect.centerx, oven.rect.top - 10)
        
        elif stage == STAGE_BAKING:
            return "9/10", "Klik/Tap saat penunjuk di zona HIJAU!", (SCREEN_WIDTH // 2, kitchen.half_bottom_top + 230)
        
        elif stage == STAGE_COOKIE_DONE:
            cookie_x = kitchen.CENTER_MIX_POS[0] + 40
            cookie_y = kitchen.CENTER_MIX_POS[1] + 30
            return "10/10", "Klik Kue / Pelanggan untuk menyajikan!", (cookie_x, cookie_y)
        
        elif stage == STAGE_SERVED:
            return "SERVED", "Kue disajikan! Menunggu pelanggan baru...", None

        return "", "", None

    def draw(self, screen, kitchen, oven, customer):
        if not self.is_enabled:
            return

        step_num, text, target_pos = self.get_step_info(kitchen, oven, customer)
        if not text:
            return

        # 1. Render Top Guide Banner Card
        banner_rect = pygame.Rect(12, 48, SCREEN_WIDTH - 24, 34)
        
        # Dark Card with Gold Accent Border
        pygame.draw.rect(screen, (25, 28, 38), banner_rect, border_radius=10)
        pygame.draw.rect(screen, GOLD, banner_rect, width=2, border_radius=10)

        # Step Pill Badge
        step_bg = pygame.Rect(banner_rect.x + 5, banner_rect.y + 5, 52, 24)
        pygame.draw.rect(screen, GOLD, step_bg, border_radius=6)
        step_surf = self.font_small.render(step_num if step_num else "GUIDE", True, BLACK)
        screen.blit(step_surf, step_surf.get_rect(center=step_bg.center))

        # Instruction Text
        msg_surf = self.font_small.render(text, True, WHITE)
        msg_rect = msg_surf.get_rect(midleft=(step_bg.right + 8, banner_rect.centery))
        screen.blit(msg_surf, msg_rect)

        # 2. Render Bouncing Pointer Arrow & Pulsing Target Ring
        if target_pos:
            tx, ty = target_pos
            bounce_y = math.sin(self.anim_timer * 7.0) * 5.0
            arrow_y = ty - 10 + bounce_y

            # Pulsing target ring
            pulse_r = 16 + int(math.sin(self.anim_timer * 8.0) * 4.0)
            ring_surf = pygame.Surface((pulse_r * 2 + 4, pulse_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (255, 215, 0, 160), (pulse_r + 2, pulse_r + 2), pulse_r, width=3)
            screen.blit(ring_surf, ring_surf.get_rect(center=(tx, ty + 18)))

            # Animated Arrow ▼
            arrow_surf = self.font_sub.render("▼", True, (255, 215, 0))
            shadow_surf = self.font_sub.render("▼", True, BLACK)
            screen.blit(shadow_surf, shadow_surf.get_rect(center=(tx + 1, arrow_y + 1)))
            screen.blit(arrow_surf, arrow_surf.get_rect(center=(tx, arrow_y)))
