import numpy as np
import tensorflow as tf
import paho.mqtt.client as mqtt

MQTT_SERVER = 'localhost'
MQTT_PATH = 'test_img'


#helper function for running with an imgfile/off RPI
def img_to_tensor():

    # tf read file
    img_path = 'mqtt_img/output.jpg'
    file_reader = tf.read_file(img_path, "file_reader")

    # tf decode_jpeg, 3 channels
    image_reader = tf.image.decode_jpeg(file_reader, channels=3, name='jpeg_reader')

    #convert to tf.float, dim, resize [299,299] and normalize
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(dims_expander, [299, 299])
    normalized = tf.divide(tf.subtract(resized, [0]), [255])

    make_prediction(normalized)


def make_prediction(normalized):
    with open('model_outputs/output_labels.txt', 'r') as label_file:
        labels = [line.strip('\n') for line in label_file]
    labels = labels
    # load model
    with tf.gfile.FastGFile('model_outputs/output_graph.pb', 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')
    # get classification
    with tf.Session() as sess:
        #convert to 4-d np.array[batch_size, height, width, channel] 
        img = sess.run(normalized)
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
        predictions = sess.run(softmax_tensor, {'Placeholder:0': img})
        prediction = predictions[0]

        prediction = prediction.tolist()
        max_value = max(prediction)
        max_index = prediction.index(max_value)
        predicted_label = labels[max_index]

        print(predictions, labels)
        print(("%s (%.2f%%)" % (predicted_label, max_value)))



def on_connect(client, userdata, flags, rc):
    print("Connected : " +str(rc))
    client.subscribe(MQTT_PATH)


def on_message(client, userdata, msg):
    print("Message_Topic : ", msg.topic)
    # write the bytes to img 
    f = open("mqtt_img/output.jpg", "wb")
    f.write(msg.payload)
    f.close()
    img_to_tensor()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)

client.loop_forever()


