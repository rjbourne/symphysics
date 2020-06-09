#imports
import symphysics
import sympy as sp
import numpy as np
from sympy.physics.mechanics import dynamicsymbols, mlatex

m, g, l = sp.symbols('m, g, l') #constants
a= dynamicsymbols('theta') #coordinates
coords = [a] # put coordinates in list

#lagrangian
L = m*l**2*a.diff()**2/2 + m*g*l*sp.cos(a)

Pendulum = symphysics.SystemL(L, coords)

print(Pendulum.motion)
print(mlatex(Pendulum.motion))
#[Eq(Derivative(omega_theta(t), t), -g*sin(theta(t))/l)]
#\left[ \dot{\omega}_{\theta} = - \frac{g \operatorname{sin}\left(\theta\right)}{l}\right]

#numerical values of constants
consts = [(m, 1), (l, 1), (g, 9.81)]
#initial conditions - 1 radian of rotation with no initial angular velocity
initials = [1, 0]
#times at whch to collect data
times = np.linspace(0,5,5) #every second for 5 seconds
data = Pendulum.ODESolve(initials, times, consts)
print(data)