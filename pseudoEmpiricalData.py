import numpy as np
from scipy import stats, linalg

def pseudoEmpiricalData(data, model, sample_size = 1000, weights_given = False, min_coeff = 0.3, max_coeff = 0.8, p_neg = 0.3):
    '''
    Generate pseudoempirical data, using an empirical dataset and a causal model

    INPUT:
        data : a data array with dimensions [timepoints x num_nodes]
        model : a binary square matrix, with column --> row, causal direction M[i,j] = 1 : j --> i
                can also be a weighted matrix, if so set weights=True 
        sample_size : number of datapoints sampled using bootstrap,
                     (ie. sample with replacement from data), default is 1000.
        weights : if False, compute weights for the model, otherwise use the weights from input model
        min and max_coeff : limits for coefficients sampled from a random uniform, 
        p_neg : a value between 0 and 1, 
                it determines the aprox. proportion of negative coefficients in the matrix 
                
    OUTPUT:
        X : data array with dimensions [num_nodes x sample_size]
        W : weighted directed connectivity matrix [num_nodes x num_nodes], causal direction M[i,j]: j --> i
    '''
    
    
    #number of nodes in the model
    num_nodes = model.shape[0]
    #number of datapoints in the dataset
    time_points = data.shape[0]
    
    #define the error terms E using the randomized empirical data
    E = np.zeros((num_nodes, sample_size))
    #methods 1: randomize original timepoints
    #for n in range(numNodes):
        #randomize the timepoints
        #random_time = np.arange(timePoints)
        #np.random.shuffle(random_time)
        #random_node = np.random.randint(0,data.shape[1])
        #E[n,:] = data[random_time, random_node]
        
    #method 2: bootstrap: sample with replacement from the original timepoints
    for n in range(num_nodes):
        #choose a random noise
        random_node = np.random.randint(0,data.shape[1])
        #get the data from that random node
        R = data[:,random_node]
        #bootstrap: sample random points from the original sample, with replacement
        E[n,:] = np.random.choice(R,size=[1,sample_size],replace=True)
    
    #standardize the timepoints
    E = stats.zscore(E,axis=1)
        
    if weights_given == False:
        #define the W matrix from the model
        W = np.zeros((num_nodes, num_nodes))
        num_edges = np.sum(model == 1)
        
        #sample the coefficients from a random uniform U(min_coeff,max_coeff)
        coeff = np.random.uniform(min_coeff, max_coeff, size = (1, num_edges))
        
        #each coefficient has a probability p_neg of being negative.
        #p_neg determines the aprox. overall proportion of negative and positive edges
        aux_sign= np.random.choice([-1,1],size = (1, num_edges), p = [p_neg, 1-p_neg])
        #multiply the sign by the coefficient
        coeff = np.multiply(coeff,aux_sign)
        
        #threshold to avoid edges with small coefficients close to zero
        #thresh = 0.2
        #coeff[(coeff < thresh) & (coeff >= 0)] = thresh
        #coeff[(coeff > -thresh) & (coeff < 0)] = -thresh
        #assigned the coefficients to the edges
        W[model.nonzero()] = coeff
        #guarantee that the diagonal is zero
        np.fill_diagonal(W,0)
    
    elif weights_given == True:
        W = model
    
    #in the linear model the dataset X is defined as X = WX + E, 
    #so it can be expressed as X = inv(I-W)*E to generate X dataset, where I is the identity matrix
    I = np.identity(num_nodes)  
    X = np.dot(linalg.pinv(I - W), E)
    #standardize the data to mean 0 and std.dev 1
    #X = stats.zscore(X,axis=1)
    
    return X, W