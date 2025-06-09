"""
Gonality calculation and gonality games for chip-firing graphs.

This module provides functionality for computing graph gonality and playing gonality games,
based on the mathematical framework described in "Chip-firing on the Platonic solids: A primer
for studying graph gonality" by Beougher et al.

The gonality of a graph G, denoted gon(G), is the minimum number of chips Player A needs to
guarantee a win in the Gonality Game, regardless of where Player B places the -1 chip.
"""
from __future__ import annotations
from .CFGraph import CFGraph
from .CFDivisor import CFDivisor
from .algo import is_winnable
from typing import List, Dict, Tuple, Optional
import itertools


class GonalityGameResult:
    """
    Represents the result of a single gonality game instance.
    
    Attributes:
        player_a_wins (bool): True if Player A wins, False if Player B wins
        initial_placement (CFDivisor): Player A's initial chip placement
        player_b_placement (str): Vertex name where Player B placed the -1 chip
        final_divisor (CFDivisor): The divisor after Player B's move
        winnability (bool): Whether the final divisor is winnable via chip-firing
        winning_sequence (Optional[List[str]]): Sequence of vertices fired to win (if applicable)
    """
    
    def __init__(self, player_a_wins: bool, initial_placement: CFDivisor, 
                 player_b_placement: str, final_divisor: CFDivisor, 
                 winnability: bool, winning_sequence: Optional[List[str]] = None):
        self.player_a_wins = player_a_wins
        self.initial_placement = initial_placement
        self.player_b_placement = player_b_placement
        self.final_divisor = final_divisor
        self.winnability = winnability
        self.winning_sequence = winning_sequence or []


class GonalityResult:
    """
    Represents the result of a gonality calculation.
    
    Attributes:
        gonality (int): The computed gonality value
        winning_strategies (List[CFDivisor]): List of N-chip placements that guarantee Player A wins
        logs (List[str]): Detailed logs of the calculation process
        verification_games (Dict[int, List[GonalityGameResult]]): Game results for verification
    """
    
    def __init__(self):
        self.gonality: Optional[int] = None
        self.winning_strategies: List[CFDivisor] = []
        self.logs: List[str] = []
        self.verification_games: Dict[int, List[GonalityGameResult]] = {}
    
    def log(self, message: str):
        """Add a log message."""
        self.logs.append(message)
    
    def get_log_summary(self) -> str:
        """Get complete log of the gonality calculation."""
        if not self.logs:
            return "No calculation logs available."
        return "\n".join(self.logs)


