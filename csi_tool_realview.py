# coding: utf-8
import modify_extract
#import extract
import udp
from plot import  Display
import struct


ret = []  # to store csi
s = udp.udp_init(5563)  # create a udp handle
f = Display() #initialize the realview procedure
f.display()

try:
        while True:  # a loop to receive the data
            csiInfo = []
            data, addr = udp.recv(s)  # receive a udp socket
            for i in range(1,len(data)):
                csiInfo.append(struct.unpack("!B", data[i])[0]) # decode csi from udp

            CSI_matrix = modify_extract.readFile(csiInfo)
            f.push(CSI_matrix)
            # print CSI_matrix
except KeyboardInterrupt:
        udp.close(s)  # close udp
        f.stop()           # close view


