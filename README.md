Project to beacon APRS position of a HAB over HF utilizing JS8Call. 

BalloonTX.py will eventaully pull a GPS position and convert the lat/lon to maidenhead for compatibility with JS8Call APRS gateways.

main.py is RX only and converts the maidenhead grid from JS8 to lat/lon then sends the point to a TAK server as COT. Working on reading the long grid from the message for better precison.

Ensure your reporting settings look like the image below in JS8Call:
![image](https://github.com/user-attachments/assets/f61b1f9c-8f2a-4f37-ae51-78983c821d73)
