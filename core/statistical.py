"""
Statistical analysis module for test readiness evaluation.

This module provides statistical calculations for A/B test validity,
including sample size calculations, duration estimates, and power analysis.
"""

import math
from typing import List
from scipy.stats import norm

from .models import TestProposal, StatisticalAnalysis


def calculate_sample_size(
    baseline_rate: float,
    mde: float,
    power: float = 0.8,
    alpha: float = 0.05
) -> int:
    """
    Calculate required sample size per variation for a two-sample proportion test.
    
    Args:
        baseline_rate: Baseline conversion rate (0-1)
        mde: Minimum detectable effect (0-1)
        power: Statistical power (default 0.8)
        alpha: Significance level (default 0.05)
    
    Returns:
        Required sample size per variation
    """
    # Calculate z-scores
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)
    
    # Calculate pooled proportion
    p1 = baseline_rate
    p2 = baseline_rate + mde
    
    # Ensure p2 doesn't exceed 1
    p2 = min(p2, 1.0)
    
    # Pooled proportion for variance calculation
    p_pooled = (p1 + p2) / 2
    
    # Calculate sample size using two-sample proportion test formula
    numerator = (z_alpha + z_beta) ** 2 * 2 * p_pooled * (1 - p_pooled)
    denominator = mde ** 2
    
    sample_size = math.ceil(numerator / denominator)
    
    return max(sample_size, 100)  # Minimum sample size of 100


def estimate_duration(
    required_sample_size: int,
    daily_traffic: int,
    number_of_variations: int
) -> int:
    """
    Estimate test duration based on required sample size and traffic.
    
    Args:
        required_sample_size: Required sample size per variation
        daily_traffic: Daily traffic volume
        number_of_variations: Number of test variations
    
    Returns:
        Estimated duration in days
    """
    # Total samples needed across all variations
    total_samples_needed = required_sample_size * number_of_variations
    
    # Calculate duration
    duration = math.ceil(total_samples_needed / daily_traffic)
    
    return max(duration, 1)  # Minimum 1 day


def analyze_statistical_validity(proposal: TestProposal) -> StatisticalAnalysis:
    """
    Perform comprehensive statistical analysis of the test proposal.
    
    Args:
        proposal: TestProposal object containing test parameters
    
    Returns:
        StatisticalAnalysis object with results and warnings
    """
    warnings: List[str] = []
    
    # Calculate required sample size
    required_sample_size = calculate_sample_size(
        baseline_rate=proposal.baseline_conversion_rate,
        mde=proposal.minimum_detectable_effect,
        power=0.8,
        alpha=0.05
    )
    
    # Estimate duration
    estimated_duration = estimate_duration(
        required_sample_size=required_sample_size,
        daily_traffic=proposal.daily_traffic,
        number_of_variations=proposal.number_of_variations
    )
    
    # Calculate samples per day needed
    total_samples_needed = required_sample_size * proposal.number_of_variations
    samples_per_day = math.ceil(total_samples_needed / estimated_duration)
    
    # Generate warnings based on analysis
    if estimated_duration > 60:
        warnings.append(
            f"Test duration is {estimated_duration} days, which may be too long. "
            "Consider increasing traffic or reducing MDE."
        )
    elif estimated_duration > 30:
        warnings.append(
            f"Test duration is {estimated_duration} days. "
            "Consider if this timeline is acceptable for your business."
        )
    
    if proposal.minimum_detectable_effect < 0.01:
        warnings.append(
            "Very small MDE detected. This may require very large sample sizes "
            "and long test durations."
        )
    elif proposal.minimum_detectable_effect > 0.5:
        warnings.append(
            "Large MDE detected. This may indicate unrealistic expectations "
            "for the test impact."
        )
    
    if proposal.baseline_conversion_rate < 0.01:
        warnings.append(
            "Very low baseline conversion rate. Consider if the metric is "
            "appropriate for testing."
        )
    
    if proposal.number_of_variations > 4:
        warnings.append(
            f"Testing {proposal.number_of_variations} variations may dilute "
            "traffic and reduce statistical power."
        )
    
    # Check if daily traffic is sufficient
    if samples_per_day > proposal.daily_traffic:
        warnings.append(
            f"Daily traffic ({proposal.daily_traffic}) is insufficient for "
            f"required sample rate ({samples_per_day} samples/day)."
        )
    
    return StatisticalAnalysis(
        required_sample_size=required_sample_size,
        estimated_duration_days=estimated_duration,
        samples_per_day_needed=samples_per_day,
        confidence_level=0.95,
        statistical_power=0.8,
        warnings=warnings
    )




