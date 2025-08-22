# test2.py
from machine import Pin, PWM
import utime

# -----------------------------
# Motor setup (same pins as yours)
# -----------------------------
Motor1_In1 = Pin(1, Pin.OUT)
Motor1_In2 = Pin(5, Pin.OUT)
Motor1_EN  = PWM(Pin(0, Pin.OUT))   # ENA -> GP0 (remove the ENA jumper on L298N)

Motor2_In1 = Pin(4, Pin.OUT)
Motor2_In2 = Pin(5, Pin.OUT)
Motor2_EN  = PWM(Pin(3, Pin.OUT))   # ENB/ENA (depending on your board) -> GP3

Motor3_In1 = Pin(27, Pin.OUT)
Motor3_In2 = Pin(26, Pin.OUT)
Motor3_EN  = PWM(Pin(28, Pin.OUT))

Motor4_In1 = Pin(21, Pin.OUT)
Motor4_In2 = Pin(20, Pin.OUT)
Motor4_EN  = PWM(Pin(22, Pin.OUT))

for en in (Motor1_EN, Motor2_EN, Motor3_EN, Motor4_EN):
    en.freq(1000)

# -----------------------------
# Ultrasonic sensor
# -----------------------------
trigger = Pin(17, Pin.OUT)
echo    = Pin(16, Pin.IN)

# -----------------------------
# (Optional) Servo: hold at center
# -----------------------------
servo = PWM(Pin(15))
servo.freq(50)
servo.duty_ns(1_500_000)  # center ~1.5 ms

# -----------------------------
# Parameters
# -----------------------------
THRESHOLD_CM   = 10       # follow when object is within this distance (cm)
FOLLOW_SPEED   = 30_000   # motor speed when following
ULTRA_TIMEOUT  = 30_000   # us, basic timeout so ultra() won't hang
SAMPLE_DELAY_S = 0.05     # how often to measure

# -----------------------------
# Direction polarity map
# CHANGE: M1 -> False (to correct its reversed spin)
# -----------------------------
FORWARD_POLARITY = {
    "M1": True,   # flipped
    "M2": False,
    "M3": False,
    "M4": True,
}

# -----------------------------
# Motor helpers
# -----------------------------
def set_speed(s):
    Motor1_EN.duty_u16(s)
    Motor2_EN.duty_u16(s)
    Motor3_EN.duty_u16(s)
    Motor4_EN.duty_u16(s)

def _drive_motor(m, go_forward, speed):
    if m == 1:
        in1, in2, en, pol = Motor1_In1, Motor1_In2, Motor1_EN, FORWARD_POLARITY["M1"]
    elif m == 2:
        in1, in2, en, pol = Motor2_In1, Motor2_In2, Motor2_EN, FORWARD_POLARITY["M2"]
    elif m == 3:
        in1, in2, en, pol = Motor3_In1, Motor3_In2, Motor3_EN, FORWARD_POLARITY["M3"]
    else:
        in1, in2, en, pol = Motor4_In1, Motor4_In2, Motor4_EN, FORWARD_POLARITY["M4"]

    # desired direction ⊕ polarity -> electrical direction
    dir_bit = (1 if go_forward else 0) ^ (0 if pol else 1)
    if dir_bit:
        in1.high(); in2.low()
    else:
        in1.low();  in2.high()
    en.duty_u16(speed)

def forward(speed):
    _drive_motor(1, True,  speed)
    _drive_motor(2, True,  speed)
    _drive_motor(3, True,  speed)
    _drive_motor(4, True,  speed)

def stop():
    Motor1_In1.low(); Motor1_In2.low(); Motor1_EN.duty_u16(0)
    Motor2_In1.low(); Motor2_In2.low(); Motor2_EN.duty_u16(0)
    Motor3_In1.low(); Motor3_In2.low(); Motor3_EN.duty_u16(0)
    Motor4_In1.low(); Motor4_In2.low(); Motor4_EN.duty_u16(0)

# -----------------------------
# Quick diagnostics (optional)
# -----------------------------
def jog_test():
    print("Jogging each motor FORWARD for 1s (expect all wheels to move forward).")
    for i in (1, 2, 3, 4):
        _drive_motor(i, True, 20000)
        utime.sleep(1.0)
        _drive_motor(i, True, 0)
        utime.sleep(0.4)

# -----------------------------
# Ultrasonic (with timeout)
# -----------------------------
def ultra(timeout_us=ULTRA_TIMEOUT):
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(10)
    trigger.low()

    start = utime.ticks_us()
    while echo.value() == 0:
        if utime.ticks_diff(utime.ticks_us(), start) > timeout_us:
            return 9999.0
    t_on = utime.ticks_us()

    while echo.value() == 1:
        if utime.ticks_diff(utime.ticks_us(), t_on) > timeout_us:
            return 9999.0
    t_off = utime.ticks_us()

    pulse = utime.ticks_diff(t_off, t_on)
    return (pulse * 0.0343) / 2.0  # cm

# -----------------------------
# Super-simple follow loop
# -----------------------------
def follow_simple():
    while True:
        d = ultra()
        print(f"Distance: {d:.1f} cm")

        if d <= THRESHOLD_CM:
            print("Object within 20 cm → FOLLOW (forward)")
            forward(FOLLOW_SPEED)
        else:
            print("No object within 20 cm → STOP")
            stop()

        utime.sleep(SAMPLE_DELAY_S)

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    print("Simple follow mode: forward if object ≤ 20 cm, else stop.")
    try:
        # jog_test()  # uncomment once to verify directions
        follow_simple()
    except KeyboardInterrupt:
        stop()
        print("Program stopped by user")

