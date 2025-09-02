#!/usr/bin/env python3
"""
Advanced Flight Simulator with Mission Profile
Based on Aircraft Mission Performance Analysis
"""

import pygame
import sys
import json
from aircraft import Aircraft
from world import World
from mission import MissionProfile
from hud import HUD

class FlightSimulator:
    def __init__(self):
        pygame.init()
        
        # Display settings
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        self.FPS = 60
        
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Advanced Flight Simulator - Mission Profile")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.aircraft = Aircraft()
        self.world = World(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.mission = MissionProfile(self.aircraft)
        self.hud = HUD(self.screen, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Camera settings
        self.camera_offset = pygame.math.Vector3(0, 15, -50)  # 더 멀리서 보기
        self.camera_position = pygame.math.Vector3(0, 0, 0)
        self.camera_mode = "third_person"  # third_person, chase, free
        
        # Simulation state
        self.running = True
        self.paused = False
        self.crashed = False
        self.warning_timer = 0
        self.collision_warning = False
        
        # Debug mode
        self.debug_mode = True
        print("Debug mode enabled - press D to toggle")
        
    def handle_events(self):
        """이벤트 처리"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_r and self.crashed:
                    self.reset_simulation()
                elif event.key == pygame.K_m:
                    self.mission.toggle_display()
                elif event.key == pygame.K_d:
                    self.debug_mode = not self.debug_mode
                    print(f"Debug mode: {self.debug_mode}")
                elif event.key == pygame.K_c:
                    # 카메라 모드 전환
                    self.cycle_camera_mode()
                elif event.key == pygame.K_TAB:
                    self.hud.toggle_detailed_view()
                    
    def reset_simulation(self):
        """시뮬레이션 리셋"""
        self.aircraft.reset()
        self.mission.reset()
        self.crashed = False
        self.warning_timer = 0
        self.collision_warning = False
        
    def check_collisions(self, dt):
        """충돌 검사 및 경고"""
        # 지형과의 충돌 검사
        terrain_height = self.world.get_terrain_height(
            self.aircraft.position.x, 
            self.aircraft.position.z
        )
        
        altitude_agl = self.aircraft.position.y - terrain_height
        
        # 건물과의 충돌 검사
        min_building_distance = float('inf')
        for building in self.world.buildings:
            distance = self.world.check_building_collision(
                self.aircraft.position, 
                building
            )
            min_building_distance = min(min_building_distance, distance)
        
        # 경고 시스템
        warning_threshold = 100  # 100m 이하에서 경고
        critical_threshold = 30  # 30m 이하에서 심각한 경고
        
        if altitude_agl < critical_threshold or min_building_distance < critical_threshold:
            self.collision_warning = True
            self.warning_timer += dt
            
            if altitude_agl <= 5 or min_building_distance <= 10:
                # 충돌 발생
                self.crashed = True
                self.aircraft.velocity = pygame.math.Vector3(0, 0, 0)
                
        elif altitude_agl < warning_threshold or min_building_distance < warning_threshold:
            self.collision_warning = True
            self.warning_timer += dt
        else:
            self.collision_warning = False
            self.warning_timer = 0
            
    def cycle_camera_mode(self):
        """카메라 모드 순환"""
        modes = ["third_person", "chase", "orbit", "free"]
        current_index = modes.index(self.camera_mode)
        self.camera_mode = modes[(current_index + 1) % len(modes)]
        
        # 카메라 오프셋 조정
        if self.camera_mode == "third_person":
            self.camera_offset = pygame.math.Vector3(0, 20, -60)
        elif self.camera_mode == "chase":
            self.camera_offset = pygame.math.Vector3(0, 10, -40)
        elif self.camera_mode == "orbit":
            self.camera_offset = pygame.math.Vector3(30, 15, -30)
        elif self.camera_mode == "free":
            self.camera_offset = pygame.math.Vector3(0, 50, -100)
            
    def update_camera(self):
        """카메라 업데이트"""
        if self.camera_mode == "third_person":
            # 항공기를 3인칭으로 보는 카메라
            target_offset = self.camera_offset
            
            # 항공기 회전에 따라 카메라도 회전
            target_offset = target_offset.rotate_y(self.aircraft.rotation.y)
            target_offset = target_offset.rotate_x(self.aircraft.rotation.x * 0.3)
            
            target_pos = self.aircraft.position + target_offset
            
            # 부드러운 카메라 이동
            self.camera_position.x += (target_pos.x - self.camera_position.x) * 0.1
            self.camera_position.y += (target_pos.y - self.camera_position.y) * 0.1
            self.camera_position.z += (target_pos.z - self.camera_position.z) * 0.1
            
        elif self.camera_mode == "chase":
            # 더 가까운 추적 카메라
            target_offset = self.camera_offset
            target_offset = target_offset.rotate_y(self.aircraft.rotation.y)
            target_offset = target_offset.rotate_x(self.aircraft.rotation.x * 0.5)
            
            target_pos = self.aircraft.position + target_offset
            
            # 빠른 카메라 추적
            self.camera_position.x += (target_pos.x - self.camera_position.x) * 0.2
            self.camera_position.y += (target_pos.y - self.camera_position.y) * 0.2
            self.camera_position.z += (target_pos.z - self.camera_position.z) * 0.2
            
        elif self.camera_mode == "orbit":
            # 궤도 카메라 (시간에 따라 회전)
            orbit_angle = pygame.time.get_ticks() / 5000.0
            
            target_offset = pygame.math.Vector3(
                math.sin(orbit_angle) * 50,
                20,
                math.cos(orbit_angle) * 50
            )
            
            target_pos = self.aircraft.position + target_offset
            
            self.camera_position.x += (target_pos.x - self.camera_position.x) * 0.1
            self.camera_position.y += (target_pos.y - self.camera_position.y) * 0.1
            self.camera_position.z += (target_pos.z - self.camera_position.z) * 0.1
            
        elif self.camera_mode == "free":
            # 자유 시점 (고정된 거리)
            target_offset = self.camera_offset
            target_offset = target_offset.rotate_y(self.aircraft.rotation.y * 0.5)
            
            target_pos = self.aircraft.position + target_offset
            
            self.camera_position.x += (target_pos.x - self.camera_position.x) * 0.05
            self.camera_position.y += (target_pos.y - self.camera_position.y) * 0.05
            self.camera_position.z += (target_pos.z - self.camera_position.z) * 0.05
        
    def update(self, dt):
        """게임 로직 업데이트"""
        if self.paused or self.crashed:
            return
            
        keys = pygame.key.get_pressed()
        
        # 항공기 업데이트
        self.aircraft.update(dt, keys)
        
        # 미션 프로파일 업데이트
        self.mission.update(dt)
        
        # 월드 업데이트
        self.world.update(dt, self.aircraft.position)
        
        # 충돌 검사
        self.check_collisions(dt)
        
        # 카메라 업데이트
        self.update_camera()
        
    def render(self):
        """렌더링"""
        # 배경 (하늘)
        self.screen.fill((135, 206, 235))
        
        # 3D 월드 렌더링
        self.world.render(self.screen, self.camera_position, self.aircraft.rotation)
        
        # 항공기 렌더링 (3인칭 시점에서)
        self.render_aircraft()
        
        # HUD 렌더링
        self.hud.render(
            self.aircraft,
            self.mission,
            self.collision_warning,
            self.warning_timer,
            self.crashed
        )
        
        # 디버그 정보 표시
        if self.debug_mode:
            self.render_debug_info()
        
        # 충돌 시 메시지
        if self.crashed:
            font = pygame.font.Font(None, 72)
            text = font.render("CRASHED!", True, (255, 0, 0))
            text_rect = text.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2))
            self.screen.blit(text, text_rect)
            
            font_small = pygame.font.Font(None, 36)
            text_restart = font_small.render("Press R to Restart", True, (255, 255, 255))
            restart_rect = text_restart.get_rect(center=(self.SCREEN_WIDTH//2, self.SCREEN_HEIGHT//2 + 50))
            self.screen.blit(text_restart, restart_rect)
            
        pygame.display.flip()
        
    def render_debug_info(self):
        """디버그 정보 렌더링"""
        font = pygame.font.Font(None, 20)
        debug_surface = pygame.Surface((300, 150))
        debug_surface.set_alpha(200)
        debug_surface.fill((0, 0, 0))
        self.screen.blit(debug_surface, (10, self.SCREEN_HEIGHT - 400))
        
        keys = pygame.key.get_pressed()
        debug_text = [
            f"=== DEBUG INFO ===",
            f"Camera: {self.camera_mode}",
            f"Rotation: ({self.aircraft.rotation.x:.2f}, {self.aircraft.rotation.y:.2f}, {self.aircraft.rotation.z:.2f})",
            f"Velocity: {self.aircraft.velocity.length():.1f} m/s",
            f"Keys: W:{keys[pygame.K_w]} S:{keys[pygame.K_s]}",
            f"      A:{keys[pygame.K_a]} D:{keys[pygame.K_d]}",
            f"      Shift:{keys[pygame.K_LSHIFT]} Ctrl:{keys[pygame.K_LCTRL]}"
        ]
        
        y_offset = self.SCREEN_HEIGHT - 390
        for line in debug_text:
            text = font.render(line, True, (0, 255, 0))
            self.screen.blit(text, (20, y_offset))
            y_offset += 20
        
    def render_aircraft(self):
        """항공기 모델 렌더링"""
        # 항공기 위치를 화면 좌표로 변환
        aircraft_screen_pos = self.world.project_3d_to_2d(
            self.aircraft.position, 
            self.camera_position, 
            self.aircraft.rotation
        )
        
        if aircraft_screen_pos:
            # 항공기와 카메라 사이의 거리
            distance = (self.aircraft.position - self.camera_position).length()
            
            # 거리에 따른 크기 조절
            scale = max(0.5, min(2.0, 100 / (distance + 50)))
            
            # 항공기 동체
            fuselage_length = int(30 * scale)
            fuselage_width = int(8 * scale)
            
            # 항공기 방향 벡터
            direction = pygame.math.Vector3(0, 0, 1)
            direction = direction.rotate_x(self.aircraft.rotation.x)
            direction = direction.rotate_y(self.aircraft.rotation.y)
            
            # 항공기 앞뒤 위치
            nose_pos = self.aircraft.position + direction * 10
            tail_pos = self.aircraft.position - direction * 10
            
            nose_screen = self.world.project_3d_to_2d(nose_pos, self.camera_position, self.aircraft.rotation)
            tail_screen = self.world.project_3d_to_2d(tail_pos, self.camera_position, self.aircraft.rotation)
            
            if nose_screen and tail_screen:
                # 동체 그리기
                pygame.draw.line(self.screen, (80, 80, 80), tail_screen, nose_screen, fuselage_width)
                
                # 날개
                wing_span = int(40 * scale)
                wing_pos = self.aircraft.position - direction * 3
                
                # 좌우 날개 끝
                right_vector = pygame.math.Vector3(1, 0, 0)
                right_vector = right_vector.rotate_y(self.aircraft.rotation.y)
                right_vector = right_vector.rotate_z(self.aircraft.rotation.z)
                
                left_wing = wing_pos - right_vector * wing_span/2
                right_wing = wing_pos + right_vector * wing_span/2
                
                left_screen = self.world.project_3d_to_2d(left_wing, self.camera_position, self.aircraft.rotation)
                right_screen = self.world.project_3d_to_2d(right_wing, self.camera_position, self.aircraft.rotation)
                
                if left_screen and right_screen:
                    # 날개 그리기
                    pygame.draw.line(self.screen, (100, 100, 100), left_screen, right_screen, int(5 * scale))
                    
                # 수직 꼬리날개
                tail_fin_top = tail_pos + pygame.math.Vector3(0, -8, 0)
                tail_fin_screen = self.world.project_3d_to_2d(tail_fin_top, self.camera_position, self.aircraft.rotation)
                
                if tail_fin_screen:
                    pygame.draw.line(self.screen, (100, 100, 100), tail_screen, tail_fin_screen, int(4 * scale))
                    
                # 엔진 불꽃 (추력이 있을 때)
                if self.aircraft.throttle > 0.1:
                    flame_length = int(15 * scale * self.aircraft.throttle)
                    flame_pos = tail_pos - direction * flame_length
                    flame_screen = self.world.project_3d_to_2d(flame_pos, self.camera_position, self.aircraft.rotation)
                    
                    if flame_screen:
                        # 불꽃 그라데이션
                        for i in range(3):
                            flame_color = (
                                min(255, 255 - i * 30),
                                min(255, 200 - i * 50),
                                0
                            )
                            flame_size = int((6 - i * 2) * scale)
                            if flame_size > 0:
                                pygame.draw.circle(self.screen, flame_color, flame_screen, flame_size)
        
    def run(self):
        """메인 게임 루프"""
        print("=" * 50)
        print("Advanced Flight Simulator with Mission Profile")
        print("=" * 50)
        print("\nControls:")
        print("  W/S: Pitch (Up/Down)")
        print("  A/D: Roll (Left/Right)")
        print("  Q/E: Yaw (Left/Right)")
        print("  Shift/Ctrl: Throttle (Up/Down)")
        print("  Space: Auto-level")
        print("  C: Change Camera Mode")
        print("  M: Toggle Mission Profile Display")
        print("  Tab: Toggle Detailed HUD")
        print("  P: Pause")
        print("  R: Restart (after crash)")
        print("  ESC: Quit")
        print("\nMission Profile: WUTO → Climb → Cruise → Turn → Descent → Landing")
        print("\n")
        
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.render()
            
        pygame.quit()
        sys.exit()

def main():
    sim = FlightSimulator()
    sim.run()

if __name__ == "__main__":
    main()