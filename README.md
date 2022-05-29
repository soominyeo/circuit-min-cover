# Explanation
`product.py` provides a type definition for product of terms which can be printed like '10--' and can determine whether
to merge one onother.

`solutions.py` provides `find_pi(n, minterms, dterms)`, `find_epis(n, minterms, _pis, dterms):`
, `find_min_cover(n, _minterms, dterms, _pis, _epis, ...)` functions.

`test.py` is an unittest setup, but not completed.

# How to test
## Predefined test cases

Simply run `python main.py` without any parameter except `--detail` option.

## Run your own test cases

Run `python main.py <N> <M0>,<M1>,...<Mn>` with some options. You can specify whether to print detail by adding `--detail` and whether to
use Petrick's method only by adding `--petrick-only`, whether '1' comes first or not by adding `--one-precedes-dash`.

### Example
```bash
python main.py --detail --petrick-only 4 0,1,2,3
```

### Result
```
--------------------------------------------------------------------------------

Case 1: n=3, minterms=[0, 1, 2, 3], dterms=None, input_cost=None, output_cost=No
ne, petrick_only=True
user input #1

Process(1): Find all PIs:pis=[0--], epis=EMPTY, nepis=[0--], minterms={0, 1, 2, 
3}
Process(2): Find all EPIs:pis=[0--], epis=[0--], nepis=EMPTY, minterms=EMPTY    
>> EPIs=[0--], NEPIs=[]
elapsed time: 1.0008811950683594ms


Ran total 1 cases, took 1.001119613647461ms.
```

