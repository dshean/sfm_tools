#! /usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

NEX5 = {'name':'NEX-5', 'weight':338, 'x_mm':23.4, 'y_mm':15.6, 'x_px':4912, 'y_px':3264, 'f':20.0 }

#knots
v = np.arange(64, 193)
#v *= 0.514444
#m/s
#v = np.arange(5, 16) 
#feet
alt_list = np.array([500.0, 1000.0, 1500.0, 2000.0, 3000.0, 4000.0, 5000.0])
#alt_list *= 0.3048
overlap = 0.6

xfov = 2*np.arctan2(NEX5['x_mm'],(2*NEX5['f']))
yfov = 2*np.arctan2(NEX5['y_mm'],(2*NEX5['f']))
diag_mm = np.sqrt(NEX5['x_mm']**2 + NEX5['y_mm']**2)
diag_px = np.sqrt(NEX5['x_px']**2 + NEX5['y_px']**2)
diag_fov = 2*np.arctan2(diag_mm,(2*NEX5['f']))

fov = xfov
cross_fov = yfov

plt.figure(1)
plt.title('Time interval for NEX-5 (20 mm lens, %0.1f deg fov along-track)' % np.degrees(fov))
#plt.xlabel('Ground velocity (m/s)')
plt.xlabel('Groundspeed (kt)')
plt.ylabel('Time interval for 60% overlap (s)')
for alt in alt_list:
    t_int = ((1.0 - overlap) * 2 * (alt*0.3048) * np.tan(fov/2.0))/(v*0.514444)
    plt.figure(1)
    plt.plot(v, t_int, label="%i\' AGL" % (alt))
plt.grid()
plt.legend()
plt.savefig('nex5_time_interval.pdf')

plt.figure(2)
plt.title('Flightline spacing for NEX-5 (20 mm lens, %0.1f deg fov along-track)' % np.degrees(fov))
plt.xlabel('Altitude (ft AGL)')
plt.ylabel('Cross-track spacing for 60% overlap (m)')
spacing = (1.0 - overlap) * 2 * (alt_list*0.3048) * np.tan(cross_fov/2.0)
plt.plot(alt_list, spacing)
plt.grid()
plt.legend()
plt.savefig('nex5_crosstrack_spacing.pdf')

plt.figure(3)
plt.title('GSD for NEX-5 (20 mm lens)')
plt.xlabel('Altitude (ft AGL)')
plt.ylabel('Ground Sample Distance (m)')
gsd = 2*alt_list*diag_fov/diag_px
plt.plot(alt_list, gsd)
plt.grid()
plt.savefig('nex5_gsd.pdf')

plt.show()
