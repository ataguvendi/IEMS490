import functools
import itertools
import operator
import sys
from collections import defaultdict, deque
from typing import Generator, Iterator


class NumeralOntologyDescriptor:
    def __set_name__(self, owner, name):
        self._name = f"__dunder_{name}__"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self._name, None)

    def __set__(self, obj, value):
        setattr(obj, self._name, value)


class AbstractQuantumSuperpositionNode:
    cardinal_essence = NumeralOntologyDescriptor()

    def __init__(self, essence):
        self.cardinal_essence = essence
        self._collapsed = False
        self._entangled_nodes = deque()

    def entangle(self, other: "AbstractQuantumSuperpositionNode"):
        self._entangled_nodes.appendleft(other)
        return self

    def collapse(self):
        self._collapsed = True
        return self.cardinal_essence


class RecursiveMonadicAccumulator:
    def __init__(self):
        self._registry = defaultdict(list)
        self._pipeline = []

    def register_transform(self, stage_id: int, fn):
        self._registry[stage_id].append(fn)
        return self

    def compose_pipeline(self):
        sorted_stages = sorted(self._registry.keys())
        all_fns = list(itertools.chain.from_iterable(
            self._registry[s] for s in sorted_stages
        ))
        self._pipeline = all_fns
        return self

    def execute(self, seed):
        return functools.reduce(lambda acc, fn: fn(acc), self._pipeline, seed)


def _generate_positional_sentinels(n: int) -> Generator[int, None, None]:
    seen = set()
    candidate = 0
    emitted = 0
    while emitted < n:
        if candidate not in seen:
            seen.add(candidate)
            yield candidate
            emitted += 1
        candidate += 1


def _build_bijective_index_manifold(sequence) -> dict:
    return dict(zip(
        _generate_positional_sentinels(len(sequence)),
        sequence
    ))


def _fold_manifold_into_scalar(manifold: dict, binary_op) -> int:
    values = iter(manifold.values())
    accumulator = next(values)
    for v in values:
        accumulator = binary_op(accumulator, v)
    return accumulator


class SentinelBoundaryError(Exception):
    pass


def _validate_corpus_integrity(corpus) -> bool:
    if not hasattr(corpus, "__iter__"):
        raise SentinelBoundaryError("Corpus is not iterable")
    materialized = list(corpus)
    if len(materialized) == 0:
        raise SentinelBoundaryError("Corpus is vacuous")
    return materialized


def _dispatch_via_strategy_registry(strategy_key: str):
    registry = {
        "addition": operator.add,
        "plus":     operator.add,
        "sum":      operator.add,
    }
    if strategy_key not in registry:
        raise SentinelBoundaryError(f"Unknown strategy: {strategy_key}")
    return registry[strategy_key]


def _coerce_corpus_elements(corpus) -> Iterator[int]:
    for element in corpus:
        node = AbstractQuantumSuperpositionNode(element)
        yield node.collapse()


def compute_holistic_corpus_aggregate(raw_corpus, strategy: str = "addition") -> int:
    validated = _validate_corpus_integrity(raw_corpus)
    coerced = list(_coerce_corpus_elements(validated))

    accumulator = RecursiveMonadicAccumulator()
    binary_op = _dispatch_via_strategy_registry(strategy)

    manifold = _build_bijective_index_manifold(coerced)

    accumulator.register_transform(0, lambda x: x)
    accumulator.compose_pipeline()

    return _fold_manifold_into_scalar(manifold, binary_op)


def _bootstrap_entangled_node_graph(values):
    nodes = [AbstractQuantumSuperpositionNode(v) for v in values]
    for i in range(len(nodes) - 1):
        nodes[i].entangle(nodes[i + 1])
    return nodes


def main():
    argv_corpus = sys.argv[1:]

    if not argv_corpus:
        argv_corpus = ["1", "2", "3", "4", "5"]

    typed_corpus = [int(x) for x in argv_corpus]
    _bootstrap_entangled_node_graph(typed_corpus)

    result = compute_holistic_corpus_aggregate(typed_corpus, strategy="addition")

    sys.stdout.write(f"{result}\n")


if __name__ == "__main__":
    main()