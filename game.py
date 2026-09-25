import pygame
import random
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, DARK_GRAY, GOLD,
    STATE_HOME, STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER,
    MODE_CASUAL, MODE_UNLIMITED, GAME_DURATION
)
from models.customer import Customer
from models.oven import Oven
from models.qte import QTEBar
from models.kitchen import Kitchen

def ease_out_back(t):
    """Ease out back curve (overshoot / pop-in bounce effect)"""
    if t <= 0: return 0.0
    if t >= 1: return 1.0
    c1 = 1.70158
    c3 = c1 + 1.0
    return 1.0 + c3 * math.pow(t - 1.0, 3) + c1 * math.pow(t - 1.0, 2)

def ease_out_cubic(t):
    """Smooth cubic deceleration curve"""
    if t <= 0: return 0.0
    if t >= 1: return 1.0
    return 1.0 - math.pow(1.0 - t, 3)

def create_gradient_surface(width, height, start_color, end_color):
    surf = pygame.Surface((width, height))
    for y in range(height):
        t = y / height
        r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
    return surf

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tap & Serve")
        self.clock = pygame.time.Clock()
        
        self.current_state = STATE_HOME
        self.show_mode_modal = False
        self.selected_mode = MODE_CASUAL
        self.score = 0
        self.game_timer = GAME_DURATION
        self.elapsed_timer = 0.0
        
        # Animation Timers
        self.home_anim_timer = 0.0
        self.modal_anim_timer = 0.0
        self.fade_timer = 0.0
        
        # Fonts
        self.font_title = pygame.font.Font(None, 42)
        self.font_start = pygame.font.Font(None, 28)
        self.font_sub = pygame.font.Font(None, 22)

        # Gradient Background for HOME screen (Cream top to Warm Peach bottom)
        self.home_bg_surf = create_gradient_surface(
            SCREEN_WIDTH, SCREEN_HEIGHT,
            start_color=(255, 240, 222),
            end_color=(235, 178, 138)
        )

        # Load Logo Asset
        logo_raw = pygame.image.load("asset/Logo.png").convert_alpha()
        l_w, l_h = logo_raw.get_size()
        l_scale = 250 / l_w
        l_new_h = int(l_h * l_scale)
        self.logo_img = pygame.transform.scale(logo_raw, (250, l_new_h))
        self.logo_rect = self.logo_img.get_rect(center=(SCREEN_WIDTH // 2, 175))

        # Load Close Button Asset
        close_raw = pygame.image.load("asset/Close.png").convert_alpha()
        self.close_btn_img = pygame.transform.scale(close_raw, (100, 50))
        self.close_btn_rect = self.close_btn_img.get_rect(bottomright=(SCREEN_WIDTH - 15, SCREEN_HEIGHT - 15))

        # Background Assets
        half_bottom_raw = pygame.image.load("asset/background/Half-bottom.png").convert_alpha()
        b_width, b_height = half_bottom_raw.get_size()
        b_ratio = SCREEN_WIDTH / b_width
        b_new_height = int(b_height * b_ratio)
        self.half_bottom_img = pygame.transform.scale(half_bottom_raw, (SCREEN_WIDTH, b_new_height))
        self.half_bottom_rect = self.half_bottom_img.get_rect()
        self.half_bottom_rect.bottomleft = (0, SCREEN_HEIGHT)

        half_upper_raw = pygame.image.load("asset/background/Half-upper.png").convert_alpha()
        u_width, u_height = half_upper_raw.get_size()
        u_ratio = SCREEN_WIDTH / u_width
        u_new_height = int(u_height * u_ratio)
        self.half_upper_img = pygame.transform.scale(half_upper_raw, (SCREEN_WIDTH, u_new_height))
        self.half_upper_rect = self.half_upper_img.get_rect()
        self.half_upper_rect.topleft = (0, 0)

        # Start Button Asset
        start_btn_raw = pygame.image.load("asset/Start-Button.png").convert_alpha()
        self.start_btn_img = pygame.transform.scale(start_btn_raw, (180, 54))
        self.start_btn_rect = self.start_btn_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

        # Mode Selection Rectangles (Inside Mode Select Overlay)
        self.casual_btn_rect = pygame.Rect(0, 0, 210, 44)
        self.casual_btn_rect.center = (SCREEN_WIDTH // 2, 270)
        
        self.unlimited_btn_rect = pygame.Rect(0, 0, 210, 44)
        self.unlimited_btn_rect.center = (SCREEN_WIDTH // 2, 335)

        # Pause Button (Aligned with Timer pill ~30x26)
        self.pause_btn_rect = pygame.Rect(14, 12, 30, 26)

        # Pause Modal Buttons
        self.resume_btn_rect = pygame.Rect(0, 0, 180, 42)
        self.resume_btn_rect.center = (SCREEN_WIDTH // 2, 220)
        
        self.pause_restart_btn_rect = pygame.Rect(0, 0, 180, 42)
        self.pause_restart_btn_rect.center = (SCREEN_WIDTH // 2, 275)
        
        self.pause_home_btn_rect = pygame.Rect(0, 0, 180, 42)
        self.pause_home_btn_rect.center = (SCREEN_WIDTH // 2, 330)

        # Game Over Modal Buttons
        self.restart_btn_rect = pygame.Rect(0, 0, 180, 42)
        self.restart_btn_rect.center = (SCREEN_WIDTH // 2, 340)
        
        self.gameover_home_btn_rect = pygame.Rect(0, 0, 180, 42)
        self.gameover_home_btn_rect.center = (SCREEN_WIDTH // 2, 395)

        # Models
        pelanggan_files = [f"asset/orang/Pelanggan{i}.png" for i in range(1, 8)]
        cookie_done_img = pygame.transform.scale(pygame.image.load("asset/bahan/Cookies-Cookie-Done.png").convert_alpha(), (50, 50))
        
        self.customer = Customer(
            asset_files=pelanggan_files,
            font_sub=self.font_sub,
            cookie_done_img=cookie_done_img,
            bottom_y=self.half_upper_rect.bottom
        )
        
        self.oven = Oven(
            idle_path="asset/bahan/Oven-Idle.png",
            proses_path="asset/bahan/Oven-Proses.png",
            topright_pos=(SCREEN_WIDTH - 3, self.half_bottom_rect.top - 10)
        )
        
        self.qte_bar = QTEBar(font_sub=self.font_sub, half_bottom_top=self.half_bottom_rect.top)
        self.kitchen = Kitchen(
            half_bottom_top=self.half_bottom_rect.top,
            font_title=self.font_title,
            font_sub=self.font_sub
        )
        
        self.show_hitboxes = False

        # Start Lobby Music (Random Jazz 1-3)
        self.play_lobby_music()

    def play_lobby_music(self):
        """Plays random background Jazz 1-3 for Lobby/Home"""
        try:
            if pygame.mixer.get_init():
                track_num = random.randint(1, 3)
                track_path = f"asset/audio/music/Jazz{track_num}.mp3"
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
                print(f"Lobby BGM Playing: Jazz{track_num}.mp3")
        except Exception as e:
            print(f"Failed playing lobby music: {e}")

    def play_gameplay_music(self):
        """Plays random background Jazz 4-10 for Gameplay"""
        try:
            if pygame.mixer.get_init():
                track_num = random.randint(4, 10)
                track_path = f"asset/audio/music/Jazz{track_num}.mp3"
                pygame.mixer.music.load(track_path)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
                print(f"Gameplay BGM Playing: Jazz{track_num}.mp3")
        except Exception as e:
            print(f"Failed playing gameplay music: {e}")

    def start_game(self, mode=MODE_CASUAL):
        self.selected_mode = mode
        self.score = 0
        self.game_timer = GAME_DURATION
        self.elapsed_timer = 0.0
        self.fade_timer = 0.5
        self.current_state = STATE_PLAYING
        self.show_mode_modal = False
        self.customer.reset()
        self.kitchen.reset_recipe()
        self.play_gameplay_music()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.current_state == STATE_HOME:
                    if self.show_mode_modal:
                        if self.casual_btn_rect.collidepoint(event.pos):
                            self.start_game(mode=MODE_CASUAL)
                        elif self.unlimited_btn_rect.collidepoint(event.pos):
                            self.start_game(mode=MODE_UNLIMITED)
                        else:
                            modal_box = pygame.Rect(35, 180, SCREEN_WIDTH - 70, 220)
                            if not modal_box.collidepoint(event.pos):
                                self.show_mode_modal = False
                    else:
                        if self.start_btn_rect.collidepoint(event.pos):
                            self.show_mode_modal = True
                            self.modal_anim_timer = 0.0

                elif self.current_state == STATE_PLAYING:
                    # 1. Pause Button
                    if self.pause_btn_rect.collidepoint(event.pos):
                        self.current_state = STATE_PAUSED
                        return True

                    # 2. Unlimited Mode Close Asset Button
                    if self.selected_mode == MODE_UNLIMITED and self.close_btn_rect.collidepoint(event.pos):
                        self.current_state = STATE_GAMEOVER
                        print(f"Session Closed! Final Score: {self.score}")
                        return True

                    # 3. Kitchen Interaction
                    points = self.kitchen.handle_click(event.pos, self.oven, self.qte_bar, self.customer)
                    if points:
                        self.score += points

                elif self.current_state == STATE_PAUSED:
                    if self.resume_btn_rect.collidepoint(event.pos):
                        self.current_state = STATE_PLAYING
                    elif self.pause_restart_btn_rect.collidepoint(event.pos):
                        self.start_game(mode=self.selected_mode)
                    elif self.pause_home_btn_rect.collidepoint(event.pos):
                        self.current_state = STATE_HOME
                        self.home_anim_timer = 0.0
                        self.show_mode_modal = False
                        self.play_lobby_music()

                elif self.current_state == STATE_GAMEOVER:
                    if self.restart_btn_rect.collidepoint(event.pos):
                        self.start_game(mode=self.selected_mode)
                    elif self.gameover_home_btn_rect.collidepoint(event.pos):
                        self.current_state = STATE_HOME
                        self.home_anim_timer = 0.0
                        self.show_mode_modal = False
                        self.play_lobby_music()

            if event.type == pygame.KEYDOWN:
                if self.current_state == STATE_HOME:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if not self.show_mode_modal:
                            self.show_mode_modal = True
                            self.modal_anim_timer = 0.0
                        else:
                            self.start_game(mode=MODE_CASUAL)
                elif self.current_state == STATE_PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.current_state = STATE_PAUSED
                elif self.current_state == STATE_PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.current_state = STATE_PLAYING
                elif self.current_state == STATE_GAMEOVER:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.start_game(mode=self.selected_mode)
                        
        return True

    def update(self, dt):
        if self.current_state == STATE_HOME:
            self.home_anim_timer += dt
            if self.show_mode_modal:
                self.modal_anim_timer += dt

        elif self.current_state == STATE_PLAYING:
            if self.fade_timer > 0:
                self.fade_timer -= dt
                if self.fade_timer < 0:
                    self.fade_timer = 0.0

            if self.selected_mode == MODE_CASUAL:
                # 1-minute Countdown Timer
                self.game_timer -= dt
                if self.game_timer <= 0:
                    self.game_timer = 0
                    self.current_state = STATE_GAMEOVER
                    print(f"Time's up! Final Score: {self.score}")
            else:
                # Unlimited Mode Elapsed Timer
                self.elapsed_timer += dt

            has_left = self.customer.update(dt, self.current_state)
            if has_left:
                self.customer.reset()
                self.kitchen.reset_recipe()
                print("Pelanggan baru datang!")
                
            new_stage = self.oven.update(dt, self.kitchen.cookie_stage)
            if new_stage:
                self.kitchen.cookie_stage = new_stage
            
            earned_score = self.kitchen.update(dt, self.qte_bar, self.oven)
            if earned_score > 0:
                self.score += earned_score

    def draw(self):
        self.screen.fill(WHITE)

        if self.current_state == STATE_HOME:
            # 1. Warm Pastel Gradient Background
            self.screen.blit(self.home_bg_surf, (0, 0))

            # 2. Animated Logo Entrance (Pop-in bounce + continuous floating)
            t_logo = min(1.0, self.home_anim_timer / 0.7)
            ease_logo = ease_out_back(t_logo)
            logo_y = -150 + (175 - (-150)) * ease_logo
            float_y = math.sin(self.home_anim_timer * 2.5) * 6 * t_logo
            anim_logo_rect = self.logo_img.get_rect(center=(SCREEN_WIDTH // 2, int(logo_y + float_y)))
            self.screen.blit(self.logo_img, anim_logo_rect)

            # 3. Animated Start Button (Ease-out entry scaling)
            t_btn = max(0.0, min(1.0, (self.home_anim_timer - 0.25) / 0.5))
            ease_btn = ease_out_back(t_btn)
            scale_factor = max(0.01, ease_btn)

            btn_w = max(1, int(180 * scale_factor))
            btn_h = max(1, int(54 * scale_factor))
            scaled_btn = pygame.transform.scale(self.start_btn_img, (btn_w, btn_h))
            self.start_btn_rect = scaled_btn.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            self.screen.blit(scaled_btn, self.start_btn_rect)

            # 4. Animated Pulsing Hint Subtext
            t_hint = max(0.0, min(1.0, (self.home_anim_timer - 0.5) / 0.4))
            if t_hint > 0:
                hint_surf = self.font_sub.render("Tekan SPACE atau Klik START", True, DARK_GRAY)
                hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, self.start_btn_rect.bottom + 25))
                self.screen.blit(hint_surf, hint_rect)

            # 5. Animated Mode Selection Modal Pop-in
            if self.show_mode_modal:
                t_m = min(1.0, self.modal_anim_timer / 0.3)
                ease_m = ease_out_back(t_m)

                # Fade in backdrop overlay
                alpha_m = int(160 * min(1.0, self.modal_anim_timer / 0.2))
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, alpha_m))
                self.screen.blit(overlay, (0, 0))

                # Modal Card Pop-in scaling
                m_w = max(10, int((SCREEN_WIDTH - 70) * ease_m))
                m_h = max(10, int(220 * ease_m))
                modal_rect = pygame.Rect(0, 0, m_w, m_h)
                modal_rect.center = (SCREEN_WIDTH // 2, 290)

                pygame.draw.rect(self.screen, (30, 30, 40), modal_rect, border_radius=16)
                pygame.draw.rect(self.screen, GOLD, modal_rect, width=3, border_radius=16)

                if t_m >= 0.4:
                    m_title = self.font_start.render("PILIH MODE PERMAINAN", True, GOLD)
                    self.screen.blit(m_title, m_title.get_rect(center=(SCREEN_WIDTH // 2, 215)))

                    # Casual Mode Button
                    pygame.draw.rect(self.screen, (40, 160, 220), self.casual_btn_rect, border_radius=10)
                    pygame.draw.rect(self.screen, WHITE, self.casual_btn_rect, width=2, border_radius=10)
                    c_txt = self.font_start.render("CASUAL (1 MIN)", True, WHITE)
                    self.screen.blit(c_txt, c_txt.get_rect(center=self.casual_btn_rect.center))

                    # Unlimited Mode Button
                    pygame.draw.rect(self.screen, (220, 140, 40), self.unlimited_btn_rect, border_radius=10)
                    pygame.draw.rect(self.screen, WHITE, self.unlimited_btn_rect, width=2, border_radius=10)
                    u_txt = self.font_start.render("UNLIMITED MODE", True, WHITE)
                    self.screen.blit(u_txt, u_txt.get_rect(center=self.unlimited_btn_rect.center))

        elif self.current_state in (STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER):
            # Render Gameplay World
            self.screen.blit(self.half_upper_img, self.half_upper_rect)
            self.screen.blit(self.half_bottom_img, self.half_bottom_rect)
            
            self.customer.draw(self.screen, self.kitchen.cookie_stage)
            self.kitchen.draw(self.screen, show_hitboxes=self.show_hitboxes)
            self.oven.draw(self.screen)
            self.qte_bar.draw(self.screen)

            # Pause Button Top-Left (2 Garis Vertikal || Tanpa Box Outer Line)
            bar_w = 3
            bar_h = 14
            bar_y = self.pause_btn_rect.centery - (bar_h // 2)
            pygame.draw.rect(self.screen, WHITE, (self.pause_btn_rect.centerx - 4, bar_y, bar_w, bar_h), border_radius=1)
            pygame.draw.rect(self.screen, WHITE, (self.pause_btn_rect.centerx + 2, bar_y, bar_w, bar_h), border_radius=1)

            # Timer Pill (Top-Left next to Pause button)
            if self.selected_mode == MODE_CASUAL:
                mins = int(self.game_timer) // 60
                secs = int(self.game_timer) % 60
                time_str = f"TIME: {mins}:{secs:02d}"
                time_color = (255, 60, 60) if self.game_timer <= 10.0 else WHITE
            else:
                mins = int(self.elapsed_timer) // 60
                secs = int(self.elapsed_timer) % 60
                time_str = f"TIME: {mins}:{secs:02d}"
                time_color = GOLD

            time_surf = self.font_sub.render(time_str, True, time_color)
            time_rect = time_surf.get_rect(topleft=(54, 15))
            bg_time = time_rect.inflate(14, 6)
            pygame.draw.rect(self.screen, (30, 30, 30), bg_time, border_radius=6)
            self.screen.blit(time_surf, time_rect)

            # Score Pill (Top-Right)
            score_surf = self.font_sub.render(f"SCORE: {self.score}", True, GOLD)
            score_rect = score_surf.get_rect(topright=(SCREEN_WIDTH - 12, 15))
            bg_score = score_rect.inflate(14, 6)
            pygame.draw.rect(self.screen, (30, 30, 30), bg_score, border_radius=6)
            self.screen.blit(score_surf, score_rect)

            # Render Close Button Asset in Unlimited Mode (Bottom-Right of half-bottom)
            if self.selected_mode == MODE_UNLIMITED:
                self.screen.blit(self.close_btn_img, self.close_btn_rect)

            # Fade-out Black Overlay Transition on Game Start
            if self.fade_timer > 0:
                alpha = int(255 * (self.fade_timer / 0.5))
                fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                fade_surf.fill((0, 0, 0, alpha))
                self.screen.blit(fade_surf, (0, 0))

            # -----------------------------------------------------------------
            # PAUSED OVERLAY
            # -----------------------------------------------------------------
            if self.current_state == STATE_PAUSED:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))

                modal_rect = pygame.Rect(40, 140, SCREEN_WIDTH - 80, 250)
                pygame.draw.rect(self.screen, (30, 30, 40), modal_rect, border_radius=14)
                pygame.draw.rect(self.screen, GOLD, modal_rect, width=2, border_radius=14)

                p_title = self.font_title.render("GAME PAUSED", True, GOLD)
                self.screen.blit(p_title, p_title.get_rect(center=(SCREEN_WIDTH // 2, 175)))

                # Resume Button
                pygame.draw.rect(self.screen, (50, 160, 70), self.resume_btn_rect, border_radius=8)
                r_txt = self.font_start.render("RESUME", True, WHITE)
                self.screen.blit(r_txt, r_txt.get_rect(center=self.resume_btn_rect.center))

                # Restart Button
                pygame.draw.rect(self.screen, (200, 140, 40), self.pause_restart_btn_rect, border_radius=8)
                pr_txt = self.font_start.render("RESTART", True, WHITE)
                self.screen.blit(pr_txt, pr_txt.get_rect(center=self.pause_restart_btn_rect.center))

                # Home Button
                pygame.draw.rect(self.screen, (180, 50, 50), self.pause_home_btn_rect, border_radius=8)
                ph_txt = self.font_start.render("MAIN MENU", True, WHITE)
                self.screen.blit(ph_txt, ph_txt.get_rect(center=self.pause_home_btn_rect.center))

            # -----------------------------------------------------------------
            # GAME OVER / RESULTS OVERLAY
            # -----------------------------------------------------------------
            elif self.current_state == STATE_GAMEOVER:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 190))
                self.screen.blit(overlay, (0, 0))

                modal_rect = pygame.Rect(30, 110, SCREEN_WIDTH - 60, 340)
                pygame.draw.rect(self.screen, (30, 30, 40), modal_rect, border_radius=16)
                pygame.draw.rect(self.screen, GOLD, modal_rect, width=3, border_radius=16)

                header_title = "TIME'S UP!" if self.selected_mode == MODE_CASUAL else "SESSION CLOSED!"
                title_surf = self.font_title.render(header_title, True, GOLD)
                self.screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 150)))

                score_lbl = self.font_sub.render("FINAL SCORE", True, DARK_GRAY)
                self.screen.blit(score_lbl, score_lbl.get_rect(center=(SCREEN_WIDTH // 2, 195)))

                score_val = self.font_title.render(f"{self.score} PTS", True, WHITE)
                self.screen.blit(score_val, score_val.get_rect(center=(SCREEN_WIDTH // 2, 230)))

                # Rank Rating Evaluation
                if self.score >= 3000:
                    rank_str = "RANK S: MASTER CHEF!"
                    rank_color = GOLD
                elif self.score >= 2000:
                    rank_str = "RANK A: PRO BAKER!"
                    rank_color = (100, 230, 100)
                elif self.score >= 1000:
                    rank_str = "RANK B: GOOD JOB!"
                    rank_color = (100, 200, 255)
                else:
                    rank_str = "RANK C: KEEP PRACTICING!"
                    rank_color = (220, 220, 220)

                rank_surf = self.font_start.render(rank_str, True, rank_color)
                self.screen.blit(rank_surf, rank_surf.get_rect(center=(SCREEN_WIDTH // 2, 280)))

                # Restart Button
                pygame.draw.rect(self.screen, (50, 160, 70), self.restart_btn_rect, border_radius=8)
                rst_txt = self.font_start.render("PLAY AGAIN", True, WHITE)
                self.screen.blit(rst_txt, rst_txt.get_rect(center=self.restart_btn_rect.center))

                # Home Button
                pygame.draw.rect(self.screen, (180, 50, 50), self.gameover_home_btn_rect, border_radius=8)
                hm_txt = self.font_start.render("MAIN MENU", True, WHITE)
                self.screen.blit(hm_txt, hm_txt.get_rect(center=self.gameover_home_btn_rect.center))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
