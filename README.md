# PiGMiMon
Monitor code to be used with My-Garage( https://github.com/robboz4/My-Garage), implemented as PiGMi.

This is the monitor code that can be armed by the PiGMi settings page. It is configured to run and check the status of the 
doors every minute. If no change is detetcted it will keep looping and post a 60 minute no change message to the PiGMi log
file. If there is a  change and it is in passive mode, it will log the door in the PiGMi log file and reset the 60 minute 
counter. If it is active it will send an email and sms to the destinations configured in the code. It only
sends one message and starts the 60 minute timer again.

To set up you need to have an email account where you can programmatically send email from, such as Google. For sms you need a cellphone number. It uses the same email account to send an SMS message via number@text.att.net . There are other phones providers that offer the same service. Check here http://www.computerhope.com/issues/ch000952.htm
You can customize the email or sms message. For example in the sms message I added the url for my PiGMi. This way I can
simply click on the link and open up the main page.

It should be set up to run on boot up. There are instructions on the main
Raspberry Pi pages on how to do this. It is recommended to use the system service method, so it runs after Apache and PHP have been launced.
