#IMPORTS
from sympy.physics.mechanics import dynamicsymbols, mlatex
import sympy as sp
import numpy as np
from sympy.calculus.euler import euler_equations
from scipy.integrate import odeint
import copy, pickle, pathlib, dill, functools
from time import perf_counter

t = sp.symbols("t") # time symbol

def _get_functions(function, current = [] ,top_level = False): # recursive
    returns = [] # funtions to return, current is those already found
    sub_functions = list(function.atoms(sp.Function)) # get all functions whch are arguments
    if function.is_Function: # if this is a function not an expression
        sub_functions.remove(function) # remove itself from the list
        if function not in [j[0] for j in current] and not top_level: # if not already recorded and we want to record it (not first argument passed in)
            sub_args = list(function.args) # split it's arguments into symbols and functions
            sub_symbols = []
            sub_funcs = []
            for j in sub_args:
                if j.is_Symbol:
                    sub_symbols.append(j)
                elif j.is_Function:
                    sub_funcs.append(j)
            try: # return the tuple respresenting the conversin of this function into a symbol
                returns.append((function, sp.Symbol(function.name + "_temp"), sub_funcs, sub_symbols))
            except: # if fails as function has no name then function is in built - allowed
                pass
    for i in sub_functions: # combine tuples from all sub_functions
        returns += _get_functions(i, current = returns + current, top_level = False)
    return returns

def _get_func_from_iter(iterable):
    returns = []
    for expr in iterable: # combine functions in all expressions in iterable e.g. list
        returns += _get_functions(expr)
    final = []
    for j in returns: # remove any duplicates
        if j not in final:
            final.append(j)
    return final # return iterable of all functions

