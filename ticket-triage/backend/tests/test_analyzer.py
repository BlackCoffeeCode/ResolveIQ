from app.analyzer.ticket_analyzer import TicketAnalyzer


def test_billing_classification():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze(
        "My credit card was charged twice this month, I need a refund"
    )
    assert result["category"] == "Billing"


def test_technical_classification():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze(
        "The API endpoint keeps returning 500 error and crashes the app"
    )
    assert result["category"] == "Technical"


def test_account_classification():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze(
        "I cannot login to my account, password reset not working"
    )
    assert result["category"] == "Account"


def test_feature_request_classification():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze(
        "Would be nice to add dark mode support to the dashboard"
    )
    assert result["category"] == "Feature Request"


def test_security_classification():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze(
        "I think my account was hacked and there's unauthorized access"
    )
    assert result["category"] == "Security"


def test_other_classification():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze("Hello there")
    assert result["category"] == "Other"
    assert result["confidence_score"] == 0.1


def test_urgency_detection_true():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze("Need help asap, production down and customers affected")
    assert result["urgency"] is True


def test_urgency_detection_false():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze("I was wondering if you could look into this")
    assert result["urgency"] is False


def test_p0_priority():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze("Production is down completely, system outage right now")
    assert result["priority"] == "P0"


def test_p1_priority():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze("Urgent: users cannot access their accounts")
    assert result["priority"] == "P1"


def test_p3_priority():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze("No rush, just a suggestion for when you have time")
    assert result["priority"] == "P3"


def test_security_escalation_forces_p0():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze(
        "I found a SQL injection vulnerability in your login form"
    )
    assert result["priority"] == "P0"
    assert result["is_security_escalated"] is True


def test_security_escalation_forces_urgency():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze(
        "Possible data leak and unauthorized token exposed in logs"
    )
    assert result["urgency"] is True


def test_confidence_score_range():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze(
        "My invoice failed and payment charge appears twice on subscription"
    )
    assert 0.0 <= result["confidence_score"] <= 1.0


def test_keywords_extracted():
    analyzer = TicketAnalyzer()
    result = analyzer.analyze(
        "Billing issue: charged twice and refund needed for invoice"
    )
    assert result["keywords"]
    assert any(keyword in result["keywords"] for keyword in ["billing", "charged", "refund", "invoice"])
