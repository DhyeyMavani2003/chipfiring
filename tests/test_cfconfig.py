import pytest
from chipfiring import CFGraph, CFDivisor, CFConfig, Vertex
import copy

# --- Fixtures for CFConfig tests ---

@pytest.fixture
def graph_abc():
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 1), ("B", "C", 1), ("A", "C", 2)]
    return CFGraph(vertices, edges)

@pytest.fixture
def divisor_abc_1(graph_abc):
    # A=2, B=1, C=0, q=None initially
    return CFDivisor(graph_abc, [("A", 2), ("B", 1), ("C", 0)])

@pytest.fixture
def config_qA_1(divisor_abc_1):
    # q=A, V~={B,C}, c(B)=1, c(C)=0
    return CFConfig(divisor_abc_1, "A")

@pytest.fixture
def config_qB_1(divisor_abc_1):
    # q=B, V~={A,C}, c(A)=2, c(C)=0
    return CFConfig(divisor_abc_1, "B")

@pytest.fixture
def graph_line3(): # A-B-C
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 1), ("B", "C", 1)]
    return CFGraph(vertices, edges)

@pytest.fixture
def divisor_line3_effective(graph_line3):
    # A=1, B=1, C=1
    return CFDivisor(graph_line3, [("A",1), ("B",1), ("C",1)])

@pytest.fixture
def config_line3_qB_eff(divisor_line3_effective):
    # q=B, V~={A,C}, c(A)=1, c(C)=1. D(q)=D(B)=1
    return CFConfig(divisor_line3_effective, "B")

@pytest.fixture
def graph_K3():
    vertices = {"v1", "v2", "v3"}
    edges = [("v1", "v2", 1), ("v2", "v3", 1), ("v1", "v3", 1)]
    return CFGraph(vertices, edges)

# --- Test CFConfig Initialization and Basic Properties ---

def test_cfconfig_init(divisor_abc_1, graph_abc):
    config = CFConfig(divisor_abc_1, "A")
    assert config.divisor == divisor_abc_1
    assert config.graph == graph_abc
    assert config.q_vertex == Vertex("A")
    assert config.v_tilde_vertices == {Vertex("B"), Vertex("C")}

def test_cfconfig_init_invalid_q(divisor_abc_1):
    with pytest.raises(ValueError, match="Vertex q='X' not found in the graph of the divisor."):
        CFConfig(divisor_abc_1, "X")

def test_get_degree_at(config_qA_1):
    assert config_qA_1.get_degree_at("B") == 1
    assert config_qA_1.get_degree_at("C") == 0

def test_get_degree_at_q_or_invalid(config_qA_1):
    with pytest.raises(ValueError, match="Configuration degree is not defined for q_vertex 'A'"):
        config_qA_1.get_degree_at("A")
    with pytest.raises(ValueError, match="Vertex 'X' not in V~"):
        config_qA_1.get_degree_at("X")

def test_is_non_negative(graph_abc, divisor_abc_1):
    config1 = CFConfig(divisor_abc_1, "A") # c(B)=1, c(C)=0. D(q)=2
    assert config1.is_non_negative()

    div_neg_B = CFDivisor(graph_abc, [("A", 2), ("B", -1), ("C", 0)])
    config2 = CFConfig(div_neg_B, "A") # c(B)=-1, c(C)=0
    assert not config2.is_non_negative()
    
    config3 = CFConfig(div_neg_B, "C") # c(A)=2, c(B)=-1. q=C, D(q)=0
    assert not config3.is_non_negative() 

def test_get_degree_sum(config_qA_1, config_qB_1):
    # config_qA_1: q=A, c(B)=1, c(C)=0. Sum = 1
    assert config_qA_1.get_degree_sum() == 1
    # config_qB_1: q=B, c(A)=2, c(C)=0. Sum = 2
    assert config_qB_1.get_degree_sum() == 2

def test_get_q_vertex_name_and_underlying_degree(config_qA_1):
    assert config_qA_1.get_q_vertex_name() == "A"
    assert config_qA_1.get_q_underlying_degree() == 2 # D(A)

def test_get_v_tilde_names(config_qA_1):
    assert config_qA_1.get_v_tilde_names() == {"B", "C"}

def test_get_config_degrees_as_dict(config_qA_1):
    assert config_qA_1.get_config_degrees_as_dict() == {"B": 1, "C": 0}

def test_repr(config_qA_1):
    assert repr(config_qA_1) == "CFConfig(q='A', Config(V~)={ B:1, C:0 })"

# --- Test CFConfig Copy ---
def test_cfconfig_copy(config_qA_1):
    copied_config = config_qA_1.copy()
    assert copied_config == config_qA_1
    assert copied_config is not config_qA_1
    assert copied_config.divisor is not config_qA_1.divisor
    assert copied_config.divisor.degrees is not config_qA_1.divisor.degrees
    # Modify original, copy should not change
    config_qA_1.divisor.degrees[Vertex("B")] = 100
    assert copied_config.get_degree_at("B") == 1
    assert config_qA_1.get_degree_at("B") == 100

