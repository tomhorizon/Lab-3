In this experiment we used much of the previous lab to use proportional
control on a dc motor's position. This time though, we used Dr. Ridgley's
cotask class and function to accomplish the same thing on two motors at once.

We were able to have both our motors function quickly and with effective
proportional control. We found a cotask period of 10 milliseconds to be a
very optimal delay between each task. See image below

![Ideal Response](/ideal_response2.png)


This next image shows a period delay double that of the previous, 20 milliseconds
As you can see, if the delay or period between the tasks is too high, the motor
cannot properly correct itself, as it is overshooting while the other task is running.

![Large Period](/too_much_delay2.png)