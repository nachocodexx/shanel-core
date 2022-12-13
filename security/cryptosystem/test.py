gen_range = lambda min,max: list(range(min,max))

def range_id(**kwargs):
    n_range = kwargs.get("n_range")
    range_ids= []
    for i in range(n_range):
        id = 'RANGE_{}'.format(i)
        range_ids.append(id)
    return range_ids

def ranges_values(**kwargs):
    range_ids = kwargs.get("range_ids")
    maxVal    = kwargs.get("maxVal")
    n_range   = kwargs.get("n_range")
    r         = round(maxVal / n_range)
    
    for i in range(n_range):
        if(i == 0):
            min = 0
            max = r
        elif(i == n_range):
            min = min
            max = maxVal
        else:
            min = min
            max = min + r
        range_ids[i]: gen_range(min,max)
        min = max
    print(range_ids)
   

n_range = 3
range_ids = range_id(n_range = n_range)
ranges_values(maxVal = 70, range_ids = range_ids, n_range = n_range)
