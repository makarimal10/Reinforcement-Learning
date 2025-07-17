import pygame 
import numpy as np
import math
import time

class Sensor:
    def __init__(self, angle):
        self.sensor_x, self.sensor_y = 10, 10
        self.sensor_max = 62
        self.angle = angle
    
    def position(self, x_off, y_off, orientation):
        self.x = int(x_off + self.sensor_x * math.cos(math.radians(orientation + self.angle)))
        self.y = int(y_off + self.sensor_y * math.sin(math.radians(orientation + self.angle)))
        return [self.x, self.y]

    def get_collision(self, color):
        if color == (0, 0, 0):
            if self.sensor_x <= self.sensor_max or self.sensor_y <= self.sensor_max:
                if self.sensor_x <= 0 or self.sensor_y <= 0:
                    pass
                else:
                    self.sensor_x -= 1
                    self.sensor_y -= 1
        else:
            if self.sensor_x >= self.sensor_max or self.sensor_y >= self.sensor_max:
                pass
            else:
                self.sensor_x += 1
                self.sensor_y += 1

        return [self.sensor_x, self.sensor_y]
    

class Agent:
    def __init__(self, width, height, x, y, orientation):
        self.width = width 
        self.height = height
        self.velocity = 10
        self.offset = 15
        self.orientation = orientation
        self.rectangle = [
                    {"x":25, "y":215, "w":120,"h":500},
                    {"x":265, "y":25, "w":420,"h":210},
                    {"x":265, "y":25, "w":200,"h":540},
                    {"x":25, "y":415, "w":400,"h":150},
                    {"x":415, "y":515, "w":210,"h":200}
                    ]
        init_rect = np.random.choice(self.rectangle)
        self.x = y
        self.y = x
        self.sensor = [Sensor(angle) for angle in [-80,-40,-15,0,15,40,80]]
        # self.sensor = [Sensor(angle) for angle in range(-90,90,6)]

    def take_action(self, action):
        self.velocity = 0
        if action == 0:
            self.velocity += 10
            new_x = self.x + self.velocity * math.cos(math.radians(self.orientation))
            new_y = self.y + self.velocity * math.sin(math.radians(self.orientation))
            
            # Check boundaries within the rectangles
            for rect in self.rectangle:
                if (rect["x"] + self.offset <= new_x <= rect["x"] + rect["w"] - self.offset and 
                    rect["y"] + self.offset <= new_y <= rect["y"] + rect["h"] - self.offset):
                    self.x = new_x - 1
                    self.y = new_y - 1
                    break
        elif action == 1:
            self.orientation += 10
        elif action == 2:
            self.orientation -= 10
    
    def init_pos(self):
        self.rectangle = [
                    {"x":25, "y":215, "w":120,"h":500},
                    {"x":565, "y":25, "w":120,"h":210},
                    {"x":265, "y":25, "w":200,"h":240},      #265,25,500,140
                    {"x":25, "y":415, "w":400,"h":150},
                    {"x":415, "y":515, "w":210,"h":200}
                    ]
        init_rect = np.random.choice(self.rectangle)
        self.x = np.random.uniform(init_rect["x"] + self.offset, init_rect["x"] + init_rect["w"] - self.offset)
        self.y = np.random.uniform(init_rect["y"] + self.offset, init_rect["y"] + init_rect["h"] - self.offset)
        self.orientation = np.random.randint(-180, 180)
    
    def init_xy(self, x, y, orientation):
        self.x = x
        self.y = y
        self.orientation = orientation

