import modelCreate as mc
import subprocess
import pandas as pd
import os

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

# variables: 0. total floor area, 1. aspect ratio, 2. window-to-wall ratio,
# 3. glazing sill height, 4. floor-to-floor height, 5. insulated R-value of exterior walls,
# 6. insulated R-value of roof, 7. U-factor of windows, 8. shgc of windows, 9. insulated R-value of foundation,
# 10. infiltration rate, 11. start time other, 12. end time other, 13. start time hvac,
# 14. end time hvac, 15. people density, 16. lighting power density, 17. electric equipment power density,
# 18. cooling cop, 19. burner efficiency, 20. fan efficiency, 21. outdoor air flow, 22. swh efficiency
total_floor_area = 3130
aspect_ratio = 2.01
wwr = 0.275
glazing_sill_height = 1.02
floor_to_floor_height = 4.47
rval_ext_wall = [[0.77,0.77,0.77,0.78,0.77,0.79,0.99,0.96,1.01,1.13,1.09,1.22,1.22,1.30,1.41],
                 [0.32,1.17,0.73,1.36,1.10,1.36,1.98,1.76,1.92,2.15,2.15,2.71,2.44,3.04,3.91]]
rval_roof = [[1.76,1.76,1.76,1.76,1.76,1.76,2.04,1.98,2.07,2.50,2.37,2.99,2.99,2.93,2.99],
             [2.38,2.67,3.83,2.44,3.66,2.00,3.03,2.99,2.75,3.38,3.51,3.97,3.65,4.41,5.75]]
ufac_window = [[5.84,5.84,5.84,5.84,5.84,5.84,5.84,5.84,5.84,3.53,3.53,3.53,3.53,3.53,3.53],
               [5.84,5.84,5.84,4.09,5.84,4.09,3.35,4.09,4.09,3.35,3.35,2.96,2.96,2.96,2.96]]
shgc_window = [[0.54,0.54,0.54,0.54,0.54,0.54,0.54,0.54,0.54,0.41,0.41,0.41,0.41,0.41,0.41],
               [0.25,0.25,0.25,0.26,0.25,0.39,0.36,0.36,0.39,0.39,0.39,0.39,0.39,0.49,0.62]]
rval_foundation = 0.54
inf_rate = 0.0002677
start_time_other = 8.0
end_time_other = 18.0
start_time_hvac = 7.0
end_time_hvac = 19.0
people_density = 46.87
lpd = 19.4
epd = 9.77
cooling_cop = [2.52,2.71]
burner_eff = [0.7,0.78]
fan_eff = [0.48,0.56]
oa_flow = 0.02609869
swh_eff = [0.78,0.8]

vintage = ['Pre1980','Post1980']
climate = ['1A','2A','2B','3A','3B','3C','4A','4B','4C','5A','5B','6A','6B','7','8']

for i in range(2):# vintage
    for j in range(15):# climate
        variables = [total_floor_area,aspect_ratio,wwr,glazing_sill_height,floor_to_floor_height,
                     rval_ext_wall[i][j],rval_roof[i][j],ufac_window[i][j],shgc_window[i][j],
                     rval_foundation,inf_rate,start_time_other,end_time_other,start_time_hvac,
                     end_time_hvac,people_density,lpd,epd,cooling_cop[i],burner_eff[i],
                     fan_eff[i],oa_flow,swh_eff[i]]
        
        file_name = 'RefBldgMediumOffice'
        file_name_sch = 'schedule'
        climate_name = climate[j]
        
        # create baseline models
        mc.modelCreate(file_name,file_name_sch,file_name+'_'+vintage[i]+'_'+climate[j],variables,climate_name)
        
        # run models
        subprocess.call(['C:\EnergyPlusV8-6-0\energyplus.exe', '-w', './climate/'+climate_name+'_2003.epw',
                         '-d', './baseline', '-p', file_name+'_'+vintage[i]+'_'+climate[j], 
                         './baseline/'+file_name+'_'+vintage[i]+'_'+climate[j]+'.idf'])
        
        # collect simulation data
        data = collectInformation('./baseline/'+file_name+'_'+vintage[i]+'_'+climate[j]+'tbl.htm')
        
        line = vintage[i]+','+climate[j]
        for x in data:
            line += ','
            line += str(x)
        line += '\n'
        
        # record simulation data
        if not os.path.isfile('baseline_result.csv'):
            title = 'vintage,climate,site_EUI,elec_EUI,ng_EUI,heat_elec_EUI,cool_elec_EUI,int_lig_elec_EUI,ext_lig_elec_EUI,int_eqp_elec_EUI,fan_elec_EUI,pump_elec_EUI,water_elec_EUI,heat_ng_EUI,water_ng_EUI\n'
            f = open('baseline_result.csv','ab')
            f.writelines(title)
            f.close()
        f = open('baseline_result.csv','ab')
        f.writelines(line)
        f.close()
        
        