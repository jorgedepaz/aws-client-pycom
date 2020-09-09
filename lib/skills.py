#Librerira para poder cambiar el comportamiento de la placa dependiendo de los requerimientos.
import machine
import pycom
import time
from machine import Pin
import utime
from deepsleep import DeepSleep
import deepsleep
import config
import ubinascii
import utime
import ujson
from machine import Timer

from network import WLAN
from geoposition import geolocate
from pysense import Pysense
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE
from SI7006A20 import SI7006A20
from LIS2HH12 import LIS2HH12
from LTR329ALS01 import LTR329ALS01
from MQTTLib import AWSIoTMQTTClient
from machine import RTC
#WIFI_SSID = 'jorge-G551JW'
#WIFI_PASS = 'GkQjtoPa'
#f1 = open('/flash/status.json', 'r')
#parsed = ujson.load(f1)
#WIFI_SSID = f1["ssid"]
#WIFI_PASS = f1["pass"]
#f.close()
#WIFI_SSID = 'LA ESQUINA'
#WIFI_PASS = 'LRE01486'
#WIFI_SSID = 'Quetzaltech'
#WIFI_PASS = '@1234@qt'
"""
# Relay conectado al P3 (GPIO4)
actuador = Pin("P3", mode=Pin.OUT)
actuador.value(False)
# Set onboard LED to dim red


def actuador_status(reference):
    if reference == "SW":
        return actuador.value()


def handle_actuation(reference, value):
    if reference == "SW":
        if value is True:
            actuador.value(True)
        else:
            actuador.value(False)
"""
wlan = WLAN(mode=WLAN.STA)

py = Pysense()
si = SI7006A20(py)
mpp = MPL3115A2(py,mode=PRESSURE)
mpp1 = MPL3115A2(py,mode=ALTITUDE)
lt = LTR329ALS01(py)
acc = LIS2HH12()
#para los timers
sleep_time =0
connection_time = 0
timeFlag=False
#tresholds
thresholdTemp = 0
thresholdLux = 0
thresholdHum = 0
thresholdBat = 0
thresholdPress = 0
thresholdAlt = 0

#bandera para cambiar al modo normal
tempFlag = False
luxFlag = False
pressFlag = False
altFlag = False
humedadFlag = False
batteryFlag = False
geoFlag = False
accFlag = False
#aun no
wifiFlag = False
catmFlag = False
blueFlag = False

general ={}
info={}
infoTimers={}
infowifi={}
infoT={}
infoSleep={}
infoL={}
infoH={}
infoP={}
infoA={}
infoB={}
infoRTC = {}
infoConnect = {}
rtc = RTC()
#usuarios = {'Enrique','Jorge','Carlos','Erick'}
#En user los nombres que se manden por alli se guardarn en un array de strings y luego se le daran permisos.

def diferenciador(dictAWS):
    global info
    global infowifi
    global infoSleep
    global tempFlag
    global timeFlag
    global luxFlag
    global pressFlag
    global humedadFlag
    global batteryFlag
    global geoFlag
    global accFlag
    global connectFlag

    info.clear()

    info["flag"] = False

    try:
        if type(dictAWS["temp"]) is str:#Informacion de temperatura
            info["Temp"] = smartTemp(dictAWS["temp"])
    except KeyError:
        pass

    try:
        if type(dictAWS["lux"]) is int:#Informacion de Iluminacion----------------------------------------------------------------
            info["Lux"] = smartLux(dictAWS["lux"])
        elif dictAWS["lux"] == False:
            luxFlag=False
    except KeyError:
        pass


    try:
        if type(dictAWS["acc"]) is int:#Informacion de acelerecion----------------------------------------------------------------
            info["Aceleracion"] = smartAcc(dictAWS["acc"])
        elif dictAWS["acc"] == False:
            accFlag = False
    except KeyError:
        pass


    try:
        if type(dictAWS["hum"]) is str:#Informacion de humedad--------------------------------------------------------------------------------
            info["Humedad"] = smartHum(dictAWS["hum"])
    except KeyError:
        pass


    try:
        if type(dictAWS["press"]) is str:#Informacion de presion------------------------------------------------------------------------------
            info["Presion"] = smartPres(dictAWS["press"])
    except KeyError:
        pass

    try:
        if type(dictAWS["alt"]) is str:#Informacion de presion------------------------------------------------------------------------------
            info["Altura"] = smartAlt(dictAWS["alt"])
    except KeyError:
        pass


    try:
        if type(dictAWS["bat"]) is str:
            info["Battery"] = smartBat(dictAWS["bat"])
        elif dictAWS["bat"] == False:
            batFlag = False
    except KeyError:
        pass


    try:
        if dictAWS["geo"] == True:#Informacion de Iluminacion
            info["Geo"] = geo(dictAWS["geo"])
        elif dictAWS["geo"] == False:
            geoFlag = False
    except KeyError:
        pass


    try:
        if type(dictAWS["connect"]) is dict:#escoger conexiones
            info["Conexiones"] = connects(dictAWS["connect"])
            info["flag"] = True #bandera para que se reinicie el sistema
        elif dictAWS["connect"] == False:
            connectFlag=False
            info["flag"] = False
    except KeyError:
        pass


    try:
        if type(dictAWS["timers"]) is str:#escoger conexiones
            info["Timers"] = timers(dictAWS["timers"])


    except KeyError:
        pass


    try:
        if dictAWS["status"] == True:#informacion general del sistema
            info["Status"] = statusPycom(dictAWS["status"])
        elif dictAWS["status"] == False:
            statusFlag = False
    except KeyError:
        pass

    return(info)

