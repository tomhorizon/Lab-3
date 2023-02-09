import pyb


class MotorDriver:
    """! @brief The DC motor is powered by an external 12V supply. The STM32
    provides a PWM signal that is then turned into -12 to +12V.
    """
    def __init__(self, en_pin, in1pin, in2pin, timer):
        """! The initialization sets up the output pins and PWM channel.
        @param in1pin: Channel 1 on pin 1 is used for PWM forward.
        @param in2pin: Channel 2 on pin 2 is used for PWM reverse.
        @param en_pin: The motor must be enabled to run. This is done by pulling an input
        pin high - this convention is used so the motor can shut itself off if there
        is an internal fault detected. The input pin will convey the news to the MCU.
        @param timer: The motor receives a functioning timer channel to use.
        """
        motorpin1 = pyb.Pin(in1pin, pyb.Pin.OUT_PP)
        motorpin2 = pyb.Pin(in2pin, pyb.Pin.OUT_PP)
        enablepin = pyb.Pin(en_pin, pyb.Pin.IN, pyb.Pin.PULL_UP)

        self.internaltimer = timer

        self.ch1 = timer.channel(1, pyb.Timer.PWM, pin=motorpin1)
        self.ch2 = timer.channel(2, pyb.Timer.PWM, pin=motorpin2)
        #print("Creating a motor driver")

    def set_duty_cycle(self, level):
        """! The motor will update with a new speed request from -100 to 100 percent. The new
        speed will be printed.
        @param level: Level is the requested speed and direction.
        """
        if level <= 0:
            level = -1 * level
            self.ch1.pulse_width_percent(level)
            self.ch2.pulse_width_percent(0)
        else:
            self.ch1.pulse_width_percent(0)
            self.ch2.pulse_width_percent(level)
            #print(f"Setting duty cycle to {level}")


if __name__ == '__main__':
    import time

    enablePin = pyb.Pin.board.PA10
    input1Pin = pyb.Pin.board.PB4
    input2Pin = pyb.Pin.board.PB5
    motorTimer = pyb.Timer(3, freq=20000)

    motor1 = MotorDriver(enablePin, input1Pin, input2Pin, motorTimer)
    motor1.set_duty_cycle(50)
