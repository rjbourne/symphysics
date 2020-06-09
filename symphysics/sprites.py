import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
from matplotlib.collections import LineCollection, PolyCollection
import numpy as np
from pathlib import Path

class Particle():
    def __init__ (self, a, conv, color, s, ax, d):
        self.d = d
        self.color = color # color
        self.conversion = conv # conversion function from general coords to x,y(,z)
        self.position = np.array([[j] for j in self.conversion(a)]) # get position into a numpy array - each coordinate as a list - required in 3d
        if d == 2: # if 2d arrange particles at front: plot initial position
            self.pt, = ax.plot(*self.position,mfc=self.color, mec=self.color, marker='o', markersize=s , zorder=3)
        else:
            self.pt, = ax.plot(*self.position,mfc=self.color, mec=self.color, marker='o', markersize=s)
    
    def update(self,a): # update particle with general coordinates/velocities in 'a'
        self.position = np.array([[j] for j in self.conversion(a)]) # update position
        self.pt.set_data(*self.position[0:2])
        if self.d == 3: # if 3d also update z position
            self.pt.set_3d_properties(self.position[2])


class Rod():
    def __init__(self,p1,p2,color,ax, d):
        self.d = d
        self.color = color # color
        self.start = p1 # particles at either end of rod
        self.end = p2
        self.data = np.concatenate((self.start.position, self.end.position), axis=1) #sotre end points of rod as coords in a line
        if self.d == 2: # if 2d set position behind particles: set initial positions
            self.ln, = ax.plot(*np.concatenate((self.start.position, self.end.position), axis=1),color=self.color, zorder=2) 
        else:
            self.ln, = ax.plot(*np.concatenate((self.start.position, self.end.position), axis=1),color=self.color)

    def update(self): # update 
        self.data = np.concatenate((self.start.position, self.end.position), axis=1) # update position
        self.ln.set_data(*self.data[0:2])
        if self.d == 3: # if 3d also update z positions
            self.ln.set_3d_properties(self.data[2])

class Spring(Rod): # spring inherits rod
    def __init__(self, p1, p2, lamb, nat_l, color, ax, d):
        self.d = d
        self.lamb = lamb # store lambda and natural length
        self.nat_l = nat_l
        super().__init__(p1, p2, color, ax, d)
    
    def update(self):
        super().update(self.d)
        length = float(np.linalg.norm(self.start.position-self.end.position)) # get length of spring
        coloring = (length-self.nat_l)/self.nat_l # ratio of extension to length
        self.new_color = mpl.colors.hsv_to_rgb((0,1,1-min(1,abs(coloring)))) # get color based on coloring
        self.ln.set_color(self.new_color) # set color


class Trace():
    def __init__(self,p,length,color,ax, d):
        self.d = d
        self.color = color # set colour of trace, defaults to colour of the particle
        self.length = length # how many frames you want the trace to last
        self.particle = p # particle you are tracing
        self.traceCoords = self.particle.position # coordinates of the particle
        if d == 2:
            self.ln, = ax.plot(*self.traceCoords, color = color, zorder=1)
        else:
            self.ln, = ax.plot(*self.traceCoords, color = color)

    
    def update(self):
        if np.size(self.traceCoords, 1) > self.length:
            self.traceCoords = np.delete(self.traceCoords, [0], 1) # delete the oldest part of the trace once its too old
        self.traceCoords = np.concatenate((self.traceCoords, self.particle.position), axis=1)
        self.ln.set_data(*self.traceCoords[0:2])
        if self.d == 3:
            self.ln.set_3d_properties(self.traceCoords[2])


