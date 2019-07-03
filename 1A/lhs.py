import pyDOE as doe

# select building samples by using lartin hypercube sampling method
# path_uncertaintiesVar: path of uncertaintiesVar.csv
# number_samples: number of the samples
# climate: climate zone from the 15 climate zones
# vintage: Pre1980 or Post1980
def sampleLHS(path_uncertaintiesVar,number_samples,climate,vintage):
    # read data from uncertaintiesVar.csv
    f = open(path_uncertaintiesVar,'rb')
    lines = f.readlines()
    f.close()
    
    # identify the id of needed column
    for i in range(len(lines[0].split(','))):
        if vintage+'_'+climate in lines[0].split(',')[i]:
            col_loc_id = i
            break
    
    # get the data
    name_var = []
    min_var = []
    max_var = []
    for i in range(1,len(lines)):
        if '_Min' in lines[i].split(',')[0]:
            name_var.append(lines[i].split(',')[0].replace('_Min',''))
            min_var.append(float(lines[i].split(',')[col_loc_id].replace('\n','')))
        else:
            max_var.append(float(lines[i].split(',')[col_loc_id].replace('\n','')))
    
    # select samples
    sample_temp = doe.lhs(len(name_var), samples=number_samples)
    val_list = []
    for row in sample_temp:
        temp = []
        for i in range(len(min_var)):
            temp.append((max_var[i]-min_var[i])*row[i]+min_var[i])
        val_list.append(temp)
    
    return name_var,val_list
