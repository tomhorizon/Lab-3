import pyb
import utime
from motor_driver import MotorDriver
from encoder_reader import EncoderReader
from control import Control

# motor constants
motor1Pin1 = pyb.Pin.board.PB4
motor1Pin2 = pyb.Pin.board.PB5
motor1Ena = pyb.Pin.board.PA10
motor1Tim = 3
motor1Ch1 = 1
motor1Ch2 = 2

motor2Pin1 = pyb.Pin.board.PA0
motor2Pin2 = pyb.Pin.board.PA1
motor2Ena = pyb.Pin.board.PC1
motor2Tim = 5
motor2Ch1 = 1
motor2Ch2 = 2

# encoder constants
encoder1Pin1 = pyb.Pin.board.PB6
encoder1Pin2 = pyb.Pin.board.PB7
encoder1Tim = 4
encoder1Ch1 = 1
encoder1Ch2 = 2
encoder2Pin1 = pyb.Pin.board.PC6
encoder2Pin2 = pyb.Pin.board.PC7
encoder2Tim = 8
encoder2Ch1 = 1
encoder2Ch2 = 2

# initialize motors and encoder objects
motor1 = MotorDriver(motor1Ena, motor1Pin1, motor1Pin2, motor1Tim, motor1Ch1, motor1Ch2)
motor2 = MotorDriver(motor2Ena, motor2Pin1, motor2Pin2, motor2Tim, motor2Ch1, motor2Ch2)
encoder1 = EncoderReader(encoder1Pin1, encoder1Pin2, encoder1Tim, encoder1Ch1, encoder1Ch2)
encoder2 = EncoderReader(encoder2Pin1, encoder2Pin2, encoder2Tim, encoder2Ch1, encoder2Ch2)


def main():
    
    ser = pyb.UART(2, baudrate=115200, timeout = 10)
    while(not ser.any()):
        #print("No data")
        pyb.delay(100)
        pass
    setPoint1 = int(ser.readline().strip())
    setPoint2 = int(ser.readline().strip())
    KP1 = float(ser.readline().strip())
    KP2 = float(ser.readline().strip())
    control1 = Control(KP1, setPoint1)
    control2 = Control(KP2, setPoint2)
    
    print(f'{setPoint1}, {KP1}, {setPoint2}, {KP2}')
    pyb.delay(1000)
    
    encoder1.zero()
    encoder2.zero()
    
    t = []
    y1 = []
    y2 = []

    elapsed = 0
    startTime = utime.ticks_ms()
    
    while elapsed < 3000:
        currentTime = utime.ticks_ms()
        elapsed = currentTime - startTime
        t.append(elapsed)

        pos1 = encoder1.read()
        y1.append(pos1)
        psi = control1.run(pos1)
        motor1.set_duty_cycle(psi)
        pyb.delay(5)
        
        pos2 = encoder2.read()
        y2.append(pos2)
        psi = control2.run(pos2)
        motor2.set_duty_cycle(psi)
        pyb.delay(5)
    

    motor1.set_duty_cycle(0)
    motor2.set_duty_cycle(0)

    
    u2 = pyb.UART(2, baudrate=115200, timeout = 10)
    u2.write(f'{len(y1)}\r\n')
    u2.write(f'{KP1}\r\n')
    u2.write(f'{KP2}\r\n')
    for i in range(0, len(y1)):  # Just some example output
        u2.write(f'{t[i]}, {y1[i]}, {y2[i]}\r\n')  # The "\r\n" is end-of-line stuff
    print("sent")
    
while True:
    
    main()
