# Pillar-5-Capstone-Project
Pillar 5 - Capstone Project
AI-Driven Logistics Quoting & SLA Optimization

Created by: Jonathan Pimentel

Date: July 2026

For: Asian Institute of Management

Course: AI and ML

Short Description:
An end-to-end machine learning pipeline that dynamically optimizes international shipping quotes to protect Net Service Level (NSL) commitments, utilizing LightGBM, Isolation Forests, Survival Analysis, and Geographic Fairness Analysis.

Project Overview

Legacy static quoting matrices often fail to account for real-world network volatility, leading to missed Service Level Agreements (SLAs) and poor customer experiences. This capstone project solves this by replacing rigid static quotes with a dynamic, multi-model AI architecture designed to forecast transit times and detect high-risk network bottlenecks before a package is even shipped.

Key Features & Pipeline

Unsupervised Risk Profiling: Utilizes K-Means clustering to automatically group international postal codes into behavioral risk profiles (e.g., "Golden Lanes" vs. "Chronic Bottlenecks").

Advanced Multi-Model Predictions: Replaces standard average-based forecasting with three distinct algorithms:

LightGBM (Quantile Regression): Calculates realistic median (P50) and conservative (P90) confidence intervals.

Isolation Forest: Acts as an anomaly detection radar to flag statistically "weird" shipments for massive safety buffers.

Weibull AFT (Survival Analysis): Models logistics as a "time-to-event" problem, calculating the exact probability of a successful delivery over time.

Bias & Fairness Analysis: Stratifies model evaluation across varying geographic regions (e.g., urban vs. rural postal codes) and volume tiers. This ensures the AI does not systematically discriminate against developing or low-volume international lanes by unfairly inflating their transit quotes due to historical data scarcity.

Business Logic & Simulation: Pits the AI models against historical baseline data to simulate real-world Net Service Level (NSL) improvements, validated through rigorous Time-Series Cross-Validation.

Business Impact: The system automatically prescribes targeted transit buffers (e.g., adding +2 days to specific high-variance zip codes on Fridays), maximizing on-time delivery compliance and ensuring equitable quoting without unnecessarily inflating transit times across the broader, stable network.
