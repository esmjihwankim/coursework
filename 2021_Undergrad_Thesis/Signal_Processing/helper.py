
import matplotlib.pyplot as plt




def plot_two(data1, data2):
    plt.subplot(121)
    plt.plot(data1)
    plt.title('gsr raw signal')
    plt.subplot(122)
    plt.plot(data2)
    plt.title('reconstructed after level 10 decom')
    plt.show()



def plot_many(coeffs):
    num = coeffs.size

    ax1 = plt.subplot(241)
    plt.title('A' + 10-num)
    graph1 = plt.plot(coeffs[0])

    ax2 = plt.subplot(242)
    plt.title('D10')
    graph2 = plt.plot(coeffs[1])

    ax3 = plt.subplot(243)
    plt.title('D9')
    graph3 = plt.plot(coeffs[2])

    ax4 = plt.subplot(244)
    plt.title('D8')
    graph4 = plt.plot(coeffs[3])

    ax5 = plt.subplot(245)
    plt.title('D7')
    graph5 = plt.plot(coeffs[4])

    ax6 = plt.subplot(246)
    plt.title('D6')
    graph6 = plt.plot(coeffs[5])

    ax7 = plt.subplot(247)
    plt.title('D5')
    graph7 = plt.plot(coeffs[6])

    ax8 = plt.subplot(248)
    plt.title('D4')
    graph8 = plt.plot(coeffs[7])
