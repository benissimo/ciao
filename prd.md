# Product Requirements Document

## Project Name
<!-- Replace with your project name -->
Ciao

## Overview
<!-- Brief description of what you're building -->
A simple, mobile-friendly app which says "Hello" in a random language.

## Tech Stack
<!-- e.g., Next.js, TypeScript, Tailwind, PostgreSQL, etc. -->
Python

## Architecture
<!-- High-level architecture decisions -->
No DB, but use Python to render the HTML server-side.
Use uv for libs.

## Tasks

<!-- 
Each task should be:
- Atomic: one logical unit of work  
- Verifiable: clear success criteria
- Ordered: respect dependencies
- Categorized: setup, feature, integration, styling, testing

The Ralph loop picks the first task with "passes": false
-->

```json
[
  {
    "category": "setup",
    "description": "Initialize project with chosen tech stack",
    "steps": [
      "Create project scaffold",
      "Install dependencies",
      "Verify dev server starts"
    ],
    "passes": true
  },
  {
    "category": "feature",
    "description": "Implement core feature #1: each time the page loads, choose a random language in which to say hello",
    "steps": [
      "Create data models",
      "Build API endpoints",
      "Add basic UI"
    ],
    "passes": true
  },
  {
    "category": "feature",
    "description": "Implement core feature #2: use an in-memory session to keep track of the words shown to the user. Avoid repeating the same language for at least 5 visits",
    "steps": [
      "Define the feature scope",
      "Implement backend logic",
      "Wire up frontend"
    ],
    "passes": true
  },
  {
    "category": "testing",
    "description": "Add test coverage",
    "steps": [
      "Write unit tests for core logic",
      "Write integration tests for API",
      "Verify all tests pass"
    ],
    "passes": true
  },
  {
    "category": "styling",
    "description": "Polished UI and responsive design: for each language, use the colors of that country's flag and use an appropriate font and styling",
    "steps": [
      "Apply consistent styling",
      "Ensure mobile responsiveness",
      "Add loading states and error handling"
    ],
    "passes": false
  }
]
```

## Success Criteria
<!-- When is this project "done"? -->
- [ ] All tasks above pass
- [ ] Dev server runs without errors
- [ ] Core user flow works end-to-end
