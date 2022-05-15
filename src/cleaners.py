"""Text cleaning pipeline."""
import re

from nlpiper.core import Compose
from nlpiper.transformers import cleaners
from nlpiper.core import Document

from resources.articles import HEADERS, FOOTERS


class TextCleaner:
    
    def __init__(self, model, stop_words):
        self.model = model
        self.stop_words = stop_words
        self.nlp_piper_pipeline = Compose([
            cleaners.CleanURL(),
            cleaners.CleanEOF(),
            cleaners.CleanMarkup(),
            cleaners.CleanAccents(),
            cleaners.CleanNumber()
        ])
        
    def __call__(self, document):

        
        processed_doc = self._remove_footer_noise(document)
        processed_doc = self._remove_header_noise(processed_doc)

        processed_doc = Document(processed_doc.lower())
        processed_doc = self.nlp_piper_pipeline(processed_doc).cleaned

        processed_doc = self._apply_pos_tagger(processed_doc)
        processed_doc = self._remove_punctuation(processed_doc)
        processed_doc = self._remove_stop_words(processed_doc)
        processed_doc = self._remove_double_spaces(processed_doc)
        processed_doc = self._remove_space_at_sentence_end(processed_doc)
        
        return processed_doc

    def _apply_pos_tagger(self, document):

        tokens = []
        for word in self.model(document):
            if word.pos_ in ['PROPN', 'NOUN', 'ADJ', 'VERB', 'ADV', 'PUNCT']:
                tokens.append(word.text)
        return ' '.join(tokens)

    def _remove_stop_words(self, document):
        return ' '.join([word for word in document.split(' ') if word not in self.stop_words])        

    def _remove_double_spaces(self, document):
        return document.replace('  ', ' ')

    def _remove_punctuation(self, document):
        punctuation =  '!"#$%&\'()*+,-/:;<=>?@[\\]”^“_`{|}~'
        return document.translate(str.maketrans('', '', punctuation))

    def _remove_space_at_sentence_end(self, document):
        return document.replace(' .', '.')  

    def _remove_header_noise(self, document):
        doc = document
        for noise in HEADERS:
            doc =  re.sub(noise, '', doc)
        return doc
    
    def _remove_footer_noise(self, document):
        doc = document
        for noise in FOOTERS:
            doc =  re.sub(noise, '', doc)
        return doc
