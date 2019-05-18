# coding=utf-8
import time
import logging
import tensorflow as tf
import datetime
import os
import matplotlib as plt
import numpy as np
from new_model import CB_VEC
# from data_helper import *
from data_helper import *
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# os.environ["CUDA_VISIBLE_DEVICES"] = "0"
print('over')
#------------------------- define parameter -----------------------------
tf.flags.DEFINE_integer("batch_size",300, "batch size of each batch")
tf.flags.DEFINE_integer('c_window_size',3,'window size of callback code')
tf.flags.DEFINE_integer("v_window_size", 3, "window size of callback sequence")
tf.flags.DEFINE_integer("num_dx", 400, "size of callback sequence")
tf.flags.DEFINE_integer("num_rx", 20000, "size of callback code")
tf.flags.DEFINE_integer("dx_emb_size", 16, "embedding size of callback sequence")
tf.flags.DEFINE_integer("rx_emb_size", 64, "embedding size of callback code")
tf.flags.DEFINE_integer("max_visit_per_person", 35, "max size of callback sequence")
tf.flags.DEFINE_integer("max_rx_per_dx",400, "max size of callback code for each callback")
tf.flags.DEFINE_integer("visit_emb_size", 16, "embedding size for each callback sequence")
tf.flags.DEFINE_integer("max_dx_per_visit",1, "max dx for each callback")
tf.flags.DEFINE_float("l2", 0.1, "l2 regulation")
tf.flags.DEFINE_integer("max_grad_norm", 5, "the max of gradient")
tf.flags.DEFINE_float("init_scale", 0.1, "initializer scale")

tf.flags.DEFINE_float('lr',0.0001,'the learning rate')
tf.flags.DEFINE_float('lr_decay',0.6,'the learning rate decay')
tf.flags.DEFINE_integer("epoches", 100, "epoches")
tf.flags.DEFINE_integer('max_decay_epoch',30,'num epoch')
tf.flags.DEFINE_float("l2_reg_lambda", 0.0001, "l2 regulation")
tf.flags.DEFINE_string("out_dir", "save/", "output directory")

tf.flags.DEFINE_integer("num_epochs", 40, "Number of training epochs (default: 200)")
tf.flags.DEFINE_integer("evaluate_every", 100, "Evalue model on dev set after this many steps (default: 100)")
tf.flags.DEFINE_integer("checkpoint_every", 100, "Save model after this many steps (defult: 100)")
tf.flags.DEFINE_integer("num_checkpoints", 5, "Number of checkpoints to store (default: 5)")
#
# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")
# Parse parameters from commands
FLAGS = tf.flags.FLAGS
FLAGS.flag_values_dict()
# FLAGS._parse_flags()
# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = ""
timestamp = str(int(time.time()))
out_dir = os.path.abspath(os.path.join(os.path.curdir, "runs", timestamp))
print("Writing to {}\n".format(out_dir))
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
# Checkpoint directory. Tensorflow assumes this directory already exists so we need to create it
checkpoint_dir = os.path.abspath(os.path.join(out_dir, "checkpoints"))
checkpoint_prefix = os.path.join(checkpoint_dir, "model")
if not os.path.exists(checkpoint_dir):
    os.makedirs(checkpoint_dir)
path='/home/hdr/my_apk_project/callback_method_not_amd.csv'
path1='/home/hdr/my_apk_project/final_callback_method.csv'
p='/home/hdr/my_apk_project/callback_method11.csv'
# data,num_dx,num_rx=generate_train_data_new(p)
data,num_dx,num_rx=generate_train_data_new(path,path1)
print(num_dx)
print(num_rx)

