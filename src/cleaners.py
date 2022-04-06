"""Text cleaning"""

class TextCleaner:
    
    def __init__(self, model, stop_words):
        self.model = model
        self.stop_words = stop_words
        
    def __call__(self, document):
        
        processed_doc = self._apply_pos_tagger(document)
        processed_doc = self._remove_punctuation(processed_doc)
        processed_doc = self._remove_stop_words(processed_doc)
        processed_doc = self._remove_double_spaces(processed_doc)
        processed_doc = self._remove_space_at_sentence_end(processed_doc)
        
        return processed_doc

    def _apply_pos_tagger(self, document):

        tokens = []
        for word in self.model(document):
            if word.pos_ in ['NOUN', 'ADJ', 'VERB', 'ADV', 'PUNCT']:
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
