PID Controller Design for Automated Drug Infusion

This repository contains the code and report for the BM2000 Control Systems project on PID controller design for a simplified automated drug infusion system.

Contents
	•	main.py — Python implementation used for PID grid search and performance evaluation
	•	report — Final project report describing the model, approach, results, and Simulink validation

Project Overview

The biomedical system was modeled as two cascaded first-order processes:

\dot{c}(t)=\frac{1}{\tau_1}(u(t)-c(t)), \qquad
\dot{y}(t)=\frac{1}{\tau_2}(c(t)-y(t))

which gives the plant transfer function:

G(s)=\frac{1}{(\tau_1 s+1)(\tau_2 s+1)}

For the main study, the parameters were chosen as:

\tau_1=\tau_2=5

to represent slower and more realistic physiological dynamics.

A standard PID controller was used:

C(s)=K_p+\frac{K_i}{s}+K_d s

The design goals were:
	•	minimal steady-state error
	•	overshoot below 5%
	•	settling time below 2 minutes
	•	robustness to actuator and sensor noise

Method

The main code performs an exhaustive grid search over PID gains and evaluates each candidate using:
	•	steady-state error
	•	overshoot
	•	rise time
	•	settling time

A penalty-based score function was used to prioritize controllers that satisfy the design constraints.

After the grid-search result was obtained, the controller was tested in Simulink with:
	•	actuator noise added before the plant
	•	sensor noise added in the feedback path

Further manual refinement was then performed based on the noisy response.

Key Result

A valid noise-free solution was obtained during the search, and the final practical gains selected after refinement were:

K_p = 23.5,\qquad K_i = 1.5,\qquad K_d = 45.5

These gains gave:
	•	negligible steady-state error
	•	overshoot within the 5% limit
	•	fast tracking response
	•	good robustness under small noise

Notes
	•	The report contains the detailed derivation, search strategy, score function, Simulink model discussion, and final conclusions.
	•	The code and report should be read together for full context.

Authors
	•	Aaryan Chaudhari — BM24BTECH11002
	•	Dvimidh Sule — BM24BTECH11008
