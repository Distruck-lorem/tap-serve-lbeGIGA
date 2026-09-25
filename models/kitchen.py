import pygame
from config import (
    STAGE_IDLE, STAGE_BOWL_CENTER, STAGE_HAS_FLOUR, STAGE_HAS_EGG,
    STAGE_HAS_BUTTER, STAGE_HAS_SUGAR, STAGE_WHISKING, STAGE_MIXED, STAGE_DOUGH_READY,
    STAGE_CUT_DOUGH, STAGE_HAS_CHOCOCHIP, STAGE_BAKING, STAGE_COOKIE_DONE, STAGE_SERVED
)
from models.whisk import WhiskGame

class Kitchen:
    def __init__(self, half_bottom_top, font_title, font_sub):
        self.half_bottom_top = half_bottom_top
        self.BOWL_INIT_POS = (100, half_bottom_top + 120)
        self.CENTER_MIX_POS = (140, half_bottom_top + 190)
        self.bowl_pos = list(self.BOWL_INIT_POS)
        
        # Load Bowls
        self.bowl_empty_img = pygame.transform.scale(pygame.image.load("asset/bahan/Bowl-Bowl-Empty.png").convert_alpha(), (80, 60))
        self.bowl_flour_img = pygame.transform.scale(pygame.image.load("asset/bahan/Bowl-Bowl-Flour.png").convert_alpha(), (80, 60))
        self.bowl_flouregg_img = pygame.transform.scale(pygame.image.load("asset/bahan/Bowl-Bowl-FlourEgg.png").convert_alpha(), (80, 60))
        self.bowl_floureggbutter_img = pygame.transform.scale(pygame.image.load("asset/bahan/Bowl-Bowl-FlourEggButter.png").convert_alpha(), (80, 60))
        self.bowl_mixed_img = pygame.transform.scale(pygame.image.load("asset/bahan/Bowl-Bowl-Mixed.png").convert_alpha(), (80, 60))
        self.current_bowl_img = self.bowl_empty_img
        
        # Load Doughs & Cookies
        self.raw_dough_img = pygame.transform.scale(pygame.image.load("asset/bahan/dough.png").convert_alpha(), (130, 116))
        self.cookie_dough_img = pygame.transform.scale(pygame.image.load("asset/bahan/Cookies-Cookie-Dough.png").convert_alpha(), (50, 50))
        self.cookie_dough_chocochip_img = pygame.transform.scale(pygame.image.load("asset/bahan/Cookies-Dough-Chocochip.png").convert_alpha(), (50, 50))
        self.cookie_done_img = pygame.transform.scale(pygame.image.load("asset/bahan/Cookies-Cookie-Done.png").convert_alpha(), (50, 50))
        
        # Recipe Stage & Scores
        self.cookie_stage = STAGE_IDLE
        self.whisk_score = 0
        self.baking_score = 0
        self.font_label = pygame.font.Font(None, 18)
        
        # Instantiate Whisk Mini-Game
        self.whisk_game = WhiskGame(font_title=font_title, font_sub=font_sub, half_bottom_top=half_bottom_top)

        # Load Sound Effects (SFX)
        self.sfx_butter = self.load_sound("asset/audio/sfx/drop-butter.wav")
        self.sfx_egg = self.load_sound("asset/audio/sfx/egg-crack.wav")
        self.sfx_microwave = self.load_sound("asset/audio/sfx/microwave.wav")
        if self.sfx_microwave:
            self.sfx_microwave.set_volume(0.5)  # Volume 50%
        self.sfx_whisking = self.load_sound("asset/audio/sfx/whisking.wav")

        # Hitboxes
        self.flour        = pygame.Rect(35, half_bottom_top + 37, 40, 45)
        self.egg          = pygame.Rect(87, half_bottom_top + 46, 30, 32)
        self.butter       = pygame.Rect(125, half_bottom_top + 57, 32, 22)
        self.sugar        = pygame.Rect(163, half_bottom_top + 55, 30, 23)
        self.chocochip    = pygame.Rect(200, half_bottom_top + 41, 30, 40)
        self.cookieCutter = pygame.Rect(216, half_bottom_top + 150, 40, 30)
        self.whisker      = pygame.Rect(42, half_bottom_top + 115, 29, 40)

        self.hitboxes = [
            {"rect": self.flour,        "color": (255, 0, 0),     "name": "Flour"},
            {"rect": self.egg,          "color": (0, 255, 0),     "name": "Egg"},
            {"rect": self.butter,       "color": (0, 0, 255),     "name": "Butter"},
            {"rect": self.sugar,        "color": (255, 255, 0),   "name": "Sugar"},
            {"rect": self.chocochip,    "color": (255, 0, 255),   "name": "Chocochip"},
            {"rect": self.cookieCutter, "color": (0, 255, 255),   "name": "CookieCutter"},
            {"rect": self.whisker,      "color": (255, 128, 0),   "name": "Whisker"},
        ]

    def load_sound(self, path):
        try:
            if pygame.mixer.get_init():
                return pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Failed loading SFX {path}: {e}")
        return None

    def reset_recipe(self):
        self.bowl_pos = list(self.BOWL_INIT_POS)
        self.current_bowl_img = self.bowl_empty_img
        self.cookie_stage = STAGE_IDLE
        self.whisk_score = 0
        self.baking_score = 0

    def update(self, dt, qte_bar, oven):
        w_res, w_score = self.whisk_game.update(dt)
        if w_res == "MISS" and self.cookie_stage == STAGE_WHISKING:
            self.whisk_score = 0
            self.current_bowl_img = self.bowl_mixed_img
            self.cookie_stage = STAGE_MIXED

        qte_res, qte_score = qte_bar.update(dt)
        if qte_res == "MISS" and self.cookie_stage == STAGE_BAKING:
            self.baking_score = 0
            oven.stop_baking()
            self.cookie_stage = STAGE_COOKIE_DONE

        return 0

    def handle_click(self, pos, oven, qte_bar, customer):
        """Processes interaction click and updates recipe state. Returns score earned if any."""
        # Whisk click check
        if self.whisk_game.is_active:
            if self.sfx_whisking:
                self.sfx_whisking.play()
            result, score = self.whisk_game.handle_click()
            if result is not None:
                self.whisk_score = score
                self.current_bowl_img = self.bowl_mixed_img
                self.cookie_stage = STAGE_MIXED
            return 0

        # QTE tap check
        if qte_bar.is_active:
            qte_result, score = qte_bar.handle_tap()
            if qte_result is not None:
                self.baking_score = score
                oven.stop_baking()
                self.cookie_stage = STAGE_COOKIE_DONE
            return 0

        # 1. Bowl Click
        bowl_click_rect = self.current_bowl_img.get_rect(topleft=self.bowl_pos)
        if bowl_click_rect.collidepoint(pos):
            if self.cookie_stage == STAGE_IDLE:
                self.bowl_pos = list(self.CENTER_MIX_POS)
                self.cookie_stage = STAGE_BOWL_CENTER
                print("1. Bowl dipindah ke tengah half-bottom!")
            elif self.cookie_stage == STAGE_MIXED:
                self.bowl_pos = list(self.BOWL_INIT_POS)
                self.current_bowl_img = self.bowl_empty_img
                self.cookie_stage = STAGE_DOUGH_READY
                print("6. Bowl dikembalikan! Dough muncul di tengah.")

        # 2. Ingredients & Tools Clicks
        if self.flour.collidepoint(pos) and self.cookie_stage == STAGE_BOWL_CENTER:
            self.current_bowl_img = self.bowl_flour_img
            self.cookie_stage = STAGE_HAS_FLOUR
            print("2. Flour dimasukkan -> Bowl-Flour!")

        elif self.egg.collidepoint(pos) and self.cookie_stage == STAGE_HAS_FLOUR:
            self.current_bowl_img = self.bowl_flouregg_img
            self.cookie_stage = STAGE_HAS_EGG
            if self.sfx_egg:
                self.sfx_egg.play()
            print("3. Egg dimasukkan -> Bowl-FlourEgg!")

        elif self.butter.collidepoint(pos) and self.cookie_stage == STAGE_HAS_EGG:
            self.current_bowl_img = self.bowl_floureggbutter_img
            self.cookie_stage = STAGE_HAS_BUTTER
            if self.sfx_butter:
                self.sfx_butter.play()
            print("4. Butter dimasukkan -> Bowl-FlourEggButter!")

        elif self.sugar.collidepoint(pos) and self.cookie_stage == STAGE_HAS_BUTTER:
            self.cookie_stage = STAGE_HAS_SUGAR
            print("5. Sugar dimasukkan!")

        elif self.whisker.collidepoint(pos) and self.cookie_stage == STAGE_HAS_SUGAR:
            self.cookie_stage = STAGE_WHISKING
            self.whisk_game.start()
            if self.sfx_whisking:
                self.sfx_whisking.play()
            print("6. Whisk mini-game dimulai! Klik cepat!")

        elif self.cookieCutter.collidepoint(pos) and self.cookie_stage == STAGE_DOUGH_READY:
            self.cookie_stage = STAGE_CUT_DOUGH
            print("7. Cookie Cutter digunakan -> Cut Cookie Dough (tanpa chocochip)!")

        elif self.chocochip.collidepoint(pos) and self.cookie_stage == STAGE_CUT_DOUGH:
            self.cookie_stage = STAGE_HAS_CHOCOCHIP
            print("7b. Chocochip ditambahkan -> Cookies-Dough-Chocochip!")

        # 3. Oven Click
        elif oven.collidepoint(pos) and self.cookie_stage in (STAGE_CUT_DOUGH, STAGE_HAS_CHOCOCHIP):
            self.cookie_stage = STAGE_BAKING
            oven.start_baking()
            qte_bar.activate()
            if self.sfx_microwave:
                self.sfx_microwave.play()
            print("8. Cookie dough masuk oven -> Memasak, Animasi Oven & QTE aktif bersamaan!")

        # 4. Serve Finished Cookie to Customer (Hitung Final Score Berdasarkan Kualitas)
        elif self.cookie_stage == STAGE_COOKIE_DONE:
            done_cookie_rect = self.cookie_done_img.get_rect(center=(oven.rect.centerx - 70, oven.rect.centery + 30))
            if done_cookie_rect.collidepoint(pos) or customer.collidepoint(pos):
                self.cookie_stage = STAGE_SERVED
                customer.start_leaving()
                
                # Formula Kualitas & Final Score
                BASE_SCORE = 1000
                total_mini_game_score = self.whisk_score + self.baking_score
                quality_percentage = (total_mini_game_score / 120.0) * 100.0
                final_score = round(BASE_SCORE * quality_percentage / 100.0)
                
                print(f"10. Cookie disajikan! Whisk: {self.whisk_score}, Baking: {self.baking_score} -> Quality: {quality_percentage:.1f}%, Final Score: +{final_score}")
                return final_score

        return 0

    def draw(self, screen, show_hitboxes=False):
        # Render Bowl
        screen.blit(self.current_bowl_img, self.bowl_pos)

        # Render Dough at center workspace
        if self.cookie_stage == STAGE_DOUGH_READY:
            dough_rect = self.raw_dough_img.get_rect(center=(self.CENTER_MIX_POS[0] + 40, self.CENTER_MIX_POS[1] + 40))
            screen.blit(self.raw_dough_img, dough_rect)
        elif self.cookie_stage == STAGE_CUT_DOUGH:
            dough_rect = self.cookie_dough_img.get_rect(center=(self.CENTER_MIX_POS[0] + 40, self.CENTER_MIX_POS[1] + 50))
            screen.blit(self.cookie_dough_img, dough_rect)
        elif self.cookie_stage == STAGE_HAS_CHOCOCHIP:
            dough_rect = self.cookie_dough_chocochip_img.get_rect(center=(self.CENTER_MIX_POS[0] + 40, self.CENTER_MIX_POS[1] + 50))
            screen.blit(self.cookie_dough_chocochip_img, dough_rect)

        # Render Baked Cookie
        if self.cookie_stage == STAGE_COOKIE_DONE:
            done_cookie_rect = self.cookie_done_img.get_rect(center=(self.CENTER_MIX_POS[0] + 40, self.CENTER_MIX_POS[1] + 50))
            screen.blit(self.cookie_done_img, done_cookie_rect)

        # Render Ingredient Labels (Posisi (x, y) dapat diubah satu per satu di bawah ini)
        ingredient_items = [
            {"text": "Flour",  "pos": (self.flour.centerx, self.flour.bottom + 8)},
            {"text": "Egg",    "pos": (self.egg.centerx, self.egg.bottom + 8)},
            {"text": "Butter", "pos": (self.butter.centerx, self.butter.bottom + 20)},
            {"text": "Sugar",  "pos": (self.sugar.centerx, self.sugar.bottom + 3)},
            {"text": "Choco",  "pos": (self.chocochip.centerx, self.chocochip.bottom + 16)},
        ]
        
        for item in ingredient_items:
            lbl_surf = self.font_label.render(item["text"], True, (30, 30, 30))
            lbl_rect = lbl_surf.get_rect(center=item["pos"])
            # Background pill for high contrast & clarity
            bg_pill = lbl_rect.inflate(8, 4)
            pygame.draw.rect(screen, (255, 255, 255, 220), bg_pill, border_radius=4)
            pygame.draw.rect(screen, (100, 100, 100), bg_pill, width=1, border_radius=4)
            screen.blit(lbl_surf, lbl_rect)

        # Render Whisk Mini-Game
        self.whisk_game.draw(screen)

        # Render Hitboxes (Optional debugging)
        if show_hitboxes:
            for hb in self.hitboxes:
                pygame.draw.rect(screen, hb["color"], hb["rect"])
