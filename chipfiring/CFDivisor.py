from __future__ import annotations
from typing import List, Tuple, Dict, Set
from .CFGraph import CFGraph, Vertex

# TODO: Implement 0-divisors and 1-divisors
class CFDivisor:
    """Represents a divisor (chip configuration) on a chip-firing graph."""
    
    def __init__(self, graph: CFGraph, degrees: List[Tuple[str, int]]):
        """Initialize the divisor with a graph and list of vertex degrees.
        
        Args:
            graph: A CFGraph object representing the underlying graph
            degrees: List of tuples (vertex_name, degree) where degree is the number
                    of chips at the vertex with the given name
        
        Raises:
            ValueError: If a vertex name appears multiple times in degrees
            ValueError: If a vertex name is not found in the graph
        """
        self.graph = graph
        # Initialize the degrees dictionary with all vertices having degree 0
        self.degrees: Dict[Vertex, int] = {v: 0 for v in graph.vertices}
        self.total_degree: int = 0
        
        # Check for duplicate vertex names in degrees
        vertex_names = [name for name, _ in degrees]
        if len(vertex_names) != len(set(vertex_names)):
            raise ValueError("Duplicate vertex names are not allowed in degrees")
        
        # Update degrees (number of chips) for specified vertices
        for vertex_name, degree in degrees:
            vertex = Vertex(vertex_name)
            if vertex not in graph.graph:
                raise ValueError(f"Vertex {vertex_name} not found in graph")
            self.degrees[vertex] = degree
            self.total_degree += degree
    def get_degree(self, vertex_name: str) -> int:
        """Get the number of chips at a vertex.
        
        Args:
            vertex_name: The name of the vertex to get the number of chips for
            
        Returns:
            The number of chips at the vertex
            
        Raises:
            ValueError: If the vertex name is not found in the divisor
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.degrees:
            raise ValueError(f"Vertex {vertex_name} not in divisor")
        return self.degrees[vertex]
    
    def get_total_degree(self) -> int:
        """Get the total number of chips in the divisor."""
        return self.total_degree

    def lending_move(self, vertex_name: str) -> None:
        """Perform a lending move at the specified vertex.

        Decreases the degree of the vertex by its valence and increases the
        degree of each of its neighbors by 1.

        Args:
            vertex_name: The name of the vertex to perform the lending move at.

        Raises:
            ValueError: If the vertex name is not found in the graph.
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.graph.graph:
            raise ValueError(f"Vertex {vertex_name} not found in graph")

        valence = self.graph.get_valence(vertex_name)
        neighbors = self.graph.graph[vertex]

        # Update the degree of the vertex
        self.degrees[vertex] -= valence

        # Update the degrees of the neighbors
        for neighbor in neighbors:
            self.degrees[neighbor] += 1
        
        # Total degree remains unchanged: -valence + len(neighbors) = -valence + valence = 0

    firing_move = lending_move

    def borrowing_move(self, vertex_name: str) -> None:
        """Perform a borrowing move at the specified vertex.

        Increases the degree of the vertex by its valence and decreases the
        degree of each of its neighbors by 1.

        Args:
            vertex_name: The name of the vertex to perform the borrowing move at.

        Raises:
            ValueError: If the vertex name is not found in the graph.
        """
        vertex = Vertex(vertex_name)
        if vertex not in self.graph.graph:
            raise ValueError(f"Vertex {vertex_name} not found in graph")

        valence = self.graph.get_valence(vertex_name)
        neighbors = self.graph.graph[vertex]

        # Update the degree of the vertex
        self.degrees[vertex] += valence

        # Update the degrees of the neighbors
        for neighbor in neighbors:
            self.degrees[neighbor] -= 1
            
        # Total degree remains unchanged: +valence - len(neighbors) = +valence - valence = 0
    
    def chip_transfer(self, vertex_from_name: str, vertex_to_name: str, amount: int = 1) -> None:
        """Transfer a specified number of chips from one vertex to another.

        Decreases the degree of vertex_from_name by `amount` and increases the
        degree of vertex_to_name by `amount`.

        Args:
            vertex_from_name: The name of the vertex to transfer chips from.
            vertex_to_name: The name of the vertex to transfer chips to.
            amount: The number of chips to transfer (defaults to 1).

        Raises:
            ValueError: If either vertex name is not found in the divisor.
            ValueError: If the amount is not positive.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive for chip transfer")
            
        vertex_from = Vertex(vertex_from_name)
        vertex_to = Vertex(vertex_to_name)

        if vertex_from not in self.degrees:
            raise ValueError(f"Vertex {vertex_from_name} not in divisor")
        if vertex_to not in self.degrees:
            raise ValueError(f"Vertex {vertex_to_name} not in divisor")

        self.degrees[vertex_from] -= amount
        self.degrees[vertex_to] += amount
        
        # Total degree remains unchanged: -amount + amount = 0
    
    def set_fire(self, vertex_names: Set[str]) -> None:
        """Perform a set firing operation.

        For each vertex v in the specified set `vertex_names`, and for each 
        neighbor w of v such that w is not in `vertex_names`, transfer chips 
        from v to w equal to the number of edges between v and w.

        Args:
            vertex_names: A set of names of vertices in the firing set.

        Raises:
            ValueError: If any vertex name in the set is not found in the graph.
        """
        firing_set_vertices = set()
        # Validate vertex names and convert to Vertex objects
        for name in vertex_names:
            vertex = Vertex(name)
            if vertex not in self.graph.graph:
                raise ValueError(f"Vertex {name} not found in graph")
            firing_set_vertices.add(vertex)

        # Perform the chip transfers
        for vertex in firing_set_vertices:
            neighbors = self.graph.graph[vertex] # {neighbor_vertex: valence}
            for neighbor_vertex, valence in neighbors.items():
                if neighbor_vertex not in firing_set_vertices:
                    # Transfer 'valence' chips from vertex to neighbor_vertex
                    self.chip_transfer(vertex.name, neighbor_vertex.name, amount=valence)
    