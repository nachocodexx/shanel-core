import seaborn as sns
import pandas as pd
import numpy as np

xs = pd.DataFrame({
    "x":[-3,-2,-3,-2, 2, 3, 2, 3,-3,-3,-2,-2, 2, 3, 2, 3],
    "y":[ 3, 3, 2, 2, 3, 3, 2, 2,-2,-3,-3,-2,-3,-3,-2,-2]
})

threshold = 1

D = xs.to_numpy().tolist()
#D = [[-3,3],[-2,3],[-3,2],[-2,2], 
#    [2,3], [3,3], [2,2], [3,2], 
#     [-3,-2],[-3,-3],[-2,-3],[-2,-2],#
#     [2,-3],[3,-3],[2,-2],[3.-2]]

ED =[
    [0 , 1 , 1 , 2 , 5 , 6 , 6 , 7 , 5 , 6 , 7 , 6 , 11, 12, 10, 11],
    [1 , 0 , 2 , 1 , 4 , 5 , 5 , 6 , 6 , 7 , 6 , 5 , 10, 11, 9 , 10], 
    [1 , 2 , 0 , 1 , 6 , 7 , 5 , 6 , 4 , 5 , 6 , 5 , 10, 11, 9 , 10], 
    [2 , 1 , 1 , 0 , 5 , 6 , 4 , 5 , 5 , 6 , 5 , 4 , 9 , 10, 8 , 9], 
    [5 , 4 , 6 , 5 , 0 , 1 , 1 , 2 , 10, 11, 10, 9 , 6 , 7 , 5 , 6], 
    [6 , 5 , 7 , 6 , 1 , 0 , 2 , 1 , 11, 12, 11, 10, 7 , 6 , 6 , 5], 
    [6 , 5 , 5 , 4 , 1 , 2 , 0 , 1 , 9 , 10, 9 , 8 , 5 , 6 , 4 , 5], 
    [7 , 6 , 6 , 5 , 2 , 1 , 1 , 0 , 10, 11, 10, 9 , 6 , 5 , 5 , 4], 
    [5 , 6 , 4 , 5 , 10, 11, 9 , 10, 0 , 1 , 2 , 1 , 6 , 7 , 5 , 6], 
    [6 , 7 , 5 , 6 , 11, 12, 10, 11, 1 , 0 , 1 , 2 , 5 , 6 , 6 , 7], 
    [7 , 6 , 6 , 5 , 10, 11, 9 , 10, 2 , 1 , 0 , 1 , 4 , 5 , 5 , 6], 
    [6 , 5 , 5 , 4 , 9 , 10, 8 , 9 , 1 , 2 , 1 , 0 , 5 , 6 , 4 , 5], 
    [11, 10, 10, 9 , 6 , 7 , 5 , 6 , 6 , 5 , 4 , 5 , 0 , 1 , 1 , 2], 
    [12, 11, 11, 10, 7 , 6 , 6 , 5 , 7 , 6 , 5 , 6 , 1 , 0 , 2 , 1], 
    [10, 9 , 9 , 8 , 5 , 6 , 4 , 5 , 5 , 6 , 5 , 4 , 1 , 2 , 0 , 1], 
    [11, 10, 10, 9 , 6 , 5 , 5 , 4 , 6 , 7 , 6 , 5 , 2 , 1 , 1 , 0]
    ]

#C = [[[-3,3]]]
#C_index = [[0]]

C = []
C_indexes = []

#1.1 Llenar C con el primer registro de D 
C.append([D[0]])
C_indexes.append([0])


# Recorrer los registros en D
for record_index in range(1,len(D)):
    #print("record_index",record_index)
    #2.1 Recorrerlos indices de los clusters
    #print("C_indexes",C_indexes)
    for cluster_index, index_cluster in enumerate(C_indexes):
        #print("cluster_index",cluster_index, "index_cluster",index_cluster)
        ## distancias de un registro con respecto a todos los elementos del cluster
        record_distances = []

        #2.2 recorrer la lista de indices de clusters
        for record_index_cluster in index_cluster:
            #2.3 ubicar el registro en ED con respecto al cluster
            edi = ED[record_index][record_index_cluster] #Distancia de un registro con respecto al registro de un cluster
            record_distances.append(edi)
            #print("record_distances",record_distances)
        #2.4 Obtener menor distancia del registro con respecto a los demas registros del cluster
        min_distance_index = np.argmin(record_distances) #indice de distancia menor
        min_distance = record_distances[min_distance_index]
        #print("min_distance_index",min_distance_index, "min_distance",min_distance)
        #2.5 Decide si pertenece al cluster con respecto al umbral definido
        if (min_distance <= threshold):
            C_indexes[cluster_index].append(record_index)
            #print("Si entra")
        else:
            if(cluster_index < len(C_indexes)-1):
                continue
            else:
                C_indexes.append([record_index])
                break         
print(C_indexes)
