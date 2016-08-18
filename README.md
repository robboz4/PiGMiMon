# PiGMiMon
Monitor code to be used with PiGMi

This is the monitor code that can be armed by the PiGMi settings page. It is configured to run and check the status of the 
doors every minute. If no change is detetcted it will keep looping and post a 60 minute no change message to the PiGMi log
file. If there is a  change and it is in passive mode, it will log the door in the PiGMi log file and reset the 60 minute 
counter. If it is active it will send an email and sms to the destinations configured in the code. It only
sends one message and starts the 60 minute timer again.

To set up you need to have an email account where you can programmatcially send email from, such as Google. This needs to 
be added into the Python file. For sms you need a cellphone number. It uses a free service so there is no sign up for sms.
You can customize the email or sms messgae. For example in the sms message I added the url for my PiGMi. This way I can
simply click on the link and open up the main page.
It should be set up as either a cronjob or as a program that runs  on boot up. There are instructions on the main
Raspberry Pi pages on how to do this.
