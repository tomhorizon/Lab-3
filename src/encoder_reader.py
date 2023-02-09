import pyb


class EncoderReader:
    """! @brief The encoder is built into the DC motor. A quadrature
    encoder uses two channels to capture changes in position.
    """

    def __init__(self, pin1, pin2, position, old_count):
        """! Initialization takes in the pins and sets the initial position to a
        received value.
        @param pin1: Pin 1 is used for encoder channel A.
        @param pin2: Pin 2 is used for encoder channel B.
        @param position: Position is send to the encoder for reference.
        @param old_count: The previous count is compared for overflow correction.
        """
        self.pin1 = pyb.Pin(pin1, pyb.Pin.IN)
        self.pin2 = pyb.Pin(pin2, pyb.Pin.IN)

        self.timer = pyb.Timer(4, prescaler=0, period=0xFFFF)

        self.ch1 = self.timer.channel(1, pyb.Timer.ENC_AB, pin=pin1)
        self.ch2 = self.timer.channel(2, pyb.Timer.ENC_AB, pin=pin2)

        self.position = position
        self.old_count = old_count

    def read(self):
        """! This function returns the position of the motor when called.
        It calls the STM32 timer that has been incrementing with every
        encoder signal. Limited by 16 bits, the encoder will overflow back
        to zero or, if moving backwards, underflow to the max value
        again.
        """
        counter = self.timer.counter()
#         if counter > self.old_count + 32000:
#             self.position = self.position + counter
#             #print('+')
#         elif counter < self.old_count - 32000:
#             self.position = self.position - counter
#             #print('-')
#         self.old_count = counter
#         #print(self.position)
#         return self.position
        return counter

    def zero(self):
        """! The count can be manually reset to zero when starting a new measurement.
        """
        self.timer.counter(0)


if __name__ == '__main__':
    p1 = pyb.Pin.board.PB6
    p2 = pyb.Pin.board.PB7
    enc = EncoderReader(p1, p2, 0, 0)
    while True:
        pos = enc.read()
        #print(pos)
        if enc.timer.counter() > 40000:
            #print('reset')
            enc.zero()
        pyb.delay(100)
