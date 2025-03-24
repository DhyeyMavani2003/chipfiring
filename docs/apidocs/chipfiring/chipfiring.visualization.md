# {py:mod}`chipfiring.visualization`

```{py:module} chipfiring.visualization
```

```{autodoc2-docstring} chipfiring.visualization
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_to_networkx_graph <chipfiring.visualization._to_networkx_graph>`
  - ```{autodoc2-docstring} chipfiring.visualization._to_networkx_graph
    :summary:
    ```
* - {py:obj}`draw_graph <chipfiring.visualization.draw_graph>`
  - ```{autodoc2-docstring} chipfiring.visualization.draw_graph
    :summary:
    ```
* - {py:obj}`draw_game_state <chipfiring.visualization.draw_game_state>`
  - ```{autodoc2-docstring} chipfiring.visualization.draw_game_state
    :summary:
    ```
````

### API

````{py:function} _to_networkx_graph(G: chipfiring.graph.Graph) -> networkx.Graph
:canonical: chipfiring.visualization._to_networkx_graph

```{autodoc2-docstring} chipfiring.visualization._to_networkx_graph
```
````

````{py:function} draw_graph(G: chipfiring.graph.Graph, D: typing.Optional[chipfiring.divisor.Divisor] = None, title: typing.Optional[str] = None, pos: typing.Optional[typing.Dict[chipfiring.graph.Vertex, typing.Tuple[float, float]]] = None, node_color: str = 'lightblue', edge_color: str = 'gray', node_size: int = 1000, font_size: int = 12) -> typing.Tuple[matplotlib.pyplot.Figure, matplotlib.pyplot.Axes]
:canonical: chipfiring.visualization.draw_graph

```{autodoc2-docstring} chipfiring.visualization.draw_graph
```
````

````{py:function} draw_game_state(game: typing.Any, title: typing.Optional[str] = None, pos: typing.Optional[typing.Dict[chipfiring.graph.Vertex, typing.Tuple[float, float]]] = None, node_size: int = 1000, font_size: int = 12) -> typing.Tuple[matplotlib.pyplot.Figure, matplotlib.pyplot.Axes]
:canonical: chipfiring.visualization.draw_game_state

```{autodoc2-docstring} chipfiring.visualization.draw_game_state
```
````
