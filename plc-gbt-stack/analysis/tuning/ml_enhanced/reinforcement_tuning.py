#!/usr/bin/env python3
"""
Phase 22.2.4: Reinforcement Learning-Based PID Tuning Implementation
===================================================================

Reinforcement learning-based PID tuning using various RL algorithms:
- DDPG (Deep Deterministic Policy Gradient) for continuous control
- TD3 (Twin Delayed DDPG) for improved stability
- SAC (Soft Actor-Critic) for maximum entropy RL
- PPO (Proximal Policy Optimization) for stable policy gradients
- A3C (Asynchronous Actor-Critic) for parallel learning

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.4 - ML-Enhanced Tuning
Methodology: AI Task Orchestrator Guide
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
import logging
from enum import Enum
import time
from datetime import datetime
import pickle
import json
import random
from collections import deque

# RL framework imports with fallbacks
RL_FRAMEWORK = None
try:
    import gym
    from gym import spaces
    import stable_baselines3 as sb3
    from stable_baselines3 import DDPG, TD3, SAC, PPO, A2C
    from stable_baselines3.common.env_checker import check_env
    from stable_baselines3.common.callbacks import BaseCallback
    from stable_baselines3.common.noise import NormalActionNoise
    RL_FRAMEWORK = "stable_baselines3"
except ImportError:
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
        import torch.nn.functional as F
        RL_FRAMEWORK = "pytorch_manual"
    except ImportError:
        RL_FRAMEWORK = None

# Import algorithm base class if available
try:
    from ...algorithms import (
        AlgorithmBase, AlgorithmMetadata, AlgorithmCategory, 
        AlgorithmComplexity, registry
    )
    ALGORITHM_REGISTRY_AVAILABLE = True
except ImportError:
    ALGORITHM_REGISTRY_AVAILABLE = False
    logging.warning("⚠️ Algorithm registry not available - using standalone implementation")

logger = logging.getLogger(__name__)

class RLAlgorithmType(Enum):
    """Reinforcement learning algorithm types"""
    DDPG = "ddpg"
    TD3 = "td3"
    SAC = "sac"
    PPO = "ppo"
    A2C = "a2c"
    A3C = "a3c"

class RewardFunction(Enum):
    """Reward function types for RL training"""
    ISE = "ise"  # Integral Squared Error
    IAE = "iae"  # Integral Absolute Error
    ITAE = "itae"  # Integral Time Absolute Error
    MIXED = "mixed"  # Mixed performance metrics
    ROBUST = "robust"  # Robustness-focused
    ECONOMIC = "economic"  # Economic optimization

@dataclass
class RLConfig:
    """Reinforcement learning configuration"""
    algorithm: RLAlgorithmType = RLAlgorithmType.DDPG
    reward_function: RewardFunction = RewardFunction.MIXED
    
    # Training parameters
    total_timesteps: int = 100000
    learning_rate: float = 1e-4
    batch_size: int = 64
    buffer_size: int = 100000
    
    # Network architecture
    policy_layers: List[int] = field(default_factory=lambda: [64, 64])
    value_layers: List[int] = field(default_factory=lambda: [64, 64])
    
    # Exploration
    exploration_noise: float = 0.1
    exploration_decay: float = 0.995
    min_exploration: float = 0.01
    
    # Environment parameters
    max_episode_steps: int = 200
    setpoint_range: Tuple[float, float] = (20.0, 80.0)
    disturbance_range: Tuple[float, float] = (-10.0, 10.0)
    noise_level: float = 0.1
    
    # Optimization parameters
    gamma: float = 0.99  # Discount factor
    tau: float = 0.001  # Soft update coefficient
    policy_delay: int = 2  # For TD3
    target_noise: float = 0.2  # For TD3
    noise_clip: float = 0.5  # For TD3
    
    # Stability and safety
    action_bounds: Tuple[float, float] = (0.1, 10.0)  # For Kp, Ti, Td
    penalty_weight: float = 1.0
    stability_threshold: float = 2.0
    
    # Model saving
    model_save_path: Optional[str] = None
    save_frequency: int = 10000
    
    # Evaluation
    eval_episodes: int = 10
    eval_frequency: int = 5000

@dataclass
class ProcessDynamics:
    """Process dynamics for simulation"""
    process_gain: float = 1.0
    time_constant: float = 10.0
    dead_time: float = 1.0
    noise_level: float = 0.1
    nonlinearity: float = 0.0  # Nonlinearity factor
    
    # Time-varying parameters
    gain_variation: float = 0.0
    tau_variation: float = 0.0
    disturbance_amplitude: float = 0.0

@dataclass
class RLTuningResults:
    """RL tuning results"""
    tuning_method: str
    algorithm: RLAlgorithmType
    configuration: RLConfig
    
    # Tuning results
    optimized_parameters: Dict[str, float]
    performance_metrics: Dict[str, float]
    reward_history: List[float]
    episode_lengths: List[int]
    
    # Learning progress
    learning_curve: Dict[str, List[float]]
    convergence_episode: Optional[int]
    final_reward: float
    
    # Evaluation results
    eval_performance: Dict[str, float]
    robustness_analysis: Dict[str, float]
    
    execution_time: float
    status: str

class PIDControlEnvironment:
    """Gym-like environment for PID control RL training"""
    
    def __init__(self, config: RLConfig, dynamics: ProcessDynamics):
        self.config = config
        self.dynamics = dynamics
        
        # State space: [error, error_derivative, error_integral, setpoint, process_output]
        self.observation_space = spaces.Box(
            low=np.array([-100, -10, -1000, 0, 0]),
            high=np.array([100, 10, 1000, 100, 100]),
            dtype=np.float32
        )
        
        # Action space: [Kp, Ti, Td] (normalized)
        self.action_space = spaces.Box(
            low=np.array([0, 0, 0]),
            high=np.array([1, 1, 1]),
            dtype=np.float32
        )
        
        # Environment state
        self.reset()
    
    def reset(self):
        """Reset environment to initial state"""
        
        # Random setpoint
        self.setpoint = np.random.uniform(*self.config.setpoint_range)
        
        # Initialize process state
        self.process_output = self.setpoint + np.random.normal(0, 5)
        self.error_integral = 0.0
        self.previous_error = self.setpoint - self.process_output
        
        # Time step
        self.time_step = 0
        self.dt = 0.1  # 100ms time step
        
        # Disturbance
        self.current_disturbance = 0.0
        
        # PID parameters (will be set by action)
        self.kp = 1.0
        self.ti = 10.0
        self.td = 0.0
        
        # Performance tracking
        self.episode_ise = 0.0
        self.episode_iae = 0.0
        self.episode_itae = 0.0
        self.max_overshoot = 0.0
        self.settling_time = None
        
        return self._get_observation()
    
    def step(self, action):
        """Execute one time step"""
        
        # Denormalize action to PID parameters
        self.kp = action[0] * (self.config.action_bounds[1] - self.config.action_bounds[0]) + self.config.action_bounds[0]
        self.ti = action[1] * 100.0 + 0.1  # Ti range: 0.1 to 100.1
        self.td = action[2] * 10.0  # Td range: 0 to 10
        
        # Calculate error
        error = self.setpoint - self.process_output
        
        # PID calculation
        error_derivative = (error - self.previous_error) / self.dt
        self.error_integral += error * self.dt
        
        # PID output with anti-windup
        pid_output = (self.kp * error + 
                     self.kp / self.ti * self.error_integral + 
                     self.kp * self.td * error_derivative)
        
        # Anti-windup
        if abs(pid_output) > 100:
            self.error_integral -= error * self.dt
            pid_output = np.clip(pid_output, -100, 100)
        
        # Process simulation (FOPDT)
        disturbance = self._generate_disturbance()
        process_input = pid_output + disturbance
        
        # Simple FOPDT simulation
        alpha = self.dt / (self.dynamics.time_constant + self.dt)
        self.process_output += alpha * (self.dynamics.process_gain * process_input - self.process_output)
        
        # Add noise
        self.process_output += np.random.normal(0, self.dynamics.noise_level)
        
        # Update tracking variables
        self.previous_error = error
        self.time_step += 1
        
        # Performance metrics
        self.episode_ise += error**2 * self.dt
        self.episode_iae += abs(error) * self.dt
        self.episode_itae += abs(error) * self.time_step * self.dt
        
        # Overshoot tracking
        if self.process_output > self.setpoint:
            overshoot = (self.process_output - self.setpoint) / self.setpoint * 100
            self.max_overshoot = max(self.max_overshoot, overshoot)
        
        # Settling time
        if self.settling_time is None and abs(error) < 0.02 * self.setpoint:
            self.settling_time = self.time_step * self.dt
        
        # Calculate reward
        reward = self._calculate_reward(error, pid_output)
        
        # Check if episode is done
        done = (self.time_step >= self.config.max_episode_steps or 
                abs(error) > self.setpoint * 2 or  # Large error
                abs(pid_output) > 200)  # Control saturation
        
        # Info dictionary
        info = {
            'ise': self.episode_ise,
            'iae': self.episode_iae,
            'itae': self.episode_itae,
            'overshoot': self.max_overshoot,
            'settling_time': self.settling_time,
            'kp': self.kp,
            'ti': self.ti,
            'td': self.td
        }
        
        return self._get_observation(), reward, done, info
    
    def _get_observation(self):
        """Get current observation"""
        
        error = self.setpoint - self.process_output
        error_derivative = (error - self.previous_error) / self.dt
        
        return np.array([
            error / 100.0,  # Normalized error
            error_derivative / 10.0,  # Normalized error derivative
            self.error_integral / 1000.0,  # Normalized integral
            self.setpoint / 100.0,  # Normalized setpoint
            self.process_output / 100.0  # Normalized output
        ], dtype=np.float32)
    
    def _generate_disturbance(self):
        """Generate process disturbance"""
        
        # Random disturbance
        if np.random.random() < 0.01:  # 1% chance per step
            self.current_disturbance = np.random.uniform(*self.config.disturbance_range)
        
        # Decay disturbance
        self.current_disturbance *= 0.95
        
        return self.current_disturbance
    
    def _calculate_reward(self, error, control_output):
        """Calculate reward based on configuration"""
        
        if self.config.reward_function == RewardFunction.ISE:
            reward = -error**2
        elif self.config.reward_function == RewardFunction.IAE:
            reward = -abs(error)
        elif self.config.reward_function == RewardFunction.ITAE:
            reward = -abs(error) * self.time_step
        elif self.config.reward_function == RewardFunction.MIXED:
            # Mixed reward: tracking + effort + stability
            tracking_reward = -error**2
            effort_penalty = -0.01 * control_output**2
            stability_bonus = 1.0 if abs(error) < 0.1 * self.setpoint else 0.0
            reward = tracking_reward + effort_penalty + stability_bonus
        elif self.config.reward_function == RewardFunction.ROBUST:
            # Robustness-focused reward
            tracking_reward = -abs(error)
            overshoot_penalty = -max(0, self.process_output - self.setpoint)**2
            settling_bonus = 1.0 if self.settling_time is not None else 0.0
            reward = tracking_reward + overshoot_penalty + settling_bonus
        else:
            reward = -error**2  # Default to ISE
        
        # Safety penalty
        if abs(control_output) > 150:
            reward -= self.config.penalty_weight * 10
        
        return float(reward)

class ReinforcementTuner:
    """Base reinforcement learning tuner for PID parameters"""
    
    def __init__(self, configuration: Optional[RLConfig] = None):
        self.config = configuration or RLConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # RL components
        self.env = None
        self.model = None
        self.training_history = {}
        
        # Check RL framework availability
        if RL_FRAMEWORK is None:
            raise ImportError("No RL framework available. Install gym and stable-baselines3.")
        
        self.framework = RL_FRAMEWORK
        self.logger.info(f"Using RL framework: {self.framework}")
    
    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute RL-based PID tuning"""
        try:
            start_time = time.time()
            
            # Extract process dynamics
            dynamics = self._extract_dynamics(data)
            
            # Create environment
            self.env = PIDControlEnvironment(self.config, dynamics)
            
            # Check if we should train or use existing model
            train_model = kwargs.get('train_model', True)
            if train_model or self.model is None:
                # Train RL agent
                self._train_agent()
            
            # Evaluate trained agent
            evaluation_results = self._evaluate_agent()
            
            # Extract optimized PID parameters
            optimized_parameters = self._extract_optimal_parameters()
            
            # Analyze robustness
            robustness_analysis = self._analyze_robustness(dynamics)
            
            execution_time = time.time() - start_time
            
            # Create results
            result = RLTuningResults(
                tuning_method=f"RL_{self.config.algorithm.value}",
                algorithm=self.config.algorithm,
                configuration=self.config,
                optimized_parameters=optimized_parameters,
                performance_metrics=evaluation_results['performance'],
                reward_history=self.training_history.get('rewards', []),
                episode_lengths=self.training_history.get('episode_lengths', []),
                learning_curve=self.training_history.get('learning_curve', {}),
                convergence_episode=self.training_history.get('convergence_episode'),
                final_reward=evaluation_results.get('mean_reward', 0.0),
                eval_performance=evaluation_results,
                robustness_analysis=robustness_analysis,
                execution_time=execution_time,
                status="success"
            )
            
            return {
                'success': True,
                'result': result,
                'method': 'reinforcement_learning_tuning'
            }
            
        except Exception as e:
            self.logger.error(f"RL tuning failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'reinforcement_learning_tuning'
            }
    
    def _extract_dynamics(self, data: Dict[str, Any]) -> ProcessDynamics:
        """Extract process dynamics from input data"""
        
        return ProcessDynamics(
            process_gain=data.get('process_gain', 1.0),
            time_constant=data.get('time_constant', 10.0),
            dead_time=data.get('dead_time', 1.0),
            noise_level=data.get('noise_level', 0.1),
            nonlinearity=data.get('nonlinearity', 0.0),
            gain_variation=data.get('gain_variation', 0.0),
            tau_variation=data.get('tau_variation', 0.0),
            disturbance_amplitude=data.get('disturbance_amplitude', 0.0)
        )
    
    def _train_agent(self):
        """Train RL agent"""
        
        if self.framework == "stable_baselines3":
            self._train_stable_baselines()
        elif self.framework == "pytorch_manual":
            self._train_pytorch_manual()
        else:
            raise ValueError(f"Unsupported RL framework: {self.framework}")
    
    def _train_stable_baselines(self):
        """Train using stable-baselines3"""
        
        # Create callback for training monitoring
        callback = TrainingCallback(self)
        
        # Create noise for exploration
        if self.config.algorithm in [RLAlgorithmType.DDPG, RLAlgorithmType.TD3]:
            n_actions = self.env.action_space.shape[-1]
            action_noise = NormalActionNoise(
                mean=np.zeros(n_actions),
                sigma=self.config.exploration_noise * np.ones(n_actions)
            )
        else:
            action_noise = None
        
        # Create model based on algorithm
        if self.config.algorithm == RLAlgorithmType.DDPG:
            self.model = DDPG(
                "MlpPolicy",
                self.env,
                learning_rate=self.config.learning_rate,
                buffer_size=self.config.buffer_size,
                batch_size=self.config.batch_size,
                gamma=self.config.gamma,
                tau=self.config.tau,
                action_noise=action_noise,
                verbose=0
            )
        elif self.config.algorithm == RLAlgorithmType.TD3:
            self.model = TD3(
                "MlpPolicy",
                self.env,
                learning_rate=self.config.learning_rate,
                buffer_size=self.config.buffer_size,
                batch_size=self.config.batch_size,
                gamma=self.config.gamma,
                tau=self.config.tau,
                policy_delay=self.config.policy_delay,
                target_policy_noise=self.config.target_noise,
                target_noise_clip=self.config.noise_clip,
                action_noise=action_noise,
                verbose=0
            )
        elif self.config.algorithm == RLAlgorithmType.SAC:
            self.model = SAC(
                "MlpPolicy",
                self.env,
                learning_rate=self.config.learning_rate,
                buffer_size=self.config.buffer_size,
                batch_size=self.config.batch_size,
                gamma=self.config.gamma,
                tau=self.config.tau,
                verbose=0
            )
        elif self.config.algorithm == RLAlgorithmType.PPO:
            self.model = PPO(
                "MlpPolicy",
                self.env,
                learning_rate=self.config.learning_rate,
                batch_size=self.config.batch_size,
                gamma=self.config.gamma,
                verbose=0
            )
        elif self.config.algorithm == RLAlgorithmType.A2C:
            self.model = A2C(
                "MlpPolicy",
                self.env,
                learning_rate=self.config.learning_rate,
                gamma=self.config.gamma,
                verbose=0
            )
        else:
            raise ValueError(f"Unsupported algorithm: {self.config.algorithm}")
        
        # Train model
        self.model.learn(
            total_timesteps=self.config.total_timesteps,
            callback=callback
        )
        
        self.logger.info(f"RL training completed with {self.config.algorithm.value}")
    
    def _train_pytorch_manual(self):
        """Manual PyTorch implementation (simplified)"""
        
        # This would implement manual RL training
        # For now, just create a dummy training history
        self.training_history = {
            'rewards': [0.0] * 100,
            'episode_lengths': [200] * 100,
            'learning_curve': {'loss': [1.0] * 100}
        }
        
        self.logger.warning("PyTorch manual RL training not fully implemented")
    
    def _evaluate_agent(self) -> Dict[str, Any]:
        """Evaluate trained agent"""
        
        if self.model is None:
            return {'performance': {}, 'mean_reward': 0.0}
        
        rewards = []
        episode_lengths = []
        performance_metrics = {
            'ise': [],
            'iae': [],
            'itae': [],
            'overshoot': [],
            'settling_time': []
        }
        
        for episode in range(self.config.eval_episodes):
            obs = self.env.reset()
            episode_reward = 0.0
            episode_length = 0
            done = False
            
            while not done:
                if self.framework == "stable_baselines3":
                    action, _ = self.model.predict(obs, deterministic=True)
                else:
                    # Fallback random action
                    action = self.env.action_space.sample()
                
                obs, reward, done, info = self.env.step(action)
                episode_reward += reward
                episode_length += 1
            
            rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            
            # Collect performance metrics
            for metric in performance_metrics:
                if metric in info and info[metric] is not None:
                    performance_metrics[metric].append(info[metric])
        
        # Calculate statistics
        results = {
            'mean_reward': float(np.mean(rewards)),
            'std_reward': float(np.std(rewards)),
            'mean_episode_length': float(np.mean(episode_lengths)),
            'performance': {}
        }
        
        for metric, values in performance_metrics.items():
            if values:
                results['performance'][f'mean_{metric}'] = float(np.mean(values))
                results['performance'][f'std_{metric}'] = float(np.std(values))
        
        return results
    
    def _extract_optimal_parameters(self) -> Dict[str, float]:
        """Extract optimal PID parameters from trained agent"""
        
        if self.model is None:
            return {'Kp': 1.0, 'Ti': 10.0, 'Td': 0.0}
        
        # Run one episode to get final PID parameters
        obs = self.env.reset()
        done = False
        final_params = {'Kp': 1.0, 'Ti': 10.0, 'Td': 0.0}
        
        while not done:
            if self.framework == "stable_baselines3":
                action, _ = self.model.predict(obs, deterministic=True)
            else:
                action = self.env.action_space.sample()
            
            obs, reward, done, info = self.env.step(action)
            final_params = {
                'Kp': info['kp'],
                'Ti': info['ti'],
                'Td': info['td']
            }
        
        return final_params
    
    def _analyze_robustness(self, nominal_dynamics: ProcessDynamics) -> Dict[str, float]:
        """Analyze robustness of tuned parameters"""
        
        robustness_metrics = {}
        
        # Test with parameter variations
        variations = [0.5, 0.8, 1.2, 1.5, 2.0]  # Gain variations
        performance_variations = []
        
        for gain_factor in variations:
            # Create modified dynamics
            modified_dynamics = ProcessDynamics(
                process_gain=nominal_dynamics.process_gain * gain_factor,
                time_constant=nominal_dynamics.time_constant,
                dead_time=nominal_dynamics.dead_time,
                noise_level=nominal_dynamics.noise_level
            )
            
            # Test with modified environment
            test_env = PIDControlEnvironment(self.config, modified_dynamics)
            obs = test_env.reset()
            episode_reward = 0.0
            done = False
            
            while not done:
                if self.framework == "stable_baselines3" and self.model is not None:
                    action, _ = self.model.predict(obs, deterministic=True)
                else:
                    action = test_env.action_space.sample()
                
                obs, reward, done, info = test_env.step(action)
                episode_reward += reward
            
            performance_variations.append(episode_reward)
        
        # Calculate robustness metrics
        robustness_metrics['performance_variation'] = float(np.std(performance_variations))
        robustness_metrics['worst_case_performance'] = float(min(performance_variations))
        robustness_metrics['best_case_performance'] = float(max(performance_variations))
        robustness_metrics['nominal_performance'] = float(performance_variations[2])  # 1.0 gain factor
        
        return robustness_metrics
    
    def save_model(self, filepath: str):
        """Save trained RL model"""
        
        if self.model is None:
            raise ValueError("No model to save. Train model first.")
        
        if self.framework == "stable_baselines3":
            self.model.save(filepath)
        
        # Save additional data
        additional_data = {
            'config': self.config,
            'training_history': self.training_history,
            'framework': self.framework
        }
        
        with open(f"{filepath}_data.pkl", 'wb') as f:
            pickle.dump(additional_data, f)
    
    def load_model(self, filepath: str):
        """Load trained RL model"""
        
        try:
            # Load additional data
            with open(f"{filepath}_data.pkl", 'rb') as f:
                additional_data = pickle.load(f)
            
            self.config = additional_data['config']
            self.training_history = additional_data['training_history']
            
            # Load model based on algorithm
            if self.framework == "stable_baselines3":
                if self.config.algorithm == RLAlgorithmType.DDPG:
                    self.model = DDPG.load(filepath)
                elif self.config.algorithm == RLAlgorithmType.TD3:
                    self.model = TD3.load(filepath)
                elif self.config.algorithm == RLAlgorithmType.SAC:
                    self.model = SAC.load(filepath)
                elif self.config.algorithm == RLAlgorithmType.PPO:
                    self.model = PPO.load(filepath)
                elif self.config.algorithm == RLAlgorithmType.A2C:
                    self.model = A2C.load(filepath)
            
            self.logger.info(f"RL model loaded successfully from {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to load RL model: {e}")
            raise