class Fade(Trace): 
    def __init__(self,p,length,color,ax, d):
        self.d = d
        self.color = color # set colour of trace, defaults to colour of the particle
        self.length = length # how many frames you want the trace to last
        self.particle = p # particle you are tracing
        self.ax = ax
        self.rgb = mpl.colors.to_rgb(self.color)
        self.rgba = np.array([self.rgb[0],self.rgb[1],self.rgb[2],0.0])
        for i in range(0,self.length):
            self.rgba = np.concatenate((self.rgba,np.array([self.rgb[0],self.rgb[1],self.rgb[2],i/self.length])))
        self.rgba = np.reshape(self.rgba,(-1,4))
        self.cmp = mpl.colors.ListedColormap(self.rgba)
        self.traceCoords = np.swapaxes([self.particle.position],1,2) # coordinates of the particle
        self.traceCoords = np.concatenate((self.traceCoords, self.traceCoords),axis= 1)
        if d == 2:
            lnColl = LineCollection(self.traceCoords, color=self.rgba)
        else:
            lnColl = Line3DCollection(self.traceCoords, color=self.rgba)
        self.ln = ax.add_collection(lnColl)

    
    def update(self):
        if np.size(self.traceCoords, 0) > self.length:
            self.traceCoords = np.delete(self.traceCoords, [0], 0) # delete the oldest part of the trace once its too old
        new_segment = np.concatenate(([[self.traceCoords[-1, 1, :]]], np.swapaxes([self.particle.position], 1, 2)), axis=1)
        self.traceCoords = np.concatenate((self.traceCoords, new_segment), axis=0)
        self.ln.remove()
        if self.d == 2:
            lnColl = LineCollection(self.traceCoords, color=self.rgba)
        else:
            lnColl = Line3DCollection(self.traceCoords, color=self.rgba)
        self.ln = self.ax.add_collection(lnColl)


class Polygon():
    def __init__(self,ps,color,alpha,ax,d):
        self.d = d
        self.color = color
        self.alpha = alpha
        self.ps = ps
        self.ax = ax
        self.data = ps[0].position
        for i in self.ps[1:]:
            self.data = np.concatenate((self.data, i.position),axis=1)
        self.data = self.data.T
        if d == 2:
            self.patch = mpl.patches.Polygon(self.data,closed=True, fc=self.color, ec=self.color,alpha=self.alpha)
            ax.add_patch(self.patch)
        else:
            poly = Poly3DCollection(self.data)
            poly.set_alpha(self.alpha)
            poly.set_facecolor(self.color)
            poly.set_edgecolor(self.color)
            self.patch = self.ax.add_collection(poly)


    def update(self):
        self.data = self.ps[0].position
        for i in self.ps[1:]:
            self.data = np.concatenate((self.data, i.position),axis=1)
        self.data = self.data.T
        if self.d == 2:
            self.patch.set_xy(self.data)
        else:
            self.patch.remove()
            poly = Poly3DCollection(self.data)
            poly.set_alpha(self.alpha)
            poly.set_facecolor(self.color)
            poly.set_edgecolor(self.color)
            self.patch = self.ax.add_collection(poly)

            
class Polyhedra(): # TODO
    def __init__(self,ps,color,alpha,ax,d):
        if d != 2:
            raise Exception('Polyhedra only exist in 3D')
        self.color = color
        self.alpha = alpha
        self.ps = ps
        self.ax = ax



