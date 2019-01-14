import threading
import read_bf_file
# import read_bf_file
import  numpy as np
import pylab
import pickle
from scipy.fftpack import fft, ifft
#from dwtfilter import  dwtfilter

TIMEINYERVAL = 0.05
TIMEBIASE = 0.45
TIMELEN = 54000
TIMEWINDOW = 900
IMAGETOCSIRATIO = 30

def radReverse(subcarrier):
    return map(lambda x: float("%.2f" % np.arctan(x.imag / x.real)), subcarrier)

def complexToLatitude(subcarrier):
    return  map(lambda x: float("%.2f" % abs(x)), subcarrier)

def reviseInterp(timestamp, eachsubcarrier):
    blockedTime = []
    flag, count = 0, 0
    for tIndex in range(1, len(timestamp)):
        if timestamp[tIndex] - timestamp[tIndex - 1] > TIMEINYERVAL:
            numOfInterp = int((timestamp[tIndex] - timestamp[tIndex - 1]) / TIMEBIASE)  #todo:   Timebiase needed to be fixed
            for num in range(0, numOfInterp - 1):
                blockedTime.append(tIndex)

    ca = eachsubcarrier.tolist()
    for csiIndex in blockedTime:
        ca.insert(csiIndex + count, 0)
        count+=1

    for csiApt in range(0, len(ca) - 1):
        if ca[csiApt] == 0 and ca[csiApt + 1] != 0:
            ca[csiApt] = "%.2f" % ((ca[csiApt - 1] + ca[csiApt + 1]) / 2.0)
        elif ca[csiApt] == 0 and ca[csiApt + 1] == 0:
            for zeros in range(csiApt, len(ca)):
                if ca[zeros] != 0:
                    flag = zeros
                    break
            numOfZeros = flag - csiApt
            for num in range(0, numOfZeros):
                ca[csiApt + num] = ca[csiApt + num - 1] + float('%.2f' % ((ca[flag] - ca[csiApt - 1]) / numOfZeros))

    caNew = [float(x) for x in ca]
    blockedTime.extend([x for x in range(len(caNew), TIMELEN)])
    if len(caNew) < TIMELEN:
        caNew.extend([caNew[-1] for _ in range(0, TIMELEN - len(caNew))])
    else:
        caNew = caNew[:TIMELEN]

    return caNew, blockedTime

def my_static(temp, lenfile):
        s_t = []
        s_t_list = []
        s_t_index = []
        Max = -100
        Min = 100
        T = 5
        flag = 2
        for i in range(lenfile):
            if i < lenfile - 4 :
                s_t.append(np.mean(temp[i : i + 4]))
            else:
                s_t.append(s_t[lenfile - 5])
        for i in range(lenfile):
            if temp[i] > s_t[i] + T and temp[i] >= Max and temp[i] > 0:
                Max = temp[i]
                Max_index = i
                if flag == 0:
                    s_t_list.append(Min)
                    s_t_index.append(Min_index)
                    Min = 100
                flag = 1
            elif temp[i] < s_t[i] - T and temp[i] <= Min and temp[i] > 0:
                Min = temp[i]
                Min_index = i
                if flag == 1:
                    s_t_list.append(Max)
                    s_t_index.append(Max_index)
                    Max = -100
                flag = 0
        for i in range (len(s_t_list) - 1):
            for j in range(s_t_index[i], s_t_index[i + 1]):
                temp[j] = temp[j] - (s_t_list[i] + s_t_list[i + 1]) / 2
        return temp

def linearInterpolation(matrix, timestamp):
    raw, blockedTime = None, None
    for eachsubcarrier in matrix:
        eachsubcarrier, blockedTime = reviseInterp(timestamp, eachsubcarrier)
        raw = np.array([eachsubcarrier]) if raw is None else np.append(raw, [eachsubcarrier], axis=0)

    return raw, blockedTime

def varianceOperation(*args):
    var_list = [np.var(args[0]), np.var(args[1]), np.var(args[2])]
    mini, maxi = var_list.index(min(var_list)), var_list.index(max(var_list))
    return args[mini], args[maxi]

def relativePhaseOperation(antenna_one, antenna_two, antenna_three):

    #  amplitude, relativePhase_one, relativePhase_two = None, None,None
    # antenna_two= antenna_one * (antenna_two.conjugate())
    # antenna_three = antenna_one * (antenna_three.conjugate())
    # for subcarrier in antenna_one:
    #     raw = np.array([complexToLatitude(subcarrier)]) if raw is None else np.append(raw, [complexToLatitude(subcarrier)], axis=0)
    # for subcarrier in antenna_two:
    #     relativePhase_one = np.array([radReverse(subcarrier)]) if relativePhase_one is None else np.append(relativePhase_one, [radReverse(subcarrier)], axis=0)
    # for subcarrier in antenna_three:
    #     relativePhase_two = np.array([radReverse(subcarrier)]) if relativePhase_two is None else np.append(relativePhase_two, [radReverse(subcarrier)], axis=0)
    antenna_one_amp,conjugate_amp, conjugate, relativePhase = None, None, None,None
    tryy, tryyy = None, None
    for wins in range(0, len(antenna_one[0]), TIMEWINDOW):
        part_min, part_max = varianceOperation(antenna_one[:, wins: wins+TIMEWINDOW],
                                               antenna_two[:, wins: wins+TIMEWINDOW], antenna_three[:, wins: wins+TIMEWINDOW])
        alpha = np.mean(part_max)
        belta = alpha * 1000
        tryy = part_max * (part_min.conjugate())
        tryyy = np.array(tryy) if tryyy is None else np.hstack((tryyy,tryy))

        con_mul = (part_max - alpha) * ((part_min + belta).conjugate())
        con_mul = con_mul - np.mean(con_mul)
        conjugate = np.array(con_mul) if conjugate is None else np.hstack((conjugate,con_mul))

    for subcarrier in antenna_one:
        antenna_one_amp = np.array([complexToLatitude(subcarrier)]) \
            if antenna_one_amp is None else np.append(antenna_one_amp, [complexToLatitude(subcarrier)], axis=0)

    for subcarrier in conjugate:
        conjugate_amp = np.array([complexToLatitude(subcarrier)]) \
            if conjugate_amp is None else np.append(conjugate_amp, [complexToLatitude(subcarrier)], axis=0)

    for subcarrier in conjugate:
        relativePhase = np.array([radReverse(subcarrier)]) \
            if relativePhase is None else np.append(relativePhase, [radReverse(subcarrier)], axis=0)
        # relativePhase = np.array([complexToLatitude(subcarrier)]) \
        #     if relativePhase is None else np.append(relativePhase, [complexToLatitude(subcarrier)], axis=0)

    return antenna_one_amp,conjugate_amp, relativePhase, conjugate, tryyy

