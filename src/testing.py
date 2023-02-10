import pyb
import utime
from pyb import UART

# motor constants
motor1Pin1 = PB4
motor1Pin2 = PB5
motor1Ena = A10 
motor1Tim = 3
motor1Ch1 = 1
motor1Ch2 = 2
motor2Pin1 = PA0
motor2Pin2 = PA1
motor2Ena = PC1
motor2Tim = 5
motor2Ch1 = 1
motor2Ch2 = 2

# encoder constants
encoder1Pin1 = PB6
encoder1Pin2 = PB7
encoder1Tim = 4
encoder1Ch1 = 1
encoder1Ch2 = 2
encoder2Pin1 = PC6
encoder2Pin2 = PC7
encoder2Tim = 8
encoder2Ch1 = 1
encoder2Ch2 = 2

# initialize motors and encoder objects
motor1 = motor_driver(motor1Ena, motor1Pin1, motor1Pin2, motor1Tim, motor1Ch1, motor1Ch2)
motor2 = motor_driver(motor2Ena, motor2Pin1, motor2Pin2, motor2Tim, motor2Ch1, motor2Ch2)
encoder1 = encoder_reader(encoder1Pin1, encoder1Pin2, encoder1Tim, encoder1Ch1, encoder1Ch2)
encoder2 = encoder_reader(encoder2Pin1, encoder2Pin2, encoder2Tim, encoder2Ch1, encoder2Ch2)

'''
works for motor 1 and encoder 1
motorTimer = pyb.Timer(3, freq=20000)
motorpin1 = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP)
motorpin2 = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP)
enablepin = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.IN, pyb.Pin.PULL_UP)
motorch1 = motorTimer.channel(1, pyb.Timer.PWM, pin=motorpin1)
motorch2 = motorTimer.channel(2, pyb.Timer.PWM, pin=motorpin2)

encoderTimer = pyb.Timer(4, prescaler=0, period=0xFFFF)
encoderpin1 = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.IN)
encoderpin2 = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.IN)
encoderch1 = encoderTimer.channel(1, pyb.Timer.ENC_AB, pin=encoderpin1)
encoderch2 = encoderTimer.channel(2, pyb.Timer.ENC_AB, pin=encoderpin2)


#work for motor2 / encoder 2

motorTimer = pyb.Timer(5, freq=20000)
motorpin1 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP)
motorpin2 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
enablepin = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.IN, pyb.Pin.PULL_UP)
motorch1 = motorTimer.channel(1, pyb.Timer.PWM, pin=motorpin1)
motorch2 = motorTimer.channel(2, pyb.Timer.PWM, pin=motorpin2)

encoderTimer = pyb.Timer(8, prescaler=0, period=0xFFFF)
encoderpin1 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.IN)
encoderpin2 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.IN)
encoderch1 = encoderTimer.channel(1, pyb.Timer.ENC_AB, pin=encoderpin1)
encoderch2 = encoderTimer.channel(2, pyb.Timer.ENC_AB, pin=encoderpin2)
'''


def set_duty_cycle(level):
    if level <= 0:
        level = -1 * level
        motorch1.pulse_width_percent(level)
        motorch2.pulse_width_percent(0)
    else:
        motorch1.pulse_width_percent(0)
        motorch2.pulse_width_percent(level)


def read():
    count = encoderTimer.counter()
    return count



#ser = pyb.USB_VCP()
#ser = pyb.UART(2, baudrate=115200, timeout = 10)

def main():
    ser = pyb.UART(2, baudrate=115200, timeout = 10)
    while(not ser.any()):
        print("No data")
        pyb.delay(100)
        pass
    setPoint1 = int(ser.readline().strip())
    setPoint2 = int(ser.readline().strip())
    KP1 = float(ser.readline().strip())
    KP2 = float(ser.readline().strip())
    
    encoderTimer.counter(0)
    t = []
    y1 = []
    y2 = []

    startTime = utime.ticks_ms()
    while True:
        currentTime = utime.ticks_ms()
        elapsed = currentTime - startTime
        pos1 = encoder1.read()
        pos2 = encoder2.read()
        t.append(elapsed)
        y1.append(pos1)
        y2.append(pos2)
        
        error1 = setPoint1 - pos1
        
        set_duty_cycle(-(KP1 * error1))
        pyb.delay(10)
        print(pos1)

    set_duty_cycle(0)
    pyb.delay(5000)

    
    u2 = pyb.UART(2, baudrate=115200, timeout = 10)
    u2.write(f'{len(y)}\r\n')
    u2.write(f'{KP}\r\n')
    for i in range(0, len(y)):  # Just some example output
        u2.write(f'{t[i]}, {y[i]}\r\n')  # The "\r\n" is end-of-line stuff
    print("sent")
    
while True:
    
    main()
