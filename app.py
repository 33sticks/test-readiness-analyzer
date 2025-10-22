"""
Test Readiness Analyzer - FastAPI Application

A comprehensive tool for analyzing A/B test proposals, providing statistical
validation, hypothesis scoring, and design recommendations.
"""

import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.models import TestProposal, AnalysisResult, ReadinessStatus
from core.statistical import analyze_statistical_validity
from core.hypothesis import score_hypothesis
from core.design import validate_design

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Test Readiness Analyzer",
    description="Analyzes A/B test proposals for statistical validity, hypothesis quality, and design best practices",
    version="1.0.0"
)

# Add CORS middleware for Optimizely integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring and deployment verification.
    
    Returns:
        Status and version information
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/discovery")
async def discovery() -> Dict[str, Any]:
    """
    Optimizely Opal tool discovery endpoint.
    
    Returns:
        Tool manifest for Optimizely Opal integration
    """
    logger.info("Discovery endpoint requested")
    
    return {
        "functions": [
            {
                "name": "test_readiness_analyzer",
                "description": "Analyzes A/B test proposals for statistical validity, hypothesis quality, and design best practices. Use this when a user wants to evaluate if their experiment is ready to launch.",
                "parameters": [
                    {
                        "name": "hypothesis",
                        "type": "string",
                        "description": "The test hypothesis describing what you want to test and why",
                        "required": True
                    },
                    {
                        "name": "baseline_conversion_rate",
                        "type": "number",
                        "description": "Current baseline conversion rate (0-1)",
                        "required": True
                    },
                    {
                        "name": "minimum_detectable_effect",
                        "type": "number",
                        "description": "Minimum detectable effect you want to measure (0-1)",
                        "required": True
                    },
                    {
                        "name": "daily_traffic",
                        "type": "integer",
                        "description": "Daily traffic volume for the test",
                        "required": True
                    },
                    {
                        "name": "number_of_variations",
                        "type": "integer",
                        "description": "Number of test variations (including control)",
                        "required": False
                    },
                    {
                        "name": "primary_metric",
                        "type": "string",
                        "description": "Primary success metric for the test",
                        "required": True
                    },
                    {
                        "name": "secondary_metrics",
                        "type": "array",
                        "description": "Additional metrics to track during the test",
                        "required": False
                    },
                    {
                        "name": "test_start_date",
                        "type": "string",
                        "description": "Planned test start date (ISO format)",
                        "required": False
                    }
                ],
                "endpoint": "/analyze",
                "http_method": "POST",
                "auth_requirements": []
            }
        ]
    }


@app.post("/analyze")
async def analyze_test_proposal(proposal: TestProposal) -> AnalysisResult:
    """
    Analyze a test proposal for readiness.
    
    Args:
        proposal: TestProposal object containing test parameters
    
    Returns:
        AnalysisResult with comprehensive analysis
    
    Raises:
        HTTPException: If analysis fails
    """
    try:
        logger.info(f"Analyzing test proposal: {proposal.hypothesis[:50]}...")
        
        # Perform statistical analysis
        logger.info("Performing statistical analysis...")
        statistical_analysis = analyze_statistical_validity(proposal)
        
        # Score hypothesis quality
        logger.info("Scoring hypothesis quality...")
        hypothesis_analysis = score_hypothesis(proposal)
        
        # Validate test design
        logger.info("Validating test design...")
        design_analysis = validate_design(proposal, statistical_analysis.required_sample_size)
        
        # Determine readiness status
        readiness_status = determine_readiness_status(
            hypothesis_analysis.overall_score,
            statistical_analysis.estimated_duration_days,
            design_analysis
        )
        
        # Generate overall recommendations
        overall_recommendations = generate_overall_recommendations(
            readiness_status,
            statistical_analysis,
            hypothesis_analysis,
            design_analysis
        )
        
        result = AnalysisResult(
            readiness_status=readiness_status,
            statistical_analysis=statistical_analysis,
            hypothesis_analysis=hypothesis_analysis,
            design_analysis=design_analysis,
            overall_recommendations=overall_recommendations
        )
        
        logger.info(f"Analysis complete. Status: {readiness_status}")
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def determine_readiness_status(
    hypothesis_score: float,
    duration_days: int,
    design_analysis
) -> ReadinessStatus:
    """
    Determine overall readiness status based on analysis results.
    
    Args:
        hypothesis_score: Overall hypothesis score (0-10)
        duration_days: Estimated test duration in days
        design_analysis: DesignAnalysis object
    
    Returns:
        ReadinessStatus enum value
    """
    # Check for critical design flaws
    critical_warnings = [
        design_analysis.variation_count_warning,
        design_analysis.traffic_allocation_warning
    ]
    has_critical_warnings = any(warning for warning in critical_warnings if warning)
    
    # Determine status based on criteria
    if hypothesis_score >= 7 and duration_days <= 30 and not has_critical_warnings:
        return ReadinessStatus.READY
    elif hypothesis_score >= 5 and duration_days <= 60 and not has_critical_warnings:
        return ReadinessStatus.NEEDS_WORK
    else:
        return ReadinessStatus.NOT_READY


def generate_overall_recommendations(
    readiness_status: ReadinessStatus,
    statistical_analysis,
    hypothesis_analysis,
    design_analysis
) -> List[str]:
    """
    Generate overall recommendations based on analysis results.
    
    Args:
        readiness_status: Overall readiness status
        statistical_analysis: StatisticalAnalysis object
        hypothesis_analysis: HypothesisScore object
        design_analysis: DesignAnalysis object
    
    Returns:
        List of overall recommendations
    """
    recommendations = []
    
    # Status-specific recommendations
    if readiness_status == ReadinessStatus.READY:
        recommendations.append("✅ Test is ready to launch! All criteria met.")
    elif readiness_status == ReadinessStatus.NEEDS_WORK:
        recommendations.append("⚠️ Test needs some improvements before launch.")
    else:
        recommendations.append("❌ Test is not ready. Address critical issues before proceeding.")
    
    # Statistical recommendations
    if statistical_analysis.estimated_duration_days > 30:
        recommendations.append(
            f"📊 Consider reducing test duration from {statistical_analysis.estimated_duration_days} days "
            "by increasing traffic or reducing MDE."
        )
    
    # Hypothesis recommendations
    if hypothesis_analysis.overall_score < 7:
        recommendations.append(
            f"💡 Improve hypothesis quality (current score: {hypothesis_analysis.overall_score:.1f}/10). "
            "See detailed feedback for specific improvements."
        )
    
    # Design recommendations
    if design_analysis.recommendations:
        recommendations.extend(design_analysis.recommendations[:3])  # Top 3 design recommendations
    
    return recommendations


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




