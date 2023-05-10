import pickle


class Tokenizer:
    # TODO: get rid of this later
    def __init__(self, vocab):
        # create a mapping from characters to integers
        self.stoi = {ch: i for i, ch in enumerate(vocab)}
        self.itos = {i: ch for i, ch in enumerate(vocab)}

    def encode(self, s):
        # encoder: take a string, output a list of integers
        return [self.stoi[c] for c in s]

    def decode(self, l):
        # decoder: take a list of integers, output a string
        return ''.join([self.itos[i] for i in l])


class TokenizerUnpickler(pickle.Unpickler):

    def find_class(self, module, name):
        if name == 'Tokenizer':
            return Tokenizer
        return super().find_class(module, name)
