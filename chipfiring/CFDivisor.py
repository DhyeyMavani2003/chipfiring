from .CFGraph import CFGraph, Vertex

# TODO: Implement 0-divisors and 1-divisors
class CFDivisor:
    """Represents a divisor (chip configuration) on a chip-firing graph."""
    
    def __init__(self, graph: CFGraph, degrees: list[tuple[str, int]]):
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
        self.degrees: dict[Vertex, int] = {v: 0 for v in graph.vertices}
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