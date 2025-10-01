#!/bin/bash
# Quick launcher for FASLit Test Frontend

echo "========================================="
echo "FASLit Nav-App Test Frontend"
echo "========================================="
echo ""
echo "Make sure:"
echo "1. MQTT broker is running on shared laptop"
echo "2. mqtt_config.json has correct broker IP"
echo "3. Your nav_app is running"
echo ""
echo "Starting frontend..."
echo ""

cd /Users/donghyun/All/hello
python3 nav_app/test_frontend.py
