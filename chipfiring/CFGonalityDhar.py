"""
Enhanced Dhar's burning algorithm specifically optimized for gonality games.

This module extends the standard Dhar's burning algorithm with specialized functions
for gonality calculations, including optimizations for finding winning strategies
and determining gonality bounds efficiently.
"""
from __future__ import annotations
from typing import Set, List, Tuple, Dict
from .CFGraph import CFGraph, Vertex
from .CFDivisor import CFDivisor
from .CFDhar import DharAlgorithm
from .CFConfig import CFConfig


class GonalityDharAlgorithm(DharAlgorithm):
    """
    Enhanced Dhar's algorithm specialized for gonality game computations.
    
    This class extends the standard DharAlgorithm with methods specifically
    designed for efficiency in gonality calculations, including batch testing
    of strategies and optimized burning processes.
    """
    
    def __init__(self, graph: CFGraph, initial_divisor: CFDivisor, q_name: str):
        """
        Initialize the enhanced Dhar algorithm for gonality games.
        
        Args:
            graph: A CFGraph object representing the graph
            initial_divisor: A CFDivisor object representing the initial chip configuration
            q_name: The name of the distinguished vertex (fire source)
        """
        super().__init__(graph, initial_divisor, q_name)
        self._burning_cache: Dict[tuple, Set[str]] = {}
        self._strategy_cache: Dict[tuple, bool] = {}
    
    def test_strategy_batch(self, strategies: List[List[str]]) -> List[bool]:
        """
        Test multiple strategies efficiently using cached burning results.
        
        Args:
            strategies: List of strategies, where each strategy is a list of vertex names
            
        Returns:
            List[bool]: Results for each strategy (True if winning, False otherwise)
        """
        results = []
        
        for strategy in strategies:
            strategy_tuple = tuple(sorted(strategy))
            
            # Check cache first
            if strategy_tuple in self._strategy_cache:
                results.append(self._strategy_cache[strategy_tuple])
                continue
            
            # Test the strategy
            is_winning = self.test_strategy(strategy)
            self._strategy_cache[strategy_tuple] = is_winning
            results.append(is_winning)
        
        return results
    
    def test_strategy(self, strategy: List[str]) -> bool:
        """
        Test if a given strategy is winning.
        A strategy is winning if, after placing chips according to the strategy
        and having Player B place -1 at q, the resulting configuration is winnable
        using the same criterion as the EWD algorithm.
        
        Args:
            strategy: List of vertex names representing the strategy (chips added to V-{q})
            
        Returns:
            bool: True if the strategy is winning, False otherwise
        """
        # Create initial divisor: start with base configuration (typically all zeros)
        current_degrees = []
        for vertex in self.graph.vertices:
            base_degree = self.configuration.divisor.get_degree(vertex.name)
            current_degrees.append((vertex.name, base_degree))
        
        # Add chips according to strategy (these are on V-{q})
        for vertex_name in strategy:
            for i, (name, degree) in enumerate(current_degrees):
                if name == vertex_name:
                    current_degrees[i] = (name, degree + 1)
                    break

        # Player B places -1 at q_vertex
        for i, (name, degree) in enumerate(current_degrees):
            if name == self.q_vertex.name:
                current_degrees[i] = (name, degree - 1)
                break
            
        test_divisor = CFDivisor(self.graph, current_degrees)
        
        # Use the same winnability test as EWD/is_winnable
        from .algo import is_winnable
        return is_winnable(test_divisor)
    
    def _enhanced_burning(self, config: CFConfig) -> Set[str]:
        """
        Enhanced burning algorithm optimized for gonality calculations.
        
        Args:
            config: CFConfig object with the chip configuration
            
        Returns:
            Set[str]: Names of all burnt vertices (excluding q)
        """
        # Create cache key
        config_tuple = self._config_to_tuple(config)
        if config_tuple in self._burning_cache:
            return self._burning_cache[config_tuple]
        
        burnt_vertices = {self.q_vertex.name}
        newly_burnt = [self.q_vertex]
        
        while newly_burnt:
            next_newly_burnt = []
            
            for vertex in config.v_tilde_vertices:
                if vertex.name in burnt_vertices:
                    continue
                
                # Check if vertex should burn
                if self._should_burn(vertex, burnt_vertices, config):
                    burnt_vertices.add(vertex.name)
                    next_newly_burnt.append(vertex)
            
            newly_burnt = next_newly_burnt
        
        # Cache result (excluding q)
        result = burnt_vertices - {self.q_vertex.name}
        self._burning_cache[config_tuple] = result
        return result
    
    def _should_burn(self, vertex: Vertex, burnt_vertices: Set[str], config: CFConfig) -> bool:
        """
        Determine if a vertex should burn given current burnt set.
        
        Args:
            vertex: The vertex to test
            burnt_vertices: Set of currently burnt vertex names
            config: The chip configuration
            
        Returns:
            bool: True if vertex should burn
        """
        # Calculate chips at vertex
        chips = config.get_degree_at(vertex.name)
        
        # Calculate outgoing edges to burnt vertices
        burnt_vertex_objects = {v for v in self.graph.vertices 
                              if v.name in burnt_vertices}
        outgoing_to_burnt = self.outdegree_S(vertex, burnt_vertex_objects)
        
        # Vertex burns if it has at least as many chips as outgoing edges to burnt vertices
        return chips >= outgoing_to_burnt
    
    def _config_to_tuple(self, config: CFConfig) -> tuple:
        """
        Convert a configuration to a hashable tuple for caching.
        
        Args:
            config: CFConfig object
            
        Returns:
            tuple: Hashable representation of the configuration
        """
        degrees = []
        for vertex in sorted(config.divisor.graph.vertices, key=lambda v: v.name):
            degrees.append((vertex.name, config.divisor.get_degree(vertex.name)))
        return tuple(degrees)
    
    def find_minimal_winning_strategies(self, max_chips: int) -> List[List[str]]:
        """
        Find all minimal winning strategies using at most max_chips chips.
        
        Args:
            max_chips: Maximum number of chips to use
            
        Returns:
            List[List[str]]: List of minimal winning strategies
        """
        minimal_strategies = []
        v_tilde_names = [v.name for v in self.configuration.v_tilde_vertices]
        
        # Test all possible combinations up to max_chips
        from itertools import combinations_with_replacement
        
        for num_chips in range(1, max_chips + 1):
            for strategy in combinations_with_replacement(v_tilde_names, num_chips):
                strategy_list = list(strategy)
                
                # Skip if this is a superset of an already found minimal strategy
                if any(self._is_subset_multiset(minimal, strategy_list) 
                       for minimal in minimal_strategies):
                    continue
                
                # Test if strategy is winning
                if self.test_strategy(strategy_list):
                    # Check if it's minimal (no proper subset is also winning)
                    is_minimal = True
                    for i in range(len(strategy_list)):
                        subset = strategy_list[:i] + strategy_list[i+1:]
                        if subset and self.test_strategy(subset):
                            is_minimal = False
                            break
                    
                    if is_minimal:
                        minimal_strategies.append(strategy_list)
        
        return minimal_strategies
    
    def _is_subset_multiset(self, subset: List[str], superset: List[str]) -> bool:
        """
        Check if one multiset is a subset of another.
        
        Args:
            subset: Potential subset as list
            superset: Potential superset as list
            
        Returns:
            bool: True if subset is a subset of superset
        """
        from collections import Counter
        subset_count = Counter(subset)
        superset_count = Counter(superset)
        
        for item, count in subset_count.items():
            if superset_count[item] < count:
                return False
        return True
    
    def gonality_lower_bound(self) -> int:
        """
        Compute a lower bound for gonality using burning algorithm analysis.
        
        Returns:
            int: Lower bound for gonality
        """
        v_tilde_names = [v.name for v in self.configuration.v_tilde_vertices]
        
        # Try strategies of increasing size until one works
        for num_chips in range(1, len(v_tilde_names) + 1):
            # Test a few representative strategies of this size
            from itertools import combinations_with_replacement
            strategies_to_test = list(combinations_with_replacement(v_tilde_names, num_chips))
            
            # Limit testing to avoid exponential blowup
            if len(strategies_to_test) > 100:
                import random
                strategies_to_test = random.sample(strategies_to_test, 100)
            
            results = self.test_strategy_batch([list(s) for s in strategies_to_test])
            
            if any(results):
                return num_chips
        
        return len(v_tilde_names)  # Fallback upper bound
    
    def clear_cache(self):
        """Clear all cached results to free memory."""
        self._burning_cache.clear()
        self._strategy_cache.clear()


