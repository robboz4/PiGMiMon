# Pi Garage Monitor via Internet Monitor (PiGMiMon)
# It will run and check for a status change in the garage doors (open->close)
# If it is set to ACTIVE it will email and/or sms message the change.
# If in PASSIVE mode, it will monitor the change and log any to a file.
# 
# Based on code from Adafruit Pi Learning
# 
# Leverage logging code from Halloween project ( recycling!)
# Completed as part of PiGMi garage door project with Tom Milner ( tomkmiler.org)
# Leveraged code from:
# https://github.com/realpython/python-scripts/blob/master/27_send_sms.py
# https://github.com/kennethreitz/requests 
# High level description of what should be in the code below:

# Set up pins, email address, sms address, open log file
# current_status = Read door status
# old_status = current _status
# Read file for mode ( active/passive )
# set status
# While true loop...
#   current_status = read door status
#   if current_status == old_status then do set flag "we don't know" False
#   else
#   if Armed 
#     if flag set that "we don't know" 
#       send messages and log
#       set flag "that we know" True
#   sleep

# The active/passive mode and logging is tied into the PiGMi website 8/6/16
# Some code straightening  and comment removal needed before putting into github
# Added email function to open/close connetcion rather than leaving it active 8/16/16
# Added config() to read email and pin settings from the web server config. 9/14/16
# Changed Mail_Message to use the Google email for both email and SMS. Changed config
# routing so that email must be configured properly for both sms and email. However,
# email only can be sent with sms. 9/22/16
# Integrating new config data from My-Garage. The setting of mode is now done through the 
# config file, so no extra file is needed. Also streamlined door*_name for ease of reporting.
# Tested on a Pi Zero that did not have any hardware connected to the GPIO pins. 9/26/16
# Made cleaner variables for config changes 2/10/16
import requests
import time
import RPi.GPIO as io
import os
import sys
import smtplib                       # Email  
import urllib                        # Email sending
import xml.etree.ElementTree as ET   # For xml parsing

# End of Imports

#Set up email & sms

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

fromaddr = ""    # Add email sender account here
toaddr = ""          # Add email recipient here
msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "PiGMi Alarm"      # Customize Subject here

body = "Garage Door Alarm!   "       # This is over written
msg.attach(MIMEText(body, 'plain'))
a_pass = ""                         # Need pass code for login account


# Change message for your set up
message = "Check page,( robboz4.no-ip.org:86/PiGMi ) email or logfile for more information."

# Change for correct URL

No_Email = True
No_SMS = True
io.setmode(io.BCM)
 

door1_pin = 00    # Reed switch input. Must match the PiGMi pin numbers!!!
door2_pin = 00    # Set up for my 3 garage doors
door3_pin = 00    # Comment out for fewer doors.
door1_status_cur = 1
door2_status_cur = 1
door3_status_cur = 1
door1_status_old = 1
door2_status_old = 1
door3_status_old = 1
Door_alarm = False
Door1 = "Closed"  #Assuming default state for doors.
Door2 = "Closed"
Door3 = "Closed" 
door_name1 = ""
door_name2 = ""
door_name3 = ""
Door1_Present = False
Door2_Present = False
Door3_Present = False
# BELOW ARE FILE LOCATIONS AND SERVIVE PROVIDERS YOU MAY NEED TO CHANGE FOR YOUR SETUP.
# Set Config file default is /var/www/html/config/garage.xml
config_file = "/var/www/PiGMi/config/garage.xml" 

# Set Log file default is 
log_file_path =  "http://localhost:86/PiGMi/logm.php?"  # Set correct pathp"

# Modify line 241 if yu sue a different email server than gmail.
# Modify liine 254 if using a different service to send sms.
# Set up tick count and active/passive status

Log_update_tick = 0
Armed = False
Armed_text = ""

def Config():		# read Config data from XML file of PiGMi
        
        global config_file


        tree = ET.parse(config_file )  # Set correct path
        root = tree.getroot()
        Door_list = [] # List of doors and pins.

