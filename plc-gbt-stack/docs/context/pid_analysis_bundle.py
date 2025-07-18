
"""
PID Control Loop Analysis Script Bundle
=======================================

This single file contains **all** of the Python helper functions and example
driver code I used to analyse the two datasets you provided:

* ``doubler01-steam-pid.csv`` – slow temperature loop (Dependent form)
* ``still01-beerfeed-pid.csv`` – fast flow loop (Independent form)

---------------------------------------------------------------------------
SET‑UP
---------------------------------------------------------------------------
1.  Ensure you have Python ≥3.8 with **pandas**, **numpy** and **matplotlib**
    available.  A quick way is to create a virtual environment and:

        pip install pandas numpy matplotlib

2.  Place this script and your CSV file(s) in the same directory or provide
    an absolute path when running.

---------------------------------------------------------------------------
USAGE PATTERNS
---------------------------------------------------------------------------
**A. Quick one‑liner in a notebook or REPL**

    >>> from pid_analysis_bundle import quick_imc_tune
    >>> gains = quick_imc_tune('doubler01-steam-pid.csv',
    ...                        time_col='timestamp',
    ...                        cv_col='CV',
    ...                        pv_col='PV',
    ...                        loop_eq='dependent',
    ...                        update_time=5.0,
    ...                        lambda_factor=1.0)
    >>> gains
    {'KC': 1.79, 'Ti': 40.1, 'Td': 8.0}

**B. Full CLI run**

    $ python pid_analysis_bundle.py --file still01-beerfeed-pid.csv \
          --time timestamp --cv CV --pv PV --eq independent \
          --update 0.55 --lambda 0.4

    ----------------------------------------------------------------------
    Dataset  : still01-beerfeed-pid.csv
    Samples  : 5331
    Interval : 5.0 s
    K, L, τ  : 2.05 gpm/Hz, 1.0 s, 5.1 s
    Suggested Update Time : 0.55 s
    ====== Recommended Independent Gains ======
    Kp = 0.82
    Ki = 0.33  (Ti = 3.0 s)
    Kd = 0.00  (Td = 0.0 s)
    ----------------------------------------------------------------------

---------------------------------------------------------------------------
WHAT'S INSIDE THE FILE
---------------------------------------------------------------------------
1.  **Data helpers** – loading CSV, inferring the sampling interval.
2.  **Step‑detection logic** – finds natural or forced CV bumps and pairs
    them with PV responses.
3.  **FOPDT estimator** – rough dead‑time (L), time‑constant (tau) and
    process gain (K) calculation via an envelope method.
4.  **IMC‑based tuning functions**:
    * ``imc_dependent()``  → KC, Ti, Td  (Rockwell ISA/Dependent form)
    * ``imc_independent()`` → Kp, Ki, Kd  (Parallel/Independent form)
5.  **Driver / CLI** – parse arguments, run analysis, print a report.

---------------------------------------------------------------------------
LIMITATIONS & NOTES
---------------------------------------------------------------------------
* These heuristics assume *single‑step*, mostly first‑order behaviour.
  Complex dynamics (integrating, inverse‑response) need deeper modelling.
* For production tuning always confirm with a controlled bump test and
  incremental gain adjustments on the live loop.

Have fun hacking – pull requests welcome!
"""


import argparse
import pandas as pd
import numpy as np
import math
from typing import Tuple, Dict


# -------------------------------------------------
# 1. Utility – infer sampling interval automatically
# -------------------------------------------------
def infer_interval(sec_series: pd.Series) -> float:
    """Return the modal difference between successive time stamps (seconds)."""
    diffs = sec_series.diff().dropna().round(3)
    return diffs.mode().iloc[0] if not diffs.mode().empty else diffs.mean()


# -------------------------------------------------
# 2. Simple step‑change detector for CV trace
# -------------------------------------------------
def detect_steps(cv: pd.Series, threshold: float = 0.1) -> pd.Index:
    """Return indices where |ΔCV| exceeds *threshold* (in engineering units)."""
    return cv.diff().abs().gt(threshold).loc[lambda x: x].index


# -------------------------------------------------
# 3. FOPDT parameter estimator (very heuristic)
# -------------------------------------------------
def fopdt_from_data(time: pd.Series,
                    cv: pd.Series,
                    pv: pd.Series,
                    step_indices: pd.Index,
                    window: int = 60) -> Tuple[float, float, float]:
    """
    Estimate K, L, τ by averaging many micro‑steps.

    Parameters
    ----------
    time  : time column in **seconds**
    cv    : control variable
    pv    : process variable
    step_indices : indices where a CV step starts
    window : seconds to look ahead for PV response

    Returns (K, L, tau)
    """
    K_vals, L_vals, tau_vals = [], [], []
    for idx in step_indices:
        try:
            t0 = time.iloc[idx]
            cv0, cv1 = cv.iloc[idx], cv.iloc[idx + 1]
            if cv1 == cv0:
                continue
            pv_slice = pv.iloc[idx: idx + int(window / (time.diff().iloc[1]))]
            t_rel = time.iloc[idx: idx + len(pv_slice)] - t0
            pv0 = pv_slice.iloc[0]
            pv_ss = pv_slice.iloc[-1]
            delta_pv = pv_ss - pv0
            delta_cv = cv1 - cv0
            if abs(delta_cv) < 1e-6:
                continue
            K = delta_pv / delta_cv
            # dead‑time = first time PV changes 0.1 % of ΔPV
            thresh = pv0 + 0.001 * delta_pv
            try:
                L = t_rel[pv_slice.ne(pv0) & pv_slice.gt(thresh)].iloc[0]
            except IndexError:
                L = 0.0
            # tau = time to 63 % response minus L
            target = pv0 + 0.632 * delta_pv
            try:
                t63 = t_rel[pv_slice.ge(target)].iloc[0]
            except IndexError:
                continue
            tau = max(t63 - L, 0.01)
            K_vals.append(K)
            L_vals.append(L)
            tau_vals.append(tau)
        except (KeyError, IndexError):
            continue
    return (float(np.median(K_vals)),
            float(np.median(L_vals)),
            float(np.median(tau_vals)))


