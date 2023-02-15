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
        
        time.put(utime.ticks_ms() - begin)
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
    
def setup():
    # Create a share and a queue to test function and diagnostic printouts
    share0 = task_share.Share('f', thread_protect=False, name="KP 1")
    share1 = task_share.Share('h', thread_protect=False, name="Setpoint 1")
    share2 = task_share.Share('f', thread_protect=False, name="KP 2")
    share3 = task_share.Share('h', thread_protect=False, name="Setpoint 2")
    queue0 = task_share.Queue('l', 1000, thread_protect=False, overwrite=True, name="Time data")
    queue1 = task_share.Queue('l', 1000, thread_protect=False, overwrite=True, name="Motor 1 position")
    queue2 = task_share.Queue('l', 1000, thread_protect=False, overwrite=True, name="Motor 2 position")
    
    queue0.clear()
    queue1.clear()
    queue2.clear()

    task_1 = cotask.Task (motor1task, name = "Control Motor 1",
                          priority = 1, period = 20, profile = True, trace=False, shares=(share0, share1, queue0, queue1))
    task_2 = cotask.Task (motor2task, name = "Control Motor 2",
                          priority = 1, period = 20, profile = True,trace=False, shares=(share2, share3, queue2))
    cotask.task_list.append (task_1)
    cotask.task_list.append (task_2)
    
    return share0, share1, share2, share3, queue0, queue1, queue2 
    

    
def main(a, b, c, d, e, f, g):
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
    
    a.put(KP1)
    b.put(setPoint1)
    c.put(KP2)
    d.put(setPoint2)
    
    print(f'{setPoint1}, {KP1}, {setPoint2}, {KP2}')
    pyb.delay(1000)

    t = []
    y1 = []
    y2 = []
    elapsed = 0
    startTime = utime.ticks_ms()
    
    print("Entering Control Loop")
    while elapsed < 500:
        currentTime = utime.ticks_ms()
        elapsed = currentTime - startTime
        cotask.task_list.pri_sched ()
    
    print("Control Loop Complete")
    #motor1.set_duty_cycle(0)
    #motor2.set_duty_cycle(0)

    ser.write(f'{KP1}\r\n')
    ser.write(f'{KP2}\r\n')
    ser.write(f'{e.num_in()}\r\n')
    
    while e.empty() == 0:
        ser.write(f'{e.get()}, {f.get()}, {g.get()}\r\n')
    print("sent")
    ser.write("done")
    
if __name__ == "__main__":
    while True:
        a,b,c,d,e,f,g = setup()
        main(a,b,c,d,e,f,g)
