from typing import Iterable, Callable, Set
from product import Product


def find_pis(n, minterms: Iterable[int], dterms: Iterable[int] = None):
    if dterms is None:
        dterms = []
    terms = list(map(lambda t: Product([t], size=n), [*minterms, *dterms]))
    implicants = set()
    while terms:
        # find all combined
        combined = {i + j for i in terms for j in terms if i is not j and i.combinable(j)}
        new_implicants = {t for t in terms if all(map(lambda a: t not in a, combined))}
        implicants |= new_implicants
        terms = combined

    return [i for i in implicants if not any(map(lambda j: j != i and i in j, implicants))]


def find_epis(n, minterms: Iterable[int], _pis: Iterable[Product] = None, dterms: Iterable[int] = None):
    pis = _pis if _pis else find_pis(n, minterms, dterms)
    count = {term: sum(1 for _ in pis for t in _ if term == t) for term in minterms}
    # print(count)
    return [i for i in pis if any(map(lambda t: t in count and count[t] == 1, i.terms))]


# noinspection PyTypeChecker
def find_min_cover(n, _minterms: Iterable[int],
                   dterms: Iterable[int] = None,
                   _pis: Iterable[Product] = None, _epis: Iterable[Product] = None,
                   input_cost: int = None, output_cost: int = None, petrick_only: bool = None,
                   print_detail: bool = True):
    input_cost = input_cost if input_cost else 1
    output_cost = output_cost if output_cost else 1
    petrick_only = petrick_only if petrick_only else False

    def cost(product: Product) -> float:
        overlapping_mask, _ = product.overlapping
        input_count = bin(overlapping_mask)[2:].count('1')
        output_count = 1
        return input_count * input_cost + output_count * output_cost

    # Process(1): Find all PIs
    pis = set(_pis if _pis else find_pis(n, _minterms, dterms))
    epis = set()
    nepis = set(pis)
    minterms = set(_minterms)

    if print_detail:
        print_process(1, "Find all PIs", pis=pis, epis=epis, nepis=nepis, minterms=minterms)

    while True:
        # Process(2): Find all EPIs
        epis |= set(find_epis(n, minterms, pis))
        minterms -= {t for i in epis for t in i}
        nepis -= epis
        if print_detail:
            print_process(2, "Find all EPIs", pis=pis, epis=epis, nepis=nepis, minterms=minterms)

        # quit if no NEPIs remained
        if not nepis:
            return epis, nepis

        if petrick_only:
            break

        before = epis, nepis, minterms

        # Process(3): Apply column dominance
        epis, nepis, minterms = column_dominance(minterms, epis, nepis)
        if print_detail:
            print_process(3, "Apply column dominance", pis=pis, epis=epis, nepis=nepis, minterms=minterms)

        # Process(4): Apply row dominance
        epis, nepis, minterms = row_dominance(minterms, epis, nepis, cost)
        if print_detail:
            print_process(4, "Apply row dominance", pis=pis, epis=epis, nepis=nepis, minterms=minterms)

        # check if any simplification made or no minterm left
        if before[0] == epis and before[1] == nepis and before[2] == minterms:
            break

    if minterms and nepis:
        # Process(5): Apply Petrick's method
        minterms, epis, nepis = petricks_method(minterms, epis, nepis, cost)
        if print_detail:
            print_process(5, "Apply Petrick's method", pis=pis, epis=epis, nepis=nepis, minterms=minterms)

    return epis, nepis


def print_process(num: int, title: str, **kwargs):
    if print_process:
        print(f"Process({num}): {title}:", end='')
        value_sorted = {k: (sorted(v, key=Product.sort_key) if k in ('pis', 'epis', 'nepis') else v) for k, v in kwargs.items()}
        value_pretty = [k + '=' + (str(v) if v else "EMPTY") for k, v in value_sorted.items()]
        print(', '.join(value_pretty))


def row_dominance(_minterms: Iterable[int], _epis: Iterable[Product], _nepis: Iterable[Product],
                  cost: Callable[[Product], float]):
    epis, nepis, minterms = set(_epis), set(_nepis), set(_minterms)
    dominants = get_row_dominants(nepis, minterms, cost)
    while dominants:
        for d in dominants:
            epis.add(d)
            nepis.remove(d)
            minterms -= d.terms
        if not minterms:
            break
        dominants = get_row_dominants(nepis, minterms, cost)
    return epis, nepis, minterms


def get_row_dominants(nepis: Set[Product], minterms: Set[int], cost: Callable[[Product], float]):
    dominators = {}
    for i in nepis:
        if not i.terms.intersection(minterms):
            continue
        dominator = next((other for other in nepis if i != other and i.is_dominated_by(other, cost, minterms)), None)
        if dominator:
            dominators[i] = dominator
    # print(dominators)
    # choose dominant implicants those not dominated by others or sharing same cost and same terms
    dominants = [i for i in nepis if i in dominators.values() and
                 (i not in dominators.keys() or dominators[i] in dominators and dominators[
                     dominators[i]] == i and i.sort_key() < dominators[i].sort_key())]
    return dominants


def column_dominance(_minterms: Iterable[int], _epis: Iterable[Product], _nepis: Iterable[Product]):
    epis, nepis, minterms = set(_epis), set(_nepis), set(_minterms)
    dominators = {}
    assoc_impls = {t: set(i for i in nepis if t in i) for t in minterms}
    for t in minterms:
        dominator = next((other for other in minterms if t != other and assoc_impls[t].issubset(assoc_impls[other])),
                         None)
        if dominator:
            dominators[t] = dominator
    subservient = {t for t in minterms if t in dominators.keys()}
    minterms -= subservient
    return epis, nepis, minterms


def petricks_method(_minterms: Iterable[int], _epis: Iterable[Product], _nepis: Iterable[Product],
                    cost: Callable[[Product], float]):
    epis, nepis, minterms = set(_epis), list(_nepis), set(_minterms)
    assoc_impls = {t: set(i for i in nepis if t in i) for t in minterms}
    size = len(nepis)
    max_bits = 2 ** (size + 1)
    # for each term and its associated NEPIs, find combinations of NEPIs that satisfies the term
    p_maxterms = {term: [any(case & (1 << nepis.index(i)) != 0 for i in impls) for case in range(max_bits)]
                  for term, impls in assoc_impls.items()}
    # find combinations of NEPIs that satisfies all the terms
    p_total = [all(p_maxterms[term][i] for term in minterms) for i in range(max_bits)]

    # optimize cost
    optimizing_epis_bit, cost = min(
        ((p, sum(cost(nepis[i]) for i in range(size) if p >> i & 1 == 1)) for p in range(max_bits) if p_total[p]),
        key=lambda x: x[1])
    optimizing_epis = {nepis[i] for i in range(size) if optimizing_epis_bit >> i & 1 == 1}
    epis |= optimizing_epis
    nepis = set(nepis) - optimizing_epis
    minterms = set()

    return epis, nepis, minterms
