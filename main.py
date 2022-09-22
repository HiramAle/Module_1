import pygame
import ctypes

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
        self.outlineImage = 0
        self.get_mask()

    def get_mask(self):
        mask = pygame.mask.from_surface(self.image)
        surf = pygame.Surface((self.rect.width, self.rect.height))
        surf.set_colorkey((0, 0, 0))
        pic_mask = mask.to_surface()
        surf.blit(pic_mask, (0, 1))
        surf.blit(pic_mask, (0, -1))
        surf.blit(pic_mask, (1, 0))
        surf.blit(pic_mask, (-1, 0))
        surf.blit(self.image, (0, 0))
        self.outlineImage = surf

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

    def update(self):
        if self.click():
            self.image = self.outlineImage


class Cable(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int], name: str, groups: pygame.sprite.Group, image_path: str):
        super().__init__(groups)
        self.name = name
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.copy().inflate(0, -10)
        self.dragging = False

    def update(self):
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.centery = self.rect.centery


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

    def update(self):
        self.hitbox.center = self.rect.center


class Game:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        # Game settings
        self.width = 1280
        self.height = 720
        self.display = pygame.display.set_mode((self.width, self.height))
        self.mainPanel = pygame.Surface((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True

        self.cableDict = {"green": (int(self.width / 2), 200),
                          "orange": (int(self.width / 2), 300),
                          "blue": (int(self.width / 2), 400)}

        self.cableList = ["green", "orange", "blue"]
        self.cableOrder = ["orange", "blue", "green"]

        self.cableGroups = pygame.sprite.Group()
        self.cableGreen = Cable((int(self.width / 2), 200), "green", self.cableGroups,
                                "Assets/Cable/Cable_Strip_Green.png")
        self.cableOrange = Cable((int(self.width / 2), 300), "orange", self.cableGroups,
                                 "Assets/Cable/Cable_Plain_Orange.png")
        self.cableBlue = Cable((int(self.width / 2), 400), "blue", self.cableGroups,
                               "Assets/Cable/Cable_Plain_Blue.png")


        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

        self.ordered_flag = False

        self.selectedCable = None

        self.buttonsGroup = pygame.sprite.Group()
        self.button = ImageButton((self.width / 2, 600), "Pinzas.png", self.buttonsGroup)

        self.colorLineGroup = pygame.sprite.Group()
        self.colorLine = ColorLine((self.width / 2, 100), self.colorLineGroup, "LineColor.png")
        self.lineCursor = ColorLineCursor((self.width / 2, 100), self.colorLineGroup, "ColorCursor.png")
        self.cursor_direction = "left"

    def show_button(self):
        if self.cableList == self.cableOrder:
            return True

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

    def drag(self, event: pygame.event):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            for sprite in self.cableGroups:
                if sprite.rect.collidepoint(mouse_x, mouse_y):
                    self.dragging = True
                    sprite.dragging = True
                    self.offset_x = mouse_x - sprite.rect.x
                    self.offset_y = mouse_y - sprite.rect.y
                    self.selectedCable = sprite

        if event.type == pygame.MOUSEBUTTONUP and self.selectedCable:
            if self.selectedCable.dragging:
                self.selectedCable.dragging = False
                self.dragging = False
                self.selectedCable.rect.centery = self.cableDict[self.selectedCable.name][1]
                if self.show_button():
                    self.buttonsGroup.update()

    def cursor_movement(self):
        if self.cursor_direction == "left":
            self.lineCursor.rect.x -= 5
        else:
            self.lineCursor.rect.x += 5

        if self.lineCursor.rect.x > (self.colorLine.rect.x + self.colorLine.rect.width - 20):
            self.cursor_direction = "left"

        if self.lineCursor.rect.x < self.colorLine.rect.x:
            self.cursor_direction = "right"

    def on_dragging(self):
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.selectedCable.rect.y = mouse_y - self.offset_y
            # print(self.get_mouse_direction(mouse_y, self.cableDict[self.selectedCable.name][1]))

            for cable in self.cableGroups:
                if cable != self.selectedCable:
                    if cable.hitbox.collidepoint(mouse_x, mouse_y):
                        cable.rect.centery = self.cableDict[self.selectedCable.name][1]
                        i1 = self.cableList.index(cable.name)
                        i2 = self.cableList.index(self.selectedCable.name)

                        self.cableList[i1], self.cableList[i2] = self.cableList[i2], self.cableList[i1]

                        self.cableDict[cable.name], self.cableDict[self.selectedCable.name] = \
                            self.cableDict[self.selectedCable.name], self.cableDict[cable.name]

                        print(self.cableList)

    def update(self):

        self.colorLineGroup.update()
        self.cableGroups.update()

        self.cursor_movement()

        self.on_dragging()

    def render(self):
        # Background
        self.mainPanel.fill("#262626")

        # Groups draw
        self.cableGroups.draw(self.mainPanel)
        self.colorLineGroup.draw(self.mainPanel)
        if self.ordered_flag:
            self.buttonsGroup.draw(self.mainPanel)

        # Update display
        self.display.blit(self.mainPanel, (0, 0))
        pygame.display.update()

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                exit()

            self.drag(event)
            self.cursor_collision(event)

    def main_loop(self):
        while self.running:
            self.event_loop()
            self.update()
            self.render()
            self.clock.tick(60)


if __name__ == '__main__':
    Game().main_loop()
