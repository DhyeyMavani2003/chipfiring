from chipfiring.CFGraph import CFGraph
from chipfiring.CFDivisor import CFDivisor
from chipfiring.algo import EWD

def main():
    # Create a simple graph
    vertices = {"Alice", "Bob", "Charlie", "Elise"}
    edges = [("Alice", "Bob", 1), ("Bob", "Charlie", 1), ("Charlie", "Elise", 1), ("Elise", "Alice", 2), ("Alice", "Charlie", 1)]
    graph = CFGraph(vertices, edges)

    # Create a divisor
    divisor = CFDivisor(graph, [("Alice", 2), ("Bob", -3), ("Charlie", 4), ("Elise", -1)])

    # Run the EWD algorithm with visualization enabled.
    # The EWD function will now handle the visualization directly.
    is_winnable, _, _ = EWD(graph, divisor, optimized=True, visualize=True)

    # This print statement will execute after you close the visualization window.
    print(f"Is the divisor winnable? {is_winnable}")

if __name__ == "__main__":
    main()
