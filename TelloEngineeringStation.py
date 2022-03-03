import subprocess
import time
import tkinter as tk
from functools import partial

from tkmacosx import Button
from djitellopy import TelloSwarm, tello
import ipaddress
from subprocess import Popen, PIPE
import netifaces as ni

master = tk.Tk()
master.title("Tello drone engineering station")
master.geometry("1000x700")

# Level 1 layout
# Two LabelFrame in a column

swarmConfiguration = tk.LabelFrame(master, text="Swarm configuration",  width=900, height=400 )
swarmConfiguration.grid(row=0,column=0, padx=20)
swarmConfiguration.grid_propagate(0)

swarmOperation = tk.LabelFrame(master, text="Swarm management", width=900, height=200 )
swarmOperation.grid(row=1,column=0, columnspan = 2, padx=20)
swarmOperation.grid_propagate(0)


# Level 2 layouts
####  swarmConfiguration frame
# Two LabelFrame and a button in a row

searchTelloFrame = tk.LabelFrame(swarmConfiguration, text="Search Tellos",  width=300, height=300)
searchTelloFrame.grid (row=0, column=0, padx=20, pady=20)
searchTelloFrame.grid_propagate(0)

swarmCompositionFrame = tk.LabelFrame(swarmConfiguration, text="Swarm composition",width=300, height=300)
swarmCompositionFrame.grid (row=0, column=1, padx=20, pady=20)
swarmCompositionFrame.grid_propagate(0)

def Ping (drone):
    global tellosInAPMode
    # do something to identify the drone in the swarm
    drone.takeoff()
    drone.land()



def CreateSwarmButtonClicked ():
    global tellosInAPMode
    global swarm
    swarm = TelloSwarm.fromIps(tellosInAPMode)
    swarm.connect()
    i=0

    # add to the table of drons in the swarm the battery level and a button for ping the drone
    for drone in swarm:
        battery = drone.get_battery()
        if battery < 30:
            color ='red'
        elif battery < 60:
            color = 'orange'
        else:
            color = 'green'
        batt_lab1 = tk.Label(swarmFrame, text=drone.get_battery(), width=10, justify='left', fg=color, bg='white')
        batt_lab1.grid(row=i + 2, column=1)
        b = Button(swarmFrame, text="ping", width=50, bg='red', fg="white",
                   command=partial(Ping, drone))
        b.grid(row=i + 2, column=2)
        i=i+1


createSwarmButton = Button(swarmConfiguration, text="Create swarm", width = 150, height = 150, bg='green', fg="white", command = CreateSwarmButtonClicked)
createSwarmButton.grid (row=0, column=3, padx=20, pady=10)


####  swarmOperation frame
# Four buttons in a row

def Demo1ButtonClicked():
    swarm.takeoff()
    swarm.move_up(30)
    swarm.parallel (lambda i, drone: drone.move_forward (25))
    swarm.parallel(lambda i, drone: drone.rotate_counter_clockwise(180))
    swarm.parallel(lambda i, drone: drone.move_forward(25))
    swarm.parallel(lambda i, drone: drone.flip_forward())
    swarm.land()

demo1Button = Button(swarmOperation, text="Demo 1", width = 150, bg='green', fg="white", command = Demo1ButtonClicked)
demo1Button.grid (row=0, column=0, padx=20, pady=20)


def Demo2ButtonClicked():
    # to be defined
    pass

demo2Button = Button(swarmOperation, text="Demo 2", width = 150, bg='green', fg="white", command = Demo2ButtonClicked)
demo2Button.grid (row=0, column=1, padx=20, pady=20)

def Demo3ButtonClicked():
    # to be defined
    pass

demo3Button = Button(swarmOperation, text="Demo 3", width = 150, bg='green', fg="white", command = Demo3ButtonClicked)
demo3Button.grid (row=0, column=2, padx=20, pady=20)

def Demo4ButtonClicked():
    # to be defined
    pass

demo4Button = Button(swarmOperation, text="Demo 4", width = 150, bg='green', fg="white", command = Demo4ButtonClicked)
demo4Button.grid (row=0, column=3, padx=20, pady=20)


# Level 3 layouts
#### searchTelloFrame
# A button and a frame containing a table, in a column


