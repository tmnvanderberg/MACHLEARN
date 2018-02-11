import argparse
import tensorflow as tf
import random as r
import utilities as u
import numpy as np
from datetime import datetime
import os
import sys
from benchmarker import benchmark
from random_player import RandomPlayer
from stock_agent import StockAgent
from agent import Agent
from mlp_bitmaps import MlpBitmaps
from cnn import CNN

class SupervisedLearning( Agent ):
    def __init__(self, model, session=None, session_path=None, wd=None, session_name=None):
        super()
        self.wd = wd
        self.model = model
        self.session_name = session_name
        if self.wd is None:
            self.wd = os.getcwd()
        if self.session_name is None:
            self.session_name = 'SL_MLP'
        
        self.save_path = self.wd+'/learnt/'+self.session_name+'/'

        if not os.path.exists(self.wd):
            os.makedirs(self.wd)
        if not os.path.exists(self.wd+'/datasets/'):
            os.makedirs(self.wd+'/datasets/')
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.batch_size = 256

        self.X = self.model.X
        self.Y = tf.placeholder("float", shape=[None, self.model.out])

        self.Y_true_cls = tf.argmax(self.Y, dimension=1)

        self.ev = self.model.ev

       # self.loss_op = tf.losses.mean_squared_error(labels=self.Y, predictions=self.ev)
       # self.optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.02)
       # self.train_op = self.optimizer.minimize(self.loss_op)

        self.cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=self.model.last_layer,
                                                        labels=self.Y)
        self.loss_op = tf.reduce_mean(self.cross_entropy)
        self.train_op = tf.train.AdamOptimizer().minimize(self.loss_op)
        # self.train_op = tf.train.GradientDescentOptimizer(learning_rate=1e-2).minimize(self.loss_op)



        # to check accuracy 
        self.correct_prediction = tf.equal(self.ev, self.Y_true_cls)
        self.accuracy_test= tf.reduce_mean(tf.cast(self.correct_prediction, tf.float32))
        
        self.accuracy_train = tf.reduce_mean(tf.cast(self.correct_prediction, tf.float32))

        # summary. Need to differentiate between test and training..
        self.summary_train = tf.summary.scalar("accuracy train", self.accuracy_train)
        self.summary_test = tf.summary.scalar("accuracy test", self.accuracy_test)
        self.summary_loss = tf.summary.scalar("loss/error", self.loss_op)

        self.init = tf.global_variables_initializer()

        self.session = tf.Session()
        self.session.run(self.init)
        
        self.saver = tf.train.Saver()

        if session is not None:
            self.session = session
        elif session_path is not None:
            self.saver.restore(self.session, session_path)


    def convert_input(self, fen):
        return np.array(u.fromFen(fen)).reshape((1,258))
    
    def alphabeta(self, board, depth=2, alpha=float('-Inf'), beta=float('+Inf'), _max=True):
        
        if board.is_game_over():
            #Find out absolute value of result (1-0 white wins, 0-1 black losses)
            raw_result = board.result()
            
            if raw_result == '1-0':
                result = 1
            elif raw_result == '0-1':
                result = -1
            else:
                result = 0
            
            #Convert outcome to relative (if root is white we leave it as it is, otherwise it's the negative)
            result = result * np.sign(int(board.turn) - .5)
            return (board.fen(), result)

        if depth == 0:
            return (board.fen(), int(self.session.run(self.ev, feed_dict={self.X: self.convert_input(board.fen())})) - 1)

        if _max:
            v = float('-Inf')
            win_leaf = ''
            for move in board.legal_moves:
                board.push(move)
                leaf, score = self.alphabeta(board,depth-1, alpha, beta, False)
                board.pop()
                if score > v:
                    v = score
                    win_leaf = leaf
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return (win_leaf, v)
        else:
            v = float('Inf')
            for move in board.legal_moves:
                board.push(move)
                leaf, score = self.alphabeta(board,depth-1, alpha, beta, True)
                board.pop()
                if score < v:
                    v = score
                    win_leaf = leaf
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return (win_leaf, v)

    def train(self):
        save_file_name = self.save_path+'{}.ckpt'.format(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
        errors = []

        x, y, test_games = SupervisedLearning.prepare_data(self.wd)
        
        

        #should i put a self here ?
        #merged_summary = tf.summary.merge_all()
        writer = tf.summary.FileWriter(self.save_path, filename_suffix=datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))        

        


        improved_random, deproved_random, advantage_kept_random = benchmark(self, RandomPlayer(), test_games)
        improved_stock, deproved_stock, advantage_kept_stock = benchmark(self, StockAgent(depth=4), test_games)
        summary=tf.Summary()
        summary.value.add(tag='improved_random', simple_value = improved_random)
        summary.value.add(tag='deproved_random', simple_value = deproved_random)
        summary.value.add(tag='advantage_kept_random', simple_value = advantage_kept_random)
        summary.value.add(tag='improved_stock', simple_value = improved_stock)
        summary.value.add(tag='deproved_stock', simple_value = deproved_stock)
        summary.value.add(tag='advantage_kept_stock', simple_value = advantage_kept_stock)
        writer.add_summary(summary, 0)
        writer.flush()

        self.saver.restore(self.session, '/data/s3485781/learnt/sl_mlp_for_presentation/2018-01-23_23:34:56.ckpt')

        improved_random, deproved_random, advantage_kept_random = benchmark(self, RandomPlayer(), test_games)
        improved_stock, deproved_stock, advantage_kept_stock = benchmark(self, StockAgent(depth=4), test_games)
        summary=tf.Summary()
        summary.value.add(tag='improved_random', simple_value = improved_random)
        summary.value.add(tag='deproved_random', simple_value = deproved_random)
        summary.value.add(tag='advantage_kept_random', simple_value = advantage_kept_random)
        summary.value.add(tag='improved_stock', simple_value = improved_stock)
        summary.value.add(tag='deproved_stock', simple_value = deproved_stock)
        summary.value.add(tag='advantage_kept_stock', simple_value = advantage_kept_stock)
        writer.add_summary(summary, 1)
        writer.flush()
        


    def evaluate(self, fen, figure='r'):
        x = u.fromFen(fen,figure)
        return self.session.run(self.ev, feed_dict={self.X: np.array(x).reshape(1,258)}) - 1
    

    def next_action(self, board):
        wins = []
        losses = []
        draws = []
        
        for move in board.legal_moves:
            board.push(move)

            score = self.alphabeta(board)
            
            if score == 0:
                draws.append(move)
            if score == 1:
                wins.append(move)
            else:
                losses.append(move)
            board.pop()
            
        #Make sure we have at least one candidate move
        assert(wins or losses or draws)

        if len(wins) > 0:
            return r.choice(wins)
        elif len(draws) > 0:
            return r.choice(draws)
        else:
            return r.choice(losses)

    @staticmethod
    def prepare_data(wd):
        with open(wd+'/datasets/fen_games') as f:
            data = f.readlines()

        with open(wd+'/datasets/labels') as f:
            labels = f.readlines()
        
        x = []
        y = []

        for idx in range(len(data)):
        # for idx in range(100):
            x.append(np.array(u.fromFen(data[idx], figure='r')))
            if int(labels[idx]) == 1:
                y.append([0,0,1])
            elif int(labels[idx]) == -1:
                y.append([1,0,0])
            else:
                y.append([0,1,0])
        
        return x, y, data[len(data)-250:len(data)]

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', default='../data')
    parser.add_argument('-n', '--name_session', default='RL')
    parser.add_argument('-m', '--model')

    args = parser.parse_args()

    wd = args.directory
    sn = args.name_session

    if args.model == 'mlp':
        model = MlpBitmaps()
    elif args.model == 'cnn':
        model = CNN()
    else:
        print('Model {} not found'.format(args.model))
        quit()
    
    model = SupervisedLearning(model=model, wd=wd, session_name=sn)

    model.train()