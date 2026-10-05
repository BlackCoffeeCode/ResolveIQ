from app.config.keywords import (
    CATEGORY_KEYWORDS,
    CATEGORY_TIEBREAKER_ORDER,
    PRIORITY_BOOST_SIGNALS,
    URGENCY_KEYWORDS,
)


class TicketAnalyzer:
    def _find_matches(self, message_lower: str, keywords: list[str]) -> list[str]:
        return sorted({keyword for keyword in keywords if keyword in message_lower})

    def analyze(self, message: str) -> dict:
        message_lower = message.lower()
        signals: list[str] = []

        category_matches: dict[str, list[str]] = {
            category: self._find_matches(message_lower, keywords)
            for category, keywords in CATEGORY_KEYWORDS.items()
        }

        scores = {category: len(matches) for category, matches in category_matches.items()}
        highest_score = max(scores.values()) if scores else 0

        if highest_score == 0:
            winning_category = "Other"
        else:
            contenders = [
                category
                for category, score in scores.items()
                if score == highest_score
            ]
            for candidate in CATEGORY_TIEBREAKER_ORDER:
                if candidate in contenders:
                    winning_category = candidate
                    break
            else:
                winning_category = contenders[0]

        for category, matches in category_matches.items():
            if matches:
                signals.append(
                    f"Matched {len(matches)} {category.lower()} keywords: {', '.join(matches)}"
                )

        urgency_matches = self._find_matches(message_lower, URGENCY_KEYWORDS)
        is_urgent = len(urgency_matches) > 0
        if is_urgent:
            signals.append(f"Urgency detected: {', '.join(urgency_matches)}")

        p0_matches = self._find_matches(message_lower, PRIORITY_BOOST_SIGNALS["P0"])
        p1_matches = self._find_matches(message_lower, PRIORITY_BOOST_SIGNALS["P1"])
        p2_matches = self._find_matches(message_lower, PRIORITY_BOOST_SIGNALS["P2"])
        p3_matches = self._find_matches(message_lower, PRIORITY_BOOST_SIGNALS["P3"])

        if p0_matches:
            priority = "P0"
            signals.append(f"P0 priority signal: {', '.join(p0_matches)}")
        elif p1_matches:
            priority = "P1"
            signals.append(f"P1 priority signal: {', '.join(p1_matches)}")
        elif is_urgent and not p2_matches:
            priority = "P1"
            signals.append("Urgency escalation applied: urgent ticket promoted to P1")
        elif p2_matches:
            priority = "P2"
            signals.append(f"P2 priority signal: {', '.join(p2_matches)}")
        elif p3_matches:
            priority = "P3"
            signals.append(f"P3 priority signal: {', '.join(p3_matches)}")
        else:
            priority = "P2"
            signals.append("Default priority applied: P2")

        security_matches = category_matches.get("Security", [])
        is_security_escalated = False
        if winning_category == "Security" or security_matches:
            priority = "P0"
            is_security_escalated = True
            is_urgent = True
            signals.append(
                "SECURITY ESCALATION: Ticket auto-escalated to P0 due to security keywords detected"
            )

        if winning_category == "Other":
            confidence_score = 0.1
        else:
            matched_count = len(category_matches.get(winning_category, []))
            max_possible = len(CATEGORY_KEYWORDS.get(winning_category, []))
            raw_confidence = (matched_count / max_possible) if max_possible else 0.0
            confidence_score = min(1.0, max(0.1, raw_confidence))

        confidence_score = round(confidence_score, 2)

        all_matched_keywords = set()
        for matches in category_matches.values():
            all_matched_keywords.update(matches)
        all_matched_keywords.update(urgency_matches)

        return {
            "category": winning_category,
            "priority": priority,
            "urgency": is_urgent,
            "confidence_score": confidence_score,
            "signals": signals,
            "keywords": sorted(all_matched_keywords),
            "is_security_escalated": is_security_escalated,
        }
