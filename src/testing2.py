import pyb
import utime
from motor_driver import MotorDriver
from encoder_reader import EncoderReader
from control import Control
import cotask

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

def motor1task(shares):
    kp, setpoint = shares
    motor1 = MotorDriver(motor1Ena, motor1Pin1, motor1Pin2, motor1Tim, motor1Ch1, motor1Ch2)
    encoder1 = EncoderReader(encoder1Pin1, encoder1Pin2, encoder1Tim, encoder1Ch1, encoder1Ch2)
    control1 = Control(kp.get(), setpoint.get())
    
    while True:
        pos1 = encoder1.read()
        psi = control1.run(pos1)
        motor1.set_duty_cycle(psi)
        yield pos1

def motor2task(shares):
    
    kp, setpoint = shares
    motor2 = MotorDriver(motor2Ena, motor2Pin1, motor2Pin2, motor2Tim, motor2Ch1, motor2Ch2)
    encoder2 = EncoderReader(encoder2Pin1, encoder2Pin2, encoder2Tim, encoder2Ch1, encoder2Ch2)
    control2 = Control(kp.get(), setpoint.get())
    
    while True:
        pos2 = encoder2.read()
        psi = control2.run(pos2)
        motor2.set_duty_cycle(psi)
        yield pos2
    
    
def setup():
    task_1 = cotask.Task (motor1task, name = "Control Motor 1",
                          priority = 1, period = 10, profile = True)
    task_2 = cotask.Task (motor2task, name = "Control Motor 2",
                          priority = 1, period = 10, profile = True)
    cotask.task_list.append (task_1)
    cotask.task_list.append (task_2)
    
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
        cotask.task_list.pri_sched ()
        
    motor1.set_duty_cycle(0)
    motor2.set_duty_cycle(0)

    ser.write(f'{len(y1)}\r\n')
    ser.write(f'{KP1}\r\n')
    ser.write(f'{KP2}\r\n')
    for i in range(0, len(y1)):  
        ser.write(f'{t[i]}, {y1[i]}, {y2[i]}\r\n')  
    print("sent")
    
while True:
    setup()
    while True:
        main()
