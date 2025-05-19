import pytest
import os
import warnings
from chipfiring.CFDataProcessor import CFDataProcessor
from chipfiring.CFGraph import CFGraph
from chipfiring.CFDivisor import CFDivisor
from chipfiring.CFOrientation import CFOrientation
from chipfiring.CFiringScript import CFiringScript


@pytest.fixture
def sample_graph():
    """Create a sample graph for testing."""
    vertices = {"A", "B", "C"}
    edges = [("A", "B", 2), ("B", "C", 1), ("A", "C", 1)]
    return CFGraph(vertices, edges)


@pytest.fixture
def sample_divisor(sample_graph):
    """Create a sample divisor for testing."""
    degrees = [("A", 2), ("B", -1), ("C", 3)]
    return CFDivisor(sample_graph, degrees)


@pytest.fixture
def sample_orientation(sample_graph):
    """Create a sample orientation for testing."""
    orientations = [("A", "B"), ("B", "C"), ("A", "C")]
    return CFOrientation(sample_graph, orientations)


@pytest.fixture
def sample_firingscript(sample_graph):
    """Create a sample firing script for testing."""
    script = {"A": 2, "B": -1, "C": 3}
    return CFiringScript(sample_graph, script)


@pytest.fixture
def data_processor():
    """Create a CFDataProcessor instance."""
    return CFDataProcessor()


class TestCFDataProcessorJSON:
    """Test JSON input/output methods of CFDataProcessor."""

    def test_graph_to_json(self, data_processor, sample_graph, tmp_path):
        """Test writing and reading a graph to/from JSON."""
        # Write to JSON
        file_path = os.path.join(tmp_path, "graph.json")
        data_processor.to_json(sample_graph, file_path)
        
        # Read from JSON
        read_graph = data_processor.read_json(file_path, "graph")
        
        # Check if the read graph matches the original
        assert read_graph.to_dict() == sample_graph.to_dict()
    
    def test_divisor_to_json(self, data_processor, sample_divisor, tmp_path):
        """Test writing and reading a divisor to/from JSON."""
        # Write to JSON
        file_path = os.path.join(tmp_path, "divisor.json")
        data_processor.to_json(sample_divisor, file_path)
        
        # Read from JSON
        read_divisor = data_processor.read_json(file_path, "divisor")
        
        # Check if the read divisor matches the original
        assert read_divisor.to_dict() == sample_divisor.to_dict()
    
    def test_orientation_to_json(self, data_processor, sample_orientation, tmp_path):
        """Test writing and reading an orientation to/from JSON."""
        # Write to JSON
        file_path = os.path.join(tmp_path, "orientation.json")
        data_processor.to_json(sample_orientation, file_path)
        
        # Read from JSON
        read_orientation = data_processor.read_json(file_path, "orientation")
        
        # Check if the read orientation matches the original
        assert read_orientation.to_dict() == sample_orientation.to_dict()
    
    def test_firingscript_to_json(self, data_processor, sample_firingscript, tmp_path):
        """Test writing and reading a firing script to/from JSON."""
        # Write to JSON
        file_path = os.path.join(tmp_path, "firingscript.json")
        data_processor.to_json(sample_firingscript, file_path)
        
        # Read from JSON
        read_script = data_processor.read_json(file_path, "firingscript")
        
        # Check if the read script matches the original
        assert read_script.to_dict() == sample_firingscript.to_dict()
    
    def test_read_favorite_graph_json(self, data_processor):
        """Test reading the favorite_graph.json file."""
        file_path = "tests/data/json/favorite_graph.json"
        graph = data_processor.read_json(file_path, "graph")
        
        # Verify the graph was read correctly
        assert graph is not None
        # Check vertex count
        assert len(graph.vertices) == 4
        # Verify some vertices exist
        vertex_names = {v.name for v in graph.vertices}
        assert "Alice" in vertex_names
        assert "Bob" in vertex_names
        assert "Charlie" in vertex_names
        assert "Elise" in vertex_names
    
    def test_read_favorite_divisor_json(self, data_processor):
        """Test reading the favorite_divisor.json file."""
        file_path = "tests/data/json/favorite_divisor.json"
        divisor = data_processor.read_json(file_path, "divisor")
        
        # Verify the divisor was read correctly
        assert divisor is not None
        # Check underlying graph
        assert len(divisor.graph.vertices) == 4
        # Verify some degree values
        for vertex in divisor.graph.vertices:
            if vertex.name == "Alice":
                assert divisor.get_degree(vertex.name) is not None
    
    def test_read_favorite_orientation_json(self, data_processor):
        """Test reading the favorite_orientation.json file."""
        file_path = "tests/data/json/favorite_orientation.json"
        orientation = data_processor.read_json(file_path, "orientation")
        
        # Verify the orientation was read correctly
        assert orientation is not None
        # Check underlying graph
        assert len(orientation.graph.vertices) == 4
        # Verify orientation structure
        assert len(orientation.to_dict().get("orientations", [])) > 0
    
    def test_read_favorite_firingscript_json(self, data_processor):
        """Test reading the favorite_firing_script.json file."""
        file_path = "tests/data/json/favorite_firing_script.json"
        script = data_processor.read_json(file_path, "firingscript")
        
        # Verify the script was read correctly
        assert script is not None
        # Check underlying graph
        assert len(script.graph.vertices) == 4
        # Verify script has firing values
        assert len([val for val in script.script.values() if val != 0]) > 0
    
    def test_invalid_json_read(self, data_processor, tmp_path):
        """Test reading from an invalid JSON file."""
        # Create an invalid JSON file
        file_path = os.path.join(tmp_path, "invalid.json")
        with open(file_path, 'w') as f:
            f.write("{Invalid JSON}")
        
        # Attempt to read from invalid JSON
        result = data_processor.read_json(file_path, "graph")
        assert result is None
    
    def test_nonexistent_file_read(self, data_processor):
        """Test reading from a nonexistent file."""
        result = data_processor.read_json("nonexistent_file.json", "graph")
        assert result is None