# --- Test CFConfig Comparison Operators ---
def test_cfconfig_eq(graph_abc, divisor_abc_1):
    config1 = CFConfig(copy.deepcopy(divisor_abc_1), "A")
    config2 = CFConfig(copy.deepcopy(divisor_abc_1), "A")
    assert config1 == config2

    div_mod_B = CFDivisor(graph_abc, [("A", 2), ("B", 5), ("C", 0)])
    config3 = CFConfig(div_mod_B, "A") # c(B)=5, c(C)=0
    assert config1 != config3

    config4 = CFConfig(copy.deepcopy(divisor_abc_1), "B") # Different q
    assert config1 != config4

    graph_other = CFGraph({"A", "B", "C"}, [("A", "B", 1)])
    div_other_graph = CFDivisor(graph_other, [("A", 2), ("B", 1), ("C", 0)])
    config5 = CFConfig(div_other_graph, "A")
    assert config1 != config5

def test_cfconfig_ge_le_gt_lt(graph_abc):
    div1 = CFDivisor(graph_abc, [("A", 0), ("B", 2), ("C", 3)])
    div2 = CFDivisor(graph_abc, [("A", 0), ("B", 1), ("C", 4)])
    # q=A for all, D(q)=0
    c1_qA = CFConfig(div1, "A") # c1: B=2, C=3
    c2_qA = CFConfig(div2, "A") # c2: B=1, C=4
    c1_copy_qA = CFConfig(copy.deepcopy(div1), "A")

    assert c1_qA >= c1_copy_qA
    assert c1_qA <= c1_copy_qA
    assert not (c1_qA > c1_copy_qA)
    assert not (c1_qA < c1_copy_qA)

    assert not (c1_qA >= c2_qA) # B: 2 >= 1 is TRUE, C: 3 >= 4 is FALSE
    assert not (c1_qA <= c2_qA) # B: 2 <= 1 is FALSE, C: 3 <= 4 is TRUE

    # Let's make them comparable
    div3_vals = [("A", 0), ("B", 2), ("C", 3)]
    div4_vals = [("A", 0), ("B", 1), ("C", 2)]
    c3 = CFConfig(CFDivisor(graph_abc, div3_vals), "A") # B=2, C=3
    c4 = CFConfig(CFDivisor(graph_abc, div4_vals), "A") # B=1, C=2
    assert c3 >= c4
    assert c3 > c4
    assert not (c3 <= c4)
    assert not (c3 < c4)
    assert c4 <= c3
    assert c4 < c3
    assert not (c4 >= c3)
    assert not (c4 > c3)
    
    div5_vals = [("A", 0), ("B", 2), ("C", 2)]
    c5 = CFConfig(CFDivisor(graph_abc, div5_vals), "A") # B=2, C=2
    assert c3 >= c5 # B: 2>=2, C: 3>=2. TRUE
    assert c3 > c5
    assert c5 <= c3 # B: 2<=2, C: 2<=3. TRUE
    assert c5 < c3

    with pytest.raises(ValueError, match="Configurations must be on the same graph G and with the same q for comparison."):
        c1_qB = CFConfig(div1, "B")
        _ = c1_qA >= c1_qB

# --- Test CFConfig Operations (Lending, Borrowing, Firing) ---
def test_lending_move_config(config_qA_1):
    # config_qA_1: q=A, c(B)=1, c(C)=0. D(A)=2. Graph A-B(1), B-C(1), A-C(2)
    # Lend from B (val_B = deg(B,A)+deg(B,C) = 1+1=2)
    config_qA_1.lending_move("B")
    # D(B) changes from 1 to 1-2 = -1. This is c(B)
    # D(A) changes from 2 to 2+1 = 3 (neighbor of B)
    # D(C) changes from 0 to 0+1 = 1 (neighbor of B). This is c(C)
    assert config_qA_1.get_degree_at("B") == -1
    assert config_qA_1.get_degree_at("C") == 1
    assert config_qA_1.get_q_underlying_degree() == 3 # D(A) changed
    assert config_qA_1.get_degree_sum() == 0 # (-1) + 1

def test_lending_move_at_q_config(config_qA_1):
    # config_qA_1: q=A, c(B)=1, c(C)=0. D(A)=2. Graph A-B(1), B-C(1), A-C(2)
    # Lend from A (q) (val_A = deg(A,B)+deg(A,C) = 1+2=3)
    config_qA_1.lending_move("A")
    # D(A) changes from 2 to 2-3 = -1
    # D(B) changes from 1 to 1+1 = 2. This is c(B)
    # D(C) changes from 0 to 0+2 = 2. This is c(C)
    assert config_qA_1.get_degree_at("B") == 2
    assert config_qA_1.get_degree_at("C") == 2
    assert config_qA_1.get_q_underlying_degree() == -1 # D(A) changed
    assert config_qA_1.get_degree_sum() == 4

