# AWS-Deepracer

AWS DeepRacer 대회 출전 코드

2025 춘천 AWS DeepRacer Championship - Team T.V. - **예선 25위, 본선 11위.**

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
- 레이싱 라인 추종이 아니라 `objects_location` 기반 **장애물 회피** 보상함수
- 정적 장애물이 배치된 라운드용

### `final_smile_speedway/dh_reward.py` — 간이 버전
- 48줄, 2025-09-14
- `all_wheels_on_track` · 중앙선 거리 · 속도 · 진행 방향만 쓰는 최소 구현. 베이스라인 비교용

### 파라미터

코드에 하드코딩된 상수·가중치입니다. 각 파일에서 그대로 옮겼습니다.

**레이싱 라인 추종** — `qualifier_spain/reward_function.py`, `final_smile_speedway/reward_function.py` (두 파일 상수 동일, 레이싱 라인 배열만 다름)

| 상수 / 조건 | 값 | 역할 |
|---|---|---|
| 기본 보상 | `1` | 매 스텝 시작값 |
| `DISTANCE_MULTIPLE` | `1` | 레이싱 라인 거리 보상 `max(1e-3, 1 − dist / (track_width·0.5))` 의 가중치 |
| `SPEED_DIFF_NO_REWARD` | `1` | 최적 속도와의 차가 이 값(m/s)을 넘으면 속도 보상 0. 이내면 `(1 − (diff/1)²)²` |
| `SPEED_MULTIPLE` | `2` | 속도 보상 가중치 |
| `REWARD_PER_STEP_FOR_RAPID_TIME` / `_FASTEST_TIME` | `1` | 예상 랩타임 기반 스텝 보상의 상한 |
| `STANDARD_TIME` | `37` s | 모델이 쉽게 내는 기준 랩타임 |
| `RAPID_TIME` / `FASTEST_TIME` | `27` s | 목표 랩타임 |
| `REWARD_FOR_RAPID_TIME` / `_FASTEST_TIME` | `1500` | `progress == 100` 시 완주 보상 `max(1e-3, −1500/(15·(37−27)) · (steps − 37·15))` |
| 스텝 주기 | `15` 스텝/s | `steps` → 경과 시간 환산 |
| 방향 차 컷오프 | `> 30°` | 레이싱 라인 방향과 헤딩 차가 크면 보상 `1e-3` (스핀 등) |
| 저속 컷오프 | `> 0.5` m/s | 최적 속도보다 이만큼 느리면 보상 `1e-3` |
| 트랙 이탈 | `all_wheels_on_track == False` | 최종 보상 `1e-3` |

(예선 파일은 `RAPID_*`, 본선 파일은 `FASTEST_*` 로 이름만 다릅니다.)

**`final_smile_speedway/rnd2_reward.py`** — 항목별 계단식 점수의 가중 평균

| 항목 | 구간 → 점수 | 가중치 |
|---|---|---|
| 즉시 실패 | `is_crashed` / `is_offtrack` / 바퀴 이탈 → `1e-3` 반환 | — |
| 중심선 유지 (`distance_from_center / track_width`) | ≤0.1 → 2.5, ≤0.25 → 2.0, ≤0.4 → 1.5, ≤0.5 → 1.0, 그 외 0.1 | `3.0` |
| 방향 정렬 (waypoint 방향 − 헤딩) | ≤10° → 2.0, ≤15° → 1.5, ≤25° → 1.0, 그 외 0.5 | `2.5` |
| 속도 | 2.4–3.5 → 2.0, 1.8–2.4 → 1.5, 1.2–1.8 → 1.2, >3.5 → 1.0, <1.2 → 0.8 | `2.0` |
| 장애물 (같은 레인의 다음 장애물까지 거리) | <0.5 m → 1e-3, <1.0 → 0.3, <1.5 → 0.6, <2.0 → 1.2, 그 외 2.0. 다른 레인 1.8, 예외 시 1.5 | `5.0` |
| 스티어링 | ≤10° → 1.5, ≤20° → 1.2, ≤26° → 1.0, 그 외 0.7 | `1.5` |
| 진행률 | ≥97% → 3.0, ≥90 → 2.0, ≥75 → 1.5, ≥50 → 1.2, ≥25 → 1.0, 그 외 0.5 | `1.0` |
| 정규화 | 가중합 ÷ `15.0` | — |
| 진행률 배수 | >90% ×1.3, >75% ×1.15, >50% ×1.05 | — |
| 고속 안전 보너스 | 속도 ≥2.5 이고 중심 비율 ≤0.2 이고 장애물 점수 ≥1.5 → ×1.2 | — |
| 클램프 | `[1e-3, 20.0]` | — |

**`final_smile_speedway/dh_reward.py`**

| 항목 | 값 | 역할 |
|---|---|---|
| 기본 보상 | `1.0` | 시작값 |
| 트랙 이탈 | 바퀴 이탈 → `1e-3` 반환 | — |
| 중심선 | `+ 1.5 − (distance_from_center / (track_width/2))^(1/4)` | 중앙에 가까울수록 가산 (식은 서드파티 `matthew.py` 출처) |
| `SPEED_THRESHOLD` | `2.9` m/s | 이상이면 `+2.0` |
| `DIRECTION_THRESHOLD` | `10.0°` | waypoint 방향과 헤딩 차가 이보다 작으면 `+1.0`, 아니면 보상 `×0.7` |

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

## Driving footage

### 본선 — Smile Speedway

https://github.com/user-attachments/assets/9c1f7fce-4877-4409-a1b3-1ebe5970a81f

640×480 · 21초 · [원본 파일](media/dh-best.mp4)

### 예선 — Spain track

https://github.com/user-attachments/assets/fc6d0c31-de34-4c06-9008-8e11ec8a58fc

640×480 · 27초 · [원본 파일](media/aws_%EC%98%88%EC%84%A0.mp4)

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

## License

직접 작성한 코드는 MIT — `LICENSE` 참조. 위 "Not in this repository" 의 서드파티 자료와 그로부터 가져온 부분(레이싱 라인 산출 노트북, `dh_reward.py` 의 중심선 식 등)은 각 원저작자의 조건을 따르며 MIT 적용 대상이 아닙니다.
