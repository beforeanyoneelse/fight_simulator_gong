# Advanced Flight Simulator with Mission Profile

## 개요
논문 "항공기 임무 성능 해석 프로그램 개발"을 기반으로 한 데이터 기반 비행 시뮬레이터입니다.

## 특징
- **물리 기반 비행 모델**: 실제 항공역학 방정식 사용
- **미션 프로파일 시스템**: WUTO → Climb → Cruise → Turn → Descent → Landing
- **3D 환경**: 건물, 산, 나무, 구름이 있는 현실적인 환경
- **충돌 경고 시스템**: 지형 및 건물 충돌 감지 및 경고
- **상세한 HUD**: 비행 데이터, 미션 진행상황, 성능 지표 표시
- **다양한 항공기 모델**: 제트기, 수송기, 경항공기 데이터 포함

## 파일 구조
```
flight_simulator/
├── main.py                 # 메인 실행 파일
├── aircraft.py            # 항공기 물리 모델
├── world.py               # 3D 세계 및 객체들
├── mission.py             # 미션 프로파일 시스템
├── physics.py             # 물리 엔진 헬퍼
├── hud.py                 # HUD 및 UI
├── data/
│   └── aircraft_data.json # 항공기 데이터
└── README.md              # 사용 설명서
```

## 설치 및 실행

### 필요 라이브러리
```bash
pip install pygame numpy
```

### 실행 방법
```bash
python main.py
```

## 조작법

### 기본 조작
- **W/S**: 피치 (상승/하강)
- **A/D**: 롤 (좌/우 회전)
- **Q/E**: 요 (좌/우 방향)
- **Shift/Ctrl**: 스로틀 (증가/감소)
- **Space**: 자동 수평 유지

### 기능 키
- **M**: 미션 프로파일 표시 토글
- **Tab**: 상세 HUD 토글
- **P**: 일시정지
- **R**: 재시작 (충돌 후)
- **ESC**: 종료

## 미션 프로파일

### 1. WUTO (Warm-up and Take-off)
- 엔진 예열 및 이륙
- 목표 고도: 100m
- 소요 시간: 약 60초

### 2. Climb (상승)
- Min Fuel Climb 방식으로 최적 상승
- 목표 고도: 5000m
- 최적 속도로 상승

### 3. Cruise (순항)
- 일정 고도 및 속도 유지
- 목표 거리: 200km
- 연료 효율 최적화

### 4. Turn (선회)
- 30도 뱅크각으로 지속 선회
- 소요 시간: 120초
- 고도 유지

### 5. Descent (하강)
- 안전한 하강률로 하강
- 목표 고도: 500m
- 속도 조절

### 6. Landing (착륙)
- 착륙 접근 및 착륙
- 최종 고도: 0m
- 속도 감소

## 경고 시스템

### 지형 경고
- 100m 이하: 경고 표시
- 30m 이하: 심각한 경고
- 5m 이하: 충돌

### 건물 충돌 경고
- 근접 시 자동 경고
- "TERRAIN WARNING" 표시
- "PULL UP" 메시지

## HUD 정보

### 기본 정보
- 고도 (ALTITUDE)
- 속도 (SPEED)
- 방향 (HEADING)
- 피치각 (PITCH)
- 롤각 (ROLL)
- 스로틀 (THROTTLE)
- 연료 (FUEL)
- 항속거리 (RANGE)

### 미션 정보
- 현재 페이즈 (PHASE)
- 진행률 (Progress)
- 미션 시간 (Mission Time)

### 성능 데이터 (Tab 키로 표시)
- L/D 비율
- 상승률
- 예상 항속거리
- 체공시간
- 중량 및 균형

## 항공기 데이터 수정

`data/aircraft_data.json` 파일을 수정하여 항공기 성능을 변경할 수 있습니다:

```json
{
  "your_aircraft": {
    "name": "항공기 이름",
    "mass": 10000,           // 공허중량 (kg)
    "wing_area": 50,          // 날개 면적 (m²)
    "max_thrust": 80000,      // 최대 추력 (N)
    "fuel_capacity": 3000,    // 연료 용량 (kg)
    "fuel_flow_rate": 1.5,    // 연료 소모율 (kg/s)
    ...
  }
}
```

## 문제 해결

### 프로그램이 느린 경우
- 렌더링 거리 줄이기: `world.py`의 `render_distance` 값 감소
- 객체 수 줄이기: 건물, 나무 생성 개수 조정

### 충돌이 너무 민감한 경우
- `main.py`의 `warning_threshold` 및 `critical_threshold` 값 조정

## 참고 자료
- 논문: "항공기 임무 성능 해석 프로그램 개발" (이현석, 2013)
- 인하대학교 항공우주공학과

## 라이선스
교육 목적으로 자유롭게 사용 가능