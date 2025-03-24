# {py:mod}`chipfiring.dollar_game`

```{py:module} chipfiring.dollar_game
```

```{autodoc2-docstring} chipfiring.dollar_game
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DollarGame <chipfiring.dollar_game.DollarGame>`
  - ```{autodoc2-docstring} chipfiring.dollar_game.DollarGame
    :summary:
    ```
````

### API

`````{py:class} DollarGame(graph: chipfiring.graph.Graph, initial_divisor: chipfiring.divisor.Divisor)
:canonical: chipfiring.dollar_game.DollarGame

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame
```

```{rubric} Initialization
```

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.__init__
```

````{py:method} is_winnable() -> bool
:canonical: chipfiring.dollar_game.DollarGame.is_winnable

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.is_winnable
```

````

````{py:method} fire_vertex(v: chipfiring.graph.Vertex) -> None
:canonical: chipfiring.dollar_game.DollarGame.fire_vertex

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.fire_vertex
```

````

````{py:method} borrow_vertex(v: chipfiring.graph.Vertex) -> None
:canonical: chipfiring.dollar_game.DollarGame.borrow_vertex

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.borrow_vertex
```

````

````{py:method} fire_set(vertices: typing.Set[chipfiring.graph.Vertex]) -> None
:canonical: chipfiring.dollar_game.DollarGame.fire_set

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.fire_set
```

````

````{py:method} get_current_state() -> typing.Dict[chipfiring.graph.Vertex, int]
:canonical: chipfiring.dollar_game.DollarGame.get_current_state

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.get_current_state
```

````

````{py:method} get_degree() -> int
:canonical: chipfiring.dollar_game.DollarGame.get_degree

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.get_degree
```

````

````{py:method} is_effective() -> bool
:canonical: chipfiring.dollar_game.DollarGame.is_effective

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.is_effective
```

````

````{py:method} get_winning_strategy() -> typing.Optional[typing.List[chipfiring.graph.Vertex]]
:canonical: chipfiring.dollar_game.DollarGame.get_winning_strategy

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.get_winning_strategy
```

````

````{py:method} find_legal_firing_set(q: typing.Optional[chipfiring.graph.Vertex] = None) -> typing.Set[chipfiring.graph.Vertex]
:canonical: chipfiring.dollar_game.DollarGame.find_legal_firing_set

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.find_legal_firing_set
```

````

````{py:method} compute_q_reduced_divisor(q: typing.Optional[chipfiring.graph.Vertex] = None) -> chipfiring.divisor.Divisor
:canonical: chipfiring.dollar_game.DollarGame.compute_q_reduced_divisor

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.compute_q_reduced_divisor
```

````

````{py:method} __str__() -> str
:canonical: chipfiring.dollar_game.DollarGame.__str__

```{autodoc2-docstring} chipfiring.dollar_game.DollarGame.__str__
```

````

`````