def check():
    #importacion de flags
    global tempFlag
    global luxFlag
    global pressFlag
    global altFlag
    global humedadFlag
    global batteryFlag
    global geoFlag
    global accFlag

    global thresholdTemp
    global thresholdLux
    global thresholdHum
    global thresholdBat
    global thresholdPress
    global thresholdAlt


    values = {}

    fnx = open('/flash/status.json','r')
    dataset = ujson.load(fnx)
    fnx.close()


    if type(dataset['Status']['Sensores']['Temperatura']) is dict:                                  #Temperatura
        thresholdTemp = dataset['Status']['Sensores']['Temperatura']['Threshold']
        tempFlag = dataset['Status']['Sensores']['Temperatura']['Activo']
        if tempFlag == True and si.temperature() > thresholdTemp:
            WARNING = "Sobrepaso el limite de temperatura, temperatura actual: "+str(si.temperature())+" >"+" Limite"+str(thresholdTemp)
            return(WARNING)

    if type(dataset['Status']['Sensores']['Humedad']) is dict:                                  #Humedad
        thresholdHum = dataset['Status']['Sensores']['Humedad']['Threshold']
        humedadFlag = dataset['Status']['Sensores']['Humedad']['Activo']
        if humedadFlag == True and si.humidity() > thresholdHum:
            WARNING = "Sobrepaso el limite de humedad, humedad actual: "+str(si.humidity())+" >"+" Limite"+str(thresholdHum)
            return(WARNING)

    if type(dataset['Status']['Sensores']['Presion']) is dict:                                  #Humedad
        thresholdPress = dataset['Status']['Sensores']['Presion']['Threshold']
        pressFlag = dataset['Status']['Sensores']['Presion']['Activo']
        if pressFlag == True and mpp.pressure() > thresholdPress:
            WARNING = "Sobrepaso el limite de Presion, Presion actual: "+str(mpp.pressure())+" >"+" Limite "+str(thresholdPress)
            return(WARNING)

    if type(dataset['Status']['Sensores']['Altura']) is dict:                                  #Humedad
        thresholdAlt = dataset['Status']['Sensores']['Altura']['Threshold']
        altFlag = dataset['Status']['Sensores']['Altura']['Activo']
        if altFlag == True and mpp1.altitude() > thresholdAlt:
            WARNING = "Sobrepaso el limite de Altura, Altura actual: "+str(mpp1.altitude())+" >"+" Limite "+str(thresholdAlt)
            return(WARNING)

    if type(dataset['Status']['Nivel de bateria']) is dict:                                  #Humedad
        thresholdBat = dataset['Status']['Nivel de bateria']['Threshold']
        batteryFlag = dataset['Status']['Nivel de bateria']['Activo']
        if batteryFlag == True and int((100*py.read_battery_voltage())/5) < thresholdBat:
            WARNING = "Sobrepaso el limite de carga en la bateria, porcentaje actual: "+str(mpp1.altitude())+" >"+" Limite "+str(thresholdBat)
            return(WARNING)





