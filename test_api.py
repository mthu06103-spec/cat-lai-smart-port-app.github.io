#!/usr/bin/env python
"""
Script test backend API
Cảng Container Cát Lái - Quick API Test
"""

import requests
import json
from typing import Dict, Any
import sys

API_BASE = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.END}")

def test_health():
    """Test health check"""
    print_header("1️⃣  TEST HEALTH CHECK")
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            print_success("API khởi động thành công")
            print(json.dumps(response.json(), indent=2))
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Không thể kết nối API: {e}")
        return False
    return True

def test_register_vessel():
    """Test đăng ký tàu"""
    print_header("2️⃣  TEST ĐĂNG KÝ TÀU")
    
    vessel_data = {
        "ship_name": "MSC GULSUN",
        "vessel_type": "xlarge",
        "capacity_teu": 23756,
        "current_load_teu": 18000,
        "containers_to_load": 8000,
        "containers_to_unload": 10000,
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/vessels/register",
            json=vessel_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Tàu {result['ship_id']} đã được đăng ký")
            print(json.dumps(result, indent=2))
            return result.get('ship_id')
        else:
            print_error(f"Đăng ký tàu thất bại: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Lỗi: {e}")
        return None

def test_stow_ai(ship_id: str):
    """Test stowAI optimization"""
    print_header("3️⃣  TEST STOWAIX OPTIMIZATION")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/optimization/stow-ai?ship_id={ship_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("stowAI tối ưu hóa thành công")
            
            metrics = result.get('service_time_metrics', {})
            print(f"\n📊 Kết quả:")
            print(f"   Thời gian dịch vụ gốc: {metrics.get('original_service_time_hours', 0):.1f}h")
            print(f"   Thời gian tối ưu: {metrics.get('optimized_service_time_hours', 0):.1f}h")
            print(f"   Giảm: {metrics.get('reduction_percent', 0):.1f}%")
            print(f"   CO2 giảm: {result.get('co2_reduction_kg', 0):.0f} kg")
            
            return True
        else:
            print_error(f"stowAI thất bại: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def test_stack_ai(ship_id: str):
    """Test stackAI optimization"""
    print_header("4️⃣  TEST STACKAI OPTIMIZATION")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/optimization/stack-ai?ship_id={ship_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("stackAI tối ưu hóa thành công")
            
            stacking = result.get('stacking_metrics', {})
            print(f"\n📦 Kết quả:")
            print(f"   Shifters gốc: {stacking.get('original_shifters', 0)}")
            print(f"   Shifters tối ưu: {stacking.get('optimized_shifters', 0)}")
            print(f"   Giảm: {stacking.get('shifter_reduction_percent', 0):.1f}%")
            print(f"   CO2 giảm: {result.get('environmental_impact', {}).get('co2_reduction_kg', 0):.0f} kg")
            
            return True
        else:
            print_error(f"stackAI thất bại: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def test_kpi_metrics():
    """Test KPI metrics"""
    print_header("5️⃣  TEST KPI METRICS")
    
    try:
        response = requests.get(
            f"{API_BASE}/api/kpi/metrics",
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("KPI metrics lấy thành công")
            
            print(f"\n📊 Chỉ số Hiệu suất:")
            print(f"   Giảm thời gian chờ: {result.get('vessel_waiting_time_reduction_percent', 0):.0f}%")
            print(f"   Giảm shifters: {result.get('shifter_reduction_percent', 0):.0f}%")
            print(f"   Giảm CO2: {result.get('co2_emission_reduction_percent', 0):.0f}%")
            print(f"   Tăng năng suất cẩu: {result.get('crane_productivity_improvement_percent', 0):.0f}%")
            print(f"   Cải thiện an toàn: {result.get('safety_incident_reduction_percent', 0):.0f}%")
            
            return True
        else:
            print_error(f"Lấy KPI thất bại: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def test_simulation():
    """Test DES simulation"""
    print_header("6️⃣  TEST MÔ PHỎNG DES")
    
    sim_data = {
        "num_vessels": 5,
        "simulation_duration_hours": 8,
        "enable_stow_ai": True,
        "enable_stack_ai": True,
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/simulation/run",
            json=sim_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Mô phỏng DES hoàn thành")
            
            results = result.get('results', {})
            print(f"\n📊 Kết quả Mô phỏng:")
            print(f"   Tàu xử lý: {results.get('total_vessels', 0)}")
            print(f"   Container xử lý: {results.get('total_containers', 0)}")
            print(f"   Thời gian chờ avg: {results.get('avg_waiting_time_hours', 0):.1f}h")
            print(f"   Thời gian dịch vụ avg: {results.get('avg_service_time_hours', 0):.1f}h")
            print(f"   CO2 phát thải: {results.get('total_co2_emission_kg', 0):.0f} kg")
            
            return True
        else:
            print_error(f"Mô phỏng thất bại: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print(r"""
    ╔════════════════════════════════════════════════════════════╗
    ║     🚢 CẢNG CONTAINER CÁT LÁI - QUICK API TEST              ║
    ║                                                            ║
    ║  Kiểm tra Backend FastAPI + SimPy & AI Optimization       ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    print(Colors.END)
    
    print_info(f"API Base URL: {API_BASE}")
    print_info("Đảm bảo backend đang chạy: docker-compose up -d backend\n")
    
    # Run tests
    success_count = 0
    
    if test_health():
        success_count += 1
    
    ship_id = test_register_vessel()
    if ship_id:
        success_count += 1
        
        if test_stow_ai(ship_id):
            success_count += 1
        
        if test_stack_ai(ship_id):
            success_count += 1
    
    if test_kpi_metrics():
        success_count += 1
    
    if test_simulation():
        success_count += 1
    
    # Summary
    print_header("📋 TÓSUM KẾT")
    total_tests = 6
    print(f"Passed: {Colors.GREEN}{success_count}/{total_tests}{Colors.END}")
    
    if success_count == total_tests:
        print_success("Tất cả test đạt!")
        print_info("🚀 Hệ thống sẵn sàng sử dụng!")
        return 0
    else:
        print_error(f"{total_tests - success_count} test thất bại")
        print_info("Kiểm tra logs: docker-compose logs -f backend")
        return 1

if __name__ == "__main__":
    sys.exit(main())
