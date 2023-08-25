import subprocess
import numpy as np
import re

#A series of functions to interact with Tetrad algorithms and output
# Use in Sanchez-Romero et al.(2023) https://doi.org/10.1016/j.neuroimage.2023.120300

def PCalgRun(input_data, out_dir, out_name, tetrad_path, alpha):
    '''
    Function that wraps Tetrad Java command line
    Makes a call of PC from terminal using predefined parameters 
    described in 
    Java is required!!
    
    INPUT:
        inputData: string with the name of the datafile use for the run. Must be the full path.
                    must be continuous data, comma delimited, without labels (headers)!
        outDir: directory to output the inferred PC graph
        outName: string with the name of the output file. no extension. a txt file
        tetrad_path: the directory were Tetrad is located. Must be the full path.
        alpha: significance level for the partial correlation test: lower value produce sparser graphs
    '''
    # algorithm parameters
    algorithm = 'pc-all'
    test = 'fisher-z-test'  #z-test conditional independence
    depth = -1  #maximum size of the conditioning set, -1 is all the variables
    #Collider discovery: 1 = Lookup from adjacency sepsets, 2 = Conservative (CPC), 3 = Max-P
    collider_discovery_rule = 3                
    #Collider conflicts: 1 = Overwrite, 2 = Orient bidirected, 3 = Prioritize existing colliders
    conflict_rule = 3                     

    #input-output parameters
    data_type = 'continuous'
    delimiter = 'comma'
    #others
    thread = '360'  #for parallelization, usually equal to the number of variables
   
    #paste the string to call it from system
    call_PC = (
              f'java -Xmx20G -jar {tetrad_path} '
              f'--thread {thread} '
              f'--algorithm {algorithm} --stableFAS --concurrentFAS '
              f'--test {test} --alpha {alpha} --depth {depth} '
              f'--colliderDiscoveryRule {collider_discovery_rule} '
              f'--conflictRule {conflict_rule} '
              f'--dataset {input_data} --no-header --data-type {data_type} --delimiter {delimiter} '
              f'--out {out_dir} --prefix {out_name} --skip-latest  '
              )
    p = subprocess.call(call_PC,shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    # print if there was an error in the PC run
    if p != 0:
        print(f'{p}, error in the PC run')
        
        
        
        
def tetrad2matrix(fname):
    ''''
    Transforms a Tetrad graph (txt with list of edges) into a numpy array (connectivity matrix).
    
    Input:
       fname: string of the file containing the graph as output by Tetrad, which is a list of edges   
    Output:
        mat: a directed connectivity matrix where directed edges are encoded with 2, and undirected with 1.  
        the orientation is read from column to row, so mat(2,1)=2 implies X1 --> X2
    '''
    
    tet = [line.rstrip('\n') for line in open(fname)]
    a = tet.index('Graph Nodes:') + 1
    b = tet.index('Graph Edges:') - 1
    R = tet[a:b]
    V = re.findall('\w*\w',R[0]) #split the names no matter the delimiter used

    q = tet.index('Graph Edges:') + 1 # q is the first line index in the list of edges
    n = 0;
    fi = 0;
    #this is adjusted to fGES or FASK type of output. fGES output has more info. after the list of edges
    while fi < len(tet) and tet[fi]: #keep counting until you find a white line or fi is less than the size of the file
        n += 1
        fi = q + n -1  #fi is the index of the last line in the list of edges
    
    s = (len(V),len(V))
    mat = np.zeros(s)

    for i in range(q,fi):
        n = tet[i].split() #split the string  1.VAR_1 --> VAR_2
    
        #n1 = n[1].split('_')
        n1 = re.findall('\d*\d',n[1]) #extract the number from VAR_# or X# or X_#
        n1 = int(n1[0])-1  #get the index for VAR_1, -1 given that Python index starts at 0
    
        #n2 = n[3].split('_')
        n2 = re.findall('\d*\d',n[3])
        n2 = int(n2[0])-1 #get the index for VAR_2, -1 given that Python index start at 0
    
        at = list(n[2])[0] #arrowtail
        ah = list(n[2])[2] #arrowhead, to determine if it is a directed edge or undirected edge
    
        if (at == '-' and ah == '>'):
            mat[n2][n1] = 2
        elif (at == '-' and ah == '-'):
            mat[n2][n1] = 1
            mat[n1][n2] = 1
    
    return mat 