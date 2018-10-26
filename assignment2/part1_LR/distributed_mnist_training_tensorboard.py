import tensorflow as tf
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
        "node-0.balarjun-assgn2.uwmadison744-f18-pg0.wisc.cloudlab.us:2222"
    ],
    "worker" : [
        "node-0.balarjun-assgn2.uwmadison744-f18-pg0.wisc.cloudlab.us:2223",
        "node-1.balarjun-assgn2.uwmadison744-f18-pg0.wisc.cloudlab.us:2222"
    ]
})

clusterSpec_cluster2 = tf.train.ClusterSpec({
    "ps" : [
        "node-0.balarjun-assgn2.uwmadison744-f18-pg0.wisc.cloudlab.us:4027"
    ],
    "worker" : [
        "node-0.balarjun-assgn2.uwmadison744-f18-pg0.wisc.cloudlab.us:4029",
        "node-1.balarjun-assgn2.uwmadison744-f18-pg0.wisc.cloudlab.us:4027",
        "node-2.balarjun-assgn2.uwmadison744-f18-pg0.wisc.cloudlab.us:4027",
        "node-3.balarjun-assgn2.uwmadison744-f18-pg0.wisc.cloudlab.us:4027"
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

    mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

    is_chief = (FLAGS.task_index == 0) #checks if this is the chief node

    # Parameters
    learning_rate = 0.01
    training_epochs = 10
    batch_size = 100
    display_step = 1

    # Assigns ops to the local worker by default.
    with tf.device(tf.train.replica_device_setter(
        worker_device="/job:worker/task:%d" % FLAGS.task_index,
        cluster=clusterinfo)):

        print ("balarjun starting at device ", FLAGS.task_index) 
        # tf Graph Input
        x = tf.placeholder(tf.float32, [None, 784]) # mnist data image of shape 28*28=784
        y = tf.placeholder(tf.float32, [None, 10]) # 0-9 digits recognition => 10 classes

        # Set model weights - Initialize all weights to 0.
        W = tf.Variable(tf.zeros([784, 10]))
        b = tf.Variable(tf.zeros([10]))

        # Prediction Function
        prediction  = tf.nn.softmax(tf.matmul(x, W) + b)

        # Loss Function
        loss = tf.reduce_mean(-tf.reduce_sum(y*tf.log(prediction), reduction_indices=1))

        # Gradient Descent
        optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss)
        print("balarjun done in task ", FLAGS.task_index)

        tf.summary.scalar("loss", loss)
        tf.summary.histogram("prediction", prediction)
        merged_summary_op = tf.summary.merge_all()
    # Initialize the variables (i.e. assign their default value)
    init = tf.global_variables_initializer()

    with tf.Session(server.target) as sess:
        # Run the initializer
        summary_writer = tf.summary.FileWriter('.', sess.graph)
        sess.run(init)

        # Training cycle
        for epoch in range(training_epochs):
            avg_cost = 0.
            total_batch = int(mnist.train.num_examples/batch_size)

            # Loop over all batches
            for i in range(total_batch):
                batch_xs, batch_ys = mnist.train.next_batch(batch_size)
                # Run optimization op (backprop) and cost op (to get loss value)
                _, c, summary = sess.run([optimizer, loss, merged_summary_op], feed_dict={x: batch_xs, y: batch_ys})
                # Compute average loss
                avg_cost += c / total_batch
                summary_writer.add_summary(summary, epoch * total_batch + i)

            # Display logs per epoch step
            if (epoch+1) % display_step == 0:
                print("Epoch:", '%04d' % (epoch+1), "cost=", "{:.9f}".format(avg_cost))

        print("Optimization Finished!")

        # Test model
        correct_prediction = tf.equal(tf.argmax(prediction, 1), tf.argmax(y, 1))
        # Calculate accuracy
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        print("Accuracy:", accuracy.eval({x: mnist.test.images, y: mnist.test.labels}))
