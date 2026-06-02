import pygame
import math
import sys
import os
import random
import json

# ==========================================
# KONSTANSOK ÉS BEÁLLÍTÁSOK
# ==========================================
FPS = 60
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GRID_SIZE = 40  # Új: Grid mérete (40x40 pixel)
HUD_HEIGHT = 100 # Alsó panel magassága

# Színek
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 20)
GREEN = (20, 220, 20)
BLUE = (20, 20, 220)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (173, 216, 230)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
UI_BG_COLOR = (30, 30, 35)

# Alapértelmezett beállítások
STARTING_MONEY = 350
STARTING_LIVES = 20

# Torony típusok konfigurációja
TOWER_CONFIG = {
    "archer": {
        "name": "Íjász",
        "cost": 100,
        "damage": 15,
        "range": 160,
        "cooldown": 45, # frame-ben (60 FPS esetén 45 = 0.75 mp)
        "color": BLUE,
        "projectile_speed": 8,
        "projectile_color": BLACK,
        "image": "tower1.png",
        "upgrade_cost": 50,
        "upgrade_damage": 5,
        "upgrade_range": 20
    },
    "cannon": {
        "name": "Ágyú",
        "cost": 200,
        "damage": 40,
        "range": 120,
        "cooldown": 90, # 1.5 mp
        "color": BLACK,
        "projectile_speed": 5,
        "projectile_color": RED,
        "image": "tower2.png",
        "upgrade_cost": 100,
        "upgrade_damage": 15,
        "upgrade_range": 10
    },
    "mage": {
        "name": "Varázsló",
        "cost": 150,
        "damage": 8,
        "range": 200,
        "cooldown": 15, # 0.25 mp
        "color": (128, 0, 128), # Lila
        "projectile_speed": 10,
        "projectile_color": (0, 255, 255),
        "image": "tower3.png",
        "upgrade_cost": 75,
        "upgrade_damage": 3,
        "upgrade_range": 30
    }
}

# Ellenség típusok konfigurációja
ENEMY_CONFIG = {
    "goblin": {
        "hp": 30,
        "speed": 2.5,
        "reward": 5,
        "color": GREEN,
        "image": "enemy1.png",
        "size": 20
    },
    "orc": {
        "hp": 80,
        "speed": 1.5,
        "reward": 10,
        "color": (0, 100, 0), # Sötétzöld
        "image": "enemy2.png",
        "size": 25
    },
    "troll": {
        "hp": 250,
        "speed": 0.8,
        "reward": 25,
        "color": RED,
        "image": "enemy3.png",
        "size": 35
    }
}
# ==========================================
# ITEM RENDSZER
# ==========================================
# Minden item: (nev, ritkaság, dmg_bonus%, slow_bonus%, range_bonus%, leiras)
ITEMS = {
    # ── COMMON (10 db) ───────────────────────────────────────────
    "Rozsdás kard":         ("common", 0.08, 0.00, 0.00, "+8% torony sebzés"),
    "Fa pajzs":             ("common", 0.05, 0.05, 0.00, "+5% dmg, +5% lassítás"),
    "Íjász kesztyű":        ("common", 0.10, 0.00, 0.00, "+10% torony sebzés"),
    "Réz nyílhegy":         ("common", 0.07, 0.00, 0.05, "+7% dmg, +5% hatótáv"),
    "Tölgyfa telek":        ("common", 0.00, 0.08, 0.00, "+8% ellenség lassítás"),
    "Kopott gyűrű":         ("common", 0.05, 0.00, 0.10, "+5% dmg, +10% hatótáv"),
    "Kőgúla":               ("common", 0.00, 0.10, 0.00, "+10% ellenség lassítás"),
    "Mágus kalapács":       ("common", 0.12, 0.00, 0.00, "+12% torony sebzés"),
    "Ezüst csillag":        ("common", 0.06, 0.06, 0.06, "+6% dmg/slow/range"),
    "Homokzsák":            ("common", 0.00, 0.12, 0.00, "+12% ellenség lassítás"),

    # ── RARE (5 db) ──────────────────────────────────────────────
    "Acél pengeél":         ("rare",   0.20, 0.00, 0.00, "+20% torony sebzés"),
    "Fagyasztó rúna":       ("rare",   0.00, 0.25, 0.00, "+25% ellenség lassítás"),
    "Távolságnövelő":       ("rare",   0.10, 0.00, 0.20, "+10% dmg, +20% hatótáv"),
    "Vérgyémánt":           ("rare",   0.15, 0.15, 0.00, "+15% dmg, +15% lassítás"),
    "Viharszem":            ("rare",   0.12, 0.08, 0.12, "+12% dmg, +8% slow, +12% range"),

    # ── EPIC (3 db) ──────────────────────────────────────────────
    "Sárkányfog":           ("epic",   0.40, 0.00, 0.00, "+40% torony sebzés"),
    "Idő kristály":         ("epic",   0.00, 0.45, 0.00, "+45% ellenség lassítás"),
    "Végzet szeme":         ("epic",   0.25, 0.20, 0.20, "+25% dmg, +20% slow, +20% range"),

    # ── LEGENDARY (3 db) ─────────────────────────────────────────
    "Istenek kardja":       ("legendary", 0.80, 0.00, 0.00, "+80% torony sebzés"),
    "Örökkévalóság köve":   ("legendary", 0.00, 0.70, 0.00, "+70% ellenség lassítás"),
    "Mindenható ereklyé":   ("legendary", 0.50, 0.40, 0.40, "+50% dmg, +40% slow, +40% range"),
}

RARITY_COLORS = {
    "common":    WHITE,
    "rare":      LIGHT_BLUE,
    "epic":      (180, 0, 255),
    "legendary": GOLD,
}

RARITY_SELL_PRICE = {
    "common":    10,
    "rare":      30,
    "epic":      80,
    "legendary": 200,
}

INVENTORY_BASE_SIZE = 15
INVENTORY_EXPAND_COST = 50   # pénzbe kerül (nem goldba)
INVENTORY_EXPAND_AMOUNT = 5

KEY_COST   = 200   # kulcs ára pénzben
CRATE_COST = 300   # láda ára pénzben
SAVE_FILE  = "savegame.json"  

# Ritkaság szerinti drop pool
def _build_loot_pools():
    pools = {"common": [], "rare": [], "epic": [], "legendary": []}
    for name, data in ITEMS.items():
        pools[data[0]].append(name)
    return pools

