import pytest
import asyncio
from unittest.mock import patch, MagicMock
import json

from agents.uiux_agent import UIUXAgent

@pytest.fixture
def uiux_agent():
    """Create a UIUXAgent instance for testing."""
    agent = UIUXAgent(agent_id="test-uiux-agent", config={
        "model": "test-model",
        "wireframe_style": "minimal"
    })
    return agent

class TestUIUXAgent:
    
    @pytest.mark.asyncio
    async def test_generate_ui_recommendations_typical(self, uiux_agent):
        """Test generate_ui_recommendations with typical input."""
        requirements = {
            "type": "web",
            "target_audience": "general",
            "purpose": "e-commerce",
            "constraints": ["responsive", "accessibility"]
        }
        
        with patch.object(uiux_agent, '_generate_recommendations', 
                          return_value=["Use a clear navigation bar", "Implement responsive design"]):
            result = await uiux_agent.generate_ui_recommendations(requirements)
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert "Use a clear navigation bar" in result
            assert "Implement responsive design" in result
    
    @pytest.mark.asyncio
    async def test_generate_ui_recommendations_empty_input(self, uiux_agent):
        """Test generate_ui_recommendations with empty input."""
        requirements = {}
        
        with pytest.raises(ValueError, match="Invalid or incomplete requirements"):
            await uiux_agent.generate_ui_recommendations(requirements)
    
    @pytest.mark.asyncio
    async def test_generate_ui_recommendations_missing_fields(self, uiux_agent):
        """Test generate_ui_recommendations with missing required fields."""
        requirements = {
            "type": "web",
            # missing target_audience and purpose
            "constraints": ["responsive"]
        }
        
        with pytest.raises(ValueError, match="Invalid or incomplete requirements"):
            await uiux_agent.generate_ui_recommendations(requirements)
    
    @pytest.mark.asyncio
    async def test_generate_wireframe_typical(self, uiux_agent):
        """Test generate_wireframe with typical input."""
        specifications = {
            "page_type": "landing",
            "components": ["header", "hero", "features", "footer"],
            "layout": "single-column"
        }
        
        expected_result = {
            "wireframe_data": "SVG or JSON representation of the wireframe",
            "elements": ["header", "hero", "features", "footer"],
            "notes": "Sample wireframe for landing page"
        }
        
        with patch.object(uiux_agent, '_create_wireframe', return_value=expected_result):
            result = await uiux_agent.generate_wireframe(specifications)
            
            assert isinstance(result, dict)
            assert "wireframe_data" in result
            assert "elements" in result
            assert "notes" in result
            assert result["elements"] == ["header", "hero", "features", "footer"]
    
    @pytest.mark.asyncio
    async def test_generate_wireframe_invalid_input(self, uiux_agent):
        """Test generate_wireframe with invalid input."""
        specifications = {
            # Missing required fields
            "layout": "single-column"
        }
        
        with pytest.raises(ValueError, match="Invalid or incomplete specifications"):
            await uiux_agent.generate_wireframe(specifications)
    
    @pytest.mark.asyncio
    async def test_generate_wireframe_unsupported_page_type(self, uiux_agent):
        """Test generate_wireframe with unsupported page type."""
        specifications = {
            "page_type": "unsupported_type",
            "components": ["header", "footer"],
            "layout": "single-column"
        }
        
        # Mock the _create_wireframe method to simulate an error for unsupported page type
        with patch.object(uiux_agent, '_create_wireframe', side_effect=ValueError("Unsupported page type")):
            with pytest.raises(ValueError, match="Unsupported page type"):
                await uiux_agent.generate_wireframe(specifications)
    
    @pytest.mark.asyncio
    async def test_review_existing_design_typical(self, uiux_agent):
        """Test review_existing_design with typical input."""
        design_data = {
            "design_type": "website",
            "screenshots": ["base64_encoded_image_1", "base64_encoded_image_2"],
            "current_issues": ["navigation unclear", "poor mobile experience"]
        }
        
        expected_review = {
            "strengths": ["Clean layout", "Good color scheme"],
            "weaknesses": ["Navigation issues", "Poor responsive behavior"],
            "recommendations": ["Simplify navigation", "Enhance mobile layout"],
            "priority_fixes": ["Fix navigation", "Improve responsiveness"]
        }
        
        with patch.object(uiux_agent, '_analyze_design', return_value=expected_review):
            result = await uiux_agent.review_existing_design(design_data)
            
            assert isinstance(result, dict)
            assert "strengths" in result
            assert "weaknesses" in result
            assert "recommendations" in result
            assert "priority_fixes" in result
            assert len(result["recommendations"]) > 0
            assert len(result["priority_fixes"]) > 0
    
    @pytest.mark.asyncio
    async def test_review_existing_design_empty_input(self, uiux_agent):
        """Test review_existing_design with empty input."""
        design_data = {}
        
        with pytest.raises(ValueError, match="Invalid or incomplete design data"):
            await uiux_agent.review_existing_design(design_data)
    
    @pytest.mark.asyncio
    async def test_review_existing_design_missing_screenshots(self, uiux_agent):
        """Test review_existing_design with missing screenshots."""
        design_data = {
            "design_type": "website",
            # Missing screenshots
            "current_issues": ["navigation unclear"]
        }
        
        with pytest.raises(ValueError, match="Design data must include screenshots"):
            await uiux_agent.review_existing_design(design_data)
    
    @pytest.mark.asyncio
    async def test_review_existing_design_unsupported_type(self, uiux_agent):
        """Test review_existing_design with unsupported design type."""
        design_data = {
            "design_type": "unsupported_type",
            "screenshots": ["base64_encoded_image"],
            "current_issues": ["navigation unclear"]
        }
        
        # Mock to simulate an error for unsupported design type
        with patch.object(uiux_agent, '_analyze_design', side_effect=ValueError("Unsupported design type")):
            with pytest.raises(ValueError, match="Unsupported design type"):
                await uiux_agent.review_existing_design(design_data)
