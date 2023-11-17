import os
import pygame
import time
import random
import RPi.GPIO as GPIO
import pickle

# 파일 이름과 경로 설정
file_names = [
    "0001_t.wav", "0002_t.wav", "0003_t.wav",
    "0004_t.wav", "0005_t.wav", "0006_t.wav", "0007_t.wav"
]

# 수정된 파일 경로 설정
file_paths = [os.path.join("/home/hyun/wav", name) for name in file_names]

# 초기화 및 사운드 객체 생성
pygame.init()
pygame.mixer.init()
sounds = [pygame.mixer.Sound(path) for path in file_paths]

# PIR 센서 설정
PIR_PIN = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# 랭킹 딕셔너리 초기화
ranking = {name: 0 for name in file_names}

# 사운드 재생 함수
def play_random_sound():
    sound = random.choice(sounds)
    sound.set_volume(0.5)
    sound.play()
    time.sleep(5)
    sound.stop()
    return sound

# PIR 센서 동작 모니터링 및 랭킹 업데이트
def monitor_pir_sensor():
    last_movement_time = time.time()
    current_sound = None

    try:
        print("랭킹메소드 테스트 시작!")
        while True:
            time.sleep(1)
            print("찾는중..")
            if GPIO.input(PIR_PIN):  # PIR 센서 탐지 시
                if current_sound is None:
                    current_sound = play_random_sound()
                    if time.time() - last_movement_time >= 3:
                        current_sound.stop()
                        ranking[file_names[sounds.index(current_sound)]] -= 1
                        current_sound = play_random_sound()
                        last_movement_time = time.time()
                        continue

                    else:
                        current_sound.stop()
                        ranking[file_names[sounds.index(current_sound)]] += 1
                        last_movement_time = time.time()

                else:
                    if time.time() - last_movement_time >= 3:
                        current_sound.stop()
                        ranking[file_names[sounds.index(current_sound)]] -= 1
                        current_sound = play_random_sound()
                        last_movement_time = time.time()
                        continue

                    else:
                        current_sound.stop()
                        ranking[file_names[sounds.index(current_sound)]] += 1
                        last_movement_time = time.time()

            else:
                print("감지되지 않았습니다.")


    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    monitor_pir_sensor()
    
    sorted_ranking = sorted(ranking.items(), key=lambda x: x[1], reverse=True)
    print("랭킹:")
    for index, (name, score) in enumerate(sorted_ranking, start=1):
        print(f"{index}: {name}: {score}")

