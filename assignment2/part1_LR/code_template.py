import tensorflow as tf
import time
from tensorflow.examples.tutorials.mnist import input_data

# define the command line flags that can be sent
tf.app.flags.DEFINE_integer("task_index", 0, "Index of task with in the job.")
tf.app.flags.DEFINE_string("job_name", "worker", "either worker or ps")
tf.app.flags.DEFINE_string("deploy_mode", "single", "either single or cluster")
FLAGS = tf.app.flags.FLAGS

tf.logging.set_verbosity(tf.logging.DEBUG)

clusterSpec_single = tf.train.ClusterSpec({
    "worker" : [
        "localhost:2222"
    ]
})

clusterSpec_cluster = tf.train.ClusterSpec({
    "ps" : [
        "128.104.222.24:2226"
    ],
    "worker" : [
        "128.104.222.24:2226",
        "128.104.222.28:2226"
    ]
})

clusterSpec_cluster2 = tf.train.ClusterSpec({
    "ps" : [
        "128.104.222.24:2222"
    ],
    "worker" : [
        "128.104.222.24:2222",
        "128.104.222.28:2222",
        "128.104.222.22:2222",
        "128.104.222.16:2222"
    ]
})

clusterSpec = {
    "single": clusterSpec_single,
    "cluster": clusterSpec_cluster,
    "cluster2": clusterSpec_cluster2
}

clusterinfo = clusterSpec[FLAGS.deploy_mode]
server = tf.train.Server(clusterinfo, job_name=FLAGS.job_name, task_index=FLAGS.task_index)


if FLAGS.job_name == "ps":
    server.join()
elif FLAGS.job_name == "worker":
    # Read the data set
    mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
    
    # These are the training parameters - Play around with these!
    # TODO: These should be programmed so as to pass them as flags, but this works for the assignment.
    learning_rate = 0.01
    training_epochs = 25
    batch_size = 200

    # tf Graph Input
    x = tf.placeholder(tf.float32, [None, 784]) # 28*28 image
    y = tf.placeholder(tf.float32, [None, 10]) # 0-9 digits recognition

    # Set model weights - Initialize all weights to 0.
    W = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))

    # Prediction Function
    prediction  = tf.nn.softmax(tf.matmul(x, W) + b)

    # Loss Function
    loss = tf.reduce_mean(-tf.reduce_sum(y*tf.log(prediction), reduction_indices=1))

    # Gradient Descent Optimizer
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss)

    init = tf.global_variables_initializer()

    time_begin = time.time() # note start time
    # Let the games begin!
    with tf.Session() as sess:

        sess.run(init)

        for epoch in range(training_epochs):
            avg_cost = 0.
            total_batch = int(mnist.train.num_examples/batch_size)

            for i in range(total_batch):
                batch_x, batch_y = mnist.train.next_batch(batch_size)
                _, c = sess.run([optimizer, loss], feed_dict={x: batch_x, y: batch_y})
                # Compute average loss. This helps us visualize the covergence
                avg_cost += c / total_batch

            print("Epoch:", '%04d' % (epoch+1), "cost=", "{:.9f}".format(avg_cost))

        correct_prediction = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
        # Calculate accuracy
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        print("Accuracy:", accuracy.eval({x: mnist.test.images, y: mnist.test.labels}))

    time_end = time.time()
    training_time = time_end - time_begin
    print("Training elapsed time: %f s" % training_time)