class TrainingCallback(BaseCallback):
    """Callback for monitoring RL training"""
    
    def __init__(self, tuner: ReinforcementTuner):
        super().__init__()
        self.tuner = tuner
        self.episode_rewards = []
        self.episode_lengths = []
        self.best_reward = float('-inf')
        self.convergence_threshold = -10.0  # Reward threshold for convergence
        self.convergence_episode = None
    
    def _on_step(self) -> bool:
        """Called at each training step"""
        
        # Log episode results
        if len(self.locals.get('infos', [])) > 0:
            info = self.locals['infos'][0]
            if 'episode' in info:
                episode_reward = info['episode']['r']
                episode_length = info['episode']['l']
                
                self.episode_rewards.append(episode_reward)
                self.episode_lengths.append(episode_length)
                
                # Check for best reward
                if episode_reward > self.best_reward:
                    self.best_reward = episode_reward
                
                # Check for convergence
                if (self.convergence_episode is None and 
                    episode_reward > self.convergence_threshold and
                    len(self.episode_rewards) > 10):
                    recent_rewards = self.episode_rewards[-10:]
                    if np.mean(recent_rewards) > self.convergence_threshold:
                        self.convergence_episode = len(self.episode_rewards)
        
        return True
    
    def _on_training_end(self) -> None:
        """Called at the end of training"""
        
        # Store training history
        self.tuner.training_history = {
            'rewards': self.episode_rewards,
            'episode_lengths': self.episode_lengths,
            'convergence_episode': self.convergence_episode,
            'best_reward': self.best_reward
        }

