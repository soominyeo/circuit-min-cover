from functools import cached_property
from typing import Set, Callable


# a class for product of terms.
class Product:
    default_size = 0
    sort_one_first = False

    def __init__(self, terms, size: int = 0):
        self.terms = frozenset(terms)
        self.size = size if size != 0 else Product.default_size

    def __add__(self, other):
        return Product(self.terms | other.terms, size=max(self.size, other.size))

    def __eq__(self, other):
        return self.terms == other.terms and self.size == other.size

    def __hash__(self):
        return hash((self.terms, self.size))

    def __str__(self):
        if self.is_implicant:
            ovr_mask, ovr_portion = self.overlapping
            return ''.join(['-' if (ovr_mask >> i) & 1 == 0 \
                                else str((ovr_portion >> i) & 1) for i in reversed(range(self.size))])
        return ''.join(['[', *', '.join([bin(t)[2:].rjust(self.size, '0') for t in self.terms]), ']'])

    __repr__ = __str__

    def __contains__(self, other):
        if isinstance(other, Product):
            return self.size == other.size and self.terms.issuperset(other.terms)
        else:
            return other in self.terms

    def __iter__(self):
        return self.terms.__iter__()

    def __next(self):
        return self.__next()

    # check overlapping portion of all the terms, and return overlapping mask and portion.
    @cached_property
    def overlapping(self):
        mask = 2 ** self.size - 1
        portion, *terms = self.terms
        for term in terms:
            mask &= ~(portion ^ term)
        return mask, portion

    # return list of non-overlapping portions of all the terms.
    @cached_property
    def differences(self):
        mask, _ = self.overlapping
        return list(set(map(lambda t: t & ~mask, self.terms)))

    # checks if the Product is a valid implicant.
    @cached_property
    def is_implicant(self):
        # make sure non-overlapping portion includes all possible cases
        mask, _ = self.overlapping
        diffs = self.differences
        return len(diffs) == 2 ** (self.size - bin(mask)[2:].count('1'))

    def is_dominated_by(self, other: 'Product', cost: Callable[['Product'], float], minterms: Set[int] = None):
        if minterms:
            return self.size == other.size \
                   and (self.terms.intersection(minterms)).issubset(other.terms.intersection(minterms)) \
                   and cost(self) >= cost(other)
        else:
            return self in other

    # check if two product is combinable. Two product should be valid implicant
    def combinable(self, other: 'Product'):
        assert self.is_implicant and other.is_implicant
        return (self + other).is_implicant

    def sort_key(self, _sort_one_first: bool = None):
        sort_one_first = _sort_one_first if _sort_one_first is not None else Product.sort_one_first
        if self.is_implicant:
            ovr_mask, ovr_portion = self.overlapping
            overlapping = int(bin(ovr_portion)[2:], 3)
            non_overlapping = int(bin((2 ** self.size - 1) ^ ovr_mask)[2:], 3)
            return overlapping * 2 + non_overlapping if sort_one_first else overlapping + non_overlapping * 2
        else:
            return -1
