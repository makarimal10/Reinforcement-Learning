import pygame 
import numpy as np
import math
import time

class Sensor:
    def __init__(self, angle):
        self.sensor_x, self.sensor_y = 15, 15
        self.sensor_max = 153
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
    def __init__(self, width, height, target=False):
        self.width = width 
        self.height = height
        self.velocity = 10
        self.offset = 13
        self.orientation = np.random.randint(-9, 10) * 20
        self.rectangle = [
            # {"x":50, "y":260, "w":180,"h":290},
            # {"x":50, "y":470, "w":210,"h":280},
            {"x":50, "y":410, "w":450,"h":210},
            {"x":265, "y":50, "w":480,"h":120},
            {"x":380, "y":50, "w":390,"h":240},
            {"x":380, "y":50, "w":190,"h":570},
            {"x":500, "y":530, "w":258,"h":210}
            ]
        init_rect = np.random.choice(self.rectangle)
        if not target:
            self.x = np.random.uniform(init_rect["x"] + self.offset, 
                                       init_rect["x"] + init_rect["w"] - self.offset)
            self.y = np.random.uniform(init_rect["y"] + self.offset,
                                       init_rect["y"] + init_rect["h"] - self.offset)
        else:
            self.x = 250
            self.y = 500
        self.sensor = [Sensor(angle) for angle in [-90,-70,-50,-30,-10,10,30,50,70,90]]          #10 sensor
        # self.sensor = [Sensor(angle) for angle in [-90,-70,-45,-20,0,20,45,70,90]]          #9 sensor        
        # self.sensor = [Sensor(angle) for angle in [-75,-50,-25,0,25,50,75]]          #7 sensor
        # self.sensor = [Sensor(angle) for angle in [-90,-60,-30,0,30,60,90]]          #7 sensor
        # self.sensor = [Sensor(angle) for angle in [-75,-45,-15,15,45,75]]

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
        # self.x += self.velocity * math.cos(math.radians(self.orientation))
        # self.y += self.velocity * math.sin(math.radians(self.orientation))
    
    def init_pos(self):
        self.rectangle = [
            # {"x":50, "y":260, "w":180,"h":290},
            # {"x":50, "y":470, "w":210,"h":280},
            {"x":50, "y":410, "w":450,"h":210},
            {"x":265, "y":50, "w":480,"h":120},
            {"x":380, "y":50, "w":390,"h":240},
            {"x":380, "y":50, "w":190,"h":570},
            {"x":500, "y":530, "w":258,"h":210}
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
        # self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((width, height))
        self.color = {'grey':(128,128,128), 'white':(255,255,255), 'black':(0,0,0), 'red':(255,0,0),'cream':(240,169,144)}
        self.agent =  Agent(width, height)
        self.target =  Agent(width, height, target=True)
        
    def draw(self):
        self.window.fill(self.color['black'])
        # pygame.draw.rect(self.window, self.color['white'], (50,260,180,290))
        # pygame.draw.rect(self.window, self.color['white'], (50,470,210,280))        #tanpa meja vertikal bawah ac
        pygame.draw.rect(self.window, self.color['white'], (50,410,450,210))
        pygame.draw.rect(self.window, self.color['white'], (265,50,480,120))
        pygame.draw.rect(self.window, self.color['white'], (380,50,390,240))
        pygame.draw.rect(self.window, self.color['white'], (380,50,190,570))
        pygame.draw.rect(self.window, self.color['white'], (500,530,258,210))
        pygame.draw.circle(self.window, self.color['cream'], ((self.target.x), self.target.y), 15)           #draw target
        pygame.draw.circle(self.window, self.color['grey'], (self.agent.x, self.agent.y), 15)               #draw robot
        pygame.draw.circle(self.window, self.color['white'],
                          (self.agent.x + 13 * math.cos(math.radians(self.agent.orientation)),
                           self.agent.y + 13 * math.sin(math.radians(self.agent.orientation))), 1)  #draw front robot

    def update_sensor(self):
        coor = []
        sensor_distance = []
        for sensor in self.agent.sensor:
            count = 0
            while count < 153:
                count+=1
                x,y = sensor.position(self.agent.x, self.agent.y, self.agent.orientation)
                color = self.window.get_at((x, y))
                sensor.get_collision(color)
            dist = int(math.sqrt((x - self.agent.x)**2 + (y - self.agent.y)**2))
            dist = math.ceil(dist/150)
            if dist == 1:
                dist = 1
            elif dist > 1:
                dist = 0
            sensor_distance.append(dist)
            coor.append([x,y])
        
        for x in coor:
            pygame.draw.circle(self.window, self.color['red'], (x[0],x[1]), 2)
        return sensor_distance
    
    def calculate_sensor(self):
        count = 0
        while count < 12:
            lst = []
            release_list = []
            for data in self.update_sensor():
                lst.append(data)
                count += 1
                if count % 2 == 0:
                    nilai = sum(lst)/len(lst)
                    lst.clear()
                    release_list.append(math.floor(nilai))
        return release_list
    
    def distance_orientation(self):
        distance = int(math.sqrt((self.target.x - self.agent.x)**2 + (self.target.y - self.agent.y)**2))
        if distance < 14 :
            distance = 14
        angle_rad = math.atan2(self.target.y - self.agent.y, self.target.x - self.agent.x)
        angle_deg = math.degrees(angle_rad)
        angle_deg = (angle_deg + 360) % 360
        orientation = (angle_deg - self.agent.orientation) % 360
        if orientation > 180:
            orientation -= 360
        return[distance, self.scale_degree(int(orientation))]
        # return [distance, self.scale_degree_9(orientation), self.scale_degree_9(int(orientation)), orientation, int(orientation)]
        
    def scale_degree(self, degree):
        if -180 <= degree <= -5:
            return math.ceil((degree - 5) / 10)
        elif 5 <= degree <= 180:
            return math.floor((degree + 5) / 10)
        else:
            return 0
    
    def scale_degree_v2(self, degree):
        if -180 <= degree <= -10:
            return math.ceil((degree - 10) / 20)
        elif 10 <= degree <= 180:
            return math.floor((degree + 10) / 20)
        else:
            return 0
    
    def scale_degree_v3(self, degree):
        if -180 <= degree <= -15:
            return math.ceil((degree - 15) / 30)
        elif 15 <= degree <= 180:
            return math.floor((degree + 15) / 30)
        else:
            return 0
        
    def x_button(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True 
    
    def display(self):
        pygame.display.flip()
        # pygame.time.Clock().tick(30)

    '''
    TRAINING PACKAGE
    '''
    def step(self, action):
        target = False
        done = False
        for sensor in self.agent.sensor:
            sensor.sensor_x, sensor.sensor_y = 10,10
        
        self.draw()
        obs = self.update_sensor()
        distance = self.distance_orientation()
        state = obs + distance
        self.display()

        self.draw()
        self.agent.take_action(action)
        obs = self.update_sensor()
        distance = self.distance_orientation()
        self.display()

        if distance[0] < 40 and distance[1] <= 2:
            reward = 1000
            done = True
            target = True
        else:
            if 1 in obs:
                # reward = -10
                reward = reward1(obs) + sum(reward2(distance))
            else:
                reward = sum(reward2(distance))
        
        return state, reward, done, target
    
    def reset(self):
        for sensor in self.agent.sensor:
            sensor.sensor_x, sensor.sensor_y = 10, 10
        self.agent.init_pos()
        self.target.init_pos()

        obs = self.update_sensor()
        distance = self.distance_orientation()
        state = obs + distance

        return state


def reward1(state):
    reward = 0
    for i in state:
        if i == 1:
            reward += -4
        else:
            reward += 0
    
    return reward

#   REWARD DISTANCE ORIENTATION
def reward2(state):
    reward_dist = state[0] * -1
    reward_or = abs(state[1]) * -1
    return [reward_dist, reward_or]

if __name__ == "__main__":
    env = Environment(820, 790)

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
                sensor.sensor_x, sensor.sensor_y = 10, 10
            time.sleep(0.1)

        env.agent.take_action(action)
        env.draw()
        jarak = env.distance_orientation()
        sensor = env.update_sensor()
 
        state = sensor + jarak
        
        # reward = reward1(sensor) + sum(reward2(jarak))
        env.display()
        
        if jarak[0] < 40 and jarak[1] <= 2:
            reward = 100
            done = True
            target = True
        else:
            if 1 in sensor:
                # reward = -10
                reward = reward1(sensor) + sum(reward2(jarak))
            else:
                reward = sum(reward2(jarak))

        print("State: ",state)
        # print("bagi 2 ",env.calculate_sensor())
        # print("Reward ", reward1(sensor),reward2(jarak))
        print("Reward ", reward)

        # if jarak[0] < 5:
            # env.agent.init_pos()