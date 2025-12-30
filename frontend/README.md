# HarvestIQ Frontend

A modern, beautiful React frontend for the HarvestIQ agricultural recommendation system.

## Features

✨ **Modern UI** - Beautiful, responsive design with smooth animations
🎯 **Easy Navigation** - Intuitive navigation between features
🧠 **Model Training** - Train AI models with progress tracking
🌾 **Smart Recommendations** - Get customer-specific product recommendations
📊 **Real-time Insights** - View analytics and insights about recommendations

## Setup

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

### Running the Application

Start the development server:
```bash
npm start
```

The application will open in your browser at `http://localhost:3000`

### Building for Production

Create a production build:
```bash
npm run build
```

## Project Structure

```
frontend/
├── public/
│   └── index.html          # Main HTML file
├── src/
│   ├── App.js              # Main App component
│   ├── App.css             # Global styles
│   ├── index.js            # React entry point
│   ├── pages/              # Page components
│   │   ├── HomePage.js     # Landing page
│   │   ├── TrainPage.js    # Model training interface
│   │   └── RecommendPage.js # Recommendations interface
│   └── styles/             # Component-specific styles
│       ├── HomePage.css
│       ├── TrainPage.css
│       └── RecommendPage.css
├── package.json            # Dependencies and scripts
└── README.md              # This file
```

## API Integration

The frontend connects to the Django backend running on `http://127.0.0.1:8000/`

### Endpoints Used:
- **Train Models**: `POST /api/train/`
- **Get Recommendations**: `GET /api/recommend/<customer_id>/`

## Features Explained

### 🏠 Home Page
- Welcome section with project overview
- Feature highlights
- Quick start guide
- API endpoint information

### 🧠 Train Models
- Initialize and train ML models
- Progress tracking
- Real-time feedback
- Detailed training process information

### 🌾 Get Recommendations
- Search for customer recommendations
- View product predictions
- See surplus flags
- Get insights about recommendations

## Customization

### Colors
Edit the gradients in `App.css` and component CSS files:
```css
background: linear-gradient(135deg, #667eea, #764ba2);
```

### API Base URL
Update the API URL in page components if needed:
```javascript
axios.post('http://127.0.0.1:8000/api/train/');
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure your Django backend has CORS enabled:
```python
# settings.py
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

### Connection Issues
- Ensure Django backend is running on `http://127.0.0.1:8000/`
- Check that models are trained before getting recommendations
- Verify customer IDs exist in the training data

## Performance

- Optimized with lazy loading
- Smooth animations and transitions
- Responsive grid layouts
- Progressive enhancement

## License

MIT License - feel free to use this in your projects!

## Support

For issues or questions, please check the main project README or contact the development team.
