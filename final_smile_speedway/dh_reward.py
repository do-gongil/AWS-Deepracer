import math

def reward_function(params):

    # 파라미터 추출
    all_wheels_on_track = params['all_wheels_on_track']
    speed = params['speed']
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']
    is_left_of_center = params['is_left_of_center']
    progress = params['progress']
    steps = params['steps']
    reward = 1.0

    # 1. 트랙 이탈 감점
    if not all_wheels_on_track:
        return 1e-3
    
    # matthewsuntup
    # Give higher reward if the car is closer to centre line and vice versa
    # 0 if you're on edge of track, 1 if you're centre of track
    reward += 1.5 - (distance_from_center / (track_width / 2)) ** (1 / 4)

    # 4. 속도 보너스 (고속 우대)
    SPEED_THRESHOLD = 2.9
    if speed >= SPEED_THRESHOLD:
        reward += 2.0

    # 5. 방향 일치 보너스
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]
    track_direction = math.degrees(math.atan2(
        next_point[1] - prev_point[1],
        next_point[0] - prev_point[0]))
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff
    DIRECTION_THRESHOLD = 10.0
    if direction_diff < DIRECTION_THRESHOLD:
        reward += 1.0
    else:
        reward *= 0.7

    return float(reward)
    
