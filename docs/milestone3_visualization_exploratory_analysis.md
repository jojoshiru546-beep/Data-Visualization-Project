
 # Milestone 3 Documentation : Evolutionary failure  log
**Project: Public Health Data Visualization System**

**Dataset:Global Health Statistics (1,000,000 records × 22 columns)**

**Period:27th April - 4th May**

---

## Failure Log Table

| # | What Failed / Looked Misleading | Section | Reason / Hypothesis | Action in M4 |
|---|--------------------------------|---------|---------------------|----------------|
| 1 | The bar chart (Chart B) made country mortality differences look large – Turkey, France, UK appeared much worse than others. | M3 – Pair 1 (Trend & Map Specialists), Chart B | Y-axis was compressed (range 5.031%–5.075%), exaggerating a tiny absolute difference of 0.044%. | M4 Welch T-test + Cohen's d: p = 0.000124 but d = 0.0077 (negligible effect). Action: In M5/M6, rescale y-axis to zero or add annotation about actual range. |
| 2 | The choropleth map (Chart A) implied strong geographic/socioeconomic drivers of mortality – Turkey and UK appeared as "hotspots". | M3 – Pair 1, Chart A | Sequential colour scale (YlOrRd) amplifies small numeric differences into dramatic colour contrasts. | M4 regression showed R² = 0.038 → features explain almost no variance. Action: Add disclaimer in final report that colour scale exaggerates practically irrelevant differences. |
| 3 | The bar chart comparison between top-10 and bottom-10 mortality countries looked visually significant, but the actual gap was tiny. | M3 – Pair 3 (Design & Logic Validators), comparative chart | Visual separation in bar chart seemed large, but absolute difference was only 0.022 percentage points. | M4 found statistical significance (p=0.000124) but Cohen's d = 0.0077. Action: Never report p-value alone – always include effect size. |
| 4 | The engineered feature `Severity_Index` was used as a bar annotation, but added no real predictive value. | M3 – Annotations (from M2 features) | It looked informative visually, but its contribution to explaining mortality was negligible. | M4 regression R² = 0.038 confirmed low predictive power. Action: Review or drop `Severity_Index` before M5 dashboard. |
| 5 | The feature `Weighted_Time_Impact` was visually present but added no insight. | M3 – Any chart using time-based scaling | Derived from short time range (2000–2024) – scaling added no meaningful differentiation. | M4 recommends dropping `Weighted_Time_Impact` before M5 to avoid noise in dashboard filters. |
| 6 | The scatter plot of Per Capita Income vs. Healthcare Access (%) showed a strong positive correlation visually – points clustered along an upward slope. | M3 – Pair 2 (Core Relationships Team), scatter plot | Human eye naturally exaggerates patterns; a few high-income, high-access countries created an illusion of a strong trend. | M4 regression returned R² = 0.038 – only 3.8% of variance explained. Action: Always pair scatter plots with correlation coefficients or R² values in M5/M6 dashboards. |
| 7 | The scatter plot of Income vs. Mortality Rate suggested a clean negative linear relationship (higher income = lower mortality). | M3 – Pair 2, scatter plot | Visual appeared linear, but actual relationship was non-linear (diminishing returns: big mortality drops at low income, flat at high income). Residual plot later showed a curved pattern. | M4 regression residual analysis revealed non-linearity. Action: In M5/M6, add residual plots or use LOESS smoothing instead of assuming linearity. |
| 8 | The scatter plot implied a strong relationship between income and healthcare access. The insight written by Pair 4 claimed this as a meaningful pattern. | M3 – Pair 4 (Design Justification), based on Pair 2's scatter plot | M4 regression found that neither income nor healthcare access is a significant predictor of mortality. The visual correlation was not confirmed by statistical modeling. | In M4, note that this finding is descriptive only. Do not claim causal or predictive strength without proper testing. |
| 9 | The choropleth map was used to claim healthcare access inequality as a substantive geographic insight. | M3 – Pair 4 (Design Justification), based on Pair 1's choropleth map | M4 did not run any spatial hypothesis test (e.g., spatial autocorrelation or regional significance). The map is purely descriptive. | Add a separate spatial validation step in M4 (e.g., Moran's I or regional t‑tests), or clearly label the map as visual evidence only – not statistically confirmed. |
---

## Summary for Final Report

- **Key lesson:** Statistical significance (p < 0.05) does **not** equal practical importance. With large datasets, even trivial differences become “significant.”
- **M3 visual issues:** Compressed axes and sequential colour scales can mislead. Always check effect sizes (Cohen’s d, R²) before claiming a visual pattern is meaningful.
- **Action items for M5/M6:**
  - Add axis zero or annotation to bar chart.
  - Include Cohen’s d alongside any p‑value.
  - Drop `Weighted_Time_Impact` from dashboard filters.
  - Add a disclaimer on choropleth colour scaling.

**Non-negotiable rule satisfied:** This log documents what failed, why it failed, and the alternative solution (M4 statistical validation + recommended fixes).




