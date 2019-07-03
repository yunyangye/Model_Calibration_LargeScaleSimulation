import lhs
import modelCreate as mc
import subprocess
import pandas as pd
import os
import shutil
import time
import multiprocessing as mp
import math

number_samples = 1000

climates = ['1A']
vintages = ['Pre1980','Post1980']

# generate sample list
def sampleList():
    for climate in climates:
        for vintage in vintages:
            name_var,val_list = lhs.sampleLHS('./uncertaintiesVar.csv',number_samples,climate,vintage)
            name_var_list = ''
            for x in name_var:
                name_var_list += ','
                name_var_list += x
            name_var_list += '\n'
            val_list_1 = []
            for i,row in enumerate(val_list):
                temp = str(i+1)
                for x in row:
                    temp += ','
                    temp += str(x)
                val_list_1.append(temp + '\n')
            f = open('./sample_list/'+climate+'_'+vintage+'.csv', 'wb')
            f.writelines(name_var_list)
            for x in val_list_1:
                f.writelines(x)
            f.close()

# collect the energy data
def collectInformation(html_file):
    tables = pd.read_html(html_file)
    site_EUI = float(tables[0][2][1])
    elec_EUI = float(tables[3][1][16])/float(tables[2][1][1])*1000
    ng_EUI = float(tables[3][2][16])/float(tables[2][1][1])*1000
    heat_elec_EUI = float(tables[3][1][1])/float(tables[2][1][1])*1000
    cool_elec_EUI = float(tables[3][1][2])/float(tables[2][1][1])*1000
    int_lig_elec_EUI = float(tables[3][1][3])/float(tables[2][1][1])*1000
    ext_lig_elec_EUI = float(tables[3][1][4])/float(tables[2][1][1])*1000
    int_eqp_elec_EUI = float(tables[3][1][5])/float(tables[2][1][1])*1000
    fan_elec_EUI = float(tables[3][1][7])/float(tables[2][1][1])*1000
    pump_elec_EUI = float(tables[3][1][8])/float(tables[2][1][1])*1000
    water_elec_EUI = float(tables[3][1][12])/float(tables[2][1][1])*1000
    heat_ng_EUI = float(tables[3][2][1])/float(tables[2][1][1])*1000
    water_ng_EUI = float(tables[3][2][12])/float(tables[2][1][1])*1000
    data = [site_EUI,elec_EUI,ng_EUI,heat_elec_EUI,cool_elec_EUI,int_lig_elec_EUI,ext_lig_elec_EUI,
            int_eqp_elec_EUI,fan_elec_EUI,pump_elec_EUI,water_elec_EUI,heat_ng_EUI,water_ng_EUI]
    
    return data

# create model, conduct simulations, and collect energy data
def createSimulateModel(vintage,climate,val_var,simu_id,output):
    file_name = 'RefBldgMediumOffice'
    file_name_sch = 'schedule'
    # create a temp folder
    os.mkdir('./'+simu_id)
    # create models
    mc.modelCreate(file_name,file_name_sch,simu_id+'/'+simu_id,val_var,climate)
    # run models
    subprocess.call(['C:\EnergyPlusV8-6-0\energyplus.exe', '-w', './climate/'+climate+'_2003.epw',
                     '-d', './'+simu_id, '-p', simu_id, 
                     './'+simu_id+'/'+simu_id+'.idf'])
    # collect simulation data
    data = collectInformation('./'+simu_id+'/'+simu_id+'tbl.htm')
    line = simu_id+','+vintage+','+climate
    for x in val_var:
        line += ','
        line += str(x)
    for x in data:
        line += ','
        line += str(x)
    line += '\n'
    # record simulation data
    if not os.path.isfile('./energy_results/'+vintage+'_'+climate+'.csv'):
        title = 'id,vintage,climate,'
        title += 'TotalFloorArea,AspectRatio,FTCH,WWR,GlazingSillHeight,ExtWallRval,RoofRval,WindUfac,WindSHGC,FoundRval,InfRate,StartTimeOther,EndTimeOther,StartTimeHVAC,EndTimeHVAC,PeoD,LPD,EPD,COP,BurnEff,FanEff,Vent,SWHEff,'
        title += 'site_EUI,elec_EUI,ng_EUI,heat_elec_EUI,cool_elec_EUI,int_lig_elec_EUI,ext_lig_elec_EUI,int_eqp_elec_EUI,fan_elec_EUI,pump_elec_EUI,water_elec_EUI,heat_ng_EUI,water_ng_EUI\n'
        f = open('./energy_results/'+vintage+'_'+climate+'.csv','ab')
        f.writelines(title)
        f.close()
    f = open('./energy_results/'+vintage+'_'+climate+'.csv','ab')
    f.writelines(line)
    f.close()
    
    output.put(data)
    
    # remove the temp folder
    shutil.rmtree('./'+simu_id)

# parallel simulation
def paraSimulation(vintage,climate,Val_Var):
    #record the start time
    start = time.time()
    #multi-processing
    output = mp.Queue()
    processes = [mp.Process(target=createSimulateModel,args=(vintage,climate,Val_Var[i],str(i+1),output)) for i in range(len(Val_Var))]
    #count the number of cpu
    cpu = mp.cpu_count()#record the results including inputs and outputs
    print cpu    
    model_results = []    
    run_times = math.floor(len(processes)/cpu)
    if run_times > 0:
        for i in range(int(run_times)):
            for p in processes[i*int(cpu):(i+1)*int(cpu)]:
                p.start()
            
            for p in processes[i*int(cpu):(i+1)*int(cpu)]:
                p.join()
            #get the outputs
            temp = [output.get() for p in processes[i*int(cpu):(i+1)*int(cpu)]]
            for x in temp:
                model_results.append(x)
    for p in processes[int(run_times)*int(cpu):len(processes)]:
        p.start()
    for p in processes[int(run_times)*int(cpu):len(processes)]:
        p.join()
    #get the outputs
    temp = [output.get() for p in processes[int(run_times)*int(cpu):len(processes)]]
    for x in temp:
        model_results.append(x)
    #record the end time
    end = time.time()
    return model_results,end-start

# __main__
sampleList()
for climate in climates:
    for vintage in vintages:
        f = open('./sample_list/'+climate+'_'+vintage+'.csv', 'rb')
        lines = f.readlines()
        f.close()
        # identify the id of End_Time_Other
        for i in range(1,len(lines[0].split(','))):
            if lines[0].split(',')[i].replace('\n','') == 'EndTimeOther':
                end_time_id = i
                break
        # generate variables
        Val_Var = []
        for i in range(1,len(lines)):
            id_sample = lines[i].split(',')[0]
            val_var = []
            for j in range(1,len(lines[i].split(','))):
                if j == end_time_id - 1:
                    Start_Time_Other = float(lines[i].split(',')[j].replace('\n',''))
                    val_var.append(float(lines[i].split(',')[j].replace('\n','')))
                elif j == end_time_id:
                    val_var.append(float(lines[i].split(',')[j].replace('\n','')))
                    val_var.append(Start_Time_Other-1)
                    val_var.append(float(lines[i].split(',')[j].replace('\n',''))+1)
                else:
                    val_var.append(float(lines[i].split(',')[j].replace('\n','')))
            Val_Var.append(val_var)
        # parallel simulation
        model_results,during_time = paraSimulation(vintage,climate,Val_Var)
        print model_results
        print during_time
