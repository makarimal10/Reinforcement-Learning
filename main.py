import csv
import environment
import numpy as np
import pygame
import time

QTABLE = {}
#create q table
for i in range(1,3):
    for ii in range(1,3):
        for iii in range(1,3):
            for iv in range(1,3):
                for v in range(1,3):
                    for vi in range(1,3):
                        for vii in range(1,3):
                            # for viii in range(1,3):
                                # for ix in range(1,3):
                                    for x in range(0,185):
                                        for xi in range(-18,19):
                                            QTABLE[i, ii, iii, iv, v, vi, vii, x, xi] = [np.random.uniform(-1,0) for action in range(3)]

#   REWARD FRONT SENSOR 
def reward1(state):
    reward = 0
    for i in state:
        if i == 1:
            reward += 500 * -1
        else:
            reward += 0
    return reward

#   REWARD DISTANCE ORIENTATION
def reward2(state):
    # distance = map(state[0],0,250,1,100)
    # orientation = map(abs(state[1]),0,18,1,100)
    # reward_dist = distance * -1
    # reward_or = orientation * -1
    reward_dist = state[0] * -3
    reward_or = abs(state[1]*2) * -1

    return [reward_dist, reward_or]

def map(value, from_low, from_high, to_low, to_high):
    return int((value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low)

if __name__ == "__main__":
    env = environment.Environment(710, 740)
    
    #best = lr,dr : 0.9, 0.15
    learning_rate, discount = 0.9, 0.15
    FINISH_REWARD, COLLISION_REWARD, MOVE_REWARD = 100, -100000, -10
    sum_reward = 0
    sum_q = 0
    all_reward = []
    EPISODE, MAX_EPISODE = 0, 2000
    EPSILON, EPSILON_DECREASING = 0.9, 0.9997
    run = True
    start_time = time.time()
    state_last = 0
    qtable_save = 0

    while run:
        key = pygame.key.get_pressed()
        if key[pygame.K_q]:
            env.agent.init_pos()
        if key[pygame.K_0]:
            env.target.init_pos()

        env.draw()
        sensor = env.update_sensor()
        dist_or = env.distance_orientation()
        state = tuple(sensor + dist_or)
        
        if state == state_last:
            action = np.random.randint(0,3)       #EXPLORING
        else:
            if np.random.random() > EPSILON:
                action = np.random.randint(0,3)
            else:
                action = np.argmax(QTABLE[state])     #EXPLOIATING
        
        env.agent.take_action(action)

        env.draw()
        next_state = tuple(env.update_sensor() + env.distance_orientation())
        
        current_q = QTABLE[state][action]

        if dist_or[0] < 5 and dist_or[1] <= 1:
            reward = FINISH_REWARD
        else:
            if state_last == state and action == 0:
                reward = COLLISION_REWARD
            else:
                if sum(sensor) < 14:
                    dist = reward2(dist_or)
                    reward = reward1(sensor) + dist[0]
                else:
                    # reward = reward2(dist_or)
                    # reward = MOVE_REWARD
                    reward = sum(reward2(dist_or))
        
        if reward ==  FINISH_REWARD:
            q = FINISH_REWARD
        else:
            q = (1-learning_rate) * current_q + learning_rate * (reward + (discount * np.max(QTABLE[next_state])))

        #   alpha = learning rate, gamma = factor discount
        # q2 = current_q + (learning_rate * (reward + ((discount * np.max([QTABLE[next_state]])) - current_q)))
        # q = current_q + reward
        QTABLE[state][action] = q
        
        state_last = state
        sum_reward += reward
        sum_q += q
        env.display()

        print("EPS:  ", EPISODE)
        print("ACT   ", action)
        print("State ", state)
        print("Q     ", QTABLE[state])
        print("Next Q", QTABLE[next_state])
                
        #finish
        if dist_or[0] < 5 and dist_or[1] <= 1:
            end_time = time.time()
            time_eps = end_time - start_time
            EPISODE += 1
            EPSILON *= EPSILON_DECREASING
            all_reward.append([EPISODE, sum_reward, sum_q, time_eps, EPSILON])
            
            print(time_eps)
            print("EPS: ",EPISODE)
            sum_reward = 0
            sum_q = 0
            env.agent.init_pos()
            env.target.init_pos()
            for sensor in env.agent.sensor:
                sensor.sensor_x, sensor.sensor_y = 10, 10
            continue
        else:
            finish = False

        run = env.x_button()

        if EPISODE == MAX_EPISODE or run == False:
            run = False
            #SAVE QTABLE TO CSV
            csv_qtable = "qtable_2.csv"
            with open(csv_qtable, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['State1', 'State2', 'State3', 'State4', 'State5','State6','State7', 'Action1', 'Action2', 'Action3'])
                for state, actions in QTABLE.items():
                    row = list(state) + actions
                    writer.writerow(row)
            
            csv_reward = "reward_1.csv"
            with open(csv_reward, mode='w', newline='') as file:
                writer_rew = csv.writer(file)
                writer_rew.writerow(['Episode','Reward,','Q','Time','Epsilon'])
                writer_rew.writerows(all_reward)
            