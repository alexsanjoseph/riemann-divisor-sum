'''An interface for a database containing divisor sums.'''

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import List
from riemann.types import RiemannDivisorSum

@dataclass(frozen=True)
class SummaryStats:
    largest_computed_n: RiemannDivisorSum
    largest_witness_value: RiemannDivisorSum


class DivisorDb(ABC):

    @abstractmethod
    def load(self) -> List[RiemannDivisorSum]:
        '''Load the entire database.'''
        pass

    @abstractmethod
    def upsert(self, data: List[RiemannDivisorSum]) -> None:
        '''Insert or update the given list of data points.'''
        pass

    @abstractmethod
    def summarize(self) -> SummaryStats:
        '''Summarize the contents of the database.'''
        pass
