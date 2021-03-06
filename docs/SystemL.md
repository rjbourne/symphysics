*last updated 09/06/2020*

## SystemL
The only type of system currently implemented is SystemL, which is used to construct a system from a classical lagrangian. The development of a SystemL object is divided into three stages.

1. Providing the generalised coordinates and lagrangian for the system - then calculating the equations of motion
2. Creation of lambda functions of the equations of motion for numpy to use
3. Creation of a solution to the equations of motion given starting conditions and a time frame

IMPORTANT: sympy functions and constants ending `_temp` and `_mult` are reserved - do not pass them into SystemL methods

### Methods

#### \_\_init__(self,  `L`=None, `coords`=None,`constraints`=[] ,`LU`=True, `diagnostic`=False):

If no additional arguments are given a blank SystemL object is created. Alternatively a Lagrangian and coordinate system may be provided as `L` and `coords`. In this case the first stage of development is completed and the equations of motion will be calulated by calling the `update()` method (below)

`L`: The lagrangian of the system given as a sympy expression in terms of the coordinates (below) and sympy symbols which are treated as constants

`coords`: The generalised coordinates of the system provided as a list of sympy dynamicsymbols or functions of the sympy symbol `t`

`constraints`: A list of constraints in terms of the coordinates of the system (velocity constraints not supported). Each constraint should be a sympy expression that always equal 0

`LU`: When True by default a matrix method is used to solve the equations of motion, True by default. Provided for backwards compatibility - however `LU`=False may cause extremely slow calculations of the equations of motion and is no longer supported.
WARNING: DEPRECIATED - MAY BE REMOVED

`diagnostic`: When set to True the timing information will be provided for the calculation of the equations of motion

`returns`: A reference to the SystemL object

#### update(self, `L`, `coords`, `constraints`=[],`LU`=True, `diagnostic`=False):

This method carries out the first stage of development - by calculating the equations of motion from the lagrangian. It is automatically called by `__init__()` if a lagrangian and coords are provided.

`L`: The lagrangian of the system given as a sympy expression in terms of the coordinates (below) and sympy symbols which are treated as constants

`coords`: The generalised coordinates of the system provided as a list of sympy dynamicsymbols or functions of the sympy symbol `t`

`constraints`: A list of constraints in terms of the coordinates of the system (velocity constraints not supported). Each constraint should be a sympy expression that always equal 0

`LU`: When True by default a matrix method is used to solve the equations of motion, True by default. Provided for backwards compatibility - however `LU`=False may cause extremely slow calculations of the equations of motion and is no longer supported.
WARNING: DEPRECIATED - MAY BE REMOVED

`diagnostic`: When set to True the timing information will be provided for the calculation of the equations of motion

#### funcLambdify(self, `constants`):

This method carries out the second stage of development by converting the equations of motion into lambda functions. It is automatically called by `ODESolve()` (below) if constants are provided.

`constants`: A list of 2-tuples containing all constants and their numerical values. If no constants are in the equations of motion, an empty list should be passed

#### ODESolve(self, `initial`, `times`, `constants` = None, `diagnostic`=False):

This method calculates the solution to the equations of motion for given initial conditions and an iterable of times at which to provide coordinates. This method implements scipy's `odeint()` function

`initial`: A list of the initial values of the coordinates followed by the initial values of their time derivatives. These must be provided in the same order as the original list of coords.
e.g. if the original coords are provided as `[x, y]` where x and y are sympy functions of t, the initial should be a list `[x0, y0, vx0, vy0]` where x0 and y0 are numerical initial positions and vx0 and vy0 are numerical initial velocities

`times`: A list or 1D numpy array of the times at which data for the coordinates should be extracted

`constants`:  A list of 2-tuples containing all constants and their numerical values. If no constants are in the equations of motion, an empty list should be passed. This is passed into `funcLambdify()` (above)

`diagnostic`: Returns the total calculation time if set to True

`returns`: A 2D array of the coordinate values at times corresponding to the array of times given

#### saveSystem(`sys`, `filename`, `functions`=False, `lambdas`=True, `datas`=True):

A STATIC method which allows a system to be saved into a .lag file

`sys`: A reference to the SystemL object to be saved

`filename`: A string giving the filepath and filename, excluding the extension.

`functions`: Set to True to save the sympy expressions for the equations of motion - note that due to the complexity involved in saving sympy Function objects this may take considerable time for larger systems - it is recommended that unless required only the lambda versions of the equations of motion are saved

`lambdas`: Set to True to save the lambda functions for the equations of motion

`datas` Set to True to save the most recent data that has been calculated

#### loadSystem(`filename`):

A STATIC method to load up a saved SystemL object from a .lag file

`filename`: A string giving the filepath and filename, excluding the extension.

`returns`: A reference to the SystemL object that has been created from the file

### Examples

Examples files can be found in the examples folder in the github repository

[Basic Pendulum](https://github.com/rjbourne/symphysics/wiki/Basic-Pendulum)