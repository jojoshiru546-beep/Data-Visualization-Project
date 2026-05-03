# Milestone 2: Data Processing & Transformation

**Project:** Public Health Data Visualization System  
**Dataset:** Global Health Statistics (1,000,000 records × 22 columns)  
**Period:** April 20–27, 2026  
**Status:**  Complete  


## Executive Summary

Milestone 2 develops a robust, reproducible data processing pipeline that cleans, transforms, and engineers features from the raw dataset. The phase includes data quality auditing, cleaning operations, standardization, and feature engineering to prepare the dataset for analysis and visualization.


## 1. Project Setup

### Libraries Used

| Library | Purpose |
|---------|---------|
| `pandas` | Data loading, exploration, and manipulation |
| `numpy` | Numerical operations and array handling |
| `os` | Operating system interactions |
| `pathlib` | Cross-platform file path handling |

### Environment

- **Python Version:** 3.12.7
- **Virtual Environment:** `.venv`
- **IDE:** Visual Studio Code
- **Repository:** Feature branch `feature/milestone2-pipeline`


## 2. Data Loading Strategy

### File Path Resolution

The pipeline implements **reproducible, machine-independent file paths** using `pathlib.Path`:

```python
project_root = Path().resolve().parent if Path().resolve().name == 'notebooks' else Path().resolve()
data_path = project_root / "data" / "raw"
```

**Key Design Decision:** No hardcoded absolute paths (`C:\Users\...`). This ensures the code runs identically on any machine, regardless of installation location or OS (Windows/Mac/Linux).

### Data Loading Results

-  Dataset located: `data/raw/Global Health Statistics.csv`
-  Successfully loaded: **1,000,000 rows × 22 columns**
-  Format: CSV (Comma-Separated Values)
-  Accessible from all environments



## 3. Data Quality Audit

### Audit Methodology

A comprehensive quality audit was performed to assess data **structure**, **completeness**, and **reliability** before any transformation operations.

### Audit Checks Performed

| Check | Purpose | Findings |
|-------|---------|----------|
| **Shape** | Verify dataset dimensions and feature count | 1,000,000 rows × 22 columns confirmed |
| **Data Types** | Ensure correct storage types for numerical/categorical data |  No type issues detected |
| **Missing Values** | Identify incomplete data requiring attention |  Zero missing values |
| **Duplicate Rows** | Detect repeated records |  Zero duplicates found |
| **Range Validation** | Check for out-of-bounds values in percentage/rate columns |  All values within expected ranges |
| **Negative Values** | Identify impossible negative counts/percentages |  No invalid negatives |
| **Outliers** | Detect statistical anomalies using IQR method |  Outliers identified and documented |
| **Categorical Consistency** | Verify unique values in categorical columns |  Consistent unique values per column |

### Key Audit Results

| Metric | Result |
|--------|--------|
| Missing Values | 0% |
| Duplicate Rows | 0 |
| Data Type Errors | 0 |
| Out-of-Range Values | 0 (all within expected bounds) |
| **Overall Data Quality** | **EXCELLENT** |

## 4. Data Cleaning and Standardisation

### Missing Values

- Carried out an audit that revealed no missing values across all 22 columns.
- A `Had_Missing_Values` indicator column was added to flag any rows with missing data (all values = 0).
- No imputation was required.

### Duplicate Rows

- We found no duplicate rows in the 1,000,000-row dataset.
- The `drop_duplicates()` method was applied as a safeguard, with row count remaining at 1,000,000.

### Outlier Handling

- We used both the IQR and z-score methods to detect outliers across all numeric columns and none were detected.
- We also added a `Had_Outliers` boolean indicator.
- No capping or removal was needed.

### Data Type Corrections

- `Year` was explicitly cast to `int64`.
- Seven object-type columns with low cardinality (less than 20% unique values) were converted to the category dtype: `Country`, `Disease Name`, `Age Group`, `Gender`, `Treatment Type`, and `Availability of Vaccines/Treatment`.
- This optimization reduced memory usage from **484.66MB** to **129.70 MB**, saving memory space worth **354.96MB (73.2%)**.

### String Standardization

