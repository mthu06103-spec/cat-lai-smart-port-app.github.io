"""
Mô phỏng sự kiện rời rạc (DES) cho cảng container
Sử dụng SimPy - thư viện mô phỏng sự kiện rời rạc Python
"""

import simpy
import random
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SimulationMetrics:
    """Chỉ số mô phỏng"""
    total_vessels_processed: int = 0
    total_containers_processed: int = 0
    total_waiting_time_hours: float = 0.0
    total_service_time_hours: float = 0.0
    total_shifts_performed: int = 0
    total_co2_emission_kg: float = 0.0
    
    # Thống kê chi tiết
    vessel_waiting_times: List[float] = field(default_factory=list)
    vessel_service_times: List[float] = field(default_factory=list)
    quay_crane_utilization: float = 0.0
    rtg_crane_utilization: float = 0.0
    gate_utilization: float = 0.0
    
    def calculate_averages(self) -> Dict[str, float]:
        """Tính toán các chỉ số trung bình"""
        avg_waiting = (self.total_waiting_time_hours / self.total_vessels_processed 
                      if self.total_vessels_processed > 0 else 0)
        avg_service = (self.total_service_time_hours / self.total_vessels_processed 
                      if self.total_vessels_processed > 0 else 0)
        
        return {
            "avg_waiting_time_hours": avg_waiting,
            "avg_service_time_hours": avg_service,
            "avg_co2_per_vessel_kg": (self.total_co2_emission_kg / self.total_vessels_processed 
                                     if self.total_vessels_processed > 0 else 0),
            "avg_shifts_per_vessel": (self.total_shifts_performed / self.total_vessels_processed 
                                     if self.total_vessels_performed > 0 else 0),
        }


class PortEnvironment:
    """Môi trường mô phỏng cảng container"""
    
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.metrics = SimulationMetrics()
        
        # Tài nguyên cảng
        self.quay_cranes = simpy.Resource(env, capacity=6)  # 6 cẩu bờ
        self.rtg_cranes = simpy.Resource(env, capacity=15)  # 15 cẩu RTG
        self.berth_slots = simpy.Resource(env, capacity=6)  # 6 vị trí bến
        self.gate_lanes = simpy.Resource(env, capacity=8)  # 8 làn cổng
        
        # Hàng chờ tàu
        self.vessel_queue: List[Dict[str, Any]] = []
        
        # Lịch sử sự kiện
        self.event_log: List[Dict[str, Any]] = []
    
    def log_event(self, event_type: str, vessel_id: str, details: Dict[str, Any]) -> None:
        """Ghi lại sự kiện"""
        self.event_log.append({
            "time": self.env.now,
            "event_type": event_type,
            "vessel_id": vessel_id,
            "details": details,
        })


class ContainerVessel:
    """Mô hình tàu container trong mô phỏng"""
    
    def __init__(
        self,
        vessel_id: str,
        env: simpy.Environment,
        port: PortEnvironment,
        arrival_time: float,
        capacity_teu: int,
        load_teu: int,
        containers_to_handle: int,
    ):
        self.vessel_id = vessel_id
        self.env = env
        self.port = port
        self.arrival_time = arrival_time
        self.capacity_teu = capacity_teu
        self.load_teu = load_teu
        self.containers_to_handle = containers_to_handle
        
        # Thời gian sự kiện
        self.actual_arrival_time = None
        self.berth_allocation_time = None
        self.loading_start_time = None
        self.loading_end_time = None
        self.departure_time = None
        
        # Thống kê
        self.containers_processed = 0
        self.waiting_time = 0.0
        self.service_time = 0.0
        self.co2_emission = 0.0
    
    def run(self) -> None:
        """Chạy process cho tàu"""
        # Tàu đến cảng
        yield self.env.timeout(self.arrival_time)
        self.actual_arrival_time = self.env.now
        self.port.log_event("vessel_arrived", self.vessel_id, {
            "arrival_time": self.actual_arrival_time,
            "capacity": self.capacity_teu,
            "load": self.load_teu,
        })
        
        # Chờ vị trí bến trống
        with self.port.berth_slots.request() as req:
            yield req
            
            self.berth_allocation_time = self.env.now
            self.waiting_time = self.berth_allocation_time - self.actual_arrival_time
            
            self.port.log_event("berth_allocated", self.vessel_id, {
                "waiting_time": self.waiting_time,
                "time": self.berth_allocation_time,
            })
            
            # Tính toán thời gian xử lý
            handling_time_per_container = 2.0 / 60  # 2 phút = 0.0333 giờ
            processing_time = self.containers_to_handle * handling_time_per_container
            
            # Xử lý bốc/dỡ container
            self.loading_start_time = self.env.now
            
            # Mô phỏng xử lý (có thể được tối ưu hóa)
            yield self.env.timeout(processing_time)
            
            self.loading_end_time = self.env.now
            self.containers_processed = self.containers_to_handle
            self.service_time = self.loading_end_time - self.actual_arrival_time
            
            self.port.log_event("processing_completed", self.vessel_id, {
                "service_time": self.service_time,
                "containers_processed": self.containers_processed,
            })
        
        # Tàu rời đi
        self.departure_time = self.env.now
        
        # Tính toán phát thải CO2
        self.co2_emission = 500 + (self.waiting_time * 200)  # kg
        
        self.port.log_event("vessel_departed", self.vessel_id, {
            "departure_time": self.departure_time,
            "total_time_in_port": self.service_time,
            "co2_emission": self.co2_emission,
        })
        
        # Cập nhật metrics
        self.port.metrics.total_vessels_processed += 1
        self.port.metrics.total_containers_processed += self.containers_processed
        self.port.metrics.total_waiting_time_hours += self.waiting_time
        self.port.metrics.total_service_time_hours += self.service_time
        self.port.metrics.total_co2_emission_kg += self.co2_emission
        self.port.metrics.vessel_waiting_times.append(self.waiting_time)
        self.port.metrics.vessel_service_times.append(self.service_time)


