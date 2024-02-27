from typing import Any
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
Gravity = pygame.Vector2(0, 9.81)

class Wall(pygame.sprite.Sprite):
    def __init__(self, size, **kwargs) -> None:
        super().__init__()
        self.image = pygame.Surface(size).convert_alpha()
        self.image.fill("black")
        self.rect = self.image.get_rect(**kwargs)

class Toast(pygame.sprite.Sprite):
    def __init__(self, pos) -> None:
        super().__init__()
        self.position = pygame.Vector2(pos)
        self.velocity = pygame.Vector2()
        self.image = pygame.Surface((100, 100))
        self.image.fill("red")
        self.rect = self.image.get_rect(center=self.position.xy)
        self.on_ground = False

    def gravity(self):
        self.velocity.y += Gravity.y

    def control(self, x, y):
        self.velocity.x += x

    def jump(self):
        if self.on_ground:
            self.velocity.y = -30
            self.on_ground = False

    def update(self, walls: pygame.sprite.Group) -> None:
        self.gravity()
        self.position += self.velocity
        
        print(self.rect.top)
        # Kollisionserkennung und -behandlung
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity.y > 0:
                    self.rect.bottom = wall.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                    print("1")
                elif self.velocity.y <= 0:
                    self.rect.top = wall.rect.bottom
                    self.velocity.y = 0
                    print("2")

        self.rect.center = self.position.xy

toast = Toast((500, 500))
toasts = pygame.sprite.Group(toast)

wall_group = pygame.sprite.Group()
wall_group.add(Wall((100, 50), topleft=(screen.get_width()/2, 600)))
wall_group.add(Wall((screen.get_width(), 10), topleft=(0, screen.get_height() - 10)))

font = pygame.font.SysFont("arial", 15)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_w):  
                toast.jump()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        toast.control(-1, 0)
    if keys[pygame.K_d]:
        toast.control(1, 0)

    toasts.update(wall_group)
    wall_group.update()

    screen.fill("blue")
    wall_group.draw(screen)
    toasts.draw(screen)

    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
