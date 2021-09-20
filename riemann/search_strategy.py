'''An interface describing search strategies.'''
# this import ensures we can have X as a return type for a method for class X
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from riemann import superabundant
from riemann import divisor
from riemann.superabundant import partition_to_prime_factorization
from riemann.superabundant import partitions_of_n
from typing import List
from typing import TypeVar

SearchState = TypeVar('SearchState')


class SearchStrategy(ABC):
    @abstractmethod
    def starting_from(self, search_state: SearchState) -> SearchStrategy:
        '''Reset the search strategy to search from a given state.'''
        pass

    @abstractmethod
    def search_state(self) -> SearchState:
        '''Get an object describing the current state of the enumeration.'''
        pass

    @abstractmethod
    def next_batch(self, batch_size: int) -> List[RiemannDivisorSum]:
        '''Process the next batch of Riemann Divisor Sums'''
        pass


class ExhaustiveSearchStrategy(SearchStrategy):
    '''A search strategy that tries every positive integer starting from 5041.'''

    def __init__(self):
        self.search_index = 5041

    def starting_from(self, search_state: int) -> ExhaustiveSearchStrategy:
        self.search_index = search_state
        return self

    def search_state(self) -> int:
        return self.search_index

    def next_batch(self, batch_size: int) -> List[RiemannDivisorSum]:
        ending_n = self.search_index + batch_size - 1
        sums = divisor.compute_riemann_divisor_sums(self.search_index,
                                                    ending_n)
        self.search_index = ending_n + 1
        return sums


@dataclass(frozen=True)
class SuperabundantEnumerationIndex:
    level: int
    index_in_level: int


class SuperabundantSearchStrategy(SearchStrategy):
    '''A search strategy that iterates over possibly superabundant numbers.'''

    def __init__(self):
        self.search_index = SuperabundantEnumerationIndex(level=1,
                                                          index_in_level=0)
        self.current_level = [[1]]
        self.__maybe_reset_current_level__()

    def starting_from(
        self, search_state: SuperabundantEnumerationIndex
    ) -> SuperabundantSearchStrategy:
        self.search_index = search_state
        self.__maybe_reset_current_level__()
        return self

    def search_state(self) -> SuperabundantEnumerationIndex:
        return self.search_index

    def next_batch(self, batch_size: int) -> List[RiemannDivisorSum]:
        sums = []
        '''
        Because a batch can cross multiple levels, we need to possibly split
        the batch into pieces.
        '''
        ending_level_index = self.search_index.index_in_level + batch_size - 1
        while ending_level_index >= len(self.current_level):
            for i in range(self.search_index.index_in_level,
                           len(self.current_level)):
                fac = partition_to_prime_factorization(self.current_level[i])
                sums.append(superabundant.compute_riemann_divisor_sum(fac))

            ending_level_index -= len(self.current_level)
            self.search_index = SuperabundantEnumerationIndex(
                level=self.search_index.level + 1, index_in_level=0)
            self.__maybe_reset_current_level__()  # definitely

        for i in range(self.search_index.index_in_level,
                       ending_level_index + 1):
            fac = partition_to_prime_factorization(self.current_level[i])
            sums.append(superabundant.compute_riemann_divisor_sum(fac))
            self.search_index = SuperabundantEnumerationIndex(
                level=self.search_index.level,
                index_in_level=self.search_index.index_in_level + 1)

        return sums

    def __maybe_reset_current_level__(self):
        '''Idempotently compute the next level of the enumeration.'''
        if self.current_level[0] != self.search_index.level:
            self.current_level = partitions_of_n(self.search_index.level)
