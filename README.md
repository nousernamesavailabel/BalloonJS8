# BalloonJS8

Project to beacon APRS position of a HAB over HF utilizing JS8Call. 

All versions of the code require JS8Call to already be installed and configured. 

## BalloonTXFromPi.py 
  -Pulls a GPS position from a GT-U7 GPS module and converts the lat/lon to maidenhead (for compatibility with JS8Call APRS gateways) prior to sending the position as a directed message to @APRSIS.
  -Works best with JS8Call configured to run as a service on boot.
  
## BalloonTX.py: 
  - Generic TX code with a hardcoded position.

## main.py:
  - RX only, converts the maidenhead grid from JS8 maidenhead to lat/lon then sends the point to a TAK server as COT. 



Ensure your reporting settings look like the image below in JS8Call so that the UDP communication works. TCP not implemented yet:
![image](https://github.com/user-attachments/assets/f61b1f9c-8f2a-4f37-ae51-78983c821d73)
