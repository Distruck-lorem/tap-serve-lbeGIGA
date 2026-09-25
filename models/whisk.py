import pygame
from config import (
    SCREEN_WIDTH, WHITE, BLACK, GOLD, DARK_GRAY,
    WHISK_REQUIRED_CLICKS, WHISK_TIME_LIMIT
)

class WhiskGame:
    def __init__(self, font_title, font_sub, half_bottom_top):
        self.font_title = font_title
        self.font_sub = font_sub
        
        self.bar_width = 220
        self.bar_x = (SCREEN_WIDTH - self.bar_width) // 2
        self.bar_y = half_bottom_top + 230
        self.bar_height = 16
        
        self.is_active = False
        self.click_count = 0
        self.timer = 0.0
        self.feedback_msg = ""
        self.feedback_score = 0
        self.feedback_timer = 0.0

    def start(self):
        self.is_active = True
        self.click_count = 0
        self.timer = 0.0
        self.feedback_msg = ""
        self.feedback_score = 0

    def update(self, dt):
        """Updates timer. Returns ('MISS', 0) if time expires."""
        if self.is_active:
            self.timer += dt
            if self.timer >= WHISK_TIME_LIMIT:
                self.is_active = False
                self.feedback_msg = "MISS! (+0)"
                self.feedback_score = 0
                self.feedback_timer = 2.0
                print("Whisk MISS! Waktu habis.")
                return "MISS", 0

        if self.feedback_timer > 0:
            self.feedback_timer -= dt

        return None, 0

    def handle_click(self):
        """Increments click count and evaluates result upon reaching required clicks."""
        if not self.is_active:
            return None, 0

        self.click_count += 1
        if self.click_count >= WHISK_REQUIRED_CLICKS:
            self.is_active = False
            elapsed = self.timer
            
            if elapsed <= 4.0:
                result = "PERFECT"
                score = 20
            elif elapsed <= 7.0:
                result = "GOOD"
                score = 15
            elif elapsed <= 9.0:
                result = "BAD"
                score = 8
            else:
                result = "MISS"
                score = 0

            self.feedback_msg = f"{result}! (+{score})"
            self.feedback_score = score
            self.feedback_timer = 2.0
            print(f"Whisk {result}! Waktu: {elapsed:.2f}s, Score: +{score}")
            return result, score

        return None, 0

    def draw(self, screen):
        if self.is_active:
            # 1. WHISK! Header
            whisk_txt = self.font_title.render("WHISK!", True, (255, 140, 0))
            screen.blit(whisk_txt, whisk_txt.get_rect(center=(SCREEN_WIDTH // 2, self.bar_y - 35)))

            # 2. Click Counter Text (7 / 15)
            count_txt = self.font_sub.render(f"{self.click_count} / {WHISK_REQUIRED_CLICKS}", True, BLACK)
            screen.blit(count_txt, count_txt.get_rect(center=(SCREEN_WIDTH // 2, self.bar_y - 12)))

            # 3. Click Progress Bar
            pygame.draw.rect(screen, (50, 50, 50), (self.bar_x, self.bar_y + 4, self.bar_width, self.bar_height), border_radius=6)
            progress_w = int(self.bar_width * (self.click_count / WHISK_REQUIRED_CLICKS))
            if progress_w > 0:
                pygame.draw.rect(screen, (255, 140, 0), (self.bar_x, self.bar_y + 4, progress_w, self.bar_height), border_radius=6)
            pygame.draw.rect(screen, BLACK, (self.bar_x, self.bar_y + 4, self.bar_width, self.bar_height), width=2, border_radius=6)

            # 4. TIME Label & Progress Bar
            time_remaining = max(0.0, WHISK_TIME_LIMIT - self.timer)
            time_ratio = time_remaining / WHISK_TIME_LIMIT
            timer_y = self.bar_y + 30
            
            time_lbl = self.font_sub.render("TIME", True, DARK_GRAY)
            screen.blit(time_lbl, time_lbl.get_rect(center=(SCREEN_WIDTH // 2, timer_y)))
            
            pygame.draw.rect(screen, (60, 60, 60), (self.bar_x, timer_y + 14, self.bar_width, 10), border_radius=4)
            time_w = int(self.bar_width * time_ratio)
            if time_w > 0:
                bar_color = (50, 205, 50) if time_ratio > 0.4 else (255, 60, 60)
                pygame.draw.rect(screen, bar_color, (self.bar_x, timer_y + 14, time_w, 10), border_radius=4)
            pygame.draw.rect(screen, BLACK, (self.bar_x, timer_y + 14, self.bar_width, 10), width=1, border_radius=4)

        elif self.feedback_timer > 0 and self.feedback_msg:
            # Render Feedback result text banner
            color = GOLD if "PERFECT" in self.feedback_msg or "GOOD" in self.feedback_msg else (255, 80, 80)
            fb_surf = self.font_title.render(self.feedback_msg, True, color)
            screen.blit(fb_surf, fb_surf.get_rect(center=(SCREEN_WIDTH // 2, self.bar_y + 10)))
