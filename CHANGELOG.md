# Changelog

All notable changes to this project will be documented in this file.

## [0.1.4] - 2025-06-01
### Added
- `model_preview.py` module:
  - Automatically detects actual vs. theoretical price columns using flexible keyword matching (e.g., `price`, `model_price`)
  - Selects numeric features based on simple keyword scanning (e.g., `volatility`, `spread`, `parity`)
  - Skips non-numeric or missing features
  - Drops rows with NaNs in any selected input columns
  - Runs a Ridge regression to predict `price - model_price` deviation
  - Prints:
    - Test set Mean Squared Error (MSE)
    - Feature coefficients
    - Top 3 prediction samples with actual vs predicted deviation

### Changed
- `main.py` updated to automatically run `run_model_preview()` after feature engineering is completed

### Fixed
- Resolved SettingWithCopyWarning by adding `.copy()` after `dropna` operations
- Prevented model errors due to NaNs or string-based features during training

---

## [0.1.3] - 2025-05-29
### Changed
- `add_features()` now assumes a default `par_value` of 100 if missing.
- Feature calculations (`called_early`, `benchmark_spread`, `rolling_vol_20d`) skip gracefully if required columns are absent.
- Insert a blank spacer column named `----` before all newly added feature columns to visually separate them from original data.

---

## [0.1.2] - 2025-05-28
### Added
- `feature_engineer.py` module with:
  - `daily_return` feature using percent change on `price`
  - `rolling_vol_20d` as 20-day standard deviation of returns
  - `near_parity` binary flag for prices within $5 of par
  - `benchmark_spread` from `yield - benchmark_yield`
  - `called_early` flag if `call_date` < `maturity_date`
- Integrated `add_features()` into `main.py` pipeline
- Saves `features_[filename].csv` alongside the cleaned file

---

## [0.1.1] - 2025-05-27
### Added
- Initial file cleaner with `clean_dataframe()` pipeline
- Modular split into:
  - `loader.py` (file loading)
  - `cleaner.py` (data cleaning)
  - `utils.py` (shared functions/constants)
