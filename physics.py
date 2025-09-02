"""
Physics Engine Helper Functions
Based on Aircraft Performance Equations
"""

import math

class AtmosphereISA:
    """국제표준대기 (ISA) 모델"""
    
    # ISA 상수
    SEA_LEVEL_TEMP = 288.15  # K (15°C)
    SEA_LEVEL_PRESSURE = 101325  # Pa
    SEA_LEVEL_DENSITY = 1.225  # kg/m³
    TEMP_LAPSE_RATE = -0.0065  # K/m
    GAS_CONSTANT = 287.05  # J/(kg·K)
    GRAVITY = 9.80665  # m/s²
    
    @staticmethod
    def get_temperature(altitude):
        """고도에서의 온도 계산"""
        if altitude < 11000:  # 대류권
            return AtmosphereISA.SEA_LEVEL_TEMP + AtmosphereISA.TEMP_LAPSE_RATE * altitude
        else:  # 성층권 (간단화)
            return 216.65  # K (-56.5°C)
            
    @staticmethod
    def get_pressure(altitude):
        """고도에서의 압력 계산"""
        if altitude < 11000:
            temp = AtmosphereISA.get_temperature(altitude)
            temp_ratio = temp / AtmosphereISA.SEA_LEVEL_TEMP
            exponent = -AtmosphereISA.GRAVITY / (AtmosphereISA.TEMP_LAPSE_RATE * AtmosphereISA.GAS_CONSTANT)
            return AtmosphereISA.SEA_LEVEL_PRESSURE * (temp_ratio ** exponent)
        else:
            # 11km에서의 압력
            p_11km = AtmosphereISA.get_pressure(10999)
            # 성층권에서의 압력 (등온)
            return p_11km * math.exp(-AtmosphereISA.GRAVITY * (altitude - 11000) / 
                                     (AtmosphereISA.GAS_CONSTANT * 216.65))
                                     
    @staticmethod
    def get_density(altitude):
        """고도에서의 밀도 계산"""
        pressure = AtmosphereISA.get_pressure(altitude)
        temperature = AtmosphereISA.get_temperature(altitude)
        return pressure / (AtmosphereISA.GAS_CONSTANT * temperature)
        
    @staticmethod
    def get_speed_of_sound(altitude):
        """고도에서의 음속 계산"""
        temperature = AtmosphereISA.get_temperature(altitude)
        gamma = 1.4  # 공기의 비열비
        return math.sqrt(gamma * AtmosphereISA.GAS_CONSTANT * temperature)
        

