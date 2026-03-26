import control as ctrl
import numpy as np

PRINT_EVERY = 1000  
tau1 = 5.0
tau2 = 5.0
G = ctrl.TransferFunction([1], np.polymul([tau1, 1], [tau2, 1]))

def make_pid(Kp, Ki, Kd):
    return ctrl.TransferFunction([Kd, Kp, Ki], [1, 0])

def step_info(t, y, ref=1.0, settling_band=0.02):
    y_final_est = y[-1]
    ess = abs(ref - y_final_est)
    
    peak_idx = np.argmax(y)
    peak_value = y[peak_idx]
    peak_time = t[peak_idx]
    overshoot = max(0.0, (peak_value - ref) / abs(ref) * 100.0)
    
    idx_10 = np.argmax(y >= 0.1 * ref)
    idx_90 = np.argmax(y >= 0.9 * ref)
    rise_time = t[idx_90] - t[idx_10] if y[idx_90] >= 0.9 * ref else np.nan
    
    band = settling_band * abs(ref)
    outside_band_indices = np.where(np.abs(y - ref) > band)[0]
    
    if len(outside_band_indices) > 0:
        last_outside_idx = outside_band_indices[-1]
        if last_outside_idx + 1 < len(t):
            settling_time = t[last_outside_idx + 1]
        else:
            settling_time = np.nan 
    else:
        settling_time = t[0]

    return {
        "final_value": y_final_est,
        "steady_state_error": ess,
        "overshoot_percent": overshoot,
        "rise_time": rise_time,
        "settling_time": settling_time,
        "peak_value": peak_value,
        "peak_time": peak_time
    }

def print_metrics(iteration_name, Kp, Ki, Kd, info):
    print(f"\n--- {iteration_name} ---")
    print(f"Kp = {Kp:.4f}, Ki = {Ki:.4f}, Kd = {Kd:.4f}")
    print(f"Final Value          = {info['final_value']:.4f}")
    print(f"Steady-State Error   = {info['steady_state_error']:.4f}")
    print(f"Overshoot (%)        = {info['overshoot_percent']:.2f}")
    print(f"Rise Time            = {info['rise_time']:.4f}")
    print(f"Settling Time (2%)   = {info['settling_time']:.4f}")

def compute_score(info):
    overshoot = info["overshoot_percent"]
    settling_time = info["settling_time"]
    ess = info["steady_state_error"]

    if np.isnan(overshoot) or np.isnan(settling_time):
        return np.inf

    overshoot_penalty = max(0, overshoot - 5.0)
    settling_penalty = max(0, settling_time - 2.0)

    score = (
        1000 * overshoot_penalty +
        1000 * settling_penalty +
        100 * ess +
        overshoot +
        settling_time
    )
    return score

t = np.linspace(0, 10, 500)

kp_values = np.arange(0, 50.0 + 0.5, 0.5)
ki_values = np.arange(0, 50.0 + 0.5, 0.5)
kd_values = np.arange(0, 50.0 + 0.5, 0.5)

total_iterations = len(kp_values) * len(ki_values) * len(kd_values)
print(f"Total combinations to check = {total_iterations}")

best_candidate = None
best_info = None
best_score = np.inf

iteration_count = 0

for Kp in kp_values:
    for Ki in ki_values:
        for Kd in kd_values:
            iteration_count += 1

            C = make_pid(Kp, Ki, Kd)
            T = ctrl.feedback(C * G, 1)

            try:
                t_out, y_out = ctrl.step_response(T, t)
                if np.any(np.isnan(y_out)) or np.any(np.isinf(y_out)):
                    continue
                if np.max(np.abs(y_out)) > 1e6:
                    continue

                info = step_info(t_out, y_out)
                score = compute_score(info)

                if score < best_score:
                    best_score = score
                    best_candidate = (Kp, Ki, Kd)
                    best_info = info

                if iteration_count % PRINT_EVERY == 0 and best_candidate is not None:
                    print(f"BEST SO FAR AT ITERATION {iteration_count}/{total_iterations}")
                    print_metrics("Current Best", best_candidate[0], best_candidate[1], best_candidate[2], best_info)

            except Exception:
                continue

print("\nFINAL BEST CANDIDATE FROM FULL GRID SEARCH")
if best_candidate is not None:
    Kp_best, Ki_best, Kd_best = best_candidate
    print_metrics("Final Best Candidate", Kp_best, Ki_best, Kd_best, best_info)
else:
    print("No valid candidate found.")

print("\nProgram finished.")