def enhanced_dhar_gonality_test(graph: CFGraph, q_vertex_name: str, 
                               max_gonality: int = None) -> Tuple[int, List[List[str]]]:
    """
    Use enhanced Dhar's algorithm to compute gonality and find winning strategies.
    This computes the smallest k such that placing k chips on V-{q} results in a 
    configuration that is winnable after -1 chip is placed on q.
    
    Args:
        graph: The graph to analyze
        q_vertex_name: Name of the distinguished vertex (Player B's target)
        max_gonality: Maximum number of chips (k) to test (if None, uses |V|-1)
        
    Returns:
        Tuple[int, List[List[str]]]: (gonality_k, list of minimal winning strategies of size k)
    """
    if max_gonality is None:
        max_gonality = len(graph.vertices) - 1
    if max_gonality < 0: # Handle graph with 0 or 1 vertex
        max_gonality = 0
    
    # Initial divisor for GonalityDharAlgorithm is all zeros.
    # Chips for the strategy are added *on top* of this.
    initial_divisor_for_dhar_algo = CFDivisor(graph, [(v.name, 0) for v in graph.vertices])
    
    dhar_gon_algo = GonalityDharAlgorithm(graph, initial_divisor_for_dhar_algo, q_vertex_name)
    
    # find_minimal_winning_strategies iterates num_chips from 1 to max_gonality.
    # A strategy is a list of vertex names in V-{q} where chips are placed.
    # The number of chips is len(strategy).
    minimal_strategies = dhar_gon_algo.find_minimal_winning_strategies(max_gonality) 
    
    if minimal_strategies:
        # Gonality (k) is the size of the smallest winning strategy found
        gonality_k = min(len(s) for s in minimal_strategies)
        # Filter strategies to only include those of size gonality_k
        winning_k_strategies = [s for s in minimal_strategies if len(s) == gonality_k]
        return gonality_k, winning_k_strategies
    else:
        # If no strategy up to max_gonality chips works, return max_gonality + 1 or an indicator.
        # The problem asks for consistency with CFGonality.gonality.
        # If CFGonality.gonality would determine it's higher, this should reflect that.
        # For now, if no strategy is found, it implies gonality is > max_gonality.
        # The original code returned max_gonality, [] which is confusing.
        # Let's return a value indicating failure to find within bounds, e.g., -1 or max_gonality + 1
        return max_gonality + 1, [] # Or perhaps -1, [] if that's a better convention for "not found"


def batch_gonality_analysis(graphs: List[Tuple[CFGraph, str]], 
                           max_gonality: int = None) -> Dict[str, Dict]:
    """
    Analyze gonality for multiple graphs efficiently.
    
    Args:
        graphs: List of (graph, q_vertex_name) pairs
        max_gonality: Maximum gonality to test for each graph
        
    Returns:
        Dict[str, Dict]: Results for each graph
    """
    results = {}
    
    for i, (graph, q_vertex_name) in enumerate(graphs):
        graph_name = f"graph_{i}"
        if hasattr(graph, 'name') and graph.name: # Check if graph.name exists and is not None/empty
            graph_name = graph.name
        
        gonality, strategies = enhanced_dhar_gonality_test(graph, q_vertex_name, max_gonality)
        
        # CFGraph.total_valence is sum of degrees. Number of edges = total_valence / 2
        num_edges = graph.total_valence // 2

        results[graph_name] = {
            'gonality': gonality,
            'minimal_strategies': strategies,
            'num_vertices': len(graph.vertices),
            'num_edges': num_edges, # Use calculated num_edges
            'q_vertex': q_vertex_name
        }
    
    return results
