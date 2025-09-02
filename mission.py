"""
Mission Profile System
Based on Aircraft Mission Performance Analysis
WUTO → Climb → Cruise → Turn → Descent → Landing
"""

import pygame
import math

class MissionSegment:
    """미션 세그먼트 기본 클래스"""
    def __init__(self, name, target_altitude=None, target_speed=None, duration=None, distance=None):
        self.name = name
        self.target_altitude = target_altitude
        self.target_speed = target_speed
        self.duration = duration
        self.distance = distance
        self.completed = False
        self.progress = 0.0
        
class MissionProfile:
    """미션 프로파일 관리"""
    def __init__(self, aircraft):
        self.aircraft = aircraft
        self.segments = []
        self.current_segment_index = 0
        self.mission_complete = False
        
        # 미션 데이터
        self.total_fuel_consumed = 0.0
        self.total_distance = 0.0
        self.total_time = 0.0
        
        # 디스플레이 설정
        self.display_enabled = True
        self.profile_data = {
            'altitude': [],
            'range': [],
            'fuel': [],
            'segments': []
        }
        
        # 기본 미션 프로파일 생성
        self.create_default_mission()
        
    def create_default_mission(self):
        """기본 미션 프로파일 생성 (논문 참조)"""
        self.segments = [
            # WUTO (Warm-up and Take-off)
            MissionSegment("WUTO", target_altitude=100, target_speed=80, duration=60),
            
            # Min Fuel Climb
            MissionSegment("CLIMB", target_altitude=5000, target_speed=150, distance=50000),
            
            # Cruise
            MissionSegment("CRUISE", target_altitude=5000, target_speed=200, distance=200000),
            
            # Turn (선회)
            MissionSegment("TURN", target_altitude=5000, target_speed=180, duration=120),
            
            # Descent
            MissionSegment("DESCENT", target_altitude=500, target_speed=150, distance=40000),
            
            # Landing approach
            MissionSegment("LANDING", target_altitude=0, target_speed=70, distance=10000)
        ]
        
    def update(self, dt):
        """미션 프로파일 업데이트"""
        if self.mission_complete or self.current_segment_index >= len(self.segments):
            return
            
        current_segment = self.segments[self.current_segment_index]
        
        # 현재 세그먼트 실행
        self.execute_segment(current_segment, dt)
        
        # 미션 데이터 업데이트
        self.total_time += dt
        self.total_distance = self.aircraft.total_range
        
        # 프로파일 데이터 기록
        self.record_profile_data()
        
        # 세그먼트 완료 체크
        if current_segment.completed:
            self.current_segment_index += 1
            if self.current_segment_index >= len(self.segments):
                self.mission_complete = True
                self.aircraft.mission_data['phase'] = 'COMPLETE'
                
    def execute_segment(self, segment, dt):
        """세그먼트 실행"""
        # 현재 항공기 상태
        current_altitude = self.aircraft.position.y
        current_speed = self.aircraft.velocity.length()
        
        # 미션 페이즈 업데이트
        self.aircraft.mission_data['phase'] = segment.name
        
        if segment.name == "WUTO":
            self.execute_wuto(segment, dt)
            
        elif segment.name == "CLIMB":
            self.execute_climb(segment, dt)
            
        elif segment.name == "CRUISE":
            self.execute_cruise(segment, dt)
            
        elif segment.name == "TURN":
            self.execute_turn(segment, dt)
            
        elif segment.name == "DESCENT":
            self.execute_descent(segment, dt)
            
        elif segment.name == "LANDING":
            self.execute_landing(segment, dt)
            
    def execute_wuto(self, segment, dt):
        """WUTO (Warm-up and Take-off) 실행"""
        # 엔진 워밍업
        if segment.progress < 30:  # 처음 30초는 워밍업
            self.aircraft.throttle = 0.3
            segment.progress += dt
        else:
            # 이륙
            self.aircraft.throttle = 1.0
            
            if self.aircraft.position.y >= segment.target_altitude:
                segment.completed = True
                
    def execute_climb(self, segment, dt):
        """상승 실행 (Min Fuel Climb)"""
        target_alt = segment.target_altitude
        current_alt = self.aircraft.position.y
        
        if current_alt < target_alt:
            # 최적 상승률 계산 (논문의 Min Fuel Climb 참조)
            altitude_error = target_alt - current_alt
            
            # 고도 차이에 따른 피치 조정
            desired_pitch = min(0.3, altitude_error / 1000)
            pitch_rate = 0.5 * dt
            
            if self.aircraft.rotation.x < desired_pitch:
                self.aircraft.rotation.x += pitch_rate
            elif self.aircraft.rotation.x > desired_pitch:
                self.aircraft.rotation.x -= pitch_rate
                
            # 속도 조절
            current_speed = self.aircraft.velocity.length()
            if current_speed < segment.target_speed:
                self.aircraft.throttle = min(1.0, self.aircraft.throttle + dt * 0.5)
            else:
                self.aircraft.throttle = max(0.5, self.aircraft.throttle - dt * 0.5)
                
        else:
            # 목표 고도 도달
            segment.completed = True
            self.aircraft.rotation.x = 0  # 수평 비행
            
    def execute_cruise(self, segment, dt):
        """순항 실행"""
        # 고도 유지
        altitude_error = segment.target_altitude - self.aircraft.position.y
        self.aircraft.rotation.x = altitude_error * 0.001
        
        # 속도 유지
        current_speed = self.aircraft.velocity.length()
        speed_error = segment.target_speed - current_speed
        
        if abs(speed_error) > 5:
            throttle_adjustment = speed_error * 0.01
            self.aircraft.throttle = max(0.3, min(1.0, self.aircraft.throttle + throttle_adjustment))
            
        # 거리 체크
        if segment.distance:
            segment.progress = self.aircraft.total_range
            if segment.progress >= segment.distance:
                segment.completed = True
                
    def execute_turn(self, segment, dt):
        """선회 실행 (Sustained Turn)"""
        # 일정한 뱅크각으로 선회
        bank_angle = math.pi / 6  # 30도 뱅크
        
        if not hasattr(segment, 'turn_time'):
            segment.turn_time = 0
            
        segment.turn_time += dt
        
        # 선회 중 고도 유지
        altitude_error = segment.target_altitude - self.aircraft.position.y
        self.aircraft.rotation.x = altitude_error * 0.001
        
        # 뱅크 적용
        self.aircraft.rotation.z = bank_angle
        
        # 선회율 계산 (논문 참조)
        turn_rate = 9.81 * math.tan(bank_angle) / segment.target_speed
        self.aircraft.rotation.y += turn_rate * dt
        
        # 시간 체크
        if segment.turn_time >= segment.duration:
            segment.completed = True
            self.aircraft.rotation.z = 0  # 수평 복귀
            
    def execute_descent(self, segment, dt):
        """하강 실행"""
        target_alt = segment.target_altitude
        current_alt = self.aircraft.position.y
        
        if current_alt > target_alt:
            # 하강률 계산
            altitude_error = current_alt - target_alt
            desired_pitch = -min(0.2, altitude_error / 2000)
            
            pitch_rate = 0.3 * dt
            if self.aircraft.rotation.x > desired_pitch:
                self.aircraft.rotation.x -= pitch_rate
                
            # 추력 감소
            self.aircraft.throttle = max(0.2, self.aircraft.throttle - dt * 0.3)
            
        else:
            segment.completed = True
            self.aircraft.rotation.x = 0
            
    def execute_landing(self, segment, dt):
        """착륙 접근 실행"""
        # 점진적 속도 감소
        current_speed = self.aircraft.velocity.length()
        
        if current_speed > segment.target_speed:
            self.aircraft.throttle = max(0.1, self.aircraft.throttle - dt * 0.5)
            
        # 점진적 고도 감소
        if self.aircraft.position.y > 10:
            self.aircraft.rotation.x = -0.1
        else:
            # 착륙 완료
            segment.completed = True
            self.aircraft.throttle = 0
            self.aircraft.velocity = pygame.math.Vector3(0, 0, 0)
            
    def record_profile_data(self):
        """프로파일 데이터 기록"""
        # 매 초마다 데이터 기록
        if int(self.total_time) > len(self.profile_data['altitude']):
            self.profile_data['altitude'].append(self.aircraft.position.y)
            self.profile_data['range'].append(self.aircraft.total_range)
            self.profile_data['fuel'].append(self.aircraft.fuel_mass)
            
            if self.current_segment_index < len(self.segments):
                self.profile_data['segments'].append(self.segments[self.current_segment_index].name)
            else:
                self.profile_data['segments'].append('COMPLETE')
                
    def get_current_segment_name(self):
        """현재 세그먼트 이름 반환"""
        if self.current_segment_index < len(self.segments):
            return self.segments[self.current_segment_index].name
        return "COMPLETE"
        
    def get_mission_progress(self):
        """전체 미션 진행률 반환"""
        if len(self.segments) == 0:
            return 0
        return (self.current_segment_index / len(self.segments)) * 100
        
    def toggle_display(self):
        """디스플레이 토글"""
        self.display_enabled = not self.display_enabled
        
    def reset(self):
        """미션 리셋"""
        self.current_segment_index = 0
        self.mission_complete = False
        self.total_fuel_consumed = 0.0
        self.total_distance = 0.0
        self.total_time = 0.0
        
        # 세그먼트 리셋
        for segment in self.segments:
            segment.completed = False
            segment.progress = 0.0
            if hasattr(segment, 'turn_time'):
                delattr(segment, 'turn_time')
                
        # 프로파일 데이터 리셋
        self.profile_data = {
            'altitude': [],
            'range': [],
            'fuel': [],
            'segments': []
        }