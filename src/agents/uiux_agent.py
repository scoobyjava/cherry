import json
from typing import Dict, List, Any, Optional
import logging

class UIUXAgent:
    """
    Agent responsible for generating UI/UX wireframes with Tailwind CSS
    and providing design recommendations based on best practices.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the UIUXAgent with configuration options.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
    def generate_wireframe(self, 
                          design_requirements: Dict[str, Any],
                          component_type: str = "page",
                          include_accessibility: bool = True) -> Dict[str, Any]:
        """
        Generate a structured JSON wireframe layout using Tailwind CSS classes
        based on provided design requirements.
        
        Args:
            design_requirements: Dictionary containing design specifications
            component_type: Type of component to generate (page, section, component)
            include_accessibility: Whether to include accessibility recommendations
            
        Returns:
            Dict containing structured wireframe with Tailwind CSS classes and metadata
        """
        self.logger.info(f"Generating {component_type} wireframe based on requirements")
        
        # Extract key design parameters
        color_scheme = design_requirements.get('color_scheme', 'neutral')
        layout_type = design_requirements.get('layout', 'standard')
        priority_content = design_requirements.get('priority_content', [])
        target_devices = design_requirements.get('target_devices', ['desktop', 'mobile', 'tablet'])
        
        # Define responsive breakpoints based on Tailwind defaults
        breakpoints = {
            'sm': '640px',   # Small screens (mobile)
            'md': '768px',   # Medium screens (tablet)
            'lg': '1024px',  # Large screens (laptop)
            'xl': '1280px',  # Extra large screens (desktop)
            '2xl': '1536px', # 2X large screens (large desktop)
        }
        
        # Generate base layout structure
        wireframe = {
            "metadata": {
                "component_type": component_type,
                "responsive_breakpoints": breakpoints,
                "color_scheme": color_scheme,
                "layout_type": layout_type,
                "generated_timestamp": "{{TIMESTAMP}}",  # Placeholder to be replaced at runtime
                "design_principles": {
                    "visual_hierarchy": "Applied emphasis to priority content",
                    "consistency": "Used consistent spacing and typography",
                    "simplicity": "Avoided unnecessary complexity",
                    "feedback": "Included interactive element states"
                }
            },
            "layout": self._generate_layout_structure(layout_type, component_type),
            "components": self._generate_components(design_requirements, priority_content)
        }
        
        # Add accessibility recommendations if requested
        if include_accessibility:
            wireframe["accessibility"] = self._generate_accessibility_recommendations(
                design_requirements, component_type
            )
        
        # Add responsive design guidelines
        wireframe["responsive_behavior"] = self._generate_responsive_behavior(
            target_devices, component_type, layout_type
        )
        
        return wireframe
    
    def _generate_layout_structure(self, layout_type: str, component_type: str) -> Dict[str, Any]:
        """Generate base layout structure with appropriate Tailwind classes"""
        base_layouts = {
            "standard": {
                "container": "container mx-auto px-4 py-8",
                "wrapper": "flex flex-col space-y-6"
            },
            "dashboard": {
                "container": "container mx-auto px-4 py-6",
                "wrapper": "grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4"
            },
            "landing": {
                "container": "w-full",
                "wrapper": "flex flex-col space-y-12"
            },
            "sidebar": {
                "container": "container mx-auto",
                "wrapper": "flex flex-col md:flex-row"
            }
        }
        
        layout = base_layouts.get(layout_type, base_layouts["standard"])
        
        # Add responsive and accessibility attributes
        layout["container_attrs"] = {
            "role": "main" if component_type == "page" else None,
            "aria-label": f"{layout_type} {component_type}"
        }
        
        return layout
    
    def _generate_components(self, 
                            design_requirements: Dict[str, Any], 
                            priority_content: List[str]) -> List[Dict[str, Any]]:
        """Generate component definitions with Tailwind classes"""
        components = []
        
        # Add header if needed
        if "header" in design_requirements.get('components', []) or component_type == "page":
            components.append({
                "type": "header",
                "tailwind_classes": "w-full py-4 bg-white dark:bg-gray-800 shadow",
                "children": [
                    {
                        "type": "nav",
                        "tailwind_classes": "container mx-auto flex items-center justify-between",
                        "accessibility": {
                            "role": "navigation",
                            "aria-label": "Main navigation"
                        }
                    }
                ]
            })
        
        # Generate content section components based on priority_content
        for content_type in priority_content:
            component = self._generate_content_component(content_type, design_requirements)
            if component:
                components.append(component)
                
        # Add footer for page types
        if "footer" in design_requirements.get('components', []) or component_type == "page":
            components.append({
                "type": "footer",
                "tailwind_classes": "w-full py-6 bg-gray-100 dark:bg-gray-900 mt-8",
                "children": [
                    {
                        "type": "div",
                        "tailwind_classes": "container mx-auto flex flex-col md:flex-row justify-between"
                    }
                ]
            })
            
        return components
    
    def _generate_content_component(self, 
                                   content_type: str, 
                                   design_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a specific content component based on type"""
        component_library = {
            "hero": {
                "type": "section",
                "tailwind_classes": "w-full py-12 md:py-24 bg-gradient-to-r from-blue-500 to-indigo-600 text-white",
                "children": [
                    {
                        "type": "div",
                        "tailwind_classes": "container mx-auto text-center px-4",
                        "children": [
                            {
                                "type": "h1",
                                "tailwind_classes": "text-4xl md:text-5xl lg:text-6xl font-bold mb-6"
                            },
                            {
                                "type": "p",
                                "tailwind_classes": "text-lg md:text-xl max-w-2xl mx-auto mb-8"
                            },
                            {
                                "type": "div",
                                "tailwind_classes": "flex flex-col sm:flex-row gap-4 justify-center",
                                "children": [
                                    {
                                        "type": "button",
                                        "tailwind_classes": "px-8 py-3 bg-white text-blue-600 font-medium rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-blue-600",
                                        "accessibility": {
                                            "role": "button"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "features": {
                "type": "section",
                "tailwind_classes": "py-12 md:py-16 bg-white dark:bg-gray-800",
                "children": [
                    {
                        "type": "div",
                        "tailwind_classes": "container mx-auto px-4",
                        "children": [
                            {
                                "type": "h2",
                                "tailwind_classes": "text-3xl md:text-4xl font-bold text-center mb-12"
                            },
                            {
                                "type": "div",
                                "tailwind_classes": "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
                            }
                        ]
                    }
                ]
            },
            "form": {
                "type": "section",
                "tailwind_classes": "py-8 md:py-12 bg-gray-50 dark:bg-gray-900",
                "children": [
                    {
                        "type": "div",
                        "tailwind_classes": "container mx-auto px-4 max-w-lg",
                        "children": [
                            {
                                "type": "form",
                                "tailwind_classes": "bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md",
                                "accessibility": {
                                    "role": "form",
                                    "aria-labelledby": "form-title"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        
        return component_library.get(content_type, {})
    
    def _generate_accessibility_recommendations(self, 
                                              design_requirements: Dict[str, Any],
                                              component_type: str) -> Dict[str, Any]:
        """Generate accessibility recommendations for the wireframe"""
        return {
            "recommendations": [
                "Ensure all interactive elements are keyboard navigable",
                "Maintain color contrast ratio of at least 4.5:1 for normal text",
                "Use semantic HTML elements to improve screen reader compatibility",
                "Include appropriate ARIA labels for non-standard interactions",
                "Ensure focus states are clearly visible for keyboard navigation"
            ],
            "color_contrast": {
                "normal_text": "4.5:1 minimum",
                "large_text": "3:1 minimum",
                "ui_components": "3:1 minimum"
            },
            "keyboard_focus_order": [
                "Header navigation",
                "Main content interactive elements",
                "Form fields (in logical sequence)",
                "Footer elements"
            ],
            "screen_reader": {
                "landmarks": [
                    "banner - for the header",
                    "navigation - for navigation menus",
                    "main - for main content",
                    "contentinfo - for the footer"
                ],
                "aria_attributes": [
                    "aria-label",
                    "aria-labelledby",
                    "aria-describedby",
                    "aria-expanded",
                    "aria-controls"
                ]
            }
        }
    
    def _generate_responsive_behavior(self, 
                                     target_devices: List[str],
                                     component_type: str,
                                     layout_type: str) -> Dict[str, Any]:
        """Generate responsive behavior guidelines based on target devices"""
        responsive_behavior = {
            "breakpoints": {
                "mobile": {
                    "max_width": "640px",
                    "layout_adjustments": [
                        "Stack elements vertically",
                        "Increase touch targets to min 44x44px",
                        "Hide non-essential elements",
                        "Use condensed navigation (hamburger menu)"
                    ]
                },
                "tablet": {
                    "min_width": "641px",
                    "max_width": "1024px",
                    "layout_adjustments": [
                        "2-column grid where appropriate",
                        "Show more navigation items than mobile",
                        "Optimize for both touch and cursor inputs"
                    ]
                },
                "desktop": {
                    "min_width": "1025px",
                    "layout_adjustments": [
                        "Multi-column layout",
                        "Show full navigation",
                        "Utilize hover states",
                        "More detailed information visible"
                    ]
                }
            },
            "tailwind_utilities": {
                "container_behavior": "container px-4 md:px-6 lg:px-8",
                "flex_direction": "flex flex-col md:flex-row",
                "text_sizing": "text-base md:text-lg lg:text-xl",
                "spacing": "p-4 md:p-6 lg:p-8",
                "grid_columns": "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
            },
            "priority_content": "Ensure critical content appears above the fold on all devices"
        }
        
        # Filter responsive behavior based on target devices
        filtered_breakpoints = {k: v for k, v in responsive_behavior["breakpoints"].items() 
                              if k in target_devices}
        responsive_behavior["breakpoints"] = filtered_breakpoints
        
        return responsive_behavior
