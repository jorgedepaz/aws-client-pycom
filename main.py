from MQTTLib import AWSIoTMQTTClient
import time
import config
import ujson
from skills import *
#Pin14 es el push button
global response
from machine import Pin
from machine import RTC
from machine import Timer


# configuracion de cliente MQTT
#Pin('P11').mode(Pin.OUT)
#deepsleepInterrupt = Clock()
SmartLuxMQTTClient = AWSIoTMQTTClient(config.CLIENT_ID)
SmartLuxMQTTClient.configureEndpoint(config.AWS_HOST, config.AWS_PORT)
SmartLuxMQTTClient.configureCredentials(config.AWS_ROOT_CA, config.AWS_PRIVATE_KEY, config.AWS_CLIENT_CERT)

SmartLuxMQTTClient.configureOfflinePublishQueueing(config.OFFLINE_QUEUE_SIZE)
SmartLuxMQTTClient.configureDrainingFrequency(config.DRAINING_FREQ)
SmartLuxMQTTClient.configureConnectDisconnectTimeout(config.CONN_DISCONN_TIMEOUT)
SmartLuxMQTTClient.configureMQTTOperationTimeout(config.MQTT_OPER_TIMEOUT)
SmartLuxMQTTClient.configureLastWill(config.LAST_WILL_TOPIC, config.LAST_WILL_MSG, 1)

#Conectar al host MQTT Host
if SmartLuxMQTTClient.connect():
    print('Conexion AWS exitosa!')

#funcion callback
def funcionCallback(client, userdata, message):
    print("Mensaje recivido: ")
    print(message.payload)
    print("Del topico: ")
    print(message.topic)
    print("--------------\n\n")
    topicoSTRb = str(message.topic)
    topicoSTR = topicoSTRb[2:len(topicoSTRb)-1]
    #ubinascii.hexlify(b'~\xd8\xc6\x00').decode('utf-8')

    try:
        parsed = ujson.loads(message.payload)
        response = diferenciador(parsed)
        resetflag = response["flag"]
        del response["flag"]
        SmartLuxMQTTClient.publish(topicoSTR+'/data', ujson.dumps(response), 1)
        if resetflag == True:
            machine.reset()
    except ValueError:
        info={}
        info["ValueError"] = "Corregir la sintaxis del JSON"
        SmartLuxMQTTClient.publish(topicoSTR+'/data', ujson.dumps(info), 1)
    except TypeError:
        info={}
        info["TypeError"] = "Enviar informacion en formato JSON"
        SmartLuxMQTTClient.publish(topicoSTR+'/data', ujson.dumps(info), 1)
    #except:
    #    info={}
    #    info["NoneType Error"] = "Corregir los datos enviados"
    #    SmartLuxMQTTClient.publish(topicoSTR+'/data', ujson.dumps(info), 1)

# Subscribe to topic
SmartLuxMQTTClient.subscribe(config.TOPIC1, 1, funcionCallback)
#SmartLuxMQTTClient.subscribe(config.TOPIC2, 1, funcionCallback)
chipid=str(ubinascii.hexlify(str(machine.unique_id())))
SmartLuxMQTTClient.publish('SmartLux/usr/thing1/control/data', "Chip OnLine: "+chipid[2:len(chipid)-1], 1)
time.sleep(2)


file = open('/flash/sleepTimes.json', 'r')
parsedx = ujson.load(file)
file.close()

rst=machine.reset_cause()
if rst != 3:
    timeFlag = parsedx['timers']['timeFlag']
    connection_time = parsedx['timers']['connection_time']
    if timeFlag == True:
        alarm2 = Timer.Alarm(seconds_handler, s=connection_time, periodic=False)

if (machine.wake_reason()[0])==2: #RTC timer complete
    print('Despertando zZzZ')
    xx=check()
    if type(xx) is str:
        SmartLuxMQTTClient.publish('SmartLux/usr/thing1/control/data', xx, 1)
    alarms1 = timers("65535")
    #if values["TAlarm"] == True:
        #SmartLuxMQTTClient.publish('SmartLux/usr/thing1/sensors/data', "sobrepaso el nivel de temperatura", 1)
     #this does not restart a new interval!!"""

#clock = Clock()
"""for x in range(3):
    Pin('P11').value(1)
    Pin('P4').value(1)
    Pin('P8').value(1)
    print(1)
    time.sleep(1)
    print(0)
    Pin('P11').value(0)
    Pin('P4').value(0)
    Pin('P8').value(0)
    time.sleep(1)"""
