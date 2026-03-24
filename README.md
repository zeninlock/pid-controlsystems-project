# PID Controller Design for Automated Drug Infusion

BM2000 Control Systems project on PID controller design for a simplified biomedical drug infusion system.

## Authors

- **Aaryan Chaudhari** — BM24BTECH11002  
- **Dvimidh Sule** — BM24BTECH11008  

## Repository Contents

- **`main.py`** — Python code for PID grid search and performance evaluation  
- **`report`** — Final project report with derivation, methodology, results, and Simulink validation  

## Project Overview

The biomedical system was modeled as two cascaded first-order processes:

- c_dot(t) = (1/tau1) * (u(t) - c(t))
- y_dot(t) = (1/tau2) * (c(t) - y(t))

This gives the plant transfer function:

**G(s) = 1 / ((tau1*s + 1)(tau2*s + 1))**

For the main study, the parameters were chosen as:

**tau1 = tau2 = 5**

to represent slower and more realistic physiological dynamics than the initially tested smaller values.

A standard PID controller was used:

**C(s) = Kp + Ki/s + Kd*s**

## Design Goals

The controller was required to satisfy the following:

- minimal steady-state error  
- overshoot below **5%**  
- settling time below **2 minutes**  
- robustness to actuator and sensor noise  

## Methodology

The main Python code performs an exhaustive grid search over PID gains and evaluates each candidate using:

- steady-state error  
- overshoot  
- rise time  
- settling time  

A penalty-based score function was used to prioritize controllers that satisfy the design constraints.

### Grid Search Setup

- Kp, Ki, Kd in [0, 50]
- step size = 0.5

This resulted in a very large search space and allowed a systematic exploration of feasible PID parameters.

## Key Results

A valid noise-free solution obtained during the search was:

- **Kp = 20**
- **Ki = 1.5**
- **Kd = 45.5**

with:

- Final value = **1.0000**
- Steady-state error = **0.0000**
- Overshoot = **0.00%**
- Settling time = **1.9510 min**

After Simulink validation and manual refinement under small actuator and sensor noise, the final practical gains selected were:

- **Kp = 23.5**
- **Ki = 1.5**
- **Kd = 45.5**

These gains gave:

- negligible steady-state error  
- overshoot within the **5%** limit  
- fast response  
- good robustness under noise  

## Simulink Validation

The controller was further tested in Simulink using the biomedical feedback block diagram with:

- actuator noise added before the plant  
- sensor noise added in the feedback path  

Noise power was kept small to study robustness while preserving the main closed-loop behavior.

## Notes

- The Python code and report are intended to be read together.  
- The report contains the full derivation, scoring logic, search approach, Simulink model discussion, and final conclusions.  
- A small implementation detail encountered during testing was that the Simulink Step block initially had a nonzero step time, which artificially increased the measured settling time. This was later corrected.

## Summary

This project shows that combining:

- transfer-function modeling  
- exhaustive PID grid search  
- penalty-based performance scoring  
- Simulink-based noisy validation  
- manual refinement  

is an effective way to design a high-performance PID controller for a simplified biomedical drug infusion system.
