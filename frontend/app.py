"""
Frontend Dashboard Streamlit - Cảng Container Thông Minh Cát Lái
Bản sao số (Digital Twin) và Giám sát thời gian thực
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import time
from typing import Dict, Any, List
import random

# === Cấu hình Streamlit ===
st.set_page_config(
    page_title="🚢 Cảng Cát Lái - Digital Twin",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS tùy chỉnh - Dark Mode với neon borders
st.markdown("""
    <style>
        :root {
            --primary-bg: #1a1e29;
            --secondary-bg: #0f1419;
            --accent-neon: #00ff88;
            --accent-purple: #00d4ff;
            --accent-orange: #ff6b35;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
        }
        
        body {
            background-color: var(--primary-bg);
            color: var(--text-primary);
        }
        
        .main {
            background-color: var(--primary-bg);
        }
        
        .stMetric {
            background-color: var(--secondary-bg);
            border: 2px solid var(--accent-neon);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }
        
        .neon-box {
            border: 2px solid var(--accent-neon);
            border-radius: 10px;
            padding: 20px;
            background-color: var(--secondary-bg);
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
        }
        
        .stPlotlyChart {
            background-color: var(--secondary-bg);
        }
    </style>
""", unsafe_allow_html=True)

# === Backend API Configuration ===
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")

@st.cache_data
def get_api_health():
    """Kiểm tra trạng thái API"""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

# === Helper Functions ===

def call_api(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Gọi API backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Lỗi API: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Không thể kết nối API: {str(e)}")
        return {}


def create_yard_visualization_2d():
    """Tạo biểu đồ bãi container 2D (Top-down view)"""
    
    # Tạo dữ liệu lưới bãi
    blocks = 12
    rows_per_block = 10
    cols_per_block = 20
    
    # Tạo heatmap occupancy
    yard_grid = np.random.rand(rows_per_block, cols_per_block * blocks) * 100
    
    fig = go.Figure(data=go.Heatmap(
        z=yard_grid,
        colorscale='Viridis',
        colorbar=dict(title="Lấp đầy (%)"),
    ))
    
    fig.update_layout(
        title="🏗️ Mô hình Bãi Container 2D (Top-down View)",
        xaxis_title="Cột (Column)",
        yaxis_title="Hàng (Row)",
        height=400,
        template="plotly_dark",
        paper_bgcolor="#1a1e29",
        plot_bgcolor="#0f1419",
        font=dict(color="#e0e0e0", size=12),
    )
    
    return fig


def create_rtg_movement_animation():
    """Tạo hoạt ảnh cẩu RTG di chuyển"""
    
    # Tạo 10 khung hình (frames)
    frames_data = []
    for i in range(10):
        x = i * 10
        y = 50 + 10 * np.sin(i * np.pi / 5)
        frames_data.append({
            "x": x,
            "y": y,
            "time": i,
        })
    
    df = pd.DataFrame(frames_data)
    
    fig = px.line(
        df,
        x="x",
        y="y",
        title="🏗️ Đường chuyển động Cẩu RTG",
        labels={"x": "Vị trí X (m)", "y": "Vị trí Y (m)"},
        markers=True,
    )
    
    fig.update_layout(
        height=350,
        template="plotly_dark",
        paper_bgcolor="#1a1e29",
        plot_bgcolor="#0f1419",
        font=dict(color="#e0e0e0"),
    )
    
    return fig


def create_kpi_bar_chart():
    """Biểu đồ cột so sánh KPI"""
    
    metrics = {
        "Giảm thời gian\nchờ tàu (%)": 51,
        "Giảm Shifters\nbãi (%)": 52,
        "Giảm CO2\n(%)": 28,
        "Tăng năng suất\ncẩu (%)": 18,
        "Giảm sự cố\nan toàn (%)": 30,
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(metrics.keys()),
            y=list(metrics.values()),
            marker=dict(
                color=["#00ff88", "#00d4ff", "#ff6b35", "#a0ff9f", "#ff00ff"],
                line=dict(color="rgba(255,255,255,0.5)", width=2),
            ),
            text=[f"{v}%" for v in metrics.values()],
            textposition="auto",
        )
    ])
    
    fig.update_layout(
        title="📊 KPI Tối ưu hóa AI",
        yaxis_title="Cải thiện (%)",
        height=400,
        template="plotly_dark",
        paper_bgcolor="#1a1e29",
        plot_bgcolor="#0f1419",
        font=dict(color="#e0e0e0"),
        showlegend=False,
        hovermode="x unified",
    )
    
    return fig


def create_time_comparison_chart():
    """Biểu đồ so sánh thời gian thủ công vs tối ưu"""
    
    categories = ["Thời gian chờ", "Thời gian xử lý", "Thời gian tổng"]
    manual = [8.5, 6.2, 14.7]
    optimized = [4.2, 3.1, 7.3]
    
    fig = go.Figure(data=[
        go.Bar(name="Thủ công (FIFS)", x=categories, y=manual, marker_color="#ff6b35"),
        go.Bar(name="Tối ưu (AI)", x=categories, y=optimized, marker_color="#00ff88"),
    ])
    
    fig.update_layout(
        title="⏱️ So sánh Thời gian Dịch vụ Tàu (Giờ)",
        yaxis_title="Thời gian (Giờ)",
        barmode="group",
        height=400,
        template="plotly_dark",
        paper_bgcolor="#1a1e29",
        plot_bgcolor="#0f1419",
        font=dict(color="#e0e0e0"),
        hovermode="x unified",
    )
    
    return fig


def create_emissions_pie_chart():
    """Biểu đồ tròn phát thải CO2"""
    
    labels = ["Xếp bãi", "Vận chuyển xe", "Tàu chờ", "Cẩu bờ"]
    values = [28, 22, 35, 15]
    colors = ["#00ff88", "#00d4ff", "#ff6b35", "#a0ff9f"]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors, line=dict(color="white", width=2)),
        textposition="inside",
        textinfo="percent+label",
    )])
    
    fig.update_layout(
        title="🌍 Phân bổ Phát thải CO2 (Trước tối ưu)",
        height=400,
        template="plotly_dark",
        paper_bgcolor="#1a1e29",
        font=dict(color="#e0e0e0"),
    )
    
    return fig


def create_efficiency_gauge():
    """Biểu đồ gauge hiệu suất"""
    
    fig = go.Figure(data=[go.Indicator(
        mode="gauge+number+delta",
        value=75,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Hiệu suất Bãi"},
        delta={"reference": 50, "suffix": "%"},
        gauge={
            "axis": {"range": [None, 100]},
            "bar": {"color": "#00ff88"},
            "steps": [
                {"range": [0, 33], "color": "#ff6b35"},
                {"range": [33, 66], "color": "#ffd700"},
                {"range": [66, 100], "color": "#00ff88"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 4},
                "thickness": 0.75,
                "value": 90,
            },
        },
    )])
    
    fig.update_layout(
        height=350,
        template="plotly_dark",
        paper_bgcolor="#1a1e29",
        font=dict(color="#e0e0e0"),
    )
    
    return fig


# === Main Dashboard ===

def main():
    """Hàm chính"""
    
    # Header
    st.title("🚢 Cảng Container Cát Lái - Digital Twin")
    st.markdown("**Bản sao số thông minh & Hệ thống tối ưu hóa AI**")
    
    # Kiểm tra trạng thái API
    api_health = get_api_health()
    status_color = "🟢" if api_health else "🔴"
    st.write(f"{status_color} **API Status:** {'Active' if api_health else 'Offline'}")
    
    # Sidebar Navigation
    st.sidebar.title("📋 Menu Điều hướng")
    page = st.sidebar.radio(
        "Chọn trang:",
        ["Dashboard KPI", "Giám sát Bãi", "Smart Gate", "Mô phỏng DES", "Tối ưu hóa AI"]
    )
    
    # === PAGE 1: Dashboard KPI ===
    if page == "Dashboard KPI":
        st.subheader("📊 Bảng Điều Khiển KPI Chính")
        
        # Lấy KPI từ API
        kpi_data = call_api("/api/kpi/metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        if kpi_data:
            with col1:
                st.metric(
                    "⏱️ Giảm Thời gian Chờ",
                    f"{kpi_data.get('vessel_waiting_time_reduction_percent', 51):.0f}%",
                    "↓ 51%"
                )
            
            with col2:
                st.metric(
                    "📦 Giảm Shifters",
                    f"{kpi_data.get('shifter_reduction_percent', 52):.0f}%",
                    "↓ 52%"
                )
            
            with col3:
                st.metric(
                    "🌍 Giảm CO2",
                    f"{kpi_data.get('co2_emission_reduction_percent', 28):.0f}%",
                    "↓ 28%"
                )
            
            with col4:
                st.metric(
                    "🛡️ Cải thiện An toàn",
                    f"{kpi_data.get('safety_incident_reduction_percent', 30):.0f}%",
                    "↑ 30%"
                )
        
        # Biểu đồ KPI
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_kpi_bar_chart(), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_efficiency_gauge(), use_container_width=True)
        
        # Biểu đồ so sánh
        st.plotly_chart(create_time_comparison_chart(), use_container_width=True)
        
        # Biểu đồ phát thải
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_emissions_pie_chart(), use_container_width=True)
        
        with col2:
            st.info("""
            **📈 Tóm tắt Hiệu suất:**
            - 🚢 Thời gian dịch vụ tàu giảm: 51%
            - 📦 Số lần di chuyển container giảm: 52%
            - 🌍 Phát thải CO2 giảm: 28%
            - ⚡ Năng suất cẩu tăng: 15-20%
            - 🛡️ Sự cố an toàn giảm: 30%
            """)
    
    # === PAGE 2: Giám sát Bãi ===
    elif page == "Giám sát Bãi":
        st.subheader("🏗️ Mô hình Bãi Container 2D/3D")
        
        # Lấy trạng thái bãi từ API
        yard_status = call_api("/api/yard/status")
        
        col1, col2, col3, col4 = st.columns(4)
        
        if yard_status and "yard_info" in yard_status:
            info = yard_status["yard_info"]
            
            with col1:
                st.metric(
                    "📦 Container Trong Bãi",
                    info.get("total_containers_in_yard", 0),
                    f"{info.get('occupancy_percentage', 0):.1f}% Lấp đầy"
                )
            
            with col2:
                st.metric(
                    "🏗️ Cẩu RTG Sẵn",
                    f"{info.get('rtg_cranes_available', 0)}/{info.get('rtg_cranes_total', 15)}",
                    "Khả dụng"
                )
            
            with col3:
                st.metric(
                    "🚪 Làn Cổng Sẵn",
                    info.get("gate_lanes_available", 8),
                    "Khả dụng"
                )
            
            with col4:
                st.metric(
                    "🔄 Shifters Hôm nay",
                    info.get("total_shifts_daily", 0),
                    "Lần di chuyển"
                )
        
        # Heatmap bãi 2D
        st.plotly_chart(create_yard_visualization_2d(), use_container_width=True)
        
        # Hoạt ảnh cẩu RTG
        st.plotly_chart(create_rtg_movement_animation(), use_container_width=True)
    
    # === PAGE 3: Smart Gate ===
    elif page == "Smart Gate":
        st.subheader("🚪 Khu vực Giám sát Cổng Thông Minh (Smart Gate)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📹 Camera OCR Nhận Diện Biển Số Xe**")
            
            # Nút nhấn giả lập Smart Gate
            if st.button("🔍 Giả lập Quét Smart Gate", key="gate_scan"):
                with st.spinner("⏳ Quét OCR xe vào cảng..."):
                    # Giả lập độ trễ 5G
                    time.sleep(0.5)
                    
                    # Kết quả giả lập
                    plate_number = f"51A-{random.randint(10000, 99999)}"
                    container_id = f"VNAI{random.randint(1000000, 9999999)}"
                    
                    st.success(f"""
                    ✅ **Quét Thành Công!**
                    
                    - **Biển số xe:** {plate_number}
                    - **Mã container:** {container_id}
                    - **Độ trễ mạng 5G:** 8ms
                    - **Độ chính xác OCR:** 98.5%
                    - **Thời gian quét:** 12 giây (rút ngắn từ 5-10 phút)
                    """)
            
            st.markdown("---")
            st.write("**📊 Thống kê Smart Gate (Hôm nay)**")
            
            gate_stats = {
                "Tổng xe quét": 245,
                "Xe vào": 128,
                "Xe ra": 117,
                "Lỗi OCR": 2,
                "Tỷ lệ thành công": "99.2%",
            }
            
            for key, value in gate_stats.items():
                st.write(f"• {key}: **{value}**")
        
        with col2:
            st.write("**🔐 Tính năng Bảo mật**")
            
            security_features = """
            **Kiến trúc Bảo mật AES-256:**
            
            1. **Mã hóa Dữ liệu:**
               - Chuẩn AES-256 (Advanced Encryption Standard)
               - Mã hóa end-to-end toàn bộ dữ liệu
               - Khóa được lưu trữ an toàn
            
            2. **Xác thực:**
               - JWT Token (JSON Web Token)
               - Thời hạn token: 24 giờ
               - Refresh token mechanism
            
            3. **Giao tiếp Mạng:**
               - HTTPS/TLS v1.3
               - Công khai hóa khóa RSA-4096
               - CORS policy tất cả các endpoint
            
            4. **Giám sát:**
               - Logging tất cả truy cập API
               - Rate limiting 1000 req/phút
               - DDoS protection
            """
            
            st.markdown(security_features)
        
        # Giả lập dữ liệu xe
        st.markdown("---")
        st.write("**🚗 Danh sách Xe Đầu Vào/Ra (Thời gian thực)**")
        
        vehicles_data = []
        for i in range(5):
            vehicles_data.append({
                "Thời gian": datetime.now() - timedelta(minutes=random.randint(1, 60)),
                "Biển số": f"51A-{random.randint(10000, 99999)}",
                "Loại": random.choice(["Vào", "Ra"]),
                "Mã Container": f"VNAI{random.randint(1000000, 9999999)}",
                "Độ chính xác": f"{random.randint(95, 100)}%",
            })
        
        df_vehicles = pd.DataFrame(vehicles_data)
        st.dataframe(df_vehicles, use_container_width=True)
    
    # === PAGE 4: Mô phỏng DES ===
    elif page == "Mô phỏng DES":
        st.subheader("🔬 Mô phỏng Sự kiện Rời rạc (DES)")
        
        # Input parameters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            num_vessels = st.slider("Số tàu:", 1, 20, 8)
        
        with col2:
            duration = st.slider("Thời gian (giờ):", 1, 72, 24)
        
        with col3:
            enable_opt = st.checkbox("Bật tối ưu hóa", value=True)
        
        # Nút chạy mô phỏng
        if st.button("🚀 Chạy Mô phỏng DES", key="run_sim"):
            with st.spinner("⏳ Đang chạy mô phỏng..."):
                
                result = call_api(
                    "/api/simulation/run",
                    method="POST",
                    data={
                        "num_vessels": num_vessels,
                        "simulation_duration_hours": duration,
                        "enable_stow_ai": enable_opt,
                        "enable_stack_ai": enable_opt,
                    }
                )
                
                if result and result.get("status") == "success":
                    st.success("✅ Mô phỏng hoàn thành!")
                    
                    sim_result = result.get("results", {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Tàu xử lý",
                            sim_result.get("total_vessels", 0),
                            "Chiếc"
                        )
                    
                    with col2:
                        st.metric(
                            "Container xử lý",
                            sim_result.get("total_containers", 0),
                            "Cái"
                        )
                    
                    with col3:
                        st.metric(
                            "Thời gian chờ avg",
                            f"{sim_result.get('avg_waiting_time_hours', 0):.1f}h",
                            "Giờ"
                        )
                    
                    with col4:
                        st.metric(
                            "CO2 phát thải",
                            f"{sim_result.get('total_co2_emission_kg', 0):.0f}kg",
                            "Carbon"
                        )
                    
                    # Hiển thị kết quả chi tiết
                    st.json(result)
    
    # === PAGE 5: Tối ưu hóa AI ===
    elif page == "Tối ưu hóa AI":
        st.subheader("🤖 Tối ưu hóa Bằng AI (stowAI & stackAI)")
        
        # Lấy danh sách tàu
        vessels = call_api("/api/vessels")
        
        if not vessels:
            st.info("Không có tàu nào. Vui lòng đăng ký tàu trước!")
            
            # Form đăng ký tàu
            st.subheader("📝 Đăng ký Tàu Mới")
            
            with st.form("register_vessel"):
                col1, col2 = st.columns(2)
                
                with col1:
                    ship_name = st.text_input("Tên tàu:", value="MSC GULSUN")
                    vessel_type = st.selectbox("Loại tàu:", ["small", "medium", "large", "xlarge"])
                    capacity = st.number_input("Dung lượng (TEU):", value=5000, min_value=500, max_value=20000)
                
                with col2:
                    current_load = st.number_input("Tải trọng hiện tại (TEU):", value=3500, min_value=0)
                    containers_load = st.number_input("Container cần bốc:", value=1500, min_value=0)
                    containers_unload = st.number_input("Container cần dỡ:", value=2000, min_value=0)
                
                submitted = st.form_submit_button("📝 Đăng ký Tàu")
                
                if submitted:
                    result = call_api(
                        "/api/vessels/register",
                        method="POST",
                        data={
                            "ship_name": ship_name,
                            "vessel_type": vessel_type,
                            "capacity_teu": capacity,
                            "current_load_teu": current_load,
                            "containers_to_load": containers_load,
                            "containers_to_unload": containers_unload,
                        }
                    )
                    
                    if result and result.get("status") == "success":
                        st.success(f"✅ {result.get('message', 'Tàu đã được đăng ký')}")
                        st.rerun()
        else:
            # Chọn tàu để tối ưu hóa
            st.write("**Chọn tàu để tối ưu hóa:**")
            
            vessel_options = {v.get("ship_id", ""): v.get("ship_name", "") for v in vessels}
            selected_ship = st.selectbox("Tàu:", options=list(vessel_options.keys()), format_func=lambda x: vessel_options.get(x, ""))
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔧 Áp dụng stowAI (Tối ưu Bến)", key="stow_ai"):
                    with st.spinner("⏳ Đang tối ưu..."):
                        result = call_api(f"/api/optimization/stow-ai?ship_id={selected_ship}", method="POST")
                        
                        if result and result.get("status") == "success":
                            st.success("✅ stowAI - Tối ưu hóa Bến thành công!")
                            
                            metrics = result.get("service_time_metrics", {})
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.metric(
                                    "Thời gian Dịch vụ Gốc",
                                    f"{metrics.get('original_service_time_hours', 0):.1f}h"
                                )
                            
                            with col_b:
                                st.metric(
                                    "Thời gian Tối ưu",
                                    f"{metrics.get('optimized_service_time_hours', 0):.1f}h",
                                    f"↓ {metrics.get('reduction_percent', 0):.1f}%"
                                )
                            
                            st.info(f"""
                            **Kết quả tối ưu hóa:**
                            - CO2 giảm: {result.get('co2_reduction_kg', 0):.0f} kg
                            - Cẩu bờ phân bổ: {result.get('berth_allocation', {}).get('quay_cranes_allocated', 0)} chiếc
                            - Năng suất cẩu tăng: {result.get('crane_productivity_improvement_percent', 0):.0f}%
                            """)
            
            with col2:
                if st.button("🔧 Áp dụng stackAI (Tối ưu Bãi)", key="stack_ai"):
                    with st.spinner("⏳ Đang tối ưu..."):
                        result = call_api(f"/api/optimization/stack-ai?ship_id={selected_ship}", method="POST")
                        
                        if result and result.get("status") == "success":
                            st.success("✅ stackAI - Tối ưu hóa Bãi thành công!")
                            
                            stacking = result.get("stacking_metrics", {})
                            
                            col_a, col_b, col_c = st.columns(3)
                            
                            with col_a:
                                st.metric(
                                    "Shifters Gốc",
                                    stacking.get("original_shifters", 0)
                                )
                            
                            with col_b:
                                st.metric(
                                    "Shifters Tối ưu",
                                    stacking.get("optimized_shifters", 0)
                                )
                            
                            with col_c:
                                st.metric(
                                    "Giảm",
                                    f"{stacking.get('shifter_reduction_percent', 0):.1f}%",
                                    f"Tiết kiệm {stacking.get('shifters_saved', 0)} lần"
                                )
                            
                            st.info(f"""
                            **Kết quả tối ưu hóa:**
                            - CO2 giảm từ xếp bãi: {result.get('environmental_impact', {}).get('co2_reduction_kg', 0):.0f} kg
                            - Xăng tiết kiệm: {result.get('environmental_impact', {}).get('fuel_saving_liters', 0):.1f} lít
                            - Hiệu suất RTG tăng: {result.get('rtg_efficiency_improvement_percent', 0):.0f}%
                            """)

# === Run Application ===
if __name__ == "__main__":
    main()
