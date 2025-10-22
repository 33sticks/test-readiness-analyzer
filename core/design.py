"""
Test design validation and recommendations module.

This module validates test design elements including variation count,
traffic allocation, metric selection, and provides specific recommendations.
"""

from typing import List, Optional

from .models import TestProposal, DesignAnalysis


def validate_variation_count(number_of_variations: int) -> Optional[str]:
    """
    Validate the number of test variations.
    
    Args:
        number_of_variations: Number of test variations
    
    Returns:
        Warning message if issues found, None otherwise
    """
    if number_of_variations > 4:
        return (
            f"Testing {number_of_variations} variations may dilute traffic and "
            "reduce statistical power. Consider reducing to 2-3 variations for "
            "better results."
        )
    elif number_of_variations == 1:
        return (
            "Only 1 variation specified. Ensure you have a proper control group "
            "and treatment group for valid comparison."
        )
    
    return None


def validate_traffic_allocation(
    number_of_variations: int,
    daily_traffic: int,
    required_sample_size: int
) -> Optional[str]:
    """
    Validate traffic allocation feasibility.
    
    Args:
        number_of_variations: Number of test variations
        daily_traffic: Daily traffic volume
        required_sample_size: Required sample size per variation
    
    Returns:
        Warning message if issues found, None otherwise
    """
    # Calculate total samples needed
    total_samples_needed = required_sample_size * number_of_variations
    
    # Check if traffic is sufficient
    if total_samples_needed > daily_traffic * 30:  # 30-day minimum
        return (
            f"Insufficient traffic for {number_of_variations} variations. "
            f"Need {total_samples_needed} total samples but only have "
            f"{daily_traffic} daily traffic. Consider reducing variations "
            "or increasing traffic."
        )
    
    # Check traffic allocation per variation
    traffic_per_variation = daily_traffic // number_of_variations
    if traffic_per_variation < 100:  # Minimum 100 visitors per variation per day
        return (
            f"Traffic per variation ({traffic_per_variation}) may be too low "
            "for reliable results. Consider reducing variations or increasing traffic."
        )
    
    return None


def validate_metrics(primary_metric: str, secondary_metrics: Optional[List[str]]) -> List[str]:
    """
    Validate metric selection and provide warnings.
    
    Args:
        primary_metric: Primary success metric
        secondary_metrics: Secondary metrics to track
    
    Returns:
        List of metric-related warnings
    """
    warnings = []
    
    # Check primary metric
    primary_lower = primary_metric.lower()
    
    # High-variance metrics that may need larger sample sizes
    high_variance_metrics = [
        'revenue', 'average order value', 'aov', 'lifetime value', 'ltv',
        'time on site', 'session duration', 'bounce rate'
    ]
    
    if any(metric in primary_lower for metric in high_variance_metrics):
        warnings.append(
            f"Primary metric '{primary_metric}' has high variance. "
            "Consider increasing sample size or using a more stable metric."
        )
    
    # Check for appropriate metric types
    if 'click' in primary_lower and 'rate' not in primary_lower:
        warnings.append(
            "Consider using click-through rate instead of raw click counts "
            "for more meaningful comparison."
        )
    
    # Check secondary metrics
    if secondary_metrics:
        for metric in secondary_metrics:
            metric_lower = metric.lower()
            
            if any(high_var_metric in metric_lower for high_var_metric in high_variance_metrics):
                warnings.append(
                    f"Secondary metric '{metric}' has high variance. "
                    "Monitor closely and consider statistical significance carefully."
                )
        
        # Check for metric redundancy
        if len(secondary_metrics) > 5:
            warnings.append(
                f"Tracking {len(secondary_metrics)} secondary metrics may lead to "
                "multiple comparison issues. Focus on 2-3 key metrics."
            )
    
    return warnings


def generate_recommendations(
    proposal: TestProposal,
    variation_warning: Optional[str],
    traffic_warning: Optional[str],
    metric_warnings: List[str]
) -> List[str]:
    """
    Generate specific design recommendations.
    
    Args:
        proposal: TestProposal object
        variation_warning: Variation count warning
        traffic_warning: Traffic allocation warning
        metric_warnings: Metric-related warnings
    
    Returns:
        List of specific recommendations
    """
    recommendations = []
    
    # Variation count recommendations
    if variation_warning:
        if proposal.number_of_variations > 4:
            recommendations.append(
                f"Reduce variations from {proposal.number_of_variations} to 2-3 "
                "for better statistical power and faster results."
            )
        elif proposal.number_of_variations == 1:
            recommendations.append(
                "Ensure you have both a control and treatment group. "
                "Single variation tests are not recommended."
            )
    
    # Traffic allocation recommendations
    if traffic_warning:
        if "Insufficient traffic" in traffic_warning:
            recommendations.append(
                "Consider running a smaller test first or increasing traffic "
                "through marketing channels before launching the full test."
            )
        elif "Traffic per variation" in traffic_warning:
            recommendations.append(
                "Increase daily traffic or reduce the number of variations "
                "to ensure adequate sample size per variation."
            )
    
    # Metric recommendations
    if metric_warnings:
        high_variance_found = any("high variance" in warning for warning in metric_warnings)
        if high_variance_found:
            recommendations.append(
                "Consider using more stable metrics like conversion rates "
                "instead of revenue-based metrics for initial testing."
            )
        
        if len(proposal.secondary_metrics or []) > 5:
            recommendations.append(
                "Focus on 2-3 key secondary metrics to avoid multiple "
                "comparison issues and maintain statistical rigor."
            )
    
    # General recommendations based on test parameters
    if proposal.minimum_detectable_effect < 0.05:
        recommendations.append(
            "Small MDE detected. Consider if this level of change is "
            "practically significant for your business goals."
        )
    
    if proposal.baseline_conversion_rate < 0.02:
        recommendations.append(
            "Low baseline conversion rate. Ensure the metric is appropriate "
            "for your traffic volume and consider using a more common metric."
        )
    
    # Add general best practices
    recommendations.extend([
        "Ensure proper randomization and avoid selection bias in traffic allocation.",
        "Set up proper tracking and analytics before test launch.",
        "Define success criteria and stopping rules before starting the test.",
        "Plan for post-test analysis and implementation of winning variations."
    ])
    
    return recommendations


def validate_design(proposal: TestProposal, required_sample_size: int) -> DesignAnalysis:
    """
    Perform comprehensive design validation.
    
    Args:
        proposal: TestProposal object
        required_sample_size: Required sample size per variation
    
    Returns:
        DesignAnalysis object with validation results
    """
    # Validate variation count
    variation_warning = validate_variation_count(proposal.number_of_variations)
    
    # Validate traffic allocation
    traffic_warning = validate_traffic_allocation(
        number_of_variations=proposal.number_of_variations,
        daily_traffic=proposal.daily_traffic,
        required_sample_size=required_sample_size
    )
    
    # Validate metrics
    metric_warnings = validate_metrics(
        primary_metric=proposal.primary_metric,
        secondary_metrics=proposal.secondary_metrics
    )
    
    # Generate recommendations
    recommendations = generate_recommendations(
        proposal=proposal,
        variation_warning=variation_warning,
        traffic_warning=traffic_warning,
        metric_warnings=metric_warnings
    )
    
    return DesignAnalysis(
        variation_count_warning=variation_warning,
        traffic_allocation_warning=traffic_warning,
        metric_warnings=metric_warnings,
        recommendations=recommendations
    )