class PerformanceCalculator:
    """항공기 성능 계산"""
    
    @staticmethod
    def calculate_specific_range(velocity, fuel_flow, weight):
        """비항속거리 계산 (km/kg)
        SR = V / FF
        """
        if fuel_flow > 0:
            return velocity / fuel_flow
        return 0
        
    @staticmethod
    def calculate_specific_endurance(fuel_flow, weight):
        """비항속시간 계산 (hr/kg)
        SE = 1 / FF
        """
        if fuel_flow > 0:
            return 1 / fuel_flow
        return 0
        
    @staticmethod
    def calculate_specific_excess_power(thrust, drag, weight, velocity):
        """비잉여마력 계산 (m/s)
        Ps = (T - D) * V / W
        """
        if weight > 0:
            return (thrust - drag) * velocity / weight
        return 0
        
    @staticmethod
    def calculate_turn_radius(velocity, bank_angle):
        """선회 반경 계산 (m)
        r = V² / (g * tan(φ))
        """
        if bank_angle != 0:
            return (velocity ** 2) / (9.81 * math.tan(bank_angle))
        return float('inf')
        
    @staticmethod
    def calculate_turn_rate(velocity, bank_angle):
        """선회율 계산 (rad/s)
        ω = g * tan(φ) / V
        """
        if velocity > 0:
            return 9.81 * math.tan(bank_angle) / velocity
        return 0
        
    @staticmethod
    def calculate_load_factor(bank_angle):
        """하중계수 계산
        n = 1 / cos(φ)
        """
        return 1 / math.cos(bank_angle)
        
    @staticmethod
    def calculate_stall_speed(weight, air_density, wing_area, cl_max):
        """실속속도 계산 (m/s)
        Vs = sqrt(2 * W / (ρ * S * CLmax))
        """
        if air_density > 0 and wing_area > 0 and cl_max > 0:
            return math.sqrt(2 * weight / (air_density * wing_area * cl_max))
        return 0
        
    @staticmethod
    def calculate_best_climb_speed(weight, air_density, wing_area, cd0, k):
        """최적 상승 속도 계산 (m/s)
        Vy = sqrt(2 * W / (ρ * S)) * sqrt(K / CD0)^0.25
        """
        if air_density > 0 and wing_area > 0 and cd0 > 0:
            v_term = math.sqrt(2 * weight / (air_density * wing_area))
            efficiency = (k / cd0) ** 0.25
            return v_term * efficiency
        return 0
        
    @staticmethod
    def calculate_best_range_speed(weight, air_density, wing_area, cd0, k):
        """최적 항속거리 속도 계산 (m/s)
        Vbr = sqrt(2 * W / (ρ * S)) * sqrt(K / CD0)^0.25
        """
        if air_density > 0 and wing_area > 0 and cd0 > 0:
            return math.sqrt(2 * weight / (air_density * wing_area * math.sqrt(cd0 * k)))
        return 0
        
    @staticmethod
    def calculate_best_endurance_speed(weight, air_density, wing_area, cd0, k):
        """최적 체공 속도 계산 (m/s)
        Vbe = sqrt(2 * W / (ρ * S)) * sqrt(K / (3 * CD0))^0.25
        """
        if air_density > 0 and wing_area > 0 and cd0 > 0:
            return math.sqrt(2 * weight / (air_density * wing_area * math.sqrt(3 * cd0 * k)))
        return 0
        

class FlightEnvelope:
    """비행 포락선 계산"""
    
    @staticmethod
    def check_speed_limits(velocity, min_speed, max_speed):
        """속도 제한 확인"""
        if velocity < min_speed:
            return "STALL_WARNING"
        elif velocity > max_speed:
            return "OVERSPEED_WARNING"
        return "NORMAL"
        
    @staticmethod
    def check_g_limits(load_factor, max_positive_g, max_negative_g):
        """G 제한 확인"""
        if load_factor > max_positive_g:
            return "OVER_G_WARNING"
        elif load_factor < max_negative_g:
            return "NEGATIVE_G_WARNING"
        return "NORMAL"
        
    @staticmethod
    def check_altitude_limits(altitude, service_ceiling):
        """고도 제한 확인"""
        if altitude > service_ceiling:
            return "CEILING_WARNING"
        elif altitude < 0:
            return "TERRAIN_WARNING"
        return "NORMAL"
        

class FuelCalculator:
    """연료 계산"""
    
    @staticmethod
    def calculate_fuel_flow(thrust, tsfc):
        """연료 소모율 계산 (kg/s)
        FF = T * TSFC
        TSFC: Thrust Specific Fuel Consumption (kg/N/s)
        """
        return thrust * tsfc
        
    @staticmethod
    def calculate_range(fuel_available, specific_range):
        """항속거리 계산 (km)
        R = Fuel * SR
        """
        return fuel_available * specific_range
        
    @staticmethod
    def calculate_endurance(fuel_available, fuel_flow):
        """체공시간 계산 (hours)
        E = Fuel / FF
        """
        if fuel_flow > 0:
            return fuel_available / fuel_flow
        return 0
        
    @staticmethod
    def calculate_reserve_fuel(cruise_fuel_flow, reserve_time):
        """예비 연료 계산 (kg)
        Reserve = FF * time
        """
        return cruise_fuel_flow * reserve_time