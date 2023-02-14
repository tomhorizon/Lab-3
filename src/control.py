class Control:
    """! @brief The Control class carries out the the calculations for a proportional controller based off of Kp, the proportional
        controller constant, the set point (goal), and the current position
    """
    def __init__(self, kp, setpt):
        self.kp = kp
        self.setpt = setpt
        """! Initialization takes in the controller parameters and intiallizes the controller object
        @param kp: Kp is the controller constant (must range from 0 --> 4 for this application)
        @param setpt: setpt is the setpoint, or the encoder value for the "goal" position of the motor
        """

    def run(self, pos):
        self.error = self.setpt - pos
        self.psi = -self.kp*self.error
        return self.psi
        """! The run method takes in the current motor position and calculates and scales the error to ouput the
            necessary motor effort.
        @param pos: pos is the current motor position as read by the encoder
        """

    def set_setpoint(self, setpt_new):
        """! set_setpoint takes in the new setpoint, or goal position, of the motor and applies it to the controller object
        @param setpt_new: setpt_new is the new setpoint for the motor, given in an encoder position
        """
        self.setpt = setpt_new
        return self.setpt

    def set_Kp(self, kp_new):
        """! set_Kp takes in the new Kp, proortional controller constant, and applies it to the controller object
        @param kp_new: kp_new is the new Kp
        """
        self.kp = kp_new
        print('kp is:', self.kp)
        return self.kp
    
if __name__ == '__main__':
    con = Control(4, 180)
    con.set_Kp(5)