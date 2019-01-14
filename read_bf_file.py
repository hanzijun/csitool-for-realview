import numpy as np
import os
import sys
import struct
# from .csi import WifiCsi


class WifiCsi:

    def __init__(self, args, csi):
        self.timestamp_low = args[0]
        self.bfee_count = args[1]
        self.Nrx = args[2]
        self.Ntx = args[3]
        self.rssi_a = args[4]
        self.rssi_b = args[5]
        self.rssi_c = args[6]
        self.noise = args[7]
        self.agc = args[8]
        self.perm = args[9]
        self.rate = args[10]
        self.csi = csi
        pass

def get_bit_num(in_num, data_length):
    max_value = (1 << data_length - 1) - 1
    if not -max_value-1 <= in_num <= max_value:
        out_num = (in_num + (max_value + 1)) % (2 * (max_value + 1)) - max_value - 1
    else:
        out_num = in_num
    return out_num
    pass

def read_bfee(in_bytes):
    timestamp_low = in_bytes[0] + (in_bytes[1] << 8) + \
        (in_bytes[2] << 16) + (in_bytes[3] << 24)
    bfee_count = in_bytes[4] + (in_bytes[5] << 8)
    Nrx = in_bytes[8]
    Ntx = in_bytes[9]
    rssi_a = in_bytes[10]
    rssi_b = in_bytes[11]
    rssi_c = in_bytes[12]
    noise = get_bit_num(in_bytes[13],8)
    agc = in_bytes[14]
    antenna_sel = in_bytes[15]
    length = in_bytes[16] + (in_bytes[17] << 8)
    fake_rate_n_flags = in_bytes[18] + (in_bytes[19] << 8)
    calc_len = (30 * (Nrx * Ntx * 8 * 2 + 3) + 7) / 8
    payload = in_bytes[20:]
    # if(length != calc_len)

    perm_size = (3)
    perm = np.ndarray(perm_size, dtype=int)


    if Nrx == 3 :
        perm[0] = ((antenna_sel) & 0x3) + 1
        perm[1] = ((antenna_sel >> 2) & 0x3) + 1
        perm[2] = ((antenna_sel >> 4) & 0x3) + 1

    elif Nrx ==2 :
        perm[0] = 2
        perm[1] = 1
        perm[2] = 3

    index = 0
    Nrx_mat = 3
    csi_size = (30, Ntx, Nrx_mat)
    row_csi = np.ndarray(csi_size, dtype=complex)
    perm_csi = np.ndarray(csi_size, dtype=complex)
    try:
        for i in range(30):
            index += 3
            remainder = index % 8
            for j in range(Nrx):
                for k in range(Ntx):
                    pr = get_bit_num((payload[index // 8] >> remainder),8) | get_bit_num((payload[index // 8+1] << (8-remainder)),8)
                    pi = get_bit_num((payload[(index // 8)+1] >> remainder),8) | get_bit_num((payload[(index // 8)+2] << (8-remainder)),8)
                    if Nrx == 3:
                        perm_csi[i][k][perm[j] - 1] = complex(pr, pi)
                    elif Nrx == 2:
                        perm_csi[i][k][perm[j]] = complex(pr, pi)
                    index += 16
                    pass
                pass
            pass
        pass
    except:
        pass

    args = [timestamp_low, bfee_count, Nrx, Ntx, rssi_a,
            rssi_b, rssi_c, noise, agc, perm, fake_rate_n_flags]

    temp_wifi_csi = WifiCsi(args, perm_csi)
    return temp_wifi_csi


def read_file(file_path):
    csi_data = []
    csi_data.append(read_bfee(file_path))

    return csi_data

