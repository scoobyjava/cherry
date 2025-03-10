# Add more components to your website
scheduler.schedule_task({
    "type": "generate_code",
    "priority": 9,
    "data": {
        "project_name": "Cherry Website",
        "file_path": "frontend/components/Navigation.jsx",
        "language": "jsx",
        "requirements": "Create a responsive navigation bar with links to Home, Features, Pricing, and Contact pages"
    }
})

scheduler.schedule_task({
    "type": "generate_code",
    "priority": 8,
    "data": {
        "project_name": "Cherry Website",
        "file_path": "frontend/pages/Home.jsx",
        "language": "jsx",
        "requirements": "Create a landing page with hero section, feature highlights, and call-to-action buttons"
    }
})

# Add backend API endpoints
scheduler.schedule_task({
    "type": "generate_code",
    "priority": 7,
    "data": {
        "project_name": "Cherry Website",
        "file_path": "backend/api/user_routes.js",
        "language": "javascript",
        "requirements": "Create Express.js API routes for user authentication including login, registration, and profile management"
    }
})
