# Changelog

All notable changes to this project will be documented in this file.

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
