import tensorflow as tf

class MlpFeatures( object ):
    def __init__(self):
        
        self.n_general = 3; self.n_piece_c = 12; self.n_square_c = 128
        self.n_input = self.n_general + self.n_piece_c + self.n_square_c
        self.n_hidden_2 = 9

        self.X = tf.placeholder("float", shape=[None, self.n_input])

        self.weights = {
            'general': tf.Variable(tf.random_normal([self.n_general, self.n_general])),
            'piece_c': tf.Variable(tf.random_normal([self.n_piece_c, self.n_piece_c])),
            'square_c': tf.Variable(tf.random_normal([self.n_square_c, self.n_square_c])),
            'hidden_2': tf.Variable(tf.random_normal([self.n_input, self.n_hidden_2])),
            'out': tf.Variable(tf.random_normal([self.n_hidden_2, 1]))
        }
        self.biases = {
            'b1': tf.Variable(tf.random_normal([self.n_input])),
            'b2': tf.Variable(tf.random_normal([self.n_hidden_2])),
            'out': tf.Variable(tf.random_normal([1]))
        }

        # Locally connected layers
        general_i = tf.gather(self.X,tf.convert_to_tensor(list(range(self.n_general)), dtype=tf.int32),axis=1)
        piece_i = tf.gather(self.X,tf.convert_to_tensor(list(range(self.n_general,self.n_general+self.n_piece_c)), dtype=tf.int32), axis=1)
        square_i = tf.gather(self.X,tf.convert_to_tensor(list(range(self.n_general+self.n_piece_c, self.n_general + self.n_piece_c + self.n_square_c)), dtype=tf.int32), axis=1)
        general = tf.matmul(general_i, self.weights['general'])
        piece_c = tf.matmul(piece_i, self.weights['piece_c'])
        square_c = tf.matmul(square_i, self.weights['square_c'])
        hidden_1 = tf.nn.relu(tf.add(tf.concat([general, piece_c, square_c], 1), self.biases['b1']))
        # Fully connected layer
        hidden_2 = tf.nn.relu(tf.add(tf.matmul(hidden_1, self.weights['hidden_2']), self.biases['b2']))
        # Output layer
        self.ev = tf.tanh(tf.add(tf.matmul(hidden_2, self.weights['out']), self.biases['out']))

        self.trainables = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
        
    
