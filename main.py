import random
import pygame
import ctypes
from Cable import Cable

# Avoid DPI virtualization
ctypes.windll.user32.SetProcessDPIAware()

# Colors
red = "#EA5E5E"
yellow = "#F7BA3E"
blue = "#56B3B4"
purple = "#BF85BF"
grayBackground = "#1A2B34"
gray = "#465862"


class ImageButton(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, image_path: str, groups: pygame.sprite.Group):
        super().__init__(groups)
        self.x = pos[0]
        self.y = pos[1]
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.pressed = False

    def hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        else:
            return False

    def click(self):
        if self.hover():
            action = False
            if pygame.mouse.get_pressed()[0] and not self.pressed:
                self.pressed = True
                action = True
            if not pygame.mouse.get_pressed()[0]:
                self.pressed = False
            return action


class ColorLine(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, groups: pygame.sprite.Group, image_path: str):
        super().__init__(groups)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.orangeHitbox = self.rect.inflate(-25, 0)
        self.yellowHitbox = self.rect.inflate(-150, 0)
        self.greenHitbox = self.rect.inflate(-230, 0)


class ColorLineCursor(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, groups: pygame.sprite.Group, image_path: str):
        super().__init__(groups)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.copy().inflate(-30, -10)
        self.direction = "left"

    def update(self):
        self.hitbox.center = self.rect.center


class Generic(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, name: str, groups: pygame.sprite.Group, image_path: str, horizontal_flip=False,
                 centered=True):
        super().__init__(groups)
        self.name = name
        if horizontal_flip:
            self.image = pygame.transform.flip(pygame.image.load(image_path).convert_alpha(), True, False)
        else:
            self.image = pygame.image.load(image_path).convert_alpha()

        self.rect = self.image.get_rect(center=pos) if centered else self.image.get_rect(topleft=pos)