def seconds_handler(alarm):
    global connection_time
    global timeFlag

    file = open('/flash/sleepTimes.json', 'r')
    parsedx = ujson.load(file)
    file.close()
    timeFlag = parsedx['timers']['timeFlag']
    connection_time = parsedx['timers']['connection_time']
    sleep_time = parsedx['timers']['sleep_time']
    if timeFlag == False:
        print("Alarma desactivada")
        alarm.cancel()
    elif timeFlag == True:
        print("Pasaron: " +str(connection_time)+" segundos")
        machine.deepsleep(sleep_time*1000)

#Para lectura de datos
def timers(data):

    global sleep_time
    global connection_time
    global timeFlag
    global infoTimers
    infoTimers.clear()

    x = open('/flash/sleepTimes.json', 'r')
    parsed = ujson.load(x)
    x.close()

    timeFlag = parsed['timers']['timeFlag']
    connection_time = parsed['timers']['connection_time']
    sleep_time = parsed['timers']['sleep_time']

    data=data.split(",")
    print(data)
    if data[0] == "65535":
        connection_time=int(connection_time)
        if timeFlag == False:
            alarm = Timer.Alarm(seconds_handler, s=1, periodic=False)
        if timeFlag == True:
            alarm2 = Timer.Alarm(seconds_handler, s=connection_time, periodic=False)

    if len(data)<=1:
        if int(data[0]) == 0:#Para desactivar el sensor
            timeFlag = False
            infoTimers["Activo"] = timeFlag
            parsed['timers']['timeFlag'] = timeFlag
            x2 = open('/flash/sleepTimes.json', 'w')
            x2.write(ujson.dumps(parsed))
            x2.close()
            if timeFlag == False:
                alarm = Timer.Alarm(seconds_handler, s=4, periodic=False)

        elif int(data[0]) == 1:#Unicamente para saber cual es el valor actual
            infoTimers["State"] = "DeepSleep time: " + str(parsed['timers']['sleep_time'])+"S"+" Connection time: "+str(parsed['timers']['connection_time'])+"S"
            infoTimers["Activo"] = timeFlag
        elif int(data[0]) != 1 or int(data[0]) != 0: #Devuelve un error por cualquier otro valor diferente de 1 ó 0
            infoTimers["Error"] = "Comando invalido"

    if len(data)<4 and len(data) > 1:
        if int(data[0]) == 2 and int(data[1]) < 80 and int(data[2]) < 80: #preguntar por los limites en segundos para esta fase

            timeFlag = True
            connection_time = int(data[1])
            sleep_time = int(data[2])

            infoTimers["Activo"] = timeFlag
            infoTimers["Threshold"] = "El dispositivo despertara a cada : " + str(sleep_time)+"s "+" y estara conectado por "+str(connection_time)+"s"


            file = open('/flash/status.json', 'r')
            parsedx = ujson.load(file)
            parsedx['Status']['Timers'] = infoTimers #verificar siempre el json para que no hayan problemas

            file.close()

            file2 = open('/flash/status.json', 'w')
            file2.write(ujson.dumps(parsedx))
            file2.close()
        #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            fq = open('/flash/sleepTimes.json','r')
            parsedd = ujson.load(fq)
            parsedd['timers']['connection_time']= connection_time
            parsedd['timers']['sleep_time']=sleep_time
            parsedd['timers']['timeFlag']=timeFlag
            fq.close()

            fil2 = open('/flash/sleepTimes.json', 'w')
            fil2.write(ujson.dumps(parsedd))
            fil2.close()

        ##--------------------------------------- nuevo codigo de aqui para arriba
            if timeFlag == True:
                alarm2 = Timer.Alarm(seconds_handler, s=connection_time, periodic=False)#-----------------------------------------------------> PROBLEMA AQUI, NO ENTRA A LA FUNCION PARA INICIAR A CONTAR
               #alarm = Timer.Alarm(seconds_handler, s=4, periodic=False)
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        else:
            infoTimers["Error"] = "Utilize el numero 2 para actvar la alarma y revise que este bajo el limite de 80℃"


    return infoTimers
    #-------------------------------------------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>---------------------------->>>>>>>>>>>>>>>>>>>>---------------------

