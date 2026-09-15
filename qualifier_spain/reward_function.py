import math


class Reward:
    def __init__(self, verbose=False):
        self.first_racingpoint_index = None
        self.verbose = verbose

    def reward_function(self, params):
        if self.first_racingpoint_index is None:
            self.first_racingpoint_index = 0  # 또는 closest_index
            
        ################## HELPER FUNCTIONS ###################

        def dist_2_points(x1, x2, y1, y2):
            return abs(abs(x1-x2)**2 + abs(y1-y2)**2)**0.5

        def closest_2_racing_points_index(racing_coords, car_coords):

            # Calculate all distances to racing points
            distances = []
            for i in range(len(racing_coords)):
                distance = dist_2_points(x1=racing_coords[i][0], x2=car_coords[0],
                                         y1=racing_coords[i][1], y2=car_coords[1])
                distances.append(distance)

            # Get index of the closest racing point
            closest_index = distances.index(min(distances))

            # Get index of the second closest racing point
            distances_no_closest = distances.copy()
            distances_no_closest[closest_index] = 999
            second_closest_index = distances_no_closest.index(
                min(distances_no_closest))

            return [closest_index, second_closest_index]

        def dist_to_racing_line(closest_coords, second_closest_coords, car_coords):
            
            # Calculate the distances between 2 closest racing points
            a = abs(dist_2_points(x1=closest_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=closest_coords[1],
                                  y2=second_closest_coords[1]))

            # Distances between car and closest and second closest racing point
            b = abs(dist_2_points(x1=car_coords[0],
                                  x2=closest_coords[0],
                                  y1=car_coords[1],
                                  y2=closest_coords[1]))
            c = abs(dist_2_points(x1=car_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=car_coords[1],
                                  y2=second_closest_coords[1]))

            # Calculate distance between car and racing line (goes through 2 closest racing points)
            # try-except in case a=0 (rare bug in DeepRacer)
            try:
                distance = abs(-(a**4) + 2*(a**2)*(b**2) + 2*(a**2)*(c**2) -
                               (b**4) + 2*(b**2)*(c**2) - (c**4))**0.5 / (2*a)
            except:
                distance = b

            return distance

        # Calculate which one of the closest racing points is the next one and which one the previous one
        def next_prev_racing_point(closest_coords, second_closest_coords, car_coords, heading):

            # Virtually set the car more into the heading direction
            heading_vector = [math.cos(math.radians(
                heading)), math.sin(math.radians(heading))]
            new_car_coords = [car_coords[0]+heading_vector[0],
                              car_coords[1]+heading_vector[1]]

            # Calculate distance from new car coords to 2 closest racing points
            distance_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                        x2=closest_coords[0],
                                                        y1=new_car_coords[1],
                                                        y2=closest_coords[1])
            distance_second_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                               x2=second_closest_coords[0],
                                                               y1=new_car_coords[1],
                                                               y2=second_closest_coords[1])

            if distance_closest_coords_new <= distance_second_closest_coords_new:
                next_point_coords = closest_coords
                prev_point_coords = second_closest_coords
            else:
                next_point_coords = second_closest_coords
                prev_point_coords = closest_coords

            return [next_point_coords, prev_point_coords]

        def racing_direction_diff(closest_coords, second_closest_coords, car_coords, heading):

            # Calculate the direction of the center line based on the closest waypoints
            next_point, prev_point = next_prev_racing_point(closest_coords,
                                                            second_closest_coords,
                                                            car_coords,
                                                            heading)

            # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
            track_direction = math.atan2(
                next_point[1] - prev_point[1], next_point[0] - prev_point[0])

            # Convert to degree
            track_direction = math.degrees(track_direction)

            # Calculate the difference between the track direction and the heading direction of the car
            direction_diff = abs(track_direction - heading)
            if direction_diff > 180:
                direction_diff = 360 - direction_diff

            return direction_diff

        # Gives back indexes that lie between start and end index of a cyclical list 
        # (start index is included, end index is not)
        def indexes_cyclical(start, end, array_len):

            if end < start:
                end += array_len

            return [index % array_len for index in range(start, end)]

        # Calculate how long car would take for entire lap, if it continued like it did until now
        def projected_time(first_index, closest_index, step_count, times_list):

            # Calculate how much time has passed since start
            current_actual_time = (step_count-1) / 15

            # Calculate which indexes were already passed
            indexes_traveled = indexes_cyclical(first_index, closest_index, len(times_list))

            # Calculate how much time should have passed if car would have followed optimals
            current_expected_time = sum([times_list[i] for i in indexes_traveled])

            # Calculate how long one entire lap takes if car follows optimals
            total_expected_time = sum(times_list)

            # Calculate how long car would take for entire lap, if it continued like it did until now
            try:
                projected_time = (current_actual_time/current_expected_time) * total_expected_time
            except:
                projected_time = 9999

            return projected_time

        #################### RACING LINE ######################

        # Optimal racing line for the Spain track
        # Each row: [x,y,speed,timeFromPreviousPoint]
        racing_track = [[3.48234, 1.43101, 2.63323, 0.07822],
                        [3.28371, 1.45444, 3.17194, 0.06306],
                        [3.0797, 1.469, 4.0, 0.05113],
                        [2.85353, 1.47901, 4.0, 0.0566],
                        [2.59425, 1.48824, 4.0, 0.06486],
                        [2.32024, 1.49562, 4.0, 0.06853],
                        [2.0393, 1.50092, 4.0, 0.07025],
                        [1.7541, 1.5042, 4.0, 0.0713],
                        [1.46589, 1.50561, 4.0, 0.07206],
                        [1.17535, 1.50536, 4.0, 0.07263],
                        [0.88294, 1.50366, 4.0, 0.0731],
                        [0.589, 1.50074, 4.0, 0.07349],
                        [0.29379, 1.49684, 4.0, 0.07381],
                        [-0.00239, 1.4922, 4.0, 0.07406],
                        [-0.30513, 1.48696, 4.0, 0.0757],
                        [-0.60792, 1.48213, 4.0, 0.07571],
                        [-0.91079, 1.47804, 4.0, 0.07572],
                        [-1.21376, 1.47506, 4.0, 0.07575],
                        [-1.51688, 1.47352, 4.0, 0.07578],
                        [-1.8201, 1.47379, 4.0, 0.07581],
                        [-2.12313, 1.47624, 2.64788, 0.11444],
                        [-2.42573, 1.48124, 2.05552, 0.14723],
                        [-2.72786, 1.48916, 1.72188, 0.17552],
                        [-3.02944, 1.50068, 1.50188, 0.20094],
                        [-3.33038, 1.51651, 1.50188, 0.20066],
                        [-3.60902, 1.52186, 1.50188, 0.18556],
                        [-3.87168, 1.50357, 1.50188, 0.17531],
                        [-4.11539, 1.45194, 1.50188, 0.16588],
                        [-4.33733, 1.35846, 1.50188, 0.16034],
                        [-4.53046, 1.21327, 1.58122, 0.15281],
                        [-4.69199, 1.0214, 1.59797, 0.15696],
                        [-4.81111, 0.78566, 1.61412, 0.16363],
                        [-4.87329, 0.52231, 1.63043, 0.16597],
                        [-4.87351, 0.25872, 1.64394, 0.16034],
                        [-4.81823, 0.01075, 1.65736, 0.15329],
                        [-4.71496, -0.21477, 1.6709, 0.14845],
                        [-4.56866, -0.41403, 1.67754, 0.14736],
                        [-4.38138, -0.58284, 1.95256, 0.12913],
                        [-4.16357, -0.72532, 2.15993, 0.1205],
                        [-3.91959, -0.84274, 2.44728, 0.11064],
                        [-3.65342, -0.93765, 2.87578, 0.09826],
                        [-3.36629, -1.01467, 3.52677, 0.08429],
                        [-3.07189, -1.07646, 3.76994, 0.07979],
                        [-2.77613, -1.12372, 4.0, 0.07488],
                        [-2.47968, -1.15854, 4.0, 0.07462],
                        [-2.18303, -1.18293, 4.0, 0.07441],
                        [-1.88648, -1.19883, 4.0, 0.07424],
                        [-1.59076, -1.20709, 4.0, 0.07396],
                        [-1.29889, -1.20815, 4.0, 0.07297],
                        [-1.01214, -1.20262, 4.0, 0.0717],
                        [-0.72937, -1.19106, 4.0, 0.07075],
                        [-0.44972, -1.17389, 4.0, 0.07005],
                        [-0.17257, -1.15145, 3.81098, 0.07296],
                        [0.10249, -1.12404, 3.25822, 0.08484],
                        [0.37578, -1.09191, 2.88856, 0.09526],
                        [0.64755, -1.05528, 2.62055, 0.10465],
                        [0.91463, -1.01486, 2.62055, 0.10308],
                        [1.1814, -0.98182, 2.62055, 0.10258],
                        [1.44748, -0.96024, 2.62055, 0.10187],
                        [1.71233, -0.95404, 2.62055, 0.10109],
                        [1.97524, -0.96699, 2.61444, 0.10068],
                        [2.2353, -1.00286, 2.14071, 0.12263],
                        [2.49235, -1.05901, 1.85615, 0.14175],
                        [2.74579, -1.13621, 1.66026, 0.15957],
                        [2.99472, -1.23552, 1.51411, 0.17701],
                        [3.24267, -1.36097, 1.39625, 0.19902],
                        [3.49566, -1.46086, 1.3, 0.20923],
                        [3.75189, -1.52405, 1.3, 0.203],
                        [4.00606, -1.54158, 1.3, 0.19598],
                        [4.24958, -1.50729, 1.3, 0.18918],
                        [4.47127, -1.41793, 1.3, 0.18386],
                        [4.65753, -1.2722, 1.3, 0.18192],
                        [4.79036, -1.06965, 1.66631, 0.14536],
                        [4.88294, -0.83501, 1.83688, 0.13732],
                        [4.93568, -0.57382, 1.90375, 0.13997],
                        [4.94899, -0.29102, 1.82278, 0.15532],
                        [4.92523, 0.00726, 1.74468, 0.1715],
                        [4.86331, 0.28978, 1.74468, 0.16578],
                        [4.76701, 0.54449, 1.74468, 0.15608],
                        [4.63953, 0.76997, 1.74468, 0.14846],
                        [4.4837, 0.96442, 1.74468, 0.14282],
                        [4.30266, 1.12494, 1.74468, 0.13868],
                        [4.10177, 1.24684, 1.88359, 0.12475],
                        [3.89276, 1.33424, 2.06053, 0.10995],
                        [3.68481, 1.39321, 2.29768, 0.09407]]

        ################## INPUT PARAMETERS ###################

        # Read all input parameters
        all_wheels_on_track = params['all_wheels_on_track']
        x = params['x']
        y = params['y']
        distance_from_center = params['distance_from_center']
        is_left_of_center = params['is_left_of_center']
        heading = params['heading']
        progress = params['progress']
        steps = params['steps']
        speed = params['speed']
        steering_angle = params['steering_angle']
        track_width = params['track_width']
        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        is_offtrack = params['is_offtrack']

        ############### OPTIMAL X,Y,SPEED,TIME ################

        # Get closest indexes for racing line (and distances to all points on racing line)
        closest_index, second_closest_index = closest_2_racing_points_index(
            racing_track, [x, y])

        # Get optimal [x, y, speed, time] for closest and second closest index
        optimals = racing_track[closest_index]
        optimals_second = racing_track[second_closest_index]

        # first racingpoint of episode for later
        if self.verbose == True:
            self.first_racingpoint_index = 0 # this is just for testing purposes
        if steps == 1:
            self.first_racingpoint_index = closest_index

        ################ REWARD AND PUNISHMENT ################

        ## Define the default reward ##
        reward = 1

        ## Reward if car goes close to optimal racing line ##
        DISTANCE_MULTIPLE = 1
        dist = dist_to_racing_line(optimals[0:2], optimals_second[0:2], [x, y])
        distance_reward = max(1e-3, 1 - (dist/(track_width*0.5)))
        reward += distance_reward * DISTANCE_MULTIPLE

        ## Reward if speed is close to optimal speed ##
        SPEED_DIFF_NO_REWARD = 1
        SPEED_MULTIPLE = 2
        speed_diff = abs(optimals[2]-speed)
        if speed_diff <= SPEED_DIFF_NO_REWARD:
            # we use quadratic punishment (not linear) bc we're not as confident with the optimal speed
            # so, we do not punish small deviations from optimal speed
            speed_reward = (1 - (speed_diff/(SPEED_DIFF_NO_REWARD))**2)**2
        else:
            speed_reward = 0
        reward += speed_reward * SPEED_MULTIPLE

        # Reward if less steps
        REWARD_PER_STEP_FOR_RAPID_TIME = 1 
        STANDARD_TIME = 37
        RAPID_TIME = 27
        times_list = [row[3] for row in racing_track]
        projected_time = projected_time(self.first_racingpoint_index, closest_index, steps, times_list)
        try:
            steps_prediction = projected_time * 15 + 1
            reward_prediction = max(1e-3, (-REWARD_PER_STEP_FOR_RAPID_TIME*(RAPID_TIME) /
                                           (STANDARD_TIME-RAPID_TIME))*(steps_prediction-(STANDARD_TIME*15+1)))
            steps_reward = min(REWARD_PER_STEP_FOR_RAPID_TIME, reward_prediction / steps_prediction)
        except:
            steps_reward = 0
        reward += steps_reward

        # Zero reward if obviously wrong direction (e.g. spin)
        direction_diff = racing_direction_diff(
            optimals[0:2], optimals_second[0:2], [x, y], heading)
        if direction_diff > 30:
            reward = 1e-3
            
        # Zero reward of obviously too slow
        speed_diff_zero = optimals[2]-speed
        if speed_diff_zero > 0.5:
            reward = 1e-3
            
        ## Incentive for finishing the lap in less steps ##
        REWARD_FOR_RAPID_TIME = 1500 # should be adapted to track length and other rewards
        STANDARD_TIME = 37  # seconds (time that is easily done by model)
        RAPID_TIME = 27  # seconds (best time of 1st place on the track)
        if progress == 100:
            finish_reward = max(1e-3, (-REWARD_FOR_RAPID_TIME /
                      (15*(STANDARD_TIME-RAPID_TIME)))*(steps-STANDARD_TIME*15))
        else:
            finish_reward = 0
        reward += finish_reward
        
        ## Zero reward if off track ##
        if all_wheels_on_track == False:
            reward = 1e-3

        ####################### VERBOSE #######################
        
        if self.verbose == True:
            print("Closest index: %i" % closest_index)
            print("Distance to racing line: %f" % dist)
            print("=== Distance reward (w/out multiple): %f ===" % (distance_reward))
            print("Optimal speed: %f" % optimals[2])
            print("Speed difference: %f" % speed_diff)
            print("=== Speed reward (w/out multiple): %f ===" % speed_reward)
            print("Direction difference: %f" % direction_diff)
            print("Predicted time: %f" % projected_time)
            print("=== Steps reward: %f ===" % steps_reward)
            print("=== Finish reward: %f ===" % finish_reward)
            
        #################### RETURN REWARD ####################
        
        # Always return a float value
        return float(reward)


reward_object = Reward() # add parameter verbose=True to get noisy output for testing


def reward_function(params):
    return reward_object.reward_function(params)