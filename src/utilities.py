from random import randint

def expandEmpty(char):

    """ expand empty places to spaces in fen """ 

    if char.isnumeric():
        piece = int(char) * "."
    else:
        piece = char
    return piece

def parsePieces(fen):

    """ get piece info from fen string """ 

    split = fen.split('/', 8)               # split ranks
    split[7] = split[7].split(' ')[0]       # remove extra info (?)
    parsedfen = ""                          # insert empty space
    for rank in split:
        for char in rank:
            parsedfen += expandEmpty(char)
    return parsedfen

def findPieces(parsedfen):

    """ create a position string for each piece """

    out = [0] * 64 * 4
    out[parsedfen.index('K')]             = 1             # white king
    out[parsedfen.index('k') + 64]        = 1             # black king
    out[parsedfen.index('N') + 2 * 64]    = 1             # white knight
    out[parsedfen.index('r') + 3 * 64]    = 1             # black rook
    return out

def fromFen(fenstring):

    """ convert fen notaton to bit notation """ 

    return findPieces(parsePieces(fenstring))

def toFen(bitmap):
    """toFen
    
    Convert bit notation to fen notation
    
    Arguments:
        bitmap {list} -- bit notation 64*4 with board for each piece
    """
    
    # Split board into pieces representation
    (K, k, N, r) = (bitmap[piece*64:piece*64+64] for piece in range(4))
    
    simplified_board = ['.'] * 64;

    simplified_board[K.index(1)] = 'K'
    simplified_board[k.index(1)] = 'k'
    simplified_board[N.index(1)] = 'N'
    simplified_board[r.index(1)] = 'r'

    fen = ""
    ind = 0
    blank = 0
    for ind in range(64):
        if simplified_board[ind] != '.':
            if blank != 0:
                fen += str(blank)
            fen += simplified_board[ind]
            blank = 0
        else:
            blank += 1

        if ind % 8 == 7:
            if blank > 0:
                fen += str(blank)
            fen+='/'
            blank = 0
    
    fen += ' {} - - 0 1'.format(['w','b'][randint(0,1)])

    return fen
        
if __name__ == "__main__":
    test = "rnbqkbnr/ppp2ppp/3p1p2/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    print(fromFen(test))