def readFile(filepath):

    file=read_bf_file.read_file(filepath)
    #print "Length of packets: ", len(file)
    # pair_one_real =pair_one_imag=pair_Two_real=pair_Two_imag=pair_Three_real=pair_Three_imag =np.zeros((30,len(file)))
    timestamp = np.array([])
    startTime = file[0].timestamp_low
    #print "Start timestamp:" + str(startTime)
    antennaPair_raw, antennaPair_One, antennaPair_Two, antennaPair_Three= [], [], [], []
    for item in file:
            timestamp = np.append(timestamp, (item.timestamp_low - startTime) / 1000000.0)
            for eachcsi in range(0, 30):
                ''''
                acquire csi complex value for each antenna pair with shape ( len(file) * 30), i.e., packet number * subcarrier number
                '''
                antennaPair_One.append(item.csi[eachcsi][0][0])
                antennaPair_Two.append(item.csi[eachcsi][0][1])
                antennaPair_Three.append(item.csi[eachcsi][0][2])

    antennaPair_One = np.reshape(antennaPair_One,(len(file), 30)).transpose()
    antennaPair_Two = np.reshape(antennaPair_Two, (len(file), 30)).transpose()
    antennaPair_Three = np.reshape(antennaPair_Three, (len(file), 30)).transpose()

    """
    To get the relative phase between each antenna pair.
    Linear inteplotation operation.
    """
    antenna_one_amp, conjugate_amp,relativePhase,conjugate, tryyy = relativePhaseOperation(antennaPair_One, antennaPair_Two, antennaPair_Three)
    #antenna_one_amp, blocked = linearInterpolation(antenna_one_amp, timestamp)
    #conjugate_amp, blocked = linearInterpolation(conjugate_amp, timestamp)
    #relativePhase, blocked = linearInterpolation(relativePhase, timestamp)

    # TODO: MORE SINGAL OPERATIONS NEEDED TO BE ADDED!
    '''for subcarrier in range(len(amplitude)):
        amplitude[subcarrier] = dwtfilter(amplitude[subcarrier]).butterWorth()
        amplitude[subcarrier] = dwtfilter(amplitude[subcarrier]).filterOperation()'''

    csi_matrix = np.array([antenna_one_amp])
    csi_matrix = np.append(csi_matrix, [conjugate_amp], axis=0)
    csi_matrix = np.append(csi_matrix, [relativePhase], axis=0)
    return csi_matrix
    #return csi_matrix, conjugate, tryyy

if __name__ == '__main__':
    csi= readFile("test.dat")
    #csi, conjugate, tryyy= readFile("test.dat")
    # with open('../data/1/static_csi.pkl', 'wb') as handle:
    #     pickle.dump(csi, handle, -1)
    phase1, value1 = None, None
    phase2, value2 = None, None
    pylab.figure()
    pylab.plot(csi[0][0], 'g-', label='butterworth')
    pylab.pcolormesh(csi[0][0], cmap = cm_  )
    # pylab.plot(csi[1][0], 'g-', label='butterworth')
    # ff = fft(conjugate)
    # for subcarrier in ff:
    #     phase1 = np.array([radReverse(subcarrier)]) \
    #         if phase1 is None else np.append(phase1, [radReverse(subcarrier)], axis=0)
    #     value1 = np.array([complexToLatitude(subcarrier)]) \
    #         if value1 is None else np.append(value1, [complexToLatitude(subcarrier)], axis=0)
    # pylab.plot(phase1[0], 'r--', label='fft_alpha')
    #
    # yy = fft(tryyy)
    # for subcarrier in yy:
    #     phase2 = np.array([radReverse(subcarrier)]) \
    #         if phase2 is None else np.append(phase2, [radReverse(subcarrier)], axis=0)
    #     value2 = np.array([complexToLatitude(subcarrier)]) \
    #         if value2 is None else np.append(value2, [complexToLatitude(subcarrier)], axis=0)
    # pylab.plot(phase2[0], 'b', label='fft_raw')


    # pylab.plot(value[0], 'b--',label='fft_value')

    pylab.legend(loc='best')
    pylab.ylim(0, 50)
    pylab.show()



