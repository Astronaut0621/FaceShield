from app.domain.enums import RiskLevel


class RiskPolicy:
    LOW_THRESHOLD = 0.35
    HIGH_THRESHOLD = 0.8

    SUGGESTIONS = {
        RiskLevel.LOW: "未发现明显伪造风险，仅供参考。",
        RiskLevel.MEDIUM: "该图片存在中等伪造风险，请核实来源与上下文后再采信。",
        RiskLevel.HIGH: "该图片存在较高伪造风险，在身份核验或涉诈场景中请谨慎处理。",
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

