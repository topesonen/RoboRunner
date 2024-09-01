# Complete your game here
import pygame
import random

class GameObject:
    def __init__(self, x: int, y: int, img: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.img = img


class Robot(GameObject):
    def __init__(self, x:int, y:int, img: pygame.Surface) -> None:
        super().__init__(x,y,img)
        self.velocity = 0
        self.is_jumping = False
        self.gravity = 0.8
        self.jump_strength = -15
        self.floor = Game.HEIGHT - self.img.get_height()
    
    def jump(self):
        # jumping means setting the velocity to negative, moving upwards
        if not self.is_jumping:
            self.velocity = self.jump_strength
            self.is_jumping = True

    def move(self):
        # y positions is increased by velocity, acceleration slowed by gravity
        if self.is_jumping:
            self.y += self.velocity
            self.velocity += self.gravity

            # stop movement when the floor is hit
            if self.y >= self.floor:
                self.y = self.floor
                self.is_jumping = False
                self.velocity = 0


class Monster(GameObject):
    # move ghost left
    def move(self):
        self.x -= 2

class Coin(GameObject):
    # mve coins left
    def move(self):
        self.x -= 3

class Door(GameObject):
    pass

class Game:
    WIDTH = 640
    HEIGHT = 480

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("RoboRunner")

        self.coin_img = pygame.image.load("coin.png")
        self.door_img = pygame.image.load("door.png")
        self.monster_img = pygame.image.load("monster.png")
        self.robot_img = pygame.image.load("robot.png")

        self.robot = Robot(self.WIDTH / 4, self.HEIGHT - self.robot_img.get_height(), self.robot_img)
        self.coins = []
        self.monsters = []

        self.score = 0
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.game_over_font = pygame.font.SysFont("Arial", 72)

    def spawn_objects(self):
        # randomly spawn coins the the right side of screen
        if random.random() > 0.99:

            coin_x = self.WIDTH
            # coin should be reachable by the robot
            max_jump_height = self.robot.floor - (self.robot.jump_strength ** 2) / (2 * self.robot.gravity)
            coin_y = random.randint(int(max_jump_height), self.robot.floor)
            self.coins.append(Coin(coin_x, coin_y, self.coin_img))

        # randomly spawn monsters the the right side of screen
        if random.random() > 0.995:

            monster_x = self.WIDTH
            # coin should be reachable by the robot
            max_jump_height = self.robot.floor - (self.robot.jump_strength ** 2) / (2 * self.robot.gravity)
            monster_y = random.randint(int(max_jump_height), self.robot.floor)
            self.monsters.append(Coin(monster_x, monster_y, self.monster_img))
    
    def move_objects(self):
        self.robot.move()    
        for coin in self.coins:
            coin.move()

        for monster in self.monsters:
            monster.move()

        # remove coins and monsters when they reach the left side of the screen
        self.coins = [coin for coin in self.coins if coin.x > -self.coin_img.get_width()]
        self.monsters = [monster for monster in self.monsters if monster.x > -self.monster_img.get_width()]

    def check_collisions(self):
        for coin in self.coins[:]:
            if (abs(self.robot.x - coin.x) < self.robot.img.get_width() and 
                abs(self.robot.y - coin.y) < self.robot.img.get_height()):
                self.coins.remove(coin)
                self.score += 1

        for monster in self.monsters[:]:
            if (abs(self.robot.x - monster.x) < self.robot.img.get_width() and 
                abs(self.robot.y - monster.y) < self.robot.img.get_height()):
                return True 

        return False # game goes on
    
    def draw(self):
        self.screen.fill((135, 206, 235))

        # draw the robot
        self.screen.blit(self.robot.img, (self.robot.x, self.robot.y))

        # draw the coins
        for coin in self.coins:
            self.screen.blit(coin.img, (coin.x, coin.y))

        # draw the monsters
        for monster in self.monsters:
            self.screen.blit(monster.img, (monster.x, monster.y))

        score_text = self.font.render(f'Score: {self.score}', True, (255, 0, 0))
        self.screen.blit(score_text, (500, 10))
        pygame.display.flip()

    def game_over(self):
        self.screen.fill((0, 0, 0))  # Black background
        game_over_text = self.game_over_font.render("YOU LOST", True, (255, 0, 0))  # Red text
        text_rect = game_over_text.get_rect(center=(self.WIDTH/2, self.HEIGHT/2))
        self.screen.blit(game_over_text, text_rect)
        pygame.display.flip()
        pygame.time.wait(3000)  # Wait for 3 seconds before closing

    def play(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.robot.jump()

            self.spawn_objects()
            self.move_objects()
            if self.check_collisions():
                self.game_over()
                running = False
            self.draw()
        
            self.clock.tick(60)

        pygame.quit()
        

if __name__ == "__main__":
    game_instance = Game()
    game_instance.play()
