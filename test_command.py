
import time
from listeners.runcommandprocess import RunCommandProcess

if __name__ == '__main__':
    process1 = RunCommandProcess(command='ping 127.0.0.1')
    process1.start()

    time.sleep(0.1)

    process2 = RunCommandProcess(command='ping 127.0.0.2')
    process2.start()

    time.sleep(0.1)

    process3 = RunCommandProcess(command='ping 127.0.0.3')
    process3.start()

    time.sleep(0.1)