LOOT_POOLS = _build_loot_pools()
# ==========================================
# SEGÉDFÜGGVÉNYEK (ASSET BETÖLTÉS TRY/EXCEPT-TEL)
# ==========================================
def load_image(filename, fallback_color, size, shape="rect"):
    """
    Megpróbál betölteni egy képet. Ha nem sikerül, létrehoz egy fallback alakzatot.
    Így a játék sosem omlik össze hiányzó fájlok miatt.
    """
    path = os.path.join("assets", filename)
    try:
        if not os.path.exists("assets"):
            os.makedirs("assets")
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)
    except (pygame.error, FileNotFoundError):
        # Fallback ha nincs kép
        surf = pygame.Surface(size, pygame.SRCALPHA)
        if shape == "circle":
            pygame.draw.circle(surf, fallback_color, (size[0]//2, size[1]//2), size[0]//2)
        else:
            surf.fill(fallback_color)
            pygame.draw.rect(surf, BLACK, surf.get_rect(), 2) # Keret
        return surf

def load_sound(filename):
    """
    Megpróbál betölteni egy hangot. Ha nem sikerül, egy "üres" hang objektumot ad vissza,
    amelynek play() metódusa nem csinál semmit.
    """
    path = os.path.join("assets", filename)
    try:
        return pygame.mixer.Sound(path)
    except (pygame.error, FileNotFoundError, NotImplementedError):
        class DummySound:
            def play(self): pass
            def set_volume(self, vol): pass
        return DummySound()

def draw_item_icon(surface, item_name, x, y, size=40):
    """
    Minden itemhez egyedi ikont rajzol pygame-ben.
    x, y: a négyzet bal felső sarka. size: méret pixelben.
    """
    rarity = ITEMS[item_name][0]
    bg_color = {
        "common":    (50, 50, 55),
        "rare":      (20, 40, 80),
        "epic":      (50, 10, 70),
        "legendary": (70, 50, 5),
    }.get(rarity, (50, 50, 55))

    border_color = RARITY_COLORS.get(rarity, WHITE)
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, bg_color, rect, border_radius=4)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=4)

    cx = x + size // 2
    cy = y + size // 2
    s = size  # shorthand

    # ── Egyedi ikonok itemenként ──────────────────────────────────────
    if item_name == "Rozsdás kard":
        # Kard: vízszintes vonal + markolat
        pygame.draw.line(surface, (180,140,80), (x+6, cy), (x+s-6, cy), 3)
        pygame.draw.line(surface, (120,80,40), (cx, cy), (cx, y+s-8), 3)
        pygame.draw.line(surface, (180,140,80), (cx-7, cy+4), (cx+7, cy+4), 2)

    elif item_name == "Fa pajzs":
        pts = [(cx, y+6), (x+s-7, cy-4), (x+s-7, cy+8), (cx, y+s-6), (x+7, cy+8), (x+7, cy-4)]
        pygame.draw.polygon(surface, (120, 70, 20), pts)
        pygame.draw.polygon(surface, (180, 110, 40), pts, 2)
        pygame.draw.line(surface, (100,60,15), (cx, cy-6), (cx, cy+8), 2)

    elif item_name == "Íjász kesztyű":
        pygame.draw.rect(surface, (160,100,50), (cx-7, cy-4, 14, 10), border_radius=3)
        for i in range(5):
            pygame.draw.rect(surface, (180,120,60), (x+5+i*6, cy-10, 4, 8), border_radius=2)

    elif item_name == "Réz nyílhegy":
        pts = [(cx, y+6), (cx-5, cy+8), (cx+5, cy+8)]
        pygame.draw.polygon(surface, (180,130,50), pts)
        pygame.draw.line(surface, (200,160,60), (cx, cy+8), (cx, y+s-6), 2)

    elif item_name == "Tölgyfa telek":
        pygame.draw.circle(surface, (30,120,30), (cx, cy-3), s//5)
        pygame.draw.circle(surface, (20,100,20), (cx-6, cy), s//6)
        pygame.draw.circle(surface, (20,100,20), (cx+6, cy), s//6)
        pygame.draw.line(surface, (100,60,10), (cx, cy+3), (cx, y+s-6), 3)

    elif item_name == "Kopott gyűrű":
        pygame.draw.circle(surface, (0,0,0), (cx, cy), s//4+1)
        pygame.draw.circle(surface, (160,140,100), (cx, cy), s//4, 3)
        pygame.draw.circle(surface, (100,200,220), (cx, cy-s//4), 4)

    elif item_name == "Kőgúla":
        pts = [(cx, y+6), (x+s-8, y+s-8), (x+8, y+s-8)]
        pygame.draw.polygon(surface, (140,140,140), pts)
        pygame.draw.polygon(surface, (180,180,180), pts, 2)

    elif item_name == "Mágus kalapács":
        pygame.draw.rect(surface, (80,80,90), (cx-9, cy-5, 18, 10), border_radius=2)
        pygame.draw.line(surface, (150,110,60), (cx+3, cy+5), (cx+8, y+s-7), 3)

    elif item_name == "Ezüst csillag":
        for i in range(5):
            angle = math.radians(i * 72 - 90)
            ex = int(cx + math.cos(angle) * (s//3))
            ey = int(cy + math.sin(angle) * (s//3))
            pygame.draw.line(surface, (200,200,220), (cx, cy), (ex, ey), 2)
        pygame.draw.circle(surface, (220,220,240), (cx, cy), 4)

    elif item_name == "Homokzsák":
        pygame.draw.ellipse(surface, (160,130,80), (cx-8, cy-10, 16, 20))
        pygame.draw.line(surface, (120,90,40), (cx-8, cy-2), (cx+8, cy-2), 2)

    elif item_name == "Acél pengeél":
        pts = [(cx, y+5), (cx+8, cy+5), (cx, y+s-7), (cx-8, cy+5)]
        pygame.draw.polygon(surface, (160,170,190), pts)
        pygame.draw.line(surface, (220,230,255), (cx, y+5), (cx, y+s-7), 1)

    elif item_name == "Fagyasztó rúna":
        for i in range(6):
            angle = math.radians(i * 60)
            ex = int(cx + math.cos(angle) * (s//3))
            ey = int(cy + math.sin(angle) * (s//3))
            pygame.draw.line(surface, (100,200,255), (cx, cy), (ex, ey), 2)
        pygame.draw.circle(surface, (180,230,255), (cx, cy), 4)

    elif item_name == "Távolságnövelő":
        pygame.draw.line(surface, (200,200,50), (x+6, cy), (x+s-6, cy), 2)
        pygame.draw.circle(surface, (200,200,50), (x+6, cy), 4)
        pygame.draw.circle(surface, (200,200,50), (x+s-6, cy), 4)
        pygame.draw.rect(surface, (180,180,40), (cx-4, cy-8, 8, 6))

    elif item_name == "Vérgyémánt":
        pts = [(cx, y+6), (cx+10, cy), (cx, y+s-6), (cx-10, cy)]
        pygame.draw.polygon(surface, (180,0,50), pts)
        pygame.draw.polygon(surface, (255,80,80), [(cx, y+8), (cx+6, cy), (cx, y+s-8), (cx-6, cy)], 1)

    elif item_name == "Viharszem":
        pygame.draw.ellipse(surface, (30,30,80), (cx-10, cy-6, 20, 12))
        pygame.draw.ellipse(surface, (100,150,255), (cx-5, cy-3, 10, 6))
        pygame.draw.circle(surface, (200,220,255), (cx, cy), 3)

    elif item_name == "Sárkányfog":
        pts = [(cx, y+5), (cx+6, cy+6), (cx+3, y+s-7), (cx-3, y+s-7), (cx-6, cy+6)]
        pygame.draw.polygon(surface, (220,80,20), pts)
        pygame.draw.line(surface, (255,180,50), (cx, y+5), (cx, y+s-7), 1)

    elif item_name == "Idő kristály":
        pygame.draw.polygon(surface, (150,100,255), [(cx, y+5), (cx+8, cy), (cx+8, cy+8), (cx, y+s-5), (cx-8, cy+8), (cx-8, cy)])
        pygame.draw.polygon(surface, (200,180,255), [(cx, y+5), (cx+8, cy), (cx+8, cy+8), (cx, y+s-5), (cx-8, cy+8), (cx-8, cy)], 2)
        pygame.draw.circle(surface, (230,210,255), (cx, cy), 4)

    elif item_name == "Végzet szeme":
        pygame.draw.ellipse(surface, (20,20,20), (cx-10, cy-6, 20, 12))
        pygame.draw.ellipse(surface, (180,20,20), (cx-6, cy-4, 12, 8))
        pygame.draw.circle(surface, (0,0,0), (cx, cy), 3)
        pygame.draw.circle(surface, (255,255,255), (cx-1, cy-1), 1)

    elif item_name == "Istenek kardja":
        # Nagy arany kard
        pygame.draw.line(surface, (255,215,0), (cx, y+4), (cx, y+s-4), 4)
        pygame.draw.line(surface, (255,215,0), (x+5, cy-2), (x+s-5, cy-2), 3)
        pygame.draw.circle(surface, (255,240,100), (cx, cy-2), 3)
        # Szárnyak
        pygame.draw.line(surface, (220,180,30), (x+5, cy-2), (cx-4, y+8), 1)
        pygame.draw.line(surface, (220,180,30), (x+s-5, cy-2), (cx+4, y+8), 1)

    elif item_name == "Örökkévalóság köve":
        # Forgó körök
        pygame.draw.circle(surface, (0,0,0), (cx, cy), s//4+1)
        pygame.draw.circle(surface, (80,0,200), (cx, cy), s//4, 3)
        pygame.draw.circle(surface, (180,100,255), (cx, cy), s//6, 2)
        pygame.draw.circle(surface, (220,200,255), (cx, cy), 4)

    elif item_name == "Mindenható ereklyé":
        # Korona forma
        pts = [(cx-10, cy+6), (cx-10, cy-4), (cx-6, cy-10), (cx, cy-4),
               (cx+6, cy-10), (cx+10, cy-4), (cx+10, cy+6)]
        pygame.draw.polygon(surface, (255,215,0), pts)
        pygame.draw.polygon(surface, (255,255,150), pts, 2)
        pygame.draw.circle(surface, (255,50,50), (cx-6, cy-2), 3)
        pygame.draw.circle(surface, (50,150,255), (cx, cy-4), 3)
        pygame.draw.circle(surface, (50,255,50), (cx+6, cy-2), 3)

    else:
        # Általános fallback: rarity szín "?" jellel
        font_fb = pygame.font.SysFont("Arial", size//2, bold=True)
        t = font_fb.render("?", True, border_color)
        surface.blit(t, (cx - t.get_width()//2, cy - t.get_height()//2))


def load_music(filename):
    """
    Háttérzene betöltése hibakezeléssel.
    """
    path = os.path.join("assets", filename)
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except (pygame.error, FileNotFoundError, NotImplementedError):
        pass # Nem probléma, ha nincs zene

# ==========================================
# OSZTÁLYOK: UI ELEMEK
# ==========================================
class Button:
    """Grafikus gomb a menükhöz és az UI-hoz, automatikus szöveg skálázással."""
    def __init__(self, x, y, width, height, text, font, bg_color, text_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.action = action
        self.hovered = False
        self.padding = 10 # Belső margó a szövegnek

    def draw(self, surface):
        # Hover effektus (szín világosítása)
        if self.hovered:
            color = (min(self.bg_color[0] + 40, 255), 
                     min(self.bg_color[1] + 40, 255), 
                     min(self.bg_color[2] + 40, 255))
        else:
            color = self.bg_color
            
        # Gomb alapjának rajzolása
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE if self.hovered else BLACK, self.rect, 2, border_radius=8)
        
        # Szöveg renderelése és automatikus skálázása, ha túllóg
        text_surf = self.font.render(self.text, True, self.text_color)
        max_width = self.rect.width - (self.padding * 2)
        max_height = self.rect.height - (self.padding * 2)
        
        # Ha a szöveg szélesebb vagy magasabb a rendelkezésre álló helynél
        if text_surf.get_width() > max_width or text_surf.get_height() > max_height:
            scale_w = max_width / text_surf.get_width()
            scale_h = max_height / text_surf.get_height()
            scale_factor = min(scale_w, scale_h) # Az arányok megtartása
            
            new_width = int(text_surf.get_width() * scale_factor)
            new_height = int(text_surf.get_height() * scale_factor)
            text_surf = pygame.transform.smoothscale(text_surf, (new_width, new_height))
            
        # Szöveg középre igazítása
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                self.action()

class FloatingText:
    """Lebegő szöveg (pl. sebzés vagy pénz jelzésére)."""
    def __init__(self, x, y, text, color, font, duration=60):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = font
        self.duration = duration
        self.timer = duration
        self.alpha = 255

    def update(self):
        self.y -= 1
        self.timer -= 1
        self.alpha = max(0, int((self.timer / self.duration) * 255))
        return self.timer <= 0

    def draw(self, surface):
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        surface.blit(text_surf, (self.x, self.y))

# ==========================================
# OSZTÁLYOK: CS:GO LÁDA ANIMÁCIÓ
# ==========================================
class CrateOpenAnimation:
    """
    CS:GO stílusú láda nyitás animáció.
    Egy görgető sáv mutat véletlenszerű itemeket, majd lelassul és megáll a nyerőnél.
    """
    STRIP_ITEMS = 30        # Hány item jelenjen meg a sávban
    ITEM_W      = 100       # Egy item szélessége
    ITEM_H      = 100       # Egy item magassága
    STRIP_W     = 700       # Látható sáv szélessége
    SPIN_FRAMES = 180       # Összesen ennyi frame az animáció
    EASE_START  = 80        # Ettől a frame-től kezdve lassul

    def __init__(self, won_item, won_rarity, font_small, font_medium, font_large, screen_w, screen_h):
        self.won_item   = won_item
        self.won_rarity = won_rarity
        self.font_small  = font_small
        self.font_medium = font_medium
        self.font_large  = font_large
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.frame   = 0
        self.done    = False
        self.showing_result = False
        self.result_timer = 0

        # Generálunk egy véletlenszerű item-sorozatot; a közepére (14. slot) kerül a nyerő
        all_items = list(ITEMS.keys())
        self.strip_items = []
        for i in range(self.STRIP_ITEMS):
            if i == self.STRIP_ITEMS // 2:
                self.strip_items.append(won_item)
            else:
                self.strip_items.append(random.choice(all_items))

        # A nyerő item pixel-pozíciója a sávban (közép)
        win_idx = self.STRIP_ITEMS // 2
        self.target_offset = win_idx * self.ITEM_W - (self.STRIP_W // 2 - self.ITEM_W // 2)

        # Kezdő offset: balról indul
        self.start_offset = 0
        self.current_offset = float(self.start_offset)

    def _ease_out(self, t):
        """Exponenciális lassítás (0→1)."""
        return 1 - (1 - t) ** 3

    def update(self):
        if self.showing_result:
            self.result_timer += 1
            if self.result_timer > 180:
                self.done = True
            return

        self.frame += 1
        t = self.frame / self.SPIN_FRAMES

        if self.frame >= self.SPIN_FRAMES:
            self.current_offset = float(self.target_offset)
            self.showing_result = True
            self.result_timer = 0
        else:
            eased = self._ease_out(t)
            self.current_offset = self.start_offset + eased * (self.target_offset - self.start_offset)

    def draw(self, surface):
        # Sötét overlay
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        surface.blit(overlay, (0, 0))

        strip_x = self.screen_w // 2 - self.STRIP_W // 2
        strip_y = self.screen_h // 2 - self.ITEM_H // 2

        # "LÁDA NYITÁS" felirat
        title = self.font_large.render("LÁDA NYITÁS", True, GOLD)
        surface.blit(title, (self.screen_w // 2 - title.get_width() // 2, strip_y - 80))

        # Sáv háttér
        pygame.draw.rect(surface, (20, 20, 25), (strip_x - 2, strip_y - 2, self.STRIP_W + 4, self.ITEM_H + 4))

        # Clip a sávra
        clip_rect = pygame.Rect(strip_x, strip_y, self.STRIP_W, self.ITEM_H)
        surface.set_clip(clip_rect)

        for i, item_name in enumerate(self.strip_items):
            ix = strip_x + i * self.ITEM_W - int(self.current_offset)
            iy = strip_y

            if ix + self.ITEM_W < strip_x or ix > strip_x + self.STRIP_W:
                continue  # Nem látható, skip

            rarity = ITEMS[item_name][0]
            bg = {
                "common":    (40, 40, 45),
                "rare":      (15, 30, 65),
                "epic":      (40, 8, 58),
                "legendary": (60, 45, 5),
            }.get(rarity, (40, 40, 45))
            border = RARITY_COLORS.get(rarity, WHITE)

            pygame.draw.rect(surface, bg, (ix+2, iy+2, self.ITEM_W-4, self.ITEM_H-4))
            pygame.draw.rect(surface, border, (ix+2, iy+2, self.ITEM_W-4, self.ITEM_H-4), 2)

            # Item ikon (48x48, középre igazítva)
            icon_surf = pygame.Surface((48, 48), pygame.SRCALPHA)
            draw_item_icon(icon_surf, item_name, 0, 0, size=48)
            surface.blit(icon_surf, (ix + (self.ITEM_W - 48) // 2, iy + 8))

            # Item neve (nagyon rövidítve)
            short = item_name[:10] + "…" if len(item_name) > 10 else item_name
            name_surf = pygame.font.SysFont("Arial", 13).render(short, True, border)
            surface.blit(name_surf, (ix + self.ITEM_W//2 - name_surf.get_width()//2, iy + 62))

        surface.set_clip(None)

        # Közép jelölő nyíl
        mid_x = self.screen_w // 2
        pygame.draw.polygon(surface, GOLD, [
            (mid_x - 10, strip_y - 6),
            (mid_x + 10, strip_y - 6),
            (mid_x, strip_y + 4)
        ])
        pygame.draw.polygon(surface, GOLD, [
            (mid_x - 10, strip_y + self.ITEM_H + 6),
            (mid_x + 10, strip_y + self.ITEM_H + 6),
            (mid_x, strip_y + self.ITEM_H - 4)
        ])
        # Függőleges vonalak a "nyerő ablakra"
        pygame.draw.line(surface, GOLD, (mid_x - self.ITEM_W//2, strip_y - 2),
                         (mid_x - self.ITEM_W//2, strip_y + self.ITEM_H + 2), 2)
        pygame.draw.line(surface, GOLD, (mid_x + self.ITEM_W//2, strip_y - 2),
                         (mid_x + self.ITEM_W//2, strip_y + self.ITEM_H + 2), 2)

        # Eredmény megjelenítése, ha megállt
        if self.showing_result:
            col = RARITY_COLORS.get(self.won_rarity, WHITE)
            # Fénylő háttér
            glow = pygame.Surface((500, 140), pygame.SRCALPHA)
            glow.fill((0, 0, 0, 0))
            alpha = min(200, self.result_timer * 5)
            glow.fill((*col[:3], min(60, alpha // 3)), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(glow, (self.screen_w // 2 - 250, strip_y + self.ITEM_H + 30))

            r_text = self.font_medium.render(f"{self.won_rarity.upper()} ITEM!", True, col)
            surface.blit(r_text, (self.screen_w // 2 - r_text.get_width() // 2, strip_y + self.ITEM_H + 30))

            i_text = self.font_medium.render(self.won_item, True, WHITE)
            surface.blit(i_text, (self.screen_w // 2 - i_text.get_width() // 2, strip_y + self.ITEM_H + 65))

            desc = ITEMS[self.won_item][4]
            d_text = self.font_small.render(desc, True, GRAY)
            surface.blit(d_text, (self.screen_w // 2 - d_text.get_width() // 2, strip_y + self.ITEM_H + 100))

            hint = self.font_small.render("(Az animáció rövidesen bezárul…)", True, DARK_GRAY)
            surface.blit(hint, (self.screen_w // 2 - hint.get_width() // 2, strip_y + self.ITEM_H + 128))


# ==========================================
# OSZTÁLYOK: JÁTÉKMECHANIKA
# ==========================================
class Projectile:
    """Lövedék, amit a tornyok lőnek az ellenségekre."""
    def __init__(self, x, y, target, damage, speed, color):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.color = color
        self.image = load_image("bullet.png", color, (10, 10), shape="circle")
        self.active = True
        
        # Ha az ellenség meghal mielőtt odaérne, ide tart utoljára
        self.last_target_pos = (target.x, target.y)

    def update(self):
        if self.target and self.target.active:
            self.last_target_pos = (self.target.x, self.target.y)
            
        dx = self.last_target_pos[0] - self.x
        dy = self.last_target_pos[1] - self.y
        dist = math.hypot(dx, dy)
        
        if dist < self.speed:
            self.active = False
            if self.target and self.target.active:
                self.target.take_damage(self.damage)
            return
            
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed

    def draw(self, surface):
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.image, rect)

class Tower:
    """Védekező torony (Grid rendszerhez igazítva)."""
    def __init__(self, grid_x, grid_y, tower_type, sound_shoot, game_state=None):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x + GRID_SIZE // 2
        self.y = grid_y + GRID_SIZE // 2
        self.type = tower_type
        self.sound_shoot = sound_shoot
        self.game_state = game_state
        
        config = TOWER_CONFIG[tower_type]
        self.name = config["name"]
        self.damage = config["damage"]
        self.range = config["range"]
        self.cooldown_max = config["cooldown"]
        self.cooldown_timer = 0
        self.color = config["color"]
        
        self.proj_speed = config["projectile_speed"]
        self.proj_color = config["projectile_color"]
        
        self.level = 1
        self.upgrade_cost = config["upgrade_cost"]
        self.upgrade_damage = config["upgrade_damage"]
        self.upgrade_range = config["upgrade_range"]
        
        # A torony mérete illeszkedjen a gridhez
        self.image = load_image(config["image"], self.color, (GRID_SIZE - 4, GRID_SIZE - 4))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
        self.target = None

    def upgrade(self, game_state):
        """Torony fejlesztése, ha van rá elég pénz."""
        if game_state.money >= self.upgrade_cost:
            game_state.money -= self.upgrade_cost
            self.level += 1
            self.damage += self.upgrade_damage
            self.range += self.upgrade_range
            self.upgrade_cost = int(self.upgrade_cost * 1.5)
            return True
        return False

    def get_distance(self, enemy):
        return math.hypot(enemy.x - self.x, enemy.y - self.y)

    def find_target(self, enemies):
        """Megkeresi a legközelebbi, még élő ellenséget a hatótávon belül."""
        closest_enemy = None
        min_dist = getattr(self, 'effective_range', self.range)
        
        for enemy in enemies:
            if not enemy.active:
                continue
            dist = self.get_distance(enemy)
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
                
        self.target = closest_enemy

    def update(self, enemies, projectiles):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

        # Hatótáv bónusz alkalmazása
        if self.game_state:
            _, _, rng_bonus = self.game_state.get_equipped_bonuses()
            self.effective_range = int(self.range * (1 + rng_bonus))
        else:
            self.effective_range = self.range

        self.find_target(enemies)

        if self.target and self.cooldown_timer <= 0:
            self.shoot(projectiles)

    def shoot(self, projectiles):
        self.sound_shoot.play()
        self.cooldown_timer = self.cooldown_max
        if self.game_state:
            dmg_bonus, _, _ = self.game_state.get_equipped_bonuses()
        else:
            dmg_bonus = 0.0
        actual_damage = int(self.damage * (1 + dmg_bonus))
        proj = Projectile(self.x, self.y, self.target, actual_damage, self.proj_speed, self.proj_color)
        projectiles.append(proj)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
        # Szint jelzése
        if self.level > 1:
            font = pygame.font.SysFont(None, 20)
            lvl_text = font.render(f"L{self.level}", True, WHITE)
            surface.blit(lvl_text, (self.rect.right - 15, self.rect.bottom - 15))

    def draw_range(self, surface):
        # Félig átlátszó kör a hatótávhoz
        r = getattr(self, 'effective_range', self.range)
        range_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(range_surf, (255, 255, 255, 60), (r, r), r)
        pygame.draw.circle(range_surf, WHITE, (r, r), r, 1)
        surface.blit(range_surf, (self.x - r, self.y - r))


class Enemy:
    """Az útvonalon haladó ellenség."""
    def __init__(self, enemy_type, path, game_state):
        self.type = enemy_type
        self.path = path
        self.path_index = 0
        self.game_state = game_state
        
        config = ENEMY_CONFIG[enemy_type]
        # Hp skálázódás hullámtól függően
        hp_multiplier = 1.0 + (game_state.wave_manager.current_wave_index * 0.2)
        self.max_hp = int(config["hp"] * hp_multiplier)
        self.hp = self.max_hp
        self.base_speed = config["speed"]
        _, slow_bonus, _ = game_state.get_equipped_bonuses()
        self.speed = self.base_speed * (1 - slow_bonus)
        self.reward = config["reward"]
        self.size = config["size"]
        
        self.image = load_image(config["image"], config["color"], (self.size, self.size), shape="circle")
        
        # Kezdőpozíció beállítása az első pontra
        self.x, self.y = self.path[0]
        self.active = True

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0 and self.active:
            self.active = False
            self.game_state.money += self.reward
            self.game_state.floating_texts.append(
                FloatingText(self.x, self.y - 20, f"+${self.reward}", GOLD, self.game_state.font_small)
            )
            self.game_state.sound_death.play()

    def update(self):
        if not self.active:
            return

        # Sebesség dinamikus frissítése (slow bónusz változhat)
        _, slow_bonus, _ = self.game_state.get_equipped_bonuses()
        self.speed = self.base_speed * max(0.1, 1 - slow_bonus)

        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)

            if dist < self.speed:
                # Elérte a pontot, lépés a következőre
                self.x = target_x
                self.y = target_y
                self.path_index += 1
            else:
                # Mozgás a célpont felé
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        else:
            # Végigért az úton
            self.active = False
            self.game_state.lives -= 1

    def draw(self, surface):
        rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.image, rect)
        
        # Életerő sáv rajzolása
        if self.hp < self.max_hp:
            bar_width = self.size
            bar_height = 4
            hp_ratio = max(0, self.hp / self.max_hp)
            
            bg_rect = pygame.Rect(self.x - bar_width//2, self.y - self.size//2 - 10, bar_width, bar_height)
            fg_rect = pygame.Rect(self.x - bar_width//2, self.y - self.size//2 - 10, int(bar_width * hp_ratio), bar_height)
            
            pygame.draw.rect(surface, RED, bg_rect)
            pygame.draw.rect(surface, GREEN, fg_rect)


class Map:
    """A pálya és az útvonal kezelése, Grid rendszer integrációja."""
    def __init__(self, level_num):
        self.level_num = level_num
        self.path = self._generate_path(level_num)
        
        # Kiszámoljuk, hogy a grid mely cellái vannak blokkolva az út által
        self.invalid_grid_cells = set()
        self._calculate_invalid_cells()
        
        # Háttérkép
        bg_name = f"background{level_num}.png"
        self.background = load_image(bg_name, (34, 139, 34), (SCREEN_WIDTH, SCREEN_HEIGHT))
        self._draw_path_on_bg()

    def _generate_path(self, level):
        """Pályák útvonalának definiálása."""
        if level == 1:
            return [(0, 160), (280, 160), (280, 600), (800, 600), (800, 320), (SCREEN_WIDTH, 320)]
        elif level == 2:
            return [(120, 0), (120, 440), (480, 440), (480, 160), (760, 160), (760, SCREEN_HEIGHT)]
        else: # Level 3
            return [(0, 400), (160, 400), (160, 120), (880, 120), (880, 640), (400, 640), (400, 400), (720, 400)]

    def _calculate_invalid_cells(self):
        """
        Végigmegy az útvonalon és kiszámítja, mely grid cellákba nem lehet építeni.
        Csak azokat a cellákat blokkoljuk, amelyeken az út ténylegesen átmegy.
        """
        path_half = 23  # Az út fél-szélessége pixelben (45px / 2, kicsit tágabb)

        for i in range(len(self.path) - 1):
            p1 = pygame.math.Vector2(self.path[i])
            p2 = pygame.math.Vector2(self.path[i+1])

            dist = p1.distance_to(p2)
            steps = max(1, int(dist / (GRID_SIZE // 2)))  # Fél-cella lépésközök elégségesek

            for step in range(steps + 1):
                t = step / steps if steps > 0 else 0
                cx = p1.lerp(p2, t).x
                cy = p1.lerp(p2, t).y

                # Az út által lefedett grid cellák meghatározása a fél-szélességgel
                min_gx = int((cx - path_half)) // GRID_SIZE
                max_gx = int((cx + path_half)) // GRID_SIZE
                min_gy = int((cy - path_half)) // GRID_SIZE
                max_gy = int((cy + path_half)) // GRID_SIZE

                for gx in range(min_gx, max_gx + 1):
                    for gy in range(min_gy, max_gy + 1):
                        self.invalid_grid_cells.add((gx, gy))

    def _draw_path_on_bg(self):
        """Beégeti az útvonalat a háttérképbe vizuálisan."""
        path_color = (194, 178, 128) # Homok szín
        for i in range(len(self.path) - 1):
            pygame.draw.line(self.background, path_color, self.path[i], self.path[i+1], 45)
            pygame.draw.circle(self.background, path_color, self.path[i], 22)
        if self.path:
            pygame.draw.circle(self.background, path_color, self.path[-1], 22)

    def draw(self, surface):
        surface.blit(self.background, (0, 0))


class WaveManager:
    """A hullámok és az ellenségek spawnolásának kezelője."""
    def __init__(self, level_num, game_state):
        self.game_state = game_state
        self.waves = self._generate_waves(level_num)
        self.current_wave_index = 0
        self.current_wave_data = []
        self.spawn_timer = 0
        self.wave_active = False
        self.wave_finished = False

    def _generate_waves(self, level):
        """Különböző szintek hullámainak generálása. (ellenség_típus, késleltetés_framekben)"""
        waves = []
        if level == 1:
            waves.append([("goblin", 60)] * 10)
            waves.append([("goblin", 45)] * 15 + [("orc", 120)] * 2)
            waves.append([("orc", 90)] * 10 + [("goblin", 30)] * 20)
            waves.append([("goblin", 30)] * 15 + [("troll", 150)] * 3)
        elif level == 2:
            waves.append([("goblin", 50)] * 15)
            waves.append([("orc", 80)] * 12)
            waves.append([("goblin", 20)] * 30)
            waves.append([("troll", 120)] * 5 + [("orc", 60)] * 10)
            waves.append([("goblin", 15)] * 40 + [("troll", 90)] * 8)
        else:
            waves.append([("orc", 60)] * 15)
            waves.append([("goblin", 15)] * 30 + [("orc", 50)] * 10)
            waves.append([("troll", 100)] * 10)
            waves.append([("goblin", 10)] * 50 + [("troll", 60)] * 5)
            waves.append([("troll", 80)] * 15 + [("orc", 40)] * 20)
        return waves

    def start_next_wave(self):
        if self.current_wave_index < len(self.waves):
            self.current_wave_data = self.waves[self.current_wave_index].copy()
            self.wave_active = True
            self.spawn_timer = 0
        else:
            self.wave_finished = True

    def update(self):
        if not self.wave_active:
            return

        # Ha elfogyott a spórolni való, de még vannak ellenségek, vár
        if len(self.current_wave_data) == 0:
            if len(self.game_state.enemies) == 0:
                # Hullám vége
                self.wave_active = False
                self.current_wave_index += 1
                self.game_state.money += 50 + (self.current_wave_index * 20) # Bónusz pénz hullám végén
                if self.current_wave_index >= len(self.waves):
                    self.wave_finished = True
            return

        # Ellenség spawnolása időzítve
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            enemy_type, delay = self.current_wave_data.pop(0)
            new_enemy = Enemy(enemy_type, self.game_state.current_map.path, self.game_state)
            self.game_state.enemies.append(new_enemy)
            self.spawn_timer = delay

class EndlessWaveManager:
    def __init__(self, game_state):
        self.game_state = game_state

        self.current_wave_index = 0
        self.current_wave_data = []

        self.spawn_timer = 0
        self.wave_active = False
        self.wave_finished = False

    def generate_wave(self):
        wave = []

        wave_number = self.current_wave_index + 1

        goblins = 10 + wave_number * 2
        orcs = max(0, wave_number // 2)
        trolls = max(0, wave_number // 5)

        for i in range(goblins):
            wave.append(("goblin", max(10, 60 - wave_number)))

        for i in range(orcs):
            wave.append(("orc", max(20, 100 - wave_number)))

        for i in range(trolls):
            wave.append(("troll", 120))

        return wave

    def start_next_wave(self):
        self.current_wave_data = self.generate_wave()
        self.wave_active = True
        self.spawn_timer = 0

    def update(self):
        if not self.wave_active:
            return

        if len(self.current_wave_data) == 0:
            if len(self.game_state.enemies) == 0:
                self.wave_active = False
                self.current_wave_index += 1

                reward = 100 + self.current_wave_index * 25
                self.game_state.money += reward
                # Random crate drop
                if random.random() < 0.4:
                    self.game_state.crates += 1

                    self.game_state.floating_texts.append(
                        FloatingText(
                            SCREEN_WIDTH // 2 - 120,120,"LÁDA DROP!",GOLD,
                                self.game_state.font_large,
                                duration=120
                        )
                    )
            return

        self.spawn_timer -= 1

        if self.spawn_timer <= 0:
            enemy_type, delay = self.current_wave_data.pop(0)

            new_enemy = Enemy(
                enemy_type,
                self.game_state.current_map.path,
                self.game_state
            )

            self.game_state.enemies.append(new_enemy)

            self.spawn_timer = delay


# ==========================================
# OSZTÁLYOK: FŐ JÁTÉK
# ==========================================
class Game:
    """A fő játékmotor és állapotgép."""
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Fullscreen / windowed állapot
        self.fullscreen = False
        self.render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Python Tower Defense - Grid Edition")
        self.clock = pygame.time.Clock()
        
        # Betűtípusok
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 30, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.font_hud = pygame.font.SysFont("Consolas", 24, bold=True)
        
        # Hangok betöltése
        self.sound_shoot = load_sound("shoot.wav")
        self.sound_death = load_sound("death.wav")
        load_music("bgm.mp3")
        
        # Játékállapotok
        self.STATE_MENU = 0
        self.STATE_PLAYING = 1
        self.STATE_GAMEOVER = 2
        self.STATE_VICTORY = 3
        self.state = self.STATE_MENU
        #endless/1
        self.endless_mode = False
        #inv rendszer
        self.INV_VISIBLE_ROWS = 20  # Látható sorok száma az inventory listában
        self.keys = 0
        self.crates = 0
        self.inventory = []
        self.gold = 0
        self.equipped_items = [None, None, None, None]  # 4 equip slot
        self.inventory_max_size = INVENTORY_BASE_SIZE
        self.crate_animation = None   # CS:GO animáció objektum (None = nincs aktív)
        self.inv_scroll_offset = 0    # Inventory lista görgetési eltolás

        # Aktív menü panel (None = főlap, "levels" / "inventory" / "quit")
        self.menu_panel = None

        # 3 nagy főgomb
        big_btn_w, big_btn_h = 260, 80
        cx = SCREEN_WIDTH // 2 - big_btn_w // 2
        self.main_menu_buttons = [
            Button(cx, 220, big_btn_w, big_btn_h, ">> Folytatás", self.font_medium, (0,140,0), WHITE, self.load_game),
            Button(cx, 320, big_btn_w, big_btn_h, "Szintek", self.font_medium, DARK_GRAY, WHITE, lambda: self._open_panel("levels")),
            Button(cx, 420, big_btn_w, big_btn_h, "Inventory", self.font_medium, DARK_GRAY, WHITE, lambda: self._open_panel("inventory")),
            Button(cx, 520, big_btn_w, big_btn_h, "Kilépés", self.font_medium, RED, WHITE, lambda: self._open_panel("quit")),
        ]

        # Szintek alpanel gombjai
        sub_btn_w, sub_btn_h = 220, 58
        scx = SCREEN_WIDTH // 2 - sub_btn_w // 2
        self.level_buttons = [
            Button(scx, 270, sub_btn_w, sub_btn_h, "Pálya 1", self.font_medium, GRAY, WHITE, lambda: self.start_game(1)),
            Button(scx, 348, sub_btn_w, sub_btn_h, "Pálya 2", self.font_medium, GRAY, WHITE, lambda: self.start_game(2)),
            Button(scx, 426, sub_btn_w, sub_btn_h, "Pálya 3", self.font_medium, GRAY, WHITE, lambda: self.start_game(3)),
            Button(scx, 510, sub_btn_w, sub_btn_h, "Endless Mode", self.font_medium, GOLD, BLACK, lambda: self.start_endless_game()),
            Button(scx, 600, sub_btn_w, 45, "← Vissza", self.font_small, DARK_GRAY, WHITE, lambda: self._open_panel(None)),
        ]

        # Kilépés alpanel gombjai
        self.quit_panel_buttons = [
            Button(scx, 380, sub_btn_w, sub_btn_h, "Igen, kilépés", self.font_medium, RED, WHITE, self.quit_game),
            Button(scx, 460, sub_btn_w, 45, "← Vissza", self.font_small, DARK_GRAY, WHITE, lambda: self._open_panel(None)),
        ]

        # Inventory alpanel gombjai
        self.inventory_back_button = Button(60, 700, 180, 40, "← Vissza", self.font_small, DARK_GRAY, WHITE, lambda: self._open_panel(None))
        self.inv_open_crate_btn  = Button(60,  408, 175, 38, "Lada nyitas",  self.font_small, (255,140,0), BLACK, self.open_crate)
        self.inv_buy_key_btn     = Button(243, 408, 160, 38, f"Kulcs (${KEY_COST})", self.font_small, GOLD, BLACK, self.buy_key)
        self.inv_buy_crate_btn   = Button(411, 408, 170, 38, f"Lada (${CRATE_COST})", self.font_small, (80,160,220), BLACK, self.buy_crate)
        self.inv_expand_btn      = Button(60,  452, 360, 34, f"Bővítés (+{INVENTORY_EXPAND_AMOUNT} hely) — ${INVENTORY_EXPAND_COST}", self.font_small, DARK_GRAY, GOLD, self.expand_inventory)
        self.inv_scroll_up_btn   = Button(952,  82,  40, 24, "▲", self.font_small, DARK_GRAY, WHITE, self._inv_scroll_up)
        self.inv_scroll_down_btn = Button(952, 108,  40, 24, "▼", self.font_small, DARK_GRAY, WHITE, self._inv_scroll_down)

        # Összesített lista az event handling-hoz
        self.menu_buttons = self.main_menu_buttons
        
        self.gameover_buttons = [
            Button(SCREEN_WIDTH//2 - big_btn_w//2, 400, big_btn_w, big_btn_h, "Főmenü", self.font_medium, GRAY, WHITE, self.go_to_menu)
        ]
        
        self.reset_game_data()

    def _open_panel(self, panel_name):
        self.menu_panel = panel_name
        if panel_name == "inventory":
            self.inv_scroll_offset = 0  # Reset scroll when opening

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

    def get_mouse_pos(self):
        """Egér pozíció korrigálva a fullscreen skálázáshoz."""
        mx, my = pygame.mouse.get_pos()
        ox, oy = getattr(self, '_mouse_offset', (0, 0))
        scale = getattr(self, '_mouse_scale', 1.0)
        if scale > 0:
            return (int((mx - ox) / scale), int((my - oy) / scale))
        return (mx, my)

    def _inv_scroll_up(self):
        self.inv_scroll_offset = max(0, self.inv_scroll_offset - 1)

    def _inv_scroll_down(self):
        max_offset = max(0, len(self.inventory) - self.INV_VISIBLE_ROWS)
        self.inv_scroll_offset = min(max_offset, self.inv_scroll_offset + 1)

    def get_equipped_bonuses(self):
        """Visszaadja az összes equipped item összesített bónuszát."""
        dmg = 0.0
        slow = 0.0
        rng = 0.0
        for item_name in self.equipped_items:
            if item_name and item_name in ITEMS:
                rarity, d, s, r, _ = ITEMS[item_name]
                dmg += d
                slow += s
                rng += r
        return dmg, slow, rng

    def equip_item(self, item_name):
        """Betesz egy itemet az első üres slotba, ha van."""
        if item_name in self.equipped_items:
            return  # már be van rakva
        for i in range(4):
            if self.equipped_items[i] is None:
                self.equipped_items[i] = item_name
                return

    def unequip_item(self, slot_index):
        """Kivesz egy itemet a slotból."""
        self.equipped_items[slot_index] = None

    def sell_item(self, item_name, inv_index=None):
        """Elad egy itemet goldért. Ha equipelve van, először kiveszi."""
        if item_name not in self.inventory:
            return
        rarity = ITEMS[item_name][0]
        price = RARITY_SELL_PRICE[rarity]
        # Ha equipelve van, kivesszük az első matching slotból
        for i in range(4):
            if self.equipped_items[i] == item_name:
                self.equipped_items[i] = None
                break  # Csak egyszer vesszük ki (duplikált itemek esetén)
        if inv_index is not None and 0 <= inv_index < len(self.inventory):
            del self.inventory[inv_index]
        else:
            self.inventory.remove(item_name)
        # Eladásért pénzt kap a játékos (gold = cosmetic, money = játékpénz)
        self.money += price
        self.floating_texts.append(
            FloatingText(SCREEN_WIDTH//2 - 80, 200, f"+${price}", GOLD, self.font_medium, duration=120))

    def expand_inventory(self):
        """Kibővíti az inventory méretet +5 slottal, ha van elég pénz."""
        if self.money >= INVENTORY_EXPAND_COST:
            self.money -= INVENTORY_EXPAND_COST
            self.inventory_max_size += INVENTORY_EXPAND_AMOUNT
            self.floating_texts.append(
                FloatingText(SCREEN_WIDTH//2 - 100, 200, f"+{INVENTORY_EXPAND_AMOUNT} inventory hely!", WHITE, self.font_medium, duration=120))

    def buy_key(self):
        """Kulcs vásárlása pénzből (nem goldból)."""
        if self.money >= KEY_COST:
            self.money -= KEY_COST
            self.keys += 1
            self.floating_texts.append(
                FloatingText(SCREEN_WIDTH//2, 150, "+1 KULCS  -$" + str(KEY_COST), GOLD, self.font_medium))
    def buy_crate(self):
        """Láda vásárlása pénzből."""
        if self.money >= CRATE_COST:
            self.money -= CRATE_COST
            self.crates += 1
            self.floating_texts.append(
                FloatingText(SCREEN_WIDTH//2, 150, f"+1 LÁDA  -${CRATE_COST}", GOLD, self.font_medium))

    def open_crate(self):
        # Ha már fut animáció, ne indíts újat
        if self.crate_animation is not None:
            return

        if self.crates <= 0 or self.keys <= 0:
            return

        if len(self.inventory) >= self.inventory_max_size:
            self.floating_texts.append(
                FloatingText(SCREEN_WIDTH//2 - 120, 120, "Inventory tele! Adj el valamit.", RED, self.font_medium, duration=180)
            )
            return

        self.crates -= 1
        self.keys -= 1

        roll = random.random()
        if roll < 0.60:
            rarity = "common"
        elif roll < 0.85:
            rarity = "rare"
        elif roll < 0.97:
            rarity = "epic"
        else:
            rarity = "legendary"

        item_name = random.choice(LOOT_POOLS[rarity])

        # Elindítjuk a CS:GO animációt
        self.crate_animation = CrateOpenAnimation(
            item_name, rarity,
            self.font_small, self.font_medium, self.font_large,
            SCREEN_WIDTH, SCREEN_HEIGHT
        )

        # Az itemet már most hozzáadjuk az inventoryhoz (az animáció csak vizuális)
        self.inventory.append(item_name)

    # ─────────────────────────────────────────────────────
    # MENTÉS / BETÖLTÉS
    # ─────────────────────────────────────────────────────
    def save_game(self):
        """Elmenti a játék állapotát JSON fájlba."""
        if self.state != self.STATE_PLAYING:
            return
        towers_data = []
        for t in self.towers:
            towers_data.append({
                "type": t.type,
                "grid_x": t.grid_x,
                "grid_y": t.grid_y,
                "level": t.level,
                "damage": t.damage,
                "range": t.range,
            })
        data = {
            "level_num":          self.current_map.level_num,
            "money":              self.money,
            "lives":              self.lives,
            "gold":               self.gold,
            "crates":             self.crates,
            "keys":               self.keys,
            "inventory":          self.inventory,
            "equipped_items":     self.equipped_items,
            "inventory_max_size": self.inventory_max_size,
            "wave_index":         self.wave_manager.current_wave_index,
            "endless_mode":       self.endless_mode,
            "towers":             towers_data,
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.floating_texts.append(
                FloatingText(SCREEN_WIDTH//2 - 80, 60, "Játék mentve!", WHITE, self.font_medium, duration=120))
        except Exception as e:
            print(f"Mentési hiba: {e}")

    def load_game(self):
        """Betölti az elmentett játékot. Visszaad True-t ha sikerült."""
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False

        self.reset_game_data()
        level_num = data.get("level_num", 1)
        self.current_map   = Map(level_num)
        self.endless_mode  = data.get("endless_mode", False)
        if self.endless_mode:
            self.wave_manager = EndlessWaveManager(self)
        else:
            self.wave_manager  = WaveManager(level_num, self)
        self.money         = data.get("money", STARTING_MONEY)
        self.lives         = data.get("lives", STARTING_LIVES)
        self.gold          = data.get("gold", 0)
        self.crates        = data.get("crates", 0)
        self.keys          = data.get("keys", 0)
        self.inventory     = data.get("inventory", [])
        self.equipped_items= data.get("equipped_items", [None, None, None, None])
        self.inventory_max_size = data.get("inventory_max_size", INVENTORY_BASE_SIZE)

        wi = data.get("wave_index", 0)
        self.wave_manager.current_wave_index = wi

        # Tornyok visszaállítása
        for td in data.get("towers", []):
            t = Tower(td["grid_x"], td["grid_y"], td["type"], self.sound_shoot, self)
            t.level  = td.get("level", 1)
            t.damage = td.get("damage", t.damage)
            t.range  = td.get("range", t.range)
            self.towers.append(t)

        self.state = self.STATE_PLAYING
        self.floating_texts.append(
            FloatingText(SCREEN_WIDTH//2 - 80, 60, "Játék betöltve!", GREEN, self.font_medium, duration=120))
        return True

    def has_save(self):
        """Visszaadja, hogy van-e mentett játék."""
        return os.path.exists(SAVE_FILE)

    def reset_game_data(self):
        """Visszaállítja a játékváltozókat új játék kezdésekor."""
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.current_map = None
        self.wave_manager = None
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.floating_texts = []

        # Endless mód alapértelmezett visszaállítása
        self.endless_mode = False

        # UI / Építés állapotok
        self.selected_tower_type = None
        self.selected_tower_obj = None # Már lerakott, kiválasztott torony
        self.is_building = False
        
        # HUD Layout (Tiszta, nem egymásra lógó gombok)
        hud_y = SCREEN_HEIGHT - HUD_HEIGHT + 20
        btn_w, btn_h = 160, 60
        spacing = 20
        
        self.next_wave_btn = Button(SCREEN_WIDTH - btn_w - spacing, hud_y, btn_w, btn_h, "Köv. Hullám", self.font_medium, GREEN, BLACK, self.trigger_next_wave)
        save_btn_w = 70
        self.hud_buttons = [           
            Button(spacing, hud_y, btn_w, btn_h, f"Íjász (${TOWER_CONFIG['archer']['cost']})", self.font_small, BLUE, WHITE, lambda: self.select_tower_to_build("archer")),
            Button(spacing*2 + btn_w, hud_y, btn_w, btn_h, f"Ágyú (${TOWER_CONFIG['cannon']['cost']})", self.font_small, DARK_GRAY, WHITE, lambda: self.select_tower_to_build("cannon")),
            Button(spacing*3 + btn_w*2, hud_y, btn_w, btn_h, f"Varázsló (${TOWER_CONFIG['mage']['cost']})", self.font_small, (128, 0, 128), WHITE, lambda: self.select_tower_to_build("mage")),
            Button(spacing*4 + btn_w*3, hud_y, save_btn_w, btn_h, "Ment", self.font_small, (0,80,80), WHITE, self.save_game),
            self.next_wave_btn,
            ]

            
        
        self.upgrade_button = Button(0, 0, 130, 45, "Fejlesztés", self.font_small, GOLD, BLACK, self.upgrade_selected_tower)

    def start_game(self, level_num):
        self.reset_game_data()
        self.current_map = Map(level_num)
        self.wave_manager = WaveManager(level_num, self)
        self.state = self.STATE_PLAYING

    #endless
    def start_endless_game(self):
        self.reset_game_data()
        self.endless_mode = True
        self.current_map = Map(1)
        self.wave_manager = EndlessWaveManager(self)
        self.state = self.STATE_PLAYING

    def go_to_menu(self):
        # Auto-mentés ha játékból lépünk ki
        if self.state == self.STATE_PLAYING:
            self.save_game()
        self.endless_mode = False
        self.state = self.STATE_MENU

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def select_tower_to_build(self, tower_type):
        self.selected_tower_type = tower_type
        self.is_building = True
        self.selected_tower_obj = None

    def trigger_next_wave(self):
        if not self.wave_manager.wave_active:
            self.wave_manager.start_next_wave()

    def upgrade_selected_tower(self):
        if self.selected_tower_obj:
            success = self.selected_tower_obj.upgrade(self)
            if success:
                self.floating_texts.append(
                    FloatingText(self.selected_tower_obj.x, self.selected_tower_obj.y - 30, "Fejlesztve!", GREEN, self.font_small)
                )

    def get_grid_coordinates(self, pos):
        """Kiszámolja a kurzor alatti rács (grid) bal felső sarkát."""
        grid_x = (pos[0] // GRID_SIZE) * GRID_SIZE
        grid_y = (pos[1] // GRID_SIZE) * GRID_SIZE
        return grid_x, grid_y

    def is_valid_tower_position(self, grid_x, grid_y):
        """Ellenőrzi, hogy az adott rácsra lehet-e tornyot építeni."""
        # 1. UI sáv ellenőrzése
        if grid_y >= SCREEN_HEIGHT - HUD_HEIGHT:
            return False
            
        # 2. Útvonal ellenőrzése
        grid_cell_idx = (grid_x // GRID_SIZE, grid_y // GRID_SIZE)
        if grid_cell_idx in self.current_map.invalid_grid_cells:
            return False
            
        # 3. Másik torony ellenőrzése
        for t in self.towers:
            if t.grid_x == grid_x and t.grid_y == grid_y:
                return False
                
        return True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            # F11: fullscreen váltás (mindenhol működik)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                self.toggle_fullscreen()
                continue

            # Egér koordináták korrigálása skálázáshoz
            if hasattr(event, 'pos'):
                ox, oy = getattr(self, '_mouse_offset', (0, 0))
                scale = getattr(self, '_mouse_scale', 1.0)
                if scale > 0:
                    cx = int((event.pos[0] - ox) / scale)
                    cy = int((event.pos[1] - oy) / scale)
                    event = pygame.event.Event(event.type,
                        {**event.__dict__, 'pos': (cx, cy)})

            if self.state == self.STATE_MENU:
                # Ha fut a láda animáció, ignoráljuk a többi inputot
                if self.crate_animation is not None:
                    continue
                if self.menu_panel is None:
                    for btn in self.main_menu_buttons:
                        btn.handle_event(event)
                elif self.menu_panel == "levels":
                    for btn in self.level_buttons:
                        btn.handle_event(event)
                elif self.menu_panel == "inventory":
                    self.inventory_back_button.handle_event(event)
                    self.inv_open_crate_btn.handle_event(event)
                    self.inv_buy_key_btn.handle_event(event)
                    self.inv_buy_crate_btn.handle_event(event)
                    self.inv_expand_btn.handle_event(event)
                    self.inv_scroll_up_btn.handle_event(event)
                    self.inv_scroll_down_btn.handle_event(event)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        # Egérkerék görgetés
                        if event.button == 4:
                            self._inv_scroll_up()
                        elif event.button == 5:
                            self._inv_scroll_down()
                        elif event.button == 1:
                            # Equip slot kattintás (unequip)
                            for i in range(4):
                                slot_rect = pygame.Rect(60, 130 + i * 58, 380, 50)
                                if slot_rect.collidepoint(mx, my):
                                    self.unequip_item(i)
                            # Item lista bal klikk = equip
                            for idx in range(min(self.INV_VISIBLE_ROWS, len(self.inventory) - self.inv_scroll_offset)):
                                real_idx = idx + self.inv_scroll_offset
                                item_rect = pygame.Rect(500, 130 + idx * 26, 430, 24)
                                if item_rect.collidepoint(mx, my):
                                    self.equip_item(self.inventory[real_idx])
                        elif event.button == 3:
                            # Item lista jobb klikk = eladás
                            for idx in range(min(self.INV_VISIBLE_ROWS, len(self.inventory) - self.inv_scroll_offset)):
                                real_idx = idx + self.inv_scroll_offset
                                item_rect = pygame.Rect(500, 130 + idx * 26, 430, 24)
                                if item_rect.collidepoint(mx, my):
                                    self.sell_item(self.inventory[real_idx], inv_index=real_idx)
                elif self.menu_panel == "quit":
                    for btn in self.quit_panel_buttons:
                        btn.handle_event(event)
                    
            elif self.state in [self.STATE_GAMEOVER, self.STATE_VICTORY]:
                for btn in self.gameover_buttons:
                    btn.handle_event(event)

            elif self.state == self.STATE_PLAYING:
                for btn in self.hud_buttons:
                    btn.handle_event(event)
                    
                if self.selected_tower_obj:
                    self.upgrade_button.handle_event(event)

                # ESC: építés visszavonása / kijelölés törlése
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.is_building = False
                    self.selected_tower_type = None
                    self.selected_tower_obj = None

                # DELETE: kiválasztott torony eladása (fél áron)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE:
                    if self.selected_tower_obj:
                        sell_val = TOWER_CONFIG[self.selected_tower_obj.type]["cost"] // 2
                        self.money += sell_val
                        self.towers.remove(self.selected_tower_obj)
                        self.floating_texts.append(
                            FloatingText(self.selected_tower_obj.x, self.selected_tower_obj.y - 30,
                                         f"+${sell_val}", GOLD, self.font_small)
                        )
                        self.selected_tower_obj = None

                # SPACE: következő hullám
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.trigger_next_wave()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = self.get_mouse_pos()
                    
                    # Ha a HUD-ra kattint, ne vonja vissza a kijelölést azonnal, kezelje a gombokat
                    if pos[1] > SCREEN_HEIGHT - HUD_HEIGHT:
                        continue
                        
                    # Ha már van lerakott torony kiválasztva és a gombra kattint
                    if self.selected_tower_obj and self.upgrade_button.hovered:
                        continue

                    if self.is_building and self.selected_tower_type:
                        grid_x, grid_y = self.get_grid_coordinates(pos)
                        cost = TOWER_CONFIG[self.selected_tower_type]["cost"]
                        
                        if self.money >= cost and self.is_valid_tower_position(grid_x, grid_y):
                            self.money -= cost
                            new_tower = Tower(grid_x, grid_y, self.selected_tower_type, self.sound_shoot, self)
                            self.towers.append(new_tower)
                            # Benne maradhat építési módban (hogy többet lerakhasson egymás után),
                            # de vonjuk le a pénzt.
                            if self.money < cost:
                                self.is_building = False
                                self.selected_tower_type = None
                    else:
                        # Torony kiválasztása kattintással (Grid alapján)
                        clicked_tower = None
                        grid_x, grid_y = self.get_grid_coordinates(pos)
                        for t in self.towers:
                            if t.grid_x == grid_x and t.grid_y == grid_y:
                                clicked_tower = t
                                break
                        self.selected_tower_obj = clicked_tower

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    # Jobb klikk: építés és kijelölés visszavonása
                    self.is_building = False
                    self.selected_tower_type = None
                    self.selected_tower_obj = None

    def update(self):
        # Láda animáció frissítése (menüben is fut)
        if self.crate_animation is not None:
            self.crate_animation.update()
            if self.crate_animation.done:
                self.crate_animation = None
            return  # Animáció közben a játék logika szünetel

        if self.state != self.STATE_PLAYING:
            # Menüben is frissítjük a lebegő szövegeket (pl. eladás visszajelzés)
            for text in self.floating_texts:
                text.update()
            self.floating_texts = [t for t in self.floating_texts if t.timer > 0]
            return

        # Játék vége ellenőrzés
        if self.lives <= 0:
            self.state = self.STATE_GAMEOVER
            return

        # Győzelem ellenőrzés
        if not self.endless_mode:
            if self.wave_manager.wave_finished and len(self.enemies) == 0:
                self.state = self.STATE_VICTORY
                return

        self.wave_manager.update()

        # Tornyok frissítése
        for tower in self.towers:
            tower.update(self.enemies, self.projectiles)

        # Ellenségek frissítése
        for enemy in self.enemies:
            enemy.update()
        self.enemies = [e for e in self.enemies if e.active]

        # Lövedékek frissítése
        for proj in self.projectiles:
            proj.update()
        self.projectiles = [p for p in self.projectiles if p.active]

        # Szövegek frissítése
        for text in self.floating_texts:
            text.update()
        self.floating_texts = [t for t in self.floating_texts if t.timer > 0]

    def draw_hud(self):
        """Kirajzolja a kezelőfelületet a játékban tisztán, átfedések nélkül."""
        # HUD panel: gradiens felső él + háttér
        hud_top = SCREEN_HEIGHT - HUD_HEIGHT
        hud_rect = pygame.Rect(0, hud_top, SCREEN_WIDTH, HUD_HEIGHT)
        pygame.draw.rect(self.render_surface, (22, 22, 28), hud_rect)
        # Gradiens felső csík (szürke→sötét)
        for i in range(6):
            alpha = 255 - i * 40
            c = max(0, 80 - i * 12)
            pygame.draw.line(self.render_surface, (c, c, c+10), (0, hud_top + i), (SCREEN_WIDTH, hud_top + i))
        # Arany felső vonal
        pygame.draw.line(self.render_surface, GOLD, (0, hud_top), (SCREEN_WIDTH, hud_top), 2)

        # Aktív torony kiépítési típus highlight
        type_map = {"archer": 0, "cannon": 1, "mage": 2}
        if self.is_building and self.selected_tower_type in type_map:
            idx = type_map[self.selected_tower_type]
            btn = self.hud_buttons[idx]
            hl = pygame.Surface((btn.rect.width+4, btn.rect.height+4), pygame.SRCALPHA)
            hl.fill((255,255,0,60))
            self.render_surface.blit(hl, (btn.rect.x-2, btn.rect.y-2))
            pygame.draw.rect(self.render_surface, GOLD, btn.rect.inflate(4,4), 2, border_radius=6)

        # Gombok rajzolása
        # Köv. Hullám gomb állapota: inaktív ha hullám fut
        if self.wave_manager.wave_active:
            self.next_wave_btn.bg_color = DARK_GRAY
            self.next_wave_btn.text = "Hullám fut..."
        else:
            self.next_wave_btn.bg_color = GREEN
            wave_idx = self.wave_manager.current_wave_index
            if self.endless_mode:
                self.next_wave_btn.text = f"Hullám {wave_idx + 1} >>"
            else:
                total = len(self.wave_manager.waves)
                self.next_wave_btn.text = f"Hullám {wave_idx+1}/{total} >>"
        for btn in self.hud_buttons:
            btn.draw(self.render_surface)

        if self.endless_mode:
            wave_str = f"{self.wave_manager.current_wave_index + 1}. hullám (∞)"
        else:
            total = len(self.wave_manager.waves)
            current = min(self.wave_manager.current_wave_index + 1, total)
            wave_str = f"{current}/{total}"

        # HUD stats — szabad terület kb. 638–840px (3 szekció: PÉNZ, ÉLET, HULLÁM)
        # Arány/kulcs/láda info a Menü/Inventory-ban látható, HUD-ban nincs helye.
        stats_y  = SCREEN_HEIGHT - HUD_HEIGHT + 8
        lbl_font = pygame.font.SysFont("Consolas", 13)
        val_font = self.font_hud   # Consolas 24 bold

        # Szekciók: x értékek a 638–840px sávban egyenletesen
        secs = [
            ("PÉNZ",   f"${self.money}",   GOLD,  643),
            ("ÉLET",   f"{self.lives} elet",  RED,   730),
            ("HULLÁM", wave_str,            WHITE, 800),
        ]
        # Elválasztók
        for sep_x in [725, 793]:
            pygame.draw.line(self.render_surface, DARK_GRAY,
                (sep_x, SCREEN_HEIGHT - HUD_HEIGHT + 6),
                (sep_x, SCREEN_HEIGHT - 6), 1)

        for lbl, val, col, sx in secs:
            self.render_surface.blit(lbl_font.render(lbl, True, GRAY), (sx, stats_y))
            self.render_surface.blit(val_font.render(val, True, col), (sx, stats_y + 16))

        # Építés előnézet (Grid snap)
        if self.is_building and self.selected_tower_type:
            pos = self.get_mouse_pos()
            if pos[1] < SCREEN_HEIGHT - HUD_HEIGHT:
                grid_x, grid_y = self.get_grid_coordinates(pos)
                center_x = grid_x + GRID_SIZE // 2
                center_y = grid_y + GRID_SIZE // 2
                
                config = TOWER_CONFIG[self.selected_tower_type]
                
                # Hatótáv kör
                pygame.draw.circle(self.render_surface, (255, 255, 255, 100), (center_x, center_y), config["range"], 1)
                
                # Érvényes-e a hely (Piros / Zöld rács elem)
                valid = self.is_valid_tower_position(grid_x, grid_y)
                color = (0, 255, 0, 100) if valid else (255, 0, 0, 100)
                surf = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                surf.fill(color)
                self.render_surface.blit(surf, (grid_x, grid_y))

        # Aktív item bónuszok kompakt kijelzése (jobb felső, HUD felett)
        dmg_b, slow_b, rng_b = self.get_equipped_bonuses()
        if dmg_b > 0 or slow_b > 0 or rng_b > 0:
            bonus_font = pygame.font.SysFont("Consolas", 14)
            bx, by = 10, 10
            _bg = pygame.Surface((186, 62), pygame.SRCALPHA)
            _bg.fill((0, 0, 0, 170))
            self.render_surface.blit(_bg, (bx - 4, by - 4))
            self.render_surface.blit(bonus_font.render(f"+{int(dmg_b*100)}% dmg", True, GREEN), (bx, by))
            self.render_surface.blit(bonus_font.render(f"+{int(slow_b*100)}% slow", True, LIGHT_BLUE), (bx, by + 20))
            self.render_surface.blit(bonus_font.render(f"+{int(rng_b*100)}% range", True, YELLOW), (bx, by + 40))

    def draw(self):
        self.render_surface.fill(BLACK)

        if self.state == self.STATE_MENU:

            if self.menu_panel is None:
                # ── Főmenü háttér gradiens ─────────────────────
                for gy in range(SCREEN_HEIGHT):
                    t = gy / SCREEN_HEIGHT
                    r = int(10 + 20 * t)
                    g = int(15 + 30 * t)
                    b = int(30 + 40 * t)
                    pygame.draw.line(self.render_surface, (r, g, b), (0, gy), (SCREEN_WIDTH, gy))

                # Cím díszítő keret
                title_txt = "TOWER DEFENSE"
                title_s = self.font_large.render(title_txt, True, GOLD)
                tx = SCREEN_WIDTH//2 - title_s.get_width()//2
                ty = 110
                # Fényes shadow
                shadow = self.font_large.render(title_txt, True, (80, 60, 0))
                self.render_surface.blit(shadow, (tx+3, ty+3))
                self.render_surface.blit(title_s, (tx, ty))
                # Dekor vonalak
                pygame.draw.line(self.render_surface, GOLD, (tx-20, ty+title_s.get_height()+4),
                    (tx+title_s.get_width()+20, ty+title_s.get_height()+4), 2)
                pygame.draw.line(self.render_surface, GOLD, (tx-20, ty-4),
                    (tx+title_s.get_width()+20, ty-4), 1)

                # Folytatás gomb csak ha van mentés
                for i, btn in enumerate(self.main_menu_buttons):
                    if i == 0:  # Folytatás
                        if self.has_save():
                            btn.bg_color = (0, 140, 0)
                            btn.text_color = WHITE
                        else:
                            btn.bg_color = (50, 50, 50)
                            btn.text_color = GRAY
                    btn.draw(self.render_surface)

                # Verzió + F11 tipp
                ver = pygame.font.SysFont("Consolas", 14).render("F11 = Fullscreen  |  SPACE = Hullám  |  DEL = Torony eladás", True, DARK_GRAY)
                self.render_surface.blit(ver, (SCREEN_WIDTH//2 - ver.get_width()//2, SCREEN_HEIGHT - 30))

            elif self.menu_panel == "levels":
                # ── Szintek panel ────────────────────────────
                title = self.font_large.render("TOWER DEFENSE", True, WHITE)
                self.render_surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 70))
                sub_title = self.font_medium.render("Válassz pályát", True, GOLD)
                self.render_surface.blit(sub_title, (SCREEN_WIDTH//2 - sub_title.get_width()//2, 140))
                for btn in self.level_buttons:
                    btn.draw(self.render_surface)

            elif self.menu_panel == "inventory":
                # ════ INVENTORY PANEL ══════════════════════════

                # Cím (nincs "TOWER DEFENSE" felirat itt)
                inv_title = self.font_large.render("INVENTORY", True, GOLD)
                self.render_surface.blit(inv_title, (SCREEN_WIDTH//2 - inv_title.get_width()//2, 14))
                pygame.draw.line(self.render_surface, DARK_GRAY, (20, 76), (SCREEN_WIDTH-20, 76), 1)

                # ── BAL OSZLOP (x=60..440): Equip slotok + bónuszok + láda ──
                slot_x = 60
                slot_w, slot_h = 380, 46

                self.render_surface.blit(
                    self.font_small.render("Equipped itemek  (katt = kivesz)", True, GRAY),
                    (slot_x, 82))

                # 4 equip slot: y=104, 158, 212, 266  (spacing=54, height=46)
                for i in range(4):
                    sy = 104 + i * 54
                    item_name = self.equipped_items[i]
                    slot_rect = pygame.Rect(slot_x, sy, slot_w, slot_h)
                    pygame.draw.rect(self.render_surface, GOLD if item_name else DARK_GRAY, slot_rect, 2, border_radius=5)
                    if item_name:
                        rarity = ITEMS[item_name][0]
                        ic = RARITY_COLORS[rarity]
                        desc = ITEMS[item_name][4]
                        eq_icon = pygame.Surface((34, 34), pygame.SRCALPHA)
                        draw_item_icon(eq_icon, item_name, 0, 0, size=34)
                        self.render_surface.blit(eq_icon, (slot_x+6, sy+6))
                        self.render_surface.blit(
                            self.font_small.render(f"[{i+1}] {item_name}", True, ic), (slot_x+46, sy+5))
                        self.render_surface.blit(
                            pygame.font.SysFont("Arial",15).render(desc, True, GRAY), (slot_x+46, sy+26))
                    else:
                        self.render_surface.blit(
                            self.font_small.render(f"[{i+1}] — üres slot —", True, DARK_GRAY),
                            (slot_x+8, sy+14))

                # Bónuszok (4 slot vége: 104+3*54+46=312 → vonal 320, szöveg 326)
                pygame.draw.line(self.render_surface, DARK_GRAY, (slot_x, 320), (slot_x+slot_w, 320), 1)
                dmg_b, slow_b, rng_b = self.get_equipped_bonuses()
                self.render_surface.blit(self.font_small.render("Aktív bónuszok:", True, WHITE), (slot_x, 326))
                for bi, (btxt, bcol) in enumerate([
                    (f"+{int(dmg_b*100)}% sebzés", GREEN),
                    (f"+{int(slow_b*100)}% lassítás", LIGHT_BLUE),
                    (f"+{int(rng_b*100)}% hatótáv", YELLOW),
                ]):
                    self.render_surface.blit(
                        self.font_small.render(btxt, True, bcol),
                        (slot_x + bi*128, 350))

                # Láda szekció (bónuszok vége ~368 → vonal 376)
                pygame.draw.line(self.render_surface, DARK_GRAY, (slot_x, 376), (slot_x+slot_w, 376), 1)
                # Erőforrás sor: Pénz | Gold | Ládák | Kulcsok
                res_font = pygame.font.SysFont("Consolas", 17, bold=True)
                res_items = [
                    (f"${self.money}", GOLD,       slot_x),
                    (f"G:{self.gold}", (200,180,100), slot_x+110),
                    (f" {self.crates} láda",   LIGHT_BLUE,  slot_x+230),
                    (f"K:{self.keys} kulcs",    WHITE,       slot_x+310),
                ]
                for txt, col, rx in res_items:
                    self.render_surface.blit(res_font.render(txt, True, col), (rx, 382))
                self.inv_open_crate_btn.draw(self.render_surface)
                self.inv_buy_key_btn.draw(self.render_surface)
                self.inv_buy_crate_btn.draw(self.render_surface)
                self.inv_expand_btn.draw(self.render_surface)

                # ── JOBB OSZLOP (x=500..995): Item lista ──
                list_x = 500
                LIST_ROW_H = 24
                LIST_START_Y = 126
                MAX_VISIBLE = 23
                inv_count = len(self.inventory)

                self.render_surface.blit(
                    self.font_small.render(f"Itemek ({inv_count}/{self.inventory_max_size})", True, GOLD),
                    (list_x, 82))
                self.render_surface.blit(
                    pygame.font.SysFont("Arial",15).render(
                        "bal klikk: equip  •  jobb klikk: elad", True, GRAY),
                    (list_x, 104))
                self.inv_scroll_up_btn.draw(self.render_surface)
                self.inv_scroll_down_btn.draw(self.render_surface)

                if self.inventory:
                    visible = self.inventory[self.inv_scroll_offset:
                                             self.inv_scroll_offset + MAX_VISIBLE]
                    for idx, item_name in enumerate(visible):
                        rarity = ITEMS[item_name][0]
                        ic = RARITY_COLORS[rarity]
                        sell_price = RARITY_SELL_PRICE[rarity]
                        equipped = item_name in self.equipped_items
                        col = GRAY if equipped else ic
                        mark = "✓" if equipped else "•"
                        row_y = LIST_START_Y + idx * LIST_ROW_H
                        icon_s = pygame.Surface((20, 20), pygame.SRCALPHA)
                        draw_item_icon(icon_s, item_name, 0, 0, size=20)
                        self.render_surface.blit(icon_s, (list_x, row_y+2))
                        self.render_surface.blit(
                            self.font_small.render(f"{mark} {item_name}  [{sell_price}g]", True, col),
                            (list_x+24, row_y))
                    if inv_count > MAX_VISIBLE:
                        end_row = min(self.inv_scroll_offset+MAX_VISIBLE, inv_count)
                        self.render_surface.blit(
                            pygame.font.SysFont("Arial",14).render(
                                f"{self.inv_scroll_offset+1}-{end_row}/{inv_count}", True, DARK_GRAY),
                            (list_x, LIST_START_Y + MAX_VISIBLE*LIST_ROW_H + 4))
                else:
                    self.render_surface.blit(
                        self.font_small.render(
                            "(Még nincs tárgyad — nyiss ládát!)", True, DARK_GRAY),
                        (list_x, LIST_START_Y))

                self.inventory_back_button.draw(self.render_surface)
                for text in self.floating_texts:
                    text.draw(self.render_surface)

            elif self.menu_panel == "quit":
                # ── Kilépés megerősítés panel ────────────────
                sub_title = self.font_medium.render("Biztosan kilépsz?", True, RED)
                self.render_surface.blit(sub_title, (SCREEN_WIDTH//2 - sub_title.get_width()//2, 300))
                for btn in self.quit_panel_buttons:
                    btn.draw(self.render_surface)

        elif self.state == self.STATE_PLAYING:
            # Pálya és entitások
            self.current_map.draw(self.render_surface)
            
            for tower in self.towers:
                tower.draw(self.render_surface)
                
            for enemy in self.enemies:
                enemy.draw(self.render_surface)
                
            for proj in self.projectiles:
                proj.draw(self.render_surface)
                
            for text in self.floating_texts:
                text.draw(self.render_surface)

            # Kiválasztott torony UI
            if self.selected_tower_obj:
                self.selected_tower_obj.draw_range(self.render_surface)
                
                # Fejlesztés gomb pozíciójának frissítése (clamped to stay in play area)
                _bw = self.upgrade_button.rect.width
                _bh = self.upgrade_button.rect.height
                _max_y = SCREEN_HEIGHT - HUD_HEIGHT - _bh - 28  # 28 = sell hint height
                self.upgrade_button.rect.x = max(0, min(SCREEN_WIDTH - _bw, self.selected_tower_obj.x - _bw // 2))
                self.upgrade_button.rect.y = min(_max_y, self.selected_tower_obj.y + 30)

                # Kijelölő keret (Grid-hez igazítva)
                pygame.draw.rect(self.render_surface, YELLOW, (self.selected_tower_obj.grid_x, self.selected_tower_obj.grid_y, GRID_SIZE, GRID_SIZE), 2)
                
                # Fejlesztés információk
                info_text = f"Dmg: {self.selected_tower_obj.damage} → {self.selected_tower_obj.damage + self.selected_tower_obj.upgrade_damage}  |  Szint: {self.selected_tower_obj.level}"
                
                info_surf = self.font_small.render(info_text, True, WHITE)
                iw = info_surf.get_width() + 14
                # Clamping: ne menjen ki a képernyőről
                ix = max(2, min(SCREEN_WIDTH - iw - 2, self.selected_tower_obj.x - iw // 2))
                iy = max(2, self.selected_tower_obj.y - 68)

                # Átlátszó háttér helyes módon
                bg_surf = pygame.Surface((iw, 26), pygame.SRCALPHA)
                bg_surf.fill((0, 0, 0, 200))
                self.render_surface.blit(bg_surf, (ix, iy))
                pygame.draw.rect(self.render_surface, WHITE, (ix, iy, iw, 26), 1)
                self.render_surface.blit(info_surf, (ix + 7, iy + 4))
                
                # Gomb frissítése és rajzolása
                self.upgrade_button.text = f"Fejleszt (-${self.selected_tower_obj.upgrade_cost})"
                self.upgrade_button.draw(self.render_surface)

                # Eladás tipp
                sell_val = TOWER_CONFIG[self.selected_tower_obj.type]["cost"] // 2
                sell_hint = self.font_small.render(f"[DEL] Elad: +${sell_val}", True, GRAY)
                self.render_surface.blit(sell_hint, (self.upgrade_button.rect.x,
                                             self.upgrade_button.rect.bottom + 4))

            self.draw_hud()

        elif self.state == self.STATE_GAMEOVER:
            self.render_surface.fill((50, 0, 0))
            title = self.font_large.render("JÁTÉK VÉGE", True, RED)
            self.render_surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
            stats = [
                f"Elért hullám: {(self.wave_manager.current_wave_index if self.wave_manager else 0) + 1}",
                f"Épített tornyok: {len(self.towers)}",
                f"Gold: {self.gold}",
            ]
            for si, s in enumerate(stats):
                st = self.font_medium.render(s, True, GRAY)
                self.render_surface.blit(st, (SCREEN_WIDTH//2 - st.get_width()//2, 300 + si * 38))
            for btn in self.gameover_buttons:
                btn.draw(self.render_surface)

        elif self.state == self.STATE_VICTORY:
            self.render_surface.fill((0, 50, 0))
            title = self.font_large.render("GYŐZELEM!", True, GOLD)
            self.render_surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))
            stats = [
                f"Összes hullám teljesítve!",
                f"Épített tornyok: {len(self.towers)}",
                f"Gold: {self.gold}",
            ]
            for si, s in enumerate(stats):
                st = self.font_medium.render(s, True, WHITE)
                self.render_surface.blit(st, (SCREEN_WIDTH//2 - st.get_width()//2, 300 + si * 38))
            for btn in self.gameover_buttons:
                btn.draw(self.render_surface)

        # CS:GO láda animáció (minden más fölé rajzolódik)
        if self.crate_animation is not None:
            self.crate_animation.draw(self.render_surface)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            # Render surface skálázása a valós képernyőre
            sw, sh = self.screen.get_size()
            # Arány megtartva, letterbox/pillarbox
            scale = min(sw / SCREEN_WIDTH, sh / SCREEN_HEIGHT)
            scaled_w = int(SCREEN_WIDTH * scale)
            scaled_h = int(SCREEN_HEIGHT * scale)
            scaled = pygame.transform.scale(self.render_surface, (scaled_w, scaled_h))
            self.screen.fill(BLACK)
            ox = (sw - scaled_w) // 2
            oy = (sh - scaled_h) // 2
            self.screen.blit(scaled, (ox, oy))
            # Mouse offset tárolása az event handling-hoz
            self._mouse_offset = (ox, oy)
            self._mouse_scale = scale
            pygame.display.flip()
            self.clock.tick(FPS)

# ==========================================
# BELÉPÉSI PONT
# ==========================================
if __name__ == "__main__":
    game = Game()
    game.run()
