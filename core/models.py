"""
Pydantic models for the Test Readiness Analyzer.

This module defines all the data models used for input validation,
output formatting, and type safety throughout the application.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class ReadinessStatus(str, Enum):
    """Enum for test readiness status."""
    READY = "READY"
    NEEDS_WORK = "NEEDS_WORK"
    NOT_READY = "NOT_READY"


class TestProposal(BaseModel):
    """Input model for test proposal analysis."""
    
    hypothesis: str = Field(..., min_length=10, description="The test hypothesis")
    baseline_conversion_rate: float = Field(..., ge=0.0, le=1.0, description="Baseline conversion rate (0-1)")
    minimum_detectable_effect: float = Field(..., ge=0.0, le=1.0, description="Minimum detectable effect (0-1)")
    daily_traffic: int = Field(..., gt=0, description="Daily traffic volume")
    number_of_variations: int = Field(default=1, ge=1, description="Number of test variations")
    primary_metric: str = Field(..., min_length=1, description="Primary success metric")
    secondary_metrics: Optional[List[str]] = Field(default=None, description="Secondary metrics to track")
    test_start_date: Optional[datetime] = Field(default=None, description="Planned test start date")
    
    @validator('hypothesis')
    def hypothesis_must_not_be_empty(cls, v):
        """Validate that hypothesis is not just whitespace."""
        if not v.strip():
            raise ValueError('Hypothesis cannot be empty or just whitespace')
        return v.strip()
    
    @validator('secondary_metrics')
    def secondary_metrics_validation(cls, v):
        """Validate secondary metrics if provided."""
        if v is not None:
            if len(v) == 0:
                return None
            # Remove empty strings and duplicates
            v = [metric.strip() for metric in v if metric.strip()]
            return list(set(v)) if v else None
        return v


class StatisticalAnalysis(BaseModel):
    """Statistical analysis results."""
    
    required_sample_size: int = Field(..., description="Required sample size per variation")
    estimated_duration_days: int = Field(..., description="Estimated test duration in days")
    samples_per_day_needed: int = Field(..., description="Samples needed per day")
    confidence_level: float = Field(..., description="Statistical confidence level")
    statistical_power: float = Field(..., description="Statistical power")
    warnings: List[str] = Field(default_factory=list, description="Statistical warnings")


class HypothesisScore(BaseModel):
    """Hypothesis quality scoring results."""
    
    overall_score: float = Field(..., ge=0.0, le=10.0, description="Overall hypothesis score (0-10)")
    specificity_score: float = Field(..., ge=0.0, le=2.5, description="Specificity score (0-2.5)")
    measurability_score: float = Field(..., ge=0.0, le=2.5, description="Measurability score (0-2.5)")
    directionality_score: float = Field(..., ge=0.0, le=2.5, description="Directionality score (0-2.5)")
    rationale_score: float = Field(..., ge=0.0, le=2.5, description="Rationale score (0-2.5)")
    feedback: List[str] = Field(default_factory=list, description="Detailed feedback")
    improved_hypothesis: Optional[str] = Field(default=None, description="Suggested improved hypothesis")


class DesignAnalysis(BaseModel):
    """Test design validation results."""
    
    variation_count_warning: Optional[str] = Field(default=None, description="Warning about variation count")
    traffic_allocation_warning: Optional[str] = Field(default=None, description="Warning about traffic allocation")
    metric_warnings: List[str] = Field(default_factory=list, description="Metric-specific warnings")
    recommendations: List[str] = Field(default_factory=list, description="Design recommendations")


class AnalysisResult(BaseModel):
    """Combined analysis result."""
    
    readiness_status: ReadinessStatus = Field(..., description="Overall readiness status")
    statistical_analysis: StatisticalAnalysis = Field(..., description="Statistical analysis results")
    hypothesis_analysis: HypothesisScore = Field(..., description="Hypothesis scoring results")
    design_analysis: DesignAnalysis = Field(..., description="Design validation results")
    overall_recommendations: List[str] = Field(default_factory=list, description="Overall recommendations")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True