- We standardized all the seven categorical columns by:
    1. Stripping leading and trailing whitespace.
    2. Converting all values to **lowercase**.

- *Columns Standardized:* `Country`, `Disease Name`, `Disease Category`, `Age Group`, `Gender`, `Treatment Type`, `Availability of Vaccines/Treatment`
- We carried out a verification check which confirmed that no whitespace issues remained.
- The `Age Group` column flagged as not fully lowercase since its values (e.g., `0-18`, `36-60`, `61+`) are numeric range strings with no alphabetic characters to lowercase - this is expected and not an issue.

### 5. Transformation: Joins, Grouping & Aggregations.

**Group by Country** - to compare average Mortality, Recovery, and Healthcare Access rates across all 20 countries. Values were consistent with minimal variance across countries.

**Group by Disease Category** - Used `describe()` on Mortality Rate per disease caregory to capture full distibution stats. Metabolic diseases had the highest mean mortality (5.08%) while autoimmune and parasitic were lowest(5.03%).

**Group by Year** - Tracked four health indicators annually from 2000-2024 to identify longitudinal trends. No clear trend was observed, consistent with the synthetic nature of the dataset.

**Joins/Merges** - Scanned for additional CSV files to enrich the dataset but none were found. A merge template was documented for future use with external sources like World Bank or WHO data.

**Pivot Table** - Created a Disease Category * Age Group matrix of average Mortality Rate using `pd.pivot_table`. Metabolic diseases showed the highest mortality rate in the 0-18 group (5.092%).

**Cross-Tabulation** - Counted records per Disease Category * Age Group cell using `pd.crosstab` to verify dataset balance. Cell counts ranged from 22,479 to 23,181, confirming no stratified sampling is needed.



### 6. Feature Engineering

Feature engineering transforms raw columns into analytically richer representations. Eleven new features were created across four categories: ratio/derived metrics, binary flags, time-based features, and label encodings. Each feature is motivated by a specific analytical question the visualization system needs to answer.



### 1. Ratio & Derived Numerical Features

#### `Severity_Index`

```python
df['Severity_Index'] = df['Mortality Rate (%)'] / (df['Prevalence Rate (%)'] + 1e-5)
```

**What it measures:** How deadly a disease is *relative to how common it is*. A high severity index means a disease kills a large proportion of those who have it, even if it is not widespread.

**Why it was created:** Raw mortality rate alone cannot distinguish between a rare but lethal disease and a common but mild one. This ratio surfaces that distinction.

**Implementation note:** `1e-5` is added to the denominator to prevent division by zero in edge cases where `Prevalence Rate` is 0.



#### `DALY_Intensity`

```python
df['DALY_Intensity'] = df['DALYs'] / df['Population Affected']
```

**What it measures:** Per-person disease burden — the average number of Disability-Adjusted Life Years (DALYs) lost per affected individual.

**Why it was created:** Total DALYs scale with population size. Dividing by `Population Affected` normalises the burden to the individual level, making it possible to compare diseases across countries and demographic groups of different sizes.



### 2. Binary & Flag Features

#### `Vaccine_Available_Flag`

```python
df['Vaccine_Available_Flag'] = (
    df['Availability of Vaccines/Treatment'].str.lower() == 'yes'
).astype(int)
```

**Values:** `1` = vaccine/treatment available · `0` = not available

**Why it was created:** Converts the `Yes/No` string column into a machine-readable integer flag, enabling direct use in aggregations and comparisons (e.g., average mortality rate where vaccine = 1 vs. 0).



#### `High_Risk_Demographic`

```python
df['High_Risk_Demographic'] = df['Age Group'].str.lower() == '61+'
```

**Values:** `True` / `False`

**Why it was created:** The 61+ age group is consistently the most vulnerable across disease categories. This boolean flag enables fast filtering and segmentation for visualizations focused on elderly populations.



#### `Avg_Incidence_Disease`

```python
df['Avg_Incidence_Disease'] = df.groupby('Disease Name')['Incidence Rate (%)'].transform('mean')
```

**What it measures:** The mean incidence rate across all records for a given disease, broadcast back to every row of that disease.

