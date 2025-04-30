from .dollar_game import DollarGame # Relative
from .graph import Graph, Vertex # Relative
from .divisor import Divisor # Relative

def main():
    # Define vertices
    vA = Vertex('A')
    vB = Vertex('B')
    vC = Vertex('C')
    vE = Vertex('E')
    vertices = {v.name: v for v in [vA, vB, vC, vE]}

    # Create Graph instance
    graph_obj = Graph()
    graph_obj.add_edge(vA, vB, count=1)
    graph_obj.add_edge(vA, vC, count=1)
    graph_obj.add_edge(vA, vE, count=2)
    graph_obj.add_edge(vB, vC, count=1)
    graph_obj.add_edge(vC, vE, count=1)
    # Note: A-B, A-C, B-C, etc. already added symmetrically

    # Define initial divisor using Vertex objects
    initial_divisor_vals_1 = {vA: 2, vB: -3, vC: 4, vE: -1}
    divisor_obj_1 = Divisor(graph_obj, initial_divisor_vals_1)

    # Create a DollarGame instance
    game1 = DollarGame(graph_obj, divisor_obj_1)
    
    print("--- Greedy Algorithm Game --- ")
    # Play with the greedy algorithm
    winnable, result_greedy = game1.play_game(strategy="greedy") # result is firing script
    if winnable:
        print("The game is winnable with the greedy algorithm.")
        # Convert firing script keys (Vertex) to names for printing
        firing_script_print = {v.name: count for v, count in result_greedy.items()}
        print("Firing Script:", firing_script_print)

        # Apply the Laplacian matrix to verify the result
        resulting_divisor_dict = game1.apply_laplacian(result_greedy)
        # Convert resulting divisor keys (Vertex) to names for printing
        resulting_divisor_print = {v.name: val for v, val in resulting_divisor_dict.items()}
        print("Resulting Divisor:", resulting_divisor_print)
    else:
        print("The game is not winnable with the greedy algorithm.")
    print("\n" + "-"*27 + "\n")

    # Example of using Dhar's algorithm (consistent with example in write-up)
    initial_divisor_vals_2 = {vA: 3, vB: -2, vC: 1, vE: 0}
    divisor_obj_2 = Divisor(graph_obj, initial_divisor_vals_2)
    q_name = 'B'  # Distinguished vertex name for Dhar's algorithm

    # Create a new DollarGame instance with the second divisor
    game2 = DollarGame(graph_obj, divisor_obj_2)

    print("--- Dhar's Algorithm Game --- ")
    # Play with Dhar's algorithm
    winnable, result_dhar = game2.play_game(strategy="dhar", q=q_name)
    if winnable:
        print("The game is winnable with Dhar's algorithm.")
        # Convert legal firing set keys (Vertex) to names for printing
        legal_firing_set_print = {v.name: count for v, count in result_dhar.items()}
        print("Legal firing set:", legal_firing_set_print)
    else:
        print("The game is superstable with Dhar's algorithm.")

if __name__ == "__main__":
    main()