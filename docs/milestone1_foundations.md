# Milestone 1 Documentation: Data Representation & Foundations

##### **Project:** Public Health Data Visualization System
##### **Dataset:** Global Health Statistics (1,000,000 records × 22 columns)
##### **Period:** 20th April - 27th April
---

## 1. What Changed

### Dataset Acquisition
- Selected the **Global Health Statistics** dataset from a shared Google Drive folder as our primary data source.
- We chose this approach because of different working environments so the center connector would github which has a limit of <=100MB size of each file pushed to it and to work with a consistent datase for each of the 9 members.
- Automated the download process using `gdown` so every team member can reproduce the setup with a single command, regardless of OS (Ubuntu or Windows).
- Stored the raw CSV in `data/raw/` which is excluded from Git (file size > 100MB).

### Project Structure
- Established a standardized folder structure (`data/`, `notebooks/`, `docs/`) that all team members follow.
- Created a virtual environment (`.venv`) with pinned library versions in `requirements.txt` to ensure every member runs identical dependencies to prevent conflicts in running since we are all working on the same system simultaneously.
- Registered a Jupyter kernel (`dataviz`) so notebooks run consistently across machines.
- Created `notebooks/load_dataset.ipynb` as the single entry point — it detects whether the environment is local or Google Colab and downloads the dataset automatically if missing.

### Data Schema & Variable Definitions
- We catalogued all 22 columns with their respective data types, null counts, and sample values.
- Classified variables into two groups:
  - **7 Categorical:** Country, Disease Name, Disease Category, Age Group, Gender, Treatment Type, Availability of Vaccines/Treatment
  - **15 Numerical:** Year, Prevalence Rate (%), Incidence Rate (%), Mortality Rate (%), Population Affected, Healthcare Access (%), Doctors per 1000, Hospital Beds per 1000, Average Treatment Cost (USD), Recovery Rate (%), DALYs, Improvement in 5 Years (%), Per Capita Income (USD), Education Index, Urbanization Rate (%)

### Descriptive Statistics
- Computed mean, median, standard deviation, variance, min, max, and skewness for all 15 numerical columns.
- Key findings:
  - **Mortality Rate (%):** Mean = 5.05, Std = 2.86, Range = 0.1–10.0
  - **Healthcare Access (%):** Mean = 74.99, Std = 14.44, Range = 50.0–100.0
  - **Recovery Rate (%):** Mean = 74.50, Std = 14.16, Range = 50.0–99.0
  - **Year range:** 2000–2024 across 20 countries and 20 unique diseases

### Simple, Initial Data Quality Assessment
- **Missing values:** None detected across all 1,000,000 rows and 22 columns.
- **Duplicate rows:** 0 duplicates found.
- **Outliers (IQR method):** 0 statistical outliers detected in the first 5 numerical columns — data appears to be synthetically generated within defined bounds.

### Initial Visual Outputs
Produced 4 charts in a single 2×2 axes figure saved to `docs/charts/`:

| Chart | Description |
|---|---|
| Mortality Rate Distribution by Category | Stacked histogram showing distribution across top 5 disease categories |
| Healthcare Access vs Recovery Rate | Scatter plot (5,000 sample) showing positive correlation |
| Healthcare Access Trend (2000–2024) | Line chart showing average healthcare access over time |
| Mortality Rate by Disease Category | Boxplot comparing spread across all disease categories |

---

## 2. What Failed

### Issue 1 — `ipykernel` Not Found
When team members first opened a notebook in VS Code, they received:
> *"Running cells with 'Python 3.12.3' requires the ipykernel package."*

### Issue 2 — `pandas` Module Not Found
After selecting the kernel, running the first cell produced:
> *"ModuleNotFoundError: No module named 'pandas'"*

### Issue 3 — Dataset Not Found (`FileNotFoundError`)
Running the data loading cell produced:
> *"FileNotFoundError: No such file or directory: 'data/raw/Global Health Statistics.csv'"*

### Issue 4 — Git Push Rejected (Non-Fast-Forward)
When pushing to the remote branch:
> *"Updates were rejected because the tip of your current branch is behind its remote counterpart."*

### Issue 5 — Merge Conflicts on PNG Chart Files
When merging branches, Git flagged binary conflicts:
> *"CONFLICT (content): Merge conflict in docs/charts/milestone1_initial_visuals.png"*

### Issue 6 — Visualization `IndexError`
The initial chart code used `plt.subplots(2, 2)` but tried to access `axes[2, 0]`, causing:
> *"IndexError: index 2 is out of bounds for axis 0 with size 2"*

