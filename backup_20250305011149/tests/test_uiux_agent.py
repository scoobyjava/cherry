import unittest
from src.agents.uiux_agent import UIUXAgent

class TestUIUXAgent(unittest.TestCase):
    def setUp(self):
        self.agent = UIUXAgent()
        
    def test_generate_wireframe_basic(self):
        design_requirements = {
            "color_scheme": "blue",
            "layout": "standard",
            "priority_content": ["hero", "features"],
            "target_devices": ["desktop", "mobile"]
        }
        
        wireframe = self.agent.generate_wireframe(design_requirements)
        
        # Check structure of returned wireframe
        self.assertIsInstance(wireframe, dict)
        self.assertIn("metadata", wireframe)
        self.assertIn("layout", wireframe)
        self.assertIn("components", wireframe)
        self.assertIn("accessibility", wireframe)
        self.assertIn("responsive_behavior", wireframe)
        
        # Check that metadata contains expected fields
        self.assertEqual(wireframe["metadata"]["component_type"], "page")
        self.assertEqual(wireframe["metadata"]["color_scheme"], "blue")
        
        # Check that responsive behavior includes specified target devices
        self.assertIn("mobile", wireframe["responsive_behavior"]["breakpoints"])
        self.assertIn("desktop", wireframe["responsive_behavior"]["breakpoints"])
        self.assertNotIn("tablet", wireframe["responsive_behavior"]["breakpoints"])
        
    def test_generate_wireframe_with_custom_component(self):
        design_requirements = {
            "color_scheme": "green",
            "layout": "landing",
            "priority_content": ["hero", "form"],
            "target_devices": ["mobile", "tablet", "desktop"],
            "components": ["header", "footer"]
        }
        
        wireframe = self.agent.generate_wireframe(
            design_requirements,
            component_type="section",
            include_accessibility=True
        )
        
        # Check that component type is set correctly
        self.assertEqual(wireframe["metadata"]["component_type"], "section")
        
        # Check that priority content is included
        component_types = [comp.get("type") for comp in wireframe["components"]]
        self.assertIn("header", component_types)
        self.assertIn("section", component_types)  # For hero and form
        
        # Check accessibility recommendations are included
        self.assertIn("recommendations", wireframe["accessibility"])
        self.assertGreater(len(wireframe["accessibility"]["recommendations"]), 0)

if __name__ == '__main__':
    unittest.main()