class TestCFDataProcessorTXT:
    """Test TXT input/output methods of CFDataProcessor."""

    def test_graph_to_txt(self, data_processor, sample_graph, tmp_path):
        """Test writing and reading a graph to/from TXT."""
        # Write to TXT
        file_path = os.path.join(tmp_path, "graph.txt")
        data_processor.to_txt(sample_graph, file_path)
        
        # Read from TXT
        read_graph = data_processor.read_txt(file_path, "graph")
        
        # Check if the read graph matches the original
        assert read_graph.to_dict() == sample_graph.to_dict()
    
    def test_divisor_to_txt(self, data_processor, sample_divisor, tmp_path):
        """Test writing and reading a divisor to/from TXT."""
        # Write to TXT
        file_path = os.path.join(tmp_path, "divisor.txt")
        data_processor.to_txt(sample_divisor, file_path)
        
        # Read from TXT
        read_divisor = data_processor.read_txt(file_path, "divisor")
        
        # Check if the read divisor matches the original
        assert read_divisor.to_dict() == sample_divisor.to_dict()
    
    def test_orientation_to_txt(self, data_processor, sample_orientation, tmp_path):
        """Test writing and reading an orientation to/from TXT."""
        # Write to TXT
        file_path = os.path.join(tmp_path, "orientation.txt")
        data_processor.to_txt(sample_orientation, file_path)
        
        # Read from TXT
        read_orientation = data_processor.read_txt(file_path, "orientation")
        
        # Check if the read orientation matches the original
        assert read_orientation.to_dict() == sample_orientation.to_dict()
    
    def test_firingscript_to_txt(self, data_processor, sample_firingscript, tmp_path):
        """Test writing and reading a firing script to/from TXT."""
        # Write to TXT
        file_path = os.path.join(tmp_path, "firingscript.txt")
        data_processor.to_txt(sample_firingscript, file_path)
        
        # Read from TXT
        read_script = data_processor.read_txt(file_path, "firingscript")
        
        # Check if the read script matches the original
        assert read_script.to_dict() == sample_firingscript.to_dict()
    
    def test_read_favorite_graph_txt(self, data_processor):
        """Test reading the favorite_graph.txt file."""
        file_path = "tests/data/txt/favorite_graph.txt"
        graph = data_processor.read_txt(file_path, "graph")
        
        # Verify the graph was read correctly
        assert graph is not None
        # Check vertex count
        assert len(graph.vertices) == 4
        # Verify some vertices exist
        vertex_names = {v.name for v in graph.vertices}
        assert "Alice" in vertex_names
        assert "Bob" in vertex_names
        assert "Charlie" in vertex_names
        assert "Elise" in vertex_names
    
    def test_read_favorite_divisor_txt(self, data_processor):
        """Test reading the favorite_divisor.txt file."""
        file_path = "tests/data/txt/favorite_divisor.txt"
        divisor = data_processor.read_txt(file_path, "divisor")
        
        # Verify the divisor was read correctly
        assert divisor is not None
        # Check underlying graph
        assert len(divisor.graph.vertices) == 4
        # Verify some degree values
        for vertex in divisor.graph.vertices:
            if vertex.name == "Alice":
                assert divisor.get_degree(vertex.name) is not None
    
    def test_read_favorite_orientation_txt(self, data_processor):
        """Test reading the favorite_orientation.txt file."""
        file_path = "tests/data/txt/favorite_orientation.txt"
        orientation = data_processor.read_txt(file_path, "orientation")
        
        # Verify the orientation was read correctly
        assert orientation is not None
        # Check underlying graph
        assert len(orientation.graph.vertices) == 4
        # Verify orientation structure
        assert len(orientation.to_dict().get("orientations", [])) > 0
    
    def test_read_favorite_firingscript_txt(self, data_processor):
        """Test reading the favorite_firing_script.txt file."""
        file_path = "tests/data/txt/favorite_firing_script.txt"
        script = data_processor.read_txt(file_path, "firingscript")
        
        # Verify the script was read correctly
        assert script is not None
        # Check underlying graph
        assert len(script.graph.vertices) == 4
        # Verify script has firing values
        assert len([val for val in script.script.values() if val != 0]) > 0
    
    def test_malformed_txt_read(self, data_processor, tmp_path):
        """Test reading from a malformed TXT file."""
        # Create a malformed TXT file
        file_path = os.path.join(tmp_path, "malformed.txt")
        with open(file_path, 'w') as f:
            f.write("VERTICES: A, B\nMALFORMED_LINE: X, Y")
        
        # Attempt to read from malformed TXT
        result = data_processor.read_txt(file_path, "graph")
        # Should still return a graph with vertices A and B
        assert result is not None
        assert len(result.vertices) == 2
    
    def test_nonexistent_file_read_txt(self, data_processor):
        """Test reading from a nonexistent TXT file."""
        result = data_processor.read_txt("nonexistent_file.txt", "graph")
        assert result is None


