import matplotlib.pylab as plt
from collections import deque
from filter import Filter
import numpy as np
import copy
import time
import threading
import pywt

TIMEWINDOW = 1800
SLIDEWINDOW = TIMEWINDOW / 2

class Display:

    def __init__(self, REFRESH_INTERVAL=0.001):
        self.count = 0
        self.t = deque()
        self.amp =  deque()
        self.conj_amp=deque()
        self.pha = deque()
        self.amp_filter = None
        self.pha_conj = deque()
        self.end = False
        self.threads = []
        self.interval = REFRESH_INTERVAL
        pass

    def push(self, data):

        if self.count > TIMEWINDOW -1:
            self.t.popleft()
            self.amp.popleft()
            self.conj_amp.popleft()
            self.pha.popleft()

        self.t.append(self.count)
        self.amp.append(data[0][0])
        self.conj_amp.append(data[1][0])
        self.pha.append(data[2][0])

        self.count += 1

        if self.count % SLIDEWINDOW == 0:
            if self.amp_filter is None:
                self.amp_filter = list(copy.deepcopy(self.amp))
            elif len(self.amp_filter) == SLIDEWINDOW:
                self.amp_filter.extend(list(self.amp)[-SLIDEWINDOW:])
            else:
                 self.amp_filter = self.amp_filter[-SLIDEWINDOW:] + list(copy.deepcopy(self.amp))[-SLIDEWINDOW:]

    def _plot(self):
        fig, ax = plt.subplots(nrows=2, ncols=2, sharex=True)
        amplitude = ax[0][0]
        # phase = ax[0][1]
        slide = ax[0][1]
        conj_amplitude=ax[1][0]
        time_fre = ax[1][1]
        while not self.end:

            t = copy.deepcopy(self.t)
            amp = copy.deepcopy(self.amp)
            conj_amp=copy.deepcopy(self.conj_amp)
            pha = copy.deepcopy(self.pha)
            # if self.count <= TIMEWINDOW + SLIDEWINDOW:
            flt = copy.deepcopy(self.amp_filter)
            # if flt and len(flt) == TIMEWINDOW:
            #     flt = Filter(flt).butterWorth()
            # else:


            if len(t) == 0:
                time.sleep(self.interval)
                continue
            if len(t) != len(amp) or len(t) != len(pha):
                continue

            max_t = t[-1] + 100
            min_t = max_t - TIMEWINDOW if max_t - TIMEWINDOW > 0 else 0

            amplitude.cla()
            amplitude.set_title("amplitude")
            amplitude.set_xlabel("packet / per")
            amplitude.set_ylim(0, 50)
            amplitude.set_xlim(min_t, max_t)
            amplitude.grid()
            amplitude.plot(t,np.array(amp))
            # amplitude.legend(loc='best')

            # phase.cla()
            # phase.set_title("phase")
            # phase.set_xlabel("packet / per")
            # phase.set_ylim(-2, 2)
            # phase.set_xlim(min_t, max_t)
            # phase.grid()
            # phase.plot(t, np.array(pha))

            slide.cla()
            slide.set_title("slide")
            slide.set_xlabel("packet / per")
            slide.set_ylim(0, 50)
            slide.set_xlim(min_t, max_t)
            slide.grid()

            time_fre.set_title("time_fre")
            time_fre.set_xlabel("time(s)")
            time_fre.set_ylim(0, 25)

            if flt and len(flt) == TIMEWINDOW:
                slide.plot(t,np.array(flt))
                sig=[]
                for i in range(len(flt)):      #to 1 dimension
                    sig.append(flt[i][0])
                #print sig
                fs = 50
                totalscale = 256
                #t = np.arange(0, 1, 1.0 / fs)
                #sig = np.sin(2 * math.pi * f1 * t) + np.sin(2 * math.pi * f2 * t)
                wcf = pywt.central_frequency('morl')
                scale = np.arange(1, totalscale + 1, 1)
                cparam = 2 * wcf * totalscale
                scale = cparam / scale
                frequencies = pywt.scale2frequency('morl', scale)
                frequencies = frequencies * fs
                cwtmatr, freqs = pywt.cwt(sig, scale, 'morl')
                time_fre.pcolormesh(t, frequencies, abs(cwtmatr), vmax=abs(cwtmatr).max(), vmin=-abs(cwtmatr).max())

                #time_fre.colorbar()
                #time_fre.show()

            conj_amplitude.cla()
            conj_amplitude.set_title("conj_amplitude")
            conj_amplitude.set_xlabel("packet / per")
            #conj_amplitude.set_ylim(0, 100)
            conj_amplitude.set_xlim(min_t, max_t)
            conj_amplitude.grid()
            conj_amplitude.plot(t, np.array(conj_amp))

            plt.pause(self.interval)

    def stop(self):
            for t in self.threads:
                t.join()
    print('stop realview****')

    def display(self):
        t1 = threading.Thread(target=self._plot)
        self.threads.append(t1)
        for t in self.threads:
            # t.setDaemon(True)
            t.start()
    print('display starting...')

if __name__ == '__main__':
    f = Display()
    f.display()
    while True:
        data = [[[10]],[[10]],[[0.2]]]
        f.push(data)
        time.sleep(0.1)

