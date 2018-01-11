import chess
import chess.uci

handler = chess.uci.InfoHandler()
engine = chess.uci.popen_engine('stockfish') #give correct address of your engine here
engine.info_handlers.append(handler)

with open('../data/fen_games') as f:
    with open('../data/labels','w+') as label_file:
        for fen in f:
            board = chess.Board(fen)
            engine.position(board)
            evaluation = engine.go(depth=20)
            score = handler.info["score"][1].cp/100.0
            
            if score < 0:
                score = -1
            elif score > 0:
                score = 1
            else:
                score = 0
            label_file.write('{}\n'.format(score))