class SystemL():
    def __init__(self, L=None, coords=None,constraints=[] ,LU=True, diagnostic=False):
        #init variables - all set to None by default as that is what partially loaded systems have
        ###FUNCTIONS
        self.L = None
        self.coords = None
        #NB constraints only verified if no velocities - if represents distance can find force as lagrang multiplier - see link
        self.constraints = None #https://scholar.harvard.edu/files/david-morin/files/cmchap6.pdf 6.3
        self.motion = None
        self.coords1 = None # [coords] + [coords time derivatives]
        self.motion1 = None
        ###LAMBDAS
        self.motionApply = None
        ###DATA
        self.data = None
        self.times = None
        if L != None and coords != None:
            self.update(L, coords,constraints ,LU, diagnostic)
    
    #function 1 in sequence (must be called by init or individually)
    def update(self, L, coords, constraints=[],LU=True, diagnostic=False): # LU default to false as cannot simplify -  when fixed do time test TODO
        self.start = perf_counter()
        diag_data = []
        if diagnostic:
            print("printing times for system creation in s\ntimes are cumulative")
        self.L = L # Langrangian of system
        self.coords = coords # Coordinate variables, dynamicsymbols - function of "t"
        self.constraints = constraints # store contstraint expressions, which should equal 0
        if LU:
            self._calcLU(diagnostic, diag_data) # 2nd order equations by LU decomposition - better for higher degree of freedoms
        else:
            self._calc()  # 2nd order equations of motion by gaussian elimination
            self._compress() # reduce to a set of 1st order ODEs
        if diagnostic:
            diag_data.append(perf_counter()-self.start)
            print("equations compressed: " + str(diag_data[-1]))
        ###### CHECK NEW VARIABLES DON'T INTERFERE WITH SAVING
        for i in diag_data:
            print(i)
    
    #function 2 in sequence (optional) - can be called from ODEsolve
    def funcLambdify(self, constants):
        if self.motion1 == None or self.coords1 == None:
            raise Exception("missing required variables, have lagrangian and coordinates been provided or loaded from file?")
        self.motionApply = [j.rhs for j in self.motion1][:len(self.coords1)] # get RHS of equations
        self.motionApply = self.subConstants(constants, self.motionApply, differentiate=True)
        self.motionApply = [sp.lambdify(self.coords1, j, "numpy") for j in self.motionApply]
    
    #function 3 in sequence
    def ODESolve(self, initial, times, constants = None, diagnostic=False): # solves ODE over a time period - initials = [coords1 values]
        if self.motionApply == None: # If lambidification not done do it now
            if constants == None: # require coords even if an empty list
                raise Exception("No constants provided, functions not yet lambdified")
            self.funcLambdify(constants)
        self.start = perf_counter() # times total time
        self._final_t = times[-1] # stores final time of times for percentage calculation
        self.start1 = perf_counter()# times pecentage calculation
        self.data = odeint(self._eval, initial, times) # solve ode with _eval function to get derivatives
        if diagnostic:
            print("data created: " + str(perf_counter()-self.start))
        self.times = times # store times that corresponds with data
        return self.data

    def _eval(self, y, t_local):
        if perf_counter() - self.start1 > 10:
            self.start1 = perf_counter()
            print(str(round(100*t_local/self._final_t, 2)) + "%")
        temp = [j(*y) for j in self.motionApply] # evaluate time derivatives at point
        return temp
    
    def _calc(self): # DEPRECIATED
        self.L_multipliers = [sp.Symbol("lambda_" + str(j) + "_mult") for j in range(len(self.constraints))]
        L_prime = self.L
        for j in range(len(self.constraints)):
            L_prime += self.L_multipliers[j]*self.constraints[j]
        eq = euler_equations(L_prime, self.coords, t) # extract euler lagrange equations
        eq += [sp.Eq(j.diff(t,2) ,0) for j in self.constraints]
        eq = [sp.simplify(j) for j in eq]
        eq = [sp.trigsimp(j) for j in eq]
        eq = [sp.factor(j) for j in eq]
        if False in eq:
            raise Exception("Lagrangian appears to be inconsistent")
        results = sp.linsolve(eq, [i.diff(t, 2) for i in self.coords] + self.L_multipliers) # find solutions in terms of second derivatives
        # add validation / ability for non-linear systems
        result = [] # extract result if only one exists
        for num, expr in enumerate(results.args[0]):
            result.append(sp.Eq(([i.diff(t, 2) for i in self.coords] + self.L_multipliers)[num], sp.simplify(expr)))
        self.motion = result
    
    def _calcLU(self, diagnostic, diag_data):
        #create enough lagrange multipliers for constraints
        self.L_multipliers = [sp.Symbol("lambda_" + str(j) + "_mult") for j in range(len(self.constraints))]
        L_prime = self.L # stores lagrangian with constraints
        for j in range(len(self.constraints)):
            L_prime += self.L_multipliers[j]*self.constraints[j]
        eq = euler_equations(L_prime, self.coords, t) # extract euler lagrange equations
        eq += [sp.Eq(j.diff(t,2) ,0) for j in self.constraints] # add constraint equations in second t deriv. form
        if diagnostic:
            diag_data.append(perf_counter()-self.start)
            print("Euler-Lagrange equations calculated: " + str(diag_data[-1]))

        eq = [sp.simplify(j) for j in eq] # simplify equations
        eq = [sp.trigsimp(j) for j in eq]
        eq = [sp.factor(j) for j in eq]
        if diagnostic:
            diag_data.append(perf_counter()-self.start)
            print("Euler-Lagrange equations simplified: " + str(diag_data[-1]))
        if False in eq:
            raise Exception("Lagrangian appears to be inconsistent")

        placeholders = []
        seconds = []
        self.coords1 = copy.copy(self.coords) # set up list of coords
        self.motion1 = []
        for j in self.coords: # convert derivatives into placeholder variables
            new = sp.symbols(j.name + "_temp", real=True)
            new_o = dynamicsymbols("omega_" + j.name)
            self.coords1.append(new_o)
            placeholders += [(j.diff(t,2), new), (j.diff(t), new_o)]
            seconds.append(new)
        eq = self.subConstants(placeholders, eq)
        if diagnostic:
            diag_data.append(perf_counter()-self.start)
            print("derivatives substituted: " + str(diag_data[-1]))
        matrixA, matrixB = sp.linear_eq_to_matrix(eq, seconds + self.L_multipliers) # set up equations as a matrix equation
        if diagnostic:
            diag_data.append(perf_counter()-self.start)
            print("Matrix equation created: " + str(diag_data[-1]))
        solution = matrixA.LUsolve(matrixB) # solve matrix equation
        if diagnostic:
            diag_data.append(perf_counter()-self.start)
            print("matrix equation solved: " + str(diag_data[-1]))
        # add validation / ability for non-linear systems
        result = []
        for num, expr in enumerate(solution[:]): # recreate equations
            result.append(sp.Eq(([self.coords1[len(self.coords)+j].diff(t) for j in range(len(self.coords))] + self.L_multipliers)[num], expr)) # simplify(expr) breaks for double conical??? TODO
        self.motion = result
        self.motion1 = [sp.Eq(self.coords[j].diff(t), self.coords1[len(self.coords)+j]) for j in range(len(self.coords))] + self.motion
        if diagnostic:
            diag_data.append(perf_counter()-self.start)
            print("results appended and derivatives reapplied: " + str(diag_data[-1]))
    
    def _compress(self): # DEPRECIATED
        self.coords1 = copy.copy(self.coords) # set up list of coords
        self.motion1 = [] # set up blank list of good equations
        for q in self.coords: # for all coords
            qdot = dynamicsymbols("omega_" + q.name) # create a first deriv variable
            self.coords1.append(qdot) # add it to the list of coords1
            self.motion1.append(sp.Eq(q.diff(t), qdot)) # add the correspondingn ODE
        self.motion1 += self.motion # add original equation
        for i in range(len(self.coords)): # replace all derivatives/second derivatives with new variables/first derivatives
            for j in range(len(self.coords), len(self.motion1)): # only in original eq - not omega = xdot
                self.motion1[j] = self.motion1[j].subs(self.coords1[i].diff(t), self.coords1[i+len(self.coords)])
                self.motion1[j] = self.motion1[j].subs(self.coords1[i].diff(t, 2), self.coords1[i+len(self.coords)].diff(t))
    
    
    @staticmethod
    def subConstants(constants, expressions, differentiate = False): # substitute values in a list of expressions
        expressions = [j.subs(constants) for j in expressions]
        if differentiate: 
            expressions = [j.doit() for j in expressions]# doit evaluates derivaitves if consts are functions being subbed in
        return expressions
    
    @staticmethod
    def saveSystem(sys, filename, functions=True, lambdas=True, datas=True): # saves system
        stores = {} # dictionary stores data
        stores["version"] = 1 # version number of lag file - to ensure program backwards compatible
        if functions: # if stroing functions
            funcColl = [sys.coords, sys.coords1, sys.motion, sys.motion1, sys.constraints, [sys.L]]
            funcColl = [copy.copy(j) for j in funcColl] # make copy so as not to disturb original system
            funcColl, convs = SystemL.convertFunctions(funcColl) # convert functions to symbols
            stores["functions"] = funcColl # store functions
            stores["fileConversions"] = convs # store data to reconstruct functions from symbols
        if lambdas and sys.motionApply != None: # if want to store lambda functions and they exist
            stores["lambdas"] = sys.motionApply
        if datas and isinstance(sys.data, np.ndarray): # if want to store data and it exists
            stores["data"] = sys.data
            stores["times"] = sys.times
        base_path = pathlib.Path(__file__).parent # get main path of workspace
        filename += '.lag'
        file_path = str((base_path / "../saved systems/"/filename).resolve())
        outfile = open(file_path, 'wb')
        dill.settings["recurse"] = True
        dill.dump(stores, outfile) # dill the system store into a .lag file
        outfile.close()
    
    @staticmethod
    def loadSystem(filename):
        base_path = pathlib.Path(__file__).parent # get main path of workspace
        filename += '.lag'
        file_path = str((base_path / "../saved systems/"/filename).resolve())
        infile = open(file_path, 'rb')
        dill.settings["recurse"] = True
        stores = dill.load(infile) # un-dill the system store
        infile.close()
        sys = SystemL() # create a blank system
        if stores["version"] > 1: # check program can handle version number
            raise Exception("file version number exceeds maximum - please update your symlagrange")
        if "functions" in stores: # if the function is stored
            funcs = SystemL.loadFunctions(stores["functions"], stores["fileConversions"]) # unconvert functions
            sys.coords = funcs[0] # load correct functions into system
            sys.coords1 = funcs[1]
            sys.motion = funcs[2]
            sys.motion1 = funcs[3]
            sys.constraints = funcs[4]
            sys.L = funcs[5][0] # sys.L packaged as [sys.L] for function conversions
        if "lambdas" in stores: # if ambda functions sotred retrieve them
            sys.motionApply = stores["lambdas"]
        if "data" in stores: # if data stored retrieve them and corresponding times
            sys.data = stores["data"]
            sys.times = stores["times"]
        return sys # return the system

    
    @staticmethod
    def convertFunctions(funcs): # currently only works if no functions which aren't coords
        # in line below list of lists compressed into a list
        functions = _get_func_from_iter(functools.reduce(list.__add__, funcs)) # get a list of tuples of functions and their replacments and function and symbol arguments
        conversions = [[j[0], j[1]] for j in functions] # get function and replacement symbols
        fileConversions = [[j[1], SystemL.subConstants(conversions, j[2]), j[3]] for j in functions] # save function symbols and their function and symbol arguments
        for i in range(len(conversions)): # convert all functions to symbols - done 1 at a time so functions changed in other functions are still recognised
            const = [conversions[i]]
            funcs = [SystemL.subConstants(const, j) for j in funcs]
            for j in range(len(conversions)):
                conversions[j] = SystemL.subConstants(const, conversions[j]) # change conversions so function arguments match those found, see above
        return funcs, fileConversions
    
    @staticmethod
    def loadFunctions(funcs, fileConversions):
        conversions = [] # list function conversions from symbols
        while len(fileConversions) > 0: #while functions still to be converted from symbols
            loop_conversions = [] # stores conversions within this loop
            removes = [] # items to be removed after for loop
            for j in fileConversions: # for each remaining function to be converted
                if len(j[1]) == 0: # check all arguments of function whichare also functions have already been restored j[1] is unrestored function symbols
                    temp = (j[0], sp.Function(j[0].name[:len(j[0].name)-5])(*j[2]))
                    conversions.append(temp) # if so add to conversions the restored functin and arguments
                    loop_conversions.append(temp)
                    removes.append(j)
            for j in removes: # rmove resotred functions from list
                fileConversions.remove(j)
            removes = []
            for j in range(len(fileConversions)): # convert all functions in list which have just been restored and are arguments to another function
                sys.fileConversions[j][1] = SystemL.subConstants(loop_conversions, fileConversions[j][1])
                for k in fileConversions[j][1]: # all restored argument functions are moved from j[1] to j[2]
                    if k.is_Function:
                        fileConversions[j][2].append(k)
                        removes.append(k)
                for k in removes:
                    fileConversions[j][1].remove(k)
        funcs = [SystemL.subConstants(conversions, j) for j in funcs] # return a list of converted functions
        return funcs
