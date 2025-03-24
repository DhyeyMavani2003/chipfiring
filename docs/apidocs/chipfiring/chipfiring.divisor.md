# {py:mod}`chipfiring.divisor`

```{py:module} chipfiring.divisor
```

```{autodoc2-docstring} chipfiring.divisor
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Divisor <chipfiring.divisor.Divisor>`
  - ```{autodoc2-docstring} chipfiring.divisor.Divisor
    :summary:
    ```
````

### API

`````{py:class} Divisor(graph: chipfiring.graph.Graph, values: typing.Optional[typing.Dict[chipfiring.graph.Vertex, int]] = None)
:canonical: chipfiring.divisor.Divisor

```{autodoc2-docstring} chipfiring.divisor.Divisor
```

```{rubric} Initialization
```

```{autodoc2-docstring} chipfiring.divisor.Divisor.__init__
```

````{py:method} __getitem__(v: chipfiring.graph.Vertex) -> int
:canonical: chipfiring.divisor.Divisor.__getitem__

```{autodoc2-docstring} chipfiring.divisor.Divisor.__getitem__
```

````

````{py:method} __setitem__(v: chipfiring.graph.Vertex, value: int) -> None
:canonical: chipfiring.divisor.Divisor.__setitem__

```{autodoc2-docstring} chipfiring.divisor.Divisor.__setitem__
```

````

````{py:method} __eq__(other)
:canonical: chipfiring.divisor.Divisor.__eq__

```{autodoc2-docstring} chipfiring.divisor.Divisor.__eq__
```

````

````{py:method} __add__(other)
:canonical: chipfiring.divisor.Divisor.__add__

```{autodoc2-docstring} chipfiring.divisor.Divisor.__add__
```

````

````{py:method} __sub__(other)
:canonical: chipfiring.divisor.Divisor.__sub__

```{autodoc2-docstring} chipfiring.divisor.Divisor.__sub__
```

````

````{py:method} __mul__(scalar)
:canonical: chipfiring.divisor.Divisor.__mul__

```{autodoc2-docstring} chipfiring.divisor.Divisor.__mul__
```

````

````{py:method} __rmul__(scalar)
:canonical: chipfiring.divisor.Divisor.__rmul__

```{autodoc2-docstring} chipfiring.divisor.Divisor.__rmul__
```

````

````{py:method} degree() -> int
:canonical: chipfiring.divisor.Divisor.degree

```{autodoc2-docstring} chipfiring.divisor.Divisor.degree
```

````

````{py:method} is_effective() -> bool
:canonical: chipfiring.divisor.Divisor.is_effective

```{autodoc2-docstring} chipfiring.divisor.Divisor.is_effective
```

````

````{py:method} is_principal()
:canonical: chipfiring.divisor.Divisor.is_principal

```{autodoc2-docstring} chipfiring.divisor.Divisor.is_principal
```

````

````{py:method} is_linearly_equivalent(other: chipfiring.divisor.Divisor) -> bool
:canonical: chipfiring.divisor.Divisor.is_linearly_equivalent

```{autodoc2-docstring} chipfiring.divisor.Divisor.is_linearly_equivalent
```

````

````{py:method} rank()
:canonical: chipfiring.divisor.Divisor.rank

```{autodoc2-docstring} chipfiring.divisor.Divisor.rank
```

````

````{py:method} _generate_effective_divisors(degree)
:canonical: chipfiring.divisor.Divisor._generate_effective_divisors

```{autodoc2-docstring} chipfiring.divisor.Divisor._generate_effective_divisors
```

````

````{py:method} to_vector() -> numpy.ndarray
:canonical: chipfiring.divisor.Divisor.to_vector

```{autodoc2-docstring} chipfiring.divisor.Divisor.to_vector
```

````

````{py:method} from_vector(graph: chipfiring.graph.Graph, vector: numpy.ndarray) -> chipfiring.divisor.Divisor
:canonical: chipfiring.divisor.Divisor.from_vector
:classmethod:

```{autodoc2-docstring} chipfiring.divisor.Divisor.from_vector
```

````

````{py:method} apply_laplacian(firing_script: typing.Dict[chipfiring.graph.Vertex, int]) -> chipfiring.divisor.Divisor
:canonical: chipfiring.divisor.Divisor.apply_laplacian

```{autodoc2-docstring} chipfiring.divisor.Divisor.apply_laplacian
```

````

````{py:method} to_dict()
:canonical: chipfiring.divisor.Divisor.to_dict

```{autodoc2-docstring} chipfiring.divisor.Divisor.to_dict
```

````

````{py:method} from_dict(graph: chipfiring.graph.Graph, values: typing.Dict[chipfiring.graph.Vertex, int]) -> chipfiring.divisor.Divisor
:canonical: chipfiring.divisor.Divisor.from_dict
:classmethod:

```{autodoc2-docstring} chipfiring.divisor.Divisor.from_dict
```

````

````{py:method} _effective_divisors()
:canonical: chipfiring.divisor.Divisor._effective_divisors

```{autodoc2-docstring} chipfiring.divisor.Divisor._effective_divisors
```

````

````{py:method} __str__() -> str
:canonical: chipfiring.divisor.Divisor.__str__

```{autodoc2-docstring} chipfiring.divisor.Divisor.__str__
```

````

`````