class CFGonality:
    """
    Main class for gonality calculations and gonality games.
    """
    
    def __init__(self, graph: CFGraph):
        """
        Initialize gonality calculator for a given graph.
        
        Args:
            graph: The CFGraph to analyze
        """
        self.graph = graph
    
    def play_gonality_game(self, n_chips: int, player_a_placement: CFDivisor, 
                          player_b_vertex: str, verbose: bool = False) -> GonalityGameResult:
        """
        Play a single instance of the Gonality Game.
        
        Args:
            n_chips: Number of chips Player A is allowed to place
            player_a_placement: Player A's chip placement (must have total degree n_chips)
            player_b_vertex: Vertex name where Player B places the -1 chip
            verbose: Whether to include detailed winning sequence
            
        Returns:
            GonalityGameResult: Complete result of the game instance
            
        Raises:
            ValueError: If player_a_placement doesn't have exactly n_chips total degree
        """
        if player_a_placement.get_total_degree() != n_chips:
            raise ValueError(f"Player A placement must have exactly {n_chips} chips, "
                           f"but has {player_a_placement.get_total_degree()}")
        
        if player_b_vertex not in [v.name for v in self.graph.vertices]:
            raise ValueError(f"Player B vertex '{player_b_vertex}' not found in graph")
        
        # Create final divisor after Player B adds -1 chip
        final_degrees = []
        for vertex in self.graph.vertices:
            if vertex.name == player_b_vertex:
                final_degrees.append((vertex.name, player_a_placement.get_degree(vertex.name) - 1))
            else:
                final_degrees.append((vertex.name, player_a_placement.get_degree(vertex.name)))
        
        final_divisor = CFDivisor(self.graph, final_degrees)
        
        # Check winnability using Dollar Game (Dhar's algorithm)
        winnability = is_winnable(final_divisor)
        
        winning_sequence = []
        if winnability and verbose:
            # Try to find a winning sequence using Dhar's algorithm
            # This is a simplified approach - in practice, you might want more sophisticated sequence finding
            winning_sequence = self._find_winning_sequence(final_divisor)
        
        player_a_wins = winnability
        
        return GonalityGameResult(
            player_a_wins=player_a_wins,
            initial_placement=player_a_placement,
            player_b_placement=player_b_vertex,
            final_divisor=final_divisor,
            winnability=winnability,
            winning_sequence=winning_sequence
        )
    
    def _find_winning_sequence(self, divisor: CFDivisor) -> List[str]:
        """
        Find a sequence of chip-firing moves that wins the Dollar Game.
        This is a simplified implementation - a full implementation would use
        more sophisticated algorithms.
        """
        # For now, return empty list - this could be enhanced with actual sequence finding
        return []
    
    def test_n_chip_strategy(self, n_chips: int, placement: CFDivisor) -> Tuple[bool, List[str]]:
        """
        Test if a given N-chip placement guarantees Player A wins against all possible Player B moves.
        
        Args:
            n_chips: Number of chips (for validation)
            placement: Player A's chip placement strategy
            
        Returns:
            Tuple of (strategy_works, losing_vertices) where strategy_works is True if 
            the placement beats all Player B responses, and losing_vertices lists vertices
            where Player B can place -1 to win
        """
        if placement.get_total_degree() != n_chips:
            raise ValueError(f"Placement must have exactly {n_chips} chips")
        
        losing_vertices = []
        
        for vertex in self.graph.vertices:
            game_result = self.play_gonality_game(n_chips, placement, vertex.name)
            if not game_result.player_a_wins:
                losing_vertices.append(vertex.name)
        
        strategy_works = len(losing_vertices) == 0
        return strategy_works, losing_vertices
    
    def find_all_n_chip_strategies(self, n_chips: int, max_strategies: Optional[int] = None) -> List[CFDivisor]:
        """
        Find all N-chip placements that guarantee Player A wins the Gonality Game.
        
        Args:
            n_chips: Number of chips Player A can place
            max_strategies: Maximum number of strategies to find (None for all)
            
        Returns:
            List of winning CFDivisor placements
        """
        winning_strategies = []
        strategies_found = 0
        
        vertices = sorted(list(self.graph.vertices), key=lambda v: v.name)
        
        # Generate all possible ways to place n_chips on the vertices
        for placement_combo in itertools.combinations_with_replacement(vertices, n_chips):
            if max_strategies and strategies_found >= max_strategies:
                break
                
            # Count chips per vertex
            chip_counts = {v: 0 for v in vertices}
            for vertex in placement_combo:
                chip_counts[vertex] += 1
            
            # Create divisor
            degrees = [(v.name, chip_counts[v]) for v in vertices]
            placement = CFDivisor(self.graph, degrees)
            
            # Test if this strategy works
            strategy_works, _ = self.test_n_chip_strategy(n_chips, placement)
            
            if strategy_works:
                winning_strategies.append(placement)
                strategies_found += 1
        
        return winning_strategies
    
    def compute_gonality(self, max_gonality: Optional[int] = None, 
                        find_strategies: bool = True) -> GonalityResult:
        """
        Compute the gonality of the graph.
        
        The gonality is the minimum number N such that Player A has a winning strategy
        in the Gonality Game with N chips.
        
        Args:
            max_gonality: Maximum gonality to check (defaults to number of vertices)
            find_strategies: Whether to find and store winning strategies
            
        Returns:
            GonalityResult: Complete result including gonality value and winning strategies
        """
        result = GonalityResult()
        
        if max_gonality is None:
            max_gonality = len(self.graph.vertices)
        
        result.log(f"Computing gonality for graph with {len(self.graph.vertices)} vertices")
        result.log(f"Will check up to {max_gonality} chips")
        
        # Start with N=1 and increment until we find a winning strategy
        for n_chips in range(1, max_gonality + 1):
            result.log(f"\n--- Testing N = {n_chips} chips ---")
            
            if find_strategies:
                strategies = self.find_all_n_chip_strategies(n_chips, max_strategies=5)
                result.log(f"Found {len(strategies)} winning strategies for {n_chips} chips")
                
                if strategies:
                    result.gonality = n_chips
                    result.winning_strategies = strategies
                    result.log(f"Gonality found: {n_chips}")
                    
                    # Verify by testing a few strategies
                    for i, strategy in enumerate(strategies[:3]):
                        result.log(f"Strategy {i+1}: {strategy.degrees_to_str()}")
                        works, losing_vertices = self.test_n_chip_strategy(n_chips, strategy)
                        result.log(f"  Strategy works: {works}")
                        if losing_vertices:
                            result.log(f"  Loses to Player B at: {losing_vertices}")
                    
                    break
            else:
                # Just check if any strategy exists (faster)
                found_strategy = False
                vertices = sorted(list(self.graph.vertices), key=lambda v: v.name)
                
                for placement_combo in itertools.combinations_with_replacement(vertices, n_chips):
                    chip_counts = {v: 0 for v in vertices}
                    for vertex in placement_combo:
                        chip_counts[vertex] += 1
                    
                    degrees = [(v.name, chip_counts[v]) for v in vertices]
                    placement = CFDivisor(self.graph, degrees)
                    
                    strategy_works, _ = self.test_n_chip_strategy(n_chips, placement)
                    
                    if strategy_works:
                        result.gonality = n_chips
                        result.winning_strategies = [placement]
                        result.log(f"Gonality found: {n_chips}")
                        result.log(f"Winning strategy: {placement.degrees_to_str()}")
                        found_strategy = True
                        break
                
                if found_strategy:
                    break
        
        if result.gonality is None:
            result.log(f"No winning strategy found with up to {max_gonality} chips")
            result.gonality = -1  # Indicates no solution found within limit
        
        return result
    
    def verify_gonality_bounds(self, suspected_gonality: int) -> Tuple[bool, bool, List[str]]:
        """
        Verify gonality bounds by checking that suspected_gonality works but suspected_gonality-1 doesn't.
        
        Args:
            suspected_gonality: The suspected gonality value to verify
            
        Returns:
            Tuple of (upper_bound_verified, lower_bound_verified, messages)
            where upper_bound_verified means suspected_gonality works,
            and lower_bound_verified means suspected_gonality-1 doesn't work
        """
        messages = []
        
        # Test upper bound: suspected_gonality should have winning strategies
        messages.append(f"Testing upper bound: checking if {suspected_gonality} chips has winning strategies...")
        strategies = self.find_all_n_chip_strategies(suspected_gonality, max_strategies=1)
        upper_bound_verified = len(strategies) > 0
        
        if upper_bound_verified:
            messages.append(f"✓ Upper bound verified: found winning strategy with {suspected_gonality} chips")
            messages.append(f"  Example strategy: {strategies[0].degrees_to_str()}")
        else:
            messages.append(f"✗ Upper bound failed: no winning strategy found with {suspected_gonality} chips")
        
        # Test lower bound: suspected_gonality-1 should have no winning strategies
        lower_bound_verified = True
        if suspected_gonality > 1:
            messages.append(f"Testing lower bound: checking if {suspected_gonality-1} chips has no winning strategies...")
            strategies_lower = self.find_all_n_chip_strategies(suspected_gonality - 1, max_strategies=1)
            lower_bound_verified = len(strategies_lower) == 0
            
            if lower_bound_verified:
                messages.append(f"✓ Lower bound verified: no winning strategy with {suspected_gonality-1} chips")
            else:
                messages.append(f"✗ Lower bound failed: found winning strategy with {suspected_gonality-1} chips")
                messages.append(f"  Counter-example: {strategies_lower[0].degrees_to_str()}")
        else:
            messages.append("Lower bound trivially verified (suspected gonality is 1)")
        
        return upper_bound_verified, lower_bound_verified, messages


