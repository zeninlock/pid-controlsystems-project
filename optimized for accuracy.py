#THIS IS JUST MESSING AROUND WITH OPTIMIZERS AND PUSHING THE LIMITS OF ACCURACY

import control as ctrl
import numpy as np
from scipy.optimize import differential_evolution, minimize

tau1 = 5.0
tau2 = 5.0
G = ctrl.TransferFunction([1], np.polymul([tau1, 1], [tau2, 1]))

T_END   = 30.0
N_PTS   = 3000
t_sim   = np.linspace(0, T_END, N_PTS)

def make_pid(Kp, Ki, Kd):
    return ctrl.TransferFunction([Kd, Kp, Ki], [1, 0])

def step_info(t, y, ref=1.0, band=0.02):
    y_ss  = y[-1]
    ess   = abs(ref - y_ss)

    peak_idx   = int(np.argmax(y))
    overshoot  = max(0.0, (y[peak_idx] - ref) / abs(ref) * 100.0)

    idx_10 = np.argmax(y >= 0.10 * ref)
    idx_90 = np.argmax(y >= 0.90 * ref)
    rise_time = (t[idx_90] - t[idx_10]
                 if (idx_90 > idx_10 and y[idx_90] >= 0.9 * ref)
                 else np.nan)

    tol = band * abs(ref)
    outside = np.where(np.abs(y - ref) > tol)[0]
    if len(outside) == 0:
        settling_time = t[0]          
    elif outside[-1] + 1 < len(t):
        settling_time = t[outside[-1] + 1]
    else:
        settling_time = np.nan        

    return dict(final_value=y_ss, ess=ess,
                overshoot=overshoot, rise_time=rise_time,
                settling_time=settling_time)

PENALTY_OVERSHOOT  = 1e7   
PENALTY_SETTLING   = 1e7   
WEIGHT_ESS         = 1e4   
WEIGHT_SETTLING    = 1.0   
WEIGHT_OVERSHOOT   = 0.5   

def compute_score(info):
    os_  = info["overshoot"]
    ts_  = info["settling_time"]
    ess_ = info["ess"]

    if np.isnan(os_) or np.isnan(ts_):
        return 1e12

    penalty = (PENALTY_OVERSHOOT * max(0, os_ - 5.0) ** 2
             + PENALTY_SETTLING  * max(0, ts_ - 2.0) ** 2)

    objective = (WEIGHT_ESS      * ess_
               + WEIGHT_SETTLING * ts_
               + WEIGHT_OVERSHOOT * os_)

    return penalty + objective

_DIVERGE_LIMIT = 1e6

def evaluate(params):
    Kp, Ki, Kd = params
    if Kp < 0 or Ki < 0 or Kd < 0:
        return 1e12
    try:
        C = make_pid(Kp, Ki, Kd)
        T = ctrl.feedback(C * G, 1)
        _, y = ctrl.step_response(T, t_sim)

        if (np.any(np.isnan(y)) or np.any(np.isinf(y))
                or np.max(np.abs(y)) > _DIVERGE_LIMIT):
            return 1e12

        return compute_score(step_info(t_sim, y))
    except Exception:
        return 1e12

BOUNDS = [(0, 200), (0, 50), (0, 150)]

print("=" * 60)
print("Stage 1 — Differential Evolution (global search)")
print("=" * 60)

de_result = differential_evolution(
    evaluate,
    BOUNDS,
    seed        = 42,
    strategy    = "best1bin",
    maxiter     = 2000,
    popsize     = 20,
    tol         = 1e-9,
    mutation    = (0.5, 1.5),
    recombination = 0.9,
    workers     = 1,
    polish      = False,      
    disp        = True,
)

print(f"\nDE best  -> Kp={de_result.x[0]:.6f}  Ki={de_result.x[1]:.6f}  Kd={de_result.x[2]:.6f}  score={de_result.fun:.6f}")

print("\n" + "=" * 60)
print("Stage 2 — Nelder-Mead local refinement (from DE best)")
print("=" * 60)

nm_result = minimize(
    evaluate,
    de_result.x,
    method  = "Nelder-Mead",
    options = {"xatol": 1e-10, "fatol": 1e-10, "maxiter": 50_000, "disp": True},
)

candidates = [de_result, nm_result]
print(f"\nNM best  -> Kp={nm_result.x[0]:.6f}  Ki={nm_result.x[1]:.6f}  Kd={nm_result.x[2]:.6f}  score={nm_result.fun:.6f}")

print("\n" + "=" * 60)
print("Stage 3 — Multi-start local search (10 random seeds)")
print("=" * 60)

rng = np.random.default_rng(0)
starts = np.column_stack([
    rng.uniform(lo, hi, 10) for (lo, hi) in BOUNDS
])

for i, x0 in enumerate(starts):
    r = minimize(evaluate, x0, method="Nelder-Mead",
                 options={"xatol": 1e-10, "fatol": 1e-10,
                          "maxiter": 30_000, "disp": False})
    candidates.append(r)
    print(f"  seed {i+1:2d}: score={r.fun:.6f}  Kp={r.x[0]:.4f}  Ki={r.x[1]:.4f}  Kd={r.x[2]:.4f}")

best = min(candidates, key=lambda r: r.fun)
Kp_best, Ki_best, Kd_best = best.x
Kp_best = max(0.0, Kp_best)
Ki_best = max(0.0, Ki_best)
Kd_best = max(0.0, Kd_best)

C_best = make_pid(Kp_best, Ki_best, Kd_best)
T_best = ctrl.feedback(C_best * G, 1)
_, y_best = ctrl.step_response(T_best, t_sim)
info_best = step_info(t_sim, y_best)

print("\n" + "=" * 60)
print("FINAL OPTIMAL PID CONTROLLER")
print("=" * 60)
print(f"  Kp = {Kp_best:.8f}")
print(f"  Ki = {Ki_best:.8f}")
print(f"  Kd = {Kd_best:.8f}")
print()
print("Performance metrics (2 % settling band, step reference = 1):")
print(f"  Final value        = {info_best['final_value']:.8f}")
print(f"  Steady-state error = {info_best['ess']:.2e}")
print(f"  Overshoot          = {info_best['overshoot']:.4f} %  (limit: 5 %)")
print(f"  Rise time          = {info_best['rise_time']:.4f}")
print(f"  Settling time (2%) = {info_best['settling_time']:.4f}  (limit: 2)")
print()

feasible = (info_best['overshoot'] <= 5.0
            and not np.isnan(info_best['settling_time'])
            and info_best['settling_time'] <= 2.0)
print(f"  Constraints met?   {'YES ✓' if feasible else 'NO — tighten bounds or penalties'}")

try:
    gm, pm, wgc, wpc = ctrl.margin(C_best * G)
    print()
    print("Robustness (open-loop margins):")
    print(f"  Gain margin   = {20*np.log10(gm):.2f} dB  (at {wgc:.4f} rad/s)")
    print(f"  Phase margin  = {pm:.2f} °  (at {wpc:.4f} rad/s)")
except Exception:
    pass

print("\nProgram finished.")