class TestCFDataProcessorTeX:
    """Test TeX output methods of CFDataProcessor."""

    def test_graph_to_tex(self, data_processor, sample_graph, tmp_path):
        """Test writing a graph to TeX."""
        # Write to TeX
        file_path = os.path.join(tmp_path, "graph.tex")
        data_processor.to_tex(sample_graph, file_path)
        
        # Check that the file was created
        assert os.path.exists(file_path)
        
        # Basic check of file content
        with open(file_path, 'r') as f:
            content = f.read()
            assert "\\begin{tikzpicture}" in content
            assert "\\end{tikzpicture}" in content
            
            # Check that all vertices are represented
            for vertex in sample_graph.vertices:
                assert vertex.name in content
    
    def test_divisor_to_tex(self, data_processor, sample_divisor, tmp_path):
        """Test writing a divisor to TeX."""
        # Write to TeX
        file_path = os.path.join(tmp_path, "divisor.tex")
        data_processor.to_tex(sample_divisor, file_path)
        
        # Check that the file was created
        assert os.path.exists(file_path)
        
        # Basic check of file content
        with open(file_path, 'r') as f:
            content = f.read()
            assert "\\begin{tikzpicture}" in content
            assert "% Divisor Definition" in content
            
            # Check that all vertices and their degrees are represented
            for vertex in sample_divisor.graph.vertices:
                assert f"{vertex.name}" in content.replace("\\_", "_")
    
    def test_orientation_to_tex(self, data_processor, sample_orientation, tmp_path):
        """Test writing an orientation to TeX."""
        # Write to TeX
        file_path = os.path.join(tmp_path, "orientation.tex")
        data_processor.to_tex(sample_orientation, file_path)
        
        # Check that the file was created
        assert os.path.exists(file_path)
        
        # Basic check of file content
        with open(file_path, 'r') as f:
            content = f.read()
            assert "\\begin{tikzpicture}" in content
            assert "% Orientation Definition" in content
            
            # Check that the file contains path commands with arrow markers
            assert "\\path[->]" in content
    
    def test_firingscript_to_tex(self, data_processor, sample_firingscript, tmp_path):
        """Test writing a firing script to TeX."""
        # Write to TeX
        file_path = os.path.join(tmp_path, "firingscript.tex")
        data_processor.to_tex(sample_firingscript, file_path)
        
        # Check that the file was created
        assert os.path.exists(file_path)
        
        # Basic check of file content
        with open(file_path, 'r') as f:
            content = f.read()
            assert "\\begin{tikzpicture}" in content
            assert "% Firing Script Definition" in content
            
            # Check that all vertices and their firing counts are represented
            for vertex_name, fires in sample_firingscript.script.items():
                # Only check non-zero values as they are labeled in the TeX
                if fires != 0:
                    # The firing count is included in the label: "A"
                    assert f"{vertex_name}" in content.replace("\\_", "_")
    
    def test_no_invalid_escape_sequence_warnings(self, data_processor, sample_graph, tmp_path):
        """Test that no invalid escape sequence warnings are generated in TeX output."""
        # Write to TeX
        file_path = os.path.join(tmp_path, "graph_escape_test.tex")
        
        # Capture warnings during TeX writing
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered
            warnings.simplefilter("always")
            
            # Call the function that should generate no warnings
            data_processor.to_tex(sample_graph, file_path)
            
            # Check for escape sequence warnings
            for warning in w:
                assert not issubclass(warning.category, SyntaxWarning) or "invalid escape sequence" not in str(warning.message)
    
    def test_unsupported_type_tex(self, data_processor, tmp_path):
        """Test handling of unsupported object types for TeX serialization."""
        # Create a file path
        file_path = os.path.join(tmp_path, "unsupported.tex")
        
        # Create a string (unsupported type)
        unsupported_obj = "This is not a CF object"
        
        # We expect a warning to be printed, not an exception
        data_processor.to_tex(unsupported_obj, file_path)
        
        # Check that the file was created with a comment about the unsupported type
        with open(file_path, 'r') as f:
            content = f.read()
            assert "% Object type: <class 'str'>" in content
            assert "% Data: TeX representation not implemented for this type" in content


