"""
3D World Environment
Buildings, Terrain, Trees, and Mountains
"""

import pygame
import math
import random
import numpy as np

class Building:
    """건물 클래스"""
    def __init__(self, x, z, width, height, depth):
        self.position = pygame.math.Vector3(x, 0, z)
        self.width = width
        self.height = height
        self.depth = depth
        self.color = (
            random.randint(100, 180),
            random.randint(100, 180),
            random.randint(100, 180)
        )
        
class Tree:
    """나무 클래스"""
    def __init__(self, x, z, height):
        self.position = pygame.math.Vector3(x, 0, z)
        self.height = height
        self.trunk_color = (101, 67, 33)  # 갈색
        self.leaves_color = (34, 139, 34)  # 녹색
        
class Mountain:
    """산 클래스"""
    def __init__(self, x, z, radius, height):
        self.position = pygame.math.Vector3(x, 0, z)
        self.radius = radius
        self.height = height
        self.color = (105, 105, 105)  # 회색

class World:
    """3D 월드 환경"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 지형 생성
        self.terrain_size = 100
        self.terrain_scale = 50
        self.height_map = self._generate_terrain()
        
        # 객체들 생성
        self.buildings = self._generate_buildings()
        self.trees = self._generate_trees()
        self.mountains = self._generate_mountains()
        self.clouds = self._generate_clouds()
        
        # 렌더링 거리
        self.render_distance = 5000
        
    def _generate_terrain(self):
        """지형 높이맵 생성"""
        height_map = np.zeros((self.terrain_size, self.terrain_size))
        
        # Perlin noise 간단한 구현
        for i in range(5):  # 여러 옥타브
            scale = 2 ** i
            amplitude = 50 / scale
            
            for x in range(self.terrain_size):
                for y in range(self.terrain_size):
                    height_map[x, y] += amplitude * np.sin(x / (10 * scale)) * np.cos(y / (10 * scale))
                    
        return height_map
        
    def _generate_buildings(self):
        """건물 생성"""
        buildings = []
        
        # 도시 지역 (중앙 근처)
        for _ in range(30):
            x = random.randint(-1000, 1000)
            z = random.randint(-1000, 1000)
            
            # 중앙에서 멀수록 건물이 낮아짐
            distance_from_center = math.sqrt(x**2 + z**2)
            max_height = max(50, 300 - distance_from_center / 10)
            
            width = random.randint(30, 80)
            height = random.randint(50, int(max_height))
            depth = random.randint(30, 80)
            
            buildings.append(Building(x, z, width, height, depth))
            
        # 공항 근처 건물 (낮은 건물)
        for _ in range(10):
            x = random.randint(-300, 300)
            z = random.randint(-300, 300)
            width = random.randint(40, 100)
            height = random.randint(20, 50)  # 낮은 건물
            depth = random.randint(40, 100)
            
            buildings.append(Building(x, z, width, height, depth))
            
        return buildings
        
    def _generate_trees(self):
        """나무 생성"""
        trees = []
        
        # 숲 지역
        for _ in range(100):
            # 건물이 없는 외곽 지역에 나무 배치
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(1500, 3000)
            
            x = distance * math.cos(angle)
            z = distance * math.sin(angle)
            height = random.randint(10, 30)
            
            trees.append(Tree(x, z, height))
            
        return trees
        
    def _generate_mountains(self):
        """산 생성"""
        mountains = []
        
        # 원거리에 큰 산들 배치
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(3000, 5000)
            
            x = distance * math.cos(angle)
            z = distance * math.sin(angle)
            radius = random.randint(300, 600)
            height = random.randint(200, 500)
            
            mountains.append(Mountain(x, z, radius, height))
            
        return mountains
        
    def _generate_clouds(self):
        """구름 생성"""
        clouds = []
        
        for _ in range(20):
            cloud = {
                'position': pygame.math.Vector3(
                    random.randint(-3000, 3000),
                    random.randint(400, 1000),
                    random.randint(-3000, 3000)
                ),
                'size': random.randint(50, 150),
                'speed': random.uniform(5, 15)
            }
            clouds.append(cloud)
            
        return clouds
        
    def get_terrain_height(self, x, z):
        """특정 위치의 지형 높이 반환"""
        # 그리드 좌표로 변환
        grid_x = int(x / self.terrain_scale + self.terrain_size / 2)
        grid_z = int(z / self.terrain_scale + self.terrain_size / 2)
        
        # 범위 체크
        if 0 <= grid_x < self.terrain_size and 0 <= grid_z < self.terrain_size:
            base_height = self.height_map[grid_x, grid_z]
        else:
            base_height = 0
            
        # 산 높이 추가
        for mountain in self.mountains:
            dist = math.sqrt((x - mountain.position.x)**2 + (z - mountain.position.z)**2)
            if dist < mountain.radius:
                # 산의 높이 프로파일 (원뿔 형태)
                mountain_height = mountain.height * (1 - dist / mountain.radius)
                base_height = max(base_height, mountain_height)
                
        return base_height
        
    def check_building_collision(self, aircraft_pos, building):
        """건물과의 충돌 거리 계산"""
        # 건물의 바운딩 박스
        min_x = building.position.x - building.width / 2
        max_x = building.position.x + building.width / 2
        min_z = building.position.z - building.depth / 2
        max_z = building.position.z + building.depth / 2
        min_y = 0
        max_y = building.height
        
        # 항공기와 건물 사이의 최단 거리
        dx = max(min_x - aircraft_pos.x, 0, aircraft_pos.x - max_x)
        dy = max(min_y - aircraft_pos.y, 0, aircraft_pos.y - max_y)
        dz = max(min_z - aircraft_pos.z, 0, aircraft_pos.z - max_z)
        
        return math.sqrt(dx*dx + dy*dy + dz*dz)
        
    def project_3d_to_2d(self, point3d, camera_pos, aircraft_rotation):
        """3D 좌표를 2D 화면 좌표로 변환"""
        # 카메라 상대 좌표
        relative = point3d - camera_pos
        
        # 항공기 회전 적용
        relative = self.rotate_vector(relative, -aircraft_rotation.y, 'y')
        relative = self.rotate_vector(relative, -aircraft_rotation.x * 0.5, 'x')
        
        # 카메라 뒤에 있는 객체는 렌더링하지 않음
        if relative.z <= 0:
            return None
            
        # 원근 투영
        fov = 60
        factor = (self.screen_height / 2) / math.tan(math.radians(fov / 2))
        x = self.screen_width / 2 + (relative.x * factor / relative.z)
        y = self.screen_height / 2 - (relative.y * factor / relative.z)
        
        return (int(x), int(y))
        
    def rotate_vector(self, vector, angle, axis):
        """벡터 회전"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        if axis == 'y':
            x = vector.x * cos_a + vector.z * sin_a
            y = vector.y
            z = -vector.x * sin_a + vector.z * cos_a
        elif axis == 'x':
            x = vector.x
            y = vector.y * cos_a - vector.z * sin_a
            z = vector.y * sin_a + vector.z * cos_a
        else:
            return vector
            
        return pygame.math.Vector3(x, y, z)
        
    def update(self, dt, aircraft_pos):
        """월드 업데이트"""
        # 구름 이동
        for cloud in self.clouds:
            cloud['position'].x += cloud['speed'] * dt
            if cloud['position'].x > 3500:
                cloud['position'].x = -3500
                
    def render(self, screen, camera_pos, aircraft_rotation):
        """월드 렌더링"""
        # 하늘과 지평선
        self.render_sky_and_horizon(screen, aircraft_rotation)
        
        # 지형
        self.render_terrain(screen, camera_pos, aircraft_rotation)
        
        # 산
        self.render_mountains(screen, camera_pos, aircraft_rotation)
        
        # 나무
        self.render_trees(screen, camera_pos, aircraft_rotation)
        
        # 건물
        self.render_buildings(screen, camera_pos, aircraft_rotation)
        
        # 구름
        self.render_clouds(screen, camera_pos, aircraft_rotation)
        
    def render_sky_and_horizon(self, screen, aircraft_rotation):
        """하늘과 지평선 렌더링"""
        # 하늘 그라데이션
        for i in range(self.screen_height // 2):
            color_ratio = i / (self.screen_height // 2)
            color = (
                int(135 * (1 - color_ratio) + 200 * color_ratio),
                int(206 * (1 - color_ratio) + 230 * color_ratio),
                235
            )
            pygame.draw.line(screen, color, (0, i), (self.screen_width, i))
            
        # 지면
        horizon_y = self.screen_height // 2 - int(aircraft_rotation.x * 200)
        pygame.draw.rect(screen, (34, 139, 34), 
                        (0, horizon_y, self.screen_width, self.screen_height - horizon_y))
                        
    def render_terrain(self, screen, camera_pos, aircraft_rotation):
        """지형 렌더링"""
        # 간단한 그리드 렌더링
        grid_size = 100
        grid_count = 30
        
        for i in range(-grid_count, grid_count, 2):
            for j in range(-grid_count, grid_count, 2):
                x = i * grid_size
                z = j * grid_size
                y = -self.get_terrain_height(x, z)
                
                point = pygame.math.Vector3(x, y, z)
                screen_pos = self.project_3d_to_2d(point, camera_pos, aircraft_rotation)
                
                if screen_pos:
                    distance = math.sqrt((x - camera_pos.x)**2 + (z - camera_pos.z)**2)
                    if distance < self.render_distance:
                        # 거리에 따른 색상 페이드
                        fade = max(0, 1 - distance / self.render_distance)
                        color = (int(34 * fade), int(139 * fade), int(34 * fade))
                        if color[0] > 0:
                            size = max(1, int(30 / (distance / 100 + 1)))
                            pygame.draw.circle(screen, color, screen_pos, size)
                            
    def render_buildings(self, screen, camera_pos, aircraft_rotation):
        """건물 렌더링"""
        for building in self.buildings:
            distance = math.sqrt(
                (building.position.x - camera_pos.x)**2 + 
                (building.position.z - camera_pos.z)**2
            )
            
            if distance < self.render_distance:
                # 건물의 8개 꼭짓점
                vertices = []
                for dx in [-building.width/2, building.width/2]:
                    for dy in [0, building.height]:
                        for dz in [-building.depth/2, building.depth/2]:
                            point = pygame.math.Vector3(
                                building.position.x + dx,
                                -dy,  # Y축 반전
                                building.position.z + dz
                            )
                            screen_pos = self.project_3d_to_2d(point, camera_pos, aircraft_rotation)
                            if screen_pos:
                                vertices.append(screen_pos)
                                
                # 건물 면 그리기
                if len(vertices) >= 4:
                    fade = max(0.3, 1 - distance / self.render_distance)
                    color = tuple(int(c * fade) for c in building.color)
                    
                    # 앞면
                    if len(vertices) >= 4:
                        pygame.draw.polygon(screen, color, vertices[:4])
                        
    def render_trees(self, screen, camera_pos, aircraft_rotation):
        """나무 렌더링"""
        for tree in self.trees:
            distance = math.sqrt(
                (tree.position.x - camera_pos.x)**2 + 
                (tree.position.z - camera_pos.z)**2
            )
            
            if distance < self.render_distance / 2:  # 나무는 가까운 거리에서만
                # 나무 줄기
                trunk_bottom = pygame.math.Vector3(tree.position.x, 0, tree.position.z)
                trunk_top = pygame.math.Vector3(tree.position.x, -tree.height * 0.6, tree.position.z)
                
                bottom_pos = self.project_3d_to_2d(trunk_bottom, camera_pos, aircraft_rotation)
                top_pos = self.project_3d_to_2d(trunk_top, camera_pos, aircraft_rotation)
                
                if bottom_pos and top_pos:
                    pygame.draw.line(screen, tree.trunk_color, bottom_pos, top_pos, 3)
                    
                    # 나뭇잎
                    leaves_pos = pygame.math.Vector3(tree.position.x, -tree.height * 0.8, tree.position.z)
                    leaves_screen = self.project_3d_to_2d(leaves_pos, camera_pos, aircraft_rotation)
                    if leaves_screen:
                        size = max(5, int(tree.height * 100 / (distance + 100)))
                        pygame.draw.circle(screen, tree.leaves_color, leaves_screen, size)
                        
    def render_mountains(self, screen, camera_pos, aircraft_rotation):
        """산 렌더링"""
        for mountain in self.mountains:
            distance = math.sqrt(
                (mountain.position.x - camera_pos.x)**2 + 
                (mountain.position.z - camera_pos.z)**2
            )
            
            if distance < self.render_distance * 1.5:
                # 산 정상
                peak = pygame.math.Vector3(
                    mountain.position.x,
                    -mountain.height,
                    mountain.position.z
                )
                
                peak_screen = self.project_3d_to_2d(peak, camera_pos, aircraft_rotation)
                
                if peak_screen:
                    # 산 기반 점들
                    base_points = []
                    for angle in range(0, 360, 45):
                        rad = math.radians(angle)
                        base_x = mountain.position.x + mountain.radius * math.cos(rad)
                        base_z = mountain.position.z + mountain.radius * math.sin(rad)
                        base_point = pygame.math.Vector3(base_x, 0, base_z)
                        
                        base_screen = self.project_3d_to_2d(base_point, camera_pos, aircraft_rotation)
                        if base_screen:
                            base_points.append(base_screen)
                            
                    # 산 그리기
                    if base_points:
                        fade = max(0.3, 1 - distance / (self.render_distance * 1.5))
                        color = tuple(int(c * fade) for c in mountain.color)
                        
                        for base_point in base_points:
                            pygame.draw.polygon(screen, color, 
                                              [peak_screen, base_point, 
                                               base_points[(base_points.index(base_point) + 1) % len(base_points)]])
                                               
    def render_clouds(self, screen, camera_pos, aircraft_rotation):
        """구름 렌더링"""
        for cloud in self.clouds:
            screen_pos = self.project_3d_to_2d(cloud['position'], camera_pos, aircraft_rotation)
            
            if screen_pos:
                distance = math.sqrt(
                    (cloud['position'].x - camera_pos.x)**2 +
                    (cloud['position'].z - camera_pos.z)**2
                )
                
                if distance < self.render_distance:
                    size = int(cloud['size'] * 500 / (distance + 500))
                    if size > 0:
                        # 구름을 여러 원으로 표현
                        for i in range(3):
                            offset_x = random.randint(-size//2, size//2)
                            offset_y = random.randint(-size//4, size//4)
                            pygame.draw.circle(screen, (255, 255, 255),
                                            (screen_pos[0] + offset_x, screen_pos[1] + offset_y),
                                            size // 2)