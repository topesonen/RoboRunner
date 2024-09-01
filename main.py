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
        self.gravity = 0.7
        self.jump_strength = -15
        self.floor = Game.HEIGHT - self.img.get_height() - 20
        self.is_crouching = False
        self.original_img = img
        self.crouch_img = pygame.transform.scale(img, (img.get_width(), img.get_height() // 2))
    
    def jump(self):
        # jumping means setting the velocity to negative, moving upwards
        if not self.is_jumping:
            self.velocity = self.jump_strength
            self.is_jumping = True

    def crouch(self):
        # crouching means halving the robot height, to avoid monsters
        if not self.is_jumping:
            self.is_crouching = True
            self.img = self.crouch_img
            self.y = Game.HEIGHT - self.img.get_height() - 20

    def stand(self):
        if not self.is_jumping:
            self.is_crouching = False
            self.img = self.original_img
            self.y = Game.HEIGHT - self.img.get_height() - 20

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
    def move(self, speed):
        self.x -= speed * 0.8

class Coin(GameObject):
    # mve coins left
    def move(self, speed):
        self.x -= speed

class Door(GameObject):
    def __init__(self, x: int, y: int, img: pygame.Surface) -> None:
        super().__init__(x, y, img)
        self.img = pygame.transform.scale(img, (img.get_width() // 2, img.get_height() // 2))
    
    def move(self):
        self.x += 10

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

        self.robot = Robot(self.WIDTH / 4, self.HEIGHT - self.robot_img.get_height() - 20, self.robot_img)
        self.coins = []
        self.monsters = []
        self.doors = []
        self.monster_timer = 0 # to have some time between spawning monsters

        self.game_speed = 5
        self.speed_increase_timer = 0

        self.throw_cooldown = False
        self.throw_cooldown_timer = 0

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
        if random.random() > 0.995 and self.monster_timer <= 0:
            
            monster_x = self.WIDTH
            
            monster_y = random.randint(200, self.robot.floor)
            self.monsters.append(Monster(monster_x, monster_y, self.monster_img))
            self.monster_timer = 1000 # 1 second between monster spawn
    
    def move_objects(self):
        self.robot.move()    
        for coin in self.coins:
            coin.move(self.game_speed)

        for monster in self.monsters:
            monster.move(self.game_speed)

        for door in self.doors:
            door.move()

        # remove coins and monsters when they reach the left side of the screen
        self.coins = [coin for coin in self.coins if coin.x > -self.coin_img.get_width()]
        self.monsters = [monster for monster in self.monsters if monster.x > -self.monster_img.get_width()]

        # and door if the reach the rights side of the screen
        self.doors = [door for door in self.doors if door.x > self.door_img.get_width()]

    def throw_door(self):
        if self.throw_cooldown == False:
            door_x = self.robot.x + self.robot_img.get_width()
            door_y = self.robot.y - self.robot_img.get_height() / 8

            self.doors.append(Door(door_x, door_y, self.door_img))
            self.throw_cooldown = True
            self.throw_cooldown_timer = 1000

    def check_collisions(self):
        for coin in self.coins[:]:
            if (abs(self.robot.x - coin.x) < self.robot.img.get_width() and 
                abs(self.robot.y - coin.y) < self.robot.img.get_height()):
                self.coins.remove(coin)
                self.score += 1
        
        # Check for collisions between doors and monsters
        for door in self.doors[:]:
            for monster in self.monsters[:]:
                if (abs(door.x - 30 - monster.x) < monster.img.get_width() and 
                    abs(door.y - monster.y) < monster.img.get_height()):
                    self.monsters.remove(monster)
                    self.doors.remove(door)
                    self.score += 1

        for monster in self.monsters[:]:
            if (abs(self.robot.x - 30 - monster.x) < self.robot.img.get_width() and 
                abs(self.robot.y + 20 - monster.y) < self.robot.img.get_height()):
                return True 

        return False # game goes on
    
    def draw(self):
        self.screen.fill((60, 60, 60))
        # draw floor
        pygame.draw.rect(self.screen, (32, 32, 32), (0, self.HEIGHT-20, self.WIDTH, self.HEIGHT))

        # draw the robot
        self.screen.blit(self.robot.img, (self.robot.x, self.robot.y))

        # draw the coins
        for coin in self.coins:
            self.screen.blit(coin.img, (coin.x, coin.y))

        # draw the monsters
        for monster in self.monsters:
            self.screen.blit(monster.img, (monster.x, monster.y))

        # and doors
        for door in self.doors:
            self.screen.blit(door.img, (door.x, door.y))

        # draw the score
        score_text = self.font.render(f'Score: {self.score}', True, (255, 0, 0))
        self.screen.blit(score_text, (500, 10))

            # Draw the instructions
        instructions_text = [
            "Up: Jump",
            "Down: Crouch",
            "Space: Throw Door"
        ]
        
        # Render each instruction and draw it on the screen
        for i, line in enumerate(instructions_text):
            instruction_surface = self.font.render(line, True, (255, 0, 0))
            self.screen.blit(instruction_surface, (10, 10 + i * 25))  # Position each line below the previous

        pygame.display.flip()

    def game_over(self):
        self.screen.fill((0, 0, 0))  # Black background

        game_over_text = self.game_over_font.render("YOU LOST", True, (255, 0, 0))  # Red text
        score_text = self.font.render(f'Score: {self.score}', True, (255, 0, 0))

        text_rect = game_over_text.get_rect(center=(self.WIDTH/2, self.HEIGHT/2))
        score_rect = score_text.get_rect(center=(self.WIDTH/2, 4*self.HEIGHT/5))

        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(score_text, score_rect)
        pygame.display.flip()
        pygame.time.wait(3000)  # Wait for 3 seconds before closing

    def play(self):
        running = True
        while running:
            dt = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.robot.jump()
                    elif event.key == pygame.K_DOWN:
                        self.robot.crouch()
                    elif event.key == pygame.K_SPACE:
                        self.throw_door()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.robot.stand()

            self.spawn_objects()
            self.move_objects()
            if self.check_collisions():
                self.game_over()
                running = False
            self.draw()

            self.monster_timer -= dt
            self.speed_increase_timer += dt
            self.throw_cooldown_timer -= dt
            if self.throw_cooldown_timer <= 0:
                self.throw_cooldown = False
            
            if self.speed_increase_timer >= 3000:  # increase speed every 3 seconds
                self.game_speed += 0.1
                self.speed_increase_timer = 0

            self.clock.tick(60)

        pygame.quit()
        

if __name__ == "__main__":
    game_instance = Game()
    game_instance.play()
