import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.interpolate import griddata
from sklearn.preprocessing import minmax_scale
import pywt
import helper

""" 
@brief Slides with set window length to obtain amplitude and maximum value
@param 
n = length of total data
win_len = window length 
step = stride width  
"""
def slide_window(n, win_len, step, arr):
    maximum_value = []
    maximum_amplitude = []
    for i in range(0, n - win_len + 1, step):
        maximum_value.append(max(arr[i:i+win_len]))
        maximum_amplitude.append(max(arr[i:i+win_len]) - min(arr[i:i+win_len]))
    return maximum_value, maximum_amplitude


def zero_out_detailed(coeff, level):
    for i in range(1,level+1):
        for j in range(0, len(coeff[i])):
            coeff[i][j] = 0


plot_schedule_flag = True
plot_show_flag = True
export_data_flag = True

# Iterate from File 1 to File 15
for num in range(1, 16):
    read_path = '../Sensor_Data/GSR_30s_Sliced_Sub10/sliced_FS'
    file_number = '10e' + str(num)
    csv_file_extension = '.csv'
    png_file_extension = '.png'
    save_path = './Signal_Processing_Results/'

    raw_data = pd.read_csv(read_path + file_number + csv_file_extension, sep=',', header=None)
    mother_wavelet = pywt.Wavelet('db3')

    if plot_schedule_flag:
        plt.plot(raw_data.iloc[:,4])
        plt.title('Raw Data')
    if export_data_flag:
        plt.savefig(save_path+file_number+'_raw_'+png_file_extension)
    if plot_show_flag:
        plt.show()

    gsr_raw = raw_data.iloc[:,4]

    # A10 Coefficient
    coeffs_ten = pywt.wavedec(raw_data.iloc[:,4], mother_wavelet, level=10)
    zero_out_detailed(coeffs_ten, 10)
    recon_ten = pywt.waverec(coeffs_ten, 'db3')

    # A8 Coefficient
    coeffs_eight = pywt.wavedec(raw_data.iloc[:, 4], mother_wavelet, level=8)
    zero_out_detailed(coeffs_eight, 8)
    recon_eight = pywt.waverec(coeffs_eight, 'db3')

    # A6 Coefficient
    coeffs_six = pywt.wavedec(raw_data.iloc[:, 4], mother_wavelet, level=6)
    zero_out_detailed(coeffs_six, 6)
    recon_six = pywt.waverec(coeffs_six, 'db3')

    # Phasic = GSR - A10
    # SCVSR = A8 - A10
    # SCSR = A6 - A10
    time_domain_size = min(len(gsr_raw), len(recon_ten), len(recon_eight), len(recon_six))
    phasic = []
    scvsr = []
    scsr = []

    for i in range(0, time_domain_size):
        phasic.append(gsr_raw[i] - recon_ten[i])
        scvsr.append(recon_eight[i] - recon_ten[i])
        scsr.append(recon_six[i] - recon_ten[i])

    ## normalize extract parameters
    norm_phasic = minmax_scale(phasic)
    norm_scvsr = minmax_scale(scvsr)
    norm_scsr = minmax_scale(scsr)

    for i in range(0, len(norm_scvsr)):
        norm_phasic[i] = norm_phasic[i] - 0.5
        norm_scvsr[i] = norm_scvsr[i] - 0.5
        norm_scsr[i] = norm_scsr[i] - 0.5

    if plot_schedule_flag:
        plt.plot(norm_phasic)
        plt.plot(norm_scvsr)
        plt.plot(norm_scsr)
        labels = {'phasic', 'scvsr', 'scsr'}
        plt.title('GSR Different Frequency Bandwidth Normalized')
        plt.legend(labels)
    if export_data_flag:
        plt.savefig(save_path + file_number + '_frequency_analysis_' + file_number+png_file_extension)
    if plot_show_flag:
        plt.show()

    # number of zero crossings counted for each coefficient
    zero_cross_scvsr = np.nonzero(np.diff(norm_scvsr > 0))[0]
    zero_cross_scsr = np.nonzero(np.diff(norm_scsr > 0))[0]

    rate_zero_cross_scvsr = zero_cross_scvsr.size
    rate_zero_cross_scsr = zero_cross_scsr.size

    maximum_value, maximum_amplitude = slide_window(n=norm_phasic.size, win_len=2000, step=500, arr=phasic)
    if plot_schedule_flag:
        plt.plot(maximum_amplitude)
        plt.plot(maximum_value)
        labels = {'maximum amplitude', 'maximum value'}
        plt.title('GSR Maximum Amplitude and Value')
        plt.legend(labels)

    if export_data_flag:
        plt.savefig(save_path + file_number + '_amplitude_value_' + png_file_extension)
        zero_cross_data = {
                        'Zero-cross scvsr/scsr': [zero_cross_scvsr.size, zero_cross_scsr.size]
                    }
        zero_cross_df = pd.DataFrame(zero_cross_data)
        zero_cross_df.to_csv(save_path + file_number + '_Extrac_Zero_Cross_' + csv_file_extension)
        amp_val_data = {
            'amp': maximum_amplitude,
            'val': maximum_value
        }
        amp_val_df = pd.DataFrame(amp_val_data)
        amp_val_df.to_csv(save_path + file_number + '_Extrac_Amp_Val' + csv_file_extension)

    if plot_show_flag:
        plt.show()
