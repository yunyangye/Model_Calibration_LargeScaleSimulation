import numpy as np

def calculateGeoLoc(variables):
    # collect necessary parameters
    total_floor_area = variables[0]
    aspect_ratio = variables[1]
    wwr = variables[2]
    glazing_sill_height = variables[3]
    floor_to_floor_height = variables[4]
    perimeter_zone_depth = 4.572
    number_floors = 3
    plenum_height = 1.3
    
    # calculate X, Y, Z
    area = total_floor_area/number_floors
    length = np.sqrt(area*aspect_ratio)
    width = np.sqrt(area/aspect_ratio)
    X = [0.0,perimeter_zone_depth,length-perimeter_zone_depth,length]
    Y = [0.0,perimeter_zone_depth,width-perimeter_zone_depth,width]
    window_height = floor_to_floor_height*wwr
    Z = [0.0]
    for i in range(3):
        Z.append(floor_to_floor_height*i+glazing_sill_height)
        Z.append(floor_to_floor_height*i+glazing_sill_height+window_height)
        Z.append(floor_to_floor_height*i+floor_to_floor_height-plenum_height)
        Z.append(floor_to_floor_height*i+floor_to_floor_height)
    
    return X, Y, Z

def calculateRval(variables):
    # collect necessary parameters
    # exterior walls
    rval_ext_wall = variables[5]
    thick_wall = 0.0396399760059273
    thick_wall_1 = 0.01
    cond_wall_1 = 0.11
    thick_wall_2 = 0.0127
    cond_wall_2 = 0.16
    # roof
    rval_roof = variables[6]
    thick_roof = 0.110216071059399
    thick_roof_1 = 0.0095
    cond_roof_1 = 0.16
    thick_roof_2 = 0.0015
    cond_roof_2 = 45.006
    # foundation
    rval_foundation = variables[9]
    thick_foundation_1 = 0.1016
    cond_foundation_1 = 1.311
    
    # calculate cond_ext_walls, cond_roof, and rval_foundation
    cond_ext_walls = thick_wall/(rval_ext_wall-thick_wall_1/cond_wall_1-thick_wall_2/cond_wall_2)
    cond_roof = thick_roof/(rval_roof-thick_roof_1/cond_roof_1-thick_roof_2/cond_roof_2)
    rval_foundation = rval_foundation-thick_foundation_1/cond_foundation_1
    
    return thick_wall, cond_ext_walls, thick_roof, cond_roof, rval_foundation

def schedule(file_name_sch,variables,schedule_name):
    # collect necessary parameters
    start_time_other = variables[11]
    end_time_other = variables[12]
    start_time_hvac = variables[13]
    end_time_hvac = variables[14]
    
    # transfer the float into time
    if int(start_time_other) < 10:
        start_time_other_time = '0'+str(int(start_time_other))+':'
    else:
        start_time_other_time = str(int(start_time_other))+':'
    if int((start_time_other-int(start_time_other))*60) >= 10:
        start_time_other_time += str(int((start_time_other-int(start_time_other))*60))
    else:
        start_time_other_time += '0'
        start_time_other_time += str(int((start_time_other-int(start_time_other))*60))
    
    if int(end_time_other) < 10:
        end_time_other_time = '0'+str(int(end_time_other))+':'
    else:
        end_time_other_time = str(int(end_time_other))+':'
    if int((end_time_other-int(end_time_other))*60) >= 10:
        end_time_other_time += str(int((end_time_other-int(end_time_other))*60))
    else:
        end_time_other_time += '0'
        end_time_other_time += str(int((end_time_other-int(end_time_other))*60))

    if int(start_time_hvac) < 10:
        start_time_hvac_time = '0'+str(int(start_time_hvac))+':'
    else:
        start_time_hvac_time = str(int(start_time_hvac))+':'
    if int((start_time_hvac-int(start_time_hvac))*60) >= 10:
        start_time_hvac_time += str(int((start_time_hvac-int(start_time_hvac))*60))
    else:
        start_time_hvac_time += '0'
        start_time_hvac_time += str(int((start_time_hvac-int(start_time_hvac))*60))
    
    if int(end_time_hvac) < 10:
        end_time_hvac_time = '0'+str(int(end_time_hvac))+':'
    else:
        end_time_hvac_time = str(int(end_time_hvac))+':'
    if int((end_time_hvac-int(end_time_hvac))*60) >= 10:
        end_time_hvac_time += str(int((end_time_hvac-int(end_time_hvac))*60))
    else:
        end_time_hvac_time += '0'
        end_time_hvac_time += str(int((end_time_hvac-int(end_time_hvac))*60))    
    
    # read tmpl file
    f = open('./'+file_name_sch+'.tmpl','rb')
    lines_sch = f.readlines()
    f.close()
    
    # create list
    schedule = []
    for i in range(len(lines_sch)):
        if '$'+schedule_name+'$' in lines_sch[i]:
            start_id = i+1
    for i in range(start_id,len(lines_sch)):
        if '$' in lines_sch[i] and '$Start_time_' not in lines_sch[i] and '$End_time_' not in lines_sch[i]:
            end_id = i
            break
    for i in range(start_id,end_id):
        if '$Start_time_Other$' in lines_sch[i]:
            schedule.append(lines_sch[i].replace('$Start_time_Other$',start_time_other_time))
        elif '$End_time_Other$' in lines_sch[i]:
            schedule.append(lines_sch[i].replace('$End_time_Other$',end_time_other_time))
        elif '$Start_time_HVAC$' in lines_sch[i]:
            schedule.append(lines_sch[i].replace('$Start_time_HVAC$',start_time_hvac_time))
        elif '$End_time_HVAC$' in lines_sch[i]:
            schedule.append(lines_sch[i].replace('$End_time_HVAC$',end_time_hvac_time))
        else:
            schedule.append(lines_sch[i])
    
    return schedule

