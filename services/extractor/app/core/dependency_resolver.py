# argus/services/extractor/app/core/dependency_resolver.py

from collections import deque
from typing import Dict, Any, List
from loguru import logger


class DependencyResolver:
    def __init__(self, modules: Dict[str, Any]):
        """
        Initializes the resolver.

        Args:
            modules: A dictionary with the active modules for the current run.
        """
        self.modules = modules
        self.module_names = set(modules.keys())
        # The 'raw' graph containing all dependencies, including invalid ones.
        self.raw_dependencies = {
            name: getattr(mod, "REQUIRES", []) for name, mod in modules.items()
        }

    def sort(self) -> List[str]:
        """
        Performs a topological sort and returns the execution order.
        Ignores dependencies that are not in the current set of active modules.
        """
        # We build a 'clean' graph with only the dependencies that actually exist
        # in the set of active modules for this tier.
        dependencies = {}
        for name, deps in self.raw_dependencies.items():
            # Keep only the dependencies that are actually in self.module_names
            valid_deps = [dep for dep in deps if dep in self.module_names]
            if len(valid_deps) != len(deps):
                invalid_deps = set(deps) - set(valid_deps)
                logger.trace(
                    f"Module '{name}' has unmet dependencies which will be ignored: {invalid_deps}"
                )
            dependencies[name] = valid_deps

        # Step 1: Calculate the "in-degree" for each module.
        in_degree = {name: 0 for name in self.module_names}
        graph = {name: [] for name in self.module_names}

        for name, deps in dependencies.items():
            for dep in deps:
                # Because we filtered, 'dep' will always exist in self.module_names
                graph[dep].append(name)
                in_degree[name] += 1

        # Step 2: Start the queue with all modules that have an in-degree of 0.
        queue = deque([name for name in self.module_names if in_degree[name] == 0])

        sorted_order = []

        # Step 3: Process the queue.
        while queue:
            current_module = queue.popleft()
            sorted_order.append(current_module)

            for dependent_module in graph[current_module]:
                in_degree[dependent_module] -= 1
                if in_degree[dependent_module] == 0:
                    queue.append(dependent_module)

        # Step 4: Check for circular dependencies.
        if len(sorted_order) != len(self.module_names):
            cycle_nodes = {name for name, degree in in_degree.items() if degree > 0}
            raise ValueError(
                f"Circular dependency detected! Modules in cycle: {cycle_nodes}"
            )

        return sorted_order
