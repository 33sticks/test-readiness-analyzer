# Test Readiness Analyzer

A comprehensive FastAPI-based tool for analyzing A/B test proposals, providing statistical validation, hypothesis quality scoring, and design recommendations. Built as an Optimizely Opal tool for seamless integration with Optimizely's experimentation platform.

## Features

- **Statistical Analysis**: Calculate required sample sizes, test duration, and statistical power
- **Hypothesis Scoring**: Evaluate hypothesis quality across specificity, measurability, directionality, and rationale
- **Design Validation**: Check variation count, traffic allocation, and metric selection
- **Comprehensive Recommendations**: Actionable feedback for improving test readiness
- **Optimizely Opal Integration**: Native integration with Optimizely's tool ecosystem

## Project Structure

```
test-readiness-analyzer/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── Procfile              # Railway deployment configuration
├── railway.json          # Railway service configuration
├── runtime.txt           # Python version specification
├── .gitignore            # Git ignore patterns
├── README.md             # This documentation
└── core/                 # Core analysis modules
    ├── __init__.py
    ├── models.py         # Pydantic data models
    ├── statistical.py    # Statistical calculations
    ├── hypothesis.py      # Hypothesis quality scoring
    └── design.py         # Test design validation
```

## API Endpoints

### GET /health
Health check endpoint for monitoring and deployment verification.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### GET /discovery
Optimizely Opal tool discovery endpoint that returns the tool manifest.

**Response:**
```json
{
  "name": "test_readiness_analyzer",
  "display_name": "Test Readiness Analyzer",
  "description": "Analyzes A/B test proposals for statistical validity, hypothesis quality, and design best practices",
  "version": "1.0.0",
  "provider": "33 Sticks",
  "parameters": [...]
}
```

### POST /analyze
Analyze a test proposal for readiness.

**Request Body:**
```json
{
  "hypothesis": "Changing the checkout button color from blue to green will increase conversion rate because green is associated with 'go' and action",
  "baseline_conversion_rate": 0.15,
  "minimum_detectable_effect": 0.05,
  "daily_traffic": 1000,
  "number_of_variations": 2,
  "primary_metric": "conversion_rate",
  "secondary_metrics": ["click_through_rate", "time_on_page"],
  "test_start_date": "2024-01-15T00:00:00Z"
}
```

**Response:**
```json
{
  "readiness_status": "READY",
  "statistical_analysis": {
    "required_sample_size": 1234,
    "estimated_duration_days": 3,
    "samples_per_day_needed": 617,
    "confidence_level": 0.95,
    "statistical_power": 0.8,
    "warnings": []
  },
  "hypothesis_analysis": {
    "overall_score": 8.5,
    "specificity_score": 2.0,
    "measurability_score": 2.5,
    "directionality_score": 2.0,
    "rationale_score": 2.0,
    "feedback": [
      "✓ Identifies specific UI elements (1 found)",
      "✓ Uses quantitative metrics (1 found)",
      "✓ Predicts positive outcome (1 indicators)",
      "✓ Contains reasoning (1 indicators)"
    ],
    "improved_hypothesis": "Hypothesis is already well-structured. Consider adding more specific details if possible."
  },
  "design_analysis": {
    "variation_count_warning": null,
    "traffic_allocation_warning": null,
    "metric_warnings": [],
    "recommendations": [
      "Ensure proper randomization and avoid selection bias in traffic allocation.",
      "Set up proper tracking and analytics before test launch.",
      "Define success criteria and stopping rules before starting the test.",
      "Plan for post-test analysis and implementation of winning variations."
    ]
  },
  "overall_recommendations": [
    "✅ Test is ready to launch! All criteria met."
  ]
}
```

## Local Development

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd test-readiness-analyzer
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

4. Run the application:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:8000`

### API Documentation
Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Railway Deployment

### Prerequisites
- Railway account
- Git repository with the code

### Deployment Steps
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Python application
3. The deployment will use the configuration in:
   - `Procfile`: Defines the web process
   - `railway.json`: Service configuration
   - `runtime.txt`: Python version
   - `requirements.txt`: Dependencies

### Environment Variables
No additional environment variables are required for basic functionality.

### Health Checks
Railway will automatically monitor the `/health` endpoint for service health.

## Optimizely Opal Integration

### Tool Registration
1. In your Optimizely workspace, navigate to Tools
2. Add a new custom tool
3. Use the discovery endpoint URL: `https://your-app.railway.app/discovery`
4. The tool will be automatically configured with the provided parameters

### Usage in Optimizely
1. Create a new experiment in Optimizely
2. Navigate to the Tools section
3. Select "Test Readiness Analyzer"
4. Fill in the required parameters:
   - **Hypothesis**: Describe what you're testing and why
   - **Baseline Conversion Rate**: Current performance (0-1)
   - **Minimum Detectable Effect**: Smallest change you want to detect (0-1)
   - **Daily Traffic**: Expected daily visitors
   - **Number of Variations**: Test variations (including control)
   - **Primary Metric**: Main success metric
   - **Secondary Metrics**: Additional metrics to track (optional)
   - **Test Start Date**: Planned launch date (optional)

### Interpreting Results
- **READY**: Test meets all criteria and is ready to launch
- **NEEDS_WORK**: Test needs minor improvements before launch
- **NOT_READY**: Test has critical issues that must be addressed

## Statistical Methodology

### Sample Size Calculation
Uses the two-sample proportion test formula:
```
n = 2 * ((z_α/2 + z_β)² * p * (1-p)) / MDE²
```

Where:
- `z_α/2` = 1.96 (for α = 0.05)
- `z_β` = 0.84 (for power = 0.8)
- `p` = pooled proportion
- `MDE` = minimum detectable effect

### Hypothesis Scoring
Scores are calculated across four dimensions (0-2.5 each):
- **Specificity**: Identifies what's changing and what actions are expected
- **Measurability**: Uses quantitative metrics and measurement approaches
- **Directionality**: Predicts outcome direction (increase/decrease)
- **Rationale**: Contains reasoning and supporting evidence

### Readiness Status
- **READY**: hypothesis_score ≥ 7, duration ≤ 30 days, no critical warnings
- **NEEDS_WORK**: hypothesis_score 5-7 OR duration 30-60 days
- **NOT_READY**: hypothesis_score < 5 OR duration > 60 days OR critical design flaws

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -m "Add feature"`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Create an issue in the repository

## Changelog

### Version 1.0.0
- Initial release
- Statistical analysis with scipy
- Hypothesis quality scoring
- Design validation and recommendations
- Optimizely Opal integration
- Railway deployment support




