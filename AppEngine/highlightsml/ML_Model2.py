from __future__ import print_function

import tensorflow as tf
import numpy as np
import json






learning_rate = 0.001
num_steps = 3000
batch_size = 128
display_step = 100

# Network Parameters
n_hidden_1 = 20 # 1st layer number of neurons
n_hidden_2 = 30 # 2nd layer number of neurons
num_input = 3 # MNIST data input (img shape: 28*28)
num_classes = 2 # MNIST total classes (0-9 digits)

with open("./highlightsml/dataBase_results_x.json", "r") as jsonFile:
    training_data = json.load(jsonFile)

with open("./highlightsml/dataBase_results_y.json", "r") as jsonFile:
    labels = json.load(jsonFile)
training_data = np.array(training_data).astype(float)
labels = np.array(labels).astype(float)

input_fn = tf.estimator.inputs.numpy_input_fn(
    x={'images': training_data}, y=labels,
    batch_size=batch_size, num_epochs=None, shuffle=True)


def neural_net(x_dict):
    # TF Estimator input is a dict, in case of multiple inputs
    x = x_dict['images']
    # Hidden fully connected layer with 256 neurons
    layer_1 = tf.layers.dense(x, n_hidden_1)
    # Hidden fully connected layer with 256 neurons
    layer_2 = tf.layers.dense(layer_1, n_hidden_2)
    # Output fully connected layer with a neuron for each class
    out_layer = tf.layers.dense(layer_2, num_classes)
    return out_layer


def model_fn(features, labels, mode):
    # Build the neural network
    logits = neural_net(features)

    # Predictions
    pred_classes = tf.argmax(logits, axis=1)
    pred_probas = tf.nn.softmax(logits)

    # If prediction mode, early return
    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode, predictions={
            "class_ids" : pred_classes,
            "probabilities" : tf.nn.softmax(logits),
            "logits" : logits
        })

        # Define loss and optimizer
    loss_op = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(
        logits=logits, labels=tf.cast(labels, dtype=tf.int32)))
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
    train_op = optimizer.minimize(loss_op, global_step=tf.train.get_global_step())

    # Evaluate the accuracy of the model
    acc_op = tf.metrics.accuracy(labels=labels, predictions=pred_classes)

    # TF Estimators requires to return a EstimatorSpec, that specify
    # the different ops for training, evaluating, ...
    estim_specs = tf.estimator.EstimatorSpec(
        mode=mode,
        predictions=pred_classes,
        loss=loss_op,
        train_op=train_op,
        eval_metric_ops={'accuracy': acc_op})

    return estim_specs


model = tf.estimator.Estimator(model_fn)
model.train(input_fn, steps=num_steps)

# Evaluate the Model
# Define the input function for evaluating
input_fn = tf.estimator.inputs.numpy_input_fn(
    x={'images': training_data}, y=labels,
    batch_size=batch_size, shuffle=False)


# Use the Estimator 'evaluate' method



def getBestHighlights(array, time_stamps, numDesired):

    test_images = np.array(array)
    # Prepare the input data
    input_fn = tf.estimator.inputs.numpy_input_fn(
        x={'images': test_images}, shuffle=False)
    # Use the model to predict the images class
    preds = list(model.predict(input_fn))
    temp_probabilitites = []
    probabilities = []
    for i in preds:
        temp_probabilitites.append(i["probabilities"])
    for i in temp_probabilitites:
        probabilities.append(i[1])
    arr = np.array(probabilities)
    arr = arr.argsort()[-1*numDesired:][::-1]
    times = []
    for i in arr:
        times.append(str(time_stamps[i]//60) + ":" + str(time_stamps[i] % 60))
    with open("./highlightsml/one_time_example.json", "w") as jsonFile:
        json.dump(times, jsonFile)
    return times


with open("./highlightsml/one_time_example.json", "r") as jsonFile:
    data = json.load(jsonFile)

one_time = data[0]
time_stamps = data[1]
getBestHighlights(one_time, time_stamps, 10)




