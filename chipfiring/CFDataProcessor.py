from __future__ import annotations
import json
from .CFGraph import CFGraph
from .CFDivisor import CFDivisor
from .CFOrientation import CFOrientation
from .CFiringScript import CFiringScript

class CFDataProcessor:
    """
    A class to handle data input and output for chip-firing objects
    in various formats like .txt, .json, and .tex.
    """

    def __init__(self):
        """
        Initialize the CFDataProcessor.
        """
        pass

    # --- JSON Methods ---
    def read_json(self, file_path: str, object_type: str):
        """
        Reads a CF object from a .json file.

        Args:
            file_path (str): The path to the .json file.
            object_type (str): The type of CF object to read ('graph', 'divisor', 'orientation', 'firingscript').

        Returns:
            A CF object (e.g., CFGraph, CFDivisor) or None if reading fails.
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if object_type.lower() == 'graph':
                return CFGraph.from_dict(data)
            elif object_type.lower() == 'divisor':
                return CFDivisor.from_dict(data)
            elif object_type.lower() == 'orientation':
                return CFOrientation.from_dict(data)
            elif object_type.lower() == 'firingscript':
                return CFiringScript.from_dict(data)
            else:
                print(f"Unsupported object_type for JSON reading: {object_type}. Please use 'graph', 'divisor', 'orientation', or 'firingscript'.")
                return None
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {file_path}")
            return None
        except ValueError as ve:
            print(f"Error processing data for {object_type}: {ve}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while reading JSON: {e}")
            return None

    def to_json(self, cf_object, file_path: str):
        """
        Writes a CF object to a .json file.

        Args:
            cf_object: The CF object to serialize (e.g., CFGraph, CFDivisor).
            file_path (str): The path to save the .json file.
        """
        data_to_write = None
        if isinstance(cf_object, (CFGraph, CFDivisor, CFOrientation, CFiringScript)):
            data_to_write = cf_object.to_dict()
        else:
            raise ValueError(f"Unsupported object type for JSON serialization: {type(cf_object)}")

        if data_to_write is not None:
            try:
                with open(file_path, 'w') as f:
                    json.dump(data_to_write, f, indent=4)
                print(f"Successfully wrote object to {file_path}.")
            except Exception as e:
                print(f"An error occurred while writing JSON to {file_path}: {e}")
        else:
            print(f"No data to write for object of type {type(cf_object)}.")

    # --- TXT Methods ---
    def read_txt(self, file_path: str, object_type: str):
        """
        Reads a CF object from a .txt file.

        Args:
            file_path (str): The path to the .txt file.
            object_type (str): The type of CF object to read.

        Returns:
            A CF object or None if reading fails.
        """
        try:
            with open(file_path, 'r') as f:
                lines = [line.strip() for line in f if line.strip()] # Read non-empty lines

            if object_type.lower() == 'graph':
                vertex_names = []
                edges = []
                for line in lines:
                    if line.startswith("VERTICES:"):
                        vertex_names = [name.strip() for name in line.replace("VERTICES:", "").split(',')]
                    elif line.startswith("EDGE:"):
                        parts = [part.strip() for part in line.replace("EDGE:", "").split(',')]
                        if len(parts) == 3:
                            edges.append((parts[0], parts[1], int(parts[2])))
                        else:
                            print(f"Warning: Malformed EDGE line: {line}")
                if not vertex_names:
                    raise ValueError("VERTICES line missing or empty in TXT file for graph.")
                return CFGraph(set(vertex_names), edges)
            
            elif object_type.lower() == 'divisor':
                graph_vertex_names = []
                graph_edges = []
                divisor_degrees_list = []
                parsing_degrees = False

                for line in lines:
                    if line.startswith("GRAPH_VERTICES:"):
                        graph_vertex_names = [name.strip() for name in line.replace("GRAPH_VERTICES:", "").split(',')]
                    elif line.startswith("GRAPH_EDGE:"):
                        parts = [part.strip() for part in line.replace("GRAPH_EDGE:", "").split(',')]
                        if len(parts) == 3:
                            graph_edges.append((parts[0], parts[1], int(parts[2])))
                        else:
                            print(f"Warning: Malformed GRAPH_EDGE line: {line}")
                    elif line == "---DEGREES---":
                        parsing_degrees = True
                    elif line.startswith("DEGREE:") and parsing_degrees:
                        parts = [part.strip() for part in line.replace("DEGREE:", "").split(',')]
                        if len(parts) == 2:
                            divisor_degrees_list.append((parts[0], int(parts[1])))
                        else:
                            print(f"Warning: Malformed DEGREE line: {line}")
                
                if not graph_vertex_names:
                    raise ValueError("GRAPH_VERTICES line missing or empty in TXT file for divisor.")
                
                graph = CFGraph(set(graph_vertex_names), graph_edges)
                # For CFDivisor constructor, all graph vertices will default to degree 0 
                # if not specified in divisor_degrees_list.
                return CFDivisor(graph, divisor_degrees_list)

            elif object_type.lower() == 'orientation':
                graph_vertex_names = []
                graph_edges = []
                orientations_list = []
                parsing_orientations = False
                for line in lines:
                    if line.startswith("GRAPH_VERTICES:"):
                        graph_vertex_names = [name.strip() for name in line.replace("GRAPH_VERTICES:", "").split(',')]
                    elif line.startswith("GRAPH_EDGE:"):
                        parts = [part.strip() for part in line.replace("GRAPH_EDGE:", "").split(',')]
                        if len(parts) == 3: 
                            graph_edges.append((parts[0], parts[1], int(parts[2])))
                        else: 
                            print(f"Warning: Malformed GRAPH_EDGE line: {line}")
                    elif line == "---ORIENTATIONS---":
                        parsing_orientations = True
                    elif line.startswith("ORIENTED:") and parsing_orientations:
                        parts = [part.strip() for part in line.replace("ORIENTED:", "").split(',')]
                        if len(parts) == 2: 
                            orientations_list.append((parts[0], parts[1]))
                        else: 
                            print(f"Warning: Malformed ORIENTED line: {line}")
                if not graph_vertex_names: 
                    raise ValueError("GRAPH_VERTICES missing for orientation.")
                graph = CFGraph(set(graph_vertex_names), graph_edges)
                return CFOrientation(graph, orientations_list)

            elif object_type.lower() == 'firingscript':
                graph_vertex_names = []
                graph_edges = []
                script_dict = {}
                parsing_script = False
                for line in lines:
                    if line.startswith("GRAPH_VERTICES:"):
                        graph_vertex_names = [name.strip() for name in line.replace("GRAPH_VERTICES:", "").split(',')]
                    elif line.startswith("GRAPH_EDGE:"):
                        parts = [part.strip() for part in line.replace("GRAPH_EDGE:", "").split(',')]
                        if len(parts) == 3: 
                            graph_edges.append((parts[0], parts[1], int(parts[2])))
                        else: 
                            print(f"Warning: Malformed GRAPH_EDGE line: {line}")
                    elif line == "---SCRIPT---":
                        parsing_script = True
                    elif line.startswith("FIRING:") and parsing_script:
                        parts = [part.strip() for part in line.replace("FIRING:", "").split(',')]
                        if len(parts) == 2: 
                            script_dict[parts[0]] = int(parts[1])
                        else: 
                            print(f"Warning: Malformed FIRING line: {line}")
                if not graph_vertex_names: 
                    raise ValueError("GRAPH_VERTICES missing for firingscript.")
                graph = CFGraph(set(graph_vertex_names), graph_edges)
                return CFiringScript(graph, script_dict)
            else:
                print(f"Unsupported object_type for TXT reading: {object_type}")
                return None

        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return None
        except ValueError as ve:
            print(f"Error processing TXT data for {object_type}: {ve}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while reading TXT from {file_path}: {e}")
            return None

    def to_txt(self, cf_object, file_path: str):
        """
        Writes a CF object to a .txt file.

        Args:
            cf_object: The CF object to serialize.
            file_path (str): The path to save the .txt file.
        """
        try:
            lines_to_write = []
            if isinstance(cf_object, CFGraph):
                vertex_names = sorted([v.name for v in cf_object.vertices])
                lines_to_write.append(f"VERTICES: {', '.join(vertex_names)}")
                
                # Use to_dict to get canonical edge list
                graph_dict = cf_object.to_dict()
                for edge_data in sorted(graph_dict.get("edges", [])):
                    lines_to_write.append(f"EDGE: {edge_data[0]}, {edge_data[1]}, {edge_data[2]}")
            
            elif isinstance(cf_object, CFDivisor):
                graph = cf_object.graph
                graph_vertex_names = sorted([v.name for v in graph.vertices])
                lines_to_write.append(f"GRAPH_VERTICES: {', '.join(graph_vertex_names)}")

                graph_dict = graph.to_dict()
                for edge_data in sorted(graph_dict.get("edges", [])):
                    lines_to_write.append(f"GRAPH_EDGE: {edge_data[0]}, {edge_data[1]}, {edge_data[2]}")
                
                lines_to_write.append("---DEGREES---")
                # Sort degrees by vertex name for consistent output
                sorted_degrees = sorted(cf_object.degrees.items(), key=lambda item: item[0].name)
                for vertex, degree in sorted_degrees:
                    lines_to_write.append(f"DEGREE: {vertex.name}, {degree}")

            elif isinstance(cf_object, CFOrientation):
                graph = cf_object.graph
                graph_vertex_names = sorted([v.name for v in graph.vertices])
                lines_to_write.append(f"GRAPH_VERTICES: {', '.join(graph_vertex_names)}")
                graph_dict = graph.to_dict()
                for edge_data in sorted(graph_dict.get("edges", [])):
                    lines_to_write.append(f"GRAPH_EDGE: {edge_data[0]}, {edge_data[1]}, {edge_data[2]}")
                lines_to_write.append("---ORIENTATIONS---")
                # Use CFOrientation's to_dict to get canonical orientations
                orientation_data = cf_object.to_dict().get("orientations", [])
                for source, sink in sorted(orientation_data):
                    lines_to_write.append(f"ORIENTED: {source}, {sink}")

            elif isinstance(cf_object, CFiringScript):
                graph = cf_object.graph
                graph_vertex_names = sorted([v.name for v in graph.vertices])
                lines_to_write.append(f"GRAPH_VERTICES: {', '.join(graph_vertex_names)}")
                graph_dict = graph.to_dict()
                for edge_data in sorted(graph_dict.get("edges", [])):
                    lines_to_write.append(f"GRAPH_EDGE: {edge_data[0]}, {edge_data[1]}, {edge_data[2]}")
                lines_to_write.append("---SCRIPT---")
                # Get script data (name: firings), sort by name for consistency
                script_data = cf_object.script # .script property gives all vertices
                sorted_script_items = sorted(script_data.items())
                for vertex_name, firings in sorted_script_items:
                    if firings != 0: # Only write non-zero firings for brevity
                        lines_to_write.append(f"FIRING: {vertex_name}, {firings}")
            else:
                print(f"Unsupported object type for TXT serialization: {type(cf_object)}")
                lines_to_write.append(f"Object type: {type(cf_object)}")
                lines_to_write.append("Data: TXT representation not implemented for this type.")

            with open(file_path, 'w') as f:
                for line in lines_to_write:
                    f.write(line + "\n")
            print(f"Successfully wrote object to {file_path}.")
            
        except Exception as e:
            print(f"An error occurred while writing TXT to {file_path}: {e}")

    # --- TeX Methods ---
    def to_tex(self, cf_object, file_path: str):
        """
        Writes a CF object to a .tex file using basic TikZ representation.

        Args:
            cf_object: The CF object to serialize (CFGraph or CFDivisor).
            file_path (str): The path to save the .tex file.
        """
        _tikz_node_positions = {} # To store node names for edges e.g. (A) -> tikz_id

        def _get_tikz_node_label(vertex_name, obj_type, obj_instance):
            label = vertex_name.replace("_", "\\_")
            if obj_type == 'divisor':
                # Don't include degree in the node label
                label = label
            elif obj_type == 'firingscript':
                # Don't include firing info in the node label
                label = label
            return label

        def _generate_tikz_nodes(vertices_list, obj_type, obj_instance):
            tex_node_lines = []
            if not vertices_list:
                return tex_node_lines
            
            # Basic positioning
            # First node
            v_obj_first = vertices_list[0]
            node_tikz_id = v_obj_first.name.replace("_", "") # TikZ node IDs can't have underscores usually
            _tikz_node_positions[v_obj_first.name] = node_tikz_id
            
            label = _get_tikz_node_label(v_obj_first.name, obj_type, obj_instance)
            tex_node_lines.append(f"    \\node[state] ({node_tikz_id}) {{{label}}};")
            
            prev_node_tikz_id = node_tikz_id
            
            # Subsequent nodes
            for i, v_obj in enumerate(vertices_list[1:]):
                current_real_idx = i + 1 # original index in vertices_list for positioning logic
                node_tikz_id = v_obj.name.replace("_", "")
                _tikz_node_positions[v_obj.name] = node_tikz_id
                
                label = _get_tikz_node_label(v_obj.name, obj_type, obj_instance)
                
                pos_str = "right=of " + prev_node_tikz_id
                # Rudimentary grid: find the anchor node for 'below of'
                # This assumes vertices_list is sorted consistently.
                if current_real_idx % 3 == 1: # New row
                    anchor_idx = current_real_idx - (current_real_idx % 3) -1 
                    if current_real_idx == 1: 
                        anchor_idx = 0 # first in second row
                    else: 
                        anchor_idx = current_real_idx - 1 - ( (current_real_idx-1) %3)


                    anchor_node_name_orig = vertices_list[anchor_idx].name
                    anchor_node_tikz_id = _tikz_node_positions[anchor_node_name_orig]
                    pos_str = "below=of " + anchor_node_tikz_id
                elif current_real_idx % 3 == 2: # Third in row
                    # prev_node_tikz_id is already correct from previous iteration
                    pos_str = "right=of " + prev_node_tikz_id
                # else: pos_str is "right=of " prev_node_tikz_id (default, for first and second in row)

                tex_node_lines.append(f"    \\node[state] ({node_tikz_id}) [{pos_str}] {{{label}}};")
                prev_node_tikz_id = node_tikz_id
            return tex_node_lines

        tex_lines = [
            "\\documentclass{article}",
            "\\usepackage{tikz}",
            "\\usetikzlibrary{automata, positioning, arrows.meta, shapes}",
            "",
            "\\begin{document}",
            "",
            "\\begin{tikzpicture}[shorten >=1pt, node distance=2.5cm, on grid, auto,",
            "    every state/.style={draw=black!50, thick, minimum size=0.8cm, inner sep=3pt},",
            "    edge_label/.style={midway, fill=white, inner sep=1pt, font=\\small}",
            "]",
            ""
        ]
        _tikz_node_positions.clear() # Clear for current object

        try:
            obj_specific_type_str = None # For _get_tikz_node_label

            if isinstance(cf_object, CFGraph):
                obj_specific_type_str = 'graph'
                tex_lines.append("% Graph Definition")
                # Vertices must be Vertex objects for CFGraph
                vertices_for_layout = sorted(list(cf_object.vertices), key=lambda v: v.name)
                tex_lines.extend(_generate_tikz_nodes(vertices_for_layout, obj_specific_type_str, cf_object))
                
                tex_lines.append("")
                tex_lines.append("% Edges")
                graph_dict = cf_object.to_dict() 
                for v1_name, v2_name, valence in sorted(graph_dict.get("edges", [])):
                    u_node_id = _tikz_node_positions.get(v1_name)
                    v_node_id = _tikz_node_positions.get(v2_name)
                    if u_node_id and v_node_id:
                         # Draw multiple edges based on valence
                        for i in range(valence):
                            if valence == 1:
                                bend = 0
                            else:
                                if i % 2 == 0:
                                    bend = 5
                                else:
                                    bend = -5
                            bend_magnitude = 5 * (i // 2)
                            bend = (bend + bend_magnitude) if bend > 0 else (bend - bend_magnitude)
                            if bend > 0:
                                tex_lines.append(f"    \\path[-] ({u_node_id}) edge[bend right={bend}] ({v_node_id});")
                            else:
                                tex_lines.append(f"    \\path[-] ({u_node_id}) edge[bend left={abs(bend)}] ({v_node_id});")

            elif isinstance(cf_object, CFDivisor):
                obj_specific_type_str = 'divisor'
                tex_lines.append("% Divisor Definition (Graph with Chip Counts)")
                graph = cf_object.graph
                vertices_for_layout = sorted(list(graph.vertices), key=lambda v: v.name)
                tex_lines.extend(_generate_tikz_nodes(vertices_for_layout, obj_specific_type_str, cf_object))
                
                # Add degree information as labels next to nodes
                tex_lines.append("")
                tex_lines.append("% Degree information as labels")
                for vertex in vertices_for_layout:
                    degree = cf_object.degrees.get(vertex, 0)
                    node_id = _tikz_node_positions.get(vertex.name)
                    tex_lines.append(f"    \\node[anchor=west, xshift=1pt, yshift=1pt, at=({node_id}.north east), font=\\small] {{{degree}}};")
                
                tex_lines.append("")
                tex_lines.append("% Edges")
                graph_dict = graph.to_dict()
                for v1_name, v2_name, valence in sorted(graph_dict.get("edges", [])):
                    u_node_id = _tikz_node_positions.get(v1_name)
                    v_node_id = _tikz_node_positions.get(v2_name)
                    if u_node_id and v_node_id:
                        # Draw multiple edges based on valence
                        for i in range(valence):
                            if valence == 1:
                                bend = 0
                            else:
                                if i % 2 == 0:
                                    bend = 5
                                else:
                                    bend = -5
                            bend_magnitude = 5 * (i // 2)
                            bend = (bend + bend_magnitude) if bend > 0 else (bend - bend_magnitude)
                            if bend > 0:
                                tex_lines.append(f"    \\path[->] ({u_node_id}) edge[bend right={bend}] ({v_node_id});")
                            else:
                                tex_lines.append(f"    \\path[->] ({u_node_id}) edge[bend left={abs(bend)}] ({v_node_id});")

            elif isinstance(cf_object, CFOrientation):
                obj_specific_type_str = 'orientation'
                tex_lines.append("% Orientation Definition")
                graph = cf_object.graph
                vertices_for_layout = sorted(list(graph.vertices), key=lambda v: v.name)
                tex_lines.extend(_generate_tikz_nodes(vertices_for_layout, obj_specific_type_str, cf_object))

                tex_lines.append("")
                tex_lines.append("% Edges with Orientations")
                graph_edges_dict = { tuple(sorted((e[0],e[1]))): e[2] for e in graph.to_dict().get("edges", []) }
                # Get orientations from the object: list of [source, sink]
                oriented_pairs_set = { tuple(o) for o in cf_object.to_dict().get("orientations", []) }

                for v1_s_name, v2_s_name in sorted(graph_edges_dict.keys()): # Iterate unique graph edges
                    valence = graph_edges_dict[(v1_s_name, v2_s_name)]
                    u_node_id = _tikz_node_positions.get(v1_s_name)
                    v_node_id = _tikz_node_positions.get(v2_s_name)

                    if not (u_node_id and v_node_id): 
                        continue

                    # Determine arrow style based on orientation
                    if (v1_s_name, v2_s_name) in oriented_pairs_set: # v1 -> v2
                        # Draw multiple directed edges
                        for i in range(valence):
                            if valence == 1:
                                bend = 0
                            else:
                                if i % 2 == 0:
                                    bend = 5
                                else:
                                    bend = -5
                            bend_magnitude = 5 * (i // 2)
                            bend = (bend + bend_magnitude) if bend > 0 else (bend - bend_magnitude)
                            if bend > 0:
                                tex_lines.append(f"    \\path[->] ({u_node_id}) edge[bend right={bend}] ({v_node_id});")
                            else:
                                tex_lines.append(f"    \\path[->] ({u_node_id}) edge[bend left={abs(bend)}] ({v_node_id});")
                    elif (v2_s_name, v1_s_name) in oriented_pairs_set: # v2 -> v1
                        # Draw multiple directed edges in reverse
                        for i in range(valence):
                            if valence == 1:
                                bend = 0
                            else:
                                if i % 2 == 0:
                                    bend = 5
                                else:
                                    bend = -5 
                            bend_magnitude = 5 * (i // 2)
                            bend = (bend + bend_magnitude) if bend > 0 else (bend - bend_magnitude)
                            if bend > 0:
                                tex_lines.append(f"    \\path[->] ({v_node_id}) edge[bend right={bend}] ({u_node_id});")
                            else:
                                tex_lines.append(f"    \\path[->] ({v_node_id}) edge[bend left={abs(bend)}] ({u_node_id});")
                    else: # Not in orientation list, draw as undirected or per specific style
                        # Draw multiple undirected edges
                        for i in range(valence):
                            if valence == 1:
                                bend = 0
                            else:
                                if i % 2:
                                    bend = 5
                                else:
                                    bend = -5
                            
                            bend_magnitude = 5 * (i // 2)
                            bend = (bend + bend_magnitude) if bend > 0 else (bend - bend_magnitude)
                            if bend > 0:
                                tex_lines.append(f"    \\path[-] ({u_node_id}) edge[bend right={bend}] ({v_node_id});")
                            else:
                                tex_lines.append(f"    \\path[-] ({u_node_id}) edge[bend left={abs(bend)}] ({v_node_id});")


            elif isinstance(cf_object, CFiringScript):
                obj_specific_type_str = 'firingscript'
                tex_lines.append("% Firing Script Definition")
                graph = cf_object.graph
                vertices_for_layout = sorted(list(graph.vertices), key=lambda v: v.name)
                tex_lines.extend(_generate_tikz_nodes(vertices_for_layout, obj_specific_type_str, cf_object))
                
                # Add firing information as labels next to nodes
                tex_lines.append("")
                tex_lines.append("% Firing information as labels")
                for vertex in vertices_for_layout:
                    firings = cf_object.script.get(vertex.name, 0)
                    if firings != 0:  # Only show non-zero firing counts
                        node_id = _tikz_node_positions.get(vertex.name)
                        tex_lines.append(f"    \\node[anchor=west, xshift=1pt, yshift=1pt, at=({node_id}.north east), font=\\small] {{{firings}}};")
                
                tex_lines.append("")
                tex_lines.append("% Edges (structure only, firings are shown next to nodes)")
                graph_dict = graph.to_dict()
                for v1_name, v2_name, valence in sorted(graph_dict.get("edges", [])):
                    u_node_id = _tikz_node_positions.get(v1_name)
                    v_node_id = _tikz_node_positions.get(v2_name)
                    if u_node_id and v_node_id:
                        # Draw multiple edges based on valence
                        for i in range(valence):
                            if valence == 1:
                                bend = 0
                            else:
                                if i % 2 == 0:
                                    bend = 5
                                else:
                                    bend = -5
                            bend_magnitude = 5 * (i // 2)
                            bend = (bend + bend_magnitude) if bend > 0 else (bend - bend_magnitude)
                            if bend > 0:
                                tex_lines.append(f"    \\path[-] ({u_node_id}) edge[bend right={bend}] ({v_node_id});")
                            else:
                                tex_lines.append(f"    \\path[-] ({u_node_id}) edge[bend left={abs(bend)}] ({v_node_id});")
            else:
                print(f"Unsupported object type for TeX serialization: {type(cf_object)}")
                tex_lines.append(f"% Object type: {type(cf_object)}")
                tex_lines.append("% Data: TeX representation not implemented for this type.")

            tex_lines.extend([
                "",
                "\\end{tikzpicture}",
                "",
                "\\end{document}"
            ])

            with open(file_path, 'w') as f:
                for line in tex_lines:
                    f.write(line + "\n")
            print(f"Successfully wrote TeX representation to {file_path}.")

        except Exception as e:
            print(f"An error occurred while writing TeX to {file_path}: {e}")
            raise e
        
if __name__ == "__main__":

   processor = CFDataProcessor()

   graph = processor.read_txt("tests/data/txt/favorite_graph.txt", "graph")
   processor.to_tex(graph, "tests/data/tex/favorite_graph.tex")

   divisor = processor.read_txt("tests/data/txt/favorite_divisor.txt", "divisor")
   processor.to_tex(divisor, "tests/data/tex/favorite_divisor.tex")

   orientation = processor.read_txt("tests/data/txt/favorite_orientation.txt", "orientation")
   processor.to_tex(orientation, "tests/data/tex/favorite_orientation.tex")

   firingscript = processor.read_txt("tests/data/txt/favorite_firing_script.txt", "firingscript")
   processor.to_tex(firingscript, "tests/data/tex/favorite_firing_script.tex")
