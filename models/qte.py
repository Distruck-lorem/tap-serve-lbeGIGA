import pygame
from config import (
    SCREEN_WIDTH, WHITE, BLACK, GOLD, DARK_GRAY, QTE_BAR_WIDTH, QTE_BAR_HEIGHT,
    QTE_BAR_X, QTE_BAR_Y_OFFSET, QTE_DURATION,
    QTE_ZONE_BAD_START, QTE_ZONE_BAD_END,
    QTE_ZONE_GOOD_START, QTE_ZONE_GOOD_END,
    QTE_ZONE_PERFECT_START, QTE_ZONE_PERFECT_END
)

class QTEBar:
    def __init__(self, font_sub, half_bottom_top):
        self.font_sub = font_sub
        self.bar_y = half_bottom_top + QTE_BAR_Y_OFFSET
        self.is_active = False
        self.time = 0.0
        self.pointer_pos = 0.0
        self.feedback_msg = ""
        self.feedback_timer = 0.0

    def activate(self):
        self.is_active = True
        self.time = 0.0
        self.pointer_pos = 0.0
        self.feedback_msg = ""

    def update(self, dt):
        if self.is_active:
            self.time += dt
            self.pointer_pos = self.time / QTE_DURATION
            if self.pointer_pos >= 1.0:
                self.is_active = False
                self.feedback_msg = "MISS! (+0)"
                self.feedback_timer = 2.0
                print("QTE MISS! Indikator mencapai ujung tanpa tap.")
                return "MISS", 0

        if self.feedback_timer > 0:
            self.feedback_timer -= dt

        return None, 0

    def handle_tap(self):
        """Returns tuple (result_type, score_earned) based on indicator position."""
        if not self.is_active:
            return None, 0
            
        self.is_active = False
        pos = self.pointer_pos

        if QTE_ZONE_PERFECT_START <= pos <= QTE_ZONE_PERFECT_END:
            result = "PERFECT"
            score = 100
        elif QTE_ZONE_GOOD_START <= pos <= QTE_ZONE_GOOD_END:
            result = "GOOD"
            score = 80
        elif QTE_ZONE_BAD_START <= pos <= QTE_ZONE_BAD_END:
            result = "BAD"
            score = 50
        else:
            result = "MISS"
            score = 0

        self.feedback_msg = f"{result}! (+{score})"
        self.feedback_timer = 2.0
        print(f"QTE {result}! Pos: {pos:.2f}, Score: +{score}")
        return result, score

    def draw(self, screen):
        if self.is_active or self.feedback_timer > 0:
            # 1. Title Header
            if self.is_active:
                hdr_surf = self.font_sub.render("BAKING...", True, BLACK)
                screen.blit(hdr_surf, hdr_surf.get_rect(center=(SCREEN_WIDTH // 2, self.bar_y - 28)))

            # 2. Outer Dark Container
            pygame.draw.rect(screen, (40, 40, 40), (QTE_BAR_X, self.bar_y, QTE_BAR_WIDTH, QTE_BAR_HEIGHT), border_radius=6)
            
            # 3. BAD Zone (Amber/Yellow)
            bad_x = QTE_BAR_X + int(QTE_BAR_WIDTH * QTE_ZONE_BAD_START)
            bad_w = int(QTE_BAR_WIDTH * (QTE_ZONE_BAD_END - QTE_ZONE_BAD_START))
            pygame.draw.rect(screen, (240, 180, 50), (bad_x, self.bar_y + 2, bad_w, QTE_BAR_HEIGHT - 4), border_radius=4)
            
            # 4. GOOD Zone (Light Green)
            good_x = QTE_BAR_X + int(QTE_BAR_WIDTH * QTE_ZONE_GOOD_START)
            good_w = int(QTE_BAR_WIDTH * (QTE_ZONE_GOOD_END - QTE_ZONE_GOOD_START))
            pygame.draw.rect(screen, (80, 205, 90), (good_x, self.bar_y + 2, good_w, QTE_BAR_HEIGHT - 4), border_radius=4)

            # 5. PERFECT Zone (Gold - Smallest)
            perf_x = QTE_BAR_X + int(QTE_BAR_WIDTH * QTE_ZONE_PERFECT_START)
            perf_w = int(QTE_BAR_WIDTH * (QTE_ZONE_PERFECT_END - QTE_ZONE_PERFECT_START))
            pygame.draw.rect(screen, (255, 215, 0), (perf_x, self.bar_y + 2, perf_w, QTE_BAR_HEIGHT - 4), border_radius=4)

            # Outer White Border
            pygame.draw.rect(screen, WHITE, (QTE_BAR_X, self.bar_y, QTE_BAR_WIDTH, QTE_BAR_HEIGHT), width=2, border_radius=6)
            
            # 6. Moving Pointer Line & Triangle ▲ Indicator
            if self.is_active:
                pointer_x = QTE_BAR_X + int(self.pointer_pos * QTE_BAR_WIDTH)
                pygame.draw.line(screen, (255, 50, 50), (pointer_x, self.bar_y - 4), (pointer_x, self.bar_y + QTE_BAR_HEIGHT + 4), width=3)
                
                # Bottom Triangle Arrow ▲
                tri_pts = [
                    (pointer_x, self.bar_y + QTE_BAR_HEIGHT + 2),
                    (pointer_x - 6, self.bar_y + QTE_BAR_HEIGHT + 10),
                    (pointer_x + 6, self.bar_y + QTE_BAR_HEIGHT + 10)
                ]
                pygame.draw.polygon(screen, (255, 50, 50), tri_pts)

            # 7. Feedback Message Banner
            if self.feedback_timer > 0 and self.feedback_msg:
                if "PERFECT" in self.feedback_msg:
                    color = GOLD
                elif "GOOD" in self.feedback_msg:
                    color = (100, 220, 100)
                elif "BAD" in self.feedback_msg:
                    color = (240, 180, 50)
                else:
                    color = (255, 80, 80)
                txt_surf = self.font_sub.render(self.feedback_msg, True, color)
                screen.blit(txt_surf, txt_surf.get_rect(center=(SCREEN_WIDTH // 2, self.bar_y - 14)))
