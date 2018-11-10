#! /usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

def conv2bh(conv):
    return 2*np.tan(np.radians(conv/2.))

def bh2conv(bh):
    return 2*np.degrees(np.tanh(bh/2.0))

bh_range = np.arange(0.5, 2.0, 0.25)
hb_range = 1.0/bh_range
conv_range = bh2conv(bh_range)
iconv_range = np.arange(10, 70, 10)
ibh_range = conv2bh(iconv_range)

b_error = np.array([0.01, 0.1, 1.0, 10.0, 100.0])
#h_error = b_error * hb_range

plt.figure()
plt.plot(bh_range, conv_range)
plt.xlabel("Base to height ratio")
plt.ylabel("Convergence angle (deg)")
plt.figure()
plt.plot(iconv_range, ibh_range)
plt.ylabel("Base to height ratio")
plt.xlabel("Convergence angle (deg)")
plt.figure()
plt.ylabel("Vertical error (m)")
plt.xlabel("Horizontal offset (m)")
for bh in bh_range:
    plt.plot(b_error, b_error/bh, label='B/H:%0.2f (%0.1f deg)' % (bh, bh2conv(bh)))
plt.axes().set_aspect('equal')
plt.legend()
plt.show()
