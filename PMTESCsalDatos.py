# ********************************************************************************
# POSTPROCESADO ODB PARA ORDENAR NODOS
#este archivo esta prepardo para sacar los datos del control en desplzamientos con RF (reaccion)
#antes he tenido que guardar en el modelo el HISTORY OUTPUT para los nodos que quiera sacar:
#RF1, RF2, U2
# ********************************************************************************

#-------------------------------------------------------
#||||	 IMPORTACION DE MODULOS Y APERTURA DE ODB	||||		   
#-------------------------------------------------------
from os import chdir
from odbAccess import*
from sys import argv

def PMTESCsalDatos_CdesplaDCB(name_files, working_directory, salida_datos3, stepk, stepm, nnodosdamagEne, enertotal, nnodosdamagTen):

    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    
    
    #-------------------------------------------------------
    
    #--------------------------------------------------------------------------
    #|||||||||||||    		 DEFINICION DE VARIABLES            |||||||||||||||
    #--------------------------------------------------------------------------
    # de LEBIMdefplanaFFM tomo:
          # statev(1)=damage
          # statev(2)=noel
          # statev(3)=psig
          # statev(4)=Gtot
          # statev(5)=Gc 
    	  # statev(6)=factor
    key_step = odb.steps.keys()
    key_HisReg = odb.steps[key_step[0]].historyRegions.keys()
    
    
    path_HisRegU21 = odb.steps[key_step[0]].historyRegions[key_HisReg[1]]
    path_HisRegU22 = odb.steps[key_step[0]].historyRegions[key_HisReg[2]]
    
    #---------------------------------------------------
    #||||||| 	   OBTENER RF1, RF2, U1, U2      |||||||
    #---------------------------------------------------
    
    U21 = path_HisRegU21.historyOutputs['U2'].data[1][1]
    U22 = path_HisRegU22.historyOutputs['U2'].data[1][1]
    F21 = path_HisRegU21.historyOutputs['TF2'].data[1][1]
    F22 = path_HisRegU22.historyOutputs['TF2'].data[1][1]
    
    #---------------------------------------------------
    #escribir el fichero de datos
    #--------------------------------------------------
    #chdir(working_directory_Ene) 
    
    fich_salida= open(salida_datos3,'a')
    datos_escri=stepk+'\t'+stepm+'\t'+nnodosdamagTen+'\t'+nnodosdamagEne+'\t'+enertotal+'\t'+str(U21)+'\t'+str(U22)+'\t'+str(F21)+'\t'+str(F22)
    fich_salida.write('\n')
    fich_salida.write(datos_escri)
    fich_salida.close()
    
    odb.close()