**Why it was created:** Allows each row to be compared against its disease-level baseline, which is useful for identifying countries or years where a disease is spreading faster or slower than average.



#### `Mortality_YoY_Change`

```python
df = df.sort_values(['Country', 'Disease Name', 'Year'])
df['Mortality_YoY_Change'] = (
    df.groupby(['Country', 'Disease Name'])['Mortality Rate (%)']
    .diff()
    .round(2)
)
```

**What it measures:** The year-on-year change in mortality rate for each country–disease pair.

**Why it was created:** Enables trend detection — identifying whether a disease is becoming more or less deadly over time in a specific country. First-year records within each group will have `NaN` (expected behaviour, as there is no prior year to diff against).



#### `Weighted_Time_Impact`

```python
df['Weighted_Time_Impact'] = df['Improvement in 5 Years (%)'] * (df['Year'] - 2000) / 24
```

**What it measures:** The health improvement score scaled by how far into the study period the record falls (2000–2024).

**Why it was created:** A 5% improvement reported in 2024 represents a larger cumulative context than the same improvement in 2001. This weighting allows the improvement metric to be interpreted relative to the time elapsed in the dataset.



### 3. Time-Based Features

#### `decade`

```python
df['decade'] = (df['Year'] // 10) * 10
```

**Values:** `2000`, `2010`, `2020`

**Why it was created:** Groups years into decades for higher-level temporal aggregations and visualizations comparing 2000s vs. 2010s vs. 2020s health trends.


### 4. Label Encoding

Categorical columns were label-encoded to support downstream modelling and numerical aggregations.

```python
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
```


```df['Demographic_encoded']        = le.fit_transform(df['Age Group'].str.lower())
df['Gender_Encoded']             = le.fit_transform(df['Gender'].str.lower())
df['Disease_Category_Encoded']   = le.fit_transform(df['Disease Category'].str.lower())
```

| New Column | Source Column | Encoding |
| --- | --- | --- |
| `Demographic_encoded` | `Age Group` | 0-18 → 0, 19-35 → 1, 36-60 → 2, 61+ → 3 |
| `Gender_Encoded` | `Gender` | female → 0, male → 1, other → 2 |
| `Disease_Category_Encoded` | `Disease Category` | Alphabetical label encoding (0–10) |



### Engineered Features Summary

| Feature | Type | Source Column(s) | Purpose |
|---|---|---|---|
| `Severity_Index` | float32 | `Mortality Rate (%)`, `Prevalence Rate (%)` | Deadliness relative to spread |
| `DALY_Intensity` | float32 | `DALYs`, `Population Affected` | Per-person disease burden |
| `Vaccine_Available_Flag` | int32 | `Availability of Vaccines/Treatment` | Binary treatment availability |
| `High_Risk_Demographic` | bool | `Age Group` | Flag for 61+ age group |
| `Avg_Incidence_Disease` | float32 | `Incidence Rate (%)`, `Disease Name` | Disease-level incidence baseline |
| `Mortality_YoY_Change` | float32 | `Mortality Rate (%)`, `Country`, `Disease Name`, `Year` | Year-on-year mortality trend |
| `Weighted_Time_Impact` | float32 | `Improvement in 5 Years (%)`, `Year` | Time-weighted improvement score |
| `decade` | int32 | `Year` | Decade grouping |
| `Demographic_encoded` | int32 | `Age Group` | Label-encoded age group |
| `Gender_Encoded` | int32 | `Gender` | Label-encoded gender |
| `Disease_Category_Encoded` | int32 | `Disease Category` | Label-encoded disease category |



## 7. Final Pipeline & Dataset Export

### Export Details

The enriched dataset is exported as a compressed CSV to the `data/processed/` directory.

```python
from pathlib import Path

PROJECT_ROOT = Path().resolve().parent if Path().resolve().name == 'notebooks' else Path().resolve()
PROCESSED_PATH = PROJECT_ROOT / 'data' / 'processed' / 'global_health_enriched.csv.gz'
PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)

# Downcast numeric columns to reduce file size
for col in df.select_dtypes(include=['float64']).columns:
    df[col] = df[col].astype('float32')
for col in df.select_dtypes(include=['int64']).columns:
    if df[col].min() > -2147483648 and df[col].max() < 2147483647:
        df[col] = df[col].astype('int32')

df.to_csv(PROCESSED_PATH, index=False, compression='gzip') 
```

