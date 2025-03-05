/**
 * Design System Configuration
 * This file contains the core design preferences and settings
 * for maintaining consistent UI/UX across the project.
 */

const designConfig = {
  // Primary framework used across the project
  framework: "Tailwind CSS",
  
  // Core design principles that guide all UI decisions
  designPrinciples: [
    {
      name: "Minimalism",
      description: "Focus on essential elements, remove clutter, use whitespace effectively",
      guidelines: [
        "Limit UI elements to what's necessary",
        "Embrace whitespace",
        "Use subtle shadows and depth cues sparingly"
      ]
    },
    {
      name: "Clean Design",
      description: "Clear visual hierarchy, consistent components, intuitive interactions",
      guidelines: [
        "Maintain consistent spacing and alignment",
        "Use a limited color palette",
        "Design clear interactive states"
      ]
    },
    {
      name: "Accessibility",
      description: "Ensure the interface is usable by people with diverse abilities",
      guidelines: [
        "Maintain WCAG 2.1 AA compliance minimum",
        "Support keyboard navigation",
        "Test with screen readers",
        "Ensure sufficient color contrast (4.5:1 minimum)"
      ]
    },
    {
      name: "Responsive",
      description: "Adapt gracefully across device sizes and orientations",
      guidelines: [
        "Mobile-first approach",
        "Use fluid layouts and flexible components",
        "Test across breakpoints",
        "Consider touch targets on mobile (min 44px)"
      ]
    }
  ],
  
  // Target platforms with specific optimizations
  platforms: {
    web: {
      breakpoints: {
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
        "2xl": "1536px"
      },
      containerMaxWidths: {
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
        "2xl": "1536px"
      }
    },
    mobile: {
      touchTargetSize: "44px",
      safePadding: {
        top: "env(safe-area-inset-top)",
        right: "env(safe-area-inset-right)",
        bottom: "env(safe-area-inset-bottom)",
        left: "env(safe-area-inset-left)"
      },
      viewportAdjustment: "viewport-fit=cover"
    }
  },
  
  // Color system - using