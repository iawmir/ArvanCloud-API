import requests, ast, json
from pick import pick
import pyperclip as pc
from secrets import key

# read first line
headers = {'Authorization' : key}
url = "https://napi.arvancloud.com/ecc/v1/"

regionslist = {}
serverslist = {}

regionsjson = requests.get(url+"regions", headers=headers).json()
for region in regionsjson['data']:
    regionslist[region['code']] = region['dc']

regionsoptions = regionslist.values()
regionscodes = regionslist.keys()

region, index = pick(list(regionsoptions), "Select a Datacenter:")

position = list(regionsoptions).index(region)

regioncode = list(regionscodes)[position]

regionservers = requests.get(url+"regions/"+regioncode+"/servers", headers=headers).json()
for server in regionservers['data']:
    for index in server['addresses']:
        network = server['addresses'][index][0]
        ip = network['addr']
        serverslist[server['id']] = server['name'] + " ,  with ip:  " + ip

serversoptions = serverslist.values()
serversids = serverslist.keys()

server, index = pick(list(serversoptions), "Select a Server:")

position = list(serversoptions).index(server)

serverid = list(serversids)[position]

actionslist = requests.get(url+"regions/"+regioncode+"/servers/"+serverid+"/actions",headers=headers).json()

actions = ["copy ip","reboot","power-on","power-off","hard-reboot","rescue","unrescue","rename","resize","snapshot","reset-root-password","vnc"]

action, index = pick(actions, "Select an Action:")

if action == "copy ip":
    for server in regionservers['data']:
        if server['id'] == serverid:
            for index in server['addresses']:
                network = server['addresses'][index][0]
                ip = network['addr']
                pc.copy(ip)
elif action == "rename":
    actionresponse = requests.post(url+"regions/"+regioncode+"/servers/"+serverid+"/"+action, json={'name': input("New Name: ")}, headers=headers).json()
elif action == "resize":
    flavorslist = requests.get(url+"regions/"+regioncode+"/sizes",headers=headers).json()
    flavors = []
    for flavor in flavorslist['data']: 
        flavordict = {
            flavor['id']: "name " + flavor['name'] + " , disk " + str(flavor['disk'])+" GB " + " , memory " + str(flavor['memory'])+" GB " + " , bandwidth " + str(flavor['bandwidth_in_bytes']/1000000000)+" GB " + " , cpu_count " + str(flavor['cpu_count']) + " , price_per_hour " + str(flavor['price_per_hour'])+"  Rial "
        }
        flavors.append(flavordict)
    flavor, index = pick(flavors, "Select a Flavor:")
    for key, value in flavor.items():
        flavorid = key
    actionresponse = requests.post(url+"regions/"+regioncode+"/servers/"+serverid+"/"+action, json={'name': flavorid}, headers=headers).json()
elif action == "snapshot":
    actionresponse = requests.post(url+"regions/"+regioncode+"/servers/"+serverid+"/"+action, json={'name': input("Snapshot Name: ")}, headers=headers).json()
elif action == "reset-root-password":
    actionresponse = requests.post(url+"regions/"+regioncode+"/servers/"+serverid+"/"+action, headers=headers).json()
elif action == "vnc":
    actionresponse = requests.get(url+"regions/"+regioncode+"/servers/"+serverid+"/"+action, headers=headers).json()
else:
    actionresponse = requests.post(url+"regions/"+regioncode+"/servers/"+serverid+"/"+action, headers=headers).json()

try:
    print(str(actionresponse['data']))
except:
    try:
        print(str(actionresponse['message']))
    except:
        print("Nothing to Show")