*last updated 09/06/2020*

## Animate
Animate is the class designed to allow systems to be plotted as animated figures, using matplotlib. While figures can be preiewed live, best results are obtained by saving as gifs or mp4s.

### Methods

#### \_\_init__(self,`data`,`t`,`d`=2, `rows`=1, `columns`=1):

`data`: Provides the coordinate data for the system, can be taken directly from the output of a SystemL object. This is a 2D numpy array

`t`: The times corresponding to the data - note that this is only used for basic purposes, and will not guarantee an accurate frame rate - this must be provided as an argument to the animator methods

`d`: The dimension of the figure, either 2 for 2d or 3 for 3d. If multiple figures are plotted a `rows`x`columns` array of values may be provided to give different dimensions to each figure. A single value will be applied to all figures

`rows`: The number of rows of figures that should be plotted

`columns`: The number of columns of figures that should be plotted

`returns`: A reference to the Animate object

#### limits(self,`x`,`y`,`z`=False, `row`=1, `column`=1):

Sets the limits of the axes on a figure

`x`: A list of length 2 giving the minimum and maximum x coordinates to be plotted

`y`: A list of length 2 giving the minimum and maximum y coordinates to be plotted

`z`: A list of length 2 giving the minimum and maximum z coordinates to be plotted, or leave as False for a 2D figure

`row`: The row of the figure to which the limits are applied

`column`: The column of the figure to which the limits are applied

#### create_particle(self,`a`,`conv`, `color` = 'red', `s`=10, `row`=1, `column`=1):

Creates a Particle object within the Animate object that will be rendered on a figure. This appears as a point.

`a`: The initial location to place the particle, if creating an animation then `data[0]` is a suitable location as the first point the particle will exist at

`conv`: A function which takes in a list of the generalised coordinate data and returns a list or tuple of the coordinates that should be plotted on the figure

`color`: The color to draw the point - should be a recognised matplotlib color, including those from the xkcd color survey

`s`: The size to draw the particle

`row`: The row of the figure on which to plot the particle

`column`: The column of the figure on which to plot the particle

`returns`: A reference to the particle object for use when creating other graphical objects in the Animate object

#### create_rod(self,`p1`,`p2`, `color`=`k`, `row`=1, `column`=1):

Creates a Rod object within the nimate object that will be rendered on a figure. A rod is a straight connector between to particles and is drawns a line.

`p1`: A reference to a particle at one end of the rod

`p2`: A reference to a particle at the other end of the rod

`color`: The color to draw the rod - should be a recognised matplotlib color, including those from the xkcd color survey

`row`: The row of the figure on which to plot the rod

`column`: The column of the figure on which to plot the rod

#### create_spring(self,`p1`,`p2`,`lamb`,`nat_l`,`color`='red', `row`=1, `column`=1):

Creates a Spring object within the Animate object that will be rendered on a figure. A spring is a rod that changes color based on its length compared to a natural length and spring constant λ

`p1`: A reference to a particle at one end of the spring

`p2`: A reference to a particle at the other end of the spring

`lamb`: The spring constant of the spring material per unit length (=k/nat_l)

`nat_l`: The natural length of the spring

`color`: The color to draw the spring - should be a recognised matplotlib color, including those from the xkcd color survey

`row`: The row of the figure on which to plot the spring

`column`: The column of the figure on which to plot the spring

#### create_trace(self,`p`,`length`,`color` = None, `row`=1, `column`=1):

Creates a Trace object within the Animate object that will be rendered on a figure. The trace is a curve tracking the past locations of a particle.

`p`: A reference to the particle that will be traced

`length`: The number of frames for which to track the particle

`color`: The color of the trace, deafults to the color of the particle it is tracing

`row`: The row of the figure on which to plot the trace

`column`: The column of the figure on which to plot the trace

#### create_fade(self,`p`,`length`,`color` = None, `row`=1, `column`=1):

Creates a Fade object within the Animate object that will be rendered on a figure. The fade is a curve tracking the past locations of a particle, that fades out to transparency over time.

`p`: A reference to the particle that will be traced

`length`: The number of frames for which to track the particle

`color`: The color of the fade, deafults to the color of the particle it is tracing

`row`: The row of the figure on which to plot the fade

`column`: The column of the figure on which to plot the fade

#### create_polygon(self,`ps`,`color`='red',`alpha`=0.5, `row`=1, `column`=1):

Creates a Polygon object within the Animate object that will be rendered on a figure. The polygon is drawn with vertices at a series of particles, joining the first and last

`ps`: A list of references to the particles to be drawn around

`color`: The color of the polygon

`alpha`: The transparency of the polygon, an alpha value between 0 and 1

`row`: The row of the figure on which to plot the polygon

`column`: The column of the figure on which to plot the polygon

#### update(self,`j`):

Updates the locations of all the objects withi the animate object using the data array provided at creation.

`j`: The index at which to get the coordinate data from the data array provided

#### run(self, `fps`):

Run the animation live in a matplotlib window. This may be laggy on some computers - saving animations to file is strongly recommended for most purposes.

`fps`: The frames per second of the animation - for real time playback this should correspond to the frames per second of the data array

#### savegif(self, `filename`, `fps`):

Save the animation into an animated gif file. This method requires PIL to be installed.

`filename`: A string giving the filepath and filename, excluding the extension.

`fps`: The frames per second of the animation - for real time playback this should correspond to the frames per second of the data array

#### savemp4(self, `filename`, `fps`, `ffmpeg_loc`='C:/FFmpeg/bin/ffmpeg', `dpi`=500):

Save the animation into an mp4 file. This method requires ffmpeg to be installed.

`filename`: A string giving the filepath and filename, excluding the extension.

`fps`: The frames per second of the animation - for real time playback this should correspond to the frames per second of the data array

`ffmpeg_loc`: The location of the ffmpeg.exe file on the users computer e.g. default installation location of "C:/FFmpeg/bin/ffmpeg.exe" has `ffmpeg_loc` = 'C:/FFmpeg/bin/ffmpeg'

`dpi`: the dots per inch of the output mp4. Recommended for high quality is `dpi`=500.

### Examples

Examples files can be found in the examples folder in the github repository

[Animated Pendulum](https://github.com/rjbourne/symphysics/wiki/Animated-Pendulum)