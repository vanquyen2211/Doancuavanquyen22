#raspberry với step motor . a49 step motor driver .Led báo sáng màu báo hiệu tốc độ delay . 2 nút :1 nút on/off và nút xoay chiều 
#Viết bằng micropython 
from machine import Pin, ADC
from machine import Pin, ADC, PWM
from time import sleep_ms

# set up các cổng gpio 
DIR_PIN = Pin(2, Pin.OUT)    #tạo hướng quay cho motor
STEP_PIN = Pin(3, Pin.OUT)   #tạo xung bước
SWITCH_PIN = Pin(4, Pin.IN, Pin.PULL_UP)     # Nút nhấn chạy
SWITCH_DIR = Pin(7, Pin.IN, Pin.PULL_UP)     # Nút chọn hướng thủ công
SPEED_PIN = ADC(27)                          # Cần gạt chỉnh tốc độ(biển trở)
LIMIT_PIN = Pin(1, Pin.IN, Pin.PULL_UP)      # Công tắc giới hạn
LED = PWM(Pin(16))  #chân điều khiển led 
LED.freq(1000)    #tần số PWM của led ()

# Biến lưu trạng thái công tắc giới hạn
last_limit_state = 1

def map_value(x, in_min, in_max, out_min, out_max):
    x = max(min(x, in_max), in_min)   #giới hạng của x 
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

while True:
    current_limit = LIMIT_PIN.value()

    # Nếu chạm công tắc: đảo chiều
    if current_limit == 0 and last_limit_state == 1:
        print(">> Chạm công tắc giới hạn! Đổi chiều")
        DIR_PIN.value(1 - DIR_PIN.value())
        sleep_ms(500)

    last_limit_state = current_limit #cập nhật 

    # Nếu không chạm công tắc, cho phép điều chỉnh hướng thủ công
    if current_limit == 1:
        DIR_PIN.value(0 if SWITCH_DIR.value() else 1)

    # Nếu giữ nút SWITCH_PIN → motor chạy liên tục
    if SWITCH_PIN.value() == 0:
        adc_val = SPEED_PIN.read_u16() >> 6  # 0–1023
        delay = map_value(adc_val, 0, 1023, 500, 50)
        print("Thoi gian delay:", delay)

        #Điều chỉnh độ sáng LED đỏ theo tốc độ (delay lớn = sáng mạnh)
        brightness = map_value(delay, 50, 500, 1023, 0)
        LED.duty_u16(brightness << 6)  #PWM 16-bit (0–65535)
        #Phát xung bước motor
        STEP_PIN.value(1)
        sleep_ms(1)
        STEP_PIN.value(0)
        sleep_ms(delay)
    else:
        sleep_ms(10) 