class PortSimulation:
    """Mô phỏng hoạt động cảng container"""
    
    def __init__(
        self,
        simulation_duration_hours: float = 24.0,
        num_vessels: int = 8,
        avg_vessel_size_teu: int = 5000,
        random_seed: int = 42,
    ):
        self.simulation_duration_hours = simulation_duration_hours
        self.num_vessels = num_vessels
        self.avg_vessel_size_teu = avg_vessel_size_teu
        self.random_seed = random_seed
        
        random.seed(random_seed)
        
        self.env = simpy.Environment()
        self.port = PortEnvironment(self.env)
    
    def generate_vessel_arrivals(self) -> None:
        """Tạo các tàu cập bến theo phân phối Poisson"""
        arrival_rate = self.num_vessels / self.simulation_duration_hours
        time_between_arrivals = 1.0 / arrival_rate  # giờ
        
        for i in range(self.num_vessels):
            # Thời gian đến (phân phối exponential)
            arrival_time = random.expovariate(arrival_rate) if i == 0 else self.env.now + random.expovariate(arrival_rate)
            
            if arrival_time > self.simulation_duration_hours:
                break
            
            # Tạo thông số tàu
            vessel_id = f"SHIP_{i:03d}"
            capacity = int(random.gauss(self.avg_vessel_size_teu, 1000))
            load = int(capacity * random.uniform(0.6, 0.95))
            containers = load  # 1 TEU ≈ 1 container (đơn giản hóa)
            
            # Tạo tàu và chạy
            vessel = ContainerVessel(
                vessel_id=vessel_id,
                env=self.env,
                port=self.port,
                arrival_time=arrival_time,
                capacity_teu=capacity,
                load_teu=load,
                containers_to_handle=containers,
            )
            
            self.env.process(vessel.run())
    
    def run(self) -> SimulationMetrics:
        """Chạy mô phỏng"""
        logger.info(f"🚢 Bắt đầu mô phỏng cảng Cát Lái")
        logger.info(f"   Thời gian mô phỏng: {self.simulation_duration_hours} giờ")
        logger.info(f"   Số tàu dự kiến: {self.num_vessels}")
        
        self.generate_vessel_arrivals()
        
        # Chạy mô phỏng
        self.env.run()
        
        logger.info(f"✅ Mô phỏng hoàn thành")
        return self.port.metrics
    
    def get_results(self) -> Dict[str, Any]:
        """Lấy kết quả mô phỏng"""
        metrics = self.port.metrics
        averages = metrics.calculate_averages()
        
        return {
            "simulation_duration_hours": self.simulation_duration_hours,
            "total_vessels_processed": metrics.total_vessels_processed,
            "total_containers_processed": metrics.total_containers_processed,
            "total_waiting_time_hours": round(metrics.total_waiting_time_hours, 2),
            "total_service_time_hours": round(metrics.total_service_time_hours, 2),
            "total_co2_emission_kg": round(metrics.total_co2_emission_kg, 2),
            "averages": {
                "avg_waiting_time_hours": round(averages["avg_waiting_time_hours"], 2),
                "avg_service_time_hours": round(averages["avg_service_time_hours"], 2),
                "avg_co2_per_vessel_kg": round(averages["avg_co2_per_vessel_kg"], 2),
            },
            "event_count": len(self.port.event_log),
        }
