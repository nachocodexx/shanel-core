#gen_range = lambda min,max: list(range(min,max))

def generate_range_ids(**kwargs):
    n_range = kwargs.get("n_range")
    range_ids= []
    for i in range(n_range):
        id = 'RANGE_{}'.format(i)
        range_ids.append(id)
    return range_ids

def generate_ranges_values(**kwargs):
    #  Arreglo de ids
    range_ids = kwargs.get("range_ids")
    minValue = kwargs.get("minValue")
    #  Valor maximo de los rangos.
    maxValue    = kwargs.get("maxValue") 
    #  Cantidad de rangos
    n_range   = kwargs.get("n_range")
    #  Aprox. de longitud del rango 
    r         = round( (maxValue) / n_range) 
    # ESTO QUEREMOS
    # rangos = {"RANGE_1" : [0,1,2], "RANGE_2": [3,4,5], "RANGE_3": [6,7,8,9] }
    # ARRAY <STRING>
    # rangos = { <KEY> : <VALUE> }
    rangos = { }
    gen_range = lambda minValue,maxValue: list(range(minValue,maxValue))
    for index,range_id in enumerate(range_ids): 
        minVal = index * r
        maxVal = maxValue+1 if (index==n_range-1) else minVal + r 
        rangos[ range_id ] = gen_range(minValue = minVal, maxValue = maxVal)
    return rangos
    
   
# Cantidad de rangos
n_range   = 3
# Generar ids  
range_ids = generate_range_ids(n_range = n_range)
# 
ranges_values = generate_ranges_values(
    minValue  = 0,
    maxValue  = 9, 
    range_ids = range_ids, 
    n_range   = n_range
)
print(ranges_values)