class Game:
    def __init__(self):
        # ---------- Pygame Settings ----------
        # Initialize pygame
        pygame.init()
        # Game settings
        self.width = 1280
        self.height = 720
        self.display = pygame.display.set_mode((self.width, self.height))
        self.mainPanel = pygame.Surface((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True

        # ---------- Cable ----------
        # Cable set
        self.T568A = ["sGreen", "pGreen", "sOrange", "pBlue", "sBlue", "pOrange", "sBrown", "pBrown"]
        # Make a copy of the cable order and shuffle it
        self.cableShuffle = self.T568A.copy()
        random.shuffle(self.cableShuffle)
        # Save cable position on dictionary
        self.cableDict = {}
        start_pos = 200
        increase_amount = 50
        for i, cable in enumerate(self.cableShuffle):
            self.cableDict[cable] = (int(self.width / 2), start_pos + (i * increase_amount))
        # Set sprite Group for cables
        self.cableGroup = pygame.sprite.Group()
        # Set image path
        for cable in self.cableDict:
            path_name = "Assets/Cable/Cable_"
            if cable[0] == "p":
                path_name += "Plain"
            else:
                path_name += "Strip"
            path_name += "_" + cable[1:] + ".png"
            self.cableGroup.add(Cable(self.cableDict[cable], cable, self.cableGroup, path_name))

        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

        self.ordered_flag = False

        self.selectedCable = None

        self.buttonGroup = pygame.sprite.Group()
        self.button = ImageButton((self.width / 2, 600), "Pinzas.png", self.buttonGroup)

        self.colorLineGroup = pygame.sprite.Group()
        self.colorLine = ColorLine((self.width / 2, 100), self.colorLineGroup, "LineColor.png")
        self.lineCursor = ColorLineCursor((self.width / 2, 100), self.colorLineGroup, "ColorCursor.png")
        self.cursor_direction = "left"

        self.genericGroup = pygame.sprite.Group()
        self.genericGroup.add(
            Generic((-310, 155), "Plastic", self.genericGroup, "Assets/Cable/Cable_Plastic.png", horizontal_flip=True,
                    centered=False))
        self.genericGroup.add(
            Generic((800, 110), "RJ45", self.genericGroup, "Assets/Cable/Cable_RJ45.png", horizontal_flip=True,
                    centered=False))

        self.plastic = pygame.transform.flip(pygame.image.load("Assets/Cable/Cable_Plastic.png").convert_alpha(), True,
                                             False)
        self.RJ45_moved = False
        self.RJ45 = pygame.transform.flip(pygame.image.load("Assets/Cable/Cable_RJ45.png").convert_alpha(), True, False)

        self.handCursor = pygame.image.load("Assets/Cursor/Win95DefPalm.png").convert_alpha()
        self.grabCursor = pygame.image.load("Assets/Cursor/Win95DefGrab.png").convert_alpha()
        self.cursor = pygame.image.load("Assets/Cursor/Win95Tri.png").convert_alpha()

        self.actualCursor = self.cursor
        pygame.mouse.set_visible(False)
        self.cursorRect = self.actualCursor.get_rect()

    def cursor_collision(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.lineCursor.hitbox.colliderect(self.colorLine.greenHitbox) and \
                        self.lineCursor.hitbox.colliderect(self.colorLine.yellowHitbox) and \
                        self.lineCursor.hitbox.colliderect(self.colorLine.orangeHitbox):
                    print("green")

                if not self.lineCursor.hitbox.colliderect(self.colorLine.greenHitbox) and \
                        self.lineCursor.hitbox.colliderect(self.colorLine.yellowHitbox) and \
                        self.lineCursor.hitbox.colliderect(self.colorLine.orangeHitbox):
                    print("yellow")

                if not self.lineCursor.hitbox.colliderect(self.colorLine.greenHitbox) and \
                        not self.lineCursor.hitbox.colliderect(self.colorLine.yellowHitbox) and \
                        self.lineCursor.hitbox.colliderect(self.colorLine.orangeHitbox):
                    print("orange")

    def show_button(self):
        if self.cableShuffle == self.T568A:
            print("Same")
            self.ordered_flag = True
            if not self.RJ45_moved:
                self.RJ45_moved = True
                for sprite in self.genericGroup:
                    sprite: Generic
                    if sprite.name == "RJ45":
                        sprite.rect.x -= 350
        else:
            print("Not same")
            print(f"Order: {self.T568A}")
            print(f"{self.cableShuffle}")

    def drag_start(self, event: pygame.event.Event):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        hover = False

        for sprite in self.cableGroup:
            if sprite.rect.collidepoint(mouse_x, mouse_y):
                hover = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.dragging = True
                    sprite.dragging = True
                    self.offset_x = mouse_x - sprite.rect.x
                    self.offset_y = mouse_y - sprite.rect.y
                    self.selectedCable = sprite

        if hover:
            if self.actualCursor is not self.handCursor:
                self.actualCursor = self.handCursor
        else:
            if self.actualCursor is not self.cursor:
                self.actualCursor = self.cursor

    def drag_end(self, event: pygame.event):
        if event.type == pygame.MOUSEBUTTONUP and self.selectedCable:
            if self.selectedCable.dragging:
                if self.actualCursor is not self.handCursor:
                    self.actualCursor = self.handCursor
                self.selectedCable.dragging = False
                self.dragging = False
                self.selectedCable.rect.centery = self.cableDict[self.selectedCable.name][1]
                self.show_button()

    def cursor_movement(self):
        if self.lineCursor.direction == "left":
            self.lineCursor.rect.x -= 5
        else:
            self.lineCursor.rect.x += 5

        if self.lineCursor.rect.x > (self.colorLine.rect.x + self.colorLine.rect.width - 20):
            self.lineCursor.direction = "left"

        if self.lineCursor.rect.x < self.colorLine.rect.x:
            self.lineCursor.direction = "right"

    def on_dragging(self):
        if self.dragging:
            if self.actualCursor is not self.grabCursor:
                self.actualCursor = self.grabCursor
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.selectedCable.rect.y = mouse_y - self.offset_y

            for cable in self.cableGroup:
                cable: Cable
                if cable != self.selectedCable:
                    if cable.hitbox.collidepoint(mouse_x, mouse_y):
                        cable.rect.centery = self.cableDict[self.selectedCable.name][1]
                        i1 = self.cableShuffle.index(cable.name)
                        i2 = self.cableShuffle.index(self.selectedCable.name)

                        self.cableShuffle[i1], self.cableShuffle[i2] = self.cableShuffle[i2], self.cableShuffle[i1]

                        self.cableDict[cable.name], self.cableDict[self.selectedCable.name] = \
                            self.cableDict[self.selectedCable.name], self.cableDict[cable.name]

    def update(self):
        self.cursorRect.center = pygame.mouse.get_pos()
        self.colorLineGroup.update()
        self.cableGroup.update()
        self.cursor_movement()
        self.on_dragging()

    def render(self):
        # Background
        self.mainPanel.fill("#262626")
        # Groups draw
        self.cableGroup.draw(self.mainPanel)

        # self.mainPanel.blit(self.plastic, (-310, 155))
        # self.mainPanel.blit(self.RJ45, (800, 110))
        self.genericGroup.draw(self.mainPanel)

        if self.ordered_flag:
            self.buttonGroup.draw(self.mainPanel)
            self.colorLineGroup.draw(self.mainPanel)

        # Cursor
        self.mainPanel.blit(self.actualCursor, self.cursorRect)
        # Update display
        self.display.blit(self.mainPanel, (0, 0))
        pygame.display.update()

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()

            self.drag_start(event)
            self.drag_end(event)
            self.cursor_collision(event)

    def main_loop(self):
        while self.running:
            self.event_loop()
            self.update()
            self.render()
            self.clock.tick(60)


if __name__ == '__main__':
    Game().main_loop()
