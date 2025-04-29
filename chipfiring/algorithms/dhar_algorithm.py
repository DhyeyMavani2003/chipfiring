class DharAlgorithm:
    def __init__(self, graph, configuration, q):
        """
        Initialize Dhar's Algorithm for finding a maximal legal firing set.
        
        Args:
            graph: A dictionary representing the adjacency list of the graph
            configuration: A dictionary representing the chip configuration
            q: The distinguished vertex (fire source)
        """
        self.graph = graph
        # Store a copy of the full configuration
        self.full_configuration = configuration.copy()
        # For convenience, store a separate configuration excluding q
        self.configuration = {v: configuration[v] for v in graph if v != q}
        self.q = q
        self.unburnt_vertices = set(self.configuration.keys())
    
    def outdegree_S(self, vertex, S):
        """
        Calculate the number of edges from a vertex to vertices in set S.
        
        Args:
            vertex: The vertex to calculate outdegree for
            S: Set of vertices to count edges to
            
        Returns:
            Sum of edge weights from vertex to vertices in S
        """
        return sum(self.graph[vertex][neighbor] for neighbor in self.graph[vertex] if neighbor in S)
    
    def send_debt_to_q(self):
        """
        Concentrate all debt at the distinguished vertex q, making all non-q vertices out of debt.
        This method modifies self.configuration so all non-q vertices have non-negative values.
        
        The algorithm works by performing borrowing moves at vertices in debt,
        working in reverse order of distance from q (approximated by BFS).
        """
        # Sort vertices by distance from q (approximation using BFS)
        queue = [self.q]
        visited = {self.q}
        distance_ordering = [self.q]
        
        while queue:
            current = queue.pop(0)
            for neighbor in self.graph[current]:
                if neighbor not in visited and neighbor in self.unburnt_vertices:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    distance_ordering.append(neighbor)
        
        # Process vertices in reverse order of distance (excluding q)
        vertices_to_process = [v for v in reversed(distance_ordering) if v in self.unburnt_vertices]
        
        for v in vertices_to_process:
            # While v is in debt, borrow
            while self.configuration[v] < 0:
                # Perform a borrowing move at v
                vertex_degree = sum(self.graph[v].values())
                self.configuration[v] += vertex_degree
                
                # Update neighbors based on edge counts
                for neighbor, edge_count in self.graph[v].items():
                    if neighbor in self.configuration:
                        self.configuration[neighbor] -= edge_count
    
    def run(self):
        """
        Run Dhar's Algorithm to find a maximal legal firing set.
        
        This implementation uses the "burning process" metaphor:
        1. Start a fire at the distinguished vertex q
        2. A vertex burns if it has fewer chips than edges to burnt vertices
        3. Vertices that never burn form a legal firing set
        
        Returns:
            A set of vertices that form a maximal legal firing set
        """
        # First, ensure all non-q vertices are out of debt
        self.send_debt_to_q()
        
        # Initialize burnt set with the distinguished vertex q
        burnt = {self.q}
        unburnt = set(self.graph.keys()) - burnt
        
        # Continue until no new vertices burn
        changed = True
        while changed:
            changed = False
            
            # Check each unburnt vertex to see if it should burn
            for v in list(unburnt):
                # Count edges from v to burnt vertices
                edges_to_burnt = sum(self.graph[v][neighbor] 
                                    for neighbor in self.graph[v] 
                                    if neighbor in burnt)
                
                # A vertex burns if it has fewer chips than edges to burnt vertices
                if v in self.configuration and self.configuration[v] < edges_to_burnt:
                    burnt.add(v)
                    unburnt.remove(v)
                    changed = True
        
        # Return unburnt vertices (excluding q) as the maximal firing set
        return unburnt - {self.q}