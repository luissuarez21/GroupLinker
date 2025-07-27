# GroupLinker 🤝

AI-powered group scheduling app built with FastAPI. Like When2Meet, but smarter.

## Features
- Create separate groups for different events
- Add availability for each group member  
- AI-powered scheduling suggestions
- Data persistence across sessions
- RESTful API with automatic documentation

## Tech Stack
- **Backend:** Python, FastAPI
- **Algorithms:** Set intersection for availability overlap
- **Storage:** JSON file persistence
- **API:** RESTful design with OpenAPI docs

## Try It
1. `pip install -r requirements.txt`
2. `uvicorn main:app --reload`
3. Visit `http://localhost:8000/docs`

## Next Steps
- [ ] Frontend web interface
- [ ] AI integration with OpenAI
- [ ] Deployment to production