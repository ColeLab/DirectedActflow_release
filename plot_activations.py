# function to plot a matrix of activations: regions x task conditions
import matplotlib.colors as colors
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import os

def plot_activations(activations, title, functional_networks=True, no_ylabel=False, network_color_bar=False):

    # for the weights colorbar: red positive, blue negative
    v_min = np.min(activations)
    v_max = np.max(activations)
    v_mid = 0
    # define the figure and the axes
    fig,ax = plt.subplots()
    
    # to plot regions ordered by networks
    # Glasser 360 cortex parcellation ordered into functional networks reported in Ji et al., (2019)
    # path where the network file is: it contains labels (first column) and order (second column)  
    current_dir = os.getcwd()
    net_file_path = f'{current_dir}/aux_files/networks_labels.txt'
    net_file = np.loadtxt(net_file_path,delimiter=',')
       
    
    if functional_networks == True:
        # to assign each of the 360 nodes to its corresponding network
        # make as integer and subtract 1, so the indices start in 0, as Python requires.
        net_order = net_file[:,1].astype(int) - 1
    
    elif functional_networks == False:
        # no order by networks. keep the order of the dataset
        net_order = np.arange(activations.shape[0])
    
    # plot the data
    img = ax.imshow(activations[net_order,:],
                    origin = 'upper',
                    cmap='seismic',
                    alpha = 1,
                    clim=(v_min, v_max), 
                    norm=MidpointNormalize(midpoint=v_mid,vmin=v_min, vmax=v_max),
                    aspect='auto'
                   )
    plt.title(title,fontsize=18)
    
    task_conditions = ['EMOTION:fear','EMOTION:neut','GAMBLING:win','GAMBLING:loss','LANGUAGE:story','LANGUAGE:math',
                  'MOTOR:cue','MOTOR:lf','MOTOR:rf','MOTOR:lh','MOTOR:rh','MOTOR:t','REASONING:rel',
                  'REASONING:match','SOCIAL:mental','SOCIAL:rnd','WM 0bk:body','WM 0bk:faces','WM 0bk:places',
                  'WM 0bk:tools','WM 2bk:body','WM 2bk:faces','WM 2bk:places','WM 2bk:tools']
    
    plt.xticks(np.arange(24),labels=task_conditions,rotation=90)
    ax.tick_params(labelsize=11,length=0.01)
    # axes ticks labels
    a = np.round(activations.shape[0]/2).astype(int)
    b = np.round(activations.shape[0])
    # plt.xticks([1,a,b])
    plt.yticks([1,a,b])
    plt.ylabel('360 Regions\n (12 networks)',fontsize=15)
    # labels font size and length of the ticks
    # Thickness of the connectivity matrix border
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(0)
    # properties of the weights colorbar
    cbar = plt.colorbar(img,pad=0.01)
    cbar.ax.tick_params(labelsize=13)
    cbar.outline.set_linewidth(0)
    
    if no_ylabel == True:
        plt.yticks([])
        plt.ylabel('')
        
    if network_color_bar == True:
        network_palette = ['royalblue','slateblue','paleturquoise','darkorchid','limegreen',
                          'lightseagreen','yellow','orchid','r','peru','orange','olivedrab']
        network_palette = np.asarray(network_palette)
        #define the colormap as an independent graphical object
        cmap = mpl.colors.ListedColormap(network_palette)
        #number of nodes (size) in each of the 12 networks
        size_networks=[]
        #path where the network file is: it contains labels (first column) and order (second column)
        net_labels = net_file[:,0].astype(int)
        #loop through all the labels: 1 to 12 to count the number of nodes
        for i in range(np.max(net_labels)):
            size_networks.append(np.sum(net_labels==i+1))
        #the bounds of the bar are the cumulative sum for each network size starting at zero: 
        #ie, 0, 6, 6+54, 6+54+39, etc...
        su = 0
        #the first element of the networks bar bounds is zero
        bounds = [0]
        #this loop makes the cumulative sums
        for i in range(np.max(net_labels)):
            su += size_networks[i]
            bounds.append(su)
        #define the size of the color blocks according to the bounds (ie. the number of nodes)
        norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

        #get the size and position of the connectivity matrix as a reference 
        #to position the networks color bars
        l, b, w, h = ax.get_position().bounds

        ax2 = fig.add_axes([l/1.105,b,w/25,h])

        cbNet = mpl.colorbar.ColorbarBase(ax2, cmap=cmap,
                                        norm=norm,
                                        spacing='proportional',
                                        orientation='vertical')
        cbNet.outline.set_linewidth(0)
        cbNet.set_ticks([])
        cbNet.ax.invert_yaxis() 
        #flip the colorbar so it follow the network order
        ax.tick_params(axis='y',labelsize=14,pad=18,length=0.01)
        
        

class MidpointNormalize(colors.Normalize):
    """
    Normalise the colorbar so that diverging bars work there way either side from a prescribed midpoint value)
    e.g. im=ax1.imshow(array, norm=MidpointNormalize(midpoint=0.,vmin=-100, vmax=100))
    """
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))