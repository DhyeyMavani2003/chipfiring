# {py:mod}`chipfiring.graph`

```{py:module} chipfiring.graph
```

```{autodoc2-docstring} chipfiring.graph
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Vertex <chipfiring.graph.Vertex>`
  - ```{autodoc2-docstring} chipfiring.graph.Vertex
    :summary:
    ```
* - {py:obj}`Edge <chipfiring.graph.Edge>`
  - ```{autodoc2-docstring} chipfiring.graph.Edge
    :summary:
    ```
* - {py:obj}`Graph <chipfiring.graph.Graph>`
  - ```{autodoc2-docstring} chipfiring.graph.Graph
    :summary:
    ```
````

### API

`````{py:class} Vertex(name: str)
:canonical: chipfiring.graph.Vertex

```{autodoc2-docstring} chipfiring.graph.Vertex
```

```{rubric} Initialization
```

```{autodoc2-docstring} chipfiring.graph.Vertex.__init__
```

````{py:method} __eq__(other)
:canonical: chipfiring.graph.Vertex.__eq__

````

````{py:method} __hash__()
:canonical: chipfiring.graph.Vertex.__hash__

````

````{py:method} __str__()
:canonical: chipfiring.graph.Vertex.__str__

````

````{py:method} __lt__(other)
:canonical: chipfiring.graph.Vertex.__lt__

````

````{py:method} __le__(other)
:canonical: chipfiring.graph.Vertex.__le__

````

````{py:method} __gt__(other)
:canonical: chipfiring.graph.Vertex.__gt__

````

````{py:method} __ge__(other)
:canonical: chipfiring.graph.Vertex.__ge__

````

`````

`````{py:class} Edge(v1: chipfiring.graph.Vertex, v2: chipfiring.graph.Vertex)
:canonical: chipfiring.graph.Edge

```{autodoc2-docstring} chipfiring.graph.Edge
```

```{rubric} Initialization
```

```{autodoc2-docstring} chipfiring.graph.Edge.__init__
```

````{py:method} __eq__(other)
:canonical: chipfiring.graph.Edge.__eq__

````

````{py:method} __hash__()
:canonical: chipfiring.graph.Edge.__hash__

````

````{py:method} __str__()
:canonical: chipfiring.graph.Edge.__str__

````

`````

`````{py:class} Graph()
:canonical: chipfiring.graph.Graph

```{autodoc2-docstring} chipfiring.graph.Graph
```

```{rubric} Initialization
```

```{autodoc2-docstring} chipfiring.graph.Graph.__init__
```

````{py:method} add_vertex(vertex: chipfiring.graph.Vertex) -> None
:canonical: chipfiring.graph.Graph.add_vertex

```{autodoc2-docstring} chipfiring.graph.Graph.add_vertex
```

````

````{py:method} add_edge(v1: chipfiring.graph.Vertex, v2: chipfiring.graph.Vertex, count: int = 1) -> None
:canonical: chipfiring.graph.Graph.add_edge

```{autodoc2-docstring} chipfiring.graph.Graph.add_edge
```

````

````{py:method} get_edge_count(v1: chipfiring.graph.Vertex, v2: chipfiring.graph.Vertex) -> int
:canonical: chipfiring.graph.Graph.get_edge_count

```{autodoc2-docstring} chipfiring.graph.Graph.get_edge_count
```

````

````{py:method} vertex_degree(v: chipfiring.graph.Vertex) -> int
:canonical: chipfiring.graph.Graph.vertex_degree

```{autodoc2-docstring} chipfiring.graph.Graph.vertex_degree
```

````

````{py:method} get_vertex_degree(v: chipfiring.graph.Vertex) -> int
:canonical: chipfiring.graph.Graph.get_vertex_degree

```{autodoc2-docstring} chipfiring.graph.Graph.get_vertex_degree
```

````

````{py:method} get_neighbors(v: chipfiring.graph.Vertex) -> typing.List[chipfiring.graph.Vertex]
:canonical: chipfiring.graph.Graph.get_neighbors

```{autodoc2-docstring} chipfiring.graph.Graph.get_neighbors
```

````

````{py:method} is_connected() -> bool
:canonical: chipfiring.graph.Graph.is_connected

```{autodoc2-docstring} chipfiring.graph.Graph.is_connected
```

````

````{py:method} get_laplacian_matrix() -> numpy.ndarray
:canonical: chipfiring.graph.Graph.get_laplacian_matrix

```{autodoc2-docstring} chipfiring.graph.Graph.get_laplacian_matrix
```

````

````{py:method} get_reduced_laplacian(q: chipfiring.graph.Vertex) -> numpy.ndarray
:canonical: chipfiring.graph.Graph.get_reduced_laplacian

```{autodoc2-docstring} chipfiring.graph.Graph.get_reduced_laplacian
```

````

````{py:method} __str__() -> str
:canonical: chipfiring.graph.Graph.__str__

```{autodoc2-docstring} chipfiring.graph.Graph.__str__
```

````

`````
