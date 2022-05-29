import time
import os
import sys
from collections import namedtuple
from typing import Iterable

from product import Product
from solution import find_min_cover

CoverTestCase = namedtuple('TestCase',
                           ['n', 'description', 'minterms', 'dterms', 'input_cost', 'output_cost', 'petrick_only'],
                           defaults=[None, None, None, None])


def solve(cases: Iterable, print_processes: bool = True):
    i = 0
    _iter = iter(cases)
    total_start = time.time()
    while True:
        case = next(_iter, None)
        if not case:
            break
        i += 1
        print('\n' + '-' * terminal_width + '\n')
        print(f"Case {i}: n={case.n}, minterms={case.minterms}, dterms={case.dterms}, " \
              + f"input_cost={case.input_cost}, output_cost={case.output_cost}, petrick_only={case.petrick_only}")
        print(case.description + '\n')
        start = time.time()
        epis, nepis = find_min_cover(case.n, case.minterms, case.dterms,
                                     input_cost=case.input_cost, output_cost=case.output_cost,
                                     petrick_only=case.petrick_only, print_detail=print_processes)
        print(f">> EPIs={sorted(epis, key=Product.sort_key)}, NEPIs={sorted(nepis, key=Product.sort_key)}")
        end = time.time()
        print(f"elapsed time: {(end - start) * 1000}ms")
    total_end = time.time()
    print(f"\n\nRan total {i} cases, took {(total_end - total_start) * 1000}ms.")


if __name__ == "__main__":
    argv = sys.argv[1:]
    print_detail = True if any(arg == "--detail" for arg in argv) else False
    use_petrick_only = True if any(arg == "--petrick-only" for arg in argv) else False
    Product.sort_one_first = True if any(arg =="--one-precedes-dash" for arg in argv) else False
    argv = [arg for arg in argv if not arg.startswith("--")]
    try:
        terminal_width = os.get_terminal_size().columns
    except OSError as e:
        terminal_width = 30
    # noinspection PyArgumentList
    if not argv:
        cover_test_cases = [
            CoverTestCase(3, 'default testcase for hw1 / hw2', [0, 1, 2, 3]),
            CoverTestCase(4, 'from class material #1 (lecture5_tabular_method/p.4~)', [0, 4, 8, 10, 11, 12], [13, 15]),
            CoverTestCase(3, 'from class material #2 (lecture5_tabular_method/p.17)',
                          [0, 1, 2, 5, 6, 7],
                          petrick_only=False),
            CoverTestCase(3, 'from class material #2 (lecture5_tabular_method/p.17) - only with Petrick\'s method',
                          [0, 1, 2, 5, 6, 7],
                          petrick_only=True),
            CoverTestCase(4, 'from class material #3 (lecture5_tabular_method/p.18)',
                          [0, 2, 5, 6, 7, 8, 10, 12, 13, 14, 15]),
            CoverTestCase(4, 'from class material #4 (lecture5_tabular_method/p.18)',
                          [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]),
            CoverTestCase(4, 'from class material #5 (lecture5_tabular_method/p.18)',
                          [2, 3, 7, 9, 11, 13], [1, 10, 15]),
            CoverTestCase(4, 'from wikipedia: https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm',
                          [4, 8, 10, 11, 12, 15], [9, 14])
        ]
    else:
        cover_test_cases = [CoverTestCase(int(argv[i]), f"user input #{i // 2 + 1}", list(map(int, argv[i + 1].split(','))), petrick_only=use_petrick_only) for i in
                            range(0, len(argv), 2)]

    solve(cover_test_cases, print_processes=print_detail)
