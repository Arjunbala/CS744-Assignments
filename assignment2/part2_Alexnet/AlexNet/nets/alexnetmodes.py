from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from .common import ModelBuilder
from .alexnetcommon import alexnet_inference, alexnet_part_conv, alexnet_loss, alexnet_eval
from ..optimizers.momentumhybrid import HybridMomentumOptimizer


def original(images, labels, num_classes, total_num_examples, devices=None, is_train=True):
    """Build inference"""
    if devices is None:
        devices = [None]

    def configure_optimizer(global_step, total_num_steps):
        """Return a configured optimizer"""
        def exp_decay(start, tgtFactor, num_stairs):
            decay_step = total_num_steps / (num_stairs - 1)
            decay_rate = (1 / tgtFactor) ** (1 / (num_stairs - 1))
            return tf.train.exponential_decay(start, global_step, decay_step, decay_rate,
                                              staircase=True)

        def lparam(learning_rate, momentum):
            return {
                'learning_rate': learning_rate,
                'momentum': momentum
            }

        return HybridMomentumOptimizer({
            'weights': lparam(exp_decay(0.001, 250, 4), 0.9),
            'biases': lparam(exp_decay(0.002, 10, 2), 0.9),
        })

    def train(total_loss, global_step, total_num_steps):
        """Build train operations"""
        # Compute gradients
        with tf.control_dependencies([total_loss]):
            opt = configure_optimizer(global_step, total_num_steps)
            grads = opt.compute_gradients(total_loss)

        # Apply gradients.
        apply_gradient_op = opt.apply_gradients(grads, global_step=global_step)

        with tf.control_dependencies([apply_gradient_op]):
            return tf.no_op(name='train')

    with tf.device(devices[0]):
        builder = ModelBuilder()
        print('num_classes: ' + str(num_classes))
        net, logits, total_loss = alexnet_inference(builder, images, labels, num_classes)

        if not is_train:
            return alexnet_eval(net, labels)

        global_step = builder.ensure_global_step()
        print('total_num_examples: ' + str(total_num_examples))
        train_op = train(total_loss, global_step, total_num_examples)
    return net, logits, total_loss, train_op, global_step


def distribute(images, labels, num_classes, total_num_examples, devices, is_train=True):
    # Put your code here
    # You can refer to the "original" function above, it is for the single-node version.
    if devices is None:
        devices = [None]
	# copied from original function
    def configure_optimizer(global_step, total_num_steps):
        """Return a configured optimizer"""
        def exp_decay(start, tgtFactor, num_stairs):
            decay_step = total_num_steps / (num_stairs - 1)
            decay_rate = (1 / tgtFactor) ** (1 / (num_stairs - 1))
            return tf.train.exponential_decay(start, global_step, decay_step, decay_rate,
                                              staircase=True)

        def lparam(learning_rate, momentum):
            return {
                'learning_rate': learning_rate,
                'momentum': momentum
            }

        return HybridMomentumOptimizer({
            'weights': lparam(exp_decay(0.001, 250, 4), 0.9),
            'biases': lparam(exp_decay(0.002, 10, 2), 0.9),
        })
    #copied from orignal function
    def train(total_loss, global_step, total_num_steps):
        """Build train operations"""
        # Compute gradients
        with tf.control_dependencies([total_loss]):
            opt = configure_optimizer(global_step, total_num_steps)
            grads = opt.compute_gradients(total_loss)

        # Apply gradients.
        apply_gradient_op = opt.apply_gradients(grads, global_step=global_step)

        with tf.control_dependencies([apply_gradient_op]):
            return tf.no_op(name='train')


    # 1. Create global steps on the parameter server node. You can use the same method that the single-machine program uses.
    builder = ModelBuilder(devices[-1])
    global_step = builder.ensure_global_step()
        
    # 2. Configure your optimizer using HybridMomentumOptimizer.
    opt = configure_optimizer(global_step, total_num_examples)

    # 3. Construct graph replica by splitting the original tensors into sub tensors. (hint: take a look at tf.split )
    inputImagesSplit = tf.split(images, len(devices[:-1]))
    inputLabelsSplit = tf.split(labels, len(devices[:-1]))
    # keep a list to store gradients
    workerGradients = []

    with tf.variable_scope('AlexNet') as varScope:
    # 4. For each worker node, create replica by calling alexnet_inference and computing gradients.
        with tf.name_scope('') as nameScope:
            for i in range(len(devices[:-1])):
                with tf.device(devices[i]):
                    worker = devices[i]
                    with tf.name_scope("Workers_{}".format(i)):
                        net, logits, total_loss = alexnet_inference(builder, inputImagesSplit[i], inputLabelsSplit[i], num_classes)
                        gradient = opt.compute_gradients(total_loss)
                
                workerGradients.append(gradient)
                #Reuse the variable for the next replica. For more information on how to reuse variables in TensorFlow,
                varScope.reuse_variables()

   
    # 5. On the parameter server node, apply gradients.
    with tf.device(builder.variable_device()):
        combinedGrad = builder.average_gradients(workerGradients)
        trainOp = opt.apply_gradients(combinedGrad, global_step=global_step)
        allTrainOp = tf.group(trainOp, name='AllTrainOps')
    
    # 6. return required values.
    return net, logits, total_loss, allTrainOp, global_step