#imports
import symphysics
import sympy as sp
import numpy as np
from sympy.physics.mechanics import dynamicsymbols, mlatex
import math
import pathlib

m, g, l = sp.symbols('m, g, l') #constants
a= dynamicsymbols('theta') #coordinates
coords = [a] # put coordinates in list

#lagrangian
L = m*l**2*a.diff()**2/2 + m*g*l*sp.cos(a)

Pendulum = symphysics.SystemL(L, coords)

#numerical values of constants
consts = [(m, 1), (l, 1), (g, 9.81)]
#initial conditions - 1 radian of rotation with no initial angular velocity
initials = [1, 0]
#times at whch to collect data
times = np.linspace(0,5,100) #20 fps for 5 seconds
data = Pendulum.ODESolve(initials, times, consts)


def pivotConv(a):
    return [0,0]

def bobConv(a):
    return [consts[1][1]*math.sin(a[0]), -consts[1][1]*math.cos(a[0])]

animator = symphysics.Animate(data, times, d=2)
animator.limits([-1.2, 1.2], [-1.2, 0.2])
pivot = animator.create_particle(data[0], pivotConv, color="blue")
bob = animator.create_particle(data[0], bobConv, color="red")
animator.create_rod(pivot, bob)
animator.create_fade(bob, 20)
filepath = str(pathlib.Path(__file__).parent.absolute()) + "\pendulum_animated_output"
animator.savegif(filepath, fps=20)