class Animate():
    def __init__(self,data,t,d=2, rows=1, columns=1):
        self.dimension = d # 2d or 3d render
        if isinstance(d, int):
            self.dimension = [[d for j in range(columns)] for i in range(rows)]
        self.rows = rows
        self.columns = columns
        self.fig = plt.figure(figsize=(6.4*columns/max(columns, rows), 4.8*rows/max(columns, rows)))
        self.fig.set_tight_layout(True)
        self.ax = [[0 for j in range(columns)] for i in range(rows)]
        for r in range(rows):
            for c in range(columns):
                if self.dimension[r][c] == 3:
                    self.ax[r][c] = self.fig.add_subplot(rows, columns, c+1 + (r)*(columns),projection = '3d') # get 3d plot
                    self.ax[r][c].set_xlabel("x") # set up axes
                    self.ax[r][c].set_ylabel("y")
                    self.ax[r][c].set_zlabel("z")
                elif self.dimension[r][c] == 2:
                    self.ax[r][c] = self.fig.add_subplot(rows, columns, c+1 + (r)*(columns)) # get 2d plot
                    self.ax[r][c].axis('scaled') # set up axes
                    self.ax[r][c].set_xlabel("x")
                    self.ax[r][c].set_ylabel("y")
        self.particles = [] # store objects within system
        self.rods = []
        self.traces = []
        self.springs = []
        self.fades = []
        self.polygons = []
        self.data = data # data of general coordinate values at times t
        self.time = t # np.array of times
    
    def limits(self,x,y,z=False, row=1, column=1): # set axes limits
        row, column = self.check_ax(row, column)
        self.ax[row][column].set_xlim(x[0], x[1])
        self.ax[row][column].set_ylim(y[0], y[1])
        if z:
            self.ax[row][column].set_zlim(z[0], z[1])
            self.ax[row][column].autoscale_view()
    
    def create_particle(self,a,conv, color = 'red', s=10, row=1, column=1): # create a particle and store
        row, column = self.check_ax(row, column)
        temp = Particle(a,conv, color, s, self.ax[row][column], self.dimension[row][column])
        self.particles.append(temp)
        return temp # return particle reference
    
    def create_rod(self,p1,p2, color='k', row=1, column=1): # create a rod and store
        row, column = self.check_ax(row, column)
        self.rods.append(Rod(p1,p2,color,self.ax[row][column], self.dimension[row][column]))
    
    def create_trace(self,p,length,color = None, row=1, column=1): # create a trace and store
        row, column = self.check_ax(row, column)
        if color == None: # if no color given set to particle color
            color = p.color
        self.traces.append(Trace(p,length,color,self.ax[row][column], self.dimension[row][column]))
    
    def create_spring(self,p1,p2,lamb,nat_l,color='red', row=1, column=1): # create a spring and store
        row, column = self.check_ax(row, column)
        self.springs.append(Spring(p1,p2,lamb,nat_l,color,self.ax[row][column],self.dimension[row][column]))

    def create_fade(self,p,length,color = None, row=1, column=1):
        row, column = self.check_ax(row, column)
        if color == None: # if no color given set to particle color
            color = p.color
        self.fades.append(Fade(p,length,color,self.ax[row][column], self.dimension[row][column]))
    
    def create_polygon(self,ps,color='red',alpha=0.5, row=1, column=1):
        row, column = self.check_ax(row, column)
        self.polygons.append(Polygon(ps,color,alpha,self.ax[row][column],self.dimension[row][column]))
    
    def update(self,j): # update at time j
        for i in range(len(self.particles)): # update objects by calling function
            self.particles[i].update(self.data[j]) # pass in slice of data at time j
        for i in self.rods:
            i.update()
        for i in self.traces:
            i.update()
        for i in self.springs:
            i.update()
        for i in self.fades:
            i.update()
        for i in self.polygons:
            i.update()


    def run(self, fps): # run the animation as a window to be seen
        self.ani = FuncAnimation(self.fig,self.update,range(1,len(self.time)), interval=1000/fps, blit=False)
        plt.show()

    def savegif(self, filename, fps): # save animation as a gif: requires pillow
        self.ani = FuncAnimation(self.fig,self.update,range(1,len(self.time)), interval=1000/fps, blit=False) # create animation
        base_path = Path(__file__).parent # get main path of workspace
        filename += '.gif'
        file_path = (base_path / "../gifs/"/filename).resolve() # put filename in correct subdirectory
        writer = PillowWriter(fps=fps, bitrate=-1) 
        self.ani.save(file_path, writer = writer) # save gif with pillow
    
    def savemp4(self, filename, fps, ffmpeg_loc='C:/FFmpeg/bin/ffmpeg', dpi=500): # save animation as mp4: requires ffmpeg
        plt.rcParams['animation.ffmpeg_path'] = ffmpeg_loc # locate ffmpeg on computer
        self.ani = FuncAnimation(self.fig,self.update,range(1,len(self.time)), interval=1000/fps, blit=False) # create animation
        base_path = Path(__file__).parent # get main path of workspace
        filename += '.mp4'
        file_path = (base_path / "../mp4s/"/filename).resolve() # put filename in correct subdirectory
        writer = FFMpegWriter(fps=fps, bitrate=5000)
        self.ani.save(str(file_path), writer = writer, dpi=dpi) # write mp4 to file - high default dpi to get quality

    def check_ax(self, row, column):
        if row < 1 or row > self.rows: # check if row/column allowed
            raise Exception("Row index out of range, should be 1 <= row <= " + str(self.rows) +", you gave row=" + str(row))
        if column < 1 or column > self.columns:
            raise Exception("Column index out of range, should be 1 <= column <= " + str(self.columns) +", you gave column=" + str(column))
        return row-1, column-1 # return row column array indices - which are 0 based