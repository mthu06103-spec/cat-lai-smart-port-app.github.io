#!/bin/bash
# Script test nhanh hệ thống
# Cảng Container Cát Lái - Quick Test

set -e

echo "🚢 Kiểm tra hệ thống Cảng Cát Lái"
echo "=================================="

# Kiểm tra Docker
echo -n "✓ Docker... "
if command -v docker &> /dev/null; then
    echo "OK"
else
    echo "FAILED - Cài đặt Docker"
    exit 1
fi

# Kiểm tra Docker Compose
echo -n "✓ Docker Compose... "
if command -v docker-compose &> /dev/null; then
    echo "OK"
else
    echo "FAILED - Cài đặt Docker Compose"
    exit 1
fi

# Tạo .env nếu chưa tồn tại
if [ ! -f .env ]; then
    echo "📝 Tạo file .env..."
    cp .env.example .env
fi

# Khởi động hệ thống
echo ""
echo "🚀 Khởi động hệ thống..."
docker-compose up -d

# Chờ backend khởi động
echo ""
echo "⏳ Chờ backend khởi động..."
sleep 10

# Test Backend
echo ""
echo "🔍 Kiểm tra Backend..."
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend: OK"
else
    echo "❌ Backend: FAILED"
    docker-compose logs backend
    exit 1
fi

# Test Swagger UI
echo ""
echo "🔍 Kiểm tra Swagger UI..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ Swagger UI: OK"
else
    echo "⚠️  Swagger UI: PENDING"
fi

# Test Frontend
echo ""
echo "🔍 Kiểm tra Frontend..."
if curl -s http://localhost:8501 > /dev/null; then
    echo "✅ Frontend: OK"
else
    echo "⏳ Frontend: Starting..."
fi

# Hiển thị thông tin hữu ích
echo ""
echo "=================================="
echo "✅ Hệ thống khởi động thành công!"
echo ""
echo "📍 Dịch vụ khả dụng:"
echo "   🔗 Backend API:     http://localhost:8000"
echo "   📚 API Docs:        http://localhost:8000/docs"
echo "   📊 Frontend:        http://localhost:8501"
echo "   💾 PostgreSQL:      localhost:5432"
echo "   🔴 Redis:           localhost:6379"
echo ""
echo "📋 Xem logs:"
echo "   docker-compose logs -f backend"
echo "   docker-compose logs -f frontend"
echo ""
echo "🛑 Dừng hệ thống:"
echo "   docker-compose down"
echo ""
echo "✨ Hệ thống sẵn sàng!"
