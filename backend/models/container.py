"""
Mô hình dữ liệu cho Container
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class ContainerType(str, Enum):
    """Loại container"""
    EMPTY_20FT = "empty_20ft"  # Container 20 feet rỗng
    EMPTY_40FT = "empty_40ft"  # Container 40 feet rỗng
    FULL_20FT = "full_20ft"    # Container 20 feet đầy
    FULL_40FT = "full_40ft"    # Container 40 feet đầy
    REEFER = "reefer"          # Container lạnh (Reefer)


class ContainerStatus(str, Enum):
    """Trạng thái container"""
    ON_VESSEL = "on_vessel"      # Trên tàu
    IN_YARD = "in_yard"          # Trong bãi
    AT_GATE = "at_gate"          # Ở cổng
    ON_TRUCK = "on_truck"        # Trên xe tải
    IN_TRANSIT = "in_transit"    # Đang vận chuyển
    STOWED = "stowed"            # Đã xếp chặt


class ContainerDestination(str, Enum):
    """Đích đến container"""
    IMPORT = "import"        # Nhập khẩu (từ tàu về bãi)
    EXPORT = "export"        # Xuất khẩu (từ bãi lên tàu)
    TRANSSHIPMENT = "transshipment"  # Chuyển cảng


@dataclass
class YardPosition:
    """Vị trí container trong bãi"""
    block_id: str           # ID block bãi
    row_index: int          # Hàng (0-10)
    column_index: int       # Cột (0-20)
    tier_index: int         # Tầng xếp chồng (0-5)
    assignment_time: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        return f"Block{self.block_id}({self.row_index},{self.column_index},{self.tier_index})"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_id": self.block_id,
            "row": self.row_index,
            "column": self.column_index,
            "tier": self.tier_index,
            "assignment_time": self.assignment_time.isoformat(),
        }


@dataclass
class Container:
    """Mô hình container"""
    container_id: str = field(default_factory=lambda: f"CONT_{uuid.uuid4().hex[:10].upper()}")
    
    # Thông tin cơ bản
    container_type: ContainerType = ContainerType.FULL_20FT
    container_size_feet: int = 20  # 20 hoặc 40 feet
    teu_equivalent: float = 1.0    # TEU (20ft = 1 TEU, 40ft = 2 TEU)
    
    # Trạng thái
    status: ContainerStatus = ContainerStatus.ON_VESSEL
    destination: ContainerDestination = ContainerDestination.IMPORT
    
    # Vị trí
    current_yard_position: Optional[YardPosition] = None
    vessel_bay_position: Optional[str] = None  # Vị trí trên tàu (ví dụ: "Bay123Stack3Tier4")
    
    # Thời gian
    arrival_time: datetime = field(default_factory=datetime.now)
    placement_time: Optional[datetime] = None  # Thời gian đặt vào bãi
    retrieval_time: Optional[datetime] = None  # Thời gian lấy ra khỏi bãi
    
    # Trọng lượng
    weight_kg: float = 18000.0  # Trọng lượng (kg)
    is_overweight: bool = False  # Có vượt trọng lượng
    
    # Nội dung
    cargo_description: str = "General Cargo"
    is_hazardous: bool = False  # Hàng nguy hiểm
    is_reefer: bool = False     # Hàng lạnh cần điều khiển nhiệt độ
    temperature_required_celsius: Optional[float] = None  # Nhiệt độ yêu cầu (nếu có)
    
    # Số lần di chuyển bãi (Shifters)
    shift_count: int = 0  # Số lần phải dịch chuyển từ vị trí này sang vị trí khác
    
    # Tối ưu hóa
    optimization_applied: bool = False
    optimized_shift_count: Optional[int] = None
    
    # Mã số và hóa đơn
    booking_reference: str = ""
    bill_of_lading: str = ""
    
    # Phát thải CO2
    handling_co2_emission_kg: float = 5.0  # kg CO2 mỗi lần xử lý
    
    def get_summary(self) -> Dict[str, Any]:
        """Lấy tóm tắt thông tin container"""
        return {
            "container_id": self.container_id,
            "container_type": self.container_type.value,
            "container_size_feet": self.container_size_feet,
            "teu_equivalent": self.teu_equivalent,
            "status": self.status.value,
            "destination": self.destination.value,
            "weight_kg": self.weight_kg,
            "current_yard_position": self.current_yard_position.to_dict() if self.current_yard_position else None,
            "vessel_bay_position": self.vessel_bay_position,
            "shift_count": self.shift_count,
            "optimized_shift_count": self.optimized_shift_count,
            "is_hazardous": self.is_hazardous,
            "is_reefer": self.is_reefer,
            "cargo_description": self.cargo_description,
        }
    
    def calculate_handling_time_minutes(self, crane_productivity_factor: float = 1.0) -> float:
        """
        Tính toán thời gian xử lý container
        - Container 20ft: 2 phút
        - Container 40ft: 3.5 phút
        - Nhân với hệ số năng suất cẩu
        """
        base_time = 2.0 if self.container_size_feet == 20 else 3.5
        return base_time / crane_productivity_factor
    
    def update_status(self, new_status: ContainerStatus) -> None:
        """Cập nhật trạng thái container"""
        self.status = new_status
        
        if new_status == ContainerStatus.IN_YARD and self.placement_time is None:
            self.placement_time = datetime.now()
    
    def move_to_yard_position(self, new_position: YardPosition) -> None:
        """
        Di chuyển container đến vị trí bãi mới
        Tăng số lần shift nếu đã có vị trí trước đó
        """
        if self.current_yard_position is not None:
            self.shift_count += 1
        
        self.current_yard_position = new_position
        self.status = ContainerStatus.IN_YARD
    
    def calculate_total_co2_for_handling(self, number_of_moves: int = 1) -> float:
        """
        Tính toán tổng phát thải CO2 cho xử lý container
        """
        return self.handling_co2_emission_kg * number_of_moves