def smartTemp(data):
    temperatura = si.temperature()
    global thresholdTemp
    global tempFlag
    global infoT
    infoT.clear()
    data=data.split(",")
    if len(data)<=1:
        if int(data[0]) == 0:#Para desactivar el sensor
            tempFlag = False
            infoT["Activo"] = tempFlag

            x = open('/flash/status.json', 'r')
            parsed = ujson.load(x)
            parsed['Status']['Sensores']['Temperatura'] = tempFlag #verificar siempre el json para que no hayan problemas
            x.close()

            x2 = open('/flash/status.json', 'w')
            x2.write(ujson.dumps(parsed))
            x2.close()

        elif int(data[0]) == 1:#Unicamente para saber cual es el valor actual
            infoT["State"] = "temperatura actual " + str(temperatura)+"℃"
            infoT["Activo"] = tempFlag
        elif int(data[0]) != 1 or int(data[0]) != 0: #Devuelve un error por cualquier otro valor diferente de 1 ó 0
            infoT["Error"] = "Comando invalido"

    if len(data)<3 and len(data) > 1:
        if int(data[0]) == 2 and int(data[1]) < 80:
            tempFlag = True
            thresholdTemp = int(data[1])
            infoT["Activo"] = tempFlag
            infoT["Threshold"] = thresholdTemp
            infoT["State"] = "temperatura actual " + str(temperatura)+"℃"

            file = open('/flash/status.json', 'r')
            parsed = ujson.load(file)
            parsed['Status']['Sensores']['Temperatura'] = infoT #verificar siempre el json para que no hayan problemas
            file.close()

            file2 = open('/flash/status.json', 'w')
            file2.write(ujson.dumps(parsed))
            file2.close()

        else:
            infoT["Error"] = "Utilize el numero 2 para actvar la alarma y revise que este bajo el limite de 80℃"

    print(infoT)
    return infoT


def smartLux(threshold):
    lux = lt.light()
    global thresholdLux
    global luxFlag
    global infoL
    thresholdLux = threshold
    luxFlag = True
    infoL["Lux"] = luxFlag
    infoL["Threshold"] = "La alarma se disparara al sobrepasar " + str(threshold)+"lux"
    infoL["State"] = "Iluminacion ambiental Blue,Red" + str(lux)
    return(infoL)


def smartAcc(data):
    pass


def smartHum(data):
    humedad = si.humidity()
    global humedadFlag
    global infoH
    global thresholdHum
    infoH.clear()
    data=data.split(",")
    if len(data)<=1:
        if int(data[0]) == 0:#Para desactivar el sensor
            humedadFlag = False
            infoH["Activo"] = humedadFlag

            x = open('/flash/status.json', 'r')
            parsed = ujson.load(x)
            parsed['Status']['Sensores']['Humedad'] = humedadFlag #verificar siempre el json para que no hayan problemas
            x.close()

            x2 = open('/flash/status.json', 'w')
            x2.write(ujson.dumps(parsed))
            x2.close()
        elif int(data[0]) == 1:#Unicamente para saber cual es el valor actual
            infoH["State"] = "La humedad actual " + str(humedad)+"%"
            infoH["Activo"] = humedadFlag
        elif int(data[0]) != 1 or int(data[0]) != 0: #Devuelve un error por cualquier otro valor diferente de 1 ó 0
            infoH["Error"] = "Comando invalido"

    if len(data)<3 and len(data) > 1:
        if int(data[0]) == 2 and int(data[1]) <= 100:
            humedadFlag = True
            thresholdHum = int(data[1])
            infoH["Activo"] = humedadFlag
            infoH["Threshold"] = thresholdHum
            infoH["State"] = "Humedad actual: " + str(humedad)+"%"

            #print(infoT)#hasta aqui todo bien
            file = open('/flash/status.json', 'r')
            parsed = ujson.load(file)
            parsed['Status']['Sensores']['Humedad'] = infoH #verificar siempre el json para que no hayan problemas
            file.close()

            file2 = open('/flash/status.json', 'w')
            file2.write(ujson.dumps(parsed))
            file2.close()

        else:
            infoH["Error"] = "Utilize el numero 2 para actvar la alarma y revise que el valor de humedad este bajo el limite del 100%"

    print(infoH)
    return infoH


