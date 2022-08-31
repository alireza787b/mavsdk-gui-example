import asyncio
from tkinter import *
from turtle import home
from async_tkinter_loop import async_handler, async_mainloop
from mavsdk import *
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)
import time
import webbrowser

drone = System()
lastPacketTime=time.time()-10
def hyperLink(url):
    webbrowser.open_new(url)

async def setup():
    """
    General configurations, setups, and connections are done here.
    :return:
    """

    await drone.connect(system_address="udp://:"+portIn.get())

    printPxh("Waiting for drone to connect...")
    global state
    global lastPacketTime
    global health

    async for state in drone.core.connection_state():
        lastPacketTime=time.time()
        if state.is_connected:
            printPxh(f"-- Connected to drone!")
            break

    
    asyncio.ensure_future(checkTelem())
    asyncio.ensure_future(print_health(drone))
    asyncio.ensure_future(print_position(drone))

    
    printPxh("Waiting for drone to have a global position estimate...")
    
    while True:
        await print_health(drone)
        if health.is_global_position_ok and health.is_home_position_ok:
            printPxh("-- Global position estimate OK")
            break
        
        
async def checkTelem():
    global lastPacketTime 
    while True:
        #printPxh(str(time.time()))
        #printPxh(str(time.time() - lastPacketTime))
        if (time.time() - lastPacketTime) > 1 :
            linkTextObj.config(fg="red")
        else:
            linkTextObj.config(fg="green")
        await asyncio.sleep(3)

async def disarm():
    printPxh("DisArming...")
    await drone.action.disarm()
    
    
async def shutdown():
    printPxh("Shutting Down the Drone")
    await drone.action.shutdown()
 
    
async def testArm():
    printPxh("-- Arming")
    await drone.action.arm()           
    await asyncio.sleep(5)
    printPxh("-- DisArming")
    await drone.action.disarm()
    
async def takeoff(alt=10):
    printPxh("-- Initializing")
    printPxh("-- Arming")
    await drone.action.arm()
    printPxh("-- Taking off")
    await drone.action.set_takeoff_altitude(int(altIn.get()))
    await drone.action.takeoff()


async def land():
    printPxh("-- Landing")
    altIn.delete(0,END)
    altIn.insert(0,0)
    await drone.action.land()

def printPxh(msg=""):
    pxhOut.insert(END, msg + '\n')
    print(msg)
    pxhOut.see("end")


async def print_health(drone):
        defColor = portLabelObj.cget("fg")
        async for health in drone.telemetry.health():
            #printPxh(f"Health: {health}")
            if health.is_gyrometer_calibration_ok & health.is_accelerometer_calibration_ok & health.is_magnetometer_calibration_ok :
               ahrsTextObj.config(fg="green") 
               
            if health.is_local_position_ok & health.is_global_position_ok & health.is_home_position_ok :
               posTextObj.config(fg="green") 
        
            if health.is_armable:
               armTextObj.config(fg="green") 
            global lastPacketTime   
            lastPacketTime=time.time()


async def print_position(drone):
    global position
    async for position in drone.telemetry.position():
        #printPxh("Position: "+position)
        altText.delete(1.0,"end")
        altText.insert(1.0, str(round(position.relative_altitude_m,1)) + " for "+altIn.get()+" m")
        global lastPacketTime 
        lastPacketTime=time.time()
        pass    

root = Tk()
root.geometry("700x550")
root.title("PX4 MAVSDK GUI Example")

labelPortText=StringVar()
labelPortText.set("Receiving Port: ")
portLabelObj=Label(root, textvariable=labelPortText, height=4)
portLabelObj.grid(row=1,column=1,rowspan=1,columnspan=1)

defPort = StringVar(root, value='14540')
portIn = Entry(root, textvariable=defPort)
portIn.grid(row=1,column=2,rowspan=1,columnspan=1)



Button(root, text="Connect", command=async_handler(setup)).grid(row=1,column=2,rowspan=2)


posTextStr=StringVar()
posTextStr.set("NAV")
posTextObj=Label(root, textvariable=posTextStr, height=1)
posTextObj.grid(row=2,column=1,rowspan=1,columnspan=1)
posTextObj.config(fg= "red")

ahrsTextStr=StringVar()
ahrsTextStr.set("AHRS")
ahrsTextObj=Label(root, textvariable=ahrsTextStr, height=1)
ahrsTextObj.grid(row=2,column=2,rowspan=1,columnspan=1)
ahrsTextObj.config(fg= "red")


linkTextStr=StringVar()
linkTextStr.set("LINK")
linkTextObj=Label(root, textvariable=linkTextStr, height=1)
linkTextObj.grid(row=3,column=1,rowspan=1,columnspan=1)
linkTextObj.config(fg= "red")

armTextStr=StringVar()
armTextStr.set("READY")
armTextObj=Label(root, textvariable=armTextStr, height=1)
armTextObj.grid(row=3,column=2,rowspan=1,columnspan=1)
armTextObj.config(fg= "red")



labelAltInText=StringVar()
labelAltInText.set("Desired Altitude: ")
labelAltInObj=Label(root, textvariable=labelAltInText, height=4)
labelAltInObj.grid(row=2,column=3,rowspan=1,columnspan=1)

defAlt = StringVar(root, value='5')
altIn = Entry(root, textvariable=defAlt)
altIn.grid(row=2,column=4,rowspan=1,columnspan=1)
Button(root, text="Take-Off", command=async_handler(takeoff),width=30).grid(row=3,column=3,rowspan=1,columnspan=2)
Button(root, text="Land Current Position", command=async_handler(land),width=30).grid(row=8,column=3,columnspan=2)

labelAltText=StringVar()
labelAltText.set("Altitude AGL ")
altLabel=Label(root, textvariable=labelAltText, height=4)
altLabel.grid(row=8,column=1,rowspan=1)

altText = Text(root, height=2, width=30)
altText.grid(row=8,column=2,rowspan=1)
altText.insert(END,"0 for 0 m")


pxhOut = Text(
    root,
    height=20,
    width=100
)
pxhOut.grid(row=12,column=1,columnspan=4)
pxhOut.insert(END,"Drone state will be shown here..."+ '\n')
# pxhOut.config(state=DISABLED)


linkFooter = StringVar()
linkFooter.set("Alireza Ghaderi - GitHub: Alireza787b")

footerLink = Label( root, fg="green", cursor="hand2" ,textvariable=linkFooter )

footerLink.bind("<Button-1>", lambda e: hyperLink("https://github.com/alireza787b/mavsdk-gui-example"))
footerLink.grid(row=17,column=0,columnspan=20)


async_mainloop(root)