---

## 3. Why It Failed

| Issue | Root Cause |
|---|---|
| **`ipykernel`** not found | The virtual environment was created but `ipykernel` was not installed inside it. VS Code was pointing to the venv Python but the package was missing. |
| **`pandas`** not found | `pip install -r requirements.txt` was run against the system Python, not the activated `.venv`. Packages were installed in the wrong environment. |
| **Dataset not found** | The raw CSV is excluded from Git (>100MB). Team members cloned the repo but did not download the dataset separately. |
| **Git push rejected** | The remote branch had commits that the local branch did not have, causing diverged histories. |
| **PNG merge conflicts** | Generated chart images were being tracked by Git. Binary files cannot be auto-merged, so any two branches that both generated charts would always conflict. |
| **`IndexError`** on charts | The grid was declared as `2×2` (4 slots) but the code referenced row index `2`, which does not exist in a 2-row grid. |

---

## 4. Alternative Solutions

### Issue 1 & 2 — Environment Setup
**Solution applied:** Created the virtual environment, activated it, then installed all dependencies including `ipykernel` inside it, and registered the kernel:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name=dataviz --display-name "Python (dataviz)"
```
> For any member missing a pariticular module like seaborn or scipy, they would download the specific version supported by their machines using **pip install <module_name>**

**Alternative:** Use Conda environments or Docker containers for fully isolated, reproducible environments across all team members.

### Issue 3 — Dataset Not Found
**Solution applied:** Added `gdown` to `requirements.txt` and updated `load_dataset.ipynb` to automatically download the dataset from Google Drive using the file ID if the CSV is missing locally, which happens each time a member clones their repo from github since the csv file is never pushed to github:
```python
import gdown
gdown.download('https://drive.google.com/uc?id=1cug4qWE6qFArHmYwcXUdDMaJIfmUzAZD', 'data/raw/Global Health Statistics.csv')
```
**Alternative:** Host the dataset on a university server or use a cloud storage bucket (AWS S3, Azure Blob) with a public download URL.

### Issue 4 — Git Push Rejected
**Solution applied:** Used `--rebase` instead of a merge commit to replay local commits on top of the remote:
```bash
git pull origin main --rebase
git push origin main
```
**Alternative:** Set `git config --global pull.rebase true` as the default so this is handled automatically on every pull.

### Issue 5 — PNG Merge Conflicts
**Solution applied:** Added `docs/charts/` to `.gitignore` so generated chart files are never tracked by Git. Removed already-tracked files from the index:
```bash
git rm --cached docs/charts/ -r
```
**Alternative:** Store chart outputs in a separate `artifacts` branch or use a CI/CD pipeline to regenerate charts automatically on merge.

### Issue 6 — `IndexError` on Charts
**Solution applied:** Changed the grid from `plt.subplots(2, 2)` to match the number of charts being plotted, and corrected all axis references to stay within bounds.
**Alternative:** Use a flat axes array (`axes.flatten()`) and iterate over it, which avoids hardcoded index errors entirely.

---

## 5. Deliverables Status

| Deliverable | Status | Notes |
|---|---|---|
| Working prototype (Python) | ✅ Complete | `notebooks/milestone1_foundations.ipynb` runs end-to-end |
| Dataset acquisition | ✅ Complete | Auto-download via `gdown` in `load_dataset.ipynb` |
| Data schema & variable definitions | ✅ Complete | 22 columns catalogued with types, nulls, and samples |
| Basic descriptive statistics | ✅ Complete | Mean, median, std, variance, skewness for all 15 numerical columns |
| Distribution analysis | ✅ Complete | Histograms, boxplots, and scatter plots produced |
| Initial visual outputs | ✅ Complete | 4 charts in 2×2 axes layout saved to `docs/charts/` |
| Data quality assessment | ✅ Complete | 0 missing values, 0 duplicates, 0 outliers detected |

---

## 6. Key Observations from the Data

1. **No missing data** — The dataset is complete across all 1,000,000 records, suggesting it is synthetically generated.
2. **Uniform distributions** — Most numerical variables are uniformly distributed within defined ranges, which is consistent with synthetic data.
3. **Healthcare access correlates with recovery** — The scatter plot shows a visible positive trend between healthcare access and recovery rate.
4. **Healthcare access is stable over time** — The trend line (2000–2024) shows minimal variation, suggesting the dataset does not simulate real-world improvement over time.
5. **Mortality rates are consistent across disease categories** — The boxplot shows similar medians and spreads across all categories, further confirming synthetic generation.

---


