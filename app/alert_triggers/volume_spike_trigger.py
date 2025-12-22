import random
from datetime import datetime
from app.alert_triggers import BaseTrigger
from app.models import AlertOutput


class VolumeSpikeTrigger(BaseTrigger):
    def get_name(self) -> str:
        return "Volume Spike Monitor"

    def get_description(self) -> str:
        return "Detects unusual volume activity significantly above average."

    def get_default_params(self) -> dict:
        return {"ticker": "NVDA", "avg_volume": 1000000, "threshold_percent": 200}

    async def check(self, params: dict) -> AlertOutput:
        ticker = params.get("ticker", "UNKNOWN")
        avg_vol = float(params.get("avg_volume", 1000000))
        pct_thresh = float(params.get("threshold_percent", 200))
        factor = random.uniform(0.5, 3.5)
        current_vol = avg_vol * factor
        increase_pct = current_vol / avg_vol * 100
        triggered = increase_pct > pct_thresh
        return AlertOutput(
            triggered=triggered,
            importance="medium",
            ticker=ticker,
            message=f"Volume Spike: {ticker} volume is {int(current_vol):,} ({increase_pct:.1f}% of avg)",
            metadata={"current_volume": current_vol, "increase_pct": increase_pct},
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        )


if __name__ == "__main__":
    trigger = VolumeSpikeTrigger()
    result = trigger.check(trigger.get_default_params())
    print(result.json())