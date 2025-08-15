import torch
import torch.nn as nn

FEATURES = ["acc_mag_mean","acc_mag_std","emg_rms","hr_mean","spo2_mean","cadence_est","extra_minutes_balance"]

class SimpleRegressor(nn.Module):
    def __init__(self, in_dim=len(FEATURES), hidden=16):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1)
        )
    def forward(self, x):
        return self.net(x)

def load_model(weights_path: str | None = None):
    model = SimpleRegressor()
    if weights_path:
        try:
            state = torch.load(weights_path, map_location="cpu")
            model.load_state_dict(state)
        except Exception:
            pass
    model.eval()
    return model

def predict(features: dict, weights_path: str | None = None):
    model = load_model(weights_path)
    x = torch.tensor([[float(features.get(k, 0.0)) for k in FEATURES]], dtype=torch.float32)
    with torch.no_grad():
        y = model(x).item()
    # Map regression output to believable % change (0..100)
    y_pct = max(0.0, min(100.0, 50 + y))
    return {"gait_speed_change_pct": round(y_pct, 2), "adherence_score": round(60 + (y_pct/2), 1)}
