import math

def reward_function(params):
    """
    Smile Speedway 장애물 회피 최적화 보상함수

    트랙: Smile Speedway (반시계방향)
    목표: 트랙 이탈과 장애물 충돌 없이 완주
    학습 시간: 2시간 제한
    알고리즘: PPO + Discrete Action Space

    장애물 위치:
    - Obstacle 1: 25% 바깥레인
    - Obstacle 2: 50% 안쪽레인  
    - Obstacle 3: 75% 바깥레인
    """

    # 필수 파라미터 추출
    all_wheels_on_track = params['all_wheels_on_track']
    distance_from_center = params['distance_from_center']
    track_width = params['track_width']
    speed = params['speed']
    steering_angle = params['steering_angle']
    heading = params['heading']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    progress = params['progress']
    is_crashed = params.get('is_crashed', False)
    is_offtrack = params.get('is_offtrack', False)

    # 장애물 관련 파라미터
    objects_location = params.get('objects_location', [])
    objects_left_of_center = params.get('objects_left_of_center', [])
    is_left_of_center = params.get('is_left_of_center', False)
    closest_objects = params.get('closest_objects', [0, 0])
    x, y = params.get('x', 0), params.get('y', 0)

    # =============================================
    # 1. 즉시 실패 조건 확인
    # =============================================
    if is_crashed or is_offtrack or not all_wheels_on_track:
        return float(1e-3)

    # =============================================
    # 2. 기본 보상 초기화
    # =============================================
    reward = 1e-3

    # =============================================
    # 3. 트랙 중심선 유지 보상 (안전한 주행)
    # =============================================
    center_variance = distance_from_center / track_width

    if center_variance <= 0.1:       # 트랙 중심 10% 이내
        track_reward = 2.5
    elif center_variance <= 0.25:    # 트랙 중심 25% 이내
        track_reward = 2.0
    elif center_variance <= 0.4:     # 트랙 중심 40% 이내
        track_reward = 1.5
    elif center_variance <= 0.5:     # 트랙 경계 내
        track_reward = 1.0
    else:                            # 트랙 경계 근처 (위험)
        track_reward = 0.1

    # =============================================
    # 4. 방향 정렬 보상 (효율적인 주행)
    # =============================================
    if len(waypoints) > closest_waypoints[1]:
        next_point = waypoints[closest_waypoints[1]]
        prev_point = waypoints[closest_waypoints[0]]

        # 트랙 방향 계산
        track_direction = math.atan2(next_point[1] - prev_point[1], 
                                   next_point[0] - prev_point[0])
        track_direction = math.degrees(track_direction)

        # 헤딩 차이 계산
        direction_diff = abs(track_direction - heading)
        if direction_diff > 180:
            direction_diff = 360 - direction_diff

        # 방향 정렬 보상
        if direction_diff <= 10.0:
            direction_reward = 2.0
        elif direction_diff <= 15.0:
            direction_reward = 1.5
        elif direction_diff <= 25.0:
            direction_reward = 1.0
        else:
            direction_reward = 0.5
    else:
        direction_reward = 1.0

    # =============================================
    # 5. 속도 최적화 보상 (시간 효율성) action space에 따라 설정
    # =============================================
    # 2시간 내 완주를 위한 적극적인 속도 보상
    if 2.4 <= speed <= 3.5:         # 최적 속도 구간
        speed_reward = 2.0
    elif 1.8 <= speed < 2.4:        # 안전한 속도
        speed_reward = 1.5
    elif 1.2 <= speed < 1.8:        # 보수적인 속도
        speed_reward = 1.2
    elif speed >= 3.0:               # 과속 (제어 어려움)
        speed_reward = 1.0
    else:                            # 너무 느림
        speed_reward = 0.8

    # =============================================
    # 6. 장애물 회피 보상 (핵심 기능)
    # =============================================
    obstacle_reward = 2.0  # 기본값

    if objects_location and len(closest_objects) >= 2:
        try:
            # 가장 가까운 앞쪽 장애물
            next_object_index = closest_objects[1]
            if next_object_index < len(objects_location):
                next_object_loc = objects_location[next_object_index]

                # 장애물까지의 거리
                distance_to_obstacle = math.sqrt(
                    (x - next_object_loc[0])**2 + (y - next_object_loc[1])**2
                )

                # 같은 레인 여부 확인
                if (next_object_index < len(objects_left_of_center)):
                    is_same_lane = (objects_left_of_center[next_object_index] == 
                                  is_left_of_center)

                    if is_same_lane:
                        # 같은 레인의 장애물에 대한 거리별 보상
                        if distance_to_obstacle < 0.5:
                            obstacle_reward = 1e-3    # 충돌 임박
                        elif distance_to_obstacle < 1.0:
                            obstacle_reward = 0.3     # 매우 위험
                        elif distance_to_obstacle < 1.5:
                            obstacle_reward = 0.6     # 위험
                        elif distance_to_obstacle < 2.0:
                            obstacle_reward = 1.2     # 주의
                        else:
                            obstacle_reward = 2.0     # 안전
                    else:
                        # 다른 레인의 장애물은 상대적으로 안전
                        obstacle_reward = 1.8

        except (IndexError, TypeError):
            obstacle_reward = 1.5  # 예외 발생 시 중간값

    # =============================================
    # 7. 스티어링 제어 보상 (안정성)
    # =============================================
    abs_steering = abs(steering_angle)
    if abs_steering <= 10.0:
        steering_reward = 1.5
    elif abs_steering <= 20.0:
        steering_reward = 1.2
    elif abs_steering <= 26.0:
        steering_reward = 1.0
    else:
        steering_reward = 0.7  # 과도한 스티어링

    # =============================================
    # 8. 진행률 기반 보상 (완주 동기부여)
    # =============================================
    if progress >= 97.0:
        progress_bonus = 3.0      # 완주 임박
    elif progress >= 90.0:
        progress_bonus = 2.0      # 거의 완주
    elif progress >= 75.0:
        progress_bonus = 1.5      # 3/4 지점 통과
    elif progress >= 50.0:
        progress_bonus = 1.2      # 중간 지점 통과
    elif progress >= 25.0:
        progress_bonus = 1.0      # 1/4 지점 통과
    else:
        progress_bonus = 0.5      # 초기 단계

    # =============================================
    # 9. 최종 보상 계산 (가중 평균)
    # =============================================
    final_reward = (
        3.0 * track_reward +       # 트랙 유지 (핵심)
        2.5 * direction_reward +   # 방향 정렬 (효율성)
        2.0 * speed_reward +       # 속도 최적화 (시간)
        5.0 * obstacle_reward +    # 장애물 회피 (최우선)
        1.5 * steering_reward +    # 안정성
        1.0 * progress_bonus       # 진행 동기
    ) / 15.0  # 정규화

    # =============================================
    # 10. 특별 보너스 및 조정   퍼플렉시티가 시켰음
    # =============================================
    # 완주 근접 시 추가 보상
    if progress > 90.0:
        final_reward *= 1.3
    elif progress > 75.0:
        final_reward *= 1.15
    elif progress > 50.0:
        final_reward *= 1.05

    # 안전한 고속 주행에 대한 보너스
    if speed >= 2.5 and center_variance <= 0.2 and obstacle_reward >= 1.5:
        final_reward *= 1.2

    # 보상 범위 제한
    final_reward = max(1e-3, min(final_reward, 20.0))

    return float(final_reward)