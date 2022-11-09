"""main.py

Defines the NBSpaceRestorer class"""

import operator
import os
from collections import Counter
from functools import lru_cache, reduce
from math import log10
from typing import List, Tuple, Optional, Union

import nltk
import psutil

from nb_space_restorer.nb_helper import (get_tqdm, load_pickle,
                           mk_dir_if_does_not_exist, save_pickle)
from nb_space_restorer.nb_space_restorer_grid_search import NBSpaceRestorerGridSearch

tqdm_ = get_tqdm()

FREQS_FNAME = 'FREQS.pickle'
GRID_SEARCH_PATH_NAME = 'grid_searches'
MAX_CACHE_SIZE = 10_000_000

ERROR_FOLDER_EXISTS = """\
There is already a NB Space Restorer at this path. \
Either choose a new path, or load the existing NB Space Restorer"""
MESSAGE_FINISHED_LOADING = "Finished loading model."
MESSAGE_TRAINING_COMPLETE = "Training complete."


# ====================
class NBSpaceRestorer():

    # ====================
    def __init__(self,
                 train_texts: list,
                 ignore_case: bool = True,
                 save_folder: Optional[str] = None):
        """Initalize and train an instance of the class.

        Args:
          train_texts (list):
            The list of 'gold standard' documents (running text with spaces)
            on which to train the model.
          ignore_case (bool, optional):
            Whether or not to ignore case during training (so that e.g.
            'banana', 'Banana', and 'BANANA' are all counted as instances
            of 'banana'). Defaults to True.
          save_folder (Optional[str], optional):
            If specified, model assets are saved to the folder at the path
            specified so that the model can be loaded later. Defaults to None.

        Raises:
          ValueError:
            If the folder specified in save_folder already exists.
        """

        if save_folder:
            if os.path.exists(save_folder):
                raise ValueError(ERROR_FOLDER_EXISTS)
            mk_dir_if_does_not_exist(save_folder)
            self.root_folder = save_folder
        self.unigram_freqs: Counter = Counter()
        self.bigram_freqs: Counter = Counter()
        for text in train_texts:
            if ignore_case:
                text = text.lower()
            words = text.split()
            self.unigram_freqs.update(words)
            bigrams = [
                f'{first_word}_{second_word}'
                for first_word, second_word in list(nltk.bigrams(words))
            ]
            self.bigram_freqs.update(bigrams)
        freqs = {
            'unigram_freqs': self.unigram_freqs,
            'bigram_freqs': self.bigram_freqs
        }
        if hasattr(self, 'root_folder'):
            save_pickle(freqs, self.freqs_path())
        print(MESSAGE_TRAINING_COMPLETE)
        self.get_pdists()

    # ====================
    @classmethod
    def load(cls, load_folder: str) -> 'NBSpaceRestorer':
        """Load a previously saved instance of the class.

        Args:
          load_folder (str):
            The root folder that contains the instance assets
            (the same path that was passed as save_folder when the
            class instance was initialized.)

        Returns:
          NBSpaceRestorer:
            The loaded class instance.
        """

        self = cls.__new__(cls)
        self.root_folder = load_folder
        self.unigram_freqs, self.bigram_freqs = \
            self.get_freqs()
        print(MESSAGE_FINISHED_LOADING)
        self.get_pdists()
        return self

    # ====================
    def set_L(self, L: int):

        self.L = L

    # ====================
    def set_lambda_(self, lambda_: float):

        self.lambda_ = lambda_

    # ====================
    def freqs_path(self):

        return os.path.join(self.root_folder, FREQS_FNAME)

    # ====================
    def get_freqs(self):

        freqs = load_pickle(self.freqs_path())
        return freqs['unigram_freqs'], freqs['bigram_freqs']

    # ====================
    def get_pdists(self):
        """Get unigram and bigram probability distributions from unigram
        and bigram frequencies"""

        # Get total numbers of unigrams and bigrams
        self.N = sum(self.unigram_freqs.values())
        self.N2 = sum(self.bigram_freqs.values())
        # Define probability distributions for unigrams and bigrams
        self.Pdist = {word: freq / self.N
                      for word, freq in self.unigram_freqs.items()}
        self.P2dist = {bigram: freq / self.N2
                       for bigram, freq in self.bigram_freqs.items()}

    # ====================
    def splits(self, text: str) -> List[tuple]:
        """Split text into a list of candidate (word, remainder) pairs.

        Args:
          text (str):
            An unspaced input text

        Returns:
          List[tuple]:
            A list of candidate (word, remainder) pairs
        """

        return [
            (text[:i+1], text[i+1:]) for i in range(min(len(text), self.L))
        ]

    # ====================
    @staticmethod
    def product(lis_: List[float]) -> float:
        """Product of a list of numbers

        Args:
          lis_ (List[float]):
            A list of floats

        Returns:
          float:
            The product of the floats in the input list
        """

        return reduce(operator.mul, lis_, 1)

    # ====================
    def Pwords(self, words: List[str]) -> float:
        """Get Naive Bayes probability of a sequence of words.

        Args:
          words (List[str]):
            A list of words

        Returns:
          float:
            The NB probability
        """

        return self.product([self.Pw(w) for w in words])

    # ====================
    def Pw(self, word: str) -> float:
        """Get Naive Bayes probability of a single word

        Args:
          word (str):
            A single candidate word

        Returns:
          float:
            The NB probability
        """

        if word in self.Pdist:
            return self.Pdist[word]
        else:
            # For unknown words, assign lower probabilities for longer words
            return self.lambda_/(self.N * 10 ** len(word))

    # ====================
    def cPw(self, word: str, prev: str) -> float:
        """Get the conditional probability of a word given the previous word.

        Args:
          word (str):
            The candidate word
          prev (str):
            The previous word

        Returns:
            float: The Naive Bayes probability
        """

        try:
            return self.P2dist[prev + '_' + word] / float(self.Pw(prev))
        except KeyError:
            return self.Pw(word)

    # ====================
    def combine(self,
                Pfirst: float,
                first: str,
                rem_: Tuple[float, list]) -> Tuple[float, list]:
        """Combine the probability of a word, the word, and list of remaining
        words together with their probability to return the combined
        probability and combined list of words.

        Args:
          Pfirst (float):
            Probability of the first word
          first (str):
            The first word
          rem_ (Tuple[float, list]):
            The probability of the remaining words, and the list of words

        Returns:
          Tuple[float, list]:
            The combined probability and combined list of words
        """

        Prem, rem = rem_
        return Pfirst + Prem, [first] + rem

    # ====================
    @lru_cache(maxsize=MAX_CACHE_SIZE)
    def restore_chunk(self, text_: str, prev='<S>') -> Tuple[float, list]:
        """Restore spaces to a short string of input characters

        Will result in RecursionError if length of text_ is more than
        around 100.

        Args:
          text_ (str):
            The text to restore spaces to.
          prev (str, optional):
            The previous word. Defaults to '<S>'.

        Returns:
          Tuple[float, list]:
            The probability of the most likely split, and the list of
            words
        """

        if not text_:
            return 0.0, []
        candidates = [self.combine(log10(self.cPw(first, prev)),
                                   first,
                                   self.restore_chunk(rem, first))
                      for first, rem in self.splits(text_)]
        return max(candidates)

    # ====================
    def restore_doc(self,
                    text: str,
                    show_chunks: bool = False) -> str:
        """Restore spaces to a string of input characters of arbitrary
        length.

        For strings over around 100 characters in length, break them
        into chunks for segmentation and then put the words back together
        to avoid recursion limit errors.

        Args:
          text (str):
            The text to restore spaces to
          show_chunks (bool, optional):
            Whether to print out information about each chunk.
            Defaults to False.

        Returns:
          str:
            The document with spaces restored
        """

        chunk_len_chars = 80   # Low enough to avoid recursion errors
        all_words = []
        prefix = ''
        chunk_counter = 1
        # Iterate over chunks of the input string
        for offset in range(0, len(text), chunk_len_chars):
            # Prefix with the last five 'words' from the previous segmentation
            text_to_segment = prefix + text[offset:offset + chunk_len_chars]
            chunk_segmented = self.restore_chunk(text_to_segment)[1].copy()
            # Words may have been cut off at the end, so put the last five
            # words back into the segmenter next time round and discard them
            # this time
            prefix = ''.join(chunk_segmented[-5:])
            all_words.extend(chunk_segmented[:-5])
            if show_chunks:
                print(f'Chunk {chunk_counter}')
                print(f'Text segmented: {text_to_segment}')
                print(f'Result of segmentation: {chunk_segmented}')
                print(f'Words added to list this time: {chunk_segmented[:-5]}')
                print(f'Prefix for next chunk: {prefix}')
                print(f'Words added to list so far: {all_words}')
                print('-' * 100)
                chunk_counter += 1
        # Add any text remaining in 'prefix'
        all_words.extend(self.restore_chunk(prefix)[1])
        joined = ' '.join(all_words).strip()
        return joined

    # ====================
    def restore(self,
                texts: Union[str, List[str]],
                L: int = 20,
                lambda_: float = 10.0) -> Union[str, List[str]]:
        """Restore spaces to either a single string, or a list of
        strings.

        Args:
          texts (Union[str, List[str]]):
            Either a single string of input characters not containing spaces
            (e.g. 'thisisasentence') or a list of such strings
          L (int, optional):
            The maximum possible word length to consider during inference.
            Inference time increases with L as more probabilities need to
            be calculated. Defaults to 20.
          lambda_ (float, optional):
            The smoothing parameter to use during inference. Higher values
            of lambda_ cause higher probabilities to be assigned to words
            not learnt during training.

        Returns:
          Union[str, List[str]]:
            The string or list of strings with spaces restored
        """

        self.set_L(L)
        self.set_lambda_(lambda_)
        if isinstance(texts, str):
            return self.restore_doc(texts)
        if isinstance(texts, list):
            restored = []
            texts_ = tqdm_(texts)
            for text in texts_:
                restored_ = self.restore_doc(text)
                restored.append(restored_)
                cache_size = self.restore_chunk.cache_info().currsize
                texts_.set_postfix({
                    'ram_usage': f"{psutil.virtual_memory().percent}%",
                    'cache_size': f"{cache_size:,}"
                })
            return restored

    # === GRID SEARCH ===

    # ====================
    def add_grid_search(self,
                        grid_search_name: str,
                        L: list,
                        lambda_: list,
                        ref: list,
                        input: list):

        attrs = locals()
        del attrs['self']
        self.grid_search = NBSpaceRestorerGridSearch(self, **attrs)

    # ====================
    def load_grid_search(self,
                         grid_search_name: str):

        self.grid_search = \
            NBSpaceRestorerGridSearch.load(self, grid_search_name)

    # ====================
    def grid_search_path(self):

        return os.path.join(self.root_folder, GRID_SEARCH_PATH_NAME)