def test_borrowing_move_config(config_qA_1):
    # As above, but borrow at B
    config_qA_1.borrowing_move("B")
    # D(B) -> 1+2 = 3. c(B)=3
    # D(A) -> 2-1 = 1.
    # D(C) -> 0-1 = -1. c(C)=-1
    assert config_qA_1.get_degree_at("B") == 3
    assert config_qA_1.get_degree_at("C") == -1
    assert config_qA_1.get_q_underlying_degree() == 1
    assert config_qA_1.get_degree_sum() == 2

def test_set_fire_config(config_qA_1):
    # config_qA_1: q=A, c(B)=1, c(C)=0. D(A)=2. Graph A-B(1), B-C(1), A-C(2)
    # Fire S={B}. B is in V~. Neighbors of B are A, C.
    # A is q. C is in V~.
    # Edge (B,A) valence 1. Chips B->A. D(B) decr by 1, D(A) incr by 1.
    # Edge (B,C) valence 1. Chips B->C. D(B) decr by 1, D(C) incr by 1.
    # Net: D(B) decr by 2. D(A) incr by 1. D(C) incr by 1.
    config_qA_1.set_fire({"B"})
    # c(B) = 1 - 2 = -1
    # c(C) = 0 + 1 = 1
    # D(A) = 2 + 1 = 3
    assert config_qA_1.get_degree_at("B") == -1
    assert config_qA_1.get_degree_at("C") == 1
    assert config_qA_1.get_q_underlying_degree() == 3

def test_set_fire_config_S_includes_q_error(config_qA_1):
    with pytest.raises(ValueError, match="Firing set S cannot include q_vertex 'A'"):
        config_qA_1.set_fire({"A", "B"})

def test_set_fire_config_S_invalid_node_error(config_qA_1):
    with pytest.raises(ValueError, match="Vertex 'X' in firing set S not in V~"):
        config_qA_1.set_fire({"B", "X"})

# --- Test Superstability Related Methods ---

def test_get_out_degree_S(config_line3_qB_eff):
    # q=B, V~={A,C}, c(A)=1, c(C)=1. D(B)=1. Graph A-B(1), B-C(1)
    # S = {A}. v_in_S = A. Neighbors of A is {B}. B is not in S.
    # outdeg_S(A) = val(A,B) = 1
    assert config_line3_qB_eff.get_out_degree_S("A", {"A"}) == 1

    # S = {C}. v_in_S = C. Neighbors of C is {B}. B is not in S.
    # outdeg_S(C) = val(C,B) = 1 (edge is B-C, so C has B as neighbor due to how graph is stored)
    assert config_line3_qB_eff.get_out_degree_S("C", {"C"}) == 1 

    # S = {A,C}. v_in_S = A. Neighbors of A is {B}. B not in S.
    # outdeg_S(A) = val(A,B) = 1
    assert config_line3_qB_eff.get_out_degree_S("A", {"A", "C"}) == 1
    # v_in_S = C. Neighbors of C is {B}. B not in S.
    # outdeg_S(C) = val(C,B) = 1
    assert config_line3_qB_eff.get_out_degree_S("C", {"A", "C"}) == 1

def test_get_out_degree_S_errors(config_line3_qB_eff):
    with pytest.raises(ValueError, match="Vertex 'X' not found in graph"):
        config_line3_qB_eff.get_out_degree_S("X", {"X"})
    with pytest.raises(ValueError, match="out_degree_S is for v in S, and S must be a subset of V~"):
        config_line3_qB_eff.get_out_degree_S("B", {"B"})
    with pytest.raises(ValueError, match="Vertex 'A' must be in the provided set S_names"):
        config_line3_qB_eff.get_out_degree_S("A", {"C"})

