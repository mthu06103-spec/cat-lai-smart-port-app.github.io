"""
Mô hình dữ liệu cho Bãi Container (Yard)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
from enum import Enum


class BlockStatus(str, Enum):
    """Trạng thái block bãi"""
    AVAILABLE = "available"      # Có chỗ trống
    FULL = "full"                # Đầy
    MAINTENANCE = "maintenance"  # Bảo trì
    CLOSED = "closed"            # Đóng cửa


@dataclass
class ContainerStack:
    """Một cột xếp container (Stack) trong block bãi"""
    stack_id: str = field(default_factory=lambda: f"STACK_{uuid.uuid4().hex[:6].upper()}")
    row_index: int = 0
    column_index: int = 0
    max_tiers: int = 6  # Tầng xếp chồng tối đa
    
    # Container trong stack (từ dưới lên trên, index 0 là tầng 1)
    containers: List[str] = field(default_factory=list)  # Lưu container_id
    
    # Trạng thái
    is_blocked: bool = False  # Bị chặn (khó lấy do có container lạnh hay nguy hiểm)
    last_access_time: Optional[datetime] = None
    
    def add_container(self, container_id: str) -> bool:
        """
        Thêm container vào stack
        """
        if len(self.containers) < self.max_tiers:
            self.containers.append(container_id)
            self.last_access_time = datetime.now()
            return True
        return False
    
    def remove_container(self) -> Optional[str]:
        """
        Lấy container ở tầng trên cùng (LIFO - Last In First Out)
        """
        if self.containers:
            self.last_access_time = datetime.now()
            return self.containers.pop()
        return None
    
    def get_occupancy_percentage(self) -> float:
        """Tính phần trăm lấp đầy của stack"""
        return (len(self.containers) / self.max_tiers) * 100
    
    def count_shifts_needed_for_container_at_tier(self, target_tier: int) -> int:
        """
        Tính số lần shift cần thiết để lấy container ở tầng chỉ định
        Công thức: số container phía trên tầng target
        """
        if target_tier >= len(self.containers) or target_tier < 0:
            return 0
        return len(self.containers) - target_tier - 1


@dataclass
class YardBlock:
    """Một block (khu) bãi container"""
    block_id: str = field(default_factory=lambda: f"BLK_{uuid.uuid4().hex[:6].upper()}")
    
    # Cấu hình block
    rows: int = 10  # Số hàng (row)
    columns: int = 20  # Số cột (column)
    max_tiers: int = 6  # Tầng xếp chồng tối đa
    
    # Thông tin block
    status: BlockStatus = BlockStatus.AVAILABLE
    capacity_teu: int = 200  # Dung lượng tính bằng TEU
    current_occupancy_teu: int = 0  # Dung lượng hiện tại
    
    # Grid stacks
    stacks: Dict[str, ContainerStack] = field(default_factory=dict)
    
    # Thông tin quản lý
    creation_time: datetime = field(default_factory=datetime.now)
    last_modification_time: datetime = field(default_factory=datetime.now)
    
    # Cẩu RTG
    rtg_crane_available: bool = True
    rtg_busy_until: Optional[datetime] = None
    
    # Thống kê
    total_shifts: int = 0  # Tổng số shifts thực hiện
    total_containers_processed: int = 0  # Tổng số container xử lý
    
    def __post_init__(self):
        """Khởi tạo grid stacks"""
        if not self.stacks:
            for i in range(self.rows):
                for j in range(self.columns):
                    stack_id = f"{self.block_id}_R{i:02d}C{j:02d}"
                    self.stacks[stack_id] = ContainerStack(
                        stack_id=stack_id,
                        row_index=i,
                        column_index=j,
                        max_tiers=self.max_tiers,
                    )
    
    def get_occupancy_percentage(self) -> float:
        """Tính phần trăm lấp đầy của block"""
        return (self.current_occupancy_teu / self.capacity_teu) * 100
    
    def get_available_stacks(self) -> List[ContainerStack]:
        """Lấy danh sách các stack còn chỗ trống"""
        return [s for s in self.stacks.values() 
                if len(s.containers) < s.max_tiers and not s.is_blocked]
    
    def place_container(self, container_id: str, row: int, column: int) -> bool:
        """
        Đặt container vào vị trí cụ thể
        """
        stack_id = f"{self.block_id}_R{row:02d}C{column:02d}"
        if stack_id in self.stacks:
            if self.stacks[stack_id].add_container(container_id):
                self.current_occupancy_teu += 1
                self.last_modification_time = datetime.now()
                self.total_containers_processed += 1
                return True
        return False
    
    def get_stack_by_position(self, row: int, column: int) -> Optional[ContainerStack]:
        """Lấy stack theo vị trí hàng/cột"""
        stack_id = f"{self.block_id}_R{row:02d}C{column:02d}"
        return self.stacks.get(stack_id)
    
    def is_full(self) -> bool:
        """Kiểm tra block đã đầy"""
        return self.current_occupancy_teu >= self.capacity_teu or self.status == BlockStatus.FULL


@dataclass
class Yard:
    """Bãi container chính"""
    yard_id: str = field(default_factory=lambda: f"YARD_{uuid.uuid4().hex[:6].upper()}")
    yard_name: str = "Cát Lái Port - Container Yard"
    
    # Cấu hình
    total_blocks: int = 12
    blocks: List[YardBlock] = field(default_factory=list)
    
    # Tài nguyên
    rtg_cranes_total: int = 15  # Tổng số cẩu RTG
    rtg_cranes_available: int = 15  # Số cẩu RTG còn trống
    
    # Cổng
    gate_lanes: int = 8
    gate_lanes_available: int = 8
    
    # Thống kê
    total_containers_in_yard: int = 0
    total_teu_capacity: int = 0
    total_teu_occupied: int = 0
    total_shifts_daily: int = 0
    
    # Thời gian
    creation_time: datetime = field(default_factory=datetime.now)
    
    # Phát thải
    daily_co2_emission_kg: float = 0.0
    
    def __post_init__(self):
        """Khởi tạo blocks"""
        if not self.blocks:
            for i in range(self.total_blocks):
                block = YardBlock(
                    block_id=f"BLK{i:02d}",
                    rows=10,
                    columns=20,
                    max_tiers=6,
                    capacity_teu=200,
                )
                self.blocks.append(block)
            self.total_teu_capacity = sum(b.capacity_teu for b in self.blocks)
    
    def get_occupancy_percentage(self) -> float:
        """Tính phần trăm lấp đầy của toàn bộ bãi"""
        if self.total_teu_capacity == 0:
            return 0.0
        return (self.total_teu_occupied / self.total_teu_capacity) * 100
    
    def get_available_blocks(self) -> List[YardBlock]:
        """Lấy danh sách blocks còn chỗ trống"""
        return [b for b in self.blocks if not b.is_full()]
    
    def allocate_rtg_crane(self) -> bool:
        """
        Cấp phát cẩu RTG
        """
        if self.rtg_cranes_available > 0:
            self.rtg_cranes_available -= 1
            return True
        return False
    
    def release_rtg_crane(self) -> None:
        """Giải phóng cẩu RTG"""
        if self.rtg_cranes_available < self.rtg_cranes_total:
            self.rtg_cranes_available += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Lấy tóm tắt thông tin bãi"""
        return {
            "yard_id": self.yard_id,
            "yard_name": self.yard_name,
            "total_blocks": self.total_blocks,
            "total_containers_in_yard": self.total_containers_in_yard,
            "total_teu_capacity": self.total_teu_capacity,
            "total_teu_occupied": self.total_teu_occupied,
            "occupancy_percentage": round(self.get_occupancy_percentage(), 2),
            "rtg_cranes_available": self.rtg_cranes_available,
            "rtg_cranes_total": self.rtg_cranes_total,
            "gate_lanes_available": self.gate_lanes_available,
            "total_shifts_daily": self.total_shifts_daily,
            "daily_co2_emission_kg": round(self.daily_co2_emission_kg, 2),
            "blocks": [
                {
                    "block_id": b.block_id,
                    "occupancy_percentage": round(b.get_occupancy_percentage(), 2),
                    "containers_count": b.total_containers_processed,
                } for b in self.blocks
            ],
        }
