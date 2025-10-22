"""
Hypothesis quality scoring and validation module.

This module evaluates hypothesis quality based on specificity, measurability,
directionality, and rationale, providing actionable feedback for improvement.
"""

import re
from typing import List, Tuple

from .models import TestProposal, HypothesisScore


def check_specificity(hypothesis: str) -> Tuple[float, List[str]]:
    """
    Check hypothesis specificity - identifies what is changing.
    
    Args:
        hypothesis: The hypothesis text
    
    Returns:
        Tuple of (score, feedback)
    """
    score = 0.0
    feedback = []
    
    # Check for specific elements
    hypothesis_lower = hypothesis.lower()
    
    # Look for specific UI elements
    ui_elements = [
        'button', 'form', 'header', 'footer', 'navigation', 'menu', 'link',
        'image', 'text', 'title', 'subtitle', 'call-to-action', 'cta',
        'checkout', 'cart', 'product', 'pricing', 'signup', 'login'
    ]
    
    ui_found = sum(1 for element in ui_elements if element in hypothesis_lower)
    if ui_found > 0:
        score += 1.0
        feedback.append(f"✓ Identifies specific UI elements ({ui_found} found)")
    else:
        feedback.append("✗ No specific UI elements mentioned")
    
    # Look for specific actions
    action_words = [
        'click', 'submit', 'purchase', 'sign up', 'register', 'download',
        'subscribe', 'complete', 'finish', 'proceed', 'continue'
    ]
    
    actions_found = sum(1 for action in action_words if action in hypothesis_lower)
    if actions_found > 0:
        score += 1.0
        feedback.append(f"✓ Identifies specific user actions ({actions_found} found)")
    else:
        feedback.append("✗ No specific user actions mentioned")
    
    # Look for specific metrics or outcomes
    metric_words = [
        'conversion', 'click-through', 'engagement', 'time', 'revenue',
        'signups', 'purchases', 'downloads', 'registrations'
    ]
    
    metrics_found = sum(1 for metric in metric_words if metric in hypothesis_lower)
    if metrics_found > 0:
        score += 0.5
        feedback.append(f"✓ Mentions specific metrics ({metrics_found} found)")
    else:
        feedback.append("✗ No specific metrics mentioned")
    
    return min(score, 2.5), feedback


def check_measurability(hypothesis: str) -> Tuple[float, List[str]]:
    """
    Check hypothesis measurability - mentions clear metrics.
    
    Args:
        hypothesis: The hypothesis text
    
    Returns:
        Tuple of (score, feedback)
    """
    score = 0.0
    feedback = []
    
    hypothesis_lower = hypothesis.lower()
    
    # Look for quantitative metrics
    quantitative_metrics = [
        'rate', 'percentage', '%', 'ratio', 'count', 'number', 'total',
        'average', 'mean', 'median', 'conversion rate', 'click rate',
        'engagement rate', 'bounce rate', 'completion rate'
    ]
    
    quant_found = sum(1 for metric in quantitative_metrics if metric in hypothesis_lower)
    if quant_found > 0:
        score += 1.5
        feedback.append(f"✓ Uses quantitative metrics ({quant_found} found)")
    else:
        feedback.append("✗ No quantitative metrics mentioned")
    
    # Look for specific measurement tools or methods
    measurement_terms = [
        'track', 'measure', 'analytics', 'data', 'metric', 'kpi',
        'conversion tracking', 'event tracking', 'funnel'
    ]
    
    measurement_found = sum(1 for term in measurement_terms if term in hypothesis_lower)
    if measurement_found > 0:
        score += 1.0
        feedback.append(f"✓ Mentions measurement approach ({measurement_found} found)")
    else:
        feedback.append("✗ No measurement approach mentioned")
    
    return min(score, 2.5), feedback


def check_directionality(hypothesis: str) -> Tuple[float, List[str]]:
    """
    Check hypothesis directionality - predicts outcome direction.
    
    Args:
        hypothesis: The hypothesis text
    
    Returns:
        Tuple of (score, feedback)
    """
    score = 0.0
    feedback = []
    
    hypothesis_lower = hypothesis.lower()
    
    # Look for directional predictions
    positive_direction = [
        'increase', 'improve', 'boost', 'enhance', 'raise', 'lift',
        'higher', 'more', 'better', 'faster', 'easier'
    ]
    
    negative_direction = [
        'decrease', 'reduce', 'lower', 'less', 'fewer', 'minimize'
    ]
    
    pos_found = sum(1 for word in positive_direction if word in hypothesis_lower)
    neg_found = sum(1 for word in negative_direction if word in hypothesis_lower)
    
    if pos_found > 0 and neg_found == 0:
        score += 2.5
        feedback.append(f"✓ Predicts positive outcome ({pos_found} indicators)")
    elif neg_found > 0 and pos_found == 0:
        score += 2.5
        feedback.append(f"✓ Predicts negative outcome ({neg_found} indicators)")
    elif pos_found > 0 and neg_found > 0:
        score += 1.0
        feedback.append("⚠ Mixed directional predictions (may be confusing)")
    else:
        feedback.append("✗ No clear directional prediction")
    
    return min(score, 2.5), feedback


