# ********************************************************************************
# POSTPROCESADO ODB PARA ORDENAR NODOS

# ********************************************************************************

#-------------------------------------------------------
#||||	 IMPORTACION DE MODULOS Y APERTURA DE ODB	||||		   
#-------------------------------------------------------
from os import chdir,path,mkdir
from shutil import move, rmtree
from odbAccess import*
from  math import sqrt #para raiz cuadrada
from pickle import dump, load
from copy import deepcopy
#import numpy as np

#argvF simula los argv reales que habra


def PMTESCcriTen(name_files, working_directory, setnodeInt, dicc_NeL_T):
    
    working_directory_Ten=working_directory+'/FFM_optimizada01/criterioTen'
    chdir(working_directory)
    odb = openOdb(name_files + '.odb')
    Eset=setnodeInt
    dicc_NeL=deepcopy(dicc_NeL_T)
    
    #working_directory='D:\OneDrive - UNIVERSIDAD DE SEVILLA\PMTE_SC_POSTDOC\PMTE-SC UNIONES\PMTE_V16_WIN_CASA\FFM_optimizada01\odbS'
    #working_directory_Ten='D:\OneDrive - UNIVERSIDAD DE SEVILLA\PMTE_SC_POSTDOC\PMTE-SC UNIONES\PMTE_V16_WIN_CASA\FFM_optimizada01\criterioTen'
    #chdir(working_directory)
    #odb = openOdb('D:\OneDrive - UNIVERSIDAD DE SEVILLA\PMTE_SC_POSTDOC\PMTE-SC UNIONES\PMTE_V16_WIN_CASA\FFM_optimizada01\odbS\DLJCARGA_k3m1n0j0.odb')
    #Eset='EINTERFACE'
    
    #%%
    #-------------------------------------------------------
    #abrimos los 3 archivos del dagno para prepara los inicios del criterio energetico
    #Fichero del dano anterior k-1 
    archivoKm1=open(working_directory_Ten+'/damageKm1.txt','w')
    #Fichero del dano actual k para N1 todo sano 
    archivoN1=open(working_directory_Ten+'/damageN1.txt','w') 
    #Fichero del dano actual k para N2 todo dagnado 
    archivoN2=open(working_directory_Ten+'/damageN2.txt','w')
    #Fichero del dano actual k para N3 todo dagnado con ecuacion 
    archivoN3=open(working_directory_Ten+'/damageN3.txt','w')
    listarchivos=[archivoKm1,archivoN1,archivoN2,archivoN3]
    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    archDamTen=open(working_directory_Ten+'/damageTen.txt','w')
    #%%
    #--------------------------------------------------------------------------
    #|||||||||||||    		 DEFINICION DE VARIABLES            |||||||||||||||
    #--------------------------------------------------------------------------
    InterElementSet = odb.rootAssembly.elementSets[Eset]
    key_step = odb.steps.keys()
      
    key_step = odb.steps.keys()
    path_SDV1=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV1'].\
    	getSubset(region=InterElementSet).values
    path_SDV2=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV2'].\
    	getSubset(region=InterElementSet).values
    #path_SDV3=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV3'].\
    	#getSubset(region=InterElementSet).values
    path_SDV4=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    	getSubset(region=InterElementSet).values 
    path_SDV5=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV5'].\
    	getSubset(region=InterElementSet).values 
    path_SDV6=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV6'].\
    	getSubset(region=InterElementSet).values 
    path_SDV10=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV10'].\
    	getSubset(region=InterElementSet).values 
    path_SDV11=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV11'].\
    	getSubset(region=InterElementSet).values
    	
       
    area=odb.steps[key_step[0]].frames[-1].fieldOutputs['EVOL'].\
    	getSubset(region=InterElementSet).values
    	
      
    #path_SDV4_C=odb.steps[key_step[0]].frames[-1].fieldOutputs['SDV4'].\
    #    getSubset(position=CENTROID).values
    	
    #%%    
    #--------------------------------------------------------------------------
    #funciones N
    #---------------------------------------------------       
    def n1(dist,longitud):
    	z=1.00 #nada roto
    	return z
    def n2(dist,longitud):
    	z=0.00 #todo roto
    	return z
    def n3(dist,longitud):
    	try:
    		z=1.-(1./longitud)*dist
    	except ZeroDivisionError:
    		1.
    	return z
    
    listafunN=[n1,n2,n3]
    
    #%%   
    #-----------------------------------------------------------------------------------------------------------------------
    #numero de puntos de integracion y de elmentos en la interfase
    #-----------------------------------------------------------------------------------------------------------------------
    intpoint=len(path_SDV2)
    elementos=len(area)
    #damageKm1=[]
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #creacion de diccionario 
    #-----------------------------------------------------------------------------------------------------------------------
    #diccionario donde la clave sea el NeL y los datos una lista con:
    #0='NeL',1='NeG',2='area',3='x',4='y',5='distacia origen',6='GtotT'
    #7='GcT',8='GcE', 9='factor de carga', 10='suma de PI'
    #el diccionario vacio lo hago una sola vez y lo cargo el resto de veces
    
    
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ahora recorro todos los puntos de integracion de la interfase para sacar las variables de la lista de antes
    #y meterla en el diccionario
    #ademas meto en una lista los PI rotos para despues escribirlos en los archivos
    #si finalmente hay algun elmento dagnado
    #-----------------------------------------------------------------------------------------------------------------------
    dagnokm1=[]
    for k in range(intpoint): 
    	damage=path_SDV1[k].data
    	GtotT=path_SDV4[k].data #la G en cada punto de integracion del criterio tensional 
    	GcT=path_SDV5[k].data #la Gc del criterio tensional del criterio tensional 
    	ip=path_SDV2[k].integrationPoint
    	NeG=path_SDV2[k].data
    	if damage!=0.00: #and GtotT>=GcT: #damage=0 yes damage by CT. Hemos quitado la restrinccion de romper PI a PI
    		NeL=path_SDV2[k].elementLabel
    		NeL2=str(path_SDV2[k].elementLabel)+'_'+str(path_SDV2[k].instance.name)
    		GcE=path_SDV6[k].data #la Gc del criterio tensional del criterio energetico 
    		x=path_SDV10[k].data
    		y=path_SDV11[k].data
    		#saco el area de cada elemento dividida entre 4
    		#porque al ser cada elemento cuadrado y tener 4 puntos de integracion
    		#la integral en el elemento de las funciones (tensiones, deformaciones, energias...) en cada elemento 
    		#es la suma de los 4 valores de la funcion por el area total del elemento entre 4
    		#ya que el coeficiente de ponderacion es 1 en cada PI. Pagina 27 de mi Vazquez
    		#si quiero la integral en elemento sumo cada PI y lo multiplico todo por el jacobElm
    		#si quiero el valor en su CDG lo deberia dividir por el Area total
    		jacobElm=dicc_NeL[NeL2][2]/4   
    		#fcip=sqrt(GtotT/GcT)  
    		#fcelm=fcip*jacobElm     
    		#sumo el valor de cada PI dividido por 4 del factor de carga segun el CT 
    		#y de las coordandas x e y porque es como multiplicar por jacobElm y despues dividir todo 
    		#entre en Area total. Porque quiero el valor en el CDG, no la suma sobre todo el elemento.
    		dicc_NeL[NeL2][1]=int(NeG)
    		dicc_NeL[NeL2][3]=dicc_NeL[NeL2][3]+x/4.0
    		dicc_NeL[NeL2][4]=dicc_NeL[NeL2][4]+y/4.0
    		#sumo el valor de cada PI de todas las energias multiplicado por
    		#el jacobiano=Area total del elemento/4
    		dicc_NeL[NeL2][6]=dicc_NeL[NeL2][6]+GtotT*jacobElm
    		dicc_NeL[NeL2][7]=dicc_NeL[NeL2][7]+GcT*jacobElm
    		dicc_NeL[NeL2][8]=dicc_NeL[NeL2][8]+GcE*jacobElm
    		#sumo los puntos de integracion que cumplen el criterio tensional dentro de un elemento	
    		dicc_NeL[NeL2][10]=dicc_NeL[NeL2][10]+ip
    	if damage==0.00: #damage=0 yes damage
    		#guardo en una lis los PI rotos para despues escribrir en archivos 
    		#si finalmente hay algun elemento dagnado
    		dagnokm1.append([ip,NeG,damage])
    #        for n in range(len(listarchivos)):
    			#listarchivos[n].write('%d %d %e \n' % (ip,NeG,damage))
    			
    #-----------------------------------------------------------------------------------------------------------------------
    #para guardar desde abaqus y porder abrir en pyhton y hacer pruebas
    #correr en abaqus
    #filedicc=open(working_directory_Ten+'/dicc_NeL.pkl','wb')    
    #dump(dicc_NeL,filedicc)
    #filedicc.close()
    #correr en python         
    #filedicc=open(working_directory_Ten+'/dicc_NeL.pkl','rb')
    #dicc_NeL=load(filedicc)
    #filedicc.close()
    			
    #%%            
    #-----------------------------------------------------------------------------------------------------------------------
    #convierto en lista los valores del diccionario que he creado
    #y posteriormente en un array porque es mas rapido
    #-----------------------------------------------------------------------------------------------------------------------
    listaElem=list(dicc_NeL.values())
    # esto no hace falta si no obligamos a que rompan todos los PI por CT
    # listaElem.sort(key=lambda listaElem:listaElem[10],reverse=True)
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #hago una nuev lista con los elementos dagnados dameleCT=[]
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT=[]
    # Este bucle es para almacenar el dagno si queremos obligar a romper por CT todos los PI
    # for elem in range(elementos):
    	# if listaElem[elem][10]<10:
    		# break
    	# else:
    		# #fc=sqrt(GtotT/GcT)
    		# listaElem[elem][9]=sqrt(listaElem[elem][6]/listaElem[elem][7]) 
    		# dameleCT.append(listaElem[elem])
    
    # Este bucle es para almacenar el dagno si queremos obligar a romper por CT todos los PI
    for elem in range(elementos):
    	if listaElem[elem][6]>listaElem[elem][7] and listaElem[elem][10]==10:
    		listaElem[elem][9]=sqrt(listaElem[elem][6]/listaElem[elem][7])
    		dameleCT.append(listaElem[elem])
    		#dameleCT es una lista de cada elemento dagnado con toda la informacion 
    		#que tiene el diccionario dicc_NeL de ese elemento
    		
    	
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenos los elementos por su factor de dagno 
    #-----------------------------------------------------------------------------------------------------------------------
    dameleCT.sort(key=lambda dameleCT:dameleCT[9],reverse=True)
    
    for elem in range(len(dameleCT)):  
    	xa=dameleCT[0][3]
    	xb=dameleCT[elem][3]
    	ya=dameleCT[0][4]
    	yb=dameleCT[elem][4]
    	dist=sqrt(((xa-xb)**2)+((ya-yb)**2))
    	dameleCT[elem][5]=dist
    	
    #%%    
    #-----------------------------------------------------------------------------------------------------------------------
    #ordenos los elementos de mor distancia desde el elemento de facto de dagno mayor
    #-----------------------------------------------------------------------------------------------------------------------
    #dameleCT.sort(key=lambda dameleCT:dameleCT[5],reverse=False)
    
    #el parametro longitud NO SE MUY BIEN como jugar con el 
    #hay que tener cuidado porque si no hay elementos dagnados devuelve un error
    #y si solo hay un elemento da error la funcion n3
    if len(dameleCT)>1:
    	longitud=dameleCT[-1][5]
    else:
    	longitud=1.0
    
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #agnado los nuevos elemntos dagnado con su z segun  n1,n2,n3
    #escribo el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    #-----------------------------------------------------------------------------------------------------------------------
    #escribo en todos los archivo Ns y en Km1 el dagno de km1
    if len(dameleCT)!=0:
    	for n in range(len(listarchivos)):
    		for elem in dagnokm1:
    			listarchivos[n].write('%d %d %e \n' 
    						% (elem[0],elem[1],elem[2]))
    #escribo los nuevos danos del criterio tensional       
    for n in range(len(listafunN)):
    	for elem in range(len(dameleCT)):  
    		if n+1<3:
    			damage=listafunN[n](dameleCT[elem][5],longitud)
    		else:
    			if elem+1 <= len(dameleCT)*0.5:
    				damage=0
    			else:
    				damage=1
    		dameleCT[elem].append(damage)
    		NeG=dameleCT[elem][1]
    		for ip in range(1,5):
    			listarchivos[n+1].write('%d %d %e \n' % (ip,NeG,damage))
    #cierro archivos  
    for n in range(len(listarchivos)):
    	listarchivos[n].close()	
    	
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    #y abro el archivo damageTen.txt donde aparecen los siguientes datos de los
    #elementos dagnados
    #NeG, NeL, GcE del elemento, zN1, zN2, zN3
    #-----------------------------------------------------------------------------------------------------------------------    
    
    # with open('log_criTen.txt', 'w') as f:
    #     #f.write(str(dagnokm1[0]))
    #     f.write(str('prueba'))
    #     f.write('\n')
    #     f.write(str(dameleCT[0]))
    #     f.write('\n')
    #     f.write(str(dameleCT[0][9]))
    #     f.write('\n')
    #     f.write(str(dameleCT))
    #     f.write('\n')
    #     f.write(str(dagnokm1))
    #     f.write('\n')
    #     f.write(str(listaElem[0][0]))
    #     f.write(str(listaElem[0][9]))
    #     f.write('\n')
    #     f.write(str(range(len(dameleCT))))
    #     f.write(str(len(dameleCT)))
    
    damageTen=[]
    for elem in range(len(dameleCT)):
    		archDamTen.write('%d %s %e'
    		% (dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]))			
    		damageTen.append([dameleCT[elem][1],dameleCT[elem][0],dameleCT[elem][8]])
    		
    		for n in range(len(listafunN)):   
    			archDamTen.write(' %e' % (dameleCT[elem][11+n]))
    			damageTen[elem].append(dameleCT[elem][11+n])
    		archDamTen.write('\n')
    archDamTen.close()
    #%%
    #-----------------------------------------------------------------------------------------------------------------------
    odb.close() 
    return damageTen