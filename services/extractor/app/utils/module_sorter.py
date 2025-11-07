# argus/services/extractor/app/utils/module_sorter.py

from typing import Dict, List, Set
from collections import defaultdict
from loguru import logger


def topological_sort_modules(dependencies: Dict[str, List[str]]) -> List[str]:
    """
    Sorts modules topologically based on their dependencies.
    """
    graph: Dict[str, List[str]] = defaultdict(list)
    in_degree: Dict[str, int] = defaultdict(int)
    nodes: Set[str] = set()

    # Build the graph and calculate the 'in-degree' of each node
    for module, deps in dependencies.items():
        nodes.add(module)
        for dep in deps:
            nodes.add(dep)
            graph[dep].append(module)
            in_degree[module] += 1

    # Add all modules without dependencies to the queue
    queue = [module for module in nodes if in_degree[module] == 0]
    result: List[str] = []

    while queue:
        module = queue.pop(0)
        result.append(module)

        for dependent_module in graph[module]:
            in_degree[dependent_module] -= 1
            if in_degree[dependent_module] == 0:
                queue.append(dependent_module)

    if len(result) != len(nodes):
        # There is a cycle in the dependencies
        all_modules = sorted(list(nodes))
        processed_modules = set(result)
        unprocessed_modules = sorted(list(set(all_modules) - processed_modules))

        error_message = (
            f"Topological sort failed: A cycle exists in the dependencies. "
            f"Unprocessed modules: {unprocessed_modules}"
        )
        logger.error(error_message)
        raise ValueError(error_message)

    return result
