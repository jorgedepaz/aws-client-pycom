# wifi configuration
#WIFI_SSID = 'test'
#WIFI_PASS = 'pycomtest'
#WIFI_SSID = 'jorge-G551JW'
#WIFI_PASS = 'GkQjtoPa'
#WIFI_SSID = 'Honeypot'
#WIFI_PASS = 'LAS0LUCI0N7'
#WIFI_SSID = 'LA ESQUINA'
#WIFI_PASS = 'LRE01486'
#WIFI_SSID = 'Quetzaltech'
#WIFI_PASS = '@1234@qt'
#Valores para consumir la api de google

GOOGLE_API_KEY = "AIzaSyDnLXkQsyZhFUbXd5MrcV6vgJTyqguJ9XQ"

#AWS configuracion general
AWS_PORT = 8883
AWS_HOST = 'a1srqknzalh35-ats.iot.us-west-2.amazonaws.com'
AWS_ROOT_CA = '/flash/cert/AmazonRootCA1.pem'
AWS_CLIENT_CERT = '/flash/cert/7f7d87ee91-certificate.pem.crt'
AWS_PRIVATE_KEY = '/flash/cert/7f7d87ee91-private.pem.key'

################## Subscribe / Publish client #################
CLIENT_ID = 'Smartlight'
#TOPIC = 'SmartLux/aws/jorge/thing1/+/data'
TOPIC = 'SmartLux/usr'
TOPIC1 = 'SmartLux/usr/thing1/control'
#TOPIC2 = 'SmartLux/usr/thing1/actuators'



#TOPIC = '$SmartLux/aws/jorge/things/sensor/function'
#TOPIC = '$aws/things/pycom_cat_m_2/shadow/update'
OFFLINE_QUEUE_SIZE = -1
DRAINING_FREQ = 2
CONN_DISCONN_TIMEOUT = 10
MQTT_OPER_TIMEOUT = 5
#LAST_WILL_TOPIC = 'PublishTopic'
LAST_WILL_TOPIC = '$aws/things/pycom_cat_m_2/shadow/update'
#LAST_WILL_TOPIC = 'SmartLux/usr/thing1/sensors/data'
LAST_WILL_MSG = 'To All: Acabo de morir :c'

####################### Shadow updater ########################
#THING_NAME = "my thing name"
#CLIENT_ID = "ShadowUpdater"
#CONN_DISCONN_TIMEOUT = 10
#MQTT_OPER_TIMEOUT = 5

####################### Delta Listener ########################
#THING_NAME = "my thing name"
#CLIENT_ID = "DeltaListener"
#CONN_DISCONN_TIMEOUT = 10
#MQTT_OPER_TIMEOUT = 5

####################### Shadow Echo ########################
#THING_NAME = "my thing name"
#CLIENT_ID = "ShadowEcho"
#CONN_DISCONN_TIMEOUT = 10
#MQTT_OPER_TIMEOUT = 5
