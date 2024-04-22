import pygame
import math

pygame.init()
screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()
FOV = 60
RESOLUTION = 5
RENDERDIST = 3

class Maze(pygame.sprite.Sprite):
    def __init__(self, center_pos, image):
        super().__init__() 
        self.image = image
        self.rect = self.image.get_rect(center = center_pos)

    def update(self, surf):
        self.image = self.image.copy()
        self.rect = self.image.get_rect(center=self.rect.center)

class Player(pygame.sprite.Sprite):
    def __init__(self, center_pos, image):
        super().__init__() 
        self.image = image
        self.rect = self.image.get_rect(center = center_pos)
        self.angle = 0
        self.topleft = (0,0)

    def rectifyAngle(self):
        if self.angle > 360:
            self.angle = 0
        if self.angle < 0:
            self.angle = 360

    def updatePosition(self, keys):
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.x += 3 * math.sin(math.radians(self.angle))
            self.rect.y += 3 * math.cos(math.radians(self.angle))
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.x -= 3 * math.sin(math.radians(self.angle))
            self.rect.y -= 3 * math.cos(math.radians(self.angle))
        if keys[pygame.K_RIGHT]:
            self.angle += 3
        if keys[pygame.K_LEFT]:
            self.angle += -3
        if keys[pygame.K_a]:
            self.rect.x += 2 * math.sin(math.radians(self.angle-90))
            self.rect.y += 2 * math.cos(math.radians(self.angle-90))
        if keys[pygame.K_d]:
            self.rect.x += 2 * math.sin(math.radians(self.angle+90))
            self.rect.y += 2 * math.cos(math.radians(self.angle+90))

    def collisionFix(self):
        self.rect.x = self.oldX
        self.rect.y = self.oldY
        self.angle = self.oldAngle

    def update(self, surf):
        self.oldX = self.rect.x
        self.oldY = self.rect.y
        self.oldAngle = self.angle
        keys = pygame.key.get_pressed()

        self.rectifyAngle()
        self.updatePosition(keys)
        
        self.image = player_surf_old.copy()
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Raycaster(pygame.sprite.Sprite):
    def __init__(self, center_pos, image):
        super().__init__() 
        self.image = image
        self.rect = self.image.get_rect(center = center_pos)
        self.topleft = (0,0)
    
    def cast(self, playerPos, angleModifier, XModifier, YModifier, xBlast):
        try:
            self.rect.x = playerPos.rect.x + XModifier
            self.rect.y = playerPos.rect.y + YModifier
            self.angle = playerPos.angle + angleModifier
    
            notCollided = True
            i = 0
            while notCollided:
                i += 5
                if screen.get_at((int(self.rect.x +i * math.sin(math.radians(self.angle))), int(self.rect.y+i* math.cos(math.radians(self.angle))))) == (255,0,0,255) or (math.sqrt((((self.rect.x+i) - (self.rect.x))**2) + (((self.rect.y+i) - (self.rect.y))**2)))/RENDERDIST > 255:
                    notCollided = False
            
            if not (math.sqrt((((self.rect.x+i) - (self.rect.x))**2) + (((self.rect.y+i) - (self.rect.y))**2)))/RENDERDIST > 255:
                notCollided = True
                while notCollided:
                    i -= 1
                    if screen.get_at((int(self.rect.x +i * math.sin(math.radians(self.angle))), int(self.rect.y+i* math.cos(math.radians(self.angle))))) != (255,0,0,255):
                        notCollided = False

            #MARK: Raycast line
            #pygame.draw.line(screen, (0,255,255), (self.rect.x, self.rect.y), (int(self.rect.x +i * math.sin(math.radians(self.angle))),int(self.rect.y+i* math.cos(math.radians(self.angle)))))

            self.dist = math.sqrt((((self.rect.x+i) - (self.rect.x))**2) + (((self.rect.y+i) - (self.rect.y))**2))
            #MARK: WHY WONT THIS WORK
            #self.dist = self.dist * math.cos(self.angle-playerPos.angle)
            self.height = 12000/self.dist

            #pygame.draw.line(screen, (0,255,255), (xBlast+500, self.height+396), (xBlast+500, 0-self.height+396))
            return [(xBlast+500, self.height+396), (xBlast+500, 0-self.height+396), self.dist]
        except:
            print(f"Raycast failed at {self.rect.x}, {self.rect.y}.")

player_surf_old = pygame.image.load('C:/Users/YBVostro/Code/raycaster/player.png').convert_alpha()
maze_surf = pygame.image.load('C:/Users/YBVostro/Code/raycaster/Maze.png').convert_alpha()

player = Player(screen.get_rect().center, player_surf_old)
maze = Maze(screen.get_rect().center, maze_surf)
raycast = Raycaster(screen.get_rect().center, player_surf_old)
all_sprites = pygame.sprite.Group([player, maze])

maze.mask = pygame.mask.from_threshold(maze.image, (255,0,0,255), (1, 1, 1, 255))


def drawRays(screen, FOV, player, raycast):
    rays = []
    o_X = -500
    o_ScanLines = int(1000/RESOLUTION)
    for i in range(o_ScanLines):
        rays.append(raycast.cast(player, i*(FOV/o_ScanLines)-(FOV/2), 8,10, o_X))
        o_X += RESOLUTION

    #MARK: Screen Fill
    screen.fill(0)

    for i in rays:
        try:
            if i[2]/RENDERDIST < 255:
                pygame.draw.line(screen, (0,255-(i[2]/RENDERDIST),0,), i[0], i[1], width=RESOLUTION)
        except:
            print("Unable to render.")
exit = True
while exit:
    clock.tick(60) #Run at 60FPS
    for event in pygame.event.get(): #When user stops program
        if event.type == pygame.QUIT:
            exit = False

    if pygame.sprite.spritecollideany(player, [maze], pygame.sprite.collide_mask):
        player.collisionFix()    

    all_sprites.update(screen)
    screen.fill(0)
    all_sprites.draw(screen)

    drawRays(screen, FOV, player, raycast)

    pygame.display.flip()

#MARK: https://youtu.be/Vihr-PVjWF4?list=PLy4zsTUHwGJKolO9Ko_j6IStFIJnTYBul 