| Property | Value |
|---|---|
| Output file | `data/processed/global_health_enriched.csv.gz` |
| Compression | gzip |
| Final shape | 1,000,000 rows × 33 columns |
| Numeric precision | float64 → float32, int64 → int32 |

> **Why gzip?** The 1M-row dataset is large in raw form. gzip compression significantly reduces storage and transfer size while remaining natively readable by pandas via `pd.read_csv(..., compression='gzip')`.



### Data Dictionary

#### Original Columns (22)

| Column | Type | Description | Transformation Applied |
|---|---|---|---|
| `Country` | category | Country name | Lowercased, cast to category |
| `Year` | int32 | Year of record | Cast to int32 |
| `Disease Name` | category | Name of disease | Lowercased, cast to category |
| `Disease Category` | category | Disease classification | Lowercased, cast to category |
| `Prevalence Rate (%)` | float32 | % of population with disease | Cast to float32 |
| `Incidence Rate (%)` | float32 | % of new cases per year | Cast to float32 |
| `Mortality Rate (%)` | float32 | % of deaths from disease | Cast to float32 |
| `Age Group` | category | Age bracket of affected group | Lowercased, cast to category |
| `Gender` | category | Gender of affected group | Lowercased, cast to category |
| `Population Affected` | int32 | Number of people affected | Cast to int32 |
| `Healthcare Access (%)` | float32 | % with access to healthcare | Cast to float32 |
| `Doctors per 1000` | float32 | Doctors per 1,000 population | Cast to float32 |
| `Hospital Beds per 1000` | float32 | Hospital beds per 1,000 population | Cast to float32 |
| `Treatment Type` | category | Type of treatment used | Lowercased, cast to category |
| `Average Treatment Cost (USD)` | int32 | Average cost of treatment in USD | Cast to int32 |
| `Availability of Vaccines/Treatment` | category | Yes/No vaccine availability | Lowercased, cast to category |
| `Recovery Rate (%)` | float32 | % of patients who recovered | Cast to float32 |
| `DALYs` | int32 | Disability-Adjusted Life Years lost | Cast to int32 |
| `Improvement in 5 Years (%)` | float32 | % health improvement over 5 years | Cast to float32 |
| `Per Capita Income (USD)` | int32 | Average income per person in USD | Cast to int32 |
| `Education Index` | float32 | Education level index (0–1) | Cast to float32 |
| `Urbanization Rate (%)` | float32 | % of urban population | Cast to float32 |

#### Engineered Columns (11)

| Column | Type | Description | Derivation |
|---|---|---|---|
| `Severity_Index` | float32 | Deadliness relative to prevalence | `Mortality Rate / (Prevalence Rate + 1e-5)` |
| `DALY_Intensity` | float32 | Per-person disease burden | `DALYs / Population Affected` |
| `Vaccine_Available_Flag` | int32 | 1 if treatment available, else 0 | Binary encode of `Availability of Vaccines/Treatment` |
| `High_Risk_Demographic` | bool | True if Age Group is 61+ | `Age Group == '61+'` |
| `Avg_Incidence_Disease` | float32 | Mean incidence rate per disease | `groupby('Disease Name')['Incidence Rate'].transform('mean')` |
| `Mortality_YoY_Change` | float32 | Year-on-year mortality change per country–disease | `groupby(['Country','Disease Name'])['Mortality Rate'].diff()` |
| `Weighted_Time_Impact` | float32 | Improvement score weighted by time elapsed | `Improvement × (Year − 2000) / 24` |
| `decade` | int32 | Decade of the record | `(Year // 10) × 10` |
| `Demographic_encoded` | int32 | Label-encoded Age Group | `LabelEncoder` on `Age Group` |
| `Gender_Encoded` | int32 | Label-encoded Gender | `LabelEncoder` on `Gender` |
| `Disease_Category_Encoded` | int32 | Label-encoded Disease Category | `LabelEncoder` on `Disease Category` |



