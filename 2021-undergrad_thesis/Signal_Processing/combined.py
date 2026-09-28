import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import heartpy as hp #이 모듈은 깔아야 import 할수 있음
import seaborn as sns
import scipy.stats as ss
import pywt

from sklearn.preprocessing import minmax_scale

colname = ['ppg_grn', 'SKT', 'GSR', 'valence', 'arousal']
#data = pd.read_csv('WMinMaxs2e5.csv', header = None)
#data.columns = colname

MotherWavelet_ppg = pywt.Wavelet('db2')   # Mother wavelet (모함수) 지정
MotherWavelet_gsr = pywt.Wavelet('db3')

select  = 4                    # 특징추출 영역 고주파 영역부터 개수 지정 (d1~)


# 함수 정의
def rms(x):
    return np.sqrt(np.mean(x**2))

def crestF(x):
    return np.max(x) / rms(x)

def shapeF(x):
    return rms(x) / np.mean(x)

def impulseF(x):
    return np.max(x)/ np.mean(x)

def zero_out_detailed(coeff, level):
    for i in range(1, level+1):
        for j in range(0, len(coeff[i])):
            coeff[i][j] = 0

def slide_window(n, win_len, step, arr):
    maximum_value = []
    maximum_amplitude = []
    for i in range(0, n - win_len + 1, step):
        maximum_value.append(max(arr[i:i+win_len]))
        maximum_amplitude.append(max(arr[i:i+win_len]) - min(arr[i:i+win_len]))
    return maximum_value, maximum_amplitude


