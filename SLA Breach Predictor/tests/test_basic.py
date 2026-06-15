"""
Basic tests for SLA Breach Predictor
"""

import pytest
from src.processor import process_tickets
from src.utils import calculate_risk_score


def test_calculate_risk_score():
    """Test risk score calculation"""
    # Test high priority ticket
    ticket = {
        "priority": "high",
        "time_remaining": 2
    }
    score = calculate_risk_score(ticket)
    assert score > 0.7  # High risk
    
    # Test low priority ticket
    ticket = {
        "priority": "low",
        "time_remaining": 48
    }
    score = calculate_risk_score(ticket)
    assert score < 0.3  # Low risk


def test_process_tickets():
    """Test ticket processing"""
    sample_data = [
        {"ticket_id": "T001", "priority": "high", "sla_deadline": "2024-01-15T17:00:00Z"}
    ]
    result = process_tickets(sample_data)
    assert len(result) > 0
    assert "risk_score" in result[0]


if __name__ == "__main__":
    pytest.main([__file__])
