from machine import Pin, PWM, UART
import utime

# -----------------------------
# Motor setup (same pins)
# -----------------------------
Motor1_In1 = Pin(1, Pin.OUT)
Motor1_In2 = Pin(6, Pin.OUT)
Motor1_EN  = PWM(Pin(0, Pin.OUT))

Motor2_In1 = Pin(4, Pin.OUT)
Motor2_In2 = Pin(5, Pin.OUT)
Motor2_EN  = PWM(Pin(3, Pin.OUT))

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
# Bluetooth (HC-06) on UART1
#   Pico TX -> GP8 (to HC-06 RX)
#   Pico RX -> GP9 (from HC-06 TX)
# -----------------------------
uart = UART(0, baudrate=9600, tx=Pin(12), rx=Pin(13), timeout=50)


# -----------------------------
# Parameters
# -----------------------------
THRESHOLD_CM    = 10
FOLLOW_SPEED    = 30_000
MIN_SPEED       = 10_000
MAX_SPEED       = 60_000
SPEED_STEP      = 5_000

ULTRA_TIMEOUT   = 30_000   # microseconds
SAMPLE_DELAY_S  = 0.05

# Modes
MODE_AUTO   = 0
MODE_MANUAL = 1
drive_mode  = MODE_AUTO

current_speed = FOLLOW_SPEED

# -----------------------------
# Motor helpers
# -----------------------------
def set_speed(s):
    s = max(MIN_SPEED, min(MAX_SPEED, s))
    Motor1_EN.duty_u16(s)
    Motor2_EN.duty_u16(s)
    Motor3_EN.duty_u16(s)
    Motor4_EN.duty_u16(s)
    return s

def all_low():
    Motor1_In1.low(); Motor1_In2.low()
    Motor2_In1.low(); Motor2_In2.low()
    Motor3_In1.low(); Motor3_In2.low()
    Motor4_In1.low(); Motor4_In2.low()

def forward(speed):
    # Adjust directions to your wiring
    Motor1_In1.high(); Motor1_In2.low()
    Motor2_In1.low();  Motor2_In2.high()
    Motor3_In1.low();  Motor3_In2.high()
    Motor4_In1.high(); Motor4_In2.low()
    set_speed(speed)

def backward(speed):
    Motor1_In1.low();  Motor1_In2.high()
    Motor2_In1.high(); Motor2_In2.low()
    Motor3_In1.high(); Motor3_In2.low()
    Motor4_In1.low();  Motor4_In2.high()
    set_speed(speed)

def left(speed):
    # skid-left: left side backward, right side forward
    Motor1_In1.low();  Motor1_In2.high()
    Motor2_In1.low();  Motor2_In2.high()
    Motor3_In1.high(); Motor3_In2.low()
    Motor4_In1.high(); Motor4_In2.low()
    set_speed(speed)

def right(speed):
    # skid-right: left side forward, right side backward
    Motor1_In1.high(); Motor1_In2.low()
    Motor2_In1.high(); Motor2_In2.low()
    Motor3_In1.low();  Motor3_In2.high()
    Motor4_In1.low();  Motor4_In2.high()
    set_speed(speed)

def stop():
    all_low()
    set_speed(0)

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
# Bluetooth command handler
# -----------------------------
def read_bt_command():
    # Non-blocking single-character commands
    if uart.any():
        try:
            c = uart.read(1)
            if not c:
                return None
            return c.decode('utf-8', errors='ignore').upper()
        except:
            return None
    return None

def handle_command(cmd):
    global drive_mode, current_speed
    if cmd == 'A':
        drive_mode = MODE_AUTO
        uart.write(b"Mode: AUTO\r\n")
    elif cmd == 'S':
        drive_mode = MODE_MANUAL
        stop()
        uart.write(b"STOP\r\n")
    elif cmd == 'F':
        drive_mode = MODE_MANUAL
        forward(current_speed)
        uart.write(b"FORWARD\r\n")
    elif cmd == 'B':
        drive_mode = MODE_MANUAL
        backward(current_speed)
        uart.write(b"BACKWARD\r\n")
    elif cmd == 'L':
        drive_mode = MODE_MANUAL
        left(current_speed)
        uart.write(b"LEFT\r\n")
    elif cmd == 'R':
        drive_mode = MODE_MANUAL
        right(current_speed)
        uart.write(b"RIGHT\r\n")
    elif cmd == '+':
        current_speed = min(MAX_SPEED, current_speed + SPEED_STEP)
        set_speed(current_speed)
        uart.write(b"SPEED UP\r\n")
    elif cmd == '-':
        current_speed = max(MIN_SPEED, current_speed - SPEED_STEP)
        set_speed(current_speed)
        uart.write(b"SPEED DOWN\r\n")
    elif cmd == 'T':
        # quick test ping
        uart.write(b"PICO OK\r\n")

# -----------------------------
# Auto-follow loop (unchanged logic)
# -----------------------------
def follow_simple():
    global current_speed
    while True:
        # 1) Check Bluetooth first
        cmd = read_bt_command()
        if cmd:
            handle_command(cmd)

        # 2) If in AUTO, run ultrasonic behavior
        if drive_mode == MODE_AUTO:
            d = ultra()
            print(f"Distance: {d:.1f} cm")

            if d <= THRESHOLD_CM:
                print("Object within threshold -> FOLLOW (forward)")
                forward(current_speed)
            else:
                print("No object within threshold -> STOP")
                stop()

        utime.sleep(SAMPLE_DELAY_S)

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    print("Boot: Bluetooth + Auto-follow. Commands: A,S,F,B,L,R,+,-,T")
    uart.write(b"HC-06 Ready @9600. Send A,S,F,B,L,R,+,-,T\r\n")
    try:
        follow_simple()
    except KeyboardInterrupt:
        stop()
        print("Program stopped by user")

