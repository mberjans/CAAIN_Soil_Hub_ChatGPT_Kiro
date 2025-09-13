# AFAS Frontend Service

The Autonomous Farm Advisory System (AFAS) Frontend provides two distinct user interface options for accessing agricultural recommendations and farm management tools.

## 🌱 Overview

This service offers both traditional web interface (FastAPI + Jinja2) and modern data dashboard (Streamlit) options, allowing users to choose the interface that best fits their needs.

### Frontend Options

1. **FastAPI + Jinja2 Web Interface**
   - Traditional web application with server-side rendering
   - Mobile-responsive design optimized for field use
   - Form-based interactions for agricultural data input
   - Integration with all backend microservices

2. **Streamlit Data Dashboard**
   - Interactive data visualization and analysis
   - Real-time charts and graphs using Plotly
   - Streamlined interface for data-driven decisions
   - Built-in widgets for agricultural calculations

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

### Option 1: FastAPI Web Interface

```bash
# Start FastAPI server
python start_fastapi.py

# Or manually
cd src && python main.py
```

Access at: http://localhost:3000

### Option 2: Streamlit Dashboard

```bash
# Start Streamlit server
python start_streamlit.py

# Or manually
streamlit run src/streamlit_app.py --server.port 8501
```

Access at: http://localhost:8501

## 📁 Project Structure

```
services/frontend/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── streamlit_app.py        # Streamlit application
│   ├── templates/              # Jinja2 templates
│   │   ├── dashboard.html      # Main dashboard
│   │   ├── crop_selection.html # Crop selection page
│   │   ├── soil_fertility.html # Soil health page
│   │   └── fertilizer_strategy.html # Fertilizer optimizer
│   ├── static/                 # Static assets
│   │   ├── css/
│   │   │   └── agricultural.css # Agricultural theme
│   │   └── js/
│   │       └── agricultural.js  # Agricultural calculations
│   └── components/             # Reusable components
├── start_fastapi.py           # FastAPI startup script
├── start_streamlit.py         # Streamlit startup script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🌾 Features

### Core Agricultural Functions

1. **Question Processing**
   - Natural language question input
   - Integration with question router service
   - Confidence scoring and explanations

2. **Crop Selection Recommendations**
   - Soil-based crop suitability analysis
   - Climate and location considerations
   - Variety-specific recommendations

3. **Soil Health Assessment**
   - Interactive soil health scoring
   - Nutrient level visualization
   - Improvement recommendations

4. **Fertilizer Strategy Optimization**
   - Economic ROI calculations
   - 4R nutrient management principles
   - Cost-benefit analysis

### Technical Features

- **Responsive Design**: Mobile-optimized for field use
- **Real-time Validation**: Client-side agricultural data validation
- **Progressive Enhancement**: Works without JavaScript
- **Accessibility**: WCAG 2.1 compliant
- **Performance**: Optimized for rural internet connections

## 🔧 Configuration

### Environment Variables

```bash
# FastAPI Configuration
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=3000
FRONTEND_RELOAD=true

# Streamlit Configuration
STREAMLIT_PORT=8501

# Backend Service URLs
QUESTION_ROUTER_URL=http://localhost:8000
RECOMMENDATION_ENGINE_URL=http://localhost:8001
USER_MANAGEMENT_URL=http://localhost:8005
DATA_INTEGRATION_URL=http://localhost:8002
IMAGE_ANALYSIS_URL=http://localhost:8003
AI_AGENT_URL=http://localhost:8004
```

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FRONTEND_PORT=3000
export QUESTION_ROUTER_URL=http://localhost:8000

# Start development server
python start_fastapi.py
```

## 🎨 User Interface

### FastAPI Web Interface

The traditional web interface provides:

- **Dashboard**: Overview of farm data and quick question input
- **Crop Selection**: Detailed crop recommendation forms
- **Soil Fertility**: Soil health assessment and improvement plans
- **Fertilizer Strategy**: Economic optimization tools

### Streamlit Dashboard

The data dashboard includes:

- **Interactive Charts**: Plotly-powered visualizations
- **Real-time Calculations**: Live agricultural computations
- **Data Input Widgets**: Streamlined data entry
- **Export Capabilities**: Download reports and charts

## 🔌 API Integration

### Backend Service Integration

```python
# Example API call to question router
async def ask_question(question, context):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{QUESTION_ROUTER_URL}/api/v1/questions/classify",
            json={"question": question, "context": context}
        )
        return response.json()
```

### Error Handling

- Graceful degradation when services are unavailable
- User-friendly error messages
- Fallback to cached data when possible
- Retry mechanisms for transient failures

## 📱 Mobile Optimization

### Field-Ready Design

- **Large Touch Targets**: Easy to use with gloves
- **High Contrast**: Readable in bright sunlight
- **Offline Capability**: Basic functionality without internet
- **Fast Loading**: Optimized for slow connections

### Progressive Web App Features

- **App-like Experience**: Can be installed on mobile devices
- **Offline Storage**: Cache critical data locally
- **Push Notifications**: Alerts for time-sensitive recommendations

## 🧪 Testing

### Frontend Testing

```bash
# Run JavaScript tests
npm test

# Run Python tests
pytest tests/

# Run accessibility tests
axe-core tests/
```

### Agricultural Validation

- Soil data validation against known ranges
- Nutrient calculation verification
- Expert review of recommendation logic
- User acceptance testing with farmers

## 🚀 Deployment

### Production Deployment

```bash
# Build production assets
npm run build

# Start production server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
EXPOSE 3000

CMD ["python", "start_fastapi.py"]
```

## 📊 Monitoring

### Performance Metrics

- Page load times
- API response times
- User interaction tracking
- Error rates and types

### Agricultural Metrics

- Recommendation accuracy
- User satisfaction scores
- Feature usage statistics
- Conversion rates (recommendations to actions)

## 🤝 Contributing

### Development Guidelines

1. Follow agricultural domain guidelines
2. Maintain mobile-first responsive design
3. Ensure accessibility compliance
4. Test with real farm data
5. Get expert review for agricultural logic

### Code Style

- Python: Follow PEP 8 and agricultural naming conventions
- JavaScript: Use agricultural-specific variable names
- CSS: Follow BEM methodology with agricultural themes
- HTML: Semantic markup with agricultural context

## 📚 Documentation

### User Guides

- [Farmer Quick Start Guide](docs/farmer-guide.md)
- [Agricultural Consultant Manual](docs/consultant-guide.md)
- [Mobile Usage Tips](docs/mobile-guide.md)

### Technical Documentation

- [API Integration Guide](docs/api-integration.md)
- [Customization Guide](docs/customization.md)
- [Deployment Guide](docs/deployment.md)

## 🆘 Support

### Getting Help

- **Technical Issues**: Create GitHub issue
- **Agricultural Questions**: Contact agricultural experts
- **User Support**: Email support@afas.com

### Common Issues

1. **Service Unavailable**: Check backend service status
2. **Slow Loading**: Verify internet connection
3. **Invalid Data**: Review agricultural data ranges
4. **Mobile Issues**: Clear browser cache

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Agricultural experts for domain validation
- University extension services for research data
- Farmers for user feedback and testing
- Open source community for tools and libraries

---

**AFAS Frontend** - Bringing science-based agricultural recommendations to farmers through intuitive, accessible interfaces.