all_epoh=[]
all_losses=[]
def train():
    with tf.Graph().as_default():
        session_conf = tf.ConfigProto(
          allow_soft_placement=FLAGS.allow_soft_placement,
          log_device_placement=FLAGS.log_device_placement)
        sess = tf.Session(config=session_conf)
        with sess.as_default():
            model = CB_VEC(FLAGS.v_window_size,FLAGS.c_window_size,num_dx,
                         num_rx,FLAGS.dx_emb_size,FLAGS.rx_emb_size,
                          FLAGS.max_visit_per_person,FLAGS.max_rx_per_dx,FLAGS.visit_emb_size,
                          FLAGS.l2,FLAGS.batch_size,FLAGS.max_dx_per_visit)

            # Define Training procedure
            LEARNING_RATE_BASE = 0.0001
            LEARNING_RATE_DECAY = 0.8
            LEARNING_RATE_STEP = 1
            gloabl_steps = tf.Variable(0, trainable=False)
            learning_rate = tf.train.exponential_decay(LEARNING_RATE_BASE
                                                       , gloabl_steps,
                                                       LEARNING_RATE_STEP,
                                                       LEARNING_RATE_DECAY,
                                                       staircase=True)

            optimizer = tf.train.AdamOptimizer(learning_rate )
            grads_and_vars = optimizer.compute_gradients(model.loss)
            global_step = tf.Variable(0, name="global_step", trainable=False)
            train_op = optimizer.apply_gradients(grads_and_vars, global_step=global_step)

            # Keep track of gradient values and sparsity (optional)
            grad_summaries = []
            for g, v in grads_and_vars:
                if g is not None:
                    grad_hist_summary = tf.summary.histogram("{}/grad/hist".format(v.name), g)
                    sparsity_summary = tf.summary.scalar("{}/grad/sparsity".format(v.name), tf.nn.zero_fraction(g))
                    grad_summaries.append(grad_hist_summary)
                    grad_summaries.append(sparsity_summary)
            grad_summaries_merged = tf.summary.merge(grad_summaries)

            # Output directory for models and summaries
            print("Writing to {}\n".format(out_dir))

            # Summaries for loss and accuracy
            # loss_summary = tf.summary.scalar("loss", model.loss)
            loss_summary = tf.summary.histogram("loss", model.loss)

            # acc_summary = tf.summary.scalar("accuracy", cnn.accuracy)

            # Train Summaries
            train_summary_op = tf.summary.merge([loss_summary, grad_summaries_merged])
            train_summary_dir = os.path.join(out_dir, "summaries", "train")
            train_summary_writer = tf.summary.FileWriter(train_summary_dir, sess.graph)


            # Dev summaries
            dev_summary_op = tf.summary.merge([loss_summary])
            dev_summary_dir = os.path.join(out_dir, "summaries", "dev")
            dev_summary_writer = tf.summary.FileWriter(dev_summary_dir, sess.graph)

            # Checkpoint directory. Tensorflow assumes this directory already exists so we need to create it
            checkpoint_dir = os.path.abspath(os.path.join(out_dir, "checkpoints"))
            checkpoint_prefix = os.path.join(checkpoint_dir, "model")
            if not os.path.exists(checkpoint_dir):
                os.makedirs(checkpoint_dir)
            saver = tf.train.Saver(tf.global_variables(), max_to_keep=FLAGS.num_checkpoints)

            sess.run(tf.global_variables_initializer())

            def train_step(dx_batch, rx_batch,dx_label_batch):
                all_loss = []
                """
                A single training step
                """
                feed_dict = {
                    model.dx_var: dx_batch,
                    model.rx_var: rx_batch,
                    model.dx_label:dx_label_batch

                }

                _, step, summaries, loss,dx_visit,emb_r= sess.run(
                    [train_op, global_step, train_summary_op, model.loss,model.dx_visit,model.W_emb_rx_],
                    feed_dict)
                time_str = datetime.datetime.now().isoformat()
                all_loss.append(loss)


                train_summary_writer.add_summary(summaries, step)
                return all_loss,step,time_str
            data_size = len(data)
            num_batches_per_epoch = int((data_size - 1) / FLAGS.batch_size) + 1
            x=[]
            y=[]
            for epoch in range(FLAGS.num_epochs):
                loss_mes=[]
                all_epoh.append(epoch)
                shuffled_data = data
                for batch_num in range(num_batches_per_epoch):
                    start_idx = batch_num * FLAGS.batch_size
                    end_idx = min((batch_num + 1) * FLAGS.batch_size, data_size)
                    for batch in zip(shuffled_data[start_idx: end_idx]):
                        dx_batch, rx_batch, _, _, dx_label_batch = zip(*batch)
                        all_loss,step,time_str=train_step(dx_batch, rx_batch, dx_label_batch)
                        loss_mes+=all_loss
                        value1=0.0
                        for k in all_loss:
                            value1+=k
                        if step%100==0:
                            x.append(step)
                            y.append(value1/len(all_loss))
                        print("{}: step {}, loss {:g}".format(time_str, step, value1/len(all_loss)))
                        # if step==20000:
                        #     p1 = plt.scatter(x, y, marker='x', color='g', label='1', s=30)
                        #
                        #     plt.show()
                        current_step = tf.train.global_step(sess, global_step)

                        if current_step % FLAGS.checkpoint_every == 0:
                            path = saver.save(sess, checkpoint_prefix, global_step=current_step)
                            print("Saved model checkpoint to {}\n".format(path))
                value=0.0
                for k in loss_mes:
                    value+=k
                all_losses.append(value/len(loss_mes))

train()
p1=plt.scatter(all_epoh,all_losses,marker='x',color='r',label='1',s=30)
plt.plot(all_epoh,all_losses)
plt.show()
