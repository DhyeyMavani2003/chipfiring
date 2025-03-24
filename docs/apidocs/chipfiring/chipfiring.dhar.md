# {py:mod}`chipfiring.dhar`

```{py:module} chipfiring.dhar
```

```{autodoc2-docstring} chipfiring.dhar
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`outdegree_to_set <chipfiring.dhar.outdegree_to_set>`
  - ```{autodoc2-docstring} chipfiring.dhar.outdegree_to_set
    :summary:
    ```
* - {py:obj}`find_legal_firing_set <chipfiring.dhar.find_legal_firing_set>`
  - ```{autodoc2-docstring} chipfiring.dhar.find_legal_firing_set
    :summary:
    ```
* - {py:obj}`is_q_reduced <chipfiring.dhar.is_q_reduced>`
  - ```{autodoc2-docstring} chipfiring.dhar.is_q_reduced
    :summary:
    ```
* - {py:obj}`send_debt_to_q <chipfiring.dhar.send_debt_to_q>`
  - ```{autodoc2-docstring} chipfiring.dhar.send_debt_to_q
    :summary:
    ```
* - {py:obj}`q_reduce <chipfiring.dhar.q_reduce>`
  - ```{autodoc2-docstring} chipfiring.dhar.q_reduce
    :summary:
    ```
* - {py:obj}`is_winnable_dhar <chipfiring.dhar.is_winnable_dhar>`
  - ```{autodoc2-docstring} chipfiring.dhar.is_winnable_dhar
    :summary:
    ```
* - {py:obj}`get_winning_strategy_dhar <chipfiring.dhar.get_winning_strategy_dhar>`
  - ```{autodoc2-docstring} chipfiring.dhar.get_winning_strategy_dhar
    :summary:
    ```
````

### API

````{py:function} outdegree_to_set(graph: chipfiring.graph.Graph, vertex: chipfiring.graph.Vertex, subset: typing.Set[chipfiring.graph.Vertex]) -> int
:canonical: chipfiring.dhar.outdegree_to_set

```{autodoc2-docstring} chipfiring.dhar.outdegree_to_set
```
````

````{py:function} find_legal_firing_set(graph: chipfiring.graph.Graph, divisor: chipfiring.divisor.Divisor, q: chipfiring.graph.Vertex) -> typing.Set[chipfiring.graph.Vertex]
:canonical: chipfiring.dhar.find_legal_firing_set

```{autodoc2-docstring} chipfiring.dhar.find_legal_firing_set
```
````

````{py:function} is_q_reduced(graph: chipfiring.graph.Graph, divisor: chipfiring.divisor.Divisor, q: chipfiring.graph.Vertex) -> bool
:canonical: chipfiring.dhar.is_q_reduced

```{autodoc2-docstring} chipfiring.dhar.is_q_reduced
```
````

````{py:function} send_debt_to_q(graph: chipfiring.graph.Graph, divisor: chipfiring.divisor.Divisor, q: chipfiring.graph.Vertex) -> chipfiring.divisor.Divisor
:canonical: chipfiring.dhar.send_debt_to_q

```{autodoc2-docstring} chipfiring.dhar.send_debt_to_q
```
````

````{py:function} q_reduce(graph: chipfiring.graph.Graph, divisor: chipfiring.divisor.Divisor, q: chipfiring.graph.Vertex) -> chipfiring.divisor.Divisor
:canonical: chipfiring.dhar.q_reduce

```{autodoc2-docstring} chipfiring.dhar.q_reduce
```
````

````{py:function} is_winnable_dhar(graph: chipfiring.graph.Graph, divisor: chipfiring.divisor.Divisor) -> bool
:canonical: chipfiring.dhar.is_winnable_dhar

```{autodoc2-docstring} chipfiring.dhar.is_winnable_dhar
```
````

````{py:function} get_winning_strategy_dhar(graph: chipfiring.graph.Graph, divisor: chipfiring.divisor.Divisor) -> typing.Optional[typing.Dict[chipfiring.graph.Vertex, int]]
:canonical: chipfiring.dhar.get_winning_strategy_dhar

```{autodoc2-docstring} chipfiring.dhar.get_winning_strategy_dhar
```
````
