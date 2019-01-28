import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

def get_err():
    err = []
    with open('testerr.txt', 'r') as f:
        for line in f:
            line = line.strip('\n')
            line = float(line)
            err.append(line)
    return err


def get_mse():
    mse = []
    with open('testmse.txt', 'r') as f_mse:
        for line in f_mse:
            line = line.strip('\n')
            line = float(line)
            mse.append(line)
    return mse


fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = fig.add_subplot(111)
def refreshGraphData(i):
    mse = get_mse()
    err = get_err()
    if len(err) != len(mse):
        if len(err) > len(mse):
            diff = len(err) - len(mse)
            err.pop(len(err) - diff)
        else:
            diff = len(mse) - len(err)
            mse.pop(len(mse) - diff)
    ax1.clear()
    ax1.plot(err, color='red', label='Error')
    ax2.plot(mse, color='blue', label='MSE')
    ax1.legend(loc='best')
ani = animation.FuncAnimation(fig, refreshGraphData, interval=3000)
plt.show()



