from sympy.physics.mechanics import dynamicsymbols, mlatex
import matplotlib as mpl
import sympy as sp
from sympy import sin, cos, tan, sqrt
import numpy as np
from symphysics.symsystem import SystemL
from symphysics.sprites import Animate
import math, pathlib

fps = 30
duration = 20
time_factor = 604800*1000 # 1s -> 1000 weeks

######PLANETRY DATA - A.D. 2020-Apr-26 00:00:00.0000 TDB
sun = ["Sol", "xkcd:goldenrod", 1.98850E+30,[-7.113203E+08,1.068784E+09,7.428502E+06], [-1.416122E+01,-5.442970E+00,4.007734E-01]]
planets = []
#planets.append(["Mercury", "xkcd:grey", 3.30200E+23,[5.262736E+10,-1.589400E+09,-5.102762E+09], [-7.002580E+03,5.082645E+04,4.795188E+03]])
#planets.append(["Venus", "xkcd:brownish orange", 4.86850E+24,[-1.063063E+11,-2.002440E+10,5.811538E+09], [6.621502E+03,-3.450367E+04,-8.559004E+02]])
#planets.append(["Earth", "xkcd:aqua", 5.97219E+24,[-1.225762E+11,-8.731841E+10,1.196529E+07], [1.700048E+04,-2.423586E+04,4.668898E-01]])
#planets.append(["Mars", "xkcd:rust", 6.41710E+23,[1.795377E+10,-2.142757E+11,-4.962727E+09], [2.504043E+04,4.170346E+03,-5.267773E+02]])
planets.append(["Jupiter", "xkcd:pale orange", 1.89813E+27, [2.051280E+11,-7.467900E+11,-1.491730E+09],[ 1.243791E+04,4.082812E+03,-2.951946E+02]])
planets.append(["Saturn", "xkcd:sand", 5.68340E+26, [6.505602E+11,-1.349294E+12,-2.437743E+09], [8.163438E+03,4.168246E+03,-3.974701E+02]])
planets.append(["Uranus", "xkcd:pale blue", 8.68130E+25, [2.386399E+12,1.755635E+12,-2.439566E+10], [-4.085764E+03,5.168131E+03,7.195887E+01]])
planets.append(["Neptune", "xkcd:royal blue", 1.02413E+26, [4.384985E+12,-8.977817E+11,-8.256819E+10], [1.054885E+03,5.357181E+03,-1.351425E+02]])
planets.append(["Pluto", "xkcd:purple", 1.30700E+22, [1.992195E+12,-4.682331E+12,-7.522226E+10], [5.136644E+03,9.868726E+02,-1.574974E+03]])

##########EDITABLE VALUES
M, G, t = sp.symbols('M, G, t') #constants
consts = [(G, 6.67408E-11), (M, sun[2])]
coords = []
positions = []
velocities = []
L = 0
for planet in planets:
    m = sp.Symbol("m_" + planet[0])
    x,y,z = dynamicsymbols("x_" + planet[0] + ", y_" + planet[0] + ", z_" + planet[0])
    L += m*(x.diff(t)**2+y.diff(t)**2+z.diff(t)**2)/2 + G*m*M/sqrt(x**2+y**2+z**2)
    consts.append((m, planet[2]))
    coords += [x,y,z]
    positions += planet[3]
    velocities += planet[4]


initials = positions + velocities

System = SystemL(L, coords, diagnostic=True) # create the System object

times = np.linspace(0,duration*time_factor,duration*fps)

data = System.ODESolve(initials, times, consts, diagnostic=True)

def convCentre(a):
    return 0,0,0

def convFactory(i):
    def f(a):
        x = a[3*i]
        y = a[3*i+1]
        z = a[3*i+2]
        return x,y,z
    return f


convs = []
for i in range(len(planets)):
    convs.append(convFactory(i))

animate = Animate(data, times, 3)
animate.limits([-6*10**12,6*10**12], [-6*10**12,6*10**12], [-6*10**12,6*10**12])
particles = []
p_sun = animate.create_particle(data[0], convCentre, color=sun[1], s = 6)
for j in range(len(planets)):
    temp_p = animate.create_particle(data[0], convs[j], color=planets[j][1], s = 2.5)
    particles.append(temp_p)
    animate.create_fade(temp_p, 500)
animate.fig.set_facecolor("k")
for i in animate.ax:
    for j in i:
        j.set_facecolor("k")
        j.w_xaxis.set_pane_color(mpl.colors.to_rgba("k"))
        j.w_yaxis.set_pane_color(mpl.colors.to_rgba("k"))
        j.w_zaxis.set_pane_color(mpl.colors.to_rgba("k"))
        j.xaxis.label.set_color('white')
        j.tick_params(axis='x', colors='white')
        j.yaxis.label.set_color('white')
        j.tick_params(axis='y', colors='white')
        j.zaxis.label.set_color('white')
        j.tick_params(axis='z', colors='white')

filepath = str(pathlib.Path(__file__).parent.absolute()) + "\solar_system_output"
animate.savegif(filepath, fps)