def smartPres(data):#---------------------------------------------------------alarmas y demas revisar codigo
    global pressFlag
    global infoP
    global thresholdPress

    presion = mpp.pressure()
    infoP.clear()
    data=data.split(",")

    if len(data)<=1:
        if int(data[0]) == 0:#Para desactivar el sensor
            pressFlag = False
            infoP["Activo"] = pressFlag

            x = open('/flash/status.json', 'r')
            parsed = ujson.load(x)
            parsed['Status']['Sensores']['Presion'] = pressFlag #verificar siempre el json para que no hayan problemas
            x.close()

            x2 = open('/flash/status.json', 'w')
            x2.write(ujson.dumps(parsed))
            x2.close()

        elif int(data[0]) == 1:#Unicamente para saber cual es el valor actual
            infoP["State"] =  "Presion actual: " + str(presion)+"Pa"
            infoP["Activo"] = pressFlag
        elif int(data[0]) != 1 or int(data[0]) != 0: #Devuelve un error por cualquier otro valor diferente de 1 ó 0
            infoP["Error"] = "Comando invalido"

    if len(data)<3 and len(data) > 1:
        if int(data[0]) == 2 and int(data[1]) <= 20000:
            pressFlag = True
            thresholdPress = int(data[1])
            infoP["State"] =  "Presion actual: " + str(presion)+" Pa"
            infoP["Activo"] = pressFlag
            infoP["Threshold"] = thresholdPress

            file = open('/flash/status.json', 'r')
            parsed = ujson.load(file)
            parsed['Status']['Sensores']['Presion'] = infoP #verificar siempre el json para que no hayan problemas
            file.close()

            file2 = open('/flash/status.json', 'w')
            file2.write(ujson.dumps(parsed))
            file2.close()
        else:
            infoP["Error"] = "Utilize el numero 2 para actvar la alarma y revise que el valor de la presion este bajo el limite de 2000"

    print(infoP)
    return infoP

def smartAlt(data):#--------fil-------------------------------------------------alarmas y demas revisar codigo
    global altFlag
    global infoA
    global thresholdAlt

    altitud = mpp1.altitude()
    infoA.clear()
    data=data.split(",")

    if len(data)<=1:
        if int(data[0]) == 0:#Para desactivar el sensor
            altFlag = False
            infoA["Activo"] = altFlag

            x = open('/flash/status.json', 'r')
            parsed = ujson.load(x)
            parsed['Status']['Sensores']['Altura'] = altFlag #verificar siempre el json para que no hayan problemas
            x.close()

            x2 = open('/flash/status.json', 'w')
            x2.write(ujson.dumps(parsed))
            x2.close()

        elif int(data[0]) == 1:#Unicamente para saber cual es el valor actual
            infoA["State"] =  "Altura actual: " + str(altitud)+" Mts"
            infoA["Activo"] = altFlag
        elif int(data[0]) != 1 or int(data[0]) != 0: #Devuelve un error por cualquier otro valor diferente de 1 ó 0
            infoA["Error"] = "Comando invalido"

    if len(data)<3 and len(data) > 1:
        if int(data[0]) == 2 and int(data[1]) <= 20000:
            altFlag = True
            thresholdAlt = int(data[1])
            infoA["State"] =  "Altura actual: " + str(altitud)+" Mts"
            infoA["Activo"] = altFlag
            infoA["Threshold"] = thresholdAlt

            file = open('/flash/status.json', 'r')
            parsed = ujson.load(file)
            parsed['Status']['Sensores']['Altura'] = infoA #verificar siempre el json para que no hayan problemas
            file.close()

            file2 = open('/flash/status.json', 'w')
            file2.write(ujson.dumps(parsed))
            file2.close()
        else:
            infoA["Error"] = "Utilize el numero 2 para actvar la alarma y revise que el valor de altitud este bajo el limite del 2000mts"

    print(infoA)
    return infoA


def smartBat(data):
    global batteryFlag
    global infoB
    infoB.clear()
    data=data.split(",")

    if len(data)<=1:
        if int(data[0]) == 0:#Para desactivar el sensor
            batteryFlag = False
            #infoB["Activo"] = altFlag

            x = open('/flash/status.json', 'r')
            parsed = ujson.load(x)
            parsed['Status']['Nivel de bateria'] = altFlag #verificar siempre el json para que no hayan problemas
            x.close()

            x2 = open('/flash/status.json', 'w')
            x2.write(ujson.dumps(parsed))
            x2.close()

        elif int(data[0]) == 1:#Unicamente para saber cual es el valor actual
            infoB["State"] =  "Porcentaje de carga "+str(int((100*py.read_battery_voltage())/5))+"%"
            infoB["Activo"] = altFlag
        elif int(data[0]) != 1 or int(data[0]) != 0: #Devuelve un error por cualquier otro valor diferente de 1 ó 0
            infoB["Error"] = "Comando invalido"

    if len(data)<3 and len(data) > 1:
        if int(data[0]) == 2 and int(data[1]) <= 100:
            batteryFlag = True
            thresholdBat = int(data[1])
            infoB["State"] =  "Porcentaje de carga "+str(int((100*py.read_battery_voltage())/5))+"%"
            infoB["Activo"] = batteryFlag
            infoB["Threshold"] = thresholdBat
            file = open('/flash/status.json', 'r')
            parsed = ujson.load(file)
            parsed['Status']['Nivel de bateria'] = infoB #verificar siempre el json para que no hayan problemas
            file.close()

            file2 = open('/flash/status.json', 'w')
            file2.write(ujson.dumps(parsed))
            file2.close()
        else:
            infoA["Error"] = "Utilize el numero 2 para actvar la alarma y revise que el valor limite de la bateria este bajo 100%"

    print(infoB)
    return infoB