def check_rationale(hypothesis: str) -> Tuple[float, List[str]]:
    """
    Check hypothesis rationale - contains reasoning.
    
    Args:
        hypothesis: The hypothesis text
    
    Returns:
        Tuple of (score, feedback)
    """
    score = 0.0
    feedback = []
    
    hypothesis_lower = hypothesis.lower()
    
    # Look for reasoning words
    reasoning_words = [
        'because', 'since', 'due to', 'as a result', 'therefore',
        'given that', 'considering', 'based on', 'according to'
    ]
    
    reasoning_found = sum(1 for word in reasoning_words if word in hypothesis_lower)
    if reasoning_found > 0:
        score += 1.5
        feedback.append(f"✓ Contains reasoning ({reasoning_found} indicators)")
    else:
        feedback.append("✗ No clear reasoning provided")
    
    # Look for supporting evidence or data
    evidence_words = [
        'data', 'research', 'study', 'analysis', 'findings', 'results',
        'evidence', 'insights', 'observations', 'feedback', 'user behavior'
    ]
    
    evidence_found = sum(1 for word in evidence_words if word in hypothesis_lower)
    if evidence_found > 0:
        score += 1.0
        feedback.append(f"✓ References supporting evidence ({evidence_found} found)")
    else:
        feedback.append("✗ No supporting evidence mentioned")
    
    return min(score, 2.5), feedback


def detect_vague_language(hypothesis: str) -> List[str]:
    """
    Detect vague language in hypothesis.
    
    Args:
        hypothesis: The hypothesis text
    
    Returns:
        List of vague words found
    """
    vague_words = [
        'improve', 'better', 'optimize', 'enhance', 'good', 'bad',
        'nice', 'great', 'awesome', 'terrible', 'amazing', 'wonderful'
    ]
    
    hypothesis_lower = hypothesis.lower()
    found_vague = [word for word in vague_words if word in hypothesis_lower]
    
    return found_vague


def generate_improved_hypothesis(hypothesis: str, feedback: List[str]) -> str:
    """
    Generate an improved hypothesis based on feedback.
    
    Args:
        hypothesis: Original hypothesis
        feedback: List of feedback items
    
    Returns:
        Improved hypothesis suggestion
    """
    improvements = []
    
    # Check for missing elements and suggest improvements
    if "No specific UI elements mentioned" in feedback:
        improvements.append("Specify which UI element you're testing (e.g., 'checkout button', 'signup form')")
    
    if "No specific user actions mentioned" in feedback:
        improvements.append("Specify the user action you expect to change (e.g., 'click rate', 'completion rate')")
    
    if "No quantitative metrics mentioned" in feedback:
        improvements.append("Include specific metrics (e.g., 'conversion rate', 'click-through rate')")
    
    if "No clear directional prediction" in feedback:
        improvements.append("State whether you expect an increase or decrease in the metric")
    
    if "No clear reasoning provided" in feedback:
        improvements.append("Add reasoning with 'because' to explain why you expect this change")
    
    # Check for vague language
    vague_words = detect_vague_language(hypothesis)
    if vague_words:
        improvements.append(f"Replace vague words like '{', '.join(vague_words)}' with specific, measurable terms")
    
    if improvements:
        return "Consider these improvements:\n" + "\n".join(f"• {improvement}" for improvement in improvements)
    
    return "Hypothesis is already well-structured. Consider adding more specific details if possible."


def score_hypothesis(proposal: TestProposal) -> HypothesisScore:
    """
    Score hypothesis quality across multiple dimensions.
    
    Args:
        proposal: TestProposal object containing the hypothesis
    
    Returns:
        HypothesisScore object with detailed scoring and feedback
    """
    hypothesis = proposal.hypothesis
    
    # Score each dimension
    specificity_score, specificity_feedback = check_specificity(hypothesis)
    measurability_score, measurability_feedback = check_measurability(hypothesis)
    directionality_score, directionality_feedback = check_directionality(hypothesis)
    rationale_score, rationale_feedback = check_rationale(hypothesis)
    
    # Calculate overall score
    overall_score = specificity_score + measurability_score + directionality_score + rationale_score
    
    # Combine all feedback
    all_feedback = []
    all_feedback.extend(specificity_feedback)
    all_feedback.extend(measurability_feedback)
    all_feedback.extend(directionality_feedback)
    all_feedback.extend(rationale_feedback)
    
    # Add vague language detection
    vague_words = detect_vague_language(hypothesis)
    if vague_words:
        all_feedback.append(f"⚠ Vague language detected: {', '.join(vague_words)}")
    
    # Generate improved hypothesis
    improved_hypothesis = generate_improved_hypothesis(hypothesis, all_feedback)
    
    return HypothesisScore(
        overall_score=overall_score,
        specificity_score=specificity_score,
        measurability_score=measurability_score,
        directionality_score=directionality_score,
        rationale_score=rationale_score,
        feedback=all_feedback,
        improved_hypothesis=improved_hypothesis
    )




