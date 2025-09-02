"""
HUD (Head-Up Display) and UI System
Mission Profile Display and Performance Indicators
"""

import pygame
import math

class HUD:
    """HUD 및 UI 관리"""
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 폰트 설정
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # 색상 정의
        self.HUD_GREEN = (0, 255, 0)
        self.HUD_YELLOW = (255, 255, 0)
        self.HUD_RED = (255, 0, 0)
        self.HUD_WHITE = (255, 255, 255)
        self.HUD_DARK = (0, 0, 0)
        
        # 디스플레이 모드
        self.detailed_view = False
        self.show_mission_profile = True
        
    def render(self, aircraft, mission, collision_warning, warning_timer, crashed):
        """HUD 렌더링"""
        # 기본 HUD
        self.render_basic_hud(aircraft)
        
        # 미션 정보
        self.render_mission_info(mission)
        
        # 경고 시스템
        if collision_warning and not crashed:
            self.render_warning(warning_timer)
            
        # 상세 뷰
        if self.detailed_view:
            self.render_detailed_view(aircraft)
            
        # 미션 프로파일 그래프
        if self.show_mission_profile and mission.display_enabled:
            self.render_mission_profile(mission)
            
        # 중앙 조준점
        self.render_crosshair()
        
    def render_basic_hud(self, aircraft):
        """기본 HUD 렌더링"""
        # HUD 배경
        hud_surface = pygame.Surface((280, 200))
        hud_surface.set_alpha(180)
        hud_surface.fill(self.HUD_DARK)
        self.screen.blit(hud_surface, (10, 10))
        
        # 기본 정보
        info_lines = [
            f"ALTITUDE: {int(aircraft.position.y)} m",
            f"SPEED: {int(aircraft.velocity.length())} m/s",
            f"HEADING: {int(math.degrees(aircraft.rotation.y) % 360)}°",
            f"PITCH: {int(math.degrees(aircraft.rotation.x))}°",
            f"ROLL: {int(math.degrees(aircraft.rotation.z))}°",
            f"THROTTLE: {int(aircraft.throttle * 100)}%",
            f"FUEL: {int(aircraft.fuel_mass)} kg ({int(aircraft.fuel_mass/aircraft.fuel_capacity*100)}%)",
            f"RANGE: {int(aircraft.total_range/1000)} km"
        ]
        
        y_offset = 20
        for line in info_lines:
            # 연료 부족 경고
            if "FUEL" in line and aircraft.fuel_mass < aircraft.fuel_capacity * 0.2:
                color = self.HUD_YELLOW if aircraft.fuel_mass > aircraft.fuel_capacity * 0.1 else self.HUD_RED
            else:
                color = self.HUD_GREEN
                
            text = self.font_medium.render(line, True, color)
            self.screen.blit(text, (20, y_offset))
            y_offset += 22
            
    def render_mission_info(self, mission):
        """미션 정보 렌더링"""
        # 미션 상태 배경
        mission_surface = pygame.Surface((250, 80))
        mission_surface.set_alpha(180)
        mission_surface.fill(self.HUD_DARK)
        self.screen.blit(mission_surface, (self.screen_width - 260, 10))
        
        # 현재 세그먼트
        current_segment = mission.get_current_segment_name()
        text = self.font_medium.render(f"PHASE: {current_segment}", True, self.HUD_WHITE)
        self.screen.blit(text, (self.screen_width - 250, 20))
        
        # 미션 진행률
        progress = mission.get_mission_progress()
        text = self.font_small.render(f"Mission Progress: {progress:.1f}%", True, self.HUD_GREEN)
        self.screen.blit(text, (self.screen_width - 250, 45))
        
        # 미션 시간
        minutes = int(mission.total_time // 60)
        seconds = int(mission.total_time % 60)
        text = self.font_small.render(f"Mission Time: {minutes:02d}:{seconds:02d}", True, self.HUD_WHITE)
        self.screen.blit(text, (self.screen_width - 250, 65))
        
    def render_warning(self, warning_timer):
        """경고 렌더링"""
        # 깜빡이는 효과
        if int(warning_timer * 4) % 2 == 0:
            warning_text = "⚠ TERRAIN WARNING ⚠"
            text = self.font_large.render(warning_text, True, self.HUD_RED)
            text_rect = text.get_rect(center=(self.screen_width // 2, 100))
            
            # 배경
            bg_surface = pygame.Surface((text_rect.width + 20, text_rect.height + 10))
            bg_surface.fill(self.HUD_DARK)
            bg_surface.set_alpha(200)
            self.screen.blit(bg_surface, (text_rect.x - 10, text_rect.y - 5))
            
            # 텍스트
            self.screen.blit(text, text_rect)
            
            # 추가 경고
            sub_text = self.font_medium.render("PULL UP!", True, self.HUD_YELLOW)
            sub_rect = sub_text.get_rect(center=(self.screen_width // 2, 140))
            self.screen.blit(sub_text, sub_rect)
            
    def render_crosshair(self):
        """중앙 조준점 렌더링"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # 십자선
        pygame.draw.line(self.screen, self.HUD_GREEN, 
                        (center_x - 20, center_y), (center_x + 20, center_y), 2)
        pygame.draw.line(self.screen, self.HUD_GREEN,
                        (center_x, center_y - 20), (center_x, center_y + 20), 2)
        pygame.draw.circle(self.screen, self.HUD_GREEN, (center_x, center_y), 5, 2)
        
    def render_detailed_view(self, aircraft):
        """상세 정보 뷰"""
        # 상세 정보 배경
        detail_surface = pygame.Surface((300, 250))
        detail_surface.set_alpha(180)
        detail_surface.fill(self.HUD_DARK)
        self.screen.blit(detail_surface, (10, self.screen_height - 260))
        
        # 성능 데이터 (논문 기반)
        # 양력, 항력, 추력 계산
        speed = aircraft.velocity.length()
        if speed > 0:
            # 간단한 L/D 비율 계산
            alpha = aircraft.rotation.x
            CL = aircraft.CL0 + aircraft.CL_alpha * alpha
            CD = aircraft.CD0 + aircraft.K * CL * CL
            LD_ratio = CL / CD if CD > 0 else 0
            
            # 상승률
            climb_rate = aircraft.velocity.y
            
            # 항속거리 예측 (현재 연료와 소비율 기준)
            if aircraft.fuel_flow_rate * aircraft.throttle > 0:
                endurance = aircraft.fuel_mass / (aircraft.fuel_flow_rate * aircraft.throttle)
                range_estimate = speed * endurance
            else:
                endurance = 0
                range_estimate = 0
        else:
            LD_ratio = 0
            climb_rate = 0
            endurance = 0
            range_estimate = 0
            
        detail_lines = [
            "=== PERFORMANCE DATA ===",
            f"L/D Ratio: {LD_ratio:.2f}",
            f"Climb Rate: {climb_rate:.1f} m/s",
            f"Specific Range: {range_estimate/1000:.1f} km",
            f"Endurance: {endurance/60:.1f} min",
            "",
            "=== WEIGHT & BALANCE ===",
            f"Total Mass: {int(aircraft.get_total_mass())} kg",
            f"Empty Mass: {int(aircraft.mass)} kg",
            f"Fuel Mass: {int(aircraft.fuel_mass)} kg",
        ]
        
        y_offset = self.screen_height - 250
        for line in detail_lines:
            if "===" in line:
                color = self.HUD_YELLOW
            else:
                color = self.HUD_WHITE
                
            text = self.font_small.render(line, True, color)
            self.screen.blit(text, (20, y_offset))
            y_offset += 20
            
    def render_mission_profile(self, mission):
        """미션 프로파일 그래프 렌더링"""
        if len(mission.profile_data['altitude']) < 2:
            return
            
        # 그래프 영역
        graph_width = 400
        graph_height = 150
        graph_x = self.screen_width - graph_width - 20
        graph_y = self.screen_height - graph_height - 20
        
        # 그래프 배경
        graph_surface = pygame.Surface((graph_width, graph_height))
        graph_surface.set_alpha(200)
        graph_surface.fill(self.HUD_DARK)
        self.screen.blit(graph_surface, (graph_x, graph_y))
        
        # 그래프 테두리
        pygame.draw.rect(self.screen, self.HUD_GREEN, 
                        (graph_x, graph_y, graph_width, graph_height), 2)
                        
        # 제목
        title = self.font_small.render("Mission Profile", True, self.HUD_WHITE)
        self.screen.blit(title, (graph_x + 10, graph_y - 20))
        
        # 데이터 정규화
        altitudes = mission.profile_data['altitude']
        ranges = mission.profile_data['range']
        
        if altitudes and ranges:
            max_alt = max(altitudes) if max(altitudes) > 0 else 1
            max_range = max(ranges) if max(ranges) > 0 else 1
            
            # 고도 프로파일 그리기
            points = []
            for i in range(len(altitudes)):
                x = graph_x + 10 + (i / len(altitudes)) * (graph_width - 20)
                y = graph_y + graph_height - 10 - (altitudes[i] / max_alt) * (graph_height - 20)
                points.append((int(x), int(y)))
                
            if len(points) > 1:
                pygame.draw.lines(self.screen, self.HUD_GREEN, False, points, 2)
                
            # 현재 위치 표시
            current_idx = len(altitudes) - 1
            if current_idx >= 0:
                current_x = graph_x + 10 + (current_idx / len(altitudes)) * (graph_width - 20)
                current_y = graph_y + graph_height - 10 - (altitudes[current_idx] / max_alt) * (graph_height - 20)
                pygame.draw.circle(self.screen, self.HUD_YELLOW, 
                                 (int(current_x), int(current_y)), 4)
                                 
            # 축 라벨
            alt_label = self.font_small.render(f"Alt: {int(max_alt)}m", True, self.HUD_WHITE)
            self.screen.blit(alt_label, (graph_x + 10, graph_y + 5))
            
            range_label = self.font_small.render(f"Range: {int(max_range/1000)}km", True, self.HUD_WHITE)
            self.screen.blit(range_label, (graph_x + graph_width - 100, graph_y + graph_height - 20))
            
    def toggle_detailed_view(self):
        """상세 뷰 토글"""
        self.detailed_view = not self.detailed_view