import typing
from math import log10
from string import punctuation

from django.db import models
from pymorphy2 import MorphAnalyzer

morph: typing.Final = MorphAnalyzer()


# Create your models here.
class Document(models.Model):
    title = models.CharField(max_length=1000)
    text = models.TextField(max_length=10000)

    def get_words(self) -> typing.Dict[str, int]:
        words = {}
        for separated_word in self.text.split():
            word = separated_word[:-1] if separated_word.endswith(punctuation) else separated_word
            word = morph.parse(word)[0].normalized
            if not {'PREP', 'CONJ', 'PRCL', 'INTJ'} in word.tag:
                word = word.word
                if word in words:
                    words[word] += 1
                else:
                    words[word] = 1
        return words

    def tf_max(self) -> int:
        return max(self.get_words().values())

    def tf(self, t: str) -> int:
        return self.get_words().get(t, 0)

    @staticmethod
    def df(t: str) -> int:
        count = 0
        for doc in Document.objects.all():
            if t in doc.get_words():
                count += 1
        return count

    def w(self, t: str):
        try:
            return 0.5 * (1 + (self.tf(t) / self.tf_max())) * log10((Document.objects.count() / self.df(t)))
        except ZeroDivisionError:
            print(t)
            return 0

    @staticmethod
    def tf_s(t: str, s: str) -> int:
        count = 0
        for separated_word in s.split():
            word = separated_word[:-1] if separated_word.endswith((',', '.', '-', '!', '?', ';')) else separated_word
            word = morph.parse(word)[0].normalized
            if {'PREP', 'CONJ', 'PRCL', 'INTJ'} in word.tag:
                continue
            else:
                word = word.word
            if word == morph.parse(t)[0].normalized.word:
                count += 1
        return count

    def get_sentences(self) -> typing.List[str]:
        return [s.replace('\n', ' ').strip() for s in self.text.split('.')]

    def sent_score(self, s: str) -> float:
        score = 0
        for t in s.split():
            if t.endswith((',', '.', '-', '!', '?', ';')):
                t = t[:-1]
            t = morph.parse(t)[0].normalized
            if {'PREP', 'CONJ', 'PRCL', 'INTJ'} in t.tag:
                continue
            else:
                t = t.word
            score += self.tf_s(t, s) * self.w(t)
        return score

    def posd(self, s: str) -> float:
        doc = self.text
        pre, _, post = doc.partition(s)
        return 1 - (len(pre) / len(doc))

    def posp(self, s: str) -> float:
        paragraphs = self.text.split('\n\n')
        for paragraph in paragraphs:
            if s in paragraph:
                pre, _, post = paragraph.partition(s)
                return 1 - (len(pre) / len(paragraph))
        return 0

    def sent_weight(self, s: str) -> float:
        return self.posd(s) * self.posp(s) * self.sent_score(s)

    def sents_weights(self) -> typing.Dict[str, float]:
        return {s: self.sent_weight(s) for s in self.get_sentences()}
