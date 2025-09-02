"""
Aircraft Physics Model
Based on Mission Performance Analysis equations
"""

import pygame
import math
import json

class Aircraft:
    def __init__(self, config_file=None):
        """항공기 초기화"""
        # 기본 위치 및 자세
        self.position = pygame.math.Vector3(0, 500, 0)  # x, y(altitude), z
        self.velocity = pygame.math.Vector3(0, 0, 100)  # m/s - 초기 속도 설정
        self.rotation = pygame.math.Vector3(0, 0, 0)    # pitch, yaw, roll (radians)
        
        # 항공기 데이터 (논문 참조)
        if config_file:
            self.load_aircraft_data(config_file)
        else:
            # 기본 항공기 데이터 (중형 제트기 기준)
            self.mass = 50000  # kg (초기 중량)
            self.wing_area = 150  # m^2
            self.max_thrust = 200000  # N (2개 엔진)
            self.fuel_capacity = 15000  # kg
            self.fuel_flow_rate = 2.0  # kg/s at max thrust
            
        # 현재 상태
        self.fuel_mass = self.fuel_capacity * 0.8  # 80% 연료
        self.throttle = 0.5  # 0.0 ~ 1.0
        
        # 공력 계수
        self.CL0 = 0.2  # 기본 양력계수
        self.CL_alpha = 5.0  # 받음각에 따른 양력계수 변화
        self.CD0 = 0.025  # 기본 항력계수
        self.K = 0.04  # 유도항력 계수
        
        # 성능 한계
        self.max_speed = 250  # m/s (약 900 km/h)
        self.min_speed = 60   # m/s (약 216 km/h)
        self.service_ceiling = 12000  # m
        self.max_load_factor = 2.5  # g
        
        # 미션 데이터 기록
        self.mission_data = {
            'time': [],
            'altitude': [],
            'speed': [],
            'fuel': [],
            'range': [],
            'phase': 'GROUND'
        }
        self.total_range = 0.0
        self.mission_time = 0.0
        
    def load_aircraft_data(self, filename):
        """항공기 데이터 로드"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.mass = data.get('mass', 50000)
                self.wing_area = data.get('wing_area', 150)
                self.max_thrust = data.get('max_thrust', 200000)
                self.fuel_capacity = data.get('fuel_capacity', 15000)
                self.fuel_flow_rate = data.get('fuel_flow_rate', 2.0)
        except:
            print("Using default aircraft data")
            
    def get_total_mass(self):
        """총 중량 계산"""
        return self.mass + self.fuel_mass
        
    def get_thrust(self):
        """추력 계산 (고도와 속도에 따른 보정)"""
        # 고도에 따른 추력 감소
        altitude_factor = 1.0 - (self.position.y / 20000) if self.position.y < 20000 else 0.5
        
        # 속도에 따른 추력 변화
        speed = self.velocity.length()
        speed_factor = 1.0 - (speed / 1000) if speed < 1000 else 0.0
        
        return self.max_thrust * self.throttle * altitude_factor * speed_factor
        
    def get_lift(self, alpha):
        """양력 계산"""
        # 대기 밀도 (간단한 모델)
        rho = 1.225 * math.exp(-self.position.y / 8000)
        
        # 속도
        V = self.velocity.length()
        if V < 0.1:
            return 0
            
        # 받음각 기반 양력계수 (피치각을 받음각으로 사용)
        CL = self.CL0 + self.CL_alpha * alpha
        
        # 양력계수 제한 (실속 방지)
        CL = max(-1.5, min(1.5, CL))
        
        # 양력 L = 0.5 * rho * V^2 * S * CL
        return 0.5 * rho * V * V * self.wing_area * CL
        
    def get_drag(self, alpha):
        """항력 계산"""
        # 대기 밀도
        rho = 1.225 * math.exp(-self.position.y / 8000)
        
        # 속도
        V = self.velocity.length()
        if V < 0.1:
            return 0
            
        # 양력계수
        CL = self.CL0 + self.CL_alpha * alpha
        
        # 항력계수 (기본항력 + 유도항력)
        CD = self.CD0 + self.K * CL * CL
        
        # 항력 D = 0.5 * rho * V^2 * S * CD
        return 0.5 * rho * V * V * self.wing_area * CD
        
    def update_fuel(self, dt):
        """연료 소모 계산"""
        # 추력에 비례한 연료 소모
        fuel_consumption = self.fuel_flow_rate * self.throttle * dt
        
        # 고도에 따른 연료 효율 (높은 고도에서 효율적)
        altitude_efficiency = 1.0 - (self.position.y / 30000) if self.position.y < 15000 else 0.5
        fuel_consumption *= altitude_efficiency
        
        self.fuel_mass = max(0, self.fuel_mass - fuel_consumption)
        
        return fuel_consumption
        
    def update(self, dt, keys):
        """항공기 상태 업데이트"""
        if self.fuel_mass <= 0:
            # 연료 고갈
            self.throttle = 0
            
        # 조종 입력
        pitch_rate = 1.5 * dt
        roll_rate = 2.0 * dt
        yaw_rate = 1.0 * dt
        
        # Pitch control (W/S)
        if keys[pygame.K_w]:
            self.rotation.x = min(math.pi/6, self.rotation.x + pitch_rate)  # W키 = 기수 들기 (상승)
        if keys[pygame.K_s]:
            self.rotation.x = max(-math.pi/6, self.rotation.x - pitch_rate)  # S키 = 기수 내리기 (하강)
            
        # Roll control (A/D)
        if keys[pygame.K_a]:
            self.rotation.z = max(-math.pi/3, self.rotation.z - roll_rate)
        if keys[pygame.K_d]:
            self.rotation.z = min(math.pi/3, self.rotation.z + roll_rate)
            
        # Yaw control (Q/E)
        if keys[pygame.K_q]:
            self.rotation.y -= yaw_rate
        if keys[pygame.K_e]:
            self.rotation.y += yaw_rate
            
        # Throttle control (Shift/Ctrl)
        if keys[pygame.K_LSHIFT]:
            self.throttle = min(1.0, self.throttle + dt)
        if keys[pygame.K_LCTRL]:
            self.throttle = max(0.0, self.throttle - dt)
            
        # Auto-level (Space)
        if keys[pygame.K_SPACE]:
            self.rotation.x *= 0.95
            self.rotation.z *= 0.95
            
        # 물리 계산
        self.update_physics(dt)
        
        # 연료 업데이트
        self.update_fuel(dt)
        
        # 미션 데이터 기록
        self.update_mission_data(dt)
        
    def update_physics(self, dt):
        """물리 엔진 업데이트"""
        # 받음각 계산
        speed = self.velocity.length()
        if speed > 0.1:
            alpha = self.rotation.x  # 간단화된 받음각
        else:
            alpha = 0
            
        # 힘 계산
        thrust = self.get_thrust()
        lift = self.get_lift(alpha)
        drag = self.get_drag(alpha)
        weight = self.get_total_mass() * 9.81
        
        # 추력 방향 (기체 좌표계)
        thrust_dir = pygame.math.Vector3(0, 0, 1)
        # 피치 회전 적용
        cos_pitch = math.cos(self.rotation.x)
        sin_pitch = math.sin(self.rotation.x)
        thrust_dir_y = sin_pitch
        thrust_dir_z = cos_pitch
        
        # 요 회전 적용
        cos_yaw = math.cos(self.rotation.y)
        sin_yaw = math.sin(self.rotation.y)
        thrust_dir_x = thrust_dir_z * sin_yaw
        thrust_dir_z = thrust_dir_z * cos_yaw
        
        thrust_dir = pygame.math.Vector3(thrust_dir_x, thrust_dir_y, thrust_dir_z)
        
        # 가속도 계산
        mass = self.get_total_mass()
        
        # 추력에 의한 가속도
        thrust_accel = thrust_dir * (thrust / mass)
        
        # 항력에 의한 가속도 (속도 반대 방향)
        if speed > 0.1:
            drag_accel = self.velocity.normalize() * (-drag / mass)
        else:
            drag_accel = pygame.math.Vector3(0, 0, 0)
            
        # 양력에 의한 가속도 (수직 방향)
        lift_accel = pygame.math.Vector3(0, lift / mass, 0)
        
        # 중력
        gravity = pygame.math.Vector3(0, -9.81, 0)
        
        # 총 가속도
        acceleration = thrust_accel + drag_accel + lift_accel + gravity
        
        # 속도 업데이트
        self.velocity += acceleration * dt
        
        # 속도 제한
        speed = self.velocity.length()
        if speed > self.max_speed:
            self.velocity = self.velocity.normalize() * self.max_speed
            
        # 위치 업데이트
        self.position += self.velocity * dt
        
        # 고도 제한
        if self.position.y < 10:
            self.position.y = 10
            if self.velocity.y < 0:
                self.velocity.y = 0
                
        if self.position.y > self.service_ceiling:
            self.position.y = self.service_ceiling
            
    def update_mission_data(self, dt):
        """미션 데이터 업데이트"""
        self.mission_time += dt
        
        # 항속거리 계산
        horizontal_speed = math.sqrt(self.velocity.x**2 + self.velocity.z**2)
        self.total_range += horizontal_speed * dt
        
        # 데이터 기록 (1초마다)
        if int(self.mission_time) > len(self.mission_data['time']):
            self.mission_data['time'].append(self.mission_time)
            self.mission_data['altitude'].append(self.position.y)
            self.mission_data['speed'].append(self.velocity.length())
            self.mission_data['fuel'].append(self.fuel_mass)
            self.mission_data['range'].append(self.total_range)
            
    def reset(self):
        """항공기 리셋"""
        self.position = pygame.math.Vector3(0, 500, 0)
        self.velocity = pygame.math.Vector3(0, 0, 100)
        self.rotation = pygame.math.Vector3(0, 0, 0)
        self.throttle = 0.5
        self.fuel_mass = self.fuel_capacity * 0.8
        self.total_range = 0.0
        self.mission_time = 0.0
        self.mission_data = {
            'time': [],
            'altitude': [],
            'speed': [],
            'fuel': [],
            'range': [],
            'phase': 'GROUND'
        }