def test_is_legal_set_firing(config_line3_qB_eff):
    # config_line3_qB_eff: q=B, V~={A,C}, c(A)=1, c(C)=1. D(B)=1. Graph A-B(1), B-C(1)
    
    # S = {A}. c(A)=1. outdeg_S(A) = val(A,B) = 1.
    # c'(A) = c(A) - outdeg_S(A) = 1 - 1 = 0. Legal.
    assert config_line3_qB_eff.is_legal_set_firing({"A"})

    # S = {C}. c(C)=1. outdeg_S(C) = val(C,B) = 1.
    # c'(C) = c(C) - outdeg_S(C) = 1 - 1 = 0. Legal.
    assert config_line3_qB_eff.is_legal_set_firing({"C"})

    # S = {A,C}. 
    # For A: c(A)=1. outdeg_S(A) = val(A,B) = 1. c'(A) = 0.
    # For C: c(C)=1. outdeg_S(C) = val(C,B) = 1. c'(C) = 0.
    # Both >=0. Legal.
    assert config_line3_qB_eff.is_legal_set_firing({"A", "C"})

    # Test non-legal: make c(A) < outdeg_S(A)
    # A=0, B=1, C=1. q=B. c(A)=0, c(C)=1.
    div_A0 = CFDivisor(config_line3_qB_eff.graph, [("A",0), ("B",1), ("C",1)])
    config_A0_qB = CFConfig(div_A0, "B")
    # S = {A}. c(A)=0. outdeg_S(A)=1. c'(A) = 0 - 1 = -1. Not legal.
    assert not config_A0_qB.is_legal_set_firing({"A"})

    # Empty set S
    assert not config_line3_qB_eff.is_legal_set_firing(set())

def test_is_legal_set_firing_errors(config_line3_qB_eff):
    with pytest.raises(ValueError, match="Firing set S cannot include q_vertex 'B'"):
        config_line3_qB_eff.is_legal_set_firing({"B"})
    with pytest.raises(ValueError, match="Vertex 'X' in firing set S not in V~"):
        config_line3_qB_eff.is_legal_set_firing({"X"})

def test_is_superstable_path_graph_example():
    # Path graph on 4 vertices 0-1-2-3. q=0.
    # Divisor d = (0,1,0,0) -> config c = (1,0,0) for V~={1,2,3} w.r.t q=0
    # c(1)=1, c(2)=0, c(3)=0
    vertices = {"v0", "v1", "v2", "v3"}
    edges = [("v0","v1",1), ("v1","v2",1), ("v2","v3",1)]
    graph = CFGraph(vertices, edges)
    divisor = CFDivisor(graph, [("v0",0), ("v1",1), ("v2",0), ("v3",0)])
    config_q0 = CFConfig(divisor, "v0")

    # c = (1,0,0) is non-negative
    assert config_q0.is_non_negative()

    # Check legal firings for S subset of V~ = {1,2,3}
    # S={1}: c(1)=1. outdeg_S(1) = val(1,0)+val(1,2)=1+1=2. c'(1) = 1-2=-1. Not legal.
    assert not config_q0.is_legal_set_firing({"v1"})
    # S={2}: c(2)=0. outdeg_S(2) = val(2,1)+val(2,3)=1+1=2. c'(2)=0-2=-2. Not legal.
    assert not config_q0.is_legal_set_firing({"v2"})
    # S={3}: c(3)=0. outdeg_S(3) = val(3,2)=1. c'(3)=0-1=-1. Not legal.
    assert not config_q0.is_legal_set_firing({"v3"})
    # S={1,2}: 
    #   v=1: c(1)=1. outdeg_S(1)=val(1,0)=1. c'(1)=1-1=0. OK.
    #   v=2: c(2)=0. outdeg_S(2)=val(2,3)=1. c'(2)=0-1=-1. Not Legal for S.
    assert not config_q0.is_legal_set_firing({"v1","v2"})
    # S={1,2,3}: 
    #   v=1: c(1)=1. outdeg_S(1)=val(1,0)=1. c'(1)=1-1=0. OK.
    #   v=2: c(2)=0. outdeg_S(2)=val(2,3)=1. c'(2)=0. OK.
    #   v=3: c(3)=0. outdeg_S(3)=val(3,2)=1. c'(3)=0. OK.
    assert config_q0.is_legal_set_firing({"v1","v2","v3"})
    
    # Perform legal set firing for S={1,2,3}
    config_q0.set_fire({"v1","v2","v3"})
    
    # Now, the resulting config is superstable.
    assert config_q0.is_superstable()

def test_is_superstable_not_superstable(graph_K3):
    # K3 graph: v1,v2,v3. q=v1. V~={v2,v3}.
    # c(v2)=2, c(v3)=2. D(v1)=any, say 0.
    # This is non-negative.
    divisor = CFDivisor(graph_K3, [("v1",0), ("v2",2), ("v3",2)])
    config = CFConfig(divisor, "v1")
    assert config.is_non_negative()
    
    # S={v2}: c(v2)=2. outdeg_S(v2) = val(v2,v1)+val(v2,v3) = 1+1=2.
    # c'(v2) = 2-2=0. Legal.
    assert config.is_legal_set_firing({"v2"})
    # Since there is a legal non-empty set firing, it is NOT superstable.
    assert not config.is_superstable()

def test_is_superstable_non_negative_false(graph_K3):
    # c(v2)=-1, c(v3)=2. Not non-negative.
    divisor = CFDivisor(graph_K3, [("v1",0), ("v2",-1), ("v3",2)])
    config = CFConfig(divisor, "v1")
    assert not config.is_non_negative()
    assert not config.is_superstable() 