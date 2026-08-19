"""
Mô hình dữ liệu cho Tàu (Vessel)
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class VesselStatus(str, Enum):
    """Trạng thái tàu"""
    SCHEDULED = "scheduled"  # Lên lịch
    ARRIVED = "arrived"  # Đã cập bến
    BERTHED = "berthed"  # Đang neo đậu
    LOADING = "loading"  # Đang bốc/dỡ
    UNLOADING = "unloading"  # Đang dỡ
    WAITING = "waiting"  # Đang chờ bến
    DEPARTED = "departed"  # Đã rời đi


@dataclass
class BerthAllocation:
    """Thông tin gán bến cho tàu"""
    berth_id: str  # ID bến
    berth_start_position: float  # Vị trí bắt đầu bến (m)
    berth_length_occupied: float  # Chiều dài tàu chiếm dụng (m)
    quay_cranes_allocated: int  # Số cẩu bờ gán
    allocation_time: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "berth_id": self.berth_id,
            "berth_start_position": self.berth_start_position,
            "berth_length_occupied": self.berth_length_occupied,
            "quay_cranes_allocated": self.quay_cranes_allocated,
            "allocation_time": self.allocation_time.isoformat(),
        }


@dataclass
class Vessel:
    """Mô hình tàu container"""
    ship_id: str = field(default_factory=lambda: f"SHIP_{uuid.uuid4().hex[:8].upper()}")
    ship_name: str = ""
    vessel_type: str = "large"  # small, medium, large, xlarge
    
    # Thông số tàu
    length_meters: float = 290.0  # Chiều dài tàu (m)
    beam_meters: float = 32.0  # Bề rộng tàu (m)
    capacity_teu: int = 5000  # Dung lượng (TEU - Twenty-foot Equivalent Unit)
    current_load_teu: int = 3500  # Tải trọng hiện tại
    
    # Thời gian
    arrival_time: datetime = field(default_factory=datetime.now)
    estimated_service_time_hours: float = 8.0  # Thời gian dịch vụ ước tính
    actual_service_time_hours: Optional[float] = None  # Thời gian dịch vụ thực tế
    waiting_time_hours: float = 0.0  # Thời gian chờ đợi
    
    # Thông tin chi tiết containers
    containers_to_load: int = 1500  # Số container cần bốc (load)
    containers_to_unload: int = 2000  # Số container cần dỡ (unload)
    containers_loaded: int = 0  # Container đã bốc
    containers_unloaded: int = 0  # Container đã dỡ
    
    # Trạng thái
    status: VesselStatus = VesselStatus.SCHEDULED
    berth_allocation: Optional[BerthAllocation] = None
    
    # Thông tin tối ưu hóa
    optimized_service_time_hours: Optional[float] = None
    optimization_applied: bool = False
    
    # Phát thải CO2 (kg)
    estimated_co2_emission_kg: float = 1500.0  # Ước tính
    actual_co2_emission_kg: Optional[float] = None  # Thực tế
    
    # ID trích xuất dữ liệu
    voyage_id: str = field(default_factory=lambda: f"VOY_{uuid.uuid4().hex[:8].upper()}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Lấy tóm tắt thông tin tàu"""
        return {
            "ship_id": self.ship_id,
            "ship_name": self.ship_name,
            "vessel_type": self.vessel_type,
            "capacity_teu": self.capacity_teu,
            "current_load_teu": self.current_load_teu,
            "status": self.status.value,
            "arrival_time": self.arrival_time.isoformat(),
            "estimated_service_time_hours": self.estimated_service_time_hours,
            "actual_service_time_hours": self.actual_service_time_hours,
            "waiting_time_hours": round(self.waiting_time_hours, 2),
            "containers_to_load": self.containers_to_load,
            "containers_to_unload": self.containers_to_unload,
            "containers_loaded": self.containers_loaded,
            "containers_unloaded": self.containers_unloaded,
            "optimization_applied": self.optimization_applied,
            "optimized_service_time_hours": self.optimized_service_time_hours,
            "estimated_co2_emission_kg": round(self.estimated_co2_emission_kg, 2),
            "actual_co2_emission_kg": self.actual_co2_emission_kg,
            "berth_allocation": self.berth_allocation.to_dict() if self.berth_allocation else None,
        }
    
    def update_status(self, new_status: VesselStatus) -> None:
        """Cập nhật trạng thái tàu"""
        self.status = new_status
    
    def calculate_service_progress(self) -> float:
        """
        Tính toán tiến độ dịch vụ (%)
        """
        total_containers = self.containers_to_load + self.containers_to_unload
        if total_containers == 0:
            return 0.0
        processed = self.containers_loaded + self.containers_unloaded
        return (processed / total_containers) * 100
    
    def calculate_actual_co2_emission(self) -> float:
        """
        Tính toán phát thải CO2 thực tế dựa trên thời gian chờ đợi
        Công thức: CO2 = base_emission + (waiting_time * hourly_emission_rate)
        """
        base_emission = 500.0  # kg CO2 cơ bản
        hourly_emission_rate = 200.0  # kg/hour CO2 từ chờ đợi
        self.actual_co2_emission_kg = base_emission + (self.waiting_time_hours * hourly_emission_rate)
        return self.actual_co2_emission_kg
