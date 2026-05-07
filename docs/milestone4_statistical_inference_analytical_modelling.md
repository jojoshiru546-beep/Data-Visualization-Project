# MILESTONE 4 : STATISTICAL INFERENCE AND ANALYTICAL REPORTING.
#### Failur Log and Reflection Documentation.

## Section 1: Statistical Test Failures

**1.Which statistical test(s) did you run in M4?**

- Pair 1 run an Ordinary Least Squares (OLS) Regression to test the relationship between Tear and Mortality Rate%.
- Pair 3  run an independent samples Welch T-test (scipy.stats.ttest_ind with equal_var=False) comparing Mortality Rate % between the top-10 highest mortality countries and the bottom-10 lowest mortality countries.
- Cohen's d was computed as a secondary effect size measure. 

**2. Were any of them not statistically significant (high p-value / p > 0.05)?**

- Yes. The F- statistic p-value of 0.5449 was greater than 0.05.
- The model e xplicitly stated : "Trend is NOT significant (p > 0.05)
- The T-test was statistically significant because it returned p = 0.000124

**Which visual insight from M3 did your M4 p-value fail to support?**

- Pair 1 found that M3 visuals may have suggested a slight upward or downward drift due to year-to-year fluctuations. However, the p-value (0.5449) failed to support the idea that these fluctuations were part of a consistent, long-term linear trend.
The Visual pattern was noise, not a statistically meaningful pattern.
- Pair 3 found that none failed. Howerer, the Cohen's d effect size was negligible (d = 0.0077), meaning the bar chart gap in M3 Section 1 Chart B, while statistivally real, is practically tiny - only 0.0322 percentage points separating the two groups. The visual separation in the Bar Chart is misleading because the y-axis differences look larger than they actually are in absolute terms.

## Section 2: Regression Model Vs Visual Hypothesis

**4. What hypothesis from M3 did your M4 p-value fail to support?**

-  Pair 3: The chropleth and ranked bar chart in M3 Section 1 suggected that certain countries (Turkey, France, UK, Brazil, Germany) have meaningfully higher mortality rates than others(Russia, South Africa, Saudi Arabia, Italy, USA), implying geographic and possibly socioeconomic drivers of mortality differences.
- Pair 2: M3 Section 2  suggested a negative relationship between income/healthcare access and mortality (scatter plot cloud).

**5. Did your regression model agree or disagree with that hypothesis?  How?**
 
- Pair 2: Agreed partially: Regression confirmed negative coefficients for healthcare access and income, but `Hospital Beds per 1000` was insignificant (p > 0.05), disagreeing with visual emphasis on all healthcare metrics. 
- Pair 1: The regression model disagreed. While some country-level differences were visible in M3 visuals, the OLS regression Year vs Mortality Rate returned a non significant p-value (0.5449), indicating no statistically supported trend over time. \ The model provides bo evidence of a systematic tructural driver behind the visual patterns observed.

**6. If it disagreed - what do you think caused the mismatch?** 

The dataset has 1,000,000 records spread across 20 countries (~50,000 per country). With this sample size, even truvial numerical trends can appear visually significant on charts. The M3 bar chart axis y-axis was compressed making small differences appear large. The OLS model, however, found no meaningful linear signal - confirming visual patterns reflect random variation rather than a real world trend.

## Section 3: Model Performance

**7. What was your model's R-squared value?**
- Train R^2 = 0.0378, Test R^2 = 0.0381 (From Section 7 results.)

**8. Do you feel it was high enough to be trusted? Why or why not?**
- No. A test R^2 of 0.038 means the model explains only 3.8% of the variance on mortality rate. This is flagged as unreliable. It suggests that the features used - including Year, Income, Healthcare access,  Doctors per 1000, etc.- are not strong linear predictors of mortality in this dataset. This is consistent ewith the non-significant p-value(0.5449) found in the OLS regression test.

## Section 4: Feature Engineering Review

**9. What feature(s) did you engineer in M2?**

- 11 new features were engineered based on time, including: Decade, Mortality_YoY_Change, Severity_Index, DALY_Intesity, Weighted_Time_Impact,Disease_Category_Encoded, among others.
- Pair 3's visual work in M3 directly used Severity_Index (Mortality Rate / Prevalence Rate)as a bar annotation in Chart B, and Disease_Category_Encoded was used in M4 modelling as a predictor.

**10. After M4 modellind, did any feature turn out to add no predictive value?**

- Yes. Since the overall model has such low predictive poer (R^2 = 0.038), Year - and by extension, Decade- turned out to have very little predictive value as a standalone linear predictor for mortality rate. DALY_Intensity similarly showed no meaningful predictive lift.

**11. Would you recommend dropping any feature before M5/M6? Which one and why?**

- Yes. Year should be dropped as a standalone linear predictor. While it provides chronological context, it adds no predictive signal given the flat trend and non-significant F-Test. Instead, the focus should shift to Severity_Index, which likely has a stronger correlation with actual changes in mortality rates. 
- Weighted_Time_Impact should also be reviewed, as the dataset's short year range(2000-2024) limits the differentiation it adds.

## Section 5: Recommedations for M5/M6

**12. What is one thing your team thinks should be revisited before final reporting?**

- The y-axis scaling on M3 Section 1 Chart B. The bar chart visually implies large country-level differences in mortality, but the actual range  is approximately 0.044 percentage points (5.031% to 5.075%). Any report or dashboard that uses this chart without a note about the compressed scale risks misleading the audience into thinking the differences are clinically significant when they are not.

**13. Any findings that could be misleading if reported without context?**

- Yes, two key findings require contextualization:
 > 1. The OLS regression non-significat result (p = 0.5449) should be reported alongside the visual trend charts from M3 to make clear that year-to-year fluctuations are not a reliable indicator of any real-world mortality trend.
 > 2. The choropleth in M3 Chart A uses a sequential colour scale (YIOrRd) which visually implies Turkey is dramatically worse that Russia, but the actual difference is ~0.044%. The colour gradient amplifies a difference that is statistically real but practically irrelevant.
 >**A contextual note must accompany this chart in M5/M6 reporting.**

| # | What Failed / Was Statistically Insignificant | M3 Section | M4 Section | Reason | Action |
|---|-----------------------------------------------|------------|------------|--------|--------|
| 1 | OLS Regression: Year vs. Mortality Rate — trend not statistically significant | Section 1 | Section 5 | F-statistic p-value = 0.5449 > 0.05; trend NOT significant | Do not report year-on-year fluctuations as a meaningful trend; flag M3 charts with a contextual note |
| 2 | Regression feature 'Hospital Beds per 1000' — not significant | Section 2 | Section 6 | p-value > 0.05; not significant at 95% level | Drop this feature from the final model; focus on significant predictors like Healthcare Access |
| 3 | Test R-squared < 0.5 — model underperforms | Section 4 | Section 7 | Model underperforms on unseen data (Test R² = 0.038) | Flag M3 insight as unreliable; retrain model with additional features or data preprocessing |
| 4 | Engineered feature 'Year' / 'Weighted_Time_Impact' — no predictive value | Section 3 | Section 8 | Low correlation with target; adds no predictive value as a linear predictor | Recommend dropping before M5/M6; revisit feature engineering in M2 — focus on Severity_Index instead |