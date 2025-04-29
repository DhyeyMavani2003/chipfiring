from dollar_game import DollarGame

def main():
    graph = {
        'A': {'B': 1, 'C': 1, 'E': 2},
        'B': {'A': 1, 'C': 1},
        'C': {'A': 1, 'B': 1, 'E': 1},
        'E': {'A': 2, 'C': 1}
    }
    divisor = {'A': 2, 'B': -3, 'C': 4, 'E': -1}

    # Create a DollarGame instance
    game = DollarGame(graph, divisor)
    
    # Play with the greedy algorithm
    winnable, result = game.play_game(strategy="greedy")
    if winnable:
        print("The game is winnable with the greedy algorithm.")
        print("Firing Script:", dict(result))

        # Apply the Laplacian matrix to verify the result
        resulting_divisor = game.apply_laplacian(result)
        print("Resulting Divisor:", dict(resulting_divisor))
    else:
        print("The game is not winnable with the greedy algorithm.")

    # Example of using Dhar's algorithm (consistent with example in write-up)
    divisor = {'A': 3, 'B': -2, 'C': 1, 'E': 0}
    q = 'B'  # Distinguished vertex for Dhar's algorithm

    # Create a DollarGame instance
    game = DollarGame(graph, divisor)

    # Play with Dhar's algorithm
    winnable, result = game.play_game(strategy="dhar", q=q)
    if winnable:
        print("The game is winnable with Dhar's algorithm.")
        print("Legal firing set:", result)
    else:
        print("The game is superstable with Dhar's algorithm.")

if __name__ == "__main__":
    main()