def geo(data):
    global geoFlag
    global infowifi
    geoFlag = True
    geo_locate = geolocate(config.GOOGLE_API_KEY, infowifi["ssid"])
    valid, location = geo_locate.get_location()
    if(valid):
        location["geo"] = geoFlag
        return(location)

def connects(credentials):
    global wifiFlag
    global catmFlag
    global blueFlag
    global infoConnect
    global infowifi
    global wlan
    wifi = {}
    wlan.init(antenna=WLAN.INT_ANT)
    infowifi = credentials["wifi"]
    print(infowifi)

    if infowifi["source"] == "boot":
        wlan.connect(infowifi["ssid"], auth=(None, infowifi["pass"]), timeout=5000)
        while not wlan.isconnected():
            time.sleep(0.5)
        print("Conexion a "+infowifi["ssid"]+" exitosa!")

        wifistat = open('/flash/status.json', 'r')
        parsedwifi = ujson.load(wifistat)
        wifistat.close()

        wifidata= wlan.ifconfig()
        wifi["Ip"]= wifidata[0]
        wifi["SubnetMask"]= wifidata[1]
        wifi["Gateway"]= wifidata[2]
        wifi["DNS"]= wifidata[3]

        parsedwifi['Status']['Conectividad']['Wifi'] =  wifi

        f = open('/flash/status.json', 'w')
        f.write(ujson.dumps(parsedwifi))
        f.close()
        horario()

    elif infowifi["source"] == "aws":#----------------------------------------------------------------asdfasdfasdfasdfasdf
        wlan.connect(infowifi["ssid"], auth=(None, infowifi["pass"]), timeout=5000)
        while not wlan.isconnected():
            time.sleep(0.5)
        f = open('/flash/wifi.json', 'w')
        f.write(ujson.dumps(infowifi))
        f.close()
        wifistat = open('/flash/status.json', 'r')
        parsedwifi = ujson.load(wifistat)
        wifistat.close()

        wifidata= wlan.ifconfig()
        wifi["Ip"]= wifidata[0]
        wifi["SubnetMask"]= wifidata[1]
        wifi["Gateway"]= wifidata[2]
        wifi["DNS"]= wifidata[3]

        parsedwifi['Status']['Conectividad']['Wifi'] =  wifi

        f = open('/flash/status.json', 'w')
        f.write(ujson.dumps(parsedwifi))
        f.close()

        print("Conexion a "+infowifi["ssid"]+" exitosa!")

def horario():
    global rtc
    rtc.ntp_sync("time1.google.com")
    utime.sleep_ms(750)
    timenow = {}
    timestat = open('/flash/status.json', 'r')
    parsedTime = ujson.load(timestat)
    timestat.close()

    timedata = rtc.now()
    timenow["Year"]= timedata[0]
    timenow["Month"]= timedata[1]
    timenow["Day"]= timedata[2]
    timenow["Hour"]= timedata[3]
    timenow["Minute"]= timedata[4]
    timenow["Second"]= timedata[5]
    timenow["Microsecond"]= timedata[6]

    parsedTime['Status']['Horario UTC'] =  timenow

    f = open('/flash/status.json', 'w')
    f.write(ujson.dumps(parsedTime))
    f.close()

    print('\nRTC Seteado desde NTP a UTC:', str(parsedTime['Status']['Horario UTC']))

def statusPycom(data):
    STAT = open('/flash/status.json', 'r')
    parsedSTAT = ujson.load(STAT)
    STAT.close()
    return(parsedSTAT)
