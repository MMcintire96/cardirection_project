import sqlite3
import time

import matplotlib.animation as animation
import matplotlib.pyplot as plt

plt.style.use('dark_background')


def get_connection():
    conn = sqlite3.connect('cardata.db')
    c = conn.cursor()
    return c

def get_data():
    c = get_connection()
    c.execute("SELECT * FROM 'location'")
    errArr = []
    mseArr = []
    for row in c:
        errArr.append(row[4])
        mseArr.append(row[5])
    return errArr, mseArr




fig = plt.figure()
ax1 = fig.add_subplot(111)
ax2 = fig.add_subplot(111)
def refreshGraphData(i):
    errArr, mseArr = get_data()
    ax1.clear()
    ax1.plot(errArr, label='Error')
    ax2.plot(mseArr, label='MSE')
    ax1.legend(loc='best')
ani = animation.FuncAnimation(fig, refreshGraphData, interval=1000)
plt.show()
