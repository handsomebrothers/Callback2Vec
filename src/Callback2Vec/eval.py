import tensorflow as tf
import numpy as np
import os
import time
import datetime
import pandas as pd
import data_helper
# Parameters
# ==================================================

# Data Parameters

tf.flags.DEFINE_string("input_text_file", "G:/data_test.csv", "Label file for test text data source.")
# tf.flags.DEFINE_string("input_text_file", "../data/data2.csv", "Test text data source to evaluate.")
tf.flags.DEFINE_string("single_url",None,"single url to evaluate")

# Eval Parameters
tf.flags.DEFINE_integer("batch_size", 1, "Batch Size (default: 64)")
tf.flags.DEFINE_boolean("eval_train", True, "Evaluate on all training data")
# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")

FLAGS = tf.flags.FLAGS
FLAGS.flag_values_dict()
def test(checkpoint_path):
    print("\nParameters:")
    for attr, value in sorted(FLAGS.__flags.items()):
        print("{}={}".format(attr.upper(), value))
    print("")

    # validate
    # ==================================================

    # validate checkout point file
    checkpoint_file = tf.train.latest_checkpoint(
        checkpoint_path) 
    if checkpoint_file is None:
        print("Cannot find a valid checkpoint file!")
        exit(0)
    print("Using checkpoint file : {}".format(checkpoint_file))
    # Evaluation
    # ==================================================
    print("\nEvaluating...\n")
    test_data=[]
    checkpoint_file = tf.train.latest_checkpoint(checkpoint_path)
    graph = tf.Graph()
    with graph.as_default():
        session_conf = tf.ConfigProto(
            allow_soft_placement=FLAGS.allow_soft_placement,
            log_device_placement=FLAGS.log_device_placement)
        sess = tf.Session(config=session_conf)
        with sess.as_default():
            saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
            saver.restore(sess, checkpoint_file)
            dx_var = graph.get_operation_by_name("dx_var").outputs[0]
            rx_var = graph.get_operation_by_name("rx_var").outputs[0]
            rx_emb=graph.get_operation_by_name('W_emb_rx_').outputs[0]
            # batches = data_helper.batch_iter(test_data,1,20)
            visit_emb = graph.get_operation_by_name("outputs/output").outputs[0]

if __name__ == '__main__':
    checkpoint_path = "F:/DetectMaliciousURL-master/model/runs/1539574739/checkpoints"
    test(checkpoint_path)