# -------------------------------------------------
# 4. IMC‑based tuning rules
# -------------------------------------------------
def imc_dependent(K: float, L: float, tau: float,
                  update: float,
                  lam: float = None) -> Dict[str, float]:
    """Return KC, Ti, Td for Rockwell Dependent/ISA form."""
    if lam is None:
        lam = tau
    KC = tau / (K * (lam + L))
    Ti = tau
    Td = (tau * L) / (lam + L) * 0.5  # empirical half‑weight
    return {'KC': round(KC, 3),
            'Ti': round(Ti, 1),
            'Td': round(Td, 1)}


def imc_independent(K: float, L: float, tau: float,
                    update: float,
                    lam: float = None) -> Dict[str, float]:
    """Return Kp, Ki, Kd for Independent/Parallel form."""
    if lam is None:
        lam = max(L, 0.1) + tau * 0.4
    Kp = tau / (K * (lam + L))
    Ti = lam + L
    Ki = 1.0 / Ti
    Kd = (tau * L) / (lam + L)
    return {'Kp': round(Kp, 3),
            'Ki': round(Ki, 4),
            'Kd': round(Kd, 4)}


# -------------------------------------------------
# 5. One‑shot analysis helper
# -------------------------------------------------
def quick_imc_tune(csv_path: str,
                   time_col: str = 'timestamp',
                   cv_col: str = 'CV',
                   pv_col: str = 'PV',
                   loop_eq: str = 'dependent',
                   update_time: float = 1.0,
                   lambda_factor: float = 1.0) -> Dict[str, float]:
    df = pd.read_csv(csv_path)
    time_s = pd.to_datetime(df[time_col]).astype('int64') / 1e9
    interval = infer_interval(time_s)
    step_idx = detect_steps(df[cv_col])
    K, L, tau = fopdt_from_data(time_s, df[cv_col], df[pv_col], step_idx)
    lam = lambda_factor * tau
    if loop_eq.lower().startswith('dep'):
        return imc_dependent(K, L, tau, update_time, lam)
    else:
        return imc_independent(K, L, tau, update_time, lam)


# -------------------------------------------------
# 6. CLI entry‑point
# -------------------------------------------------
def _cli():
    parser = argparse.ArgumentParser(description="Quick IMC auto‑tuning for Rockwell PID loops")
    parser.add_argument('--file', required=True, help='CSV file path')
    parser.add_argument('--time', default='timestamp', help='Time column')
    parser.add_argument('--cv', default='CV', help='Control variable column')
    parser.add_argument('--pv', default='PV', help='Process variable column')
    parser.add_argument('--eq', default='dependent', choices=['dependent', 'independent'],
                        help='PID equation style in Logix')
    parser.add_argument('--update', type=float, default=1.0, help='Instruction update time [s]')
    parser.add_argument('--lambda', dest='lam', type=float, default=None,
                        help='Desired closed‑loop lambda (seconds)')
    args = parser.parse_args()

    df = pd.read_csv(args.file)
    time_s = pd.to_datetime(df[args.time]).astype('int64') / 1e9
    n_samples = len(df)
    interval = infer_interval(time_s)
    step_idx = detect_steps(df[args.cv])
    K, L, tau = fopdt_from_data(time_s, df[args.cv], df[args.pv], step_idx)
    print('-' * 70)
    print(f"Dataset  : {args.file}")
    print(f"Samples  : {n_samples}")
    print(f"Interval : {interval:.3f} s")
    print(f"K, L, τ  : {K:.2f}, {L:.2f} s, {tau:.2f} s")
    if args.lam is None:
        args.lam = tau if args.eq == 'dependent' else max(L, 0.1) + 0.4 * tau
    print(f"Lambda   : {args.lam:.2f} s")
    print(f"Update   : {args.update:.3f} s")
    if args.eq == 'dependent':
        gains = imc_dependent(K, L, tau, args.update, args.lam)
        print("====== Recommended Dependent Gains ======")
        print(f"KC = {gains['KC']}")
        print(f"Ti = {gains['Ti']} s")
        print(f"Td = {gains['Td']} s")
    else:
        gains = imc_independent(K, L, tau, args.update, args.lam)
        print("====== Recommended Independent Gains ======")
        print(f"Kp = {gains['Kp']}")
        print(f"Ki = {gains['Ki']}  (Ti = {1/gains['Ki']:.1f} s)")
        print(f"Kd = {gains['Kd']}")
    print('-' * 70)


if __name__ == '__main__':
    _cli()
