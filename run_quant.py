import os
import time

print("===== KDH AI QUANT START =====")

print("1. 시장 스캔")
os.system("python fast_scanner.py")

print("2. 급등 탐지")
os.system("python surge_detector.py")

print("3. 신호 생성")
os.system("python signal_engine.py")

print("4. 포트폴리오 업데이트")
os.system("python portfolio_manager.py")

print("===== 완료 =====")