#       Using lots of  globals
        global number
        global toaddr
        global fromaddr
        global a_pass
        global door1_pin
        global door2_pin
        global door3_pin
        global No_Email
        global No_SMS
        global door1_name
        global door2_name
        global door3_name
        global Alarm_text
        global Armed
        global Door1_Present
        global Door2_Present
        global Door3_Present

        MyLog("Reading Configuration.")

        for monitor in root.findall("monitor"):
               Alarm_text = monitor.find("monitor-state").text
               Alarm_message = "Monitor mode is:  " + Alarm_text
               if Alarm_text== "Active":
                      Armed = True
               MyLog(Alarm_message)
               
               email = monitor.find("monitor-email").text
               if email is None:
                     email = ""
                     MyLog("No recipient Email Address configured.")
                     No_Email = True
               else:
                     toaddr = email
                     account_info = "Sending email to " + toaddr
                     MyLog(account_info)
                     No_Email = False

               sms = monitor.find("monitor-sms").text
               if sms is None:
                     sms = ""
                     MyLog("No SMS Number configured.")
                     No_SMS = True
               else:
		     number = sms
                     sms_info = "SMS number is " + number
                     MyLog(sms_info)
                     No_SMS = False


               account = monitor.find("email-from-account").text
               if account is None:
                     account = ""
                     MyLog("No Eail Sender User account.")
                     No_Email = True
               else:
                     lhs, rhs  = account.split("@")
                     fromaddr = account
                     account_info = "Using account " + lhs + " at " + rhs
                     MyLog(account_info)
                     No_Email = False

               apass = monitor.find("email-from-passwd").text

               if apass  is None :
                     apass = ""
                     MyLog("No Email Password.")
                     No_Email = True
               else: 
                    a_pass = apass
                    account_info = "Using passcode " + a_pass
#                    MyLog(account_info)
                    No_EMail = False

               for door in root.findall("door"):
                     doorname  = door.find("doorname").text
                     if doorname is None :
                               doorname = "None"
                               PinR = 0
                               PinM = 0
                     else:
                               PinR = door.find("gpio-pinR").text
                               PinM = door.find("gpio-pinM").text


                     Door_list.append(doorname)
                     Door_list.append(PinR)
                     Door_list.append(PinM)
# extract magnetic switch config. There are a maximum of 9 entries (0-8)
# Door_name, relay_pin, magnet_pin. We need 3rd, 6th and 9th entired of the
# list. Door_list[2],Door_list[5], Door_list [8]...
        if Door_list[0] != "None":
            Door1_Present = True
            door1_pin = int(Door_list[2])
            door1_name = Door_list[0]
#        MyLog(door1_name)
        
        if Door_list[3] != "None":
            Door2_Present = True
            door2_pin = int(Door_list[5])    
            door2_name = Door_list[3]
        
        if Door_list[6] !="None":
            Door3_Present = True
            door3_pin = int(Door_list[8])
            door3_name = Door_list[6]    
        
# End of configuration for magnetic switch pins, email accounts and addresses and SMS.



def Mail_Message(Message, Method):      # Mail sender function 
	
        global fromaddr
        global a_pass
        global toaddr
        global number

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        lhs, rhs = fromaddr.split("@")
#        print lhs, a_pass, fromaddr
        server.login(lhs, a_pass)
#        print Message
#        print Method
        body = Message
        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string()
        if Method == "sms":
           toaddr = number + "@text.att.net"   # Set to correct provider

           r = server.sendmail(fromaddr, toaddr, text)

           
        else:
           r = server.sendmail(fromaddr, toaddr, text)
        server.close()
        return(r)

# End of Mail_Message() function

def Get_Mode():                  # Getting Mode setting

         global Armed
         global Armed_text
         cur_mode = Armed
         tree = ET.parse(config_file)          

         root = tree.getroot()


         for monitor in root.findall("monitor"):
              Monitor_Mode = monitor.find("monitor-state").text
#              Alarm_message = " Monitor mode is:  " + Monitor_Mode
#              MyLog(Alarm_message)

         if Monitor_Mode == "Active":
               Armed = True
               Armed_text = "Mode is active."
               if cur_mode != Armed:
	        	MyLog("Mode Change to Active.")

         if Monitor_Mode == "Passive":
               Armed = False
               Armed_text = "Mode is passive."
               if cur_mode != Armed:
	        	MyLog ("Mode changed to Passive.")


# End of Get_Mode() Function         

def MyLog(logData):                       # New Logging  function
                                          # Write to PiGMi log file which can easily be read via the web.
                                          # URL will need customizing for port number and web location
          log_args = { 'msg' : logData }
          encoded_args = urllib.urlencode(log_args)


          url = log_file_path + encoded_args  # Set correct path


          url_junk = urllib.urlopen(url)


# End of My_Log() function
        






def Door_Status():                       # Get Door status routine, 
                                         # reads IO pins and sets the status.

                # global Door_alarm
                global body
                global door1_status_cur
                global door2_status_cur 
                global door3_status_cur
                global door1_status_old
                global door2_status_old
                global door3_status_old
                global door1_name
                global door2_name
                global door3_name
                global Door1_Present
                global Door2_Present
                global Door3_Present
           
                if Door1_Present == True:
                   door1_status_cur = io.input(door1_pin)
		   print(door1_name + " " + str(door1_status_cur) + "; old = " + str(door1_status_old) + "\n")
