"""A Very Simple Chess Library"""

class Board(tuple):
    """Stores internal representation of a Chess Board"""
    RANKS = '12345678'
    FILES = 'abcdefgh'

    def __new__(cls, position=None):
        """
        Represents a Chess Board

        position is the current state of the board, in limted FEN
        By default:
        rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
        """
        
        if not position:
            position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        records = position.split(' ')

        # We only need the first FEN field, the rest is game state
        ranks = records[0].split('/')
        assert len(ranks) == 8

        # FEN ranks are reversed
        ranks = (tuple(rank) for rank in reversed(ranks))
        
        def intfill(unfilled_rank):
            rank = []
            for file in unfilled_rank:
                if file in 'rnbqkpRNBQKP':
                    rank.append(file)
                else:
                    rank.extend([None] * int(file))
            return tuple(rank)

        ranks = tuple(intfill(rank) for rank in ranks)

        for rank in ranks:
            assert len(rank) == 8

        return tuple.__new__(cls, ranks)

    @classmethod
    def _new_raw(cls, *args, **kwargs):
        return tuple.__new__(cls, *args, **kwargs)
    
    def piece_at(self, position):
        """Returns the piece at the given board position"""
        assert len(position) == 2
        rank = self.RANKS.index(position[1])
        file = self.FILES.index(position[0])

        return self[rank][file]

    def positions_for(self, piece):
        """Returns the positions that have a given piece"""
        positions = []
        for i, rank in enumerate(self):
            for j, file in enumerate(rank):
                if file == piece:
                    positions.append(
                        self.FILES[i] +
                        self.RANKS[j])
        return tuple(positions)

    def fen(self):
        """Render board in FEN format"""
        ranks = []
        for rank in reversed(self):
            files = []
            empty = 0
            for file in rank:
                if file is None:
                    empty += 1
                else:
                    if empty != 0:
                        files.append(str(empty))
                        empty = 0
                    files.append(file)
            if empty != 0:
                files.append(str(empty))
            ranks.append(''.join(files))
        return '/'.join(ranks)

    def move(self, old, new, replace=None):
        """
        Returns a new board, after the given move.

        Captures happen naively, and the square moved from is
        left empty.
        """
        old_rank = self.RANKS.index(old[1])
        old_file = self.FILES.index(old[0])
        new_rank = self.RANKS.index(new[1])
        new_file = self.FILES.index(new[0])
        piece = replace or self[old_rank][old_file]
        new = [list(rank) for rank in self] 
        new[old_rank][old_file] = None
        new[new_rank][new_file] = piece
        return self._new_raw(tuple(rank) for rank in new)

    def __getitem__(self, val):
        if isinstance(val, slice):
            raise NotImplemented()
        if isinstance(val, int):
            return tuple.__getitem__(self, val)
        try:
            return self.piece_at(val)
        except (AssertionError, IndexError):
            raise KeyError('Invalid position: {}'.format(val))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.fen()))



class Game(object):
    """Represents a Game, including a move log"""

    def __init__(self):
        self._moves = ''
        self._board = Board()
