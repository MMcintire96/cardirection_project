RPI:

  The folder imgserve should be on your rpi - make sure your camera is enabled and mosquitto -d is used to init the mqtt server. 

  Add the correct IP addesses to run_analysis.py then run it (use & for background run, or nohop on ssh)



Computer:

  mosquitto -d
  
  python classifier.py

You can also run 'mse_graph' while its running for a live graph of mse & err vs count

 Make sure your model is trained, I am not uploading the training data because its large, but the output_graph is there from my car classifier
 
#TODO
1. Save all frames from motion detection?
