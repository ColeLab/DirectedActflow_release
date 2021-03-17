import numpy as np
from sklearn.linear_model import LinearRegression

def featureSelectRegression(M, D, typ='symmetric'):
    '''
    Compute a weighted connectivity matrix with M as mask.
    This imply that each row in M is regressed onto its non-zero column entries
    The non-zero column entries are the selected features
    INPUT:
        M : connectivity matrix (weighted or binary)
        D : data associated with the connectivity matrix
        typ : type of input of the connectivity matrix, 
              string: 'symmetric': eg. from a partial correlation analysis 
                      'adjacencies': eg. use adjacencies from a causal search 
                      or 'parents' : eg. just use the parents of a causal search
    OUTPUT:
        M_feat : a weighted connectivity matrix
    '''
    
    #binarize the input connectivity matrix
    if typ == 'parents' or typ == 'adjacencies':
        M_bin = M == 2
    elif typ == 'symmetric':
    #For binary matrices like partial correlation matrices
        M_bin = M != 0
    
    #get number of nodes
    num_nodes = M_bin.shape[0]
    #allocate memory
    M_feat = np.zeros((num_nodes,num_nodes))
    #iterate through each node y
    for y in range(num_nodes):
        if typ == 'adjacencies':
            #get the indices for parents and children
            parents = np.where(M_bin[y,:])
            children = np.where(M_bin[:,y])
            both = np.concatenate((parents,children),axis=1)
            #extract data for parents and children
            X = D[:,both].squeeze(axis=1)
            #if the node y has at least one adjacency, run the regression
            #otherwise, skip the regression step to avoid an error
            if X.any():
                reg_y = LinearRegression().fit(X,D[:,y])
                M_feat[y,both] = reg_y.coef_
            
        elif typ == 'parents' or 'symmetric':
            #define the new dataset for the regressors X    
            X = D[:,M_bin[y,:]]
            #if the node y has at least one adjacency, run the regression
            #otherwise, skip the regression step to avoid an error
            if X.any():
                #regress y on the regressors regX
                reg_y = LinearRegression().fit(X, D[:,y])
                M_feat[y,M_bin[y,:]] = reg_y.coef_
    
    
    return M_feat