class Environment:
    def __init__(self, width, height):
        pygame.init()
        self.window = pygame.display.set_mode((width, height))
        self.color = {'grey':(128,128,128), 'white':(255,255,255), 'black':(0,0,0), 'red':(255,0,0),'cream':(240,169,144)}
        self.agent =  Agent(width, height, 150, 510, 120)
        self.target =  Agent(width, height, 500, 100, 0)
        
    def scale_degree(self, degree):
        if -180 <= degree <= -5:
            return math.ceil((degree - 5) / 10)
        elif 5 <= degree <= 180:
            return math.floor((degree + 5) / 10)
        else:
            return 0

    def draw(self):
        self.window.fill(self.color['black'])
        pygame.draw.rect(self.window, self.color['white'], (25,215,120,500))
        pygame.draw.rect(self.window, self.color['white'], (265,25,420,210))    #565,25,120,210
        pygame.draw.rect(self.window, self.color['white'], (265,25,200,540))    #265,25,500,140
        pygame.draw.rect(self.window, self.color['white'], (25,415,400,150))
        pygame.draw.rect(self.window, self.color['white'], (415,515,210,200))
        # pygame.draw.rect(self.window, self.color['black'], (395,235,40,40))     #OBSTACKLE
        pygame.draw.circle(self.window, self.color['cream'], ((self.target.x), self.target.y), 15)           #draw target
        pygame.draw.circle(self.window, self.color['grey'], (self.agent.x, self.agent.y), 15)               #draw robot
        pygame.draw.circle(self.window, self.color['white'],
                          (self.agent.x + 15 * math.cos(math.radians(self.agent.orientation)),
                           self.agent.y + 15 * math.sin(math.radians(self.agent.orientation))), 2)  #draw front robot
        pygame.draw.circle(self.window, (0,255,0),(500,100),2)

    def update_sensor(self):
        coor = []
        sensor_distance = []
        for sensor in self.agent.sensor:
            count = 0
            while count < 62:
                count+=1
                x,y = sensor.position(self.agent.x, self.agent.y, (self.agent.orientation))
                color = self.window.get_at((x, y))
                sensor.get_collision(color)
            dist = int(math.sqrt((x - self.agent.x)**2 + (y - self.agent.y)**2))
            dist = math.floor(dist/20)
            if dist < 1:
                dist = 1
            elif dist > 2:
                dist = 2
            sensor_distance.append(dist)
            coor.append([x,y])
        for x in coor:
            pygame.draw.circle(self.window, self.color['red'], (x[0],x[1]), 2)
        return sensor_distance
        
    def calculate_sensor(self):
        count = 0
        while count < 36:
            lst = []
            release_list = []
            for data in self.update_sensor():
                lst.append(data)
                count += 1
                if count % 5 == 0:
                    nilai = sum(lst)/len(lst)
                    lst.clear()
                    release_list.append(int(nilai))
        return release_list
    
    def distance_orientation(self):
        distance = int(math.sqrt((self.target.x - self.agent.x)**2 + (self.target.y - self.agent.y)**2))
        angle_rad = math.atan2(self.target.y - self.agent.y, self.target.x - self.agent.x)
        angle_deg = math.degrees(angle_rad)
        angle_deg = (angle_deg + 360) % 360
        orientation = (angle_deg - self.agent.orientation) % 360
        if orientation > 180:
            orientation -= 360
        
        return [math.floor(distance/5), self.scale_degree(orientation)]
    
    def x_button(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True 
    
    def display(self):
        pygame.display.flip()


#   REWARD FRONT SENSOR 
def reward1(state):
    reward = 0

    for i in state:
        if i == 1:
            reward += 5 * -3
        elif i == 2:
            reward += 5 * -1 
        elif i == 3:
            reward += 0
    return reward

#   REWARD DISTANCE ORIENTATION
def reward2(state):
    reward_dist = state[0] * -1
    reward_or = abs(state[1]) * -1
    return reward_dist , reward_or


if __name__ == "__main__":
    env = Environment(710, 740)

    running = True
    while running:
        running = env.x_button()

        action = None
        key = pygame.key.get_pressed()
        if key[pygame.K_UP]:
            action = 0
            for sensor in env.agent.sensor:
                sensor.sensor_x, sensor.sensor_y = 10, 10
            time.sleep(0.1)
        if key[pygame.K_LEFT]:
            action = 2
            for sensor in env.agent.sensor:
                sensor.sensor_x, sensor.sensor_y = 10, 10
            time.sleep(0.1)
        if key[pygame.K_RIGHT]:
            action = 1
            for sensor in env.agent.sensor:
                sensor.sensor_x, sensor.sensor_y = 10, 10
            time.sleep(0.1)
        
        if key[pygame.K_q]:
            env.agent.init_pos()
            env.target.init_pos()
            for sensor in env.agent.sensor:
                sensor.sensor_x, sensor.sensor_y = 20, 20
            time.sleep(0.1)

        env.agent.take_action(action)
        env.draw()
        jarak = env.distance_orientation()
        sensor = env.update_sensor()
        state = tuple(sensor + jarak)
        
        # reward = reward1(sensor) + reward2(jarak)
        env.display()
        
        # print("State: ",state)
        print(state)
        # print(reward1(sensor), reward2(jarak))
        
        if jarak[0] < 2:
            # finish = True
            # print("x: ",env.target.x - env.agent.x)
            # print("y: ",env.target.y - env.agent.y)
            env.agent.init_pos()