"""!
@file PCSide.py

This file is required to execute the ME 405 main program, "lab2main.py".
The purpose of this file is to request user input for the controller parameters,
Kp (proportional controller constant), and setpt (Setpoint, positional goal of servo).
Once user input is received, the data is communicated through serial UART communication
to the STM32, subsequentlly activating the control loop.

@author Tom Taylor
@author Jonathan Fraser
@author Dylan Weiglein

@date   2022-02-08
"""

# send a KP and setpoint from the PC side
import serial
from matplotlib import pyplot as plt

# adjust as needed for your computer
# tom           - COM8
# jonathan      - COM6
COMPORT = 'COM8'
ls = "\r\n".encode()

def userEntry():
    # get user parameters
    setpoint1 = input("Enter setpoint for motor 1: ").encode()
    setpoint2 = input("Enter setpoint for motor 2: ").encode()
    KP1 = input("Enter KP 1: ").encode()
    KP2 = input("Enter KP 2: ").encode()

    # send user parameters
    with serial.Serial(COMPORT, 115200, timeout=10) as s_port:
        s_port.write(setpoint1 + ls +
                     setpoint2 + ls +
                     KP1 + ls + KP2)
    print("Parameters Sent")

# read the resulting data,
# plot the step response with correctly labeled axes and title.
def plotter():
    x_values = []
    y1_values = []
    y2_values = []
    with(serial.Serial(COMPORT, 115200, timeout = 10) as ser):
        expectedLength = ser.readline().strip()
        KPused1 = ser.readline().strip()
        KPused2 = ser.readline().strip()

        for i in range(int(expectedLength)):
            newline = ser.readline().strip().split(b',')
            # try to convert each line into numbers
            try:
                x = float(newline[0])
                y1 = float(newline[1])
                y2 = float(newline[2])

                # only if both numbers are converted do they append
                x_values.append(x)
                y1_values.append(y1)
                y2_values.append(y2)
            except ValueError:
                pass

    # plot, label, and display - fun stuff found at:
    plt.plot(x_values, y1_values, 'k', label = "KP1 of " + str(float(KPused1)))
    plt.plot(x_values, y2_values, 'g', label = "KP2 of " + str(float(KPused2)))
    plt.minorticks_on()
    plt.axhline(y=0, color='black', linewidth = .3)
    plt.axvline(x=0, color='black', linewidth = .3)
    plt.title("Position vs. Time", size=16)
    plt.xlabel("Time, t [ms]")
    plt.ylabel("Motor Position, x [encoder ticks]")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    userEntry()
    plotter()