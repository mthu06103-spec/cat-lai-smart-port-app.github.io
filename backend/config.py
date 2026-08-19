"""
Cấu hình chính cho ứng dụng backend
Cảng container thông minh Cát Lái - Mô phỏng DES
"""
from typing import Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()

# Cấu hình chế độ chạy
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Cấu hình mô phỏng DES
SIMULATION_TIME_UNIT = "hour"  # Đơn vị thời gian: hour, minute, second
RANDOM_SEED = int(os.getenv("RANDOM_SEED", 42))

# Cấu hình cảng Cát Lái
class YardConfig:
    """Cấu hình bãi container"""
    TOTAL_BLOCKS = 12  # Số block bãi
    CONTAINERS_PER_BLOCK = 200  # Dung lượng container mỗi block
    QUAY_CRANES = 6  # Số cẩu bờ
    RTG_CRANES = 15  # Số cẩu RTG (Rubber Tyred Gantry)
    GATE_LANES = 8  # Số làn cổng
    SMART_GATE_LATENCY_MS = 10  # Độ trễ Smart Gate (ms)
    
    # Tham số tối ưu hóa
    BERTH_LENGTH_METERS = 1200  # Chiều dài bến (m)
    BERTH_SLOTS = 6  # Số vị trí bến tĩnh
    
    # Thông số hiệu suất
    CRANE_PRODUCTIVITY_IMPROVEMENT = 0.15  # Tăng 15%
    CO2_REDUCTION_TARGET = 0.28  # Giảm 28% CO2
    SAFETY_INCIDENT_REDUCTION = 0.30  # Giảm 30% sự cố


class VesselType(str, Enum):
    """Loại tàu"""
    SMALL = "small"      # <500 TEU
    MEDIUM = "medium"    # 500-3000 TEU
    LARGE = "large"      # 3000-10000 TEU
    XLARGE = "xlarge"    # >10000 TEU


class ContainerType(str, Enum):
    """Loại container"""
    EMPTY_20FT = "empty_20ft"
    EMPTY_40FT = "empty_40ft"
    FULL_20FT = "full_20ft"
    FULL_40FT = "full_40ft"
    REEFER = "reefer"


@dataclass
class SimulationConfig:
    """Cấu hình tham số mô phỏng"""
    simulation_duration_hours: float = 24.0  # Thời gian chạy mô phỏng
    random_seed: int = RANDOM_SEED
    num_vessels_per_day: int = 8  # Số tàu cập bến trong 24h
    avg_vessel_size_teu: int = 5000  # Kích thước tàu trung bình
    
    # Thời gian xử lý
    avg_load_unload_time_per_move: float = 2.0  # phút/cMove (container)
    avg_vessel_waiting_time_manual: float = 8.0  # giờ (thủ công FIFS)
    
    # Tài nguyên
    quay_cranes_available: int = YardConfig.QUAY_CRANES
    rtg_cranes_available: int = YardConfig.RTG_CRANES
    
    # Tối ưu hóa
    stow_optimization_enabled: bool = True
    stack_optimization_enabled: bool = True
    
    metrics: Dict[str, Any] = field(default_factory=lambda: {
        "vessel_waiting_time_reduction": 0.51,  # 51% giảm
        "shifter_reduction": 0.52,  # 52% giảm
        "fuel_consumption_reduction": 0.25,  # 25% giảm
        "co2_emission_reduction": 0.28,  # 28% giảm
        "safety_improvement": 0.30,  # 30% cải thiện
    })


# Cấu hình Telemetry 5G
@dataclass
class TelemetryConfig:
    """Cấu hình cảm biến và telemetry"""
    # LiDAR 3D
    lidar_frequency_hz: int = 100  # Tần số quét LiDAR
    lidar_accuracy_mm: float = 2.0  # Độ chính xác 2mm
    lidar_range_meters: float = 100  # Tầm quét 100m
    
    # Strain Gauges
    strain_gauge_frequency_hz: int = 100  # Tần số lấy mẫu
    
    # Buoy (Phao thông minh)
    buoy_data_interval_minutes: int = 15  # Chu kỳ truyền dữ liệu
    
    # 5G Network
    network_latency_ms: float = 10  # Độ trễ mạng 5G
    data_transmission_rate_mbps: float = 100  # Tốc độ truyền


# Cấu hình bảo mật
@dataclass
class SecurityConfig:
    """Cấu hình bảo mật"""
    aes_key_size: int = 256  # AES-256
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    enable_cors: bool = True
    cors_origins: list = field(default_factory=lambda: ["*"])


# Khởi tạo cấu hình mặc định
DEFAULT_SIMULATION_CONFIG = SimulationConfig()
DEFAULT_TELEMETRY_CONFIG = TelemetryConfig()
DEFAULT_SECURITY_CONFIG = SecurityConfig()
