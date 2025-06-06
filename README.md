Project to beacon APRS position of a HAB over HF utilizing JS8Call. 

BalloonTX.py will eventaully pull a GPS position and convert the lat/lon to maidenhead for compatibility with JS8Call APRS gateways.

main.py is RX only and converts the maidenhead grid rom JS8 to lat/lon then sends the point to a TAK server as COT. Working on reading the long grid from the message for better precison.
