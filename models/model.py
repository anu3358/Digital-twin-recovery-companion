import os
import random
from .torch_model import predict as torch_predict

class TwinModel:
    def __init__(self):
        self.weights = os.path.join(os.path.dirname(__file__), "weights.pth")

    def predict(self, patient_id: int, scenario: dict, feats: dict | None = None):
        # Combine features + scenario for torch model
        features = feats.copy() if feats else {}
        features["extra_minutes_balance"] = float(scenario.get("extra_minutes_balance", 0))
        try:
            res = torch_predict(features, weights_path=self.weights)
            return res
        except Exception:
            # fallback: heuristic
            base = random.uniform(0.2, 0.8)
            effect = 0.02 * float(scenario.get("extra_minutes_balance", 0))
            gait_change = round((base * 50) + (effect * 100), 2)
            return {
                "gait_speed_change_pct": gait_change,
                "adherence_score": round(base * 100, 1),
            }
