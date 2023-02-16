"""!
@file lab3main.py

This file is Lab 3 for ME 405. The goal of this exercise was to control a 12V
DC motor system as a servo system with a proportional controller. The motor is
connected to an external power supply and a STM32 PWM output. The built-in encoder
provides position feedback and uses STM-32 timers. At the beginning of the
program sequence, controller parameters are sent through UART serial communication
to the STM32, initializing the control algorithm.

The proportional controller is the most simple closed-loop controller, using
just one variable (Kp, the controller constant), to direcetly impact the amount
of "effort" that the motor applies. The "effort" applied to the motor is a duty
cycle percentage. To find the required duty cycle, the algorithm calculates the
difference between the setpoint (goal) and the actual position and multiplies it
by the proportional controller constant. A higher error implies a higher corrective
effort, while a lower error applied a lower corrective effort. Eventually, the
error becomes negligible and no further correction is needed.

This program uses 3 classes: MotorDriver, EncoderReader, and Control. After defining
the pins and starting the timer channels, the control loop waits for motor parameters.
Once the controller parameters (Kp and setpt) are received from the PC. The encoder
reads the position, which is used by the controller to calculate the required duty
cycle, which is applied to the motor. This loop runs for 3 seconds.

Unlike last lab though, we used Dr. Ridgley's cotask class and functions to implement
multitasking. This allowed us to accomplish the above tasks on two motors simultaneously.

@author Tom Taylor
@author Jonathan Fraser
@author Dylan Weiglein

@date   2022-02-15
"""
import pyb
import utime
from motor_driver import MotorDriver
from encoder_reader import EncoderReader
from control import Control
import cotask
import task_share


# initialize motors and encoder objects

def motor1task(shares):
    
    # motor constants
    motor1Pin1 = pyb.Pin.board.PB4
    motor1Pin2 = pyb.Pin.board.PB5
    motor1Ena = pyb.Pin.board.PA10
    motor1Tim = 3
    motor1Ch1 = 1
    motor1Ch2 = 2
    
    # encoder constants
    encoder1Pin1 = pyb.Pin.board.PB6
    encoder1Pin2 = pyb.Pin.board.PB7
    encoder1Tim = 4
    encoder1Ch1 = 1
    encoder1Ch2 = 2
    
    kp, setpoint, time, position = shares
    
    motor1 = MotorDriver(motor1Ena, motor1Pin1, motor1Pin2, motor1Tim, motor1Ch1, motor1Ch2)
    encoder1 = EncoderReader(encoder1Pin1, encoder1Pin2, encoder1Tim, encoder1Ch1, encoder1Ch2)
    control1 = Control(kp.get(), setpoint.get())
    
    encoder1.zero()
    begin = utime.ticks_ms()
    
    
    while True:
        pos1 = encoder1.read()
        psi = control1.run(pos1)
        motor1.set_duty_cycle(psi)
        
        elapsed = utime.ticks_ms() - begin
        time.put(elapsed)
        position.put(pos1)
        yield 0

def motor2task(shares):
    
    # motor constants
    motor2Pin1 = pyb.Pin.board.PA0
    motor2Pin2 = pyb.Pin.board.PA1
    motor2Ena = pyb.Pin.board.PC1
    motor2Tim = 5
    motor2Ch1 = 1
    motor2Ch2 = 2
    
    # encoder constants
    encoder2Pin1 = pyb.Pin.board.PC6
    encoder2Pin2 = pyb.Pin.board.PC7
    encoder2Tim = 8
    encoder2Ch1 = 1
    encoder2Ch2 = 2
    
    kp, setpoint, position = shares
    motor2 = MotorDriver(motor2Ena, motor2Pin1, motor2Pin2, motor2Tim, motor2Ch1, motor2Ch2)
    encoder2 = EncoderReader(encoder2Pin1, encoder2Pin2, encoder2Tim, encoder2Ch1, encoder2Ch2)
    
    control2 = Control(kp.get(), setpoint.get())
    encoder2.zero()
    while True:
        pos2 = encoder2.read()
        psi = control2.run(pos2)
        motor2.set_duty_cycle(psi)
        position.put(pos2)
        yield 0

    

def main():
    runTime = 1000
    
    print("Waiting for parameters from PC.")
    ser = pyb.UART(2, baudrate=115200, timeout = 10)
    while(not ser.any()):
        #print("No data")
        pyb.delay(100)
        pass

    setPoint1 = int(ser.readline().strip())
    setPoint2 = int(ser.readline().strip())
    KP1 = float(ser.readline().strip())
    KP2 = float(ser.readline().strip())
    WaitTime = float(ser.readline().strip())
    
        # Create a share and a queue to test function and diagnostic printouts
    KP1share = task_share.Share('f', thread_protect=False, name="KP 1")
    SP1share = task_share.Share('h', thread_protect=False, name="Setpoint 1")
    KP2share = task_share.Share('f', thread_protect=False, name="KP 2")
    SP2share = task_share.Share('h', thread_protect=False, name="Setpoint 2")
    timeQ = task_share.Queue('l', 1000, thread_protect=False, overwrite=True, name="Time data")
    pos1Q = task_share.Queue('l', 1000, thread_protect=False, overwrite=True, name="Motor 1 position")
    pos2Q = task_share.Queue('l', 1000, thread_protect=False, overwrite=True, name="Motor 2 position")
    
    timeQ.clear()
    pos1Q.clear()
    pos2Q.clear()

    task_1 = cotask.Task (motor1task, name = "Control Motor 1",
                          priority = 1, period = WaitTime, profile = True, trace=False, shares=(KP1share, SP1share, timeQ, pos1Q))
    task_2 = cotask.Task (motor2task, name = "Control Motor 2",
                          priority = 1, period = WaitTime, profile = True,trace=False, shares=(KP2share, SP2share, pos2Q))
    cotask.task_list.append (task_1)
    cotask.task_list.append (task_2)
    
    KP1share.put(KP1)
    SP1share.put(setPoint1)
    KP2share.put(KP2)
    SP2share.put(setPoint2)
    
    print(f'{setPoint1}, {KP1}, {setPoint2}, {KP2}')
    
    while timeQ.num_in() < (runTime / WaitTime):
        cotask.task_list.pri_sched ()
    
    print("Control Loop Complete")
    #motor1.set_duty_cycle(0)
    #motor2.set_duty_cycle(0)

    ser.write(f'{KP1}\r\n')
    ser.write(f'{KP2}\r\n')
    ser.write(f'{timeQ.num_in()}\r\n')
    
    while timeQ.empty() == 0:
        ser.write(f'{timeQ.get()}, {pos1Q.get()}, {pos2Q.get()}\r\n')
    print("sent")
    
if __name__ == "__main__":
    while True:
        main()