def climateInfo(climate,climate_name):
    # read tmpl file (climate)
    f = open('./tmpl_climate/'+climate+'.tmpl','rb')
    lines = f.readlines()
    f.close()
    
    data = []
    for i in range(len(lines)):
        if '$'+climate_name+'$' in lines[i]:
            start_id = i+1
    for i in range(start_id,len(lines)):
        if '$' in lines[i]:
            end_id = i
            break
    for i in range(start_id,end_id):
        data.append(lines[i])
    
    return data

def modelCreate(file_name,file_name_sch,new_file_name,variables,climate):
    X, Y, Z = calculateGeoLoc(variables)
    thick_wall, cond_ext_walls, thick_roof, cond_roof, rval_foundation = calculateRval(variables)
    BLDG_OCC_SCH = schedule(file_name_sch,variables,'BLDG_OCC_SCH')
    BLDG_LIGHT_SCH = schedule(file_name_sch,variables,'BLDG_LIGHT_SCH')
    BLDG_EQUIP_SCH = schedule(file_name_sch,variables,'BLDG_EQUIP_SCH')
    INFIL_QUARTER_ON_SCH = schedule(file_name_sch,variables,'INFIL_QUARTER_ON_SCH')
    CLGSETP_SCH = schedule(file_name_sch,variables,'CLGSETP_SCH')
    HTGSETP_SCH = schedule(file_name_sch,variables,'HTGSETP_SCH')
    HVACOperationSchd = schedule(file_name_sch,variables,'HVACOperationSchd')
    MinOA_MotorizedDamper_Sched = schedule(file_name_sch,variables,'MinOA_MotorizedDamper_Sched')
    BLDG_SWH_SCH = schedule(file_name_sch,variables,'BLDG_SWH_SCH')
    
    Site_Loc = climateInfo(climate,'Site_Loc')
    Size_DD = climateInfo(climate,'Size_DD')
    Site_WMT = climateInfo(climate,'Site_WMT')
    Site_GT = climateInfo(climate,'Site_GT')
    Fuel_Fac = climateInfo(climate,'Fuel_Fac')
    
    # read tmpl file
    f = open('./'+file_name+'.tmpl','rb')
    lines = f.readlines()
    f.close()
    
    # modify $variables$
    new_lines = []
    for i in range(len(lines)):
        # surface
        if '$Sur_' in lines[i]:
            for x in range(4):
                for y in range(4):
                    for z in range(13):
                        if '$Sur_'+str(x+1)+'_'+str(y+1)+'_'+str(z+1)+'$,' in lines[i] or '$Sur_'+str(x+1)+'_'+str(y+1)+'_'+str(z+1)+'$;' in lines[i]:
                            new_lines.append(lines[i].replace('$Sur_'+str(x+1)+'_'+str(y+1)+'_'+str(z+1)+'$',
                                             str(X[x])+','+str(Y[y])+','+str(Z[z])))
        # subsurface
        elif '$Sub_' in lines[i]:
            for x in range(4):
                for y in range(4):
                    for z in range(13):
                        if '$Sub_'+str(x+1)+'_'+str(y+1)+'_'+str(z+1)+'$,' in lines[i] or '$Sub_'+str(x+1)+'_'+str(y+1)+'_'+str(z+1)+'$;' in lines[i]:
                            new_lines.append(lines[i].replace('$Sub_'+str(x+1)+'_'+str(y+1)+'_'+str(z+1)+'$',
                                             str(X[x])+','+str(Y[y])+','+str(Z[z])))
        # exterior walls
        elif '$Thick_wall$' in lines[i]:
            new_lines.append(lines[i].replace('$Thick_wall$',str(thick_wall)))
        elif '$Cond_wall$' in lines[i]:
            new_lines.append(lines[i].replace('$Cond_wall$',str(cond_ext_walls)))
        # roof
        elif '$Thick_roof$' in lines[i]:
            new_lines.append(lines[i].replace('$Thick_roof$',str(thick_roof)))
        elif '$Cond_roof$' in lines[i]:
            new_lines.append(lines[i].replace('$Cond_roof$',str(cond_roof)))
        # windows
        elif '$Ufac_wind$' in lines[i]:
            new_lines.append(lines[i].replace('$Ufac_wind$',str(variables[7])))
        elif '$SHGC_wind$' in lines[i]:
            new_lines.append(lines[i].replace('$SHGC_wind$',str(variables[8])))
        # foundation
        elif '$Rval_found$' in lines[i]:
            new_lines.append(lines[i].replace('$Rval_found$',str(rval_foundation)))
        # infiltration rate
        elif '$Inf_rate$' in lines[i]:
            new_lines.append(lines[i].replace('$Inf_rate$',str(variables[10])))
        # BLDG_OCC_SCH
        elif '$BLDG_OCC_SCH$' in lines[i]:
            for line in BLDG_OCC_SCH:
                new_lines.append(line)
        # BLDG_LIGHT_SCH
        elif '$BLDG_LIGHT_SCH$' in lines[i]:
            for line in BLDG_LIGHT_SCH:
                new_lines.append(line)
        # BLDG_EQUIP_SCH
        elif '$BLDG_EQUIP_SCH$' in lines[i]:
            for line in BLDG_EQUIP_SCH:
                new_lines.append(line)
        # INFIL_QUARTER_ON_SCH
        elif '$INFIL_QUARTER_ON_SCH$' in lines[i]:
            for line in INFIL_QUARTER_ON_SCH:
                new_lines.append(line)
        # CLGSETP_SCH
        elif '$CLGSETP_SCH$' in lines[i]:
            for line in CLGSETP_SCH:
                new_lines.append(line)
        # HTGSETP_SCH
        elif '$HTGSETP_SCH$' in lines[i]:
            for line in HTGSETP_SCH:
                new_lines.append(line)
        # HVACOperationSchd
        elif '$HVACOperationSchd$' in lines[i]:
            for line in HVACOperationSchd:
                new_lines.append(line)
        # MinOA_MotorizedDamper_Sched
        elif '$MinOA_MotorizedDamper_Sched$' in lines[i]:
            for line in MinOA_MotorizedDamper_Sched:
                new_lines.append(line)
        # BLDG_SWH_SCH
        elif '$BLDG_SWH_SCH$' in lines[i]:
            for line in BLDG_SWH_SCH:
                new_lines.append(line)
        # people density
        elif '$Peo_dens$' in lines[i]:
            new_lines.append(lines[i].replace('$Peo_dens$',str(variables[15])))
        # lighting power density
        elif '$LPD$' in lines[i]:
            new_lines.append(lines[i].replace('$LPD$',str(variables[16])))
        # electric equipment power density
        elif '$EPD$' in lines[i]:
            new_lines.append(lines[i].replace('$EPD$',str(variables[17])))
        # cooling cop
        elif '$COP$' in lines[i]:
            new_lines.append(lines[i].replace('$COP$',str(variables[18])))
        # burner efficiency
        elif '$Burner_Eff$' in lines[i]:
            new_lines.append(lines[i].replace('$Burner_Eff$',str(variables[19])))
        # fan efficiency
        elif '$Fan_Eff$' in lines[i]:
            new_lines.append(lines[i].replace('$Fan_Eff$',str(variables[20])))
        # outdoor air flow
        elif '$OA_vent$' in lines[i]:
            new_lines.append(lines[i].replace('$OA_vent$',str(variables[21])))
        # swh efficiency
        elif '$SWH_Eff$' in lines[i]:
            new_lines.append(lines[i].replace('$SWH_Eff$',str(variables[22])))
        # Site:Location
        elif '$Site_Loc$' in lines[i]:
            for line in Site_Loc:
                new_lines.append(line)
        # SizingPeriod:DesignDay
        elif '$Size_DD$' in lines[i]:
            for line in Size_DD:
                new_lines.append(line)
        # Site:WaterMainsTemperature
        elif '$Site_WMT$' in lines[i]:
            for line in Site_WMT:
                new_lines.append(line)
        # Site:GroundTemperature:BuildingSurface
        elif '$Site_GT$' in lines[i]:
            for line in Site_GT:
                new_lines.append(line)
        # FuelFactors
        elif '$Fuel_Fac$' in lines[i]:
            for line in Fuel_Fac:
                new_lines.append(line)
        else:
            new_lines.append(lines[i])
        
    # save the new models
    f = open('./'+new_file_name+'.idf','wb')
    for i in range(len(new_lines)):
        f.writelines(new_lines[i])
    f.close()
