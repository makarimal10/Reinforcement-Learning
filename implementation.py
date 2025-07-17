import env_implementation as environment
import csv
import numpy as np
import pygame

def write_qtable(file):
    state = []
    with open(file, 'r') as file_csv:
        reader = csv.reader(file_csv)
        for baris in reader:
            val = [float(value) for value in baris]
            state.append(val)
    return state

def get_action(file, state):
    subset = [row for row in file if row[:9] == state]

    if subset:
        for row in subset:
            act1 = row[9]
            act2 = row[10]
            act3 = row[11]
            return [act1,act2,act3]


if __name__ == "__main__":
    env = environment.Environment(710,740)

    qtable = write_qtable('qtable_1.csv')

    start_x, start_y, start_or = 200, 800, 0
    target_x, target_y = 800, 200
    run = True
    agentpos = []

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        env.draw()
        sensor = env.update_sensor()
        dist_or = env.distance_orientation()
        state = env.update_sensor() + env.distance_orientation()
        # env.display()

        action = np.argmax(get_action(qtable,state))
        env.agent.take_action(action)

        env.draw()
        next_state = env.update_sensor() + env.distance_orientation()
        env.display()
        agentpos.append([env.agent.x, env.agent.y])
        
        print("State: ", state)
        print("Action:", action)
        # print("NextS: ", next_state)
        print("Q      ", get_action(qtable,state))
        # time.sleep(0.1)
        if dist_or[0] < 2:
            run = False
            
            csv_reward = "path_5_q_2.csv"
            with open(csv_reward, mode='w', newline='') as file:
                writer_rew = csv.writer(file)
                writer_rew.writerow(['x','y'])
                writer_rew.writerows(agentpos)
    
