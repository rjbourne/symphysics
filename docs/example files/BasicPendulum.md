## Basic Pendulum

---

source code: [pendulum.py](https://github.com/rjbourne/symphysics/blob/master/examples/pendulum.py)

---

In this example we will use SystemL to create a basic pendulum

First we make the necessary imports
```py
import symphysics
import sympy as sp
import numpy as np
from sympy.physics.mechanics import dynamicsymbols, mlatex
```
Next we create the system, here we will use the coordinate giving angle from equilibrium
```py
m, g, l = sp.symbols('m, g, l') #constants
a= dynamicsymbols('theta') #coordinates
coords = [a] # put coordinates in list
L = m*l**2*a.diff()**2/2 + m*g*l*sp.cos(a)

Pendulum = symphysics.SystemL(L, coords)
```
We can now print out the equations of motion by accessing the `motion` attribute
```py
print(Pendulum.motion)
print(mlatex(Pendulum.motion))
```
which outputs
```py
>>>[Eq(Derivative(omega_theta(t), t), -g*sin(theta(t))/l)]
>>>\left[ \dot{\omega}_{\theta} = - \frac{g \operatorname{sin}\left(\theta\right)}{l}\right]
```
The first of these is the sympy object, the second is a latex respresentation of it:

![equation](https://latex.codecogs.com/svg.latex?%5Cleft%5B%20%5Cdot%7B%5Comega%7D_%7B%5Ctheta%7D%20%3D%20-%20%5Cfrac%7Bg%20%5Coperatorname%7Bsin%7D%5Cleft%28%5Ctheta%5Cright%29%7D%7Bl%7D%5Cright%5D)

Note the use of omega_theta for the second derivative of theta with respect to time - SystemL creates all equations of motion as first order ODEs. You can access the full list with the attribute `motion1`, whch will also give us the trivial ODE:

![equation](https://latex.codecogs.com/svg.latex?%7B%5Comega%7D_%7B%5Ctheta%7D%20%3D%20%5Cdot%5Ctheta)

Finally we can collect data for the pendulum by setting some constants and initial conditions, as well as a range of times:
```py
#numerical values of constants
consts = [(m, 1), (l, 1), (g, 9.81)]
#initial conditions - 1 radian of rotation with no initial angular velocity
initials = [1, 0]
#times at whch to collect data
times = np.linspace(0,5,5) #every second for 5 seconds
data = Pendulum.ODESolve(initials, times, consts)
print(data)
```

which outputs
```py
[[ 1.          0.        ]
 [-0.86762951  1.44439542]
 [ 0.4971966  -2.57754542]
 [ 0.01954696  3.00258549]
 [-0.53034726 -2.51477589]]
```