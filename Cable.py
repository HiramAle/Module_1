import pygame


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

