# deepracer_raceline

AWS DeepRacer 대회 출전 코드

2025 춘천 AWS DeepRacer Championship 본선 11위.

## Reward functions

예선과 본선은 **트랙이 달라 보상함수 다릅니다.** 서로 호환되지 않습니다.

### `qualifier_spain/reward_function.py` — 예선
- 359줄, 2025-09-10
- **Spain track** 최적 레이싱 라인 **84점** 내장
- `class Reward` 구조. 각 점은 `[x, y, speed, timeFromPreviousPoint]`
- 현재 위치에서 가장 가까운 레이싱 라인 2점을 찾아 이탈 거리·속도 차·진행 방향으로 보상 산출

### `final_smile_speedway/reward_function.py` — 본선 최종
- 534줄, 2025-09-17
- **Smile Speedway** 최적 레이싱 라인 **257점** 내장 (예선 대비 3배 정밀)
- 예선과 같은 `class Reward` 구조이나 라인 해상도와 속도 프로파일이 재산출됨

### `final_smile_speedway/rnd2_reward.py` — 본선 2라운드 (장애물)
- 208줄, 2025-09-15
- **접근법이 다릅니다.** 레이싱 라인 추종이 아니라 `objects_location` 기반 **장애물 회피** 보상함수
- 정적 장애물이 배치된 라운드용

### `final_smile_speedway/dh_reward.py` — 간이 버전
- 48줄, 2025-09-14
- `all_wheels_on_track` · 중앙선 거리 · 속도만 쓰는 최소 구현. 베이스라인 비교용

## Analysis

`analysis/` — A to Z Speedway 트랙 분석 (2025-08)

| 파일 | 내용 |
|---|---|
| `a_to_z_track_waypoints.png` | 트랙 waypoint 분포 |
| `a_to_z_record_line.png` | 기록 주행 라인 |
| `raceline.png` | 산출된 최적 레이싱 라인 |
| `speed.png` | 구간별 목표 속도 |
| `s_v_action.png` | 액션 스페이스 (조향각 × 속도) |
| `s_v선도.png` | s-v 선도 |

## Tools

`tools/visualization.py` — 보상함수에 내장된 `racing_track` 배열을 matplotlib 으로 플로팅. 레이싱 라인과 구간 속도를 눈으로 확인하는 용도입니다.

## Media

`media/aws_예선.mp4` · `media/dh-best.mp4` — 본인 주행 기록

## Not in this repository

| 항목 | 사유 |
|---|---|
| 학습 모델 `*.tar.gz` 4개 (87MB) | 용량. 재학습으로 재생성 가능 |
| `RaceLine_Speed_ActionSpace.ipynb` / `.py` | **서드파티** — ai-castle 강의자료. 원본은 [dgnzlz/Capstone_AWS_DeepRacer](https://github.com/dgnzlz/Capstone_AWS_DeepRacer/tree/master/Compute_Speed_And_Actions), 내부에 Eric Koch (2014) 저작권 고지 포함 |
| `matthew.py` | **서드파티** — USYD 2020 Qualifier, Team IndestruciRacer (Matthew Suntup, Georgia Markham, Ashan Abey) |
| `Tandetzky.py` | **서드파티** — DeepRacer 커뮤니티 공개 보상함수 |
| `Reward_Signal_Design_for_Autonomous_Racing.pdf` | 저작권 논문 |
| 트랙 waypoint `.npy` | [aws-deepracer-community/deepracer-race-data](https://github.com/aws-deepracer-community/deepracer-race-data/tree/main/raw_data/tracks) 에서 받을 수 있습니다 |

## Notes

- 보상함수의 `class Reward` 구조는 DeepRacer 커뮤니티에서 널리 쓰이는 레이싱 라인 추종 템플릿을 따릅니다. 트랙별 레이싱 라인 좌표, 속도 프로파일, 가중치는 직접 산출·조정한 것입니다.
- 최적 레이싱 라인 산출에는 위에 링크한 서드파티 노트북을 사용했습니다. 이 저장소에는 그 **결과물(좌표 배열)만** 보상함수 안에 들어 있습니다.
