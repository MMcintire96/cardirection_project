import json
import sqlite3

import numpy as np
import paho.mqtt.client as mqtt
import tensorflow as tf

MQTT_SERVER = '136.60.227.124'


def add_to_db(output_obj):
        conn = sqlite3.connect('cardata.db')
        c = conn.cursor()
        car_left = output_obj['car_left']
        car_right = output_obj['car_right']
        no_car = output_obj['no_car']
        lot_id = output_obj['lot_id']
        err = output_obj['err']
        mse = output_obj['mse']
        # this should be modified to insert car + or car - values to the lot_id
        if car_left > .5:
                print('car has entered the lot \n')
        if car_right > .5:
                print('car has left the lot \n')
        if no_car > .5:
                print('That was not a car \n')
        c.execute("""INSERT INTO location (car_left, car_right, no_car, lot_id, err, mse)
                    values (?,?,?,?,?,?)
                    """, (str(car_left), str(car_right), str(no_car), lot_id, err, mse))
        conn.commit()
        conn.close()


def img_to_tensor(lot_id, err, mse):

        # tf read file
        img_path = 'mqtt_img/output.jpg'
        file_reader = tf.read_file(img_path, "file_reader")

        # tf decode_jpeg, 3 channels
        image_reader = tf.image.decode_jpeg(
            file_reader, channels=3, name='jpeg_reader')

        # convert to tf.float, dim, resize [299,299] and normalize
        # maybe make into b/w to match trained data
        float_caster = tf.cast(image_reader, tf.float32)
        dims_expander = tf.expand_dims(float_caster, 0)
        resized = tf.image.resize_bilinear(dims_expander, [299, 299])
        normalized = tf.divide(tf.subtract(resized, [0]), [255])

        make_prediction(normalized, lot_id, err, mse)


def make_prediction(normalized, lot_id, err, mse):

        with open('model_outputs/output_labels.txt', 'r') as label_file:
                labels = [line.strip('\n') for line in label_file]
        labels = labels

        with tf.gfile.FastGFile('model_outputs/output_graph.pb', 'rb') as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')

        with tf.Session() as sess:
                img = sess.run(normalized)
                softmax_tensor = sess.graph.get_tensor_by_name(
                                                               'final_result:0')
                predictions = sess.run(softmax_tensor, {'Placeholder:0': img})
                prediction = predictions[0]

                prediction = prediction.tolist()
                max_value = max(prediction)
                max_index = prediction.index(max_value)
                predicted_label = labels[max_index]

                print(predictions, labels)
                print(("%s (%.2f%%)" % (predicted_label, max_value)))
                output_obj = {
                    'car_left': predictions[0][0],
                    'car_right': predictions[0][1],
                    'no_car': predictions[0][2],
                    'lot_id': lot_id,
                    'err': err,
                    'mse': mse,
                }
                add_to_db(output_obj)


def on_connect(client, userdata, flags, rc):
        print("Connected : " + str(rc))
        client.subscribe('full_img')
        client.subscribe('full_send')


def on_message(client, userdata, msg):
        # this might fail on multiple lots
        if msg.topic == 'full_img':
            img = msg.payload
            f = open("mqtt_img/output.jpg", "wb")
            f.write(img)
            f.close()
        if msg.topic == 'full_send':
            mqtt_list = str(msg.payload)
            mqtt_list = mqtt_list.split(',')
            lot_id, err, mse = str(msg.payload).replace("b'", "").replace("'","").split(',')

        img_to_tensor(lot_id, err, mse)

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, 1883, 60)

    client.loop_forever()
