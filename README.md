# Hamro Platform

**Full-stack application built with React, FastAPI, and MongoDB**

## 🏗️ Project Structure

```
hamro/
├── frontend/          # React frontend application
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── ...
│   ├── package.json
│   └── .env
├── backend/           # FastAPI backend application
│   ├── modules/
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── products.py   # Product management
│   │   └── ai.py         # AI services
│   ├── server.py
│   ├── requirements.txt
│   └── .env
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB instance (local or cloud)
- yarn package manager

### Environment Variables

#### Backend (.env in /backend folder)

```bash
MONGO_URL=mongodb://localhost:27017/
DB_NAME=hamro_db
```

#### Frontend (.env in /frontend folder)

```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port 8001 --reload
   ```

   The backend will be available at: `http://localhost:8001`
   API documentation: `http://localhost:8001/docs`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   yarn install
   ```

3. Run the development server:
   ```bash
   yarn start
   ```

   The frontend will be available at: `http://localhost:3000`

## 📡 API Endpoints

### Core
- `GET /api/` - Hello from Hamro endpoint
- `GET /api/health` - Health check

### Authentication Module
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

### Products Module
- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get single product
- `POST /api/products` - Create product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### AI Module
- `POST /api/ai/recommendations` - Get product recommendations
- `POST /api/ai/search` - AI-powered semantic search
- `POST /api/ai/sentiment` - Sentiment analysis
- `POST /api/ai/chat` - AI chatbot
- `POST /api/ai/price-prediction` - Price prediction

## 🧪 Testing the Connection

1. Start both backend and frontend servers
2. Open browser to `http://localhost:3000`
3. You should see "Hello from Hamro" message and connected modules
4. Check browser console for connection logs

## 📦 Technology Stack

### Frontend
- React 19
- React Router
- Axios for API calls
- Tailwind CSS
- Shadcn UI components

### Backend
- FastAPI (Python)
- Motor (Async MongoDB driver)
- Pydantic for data validation
- CORS middleware

### Database
- MongoDB

## 🔧 Development Notes

### Current Status
- ✅ Frontend and backend connected
- ✅ MongoDB integrated
- ✅ Placeholder modules created (auth, products, ai)
- ✅ API routing configured
- ⚠️ Authentication: Placeholder endpoints (no real JWT implementation yet)
- ⚠️ Products: Using mock data (needs MongoDB integration)
- ⚠️ AI: Placeholder responses (needs actual ML models)

### Next Steps (TODOs in Code)

1. **Authentication Module**
   - Implement password hashing (bcrypt)
   - Add JWT token generation and validation
   - Create user model in MongoDB
   - Add refresh token mechanism

2. **Products Module**
   - Replace mock data with MongoDB queries
   - Add image upload functionality
   - Implement search and filtering
   - Add pagination

3. **AI Module**
   - Integrate actual ML models for recommendations
   - Implement vector search with embeddings
   - Add LLM integration for chatbot
   - Build price prediction model

## 🚢 Deployment

### Emergent Platform (Managed)

This project is configured to run on Emergent's managed infrastructure:

1. Frontend runs on port 3000 (with hot reload)
2. Backend runs on port 8001 (managed by supervisor)
3. MongoDB is pre-configured

**Restart services:**
```bash
sudo supervisorctl restart frontend
sudo supervisorctl restart backend
sudo supervisorctl restart all
```

**Check logs:**
```bash
# Backend logs
tail -f /var/log/supervisor/backend.*.log

# Frontend logs
tail -f /var/log/supervisor/frontend.*.log
```

### External Deployment

For deploying outside Emergent:

1. **Backend**: Deploy to any Python hosting (Heroku, AWS, GCP, etc.)
2. **Frontend**: Deploy to Vercel, Netlify, or S3 + CloudFront
3. **Database**: Use MongoDB Atlas or self-hosted MongoDB
4. Update environment variables accordingly

## 🔗 GitHub Integration

To connect this project to GitHub:

1. Create a new repository on GitHub named "hamro"
2. Initialize git (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Hamro platform setup"
   ```
3. Connect to remote:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/hamro.git
   git branch -M main
   git push -u origin main
   ```

## 📝 License

MIT License - feel free to use this project as a template for your own applications.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ on Emergent Platform**
