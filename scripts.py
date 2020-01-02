import neat
import pygame 
import random
import time
import os


from component import WIN_HEIGHT, WIN_WIDTH, ROCKET_SPRITE, OBSTACLE_SPRITE, GROUND_SPRITE, BACKGROUND_SPRITE, STAT_FONT

class Rocket:
    SPRITES = ROCKET_SPRITE
    MAX_ROTATION = 25
    R_VELOCITY = 20
    ANIMATION = 5

    def __init__ (self, x, y):
        self.x = x 
        self.y = y
        self.tick_count = 0
        self.vel = 0
        self.tilt = 0
        self.height = self.y
        self.img_count = 0
        self.img =self.SPRITES[0]
    
    def jump (self):
        self.vel =-10.5
        self.tick_count = 0
        self.height = self.y
    
    def move(self):
        self.tick_count += 1
        distance = self.vel * self.tick_count + 1.5 * self.tick_count ** 2
        if distance >= 16:
            distance = 16 
        if distance < 0 :
            distance -= 2

        self.y = self.y + distance  
        if distance < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.R_VELOCITY 

    def draw(self, win):
        self.img_count += 1 

        if self.img_count < self.ANIMATION:
            self.img = self.SPRITES[0]
        elif self.img_count < self.ANIMATION * 2:
            self.img = self.SPRITES[1]
        elif self.img_count < self.ANIMATION * 3:
            self.img = self.SPRITES[2]
        elif self.img_count < self.ANIMATION * 4:
            self.img = self.SPRITES[1]
        elif self.img_count < self.ANIMATION *  4 + 1:
            self.img = self.SPRITES[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.SPRITES[1]
            self.img_count = self.ANIMATION * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)

        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Obstacle:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0 
        self.bottom = 0 
        
        self.TOP_OBSTACLE = pygame.transform.flip(OBSTACLE_SPRITE, False, True) 
        self.BOTTOM_OBSTACLE = OBSTACLE_SPRITE
        
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.TOP_OBSTACLE.get_height()
        self.bottom = self.height + self.GAP 
    
    def move (self):
        self.x -= self.VEL
    
    def draw(self, win):
        win.blit(self.TOP_OBSTACLE, (self.x, self.top))
        win.blit(self.BOTTOM_OBSTACLE, (self.x, self.bottom))

    def collide(self, rocket, win):
        rocket_mask = rocket.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_OBSTACLE)
        bottom_mask = pygame.mask.from_surface(self.BOTTOM_OBSTACLE)

        top_offset = (self.x - rocket.x, self.top - round(rocket.y))
        bottom_offset = (self.x - rocket.x, self.bottom - round(rocket.y))

        b_point = rocket_mask.overlap(bottom_mask, bottom_offset)
        t_point = rocket_mask.overlap(top_mask, top_offset)
        if b_point or t_point :
            return True
        return False

class Ground:
    VEL = 5 
    WIDTH = GROUND_SPRITE.get_width()
    SPRITE = GROUND_SPRITE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    def draw(self, win):
        win.blit(self.SPRITE, (self.x1, self.y))
        win.blit(self.SPRITE, (self.x2, self.y))

        
def draw_window(win, rockets, obstacles, ground, score ):
    win.blit(BACKGROUND_SPRITE, (0,0))

    for obstacle in obstacles:
        obstacle.draw(win)

    text = STAT_FONT.render("Score: "  + str(score), 1, (255,255,255) )
    win.blit(text, (WIN_WIDTH - 350 - text.get_width(), 15))
    ground.draw(win)

    for rocket in rockets:
        rocket.draw(win)
    
    pygame.display.update()

def main(genomes, config):
    nets = []
    ge = []
    rockets = []
    
    for genome_id, g in genomes:
        
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        rockets.append(Rocket(230, 350))
        g.fitness = 0
        ge.append(g)

    ground = Ground(730)
    
    obstacles = [Obstacle(600)]

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    run = True
    timing = pygame.time.Clock()
    score =0 
    while run:
        timing.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        obstacle_ind = 0

        if len(rockets) > 0:
            if len(obstacles) > 1 and rockets[0].x > obstacles[0].x + obstacles[0].TOP_OBSTACLE.get_width():
                obstacle_ind = 1
        else:
            run = False
            break

        for x, rocket in enumerate(rockets):
            rocket.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((rocket.y, abs(rocket.y - obstacles[obstacle_ind].height), abs(rocket.y - obstacles[obstacle_ind].bottom)))
            if output[0] > 0.5:
                rocket.jump()  

        rem =[]     
        add_obstacle = False 
        print(len(rockets))
        for obstacle in obstacles: 
            obstacle.move() 

            for  x, rocket in enumerate(rockets):
                  
                if obstacle.collide(rocket, win):
                    ge[x].fitness -= 1
                    rockets.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                
                
                if not obstacle.passed and obstacle.x < rocket.x:
                    obstacle.passed = True
                    add_obstacle = True
            
            if obstacle.x + obstacle.TOP_OBSTACLE.get_width() < 0:
                    rem.append(obstacle)

            
        
        if add_obstacle:
            score += 1
            for g in ge:
                g.fitness += 5
            obstacles.append(Obstacle(600))
        for r in rem:
            obstacles.remove(r)
        for x, rocket in enumerate(rockets):
            if rocket.y + rocket.img.get_height() >= 730 or rocket.y < 0:
                rockets.pop(x)
                nets.pop(x)
                ge.pop(x)

        # rocket.move()
        
        ground.move()
        draw_window(win, rockets, obstacles, ground, score)



def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    batu = neat.Population(config)

    batu.add_reporter(neat.StdOutReporter(True))

    stats = neat.StatisticsReporter()
    
    batu.add_reporter(stats)
    
    winner = batu.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__) 
    config_path = os.path.join( local_dir, "config-feedforward.txt")
    run(config_path)