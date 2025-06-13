import unittest
from unittest.mock import patch, MagicMock
from chipfiring.CFGraph import CFGraph
from chipfiring.CFDivisor import CFDivisor
from chipfiring.CFOrientation import CFOrientation
from chipfiring.CFEWDVisualizer import EWDVisualizer

class TestEWDVisualizer(unittest.TestCase):

    def setUp(self):
        self.vertices = {"A", "B", "C"}
        self.edges = [("A", "B", 1), ("B", "C", 1)]
        self.graph = CFGraph(self.vertices, self.edges)
        
        self.degrees = [("A", 1), ("B", -1), ("C", 0)]
        self.divisor = CFDivisor(self.graph, self.degrees)
        
        self.orientations = [("A", "B")]
        self.orientation = CFOrientation(self.graph, self.orientations)
        
        self.visualizer = EWDVisualizer()

    def test_init(self):
        self.assertEqual(self.visualizer.history, [])

    def test_add_step(self):
        self.visualizer.add_step(
            divisor=self.divisor,
            orientation=self.orientation,
            unburnt_vertices={"A", "C"},
            firing_set={"B"},
            q="C",
            description="Test step",
            source_function="test_function"
        )
        self.assertEqual(len(self.visualizer.history), 1)
        step = self.visualizer.history[0]
        self.assertIsNot(step["divisor"], self.divisor)  # Check for deep copy
        self.assertIsNot(step["orientation"], self.orientation)  # Check for deep copy
        self.assertEqual(step["divisor"].to_dict(), self.divisor.to_dict())
        self.assertEqual(step["orientation"].to_dict(), self.orientation.to_dict())
        self.assertEqual(step["unburnt_vertices"], {"A", "C"})
        self.assertEqual(step["firing_set"], {"B"})
        self.assertEqual(step["q"], "C")
        self.assertEqual(step["description"], "Test step")
        self.assertEqual(step["source_function"], "test_function")

    def test_get_elements(self):
        unburnt = {"A", "C"}
        firing = {self.graph.get_vertex_by_name("B")}
        q_node = "C"

        elements = self.visualizer._get_elements(self.divisor, self.orientation, unburnt, firing, q_node)

        nodes = [e for e in elements if 'source' not in e.get('data', {})]
        edges = [e for e in elements if 'source' in e.get('data', {})]

        self.assertEqual(len(nodes), 3)
        self.assertEqual(len(edges), 2)

        node_a_data = next(e['data'] for e in nodes if e['data']['id'] == 'A')
        node_b_data = next(e['data'] for e in nodes if e['data']['id'] == 'B')
        node_c_data = next(e['data'] for e in nodes if e['data']['id'] == 'C')

        # Test divisor info and labels
        self.assertEqual(node_a_data['label'], "A\n1")
        self.assertEqual(node_a_data['divisor_sign'], 'non-negative')
        self.assertEqual(node_b_data['label'], "B\n-1")
        self.assertEqual(node_b_data['divisor_sign'], 'negative')
        self.assertEqual(node_c_data['label'], "C\n0")
        self.assertEqual(node_c_data['divisor_sign'], 'non-negative')

        # Test firing set
        self.assertEqual(node_a_data['is_in_firing_set'], 'false')
        self.assertEqual(node_b_data['is_in_firing_set'], 'true')
        self.assertEqual(node_c_data['is_in_firing_set'], 'false')

        # Test q
        self.assertEqual(node_a_data['is_q'], 'false')
        self.assertEqual(node_b_data['is_q'], 'false')
        self.assertEqual(node_c_data['is_q'], 'true')

        # Test burnt status
        # Unburnt set is {"A", "C"}, so B is burnt
        self.assertEqual(node_a_data['is_burnt'], 'false')
        self.assertEqual(node_b_data['is_burnt'], 'true')
        self.assertEqual(node_c_data['is_burnt'], 'false')

        # Test edge orientation
        edge_ab = next(e['data'] for e in edges if e['data']['id'] == 'A-B-0')
        edge_bc = next(e['data'] for e in edges if e['data']['id'] == 'B-C-0')
        
        # A -> B is oriented
        self.assertEqual(edge_ab['oriented'], True)
        self.assertEqual(edge_ab['source'], 'A')
        self.assertEqual(edge_ab['target'], 'B')
        self.assertEqual(edge_ab['arrow_shape'], 'triangle')

        # B - C is not oriented
        self.assertEqual(edge_bc['oriented'], False)
        # source/target can be either way for unoriented
        self.assertIn(edge_bc['source'], ['B', 'C'])
        self.assertIn(edge_bc['target'], ['B', 'C'])
        self.assertEqual(edge_bc['arrow_shape'], 'none')

    @patch('builtins.print')
    def test_visualize_no_history(self, mock_print):
        self.visualizer.visualize()
        mock_print.assert_called_once_with("No history to visualize.")

    @patch('chipfiring.CFEWDVisualizer.Dash')
    def test_visualize_with_history(self, mock_dash):
        # Mock the Dash app instance and its run method
        mock_app_instance = MagicMock()
        mock_dash.return_value = mock_app_instance

        # Add a step to history so visualize() doesn't just print
        self.visualizer.add_step(self.divisor, self.orientation)
        
        self.visualizer.visualize()

        # Check that Dash was initialized
        mock_dash.assert_called_once()
        # Check that the app's run method was called
        mock_app_instance.run.assert_called_once_with(debug=True)


if __name__ == '__main__':
    unittest.main() 