def gonality(graph: CFGraph, max_gonality: Optional[int] = None, 
            find_strategies: bool = True) -> GonalityResult:
    """
    Compute the gonality of a graph.
    
    The gonality of a graph G is the minimum number of chips Player A needs to 
    guarantee winning the Gonality Game, regardless of Player B's strategy.
    
    Algorithm:
    1. For N = 1, 2, 3, ..., find all possible ways Player A can place N chips
    2. For each placement, test if Player A wins against all possible Player B responses
    3. Return the minimum N for which Player A has a guaranteed winning strategy
    
    Args:
        graph: The CFGraph to analyze
        max_gonality: Maximum gonality to check (defaults to number of vertices)
        find_strategies: Whether to find and return winning strategies
        
    Returns:
        GonalityResult: Object containing gonality value, winning strategies, and logs
        
    Example:
        >>> from chipfiring import CFGraph, gonality
        >>> # Create a simple triangle graph
        >>> vertices = {"A", "B", "C"}
        >>> edges = [("A", "B", 1), ("B", "C", 1), ("A", "C", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> result = gonality(graph)
        >>> print(f"Gonality: {result.gonality}")
        >>> print(f"Winning strategies: {len(result.winning_strategies)}")
    """
    gonality_calc = CFGonality(graph)
    return gonality_calc.compute_gonality(max_gonality, find_strategies)


def play_gonality_game(graph: CFGraph, n_chips: int, player_a_placement: CFDivisor, 
                      player_b_vertex: str, verbose: bool = False) -> GonalityGameResult:
    """
    Play a single instance of the Gonality Game.
    
    Game Rules:
    1. Player A places n_chips on the vertices of the graph
    2. Player B places -1 chip on any vertex
    3. Player A wins if they can eliminate all debt through chip-firing moves
    
    Args:
        graph: The CFGraph on which to play
        n_chips: Number of chips Player A is allowed
        player_a_placement: Player A's chip placement
        player_b_vertex: Vertex where Player B places -1 chip
        verbose: Whether to include detailed winning information
        
    Returns:
        GonalityGameResult: Complete result of the game
        
    Example:
        >>> from chipfiring import CFGraph, CFDivisor, play_gonality_game
        >>> vertices = {"A", "B", "C"}
        >>> edges = [("A", "B", 1), ("B", "C", 1), ("A", "C", 1)]
        >>> graph = CFGraph(vertices, edges)
        >>> placement = CFDivisor(graph, [("A", 2), ("B", 0), ("C", 0)])
        >>> result = play_gonality_game(graph, 2, placement, "B")
        >>> print(f"Player A wins: {result.player_a_wins}")
    """
    gonality_calc = CFGonality(graph)
    return gonality_calc.play_gonality_game(n_chips, player_a_placement, player_b_vertex, verbose)