def PutAPMode (n):
    global tellos
    selectedDrone = tellos[n - 1]
    print('AP mode for ', selectedDrone)


    # connect to selected drone
    result = subprocess.run(["networksetup", "-setairportnetwork", "en0", selectedDrone, selectedDrone])
    time.sleep(2)
    me = tello.Tello()
    me.connect()
    # put the drone in AP mode, and give it the credentials of the router
    ssid = "TP-Link_E10A"
    contraseña = "73136620"
    me.connect_to_wifi(ssid, contraseña)



    # Remove the drone from the list of drones in station mode
    tellos = [drone for drone in tellos if drone != selectedDrone]

    # clear the table
    for widget in tellosFrame.winfo_children():
        widget.destroy()
    # build the table again

    heading_name = tk.Label(tellosFrame, text='TELLOS', width=10, justify='left', fg='green', bg='white')
    heading_name.grid(row=0, column=0, columnspan = 2)

    for i in range(0, len(tellos)):
        name_lab1 = tk.Label(tellosFrame, text=tellos[i], width=10, justify='left', bg='white')
        name_lab1.grid(row=i + 1, column=0)
        b = Button(tellosFrame, text="put in AP mode", width=150, bg='red', fg="white", command=partial(PutAPMode, i + 1))
        b.grid(row=i + 1, column=1)


def SearchTelloButtonClicked():
    global tellos
    global tellosFrame
    # search tellos in station mode
    scan_cmd = subprocess.Popen(['airport', '-s'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    scan_out, scan_err = scan_cmd.communicate()
    scan_out_lines = str(scan_out).split("\\n")[1:-1]
    tellos = []
    for each_line in scan_out_lines:
        split_line = [e for e in each_line.split(" ") if e != ""]
        if 'TELLO' in split_line[0]:
            tellos.append(split_line[0])

    # include drones in the table (label to identify drone and button to put it in AP mode
    for i in range(0, len(tellos)):
        name_lab1 = tk.Label(tellosFrame, text=tellos[i], width=10, justify='left', bg='white')
        name_lab1.grid(row=i + 1, column=0)
        b = Button(tellosFrame, text="put in AP mode", width=150, bg='red', fg="white", command=partial(PutAPMode, i + 1))
        b.grid(row=i + 1, column=1)

searchTelloButton = Button(searchTelloFrame, text="Search tellos in station mode", width = 250, bg='green', fg="white", command = SearchTelloButtonClicked)
searchTelloButton.grid (row=0, column=0, padx=20, pady=10)



tellosFrame = tk.Frame (searchTelloFrame, width=100, height=100)
# create heading for the tellos table
tk.Label(tellosFrame, text='Tellos', width=10, justify='left', fg='green', bg='white').grid (row=1, column=0)
tellosFrame.grid (row=1, column = 0, padx=20, pady=20)



### swarmCompositionFrame

# A button and a frame with a table, in a row


def SearchAPModeButtonClicked ():
    global tellosInAPMode
    global swarmFrame

    # clear the table of drones in AP mode
    for widget in swarmFrame.winfo_children():
        widget.destroy()


    # search devices connected to the router
    tellosInAPMode = []
    ip_net = ipaddress.ip_network(u'192.168.0.1/24', strict=False)

    # Loop through the connected hosts
    for ip in ip_net.hosts():

        # Convert the ip to a string so it can be used in the ping method
        ip = str(ip)
        # drones will have an ip starting wit the form 192.168.0.11X
        if '192.168.0.11' in ip:
            # Let's ping the IP to see if it's online
            toping = Popen(['ping', '-c', '1', '-W', '50', ip], stdout=PIPE)
            output = toping.communicate()[0]
            hostalive = toping.returncode

            # Print whether or not device is online
            if hostalive == 0:
                print(ip, "is online")
                tellosInAPMode.append((ip))

    # remove from the list my laptop, that is also connected to the router
    ni.ifaddresses('en0')
    myip = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']
    tellosInAPMode = [ip for ip in tellosInAPMode if ip != myip]
    print('IP of tellos in AP mode ', tellosInAPMode)

    # create the table of tellos in AP mode (IP and battery level)
    heading = tk.Label(swarmFrame, text='IPs', width=10, justify='left', fg='green', bg='white')
    heading.grid(row=1, column=0)
    heading2 = tk.Label(swarmFrame, text='Bat', width=10, justify='left', fg='green', bg='white')
    heading2.grid(row=1, column=1)

    # by the moment we only know the ip
    for i in range(0, len(tellosInAPMode)):
        name_lab1 = tk.Label(swarmFrame, text=tellosInAPMode[i], width=10, justify='left', bg='white')
        name_lab1.grid(row=i + 2, column=0)


connectRouterButton = Button(swarmCompositionFrame, text="Searh TELLOs in AP mode", width = 250, bg='green', fg="white", command = SearchAPModeButtonClicked)
connectRouterButton.grid (row=0, column=0, columnspan = 3, padx=20, pady=10)


swarmFrame = tk.Frame (swarmCompositionFrame, width=200, height=400)
# create headings (ip and battery level)
tk.Label(swarmFrame, text='IPs', width=10, justify='left', fg='green', bg='white').grid (row=1, column=0)
tk.Label(swarmFrame, text='Bat', width=10, justify='left', fg='green', bg='white').grid(row=1, column=1)
swarmFrame.grid (row=1, column = 0, padx=20, pady=20)



master.mainloop()