### Pipeline Summary

| Step | Action | Rows Before | Rows After | Columns Before | Columns After |
|---|---|---|---|---|---|
| Raw load | Read CSV from `data/raw/` | — | 1,000,000 | — | 22 |
| Remove duplicates | `drop_duplicates()` | 1,000,000 | 1,000,000 | 22 | 22 |
| Handle missing values | No missing values found | 1,000,000 | 1,000,000 | 22 | 22 |
| Handle outliers | No outliers detected (IQR + Z-score) | 1,000,000 | 1,000,000 | 22 | 22 |
| Type conversion | Cast to `category` / `float32` / `int32` | 1,000,000 | 1,000,000 | 22 | 22 |
| String standardisation | Lowercase + strip all `object` columns | 1,000,000 | 1,000,000 | 22 | 22 |
| Feature engineering | 11 new features created | 1,000,000 | 1,000,000 | 22 | 33 |
| **Final export** | Saved as `global_health_enriched.csv.gz` | 1,000,000 | 1,000,000 | 33 | 33 |

---

### Loading the Processed Dataset

To load the exported dataset in downstream notebooks or scripts:

```python
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path().resolve().parent if Path().resolve().name == 'notebooks' else Path().resolve()
PROCESSED_PATH = PROJECT_ROOT / 'data' / 'processed' / 'global_health_enriched.csv.gz'

df = pd.read_csv(PROCESSED_PATH, compression='gzip')
print(f'Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns')
```

---

### Errors Encountered

**Error 1- Invalid Value Check Failure.** 

*Location* Quality Audit.
- The error occured when the code attempted to compare non-numeric(string/object) columns with numeric values, which Pandas does not support.
- This was because no type check was in place before performing numeric validation, causing the comparison to fail on non-numeric columns.
  
- *Fix Applied*- Added dtype checks `df[col].dtype` in `(['float64', 'int64'])` to ensure only numeric columns are validated.
- *Outcome*- The corrected code now successfully:
      + Checks for invalid values(negative populations, rates outside 0-100)
      + Prints a summary table or confirmation message
      + Outputs min/max statistics for numeric colimns to verify data ranges
- Similar dtype-related errors were encountered win subsequent cells and resolved using the same type-check fix.

**Error 2- Severity Index (Coefficient Issue)** 

- Two instances were identified where the Severity Index produced faulty output affecting correlation analysis and modelling.
- This was because the severity index was calculated by multiplying the quotient of the mortality rate and prevalence rate by a coefficient of **2**. This created a disproportionately large gap in the output, making the results  false and difficult to analyse.
- *Fix Applied*- The coefficient was reduced from **2** to **1.5**, which produced a more manipulatable output with a variation that can be used in further analysis.

**Error 3- File Size (Github Push Failure.)** 

- After enriching the dataset, the file exceeded Github's size limit and could not be pushed.
- *File Sizes*- Before compression: **223.5 MB**
               - After Compression: **~75 MB**
- *Fix Applied-* Compressed the file, the rewrote the git history, and used `--force` to push the package.
- *Note:* The `--force` push rewites remote history. Team members may need to re-clone or reset their local branches.

**Error 4- Notebook Corruption - Invalid JSON ( Caused by Error 3 fix )**

*File Affected:* `milestone2_data_processing_transformation.ipynb`

- The `--force` push and git history rewrite performed in error 3 corrupted the Jupyter Notebook, rendering it invalid JSON.
- GitHub was unable to preview the notebook displaying
    > **Invalid Notebook**
    > "The Notebook Does Not Appear to Be Valid JSON"
    > (nbformat v5.10.4, nbconvert v7.16.6)
- The git history rewrite likely caused merge conflicts or incomplete file states that broke the notebook's JSON structure.
- *Fix Applied:* Resolved through a trial-and-error approach targeting tyhe corrupted JSON. A **new branch** was created to safe;y apply corrections without further affecting the main branch.
    >**Lesson Learned:** Force-pushing with rewritten history carries risk of filr corruption, especially for complex file formats like `.ipynb`. Future large file issues sshould consider Gir LFS (Large File Storage) as a safer alternative.  

