from app.domain.enums import RiskLevel


class RiskPolicy:
    LOW_THRESHOLD = 0.35
    HIGH_THRESHOLD = 0.8

    SUGGESTIONS = {
        RiskLevel.LOW: "No obvious forgery risk was found. Use the result as a reference only.",
        RiskLevel.MEDIUM: "The image has a moderate forgery risk. Review the source and context before trusting it.",
        RiskLevel.HIGH: "The image has a high forgery risk. Treat it cautiously in identity or fraud-sensitive scenarios.",
    }

    @classmethod
    def classify(cls, fake_probability: float) -> RiskLevel:
        if fake_probability < cls.LOW_THRESHOLD:
            return RiskLevel.LOW
        if fake_probability < cls.HIGH_THRESHOLD:
            return RiskLevel.MEDIUM
        return RiskLevel.HIGH

    @classmethod
    def suggestion_for(cls, risk_level: RiskLevel | str) -> str:
        return cls.SUGGESTIONS[RiskLevel(risk_level)]

