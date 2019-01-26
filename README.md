RPI:

  The folder imgserve should be on your rpi - make sure your camera is enabled and mosquitto -d is used to init the mqtt server. 
  
  Add the correct IP addesses to run_analysis.py then run it (use & for background run, or nohop on ssh)

Computer:

  mosquitto -d
  
  python classifier.py

 Make sure your model is trained, I am not uploading the training data because its large
 
 
