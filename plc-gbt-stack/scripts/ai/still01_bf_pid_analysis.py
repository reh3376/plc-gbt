#!/usr/bin/env python3
"""
Still01 BF PID Control Loop Analysis
====================================

Comprehensive analysis of still01-bf-pid.csv dataset following AI Task Orchestrator methodology.

Dataset Context:
- SP: Volume flow setpoint in GPM
- PV01: Volume flow process variable in GPM
- CV01: Pump speed control variable in Hz
- DV01: Level disturbance variable

PID Configuration:
- Instruction: PID
- Update: 750ms
- Bias Calculation: false
- PV Tracking: true
- PID Equation: Independent (parallel form)
- Control action: SP - PV (reverse acting)
- Derivative of: PV
- Kp: 0.625, Ki: 0.0235, Kd: 0.0012

Author: AI Task Orchestrator
Date: January 18, 2025
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Import existing control loop analyzer (removed due to dependency issues)
# import sys
# sys.path.append('/Users/reh3376/repos/plc-gbt/plc-gbt-stack/scripts/ai')
# from configurable_control_loop_analyzer import ConfigurableControlLoopAnalyzer

@dataclass
class PIDConfiguration:
    """PID Controller Configuration"""
    instruction: str = "PID"
    update_rate_ms: int = 750
    bias_calculation: bool = False
    pv_tracking: bool = True
    pid_equation: str = "Independent"
    control_action: str = "SP - PV"
    derivative_of: str = "PV"
    kp: float = 0.625
    ki: float = 0.0235
    kd: float = 0.0012

class Still01BFPIDAnalyzer:
    """
    Comprehensive analyzer for Still01 BF PID control loop dataset
    """

    def __init__(self, dataset_path: str, pid_config: PIDConfiguration):
        self.dataset_path = dataset_path
        self.pid_config = pid_config
        self.data = None
        self.analysis_results = {}
        self.session_id = f"still01_bf_pid_analysis_{int(datetime.now().timestamp())}"

    def load_dataset(self) -> pd.DataFrame:
        """Load and prepare the dataset"""
        try:
            print(f"Loading dataset from: {self.dataset_path}")
            self.data = pd.read_csv(self.dataset_path)

            # Rename columns for clarity
            column_mapping = {
                'still01-bf-pid.DV01-LIT4003-level => (Aggregate=TimeAverage2)': 'DV01_Level',
                'still01-bf-pid.CV01-plp4000a.cmdspd-hz => (Aggregate=TimeAverage2)': 'CV01_PumpSpeed_Hz',
                'still01-bf-pid.SP-pmp4000a.sp-% => (Aggregate=TimeAverage2)': 'SP_VolumeFlow_GPM',
                'still01-bf-pid.PV01-fit4008.volumeflow => (Aggregate=TimeAverage2)': 'PV01_VolumeFlow_GPM'
            }

            self.data = self.data.rename(columns=column_mapping)

            # Convert numeric columns to float, handling any string values
            numeric_columns = ['DV01_Level', 'CV01_PumpSpeed_Hz', 'SP_VolumeFlow_GPM', 'PV01_VolumeFlow_GPM']
            for col in numeric_columns:
                if col in self.data.columns:
                    # Replace "No Data" with NaN before conversion
                    self.data[col] = self.data[col].replace('No Data', np.nan)
                    self.data[col] = pd.to_numeric(self.data[col], errors='coerce')

            # Drop rows with NaN values in critical columns
            critical_columns = ['SP_VolumeFlow_GPM', 'PV01_VolumeFlow_GPM']
            initial_rows = len(self.data)
            self.data = self.data.dropna(subset=critical_columns)
            final_rows = len(self.data)

            if initial_rows != final_rows:
                print(f"   Dropped {initial_rows - final_rows} rows with missing critical data")
                print(f"   Remaining rows: {final_rows}")

            # CORRECTION: Replace all SP values with 83 GPM as specified by user
            print("   Correcting SP values: Setting all SP values to 83 GPM")
            original_sp_mean = self.data['SP_VolumeFlow_GPM'].mean()
            self.data['SP_VolumeFlow_GPM'] = 83.0
            print(f"   Original SP mean: {original_sp_mean:.2f} GPM → Corrected SP: 83.0 GPM")

            # Create time index (5-second sampling)
            self.data['timestamp'] = pd.to_datetime('2025-01-01') + pd.to_timedelta(
                self.data.index * 5, unit='s'
            )

            print("Dataset loaded successfully:")
            print(f"- Records: {len(self.data)}")
            print(f"- Columns: {list(self.data.columns)}")
            print(f"- Time span: {len(self.data) * 5 / 60:.1f} minutes")

            return self.data

        except Exception as e:
            print(f"Error loading dataset: {e}")
            raise

    def calculate_pid_performance_metrics(self) -> Dict[str, Any]:
        """Calculate PID-specific performance metrics"""
        if self.data is None:
            raise ValueError("Dataset not loaded")

        # Extract key variables
        sp = self.data['SP_VolumeFlow_GPM'].values
        pv = self.data['PV01_VolumeFlow_GPM'].values
        cv = self.data['CV01_PumpSpeed_Hz'].values

        # Calculate error signal
        error = sp - pv  # SP - PV (reverse acting)

        # Performance metrics
        metrics = {
            'control_loop_type': 'Flow Control (Volume Flow)',
            'pid_configuration': {
                'kp': self.pid_config.kp,
                'ki': self.pid_config.ki,
                'kd': self.pid_config.kd,
                'update_rate_ms': self.pid_config.update_rate_ms,
                'control_action': self.pid_config.control_action,
                'equation_form': self.pid_config.pid_equation
            },
            'process_variables': {
                'sp_range': {'min': float(np.min(sp)), 'max': float(np.max(sp)), 'mean': float(np.mean(sp))},
                'pv_range': {'min': float(np.min(pv)), 'max': float(np.max(pv)), 'mean': float(np.mean(pv))},
                'cv_range': {'min': float(np.min(cv)), 'max': float(np.max(cv)), 'mean': float(np.mean(cv))},
                'error_stats': {
                    'mean': float(np.mean(error)),
                    'std': float(np.std(error)),
                    'rms': float(np.sqrt(np.mean(error**2))),
                    'max_abs': float(np.max(np.abs(error)))
                }
            },
            'performance_indicators': {
                'iae': float(np.sum(np.abs(error)) * 5),  # Integral Absolute Error (5s sampling)
                'ise': float(np.sum(error**2) * 5),       # Integral Square Error
                'itae': float(np.sum(np.abs(error) * np.arange(len(error)) * 5)),  # ITAE
                'tracking_accuracy': float(100 * (1 - np.mean(np.abs(error)) / np.mean(sp))),
                'control_effort': float(np.std(cv)),       # Controller output variability
                'steady_state_error': float(np.mean(error[-100:]))  # Last 100 points
            }
        }

        return metrics

    def analyze_control_loop_behavior(self) -> Dict[str, Any]:
        """Analyze control loop behavior patterns"""
        if self.data is None:
            raise ValueError("Dataset not loaded")

        # For now, create a simplified analysis without ConfigurableControlLoopAnalyzer
        # to avoid dependency issues
        sp = self.data['SP_VolumeFlow_GPM'].values
        pv = self.data['PV01_VolumeFlow_GPM'].values
        cv = self.data['CV01_PumpSpeed_Hz'].values
        error = sp - pv

        # Basic control loop behavior analysis
        loop_analysis = {
            'stability_analysis': {
                'oscillation_detected': self._detect_oscillations(error),
                'control_effort_variability': float(np.std(cv)),
                'error_variance': float(np.var(error)),
                'settling_behavior': self._analyze_settling_behavior(error)
            },
            'performance_characteristics': {
                'response_time': self._estimate_response_time(error),
                'overshoot': self._calculate_overshoot(pv, sp),
                'steady_state_accuracy': self._calculate_steady_state_accuracy(error)
            },
            'disturbance_rejection': {
                'disturbance_correlation': self._analyze_disturbance_correlation(),
                'recovery_time': self._estimate_recovery_time(error)
            }
        }

        return loop_analysis

    def _detect_oscillations(self, error: np.ndarray) -> Dict[str, Any]:
        """Detect oscillatory behavior in error signal"""
        # Simple oscillation detection using zero crossings
        zero_crossings = np.where(np.diff(np.sign(error)))[0]
        oscillation_rate = len(zero_crossings) / len(error) * 100

        return {
            'oscillation_rate_percent': float(oscillation_rate),
            'is_oscillating': bool(oscillation_rate > 10),  # Threshold for oscillation
            'zero_crossings': len(zero_crossings)
        }

    def _analyze_settling_behavior(self, error: np.ndarray) -> Dict[str, Any]:
        """Analyze settling behavior"""
        # Simple settling time estimation (time to reach 5% of final value)
        final_error = np.mean(error[-100:])  # Last 100 points
        settling_threshold = 0.05 * np.std(error)

        # Find last time error exceeded threshold
        settled_indices = np.where(np.abs(error - final_error) < settling_threshold)[0]

        if len(settled_indices) > 0:
            settling_time_samples = settled_indices[0]
            settling_time_minutes = settling_time_samples * 5 / 60  # 5-second sampling
        else:
            settling_time_minutes = float('inf')

        return {
            'settling_time_minutes': float(settling_time_minutes),
            'is_settled': bool(settling_time_minutes < float('inf')),
            'settling_threshold': float(settling_threshold)
        }

    def _estimate_response_time(self, error: np.ndarray) -> float:
        """Estimate system response time"""
        # Simple response time estimation using autocorrelation
        if len(error) < 10:
            return 0.0

        # Calculate autocorrelation
        autocorr = np.correlate(error, error, mode='full')
        autocorr = autocorr[len(autocorr)//2:]

        # Find first minimum (approximate response time)
        if len(autocorr) > 1:
            min_idx = np.argmin(autocorr[1:10]) + 1  # Look in first 10 samples
            response_time = min_idx * 5 / 60  # Convert to minutes
        else:
            response_time = 0.0

        return float(response_time)

    def _calculate_overshoot(self, pv: np.ndarray, sp: np.ndarray) -> float:
        """Calculate maximum overshoot"""
        # Find maximum deviation from setpoint
        max_overshoot = np.max(np.abs(pv - sp))
        avg_setpoint = np.mean(sp)

        if avg_setpoint > 0:
            overshoot_percent = (max_overshoot / avg_setpoint) * 100
        else:
            overshoot_percent = 0.0

        return float(overshoot_percent)

    def _calculate_steady_state_accuracy(self, error: np.ndarray) -> float:
        """Calculate steady-state accuracy"""
        # Use last 20% of data for steady-state
        steady_state_start = int(len(error) * 0.8)
        steady_state_error = np.mean(np.abs(error[steady_state_start:]))

        return float(steady_state_error)

    def _analyze_disturbance_correlation(self) -> Dict[str, Any]:
        """Analyze correlation with disturbance variable"""
        if 'DV01_Level' not in self.data.columns:
            return {'correlation': 0.0, 'analysis': 'No disturbance data available'}

        dv = self.data['DV01_Level'].values
        pv = self.data['PV01_VolumeFlow_GPM'].values

        # Calculate correlation
        correlation = np.corrcoef(dv, pv)[0, 1] if len(dv) == len(pv) else 0.0

        return {
            'correlation': float(correlation),
            'analysis': 'Strong correlation' if abs(correlation) > 0.7 else 'Weak correlation'
        }

    def _estimate_recovery_time(self, error: np.ndarray) -> float:
        """Estimate recovery time from disturbances"""
        # Simple recovery time estimation
        # Look for large error spikes and recovery
        error_threshold = 2 * np.std(error)
        large_errors = np.where(np.abs(error) > error_threshold)[0]

        if len(large_errors) > 0:
            # Estimate average recovery time
            recovery_times = []
            for i in large_errors:
                # Look for recovery within next 50 samples
                end_idx = min(i + 50, len(error))
                recovery_slice = error[i:end_idx]

                # Find where error returns to normal
                normal_indices = np.where(np.abs(recovery_slice) < error_threshold/2)[0]
                if len(normal_indices) > 0:
                    recovery_time = normal_indices[0] * 5 / 60  # Convert to minutes
                    recovery_times.append(recovery_time)

            avg_recovery_time = np.mean(recovery_times) if recovery_times else 0.0
        else:
            avg_recovery_time = 0.0

        return float(avg_recovery_time)

    def generate_visualizations(self) -> None:
        """Generate comprehensive visualizations"""
        if self.data is None:
            raise ValueError("Dataset not loaded")

        # Create output directory
        output_dir = f"plc-gbt-stack/results/control_loop_analysis/{self.session_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

        # Figure 1: Time series plot
        fig, axes = plt.subplots(4, 1, figsize=(15, 12))

        # SP and PV (Volume Flow)
        axes[0].plot(self.data.index, self.data['SP_VolumeFlow_GPM'],
                    label='SP (Volume Flow GPM)', color='blue', linewidth=2)
        axes[0].plot(self.data.index, self.data['PV01_VolumeFlow_GPM'],
                    label='PV (Volume Flow GPM)', color='red', linewidth=1.5)
        axes[0].set_ylabel('Flow (GPM)')
        axes[0].set_title('Still01 BF PID Control Loop - Volume Flow Control')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # Control Variable (Pump Speed)
        axes[1].plot(self.data.index, self.data['CV01_PumpSpeed_Hz'],
                    label='CV (Pump Speed Hz)', color='green', linewidth=1.5)
        axes[1].set_ylabel('Pump Speed (Hz)')
        axes[1].set_title('Controller Output - Pump Speed')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        # Error signal
        error = self.data['SP_VolumeFlow_GPM'] - self.data['PV01_VolumeFlow_GPM']
        axes[2].plot(self.data.index, error, label='Error (SP - PV)', color='orange', linewidth=1.5)
        axes[2].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[2].set_ylabel('Error (GPM)')
        axes[2].set_title('Control Error Signal')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

        # Disturbance Variable
        axes[3].plot(self.data.index, self.data['DV01_Level'],
                    label='DV (Level)', color='purple', linewidth=1.5)
        axes[3].set_ylabel('Level')
        axes[3].set_xlabel('Sample Index')
        axes[3].set_title('Disturbance Variable - Level')
        axes[3].legend()
        axes[3].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/still01_bf_pid_timeseries.png", dpi=300, bbox_inches='tight')
        plt.close()

        # Figure 2: Performance analysis
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Error histogram
        axes[0,0].hist(error, bins=50, alpha=0.7, color='orange', edgecolor='black')
        axes[0,0].set_xlabel('Error (GPM)')
        axes[0,0].set_ylabel('Frequency')
        axes[0,0].set_title('Error Distribution')
        axes[0,0].grid(True, alpha=0.3)

        # PV vs SP scatter
        axes[0,1].scatter(self.data['SP_VolumeFlow_GPM'], self.data['PV01_VolumeFlow_GPM'],
                         alpha=0.6, s=20, color='blue')
        axes[0,1].plot([self.data['SP_VolumeFlow_GPM'].min(), self.data['SP_VolumeFlow_GPM'].max()],
                      [self.data['SP_VolumeFlow_GPM'].min(), self.data['SP_VolumeFlow_GPM'].max()],
                      'r--', linewidth=2, label='Perfect Control')
        axes[0,1].set_xlabel('SP (GPM)')
        axes[0,1].set_ylabel('PV (GPM)')
        axes[0,1].set_title('PV vs SP Correlation')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)

        # Control effort
        axes[1,0].plot(self.data.index, self.data['CV01_PumpSpeed_Hz'], color='green', linewidth=1)
        axes[1,0].set_xlabel('Sample Index')
        axes[1,0].set_ylabel('Pump Speed (Hz)')
        axes[1,0].set_title('Control Effort - Pump Speed Variation')
        axes[1,0].grid(True, alpha=0.3)

        # Rolling statistics
        window = 100
        rolling_error = error.rolling(window=window).std()
        axes[1,1].plot(self.data.index[window:], rolling_error[window:],
                      color='red', linewidth=2, label=f'Rolling Error Std ({window} samples)')
        axes[1,1].set_xlabel('Sample Index')
        axes[1,1].set_ylabel('Error Std (GPM)')
        axes[1,1].set_title('Control Performance Over Time')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"{output_dir}/still01_bf_pid_performance.png", dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Visualizations saved to: {output_dir}")

    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run complete analysis following AI Task Orchestrator methodology"""
        print("=" * 60)
        print("STILL01 BF PID CONTROL LOOP ANALYSIS")
        print("=" * 60)

        # Step 1: Load dataset
        self.load_dataset()

        # Step 2: Calculate PID performance metrics
        print("\n🔍 Calculating PID Performance Metrics...")
        pid_metrics = self.calculate_pid_performance_metrics()

        # Step 3: Analyze control loop behavior
        print("\n📊 Analyzing Control Loop Behavior...")
        loop_behavior = self.analyze_control_loop_behavior()

        # Step 4: Generate visualizations
        print("\n📈 Generating Visualizations...")
        self.generate_visualizations()

        # Compile comprehensive results
        self.analysis_results = {
            'session_info': {
                'session_id': self.session_id,
                'dataset_path': self.dataset_path,
                'analysis_timestamp': datetime.now().isoformat(),
                'data_points': len(self.data),
                'time_span_minutes': len(self.data) * 5 / 60
            },
            'pid_configuration': {
                'kp': self.pid_config.kp,
                'ki': self.pid_config.ki,
                'kd': self.pid_config.kd,
                'update_rate_ms': self.pid_config.update_rate_ms,
                'control_action': self.pid_config.control_action,
                'equation_form': self.pid_config.pid_equation
            },
            'performance_metrics': pid_metrics,
            'control_loop_behavior': loop_behavior,
            'recommendations': self.generate_recommendations(pid_metrics)
        }

        # Save results
        results_file = f"plc-gbt-stack/results/control_loop_analysis/{self.session_id}/analysis_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)

        print(f"\n✅ Analysis complete! Results saved to: {results_file}")
        return self.analysis_results

    def generate_recommendations(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate PID tuning and performance recommendations"""
        recommendations = []

        # Analyze tracking accuracy
        tracking_accuracy = metrics['performance_indicators']['tracking_accuracy']
        if tracking_accuracy < 95:
            recommendations.append({
                'category': 'Performance',
                'priority': 'High',
                'issue': f'Low tracking accuracy: {tracking_accuracy:.1f}%',
                'recommendation': 'Consider increasing proportional gain (Kp) for better tracking',
                'current_kp': self.pid_config.kp,
                'suggested_kp_range': f"{self.pid_config.kp * 1.2:.3f} - {self.pid_config.kp * 1.5:.3f}"
            })

        # Analyze steady-state error
        ss_error = abs(metrics['performance_indicators']['steady_state_error'])
        if ss_error > 0.1:  # 0.1 GPM threshold
            recommendations.append({
                'category': 'Steady State',
                'priority': 'Medium',
                'issue': f'Steady-state error: {ss_error:.3f} GPM',
                'recommendation': 'Consider increasing integral gain (Ki) to eliminate steady-state error',
                'current_ki': self.pid_config.ki,
                'suggested_ki_range': f"{self.pid_config.ki * 1.1:.4f} - {self.pid_config.ki * 1.3:.4f}"
            })

        # Analyze control effort
        control_effort = metrics['performance_indicators']['control_effort']
        if control_effort > 5.0:  # 5 Hz threshold
            recommendations.append({
                'category': 'Stability',
                'priority': 'Medium',
                'issue': f'High control effort variability: {control_effort:.2f} Hz',
                'recommendation': 'Consider reducing derivative gain (Kd) to smooth control action',
                'current_kd': self.pid_config.kd,
                'suggested_kd_range': f"{self.pid_config.kd * 0.7:.4f} - {self.pid_config.kd * 0.9:.4f}"
            })

        return recommendations

    def print_summary(self) -> None:
        """Print analysis summary"""
        if not self.analysis_results:
            print("No analysis results available. Run comprehensive analysis first.")
            return

        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)

        metrics = self.analysis_results['performance_metrics']

        print(f"📊 Control Loop: {metrics['control_loop_type']}")
        print(f"📈 Tracking Accuracy: {metrics['performance_indicators']['tracking_accuracy']:.1f}%")
        print(f"🎯 Steady-State Error: {metrics['performance_indicators']['steady_state_error']:.3f} GPM")
        print(f"⚡ Control Effort: {metrics['performance_indicators']['control_effort']:.2f} Hz")
        print(f"📉 RMS Error: {metrics['process_variables']['error_stats']['rms']:.3f} GPM")

        print("\n🔧 PID Parameters:")
        print(f"   Kp: {self.pid_config.kp}")
        print(f"   Ki: {self.pid_config.ki}")
        print(f"   Kd: {self.pid_config.kd}")

        print(f"\n💡 Recommendations ({len(self.analysis_results['recommendations'])}):")
        for rec in self.analysis_results['recommendations']:
            print(f"   [{rec['priority']}] {rec['category']}: {rec['recommendation']}")

def main():
    """Main execution function"""
    # Dataset configuration
    dataset_path = "/Users/reh3376/repos/plc-gbt/docs/data/still01-bf-pid.csv"

    # PID configuration from user input
    pid_config = PIDConfiguration(
        instruction="PID",
        update_rate_ms=750,
        bias_calculation=False,
        pv_tracking=True,
        pid_equation="Independent",
        control_action="SP - PV",
        derivative_of="PV",
        kp=0.625,
        ki=0.0235,
        kd=0.0012
    )

    # Create and run analyzer
    analyzer = Still01BFPIDAnalyzer(dataset_path, pid_config)

    try:
        # Run comprehensive analysis
        results = analyzer.run_comprehensive_analysis()

        # Print summary
        analyzer.print_summary()

        return results

    except Exception as e:
        print(f"Analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()