class TestCFDataProcessorMultiFormat:
    """Test interactions between different formats."""
    
    def test_txt_to_json(self, data_processor, sample_graph, tmp_path):
        """Test converting between formats: TXT -> JSON."""
        # Write to TXT
        txt_path = os.path.join(tmp_path, "graph.txt")
        data_processor.to_txt(sample_graph, txt_path)
        
        # Read from TXT
        txt_graph = data_processor.read_txt(txt_path, "graph")
        
        # Write to JSON
        json_path = os.path.join(tmp_path, "graph.json")
        data_processor.to_json(txt_graph, json_path)
        
        # Read from JSON
        json_graph = data_processor.read_json(json_path, "graph")
        
        # Check that the final graph still matches the original
        assert json_graph.to_dict() == sample_graph.to_dict()
    
    def test_favorite_graph_json_to_txt(self, data_processor, tmp_path):
        """Test converting favorite graph from JSON to TXT."""
        # Read original JSON
        json_path = "tests/data/json/favorite_graph.json"
        json_graph = data_processor.read_json(json_path, "graph")
        
        # Write to TXT
        txt_path = os.path.join(tmp_path, "favorite_graph_converted.txt")
        data_processor.to_txt(json_graph, txt_path)
        
        # Read back from TXT
        txt_graph = data_processor.read_txt(txt_path, "graph")
        
        # Check that the graphs match
        assert txt_graph.to_dict() == json_graph.to_dict()
        
        # Check vertex count in both
        assert len(txt_graph.vertices) == len(json_graph.vertices) == 4
    
    def test_favorite_graph_txt_to_json(self, data_processor, tmp_path):
        """Test converting favorite graph from TXT to JSON."""
        # Read original TXT
        txt_path = "tests/data/txt/favorite_graph.txt"
        txt_graph = data_processor.read_txt(txt_path, "graph")
        
        # Write to JSON
        json_path = os.path.join(tmp_path, "favorite_graph_converted.json")
        data_processor.to_json(txt_graph, json_path)
        
        # Read back from JSON
        json_graph = data_processor.read_json(json_path, "graph")
        
        # Check that the graphs match
        assert json_graph.to_dict() == txt_graph.to_dict()
        
        # Check vertex count in both
        assert len(json_graph.vertices) == len(txt_graph.vertices) == 4
    
    def test_favorite_divisor_format_conversion(self, data_processor, tmp_path):
        """Test converting favorite divisor between formats."""
        # Read from JSON
        json_divisor = data_processor.read_json("tests/data/json/favorite_divisor.json", "divisor")
        
        # Convert to TXT
        txt_path = os.path.join(tmp_path, "divisor_converted.txt")
        data_processor.to_txt(json_divisor, txt_path)
        
        # Read back from TXT
        txt_divisor = data_processor.read_txt(txt_path, "divisor")
        
        # Check equivalence
        assert txt_divisor.to_dict() == json_divisor.to_dict()
    
    def test_favorite_orientation_format_conversion(self, data_processor, tmp_path):
        """Test converting favorite orientation between formats."""
        # Read from TXT
        txt_orientation = data_processor.read_txt("tests/data/txt/favorite_orientation.txt", "orientation")
        
        # Convert to JSON
        json_path = os.path.join(tmp_path, "orientation_converted.json")
        data_processor.to_json(txt_orientation, json_path)
        
        # Read back from JSON
        json_orientation = data_processor.read_json(json_path, "orientation")
        
        # Check equivalence
        assert json_orientation.to_dict() == txt_orientation.to_dict()
    
    def test_favorite_firingscript_format_conversion(self, data_processor, tmp_path):
        """Test converting favorite firing script between formats."""
        # Read from JSON
        json_script = data_processor.read_json("tests/data/json/favorite_firing_script.json", "firingscript")
        
        # Convert to TXT
        txt_path = os.path.join(tmp_path, "firingscript_converted.txt")
        data_processor.to_txt(json_script, txt_path)
        
        # Read back from TXT
        txt_script = data_processor.read_txt(txt_path, "firingscript")
        
        # Check equivalence
        assert txt_script.to_dict() == json_script.to_dict()
    
    def test_error_handling_unsupported_type(self, data_processor, tmp_path):
        """Test error handling when trying to write an unsupported type."""
        # Create a file path
        file_path = os.path.join(tmp_path, "unsupported.json")
        
        # Try to write an unsupported type
        with pytest.raises(ValueError):
            data_processor.to_json("not_a_cf_object", file_path) 