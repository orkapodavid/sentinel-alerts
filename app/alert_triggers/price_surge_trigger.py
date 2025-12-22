import random
from datetime import datetime
from app.alert_triggers import BaseTrigger
from app.models import AlertOutput


class PriceSurgeTrigger(BaseTrigger):
    def get_name(self) -> str:
        return "Price Surge Monitor"

    def get_description(self) -> str:
        return "Detects if a stock price exceeds a specific threshold."

    def get_default_params(self) -> dict:
        return {"ticker": "AAPL", "threshold": 150.0}

    async def check(self, params: dict) -> AlertOutput:
        ticker = params.get("ticker", "UNKNOWN")
        threshold = float(params.get("threshold", 100.0))
        current_price = threshold + random.uniform(-10, 20)
        triggered = current_price > threshold
        return AlertOutput(
            triggered=triggered,
            importance="high",
            ticker=ticker,
            message=f"Price Surge Alert: {ticker} is at {current_price:.2f} (Threshold: {threshold})",
            metadata={"current_price": current_price, "threshold": threshold},
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        )


if __name__ == "__main__":
    trigger = PriceSurgeTrigger()
    result = trigger.check(trigger.get_default_params())
    print(result.json())