import control as ctrl
import numpy as np
import matplotlib.pyplot as plt

PRINT_EVERY = 50  
tau1 = 5.0
tau2 = 5.0
G = ctrl.TransferFunction([1], np.polymul([tau1, 1], [tau2, 1]))

#helper functions
def make_pid(Kp, Ki, Kd):
    return ctrl.TransferFunction([Kd, Kp, Ki], [1, 0])

def step_info(t, y, ref=1.0, settling_band=0.02):
    y_final_est = y[-1]
    ess = abs(ref - y_final_est)
    overshoot = max(0.0, (np.max(y) - ref) / abs(ref) * 100.0)
    t10 = np.nan
    t90 = np.nan
    for i in range(len(y)):
        if np.isnan(t10) and y[i] >= 0.1 * ref:
            t10 = t[i]
        if np.isnan(t90) and y[i] >= 0.9 * ref:
            t90 = t[i]
            break
    rise_time = t90 - t10 if not (np.isnan(t10) or np.isnan(t90)) else np.nan
    settling_time = np.nan
    band = settling_band * abs(ref)
    for i in range(len(y)):
        if np.all(np.abs(y[i:] - ref) <= band):
            settling_time = t[i]
            break

    peak_value = np.max(y)
    peak_time = t[np.argmax(y)]

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
    print(f"Peak Value           = {info['peak_value']:.4f}")
    print(f"Peak Time            = {info['peak_time']:.4f}")

#score function
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

t = np.linspace(0, 100, 2000)

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
                    print_metrics(
                        "Current Best",
                        best_candidate[0],
                        best_candidate[1],
                        best_candidate[2],
                        best_info
                    )

            except Exception:
                continue

print("FINAL BEST CANDIDATE FROM FULL GRID SEARCH")

if best_candidate is not None:
    Kp_best, Ki_best, Kd_best = best_candidate
    print_metrics("Final Best Candidate", Kp_best, Ki_best, Kd_best, best_info)
else:
    print("No valid candidate found.")

print("\nProgram finished.")
