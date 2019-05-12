import sys, pdb, os
import time
import numpy as np
import tensorflow as tf

class CB_VEC:
    def __init__(self,v_window_size=3,c_window_size=3,num_dx=200,num_rx=20000,dx_emb_size=64,rx_emb_size=64,
                 max_visit_per_person=34,max_rx_per_dx=1000,visit_emb_size=16
                 ,l2=0.001,batch_size=16,max_dx_per_visit=1):
        self.v_window_size=v_window_size
        self.c_window_size=c_window_size
        self.num_dx=num_dx
        self.num_rx=num_rx
        self.dx_emb_size=dx_emb_size
        self.rx_emb_size=rx_emb_size
        self.max_visit_per_person=max_visit_per_person
        self.max_dx_per_visit=max_dx_per_visit#
        self.max_rx_per_dx=max_rx_per_dx
        self.visit_emb_size=visit_emb_size
        self.L2=l2
        self.batch_size=batch_size
        self.one_label=1
        W_emb_dx = tf.get_variable('W_emb_dx', shape=(self.num_dx, self.dx_emb_size), dtype=tf.float32)
        W_emb_rx = tf.get_variable('W_emb_rx', shape=(self.num_rx, self.rx_emb_size), dtype=tf.float32)
        self.W_emb_rx_ = tf.nn.relu(W_emb_rx)
        self.W_emb_dx_ = tf.nn.relu(W_emb_dx)#
        # self.W_emb_rx_ = tf.nn.l2_normalize(W_emb_rx)#
        # self.W_emb_dx_ = tf.nn.l2_normalize(W_emb_dx)


        #label
        self.dx_var = tf.placeholder(tf.int32, shape=(None, self.max_visit_per_person, self.max_dx_per_visit), name='dx_var')
        self.rx_var = tf.placeholder(tf.int32, shape=(None, self.max_visit_per_person, self.max_dx_per_visit, self.max_rx_per_dx), name='rx_var')
        self.dx_label=tf.placeholder(tf.int32, shape=(None, self.max_visit_per_person, self.max_dx_per_visit), name='dx_label')
        self.dx_mask=tf.placeholder(tf.int32, shape=(None, self.max_visit_per_person, self.max_dx_per_visit), name='dx_mask')

        self.dx_visit = tf.nn.embedding_lookup(self.W_emb_dx_, tf.reshape(self.dx_var, (-1, self.max_dx_per_visit)))
        dx_visit = tf.reshape(self.dx_visit, (-1, self.dx_emb_size))#


        rx_visit = tf.nn.embedding_lookup(self.W_emb_rx_, tf.reshape(self.rx_var, (-1, self.max_rx_per_dx)))
        preVec=tf.reshape(rx_visit,(-1,self.max_visit_per_person,self.max_dx_per_visit*self.max_rx_per_dx,self.rx_emb_size))

        rx_visit = tf.reduce_sum(rx_visit, axis=1)
        W_dr = tf.Variable(tf.truncated_normal([self.dx_emb_size,self.rx_emb_size], stddev=0.1), name="W_dr")
        b_dr = tf.Variable(tf.constant(0.1, shape=[self.rx_emb_size]), name="b_dr")
        dr_visit=tf.matmul(dx_visit,W_dr) + b_dr
        dx_visit=tf.nn.relu(dr_visit)
        dr_visit = dx_visit * rx_visit
        dx_obj = dx_visit + dr_visit#
        # dx_obj =dr_visit  #


        W_dx = tf.Variable(tf.truncated_normal([self.rx_emb_size,self.visit_emb_size], stddev=0.1), name="W_dx")
        b_dx = tf.Variable(tf.constant(0.1, shape=[self.visit_emb_size]), name="b_dx")
        dx_obj=tf.matmul(dx_obj,W_dx) + b_dx
        dx_obj=tf.nn.relu(dx_obj)

         #
        pre_visit = tf.reshape(dx_obj, (-1,self.max_dx_per_visit, self.visit_emb_size))

        visit = tf.reduce_sum(pre_visit, axis=1)

        W_output = tf.Variable(tf.truncated_normal([self.visit_emb_size,self.num_dx], stddev=0.1), name="W_output")
        b_output = tf.Variable(tf.constant(0.1, shape=[self.num_dx]), name="b_outpt")
        dx_output=tf.matmul(dx_obj,W_output) + b_output
        dx_output=tf.nn.relu(dx_output)
        seq_visit = tf.reshape(visit, (-1, self.max_visit_per_person, self.visit_emb_size))
        dx_output=tf.reshape(dx_output,(-1, self.max_visit_per_person, self.num_dx))


        #
        all_rx_exp=tf.reduce_sum(tf.exp(tf.matmul(self.W_emb_rx_,tf.transpose(self.W_emb_rx_,[1,0]))),axis=1)
        rx_exp_visit=tf.nn.embedding_lookup(all_rx_exp,tf.reshape(self.rx_var,(-1,self.max_rx_per_dx)))
        rx_exp_visit=tf.reshape(rx_exp_visit,(-1,self.max_visit_per_person,self.max_dx_per_visit*self.max_rx_per_dx))

        all_dx_exp = tf.reduce_sum(tf.exp(tf.matmul(self.W_emb_dx_, tf.transpose(self.W_emb_dx_, [1, 0]))), axis=1)
        dx_exp_visit = tf.nn.embedding_lookup(all_dx_exp, tf.reshape(self.dx_var, (-1, self.max_dx_per_visit)))
        dx_exp_visit = tf.reshape(dx_exp_visit, (-1, self.max_visit_per_person))


        with tf.name_scope("outputs"):
            self.output=tf.reshape(visit, (-1, self.max_visit_per_person*self.visit_emb_size))
        dx_target=tf.one_hot(self.dx_label,self.num_dx)
        dx_target=tf.reduce_sum(dx_target,axis=2)
        self.prediction=tf.nn.softmax(dx_output)

        if self.v_window_size==3:
            self.loss = tf.nn.softmax_cross_entropy_with_logits_v2(logits=self.prediction, labels=dx_target)
            # self.loss1 = tf.nn.softmax_cross_entropy_with_logits_v2(logits=self.prediction[:,1:], labels=dx_target[:,1:])
            # self.loss2 = tf.nn.softmax_cross_entropy_with_logits_v2(logits=self.prediction[:,:-1], labels=dx_target[:,:-1])
            # self.loss=tf.concat([self.loss,self.loss1],1)
            # self.loss = tf.concat([self.loss, self.loss2],1)
            self.loss = self.loss / self.max_visit_per_person
            self.loss = tf.reduce_mean(self.loss)

        if self.c_window_size==3:

            norms1=tf.exp(tf.reduce_sum(preVec[:,:,1:,:]*preVec[:,:,:-1,:],axis=3))
            norms2=tf.exp(tf.reduce_sum(preVec[:,:,:-1,:]*preVec[:,:,1:,:],axis=3))
            # norms1=-tf.log(tf.clip_by_value(norms1/tf.clip_by_value(rx_exp_visit[:,:,:-1],1e-12,1.0),1e-12,1.0))
            # norms2=-tf.log(tf.clip_by_value(norms2/tf.clip_by_value(rx_exp_visit[:,:,1:],1e-12,1.0),1e-12,1.0))
            # norms1 = -tf.log(tf.clip_by_value(norms1 / tf.clip_by_value(rx_exp_visit[:, :, :-1], 1e-12, 1.0), 1e-12, 1.0))
            # norms2 = -tf.log(tf.clip_by_value(norms2 / tf.clip_by_value(rx_exp_visit[:, :, 1:], 1e-12, 1.0), 1e-12, 1.0))
            norms1 = -tf.log(norms1 / (rx_exp_visit[:, :, :-1]+ 1e-8)+1e-8)
            norms2 = -tf.log(norms2 / (rx_exp_visit[:, :, 1:]+1e-8)+1e-8)
            self.loss1=tf.reduce_mean(norms1+norms2)

        elif self.c_window_size==5:
            norms1=tf.exp(tf.reduce_sum(preVec[:,:,1:,:]*preVec[:,:,:-1,:],axis=3))
            norms2=tf.exp(tf.reduce_sum(preVec[:,:,:-1,:]*preVec[:,:,1:,:],axis=3))
            norms3=tf.exp(tf.reduce_sum(preVec[:,:,2:,:]*preVec[:,:,:-2,:],axis=3))
            norms4=tf.exp(tf.reduce_sum(preVec[:,:,:-2,:]*preVec[:,:,2:,:],axis=3))
            norms1 = -tf.log(norms1 / (rx_exp_visit[:, :, :-1] + 1e-8) + 1e-8)
            norms2 = -tf.log(norms2 / (rx_exp_visit[:, :, 1:] + 1e-8) + 1e-8)
            norms3 = -tf.log(norms3 / (rx_exp_visit[:, :, :-2] + 1e-8) + 1e-8)
            norms4 = -tf.log(norms4 / (rx_exp_visit[:, :, 2:] + 1e-8) + 1e-8)
            self.loss1=tf.reduce_mean(norms1+norms2+norms3+norms4)

        elif self.c_window_size==7:

            norms1=tf.exp(tf.reduce_sum(preVec[:,:,1:,:]*preVec[:,:,:-1,:],axis=3))
            norms2=tf.exp(tf.reduce_sum(preVec[:,:,:-1,:]*preVec[:,:,1:,:],axis=3))
            norms3=tf.exp(tf.reduce_sum(preVec[:,:,2:,:]*preVec[:,:,:-2,:],axis=3))
            norms4=tf.exp(tf.reduce_sum(preVec[:,:,:-2,:]*preVec[:,:,2:,:],axis=3))
            norms5=tf.exp(tf.reduce_sum(preVec[:,:,3:,:]*preVec[:,:,:-3,:],axis=3))
            norms6=tf.exp(tf.reduce_sum(preVec[:,:,:-3,:]*preVec[:,:,3:,:],axis=3))
            norms1 = -tf.log(norms1 / (rx_exp_visit[:, :, :-1] + 1e-8) + 1e-8)
            norms2 = -tf.log(norms2 / (rx_exp_visit[:, :, 1:] + 1e-8) + 1e-8)
            norms3 = -tf.log(norms3 / (rx_exp_visit[:, :, :-2] + 1e-8) + 1e-8)
            norms4 = -tf.log(norms4 / (rx_exp_visit[:, :, 2:] + 1e-8) + 1e-8)
            norms5 = -tf.log(norms5 / (rx_exp_visit[:, :, :-3] + 1e-8) + 1e-8)
            norms6 = -tf.log(norms6 / (rx_exp_visit[:, :, 3:] + 1e-8) + 1e-8)
            self.loss1=tf.reduce_mean(norms1+norms2+norms3+norms4+norms5+norms6)

        with tf.name_scope("loss"):
            self.loss+=self.loss1+ self.L2 * tf.reduce_mean(preVec ** 2)+ self.L2 * tf.reduce_sum(seq_visit ** 2)

