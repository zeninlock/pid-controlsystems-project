import numpy as np
import matplotlib.pyplot as plt
import control as ct



s = ct.TransferFunction.s

G_fast = 1 / ((1 * s + 1) * (2 * s + 1))
C_gentle = 9.0 + 4.0/s + 5.0*s
T_fast_gentle = ct.feedback(C_gentle * G_fast, 1)

G_slow = 1 / ((5 * s + 1) * (5 * s + 1))

T_slow_gentle = ct.feedback(C_gentle * G_slow, 1)

C_aggressive = 23.5 + 1.5/s + 45.5*s
T_slow_aggressive = ct.feedback(C_aggressive * G_slow, 1)

time = np.linspace(0, 10, 1000)
_, y_fast_gentle = ct.step_response(T_fast_gentle, T=time)
_, y_slow_gentle = ct.step_response(T_slow_gentle, T=time)
_, y_slow_aggressive = ct.step_response(T_slow_aggressive, T=time)

fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(time, y_fast_gentle, label='Fast Plant + Gentle PID (Original)', color='#4dc9f6', linestyle='--', linewidth=2)
ax.plot(time, y_slow_gentle, label='Slow Plant + Gentle PID (Fails Deadline)', color='#ff3333', linewidth=2.5)
ax.plot(time, y_slow_aggressive, label='Slow Plant + Aggressive PID (Grid Search)', color='#33cc33', linewidth=2.5)

ax.axhline(1.0, color='white', linewidth=1.5, label='Target (1.0)')
ax.axhline(1.05, color='#ffcc00', linestyle=':', linewidth=2, label='5% Overshoot Limit')
ax.axhline(1.02, color='#00ffcc', linestyle=':', linewidth=1.5, label='2% Error Band')
ax.axhline(0.98, color='#00ffcc', linestyle=':', linewidth=1.5)

ax.axvline(2.0, color='#cc33ff', linestyle=':', linewidth=2, label='2 Min Deadline')

ax.set_title('Plant Dynamics Shift: Fast vs. Slow Physiological Response', fontsize=14, fontweight='bold', color='white')
ax.set_xlabel('Time (minutes)', fontsize=12, color='white')
ax.set_ylabel('Biological Effect y(t)', fontsize=12, color='white')

legend = ax.legend(loc='lower right', facecolor='black', edgecolor='gray', fontsize=10)
for text in legend.get_texts():
    text.set_color("white")

ax.grid(True, linestyle='--', alpha=0.3, color='gray')
plt.tight_layout()
plt.show()
