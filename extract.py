import read_bf_file
import  numpy as np
# import pylab

def radReverse(subcarrier):
    return map(lambda x: float("%.2f" % np.arctan(x.imag / x.real)), subcarrier)
def complexToLatitude(subcarrier):
    return  map(lambda x: float("%.2f" % abs(x)), subcarrier)
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
    amplitude, phase = None, None

    for subcarrier in antenna_one:
        amplitude = np.array([complexToLatitude(subcarrier)]) \
            if amplitude is None else np.append(amplitude, [complexToLatitude(subcarrier)], axis=0)
    for subcarrier in antenna_two:
        phase = np.array([radReverse(subcarrier)]) \
            if phase is None else np.append(phase, [radReverse(subcarrier)], axis=0)

    return amplitude, phase

def readFile(filepath):

    file=read_bf_file.read_file(filepath)
    print len(file)
    # pair_one_real =pair_one_imag=pair_Two_real=pair_Two_imag=pair_Three_real=pair_Three_imag =np.zeros((30,len(file)))
    antennaPair_raw, antennaPair_One, antennaPair_Two, antennaPair_Three= [], [], [], []
    for item in file:
        for eachcsi in range(0, 30):
            antennaPair_One.append(item.csi[eachcsi][0][0])
            antennaPair_Two.append(item.csi[eachcsi][0][1])
            antennaPair_Three.append(item.csi[eachcsi][0][2])

    antennaPair_One = np.reshape(antennaPair_One,(1, 30)).transpose()
    antennaPair_Two = np.reshape(antennaPair_Two, (1, 30)).transpose()
    antennaPair_Three = np.reshape(antennaPair_Three, (1, 30)).transpose()

    amplitude, phase= relativePhaseOperation(antennaPair_One, antennaPair_Two, antennaPair_Three)

    csi_matrix = np.array([amplitude])
    csi_matrix = np.append(csi_matrix, [phase], axis=0)

    return csi_matrix

if __name__ == '__main__':
    csi,= readFile("/home/han/data/1/csi1.dat")
    # with open('../data/1/static_csi.pkl', 'wb') as handle:
    #     pickle.dump(csi, handle, -1)
    phase1, value1 = None, None
    phase2, value2 = None, None
    pylab.figure()
    pylab.plot(csi[0][0], 'g-', label='butterworth')

    pylab.legend(loc='best')
    pylab.ylim(0, 50)
    pylab.show()



