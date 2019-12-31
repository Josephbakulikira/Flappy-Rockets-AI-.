import pygame 
import os

pygame.font.init()

WIN_HEIGHT = 800
WIN_WIDTH = 500

ROCKET_SPRITE = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "rocket1.png"))), 
                pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "rocket2.png"))), 
                pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "rocket3.png")))]
OBSTACLE_SPRITE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe2.png")))
GROUND_SPRITE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "ground.png")))
BACKGROUND_SPRITE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

