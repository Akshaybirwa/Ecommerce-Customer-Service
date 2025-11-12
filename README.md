# 🛍️ AI-Driven E-Commerce Customer Support Assistant

An intelligent, AI-powered chatbot for e-commerce that helps customers find products, compare prices, and get instant assistance. The chatbot searches for real products from Flipkart and Amazon, displays product images, and provides direct purchase links.

![Status](https://img.shields.io/badge/status-active-success)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

- 🤖 **AI-Powered Chatbot**: Intelligent customer service assistant using Gemini AI (optional) or free alternatives
- 🔍 **Real Product Search**: Search for products across e-commerce platforms (Flipkart, Amazon)
- 🖼️ **Product Images**: Display real product images with fallback support
- 🔗 **Direct Purchase Links**: One-click links to Flipkart and Amazon product pages
- 💬 **Real-time Chat**: Interactive chat interface with typing animations
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 🎨 **Modern UI**: Beautiful gradient design with smooth animations
- 🆓 **Free APIs**: Uses DuckDuckGo and web-based search (no API limits!)
- ⚡ **Fast & Reliable**: Optimized for performance with lazy loading

## 🚀 Tech Stack

### Frontend
- **React 19** - Modern UI framework
- **Axios** - HTTP client for API calls
- **CSS3** - Custom styling with animations
- **Emotion** - CSS-in-JS styling

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Google Generative AI (Gemini)** - Optional AI responses
- **DuckDuckGo API** - Free product search
- **BeautifulSoup4** - Web scraping support
- **Requests** - HTTP library

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Node.js** (v14 or higher)
- **Python** (v3.8 or higher)
- **pip** (Python package manager)
- **npm** or **yarn** (Node package manager)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AI-Driven-Customer-Support-Assistan.git
cd AI-Driven-Customer-Support-Assistan
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 4. Environment Variables

Create a `.env` file in the `backend` directory:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Note**: The Gemini API key is optional. The application will work with free alternatives if no API key is provided.

## 🎯 Usage

### Running Locally

#### Start Backend Server

```bash
cd backend
python app.py
```

The backend will run on `http://127.0.0.1:5000`

#### Start Frontend Development Server

```bash
cd frontend
npm start
```

The frontend will run on `http://localhost:3000`

### Using the Application

1. Open your browser and navigate to `http://localhost:3000`
2. Start chatting with the AI assistant
3. Ask about products (e.g., "smart watch under 20k", "wireless headphones")
4. View product recommendations with images and purchase links
5. Click "Buy on Flipkart" or "Buy on Amazon" to visit product pages

## 🌐 Deployment to Vercel

### Frontend Deployment (React)

#### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Vercel**:
   - Go to [vercel.com](https://vercel.com) and sign in
   - Click "Add New Project"
   - Import your GitHub repository
   - Configure the project:
     - **Framework Preset**: React
     - **Root Directory**: `frontend` (or leave as root if using vercel.json)
     - **Build Command**: `npm run build` (or `cd frontend && npm run build`)
     - **Output Directory**: `build` (or `frontend/build`)
   - Add Environment Variable:
     - **Name**: `REACT_APP_API_URL`
     - **Value**: Your deployed backend URL (e.g., `https://your-backend.railway.app`)
   - Click "Deploy"

#### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   # From project root
   vercel
   
   # Or from frontend directory
   cd frontend
   vercel
   ```

4. **Add Environment Variable**:
   ```bash
   vercel env add REACT_APP_API_URL
   # Enter your backend URL when prompted
   ```

#### Option 3: Using vercel.json (Already Configured)

The project includes a `vercel.json` file that's pre-configured. Simply:
1. Push to GitHub
2. Import to Vercel
3. Vercel will automatically detect and use the configuration

### Backend Deployment Options

Since Vercel primarily supports serverless functions, you have a few options:

#### Option 1: Deploy Backend to Vercel (Serverless Functions)

Create `vercel.json` in the root directory:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/app.py"
    }
  ]
}
```

#### Option 2: Deploy Backend Separately (Recommended)

Deploy the Flask backend to:
- **Railway** - [railway.app](https://railway.app)
- **Render** - [render.com](https://render.com)
- **Heroku** - [heroku.com](https://heroku.com)
- **PythonAnywhere** - [pythonanywhere.com](https://pythonanywhere.com)

**Example for Railway/Render:**
1. Create a new project
2. Connect your GitHub repository
3. Set root directory to `backend`
4. Set start command: `python app.py` or `gunicorn app:app`
5. Add environment variable: `GOOGLE_API_KEY` (optional)

#### Setting Environment Variables in Vercel

After deploying both frontend and backend:

1. **In Vercel Dashboard**:
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add `REACT_APP_API_URL` with your backend URL
   - Example: `https://your-backend.railway.app`

2. **Redeploy** after adding environment variables (Vercel will auto-redeploy)

**Note**: The frontend is already configured to use `REACT_APP_API_URL` environment variable. No code changes needed!

## 📁 Project Structure

```
AI-Driven-Customer-Support-Assistan/
│
├── backend/
│   ├── app.py                 # Flask backend server
│   ├── requirements.txt       # Python dependencies
│   └── .env                  # Environment variables (create this)
│
├── frontend/
│   ├── public/               # Static files
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatBot.js    # Main chatbot component
│   │   │   └── ChatBot.css  # Chatbot styles
│   │   ├── App.js            # Main app component
│   │   └── index.js          # Entry point
│   ├── package.json          # Node dependencies
│   └── package-lock.json
│
├── README.md                 # This file
└── LICENSE                   # License file
```

## 🔌 API Endpoints

### `POST /api/chat`
Send a message to the chatbot and get product recommendations.

**Request:**
```json
{
  "message": "smart watch under 20k"
}
```

**Response:**
```json
{
  "response": "I found some great smartwatch options...",
  "products": [
    {
      "name": "Product Name",
      "price": "₹20,000 - ₹25,000",
      "description": "Product description...",
      "image": "https://...",
      "flipkart_link": "https://www.flipkart.com/search?q=...",
      "amazon_link": "https://www.amazon.in/s?k=...",
      "rating": "4.5"
    }
  ]
}
```

### `GET /api/products?q=query`
Search for products directly.

**Example:**
```
GET /api/products?q=wireless+headphones
```

## 🎨 Features in Detail

### Product Search
- Searches using DuckDuckGo API (free, unlimited)
- Falls back to web-based product templates
- Extracts price ranges from queries
- Provides product recommendations

### Product Display
- Real product images from Unsplash
- Product ratings and descriptions
- Direct links to Flipkart and Amazon
- Responsive product cards

### Chat Interface
- Real-time messaging
- Typing animations
- Smooth scrolling
- Error handling

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | No | Gemini API key for enhanced AI responses (optional) |

### CORS Configuration

The backend is configured to accept requests from any origin. For production, update CORS settings in `backend/app.py`:

```python
CORS(app, resources={r"/api/*": {"origins": "https://your-frontend-domain.com"}})
```

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change port in app.py
app.run(debug=True, port=5001)
```

**Module not found:**
```bash
pip install -r requirements.txt
```

### Frontend Issues

**API connection failed:**
- Check if backend is running
- Verify CORS settings
- Check API URL in ChatBot.js

**Images not loading:**
- Check browser console for CORS errors
- Verify image URLs are accessible
- Check network tab for failed requests

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- DuckDuckGo for free search API
- Unsplash for product images
- React and Flask communities

## 📞 Support

For support, email your-email@example.com or open an issue in the repository.

## ✅ Deployment Checklist

Before deploying, make sure you have:

- [ ] Backend deployed to Railway/Render/Heroku
- [ ] Backend URL noted down
- [ ] Frontend code pushed to GitHub
- [ ] Environment variable `REACT_APP_API_URL` set in Vercel
- [ ] `GOOGLE_API_KEY` set in backend (optional)
- [ ] CORS configured in backend for your frontend domain
- [ ] Tested locally before deployment

## 🚀 Quick Deploy Steps

1. **Deploy Backend** (Railway/Render):
   ```bash
   # Connect repo, set root to 'backend', deploy
   ```

2. **Deploy Frontend** (Vercel):
   ```bash
   # Import GitHub repo, set environment variable, deploy
   ```

3. **Update CORS** in backend:
   ```python
   CORS(app, resources={r"/api/*": {"origins": "https://your-frontend.vercel.app"}})
   ```

4. **Test** your deployed application!

---

⭐ If you like this project, please give it a star on GitHub!
"# rr" 