# 결과값 딕셔너리로 반환 함수
def NN_dictionary(working_data, time_interval, data1, strd):
    jump = int(time_interval / strd)
    RR_list = working_data['RR_list']
    RR_diff = working_data['RR_diff']
    cum = np.cumsum(RR_list)
    time = list(range(0, int(cum[-1]), strd))

    # PPG 시간영역(0~5)
    meanNN = []
    medianNN = []
    SDNN = []
    pNN50 = []
    NN50 = []
    RMSSD = []

    # PPG 주파수영역(6~16)
    maxFPPG = []
    minFPPG = []
    meanFPPG = []
    stdFPPG = []
    maxminFPPG = []
    kurFPPG = []
    skewFPPG = []
    rmsFPPG = []
    crestFPPG = []
    shapeFPPG = []
    impulseFPPG = []

    # GSR 시간영역(17~27)
    maxGSR = []
    minGSR = []
    meanGSR = []
    stdGSR = []
    maxminGSR = []
    kurGSR = []
    skewGSR = []
    rmsGSR = []
    crestGSR = []
    shapeGSR = []
    impulseGSR = []

    # GSR 주파수영역(28-31)
    zeroCrossScvsrFGSR = []
    zeroCrossScsrFGSR = []
    phasicMaxAmpFGSR = []
    phasicMaxValFGSR = []

    # SKT 시간영역(31~41)
    maxSKT = []
    minSKT = []
    meanSKT = []
    stdSKT = []
    maxminSKT = []
    kurSKT = []
    skewSKT = []
    rmsSKT = []
    crestSKT = []
    shapeSKT = []
    impulseSKT = []

    # valence arousal labeling(41~44)
    label_valence = []
    label_arousal = []
    valence = []
    arousal = []

    for i in range(0, len(time) - jump):
        data1 = data.iloc[int(i * fs * time_interval / 1000): int((i + 1) * fs * time_interval / 1000), 0:5]
        print(data1.shape)
        print(data1)
        idx = (cum >= time[i]) & (cum < time[i + jump])
        NN = RR_list[idx]
        diff = []
        for j in range(0, len(NN) - 1):
            diff.append(NN[j + 1] - NN[j])

        num50 = sum(np.array(diff) > 50)

        if len(diff) > 0:
            p50 = num50 / len(diff)
        else:
            p50 = 0
        rmssd = np.sqrt(np.mean(sum(NN ** 2)))

        meanNN.append(np.mean(NN))
        medianNN.append(np.median(NN))
        SDNN.append(np.std(NN))
        NN50.append(num50)
        pNN50.append(p50)
        RMSSD.append(rmssd)

        LevelFour = 4
        PPGCoef = pywt.wavedec(data1['ppg_grn'], MotherWavelet_ppg, level=LevelFour, axis=0)
        ppgApprCoef = PPGCoef[LevelFour]

        LevelTen = 10
        GSRCoef = pywt.wavedec(data1['GSR'], MotherWavelet_gsr, level=LevelTen, axis=0)


        maxFPPG.append(np.max(ppgApprCoef))
        minFPPG.append(np.min(ppgApprCoef))
        meanFPPG.append(np.mean(ppgApprCoef))
        stdFPPG.append(np.std(ppgApprCoef))
        maxminFPPG.append(np.ptp(ppgApprCoef))
        kurFPPG.append(ss.kurtosis(ppgApprCoef))
        skewFPPG.append(ss.skew(ppgApprCoef))
        rmsFPPG.append(rms(ppgApprCoef))
        crestFPPG.append(crestF(ppgApprCoef))
        shapeFPPG.append(shapeF(ppgApprCoef))
        impulseFPPG.append(impulseF(ppgApprCoef))

        maxGSR.append(np.max(data1['GSR']))
        minGSR.append(np.min(data1['GSR']))
        meanGSR.append(np.mean(data1['GSR']))
        stdGSR.append(np.std(data1['GSR']))
        maxminGSR.append(np.ptp(data1['GSR']))
        kurGSR.append(ss.kurtosis(data1['GSR']))
        skewGSR.append(ss.skew(data1['GSR']))
        rmsGSR.append(rms(data1['GSR']))
        crestGSR.append(crestF(data1['GSR']))
        shapeGSR.append(shapeF(data1['GSR']))
        impulseGSR.append(impulseF(data1['GSR']))

        maxSKT.append(np.max(data1['SKT']))
        minSKT.append(np.min(data1['SKT']))
        meanSKT.append(np.mean(data1['SKT']))
        stdSKT.append(np.std(data1['SKT']))
        maxminSKT.append(np.ptp(data1['SKT']))
        kurSKT.append(ss.kurtosis(data1['SKT']))
        skewSKT.append(ss.skew(data1['SKT']))
        rmsSKT.append(rms(data1['SKT']))
        crestSKT.append(crestF(data1['SKT']))
        shapeSKT.append(shapeF(data1['SKT']))
        impulseSKT.append(impulseF(data1['SKT']))

        valence.append(np.mean(data1['valence']))
        arousal.append(np.mean(data1['arousal']))
        label_valence.append(int(np.mean(data1['valence']) * 3 / 10.01) - 1)
        label_arousal.append(int(np.mean(data1['arousal']) * 3 / 10.01) - 1)

    result = {'meanNN': meanNN,
              'medianNN': medianNN,
              'SDNN': SDNN,
              'pNN50': pNN50,
              'NN50': NN50,
              'RMSSD': RMSSD,  # ,'HR':HR

              'maxFPPG': maxFPPG,
              'minFPPG': minFPPG,
              'meanFPPG': meanFPPG,
              'stdFPPG': stdFPPG,
              'maxminFPPG': maxminFPPG,
              'kurFPPG': kurFPPG,
              'skewFPPG': skewFPPG,
              'rmsFPPG': rmsFPPG,
              'crestFPPG': crestFPPG,
              'shapeFPPG': shapeFPPG,
              'impulseFPPG': impulseFPPG,

              'maxGSR': maxGSR,
              'minGSR': minGSR,
              'meanGSR': meanGSR,
              'stdGSR': stdGSR,
              'maxminGSR': maxminGSR,
              'kurGSR': kurGSR,
              'skewGSR': skewGSR,
              'rmsGSR': rmsGSR,
              'crestGSR': crestGSR,
              'shapeGSR': shapeGSR,
              'impulseGSR': impulseGSR,

              'zeroCrossScvsrFGSR': zeroCrossScvsrFGSR,
              'zeroCrossScsrFGSR': zeroCrossScsrFGSR
              'phasicMaxAmpFGSR': phasicMaxAmpFGSR,
              'phasicMaxValFGSR': phasicMaxValFGSR,

              'maxSKT': maxSKT,
              'minSKT': minSKT,
              'meanSKT': meanSKT,
              'stdSKT': stdSKT,
              'maxminSKT': maxminSKT,
              'kurSKT': kurSKT,
              'skewSKT': skewSKT,
              'rmsSKT': rmsSKT,
              'crestSKT': crestSKT,
              'shapeSKT': shapeSKT,
              'impulseSKT': impulseSKT,

              'valence': valence,
              'arousal': arousal,
              'label_valence': label_valence,
              'label_arousal': label_arousal

              }

    return result

"""
working_data, measures = hp.process(data['ppg_grn'].values, fs, calc_freq=True)
result = pd.DataFrame(NN_dictionary(working_data, time_interval, data))
print(result)
"""

# result.to_csv('timefeaturetest.csv', index = False)
# sns.pairplot(result)
# plt.show()

fs = 398
time_interval = 12000
strd = 400

Dir = 'C:/Users/Jihwan/Desktop/Test_Data'  # 경로 설정
outputDir = 'C:/Users/Jihwan/Desktop/Processed/'
os.chdir(Dir)
filelist = os.listdir(Dir)  # Dir 경로 폴더 안 모든 파일 이름 리스트

# idx=0;

for file in filelist:
    data = pd.read_csv(file, header=None)
    data.columns = colname
    working_data, measures = hp.process(data['ppg_grn'].values, fs, calc_freq=False)
    result = pd.DataFrame(NN_dictionary(working_data, time_interval, data, strd))
    result.to_csv(outputDir + file, index=False)