#               print("Door 1 cur = " + str(door1_status_cur) + "; old = " + str(door1_status_old) + "\n")
                if Door2_Present == True:
                   door2_status_cur = io.input(door2_pin)
                   print(door2_name + " " + str(door2_status_cur) + "; old = "  + str(door2_status_old) + "\n")
		if Door3_Present == True:
                   door3_status_cur = io.input(door3_pin)
		   print(door3_name + " " + str(door3_status_cur) + "; old = " + str(door3_status_old) + "\n")
		if Door1_Present == True:
                   if door1_status_cur != door1_status_old:
			
			door1_status_old = door1_status_cur

                        body = door1_name + " is active. "
                        msg.attach(MIMEText(body, 'plain'))
                        MyLog(body)
			return(True)
		if Door2_Present == True:	
		  if door2_status_cur != door2_status_old:
			
                        print("Alarm Door 2 cur = " + str(door2_status_cur) + "; old = "  + str(door2_status_old) + "\n")
			door2_status_old = door2_status_cur
                        body = door2_name + " is active. " 
                        msg.attach(MIMEText(body, 'plain'))
                        MyLog(body)
                        return(True)

		if Door3_Present == True:	
		  if door3_status_cur != door3_status_old:
			
			door3_status_old = door3_status_cur
                        body = door3_name + " is active. "
                        msg.attach(MIMEText(body, 'plain'))
                        MyLog(body)
			return(True)
		return(False)	
			
# End of Door_Status() function			
			
# Initial set up
# Get_Mode()
HeaderText = "Monitor  started." 
MyLog(HeaderText)
Config()

if Door1_Present == True:
	io.setup(door1_pin, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
        door1_status_old = io.input(door1_pin)
if Door2_Present == True:
        io.setup(door2_pin, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
        door2_status_old = io.input(door2_pin)
if Door3_Present == True:
        io.setup(door3_pin, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
        door3_status_old = io.input(door3_pin)



# MyLog(Armed_text)

if Door1_Present == True:
   if (io.input(door1_pin) == 1):
	Door1 = "Open"
        Initial_state = door1_name + " "  + Door1 + " Monitoring Pin: " + str(door1_pin)
        MyLog(Initial_state)
   else:	
        Initial_state = door1_name +" " + Door1 + " Monitoring Pin: " + str(door1_pin)
        MyLog(Initial_state)

if Door2_Present == True:
   if (io.input(door2_pin) == 1):
        Door2 = "Open"
        Initial_state = door2_name + " " + Door2 + " Monitoring Pin: " + str(door2_pin)
        MyLog(Initial_state)

   else:
        Initial_state = door2_name +" " + Door2 + " Monitoring Pin: " + str(door2_pin)
        MyLog(Initial_state)
if Door3_Present == True:
   if (io.input(door3_pin) == 1):
        Door3 = "Open"
        Initial_state = door3_name + " " + Door3 + " Monitoring Pin: " + str(door3_pin)
        MyLog(Initial_state)

   else:
        Initial_state = door3_name + " " + Door3  + " Monitoring Pin: " + str(door3_pin)
        MyLog(Initial_state)


Door_alarm = Door_Status() 


# Main Loop========================

while True:

    Get_Mode()          # Get mode Active/Passive	
    Door_alarm = Door_Status()       # Get Door status
    if Door_alarm == True:
        print("Alarm True")
        if Armed == True:
            if No_Email == False:
               method = "email"
               print("DOOR ALARM! Sending email alert")
               text = " Alarm at " + time.asctime( time.localtime(time.time()) ) + "..."
               r = Mail_Message(text, method)
               MyLog("Monitor sending email: Status below.")
               MyLog(r)
               
            else:
               MyLog("Email not configured, cannot send message.")
            if No_SMS == False:
               if No_Email == False:
                  method = "sms"
                  r = Mail_Message(message, method)
                  MyLog("Monitor is sending SMS: Status below.")
                  MyLog(r)
            else:
               MyLog("SMS or Email not configured, cannot send SMS message.")
        else:
            MyLog("In Passive mode no message sent.")
        Door_alarm = False
        Log_update_tick = 0
    else:

        if Log_update_tick > 59:
            MyLog("No Status Change in 60 minutes. " + Armed_text) 
            Log_update_tick = 0

        Door_alarm = False 
        Log_update_tick += 1
        print("Log tick = " + str(Log_update_tick) + "\n")

    time.sleep(60)

    print("ending timing loop  "+ str(Door_alarm) +"\n")
    Door_alarm= False
# End of while loop
