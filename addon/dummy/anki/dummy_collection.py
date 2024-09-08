from .dummy_deck import Deck
from .dummy_notes import Note
from .dummy_models import Model

class Collection:
    decks = Deck
    models = Model

    @staticmethod
    def reset():
        pass

    @staticmethod
    def remNotes(*args, **kwargs):
        pass

    @staticmethod
    def getNote(nid):
        return Note(nid)

    @staticmethod
    def findNotes():
        return []
