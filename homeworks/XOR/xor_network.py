import numpy as np
import tensorflow as tf
import random
import time

def get_batch(batch_size):
	options = [([0,1], [1, 0]), ([0,0], [1, 0]), ([1, 1], [0, 1]), ([1,0], [1, 0])]

	x = np.zeros([batch_size, 2], dtype='float')
	y = np.zeros([batch_size, 2], dtype='float')

	for i in xrange(0, batch_size):
		chosen = random.choice(options)
		x[i,:] = np.array(chosen[0], dtype='float').reshape([1,2])
		y[i,:] = np.array(chosen[1], dtype='float').reshape([1,2])
	return (x, y) 

	# for i in xrange(0, batch_size):
		# chosen = options[i]
		# x[i,:] = np.array(chosen[0], dtype='float').reshape([1,2])
		# y[i,:] = np.array(chosen[1], dtype='float').reshape([1,2])
	# return (x, y) 

# def variable_summaries(scope, variables):
	# """Attach a lot of summaries to a Tensor (for TensorBoard visualization)."""
	# with tf.variable_scope(scope, reuse = True):		
		# for var_name in variables:
			# var = tf.get_variable(var_name)
# 
			# mean = tf.reduce_mean(var)
			# stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
		# 
			# tf.summary.scalar('mean', mean)
			# tf.summary.scalar('stddev', stddev)
			# tf.summary.scalar('max', tf.reduce_max(var))
			# tf.summary.scalar('min', tf.reduce_min(var))
			# tf.summary.histogram('histogram', var)

def variable_summaries(var):
	"""Attach a lot of summaries to a Tensor (for TensorBoard visualization)."""
	with tf.name_scope('summary'):
		mean = tf.reduce_mean(var)
		tf.summary.scalar('mean', mean)
		with tf.name_scope('stddev'):
			stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
		tf.summary.scalar('stddev', stddev)
		tf.summary.scalar('max', tf.reduce_max(var))
		tf.summary.scalar('min', tf.reduce_min(var))
		tf.summary.histogram('histogram', var)

def add_fully_connected(x, input_dim, output_dim):
	with tf.name_scope('fc'):
		with tf.name_scope('weights'):
			weights = tf.Variable(tf.truncated_normal([input_dim, output_dim], mean=0, stddev=1/np.sqrt(2)), name='weights');
			variable_summaries(weights)
		with tf.name_scope('biases'):
			biases = tf.Variable(tf.zeros([output_dim]), name='biases')
			variable_summaries(biases)
	return tf.nn.relu(tf.matmul(x, weights) + biases)	

if __name__ == '__main__':
	batch_size = 100
	num_hidden = 7

	with tf.Graph().as_default():
		# with tf.device('/gpu:2'):
		# Define variables.
		x = tf.placeholder(tf.float32, [batch_size, 2], name='x')
		y = tf.placeholder(tf.float32, [batch_size, 2], name='y') 

		hidden0 = tf.nn.relu(add_fully_connected(x, 2, num_hidden))
		hidden1 = tf.nn.relu(add_fully_connected(hidden0, num_hidden, num_hidden))
		output = add_fully_connected(hidden1, num_hidden, 2)

		loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits = output, labels = y), name='loss')

		tf.summary.scalar('loss', loss)

		learning_rate = 0.2

		# optimizer = tf.train.AdamOptimizer(learning_rate)
		optimizer = tf.train.GradientDescentOptimizer(learning_rate)

		global_step = tf.Variable(0, name='global_step', trainable=False)
		optim = optimizer.minimize(loss, global_step=global_step)

		summary = tf.summary.merge_all()

		with tf.Session() as sess:
			summary_writer = tf.summary.FileWriter("train_dir", sess.graph)
			
			init = tf.global_variables_initializer()
			sess.run(init)	

			for step in xrange(1, 1000):
				data_x, data_y = get_batch(batch_size)
				feed_dict = {x: data_x, y: data_y}

				start_time = time.time()
				_, loss_value, summary_str = sess.run([optim, loss, summary],
                             feed_dict=feed_dict)
				duration = time.time() - start_time
				
				if step % 10 == 0:	
					summary_writer.add_summary(summary_str, step)

				if step % 100 == 0:
					# print data_x
					num_correct_op = tf.equal(tf.argmax(data_y, 1), tf.argmax(output, 1))
					accuracy = np.sum(sess.run(num_correct_op, feed_dict=feed_dict)) / float(batch_size)
					print 'Step %d: loss = %.2f, batch acc = %.2f (%.3f sec)' % (step, loss_value, accuracy, duration)	

			# check the results on some examples
			# for i in xrange(0,10):
				# data = get_batch()
				# f_dict = {x: data[0], y: data[1]}	
				# print f_dict
				# out = sess.run(output, f_dict)
				# print out[0, 0] > out[0, 1]
				# print out
				# print "\n"