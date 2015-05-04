import copy
import matplotlib.pyplot as plt
import numpy as np

# Global figure variable
# This is to make sure each plot is drawn in a new window, no matter which plotting methods are used
n_fig = 1

def basic_xy(x,y,color='b'):
    
    global n_fig
    figure = plt.figure(n_fig)
    figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
    plt.gca().set_aspect('equal')
    
    plt.plot(x, y, color)
    n_fig += 1

def body_wake_plot(Swimmers):
    
    global n_fig
    figure = plt.figure(n_fig)
    plt.clf()
    figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
    plt.gca().set_aspect('equal')
    maxpercentile = 95 # For truncating outliers
    
    for Swim in Swimmers:
        # Make color map based on vorticity
        color = copy.deepcopy(Swim.Wake.gamma[1:-1])
        # Take a look at positive and negative circulations separately
        if np.min(color) < 0: # Check if negative circulations exist (in case of short simulations)
            # Truncate any negative outliers
            color[color < np.percentile(color[color < 0], 100-maxpercentile)] = np.percentile(color[color < 0], 100-maxpercentile)
            # Normalize negative circulations to [-1,0)
            color[color < 0] = -color[color < 0]/np.min(color)
        if np.max(color) > 0: # Check if positive circulations exist (in case of short simulations)
            # Truncate any positive outliers
            color[color > np.percentile(color[color > 0], maxpercentile)] = np.percentile(color[color > 0], maxpercentile)
            # Normalize positive circulations to (0,1]
            color[color > 0] = color[color > 0]/np.max(color)
        
        # Scatter plot of wake points with red-white-blue colormap, as well as body outline and edge panel segment
        plt.scatter(Swim.Wake.x[1:-1], Swim.Wake.z[1:-1], s=30, c=color, edgecolors='none', cmap=plt.get_cmap('bwr_r'))
        plt.plot(Swim.Body.AF.x, Swim.Body.AF.z, 'k')
        plt.plot(Swim.Edge.x, Swim.Edge.z, 'g')
    
    n_fig += 1
    
def cp_plot(Body):
    
    global n_fig
    figure = plt.figure(n_fig)
    figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
    plt.gca().set_aspect('equal')
    plt.gca().invert_yaxis()
    
    plt.plot(Body.AF.x_col[:Body.N/2], Body.cp[:Body.N/2], 'g')
    plt.plot(Body.AF.x_col[Body.N/2:], Body.cp[Body.N/2:], 'b')
    plt.plot(Body.AF.x, -Body.AF.z, 'k')
    
    n_fig += 1
    
def drag_vs_period(Body,RHO,t):
    
    global n_fig
    figure = plt.figure(n_fig)
    figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
    plt.xlabel('tau')
    plt.ylabel('Coefficent of drag')
    
    plt.plot(t[4:]*Body.F, -Body.drag[3:]/(0.5*RHO*Body.V0**2), 'b')
    
    n_fig += 1
    
def lift_vs_period(Body,RHO,t):
    
    global n_fig
    figure = plt.figure(n_fig)
    figure.add_subplot(1, 1, 1, axisbg='1') # Change background color here
    plt.xlabel('tau')
    plt.ylabel('Coefficent of lift')
    
    plt.plot(t[4:]*Body.F, -Body.lift[3:]/(0.5*RHO*Body.V0**2), 'g')
    
    n_fig += 1