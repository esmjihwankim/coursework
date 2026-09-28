
import csv
import matplotlib.pyplot as plt


def process(file, x, y):
    ppg_red_data = []
    ppg_ir_data = []
    ppg_grn_data = []
    skin_tmp_data = []
    gsr_data = []
    timestamp = []
    valence_data = []
    arousal_data = []
    with open(file, newline='') as csvfile:
        idx = 0
        reader = csv.reader(csvfile, delimiter=' ', quotechar= '|')
        for row in reader:
            myrow = row[0].split(",")
            idx = 0
            for e in myrow:
                myrow[idx] = float(e)
                idx += 1
            ppg_red_data.append(myrow[0])
            ppg_ir_data.append(myrow[1])
            ppg_grn_data.append(myrow[2])
            skin_tmp_data.append(myrow[3])
            gsr_data.append(myrow[4])
            timestamp.append(myrow[5])
            valence_data.append(myrow[6])
            arousal_data.append(myrow[7])
            idx += 1
        # all data saved in separate array
        # TODO: make graph and place different plots onto it
        output_file = 'images/S' + str(x) + 'e' + str(y)
        fig = plt.figure()
        fig.suptitle(output_file)
        ax1 = plt.subplot(241)
        ax1.set_title("ppg_red")
        graph1 = plt.plot(ppg_red_data)
        ax2 = plt.subplot(242)
        ax2.set_title("ppg_ir")
        graph2 = plt.plot(ppg_ir_data)
        ax3 = plt.subplot(243)
        ax3.set_title("ppg_grn")
        graph3 = plt.plot(ppg_grn_data)
        ax4 = plt.subplot(244)
        ax4.set_title("skin_temp")
        graph4 = plt.plot(skin_tmp_data)
        ax5 = plt.subplot(245)
        ax5.set_title("gsr")
        graph5 = plt.plot(gsr_data)
        ax6 = plt.subplot(246)
        ax6.set_title("valence")
        graph6 = plt.plot(valence_data)
        ax7 = plt.subplot(247)
        ax7.set_title("arousal")
        graph7 = plt.plot(arousal_data)
        plt.tight_layout()
        #TODO: save
        fig.savefig(output_file)
        #end of loop
    #end of func


for i in range(9, 11):
    for j in range(1, 16):
        experiment_number = i
        stage_number = j
        file_name = "S" + str(experiment_number) + "e" + str(stage_number) + ".csv"
        process(file_name, i, j)