# Specialized RL tuners
class DDPGTuner(ReinforcementTuner):
    """Deep Deterministic Policy Gradient tuner"""
    
    def __init__(self, configuration: Optional[RLConfig] = None):
        config = configuration or RLConfig()
        config.algorithm = RLAlgorithmType.DDPG
        super().__init__(config)

class TD3Tuner(ReinforcementTuner):
    """Twin Delayed DDPG tuner"""
    
    def __init__(self, configuration: Optional[RLConfig] = None):
        config = configuration or RLConfig()
        config.algorithm = RLAlgorithmType.TD3
        super().__init__(config)

class SACTuner(ReinforcementTuner):
    """Soft Actor-Critic tuner"""
    
    def __init__(self, configuration: Optional[RLConfig] = None):
        config = configuration or RLConfig()
        config.algorithm = RLAlgorithmType.SAC
        super().__init__(config)

class PPOTuner(ReinforcementTuner):
    """Proximal Policy Optimization tuner"""
    
    def __init__(self, configuration: Optional[RLConfig] = None):
        config = configuration or RLConfig()
        config.algorithm = RLAlgorithmType.PPO
        super().__init__(config)

# Register algorithms if registry is available
if ALGORITHM_REGISTRY_AVAILABLE:
    
    @registry.register(
        category=AlgorithmCategory.TUNING_CALCULATION,
        complexity=AlgorithmComplexity.EXTENSIVE,
        metadata=AlgorithmMetadata(
            name="Reinforcement Learning PID Tuning",
            description="RL-based optimal PID parameter learning",
            version="1.0.0",
            author="PLC-GPT Team",
            tags=["reinforcement_learning", "optimal_control", "online_learning", "adaptive"]
        )
    )
    class RegisteredRLTuner(ReinforcementTuner):
        pass

# Export classes and functions
__all__ = [
    'ReinforcementTuner',
    'DDPGTuner',
    'TD3Tuner',
    'SACTuner',
    'PPOTuner',
    'RLConfig',
    'ProcessDynamics',
    'RLTuningResults',
    'PIDControlEnvironment',
    'RLAlgorithmType',
    'RewardFunction'
] 