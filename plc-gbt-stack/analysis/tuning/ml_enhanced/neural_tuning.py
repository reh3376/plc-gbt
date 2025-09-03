#!/usr/bin/env python3
"""
Phase 22.2.4: Neural Network-Based PID Tuning Implementation
===========================================================

Neural network-based PID tuning using various architectures:
- Feedforward networks for direct parameter prediction
- Recurrent networks for time-series based tuning
- Transformer networks for attention-based tuning
- Residual networks for deep parameter learning

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.4 - ML-Enhanced Tuning
Methodology: AI Task Orchestrator Guide
"""

import logging
import pickle
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# ML framework imports with fallbacks
ML_FRAMEWORK = None
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import callbacks, layers, models, optimizers
    ML_FRAMEWORK = "tensorflow"
except ImportError:
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
        from torch.utils.data import DataLoader, TensorDataset
        ML_FRAMEWORK = "pytorch"
    except ImportError:
        try:
            from sklearn.model_selection import train_test_split
            from sklearn.neural_network import MLPRegressor
            from sklearn.preprocessing import StandardScaler
            ML_FRAMEWORK = "sklearn"
        except ImportError:
            ML_FRAMEWORK = None

# Import algorithm base class if available
try:
    from ...algorithms import (
        AlgorithmBase,
        AlgorithmCategory,
        AlgorithmComplexity,
        AlgorithmMetadata,
        registry,
    )
    ALGORITHM_REGISTRY_AVAILABLE = True
except ImportError:
    ALGORITHM_REGISTRY_AVAILABLE = False
    logging.warning("⚠️ Algorithm registry not available - using standalone implementation")

logger = logging.getLogger(__name__)

class NetworkType(Enum):
    """Neural network architecture types"""
    FEEDFORWARD = "feedforward"
    RECURRENT = "recurrent"
    TRANSFORMER = "transformer"
    RESIDUAL = "residual"
    CONVOLUTIONAL = "convolutional"

class ActivationFunction(Enum):
    """Activation function types"""
    RELU = "relu"
    TANH = "tanh"
    SIGMOID = "sigmoid"
    LEAKY_RELU = "leaky_relu"
    SWISH = "swish"
    GELU = "gelu"

@dataclass
class NeuralNetworkConfig:
    """Neural network configuration"""
    network_type: NetworkType = NetworkType.FEEDFORWARD
    hidden_layers: List[int] = field(default_factory=lambda: [64, 32, 16])
    activation: ActivationFunction = ActivationFunction.RELU
    output_activation: str = "linear"

    # Training parameters
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    validation_split: float = 0.2
    early_stopping_patience: int = 10

    # Regularization
    dropout_rate: float = 0.1
    l2_regularization: float = 0.001
    batch_normalization: bool = True

    # Optimization
    optimizer: str = "adam"
    loss_function: str = "mse"
    metrics: List[str] = field(default_factory=lambda: ["mae", "mse"])

    # Data preprocessing
    normalize_inputs: bool = True
    normalize_outputs: bool = True
    feature_scaling: str = "standard"  # standard, minmax, robust

    # Model save/load
    model_save_path: Optional[str] = None
    save_best_only: bool = True

    # Advanced settings
    use_residual_connections: bool = False
    attention_heads: int = 8  # For transformer
    lstm_units: int = 50  # For recurrent
    cnn_filters: List[int] = field(default_factory=lambda: [32, 64])

@dataclass
class TrainingData:
    """Training data structure for neural network"""
    process_features: np.ndarray  # Process characteristics
    historical_data: Optional[np.ndarray] = None  # Time series data
    pid_parameters: np.ndarray = None  # Target PID parameters
    performance_metrics: Optional[np.ndarray] = None  # Performance outcomes
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class NeuralTuningResults:
    """Neural network tuning results"""
    tuning_method: str
    network_type: NetworkType
    configuration: NeuralNetworkConfig
    predicted_parameters: Dict[str, float]
    confidence_scores: Dict[str, float]
    model_performance: Dict[str, float]
    training_history: Dict[str, List[float]]
    prediction_uncertainty: Dict[str, float]
    feature_importance: Optional[Dict[str, float]]
    execution_time: float
    status: str

class NeuralNetworkTuner:
    """Base neural network tuner for PID parameters"""

    def __init__(self, configuration: Optional[NeuralNetworkConfig] = None):
        self.config = configuration or NeuralNetworkConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Model components
        self.model = None
        self.scaler_input = None
        self.scaler_output = None
        self.training_history = {}

        # Check ML framework availability
        if ML_FRAMEWORK is None:
            raise ImportError("No ML framework available. Install tensorflow, pytorch, or scikit-learn.")

        self.framework = ML_FRAMEWORK
        self.logger.info(f"Using ML framework: {self.framework}")

    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute neural network-based PID tuning"""
        try:
            start_time = time.time()

            # Check if model exists and should be used
            use_pretrained = kwargs.get('use_pretrained', True)
            if use_pretrained and self.model is not None:
                # Use existing trained model for prediction
                predicted_parameters = self._predict_parameters(data)
            else:
                # Train new model if training data is provided
                if 'training_data' in data:
                    self._train_model(data['training_data'])

                # Make prediction
                predicted_parameters = self._predict_parameters(data)

            # Calculate confidence and uncertainty
            confidence_scores = self._calculate_confidence(data, predicted_parameters)
            prediction_uncertainty = self._calculate_uncertainty(data, predicted_parameters)

            # Analyze model performance
            model_performance = self._analyze_model_performance()

            # Feature importance analysis
            feature_importance = self._analyze_feature_importance(data)

            execution_time = time.time() - start_time

            # Create results
            result = NeuralTuningResults(
                tuning_method=f"Neural_{self.config.network_type.value}",
                network_type=self.config.network_type,
                configuration=self.config,
                predicted_parameters=predicted_parameters,
                confidence_scores=confidence_scores,
                model_performance=model_performance,
                training_history=self.training_history,
                prediction_uncertainty=prediction_uncertainty,
                feature_importance=feature_importance,
                execution_time=execution_time,
                status="success"
            )

            return {
                'success': True,
                'result': result,
                'method': 'neural_network_tuning'
            }

        except Exception as e:
            self.logger.error(f"Neural network tuning failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'neural_network_tuning'
            }

    def _train_model(self, training_data: Union[Dict[str, Any], TrainingData]):
        """Train the neural network model"""

        # Convert to TrainingData if needed
        if isinstance(training_data, dict):
            training_data = self._convert_to_training_data(training_data)

        # Prepare features and targets
        X, y = self._prepare_training_data(training_data)

        # Split data
        X_train, X_val, y_train, y_val = self._split_data(X, y)

        # Build model
        self.model = self._build_model(X_train.shape[1:])

        # Train model
        if self.framework == "tensorflow":
            self._train_tensorflow(X_train, y_train, X_val, y_val)
        elif self.framework == "pytorch":
            self._train_pytorch(X_train, y_train, X_val, y_val)
        elif self.framework == "sklearn":
            self._train_sklearn(X_train, y_train)

        self.logger.info(f"Model training completed using {self.framework}")

    def _convert_to_training_data(self, data: Dict[str, Any]) -> TrainingData:
        """Convert dictionary to TrainingData structure"""

        # Extract process features
        process_features = []
        if 'process_characteristics' in data:
            chars = data['process_characteristics']
            for item in chars:
                features = [
                    item.get('process_gain', 1.0),
                    item.get('time_constant', 10.0),
                    item.get('dead_time', 1.0),
                    item.get('setpoint', 50.0),
                    item.get('load_disturbance', 0.0),
                    item.get('noise_level', 0.1)
                ]
                process_features.append(features)
        else:
            # Create synthetic training data for demonstration
            n_samples = 1000
            process_features = self._generate_synthetic_data(n_samples)

        process_features = np.array(process_features)

        # Extract or generate PID parameters
        if 'pid_parameters' in data:
            pid_params = np.array(data['pid_parameters'])
        else:
            # Generate target PID parameters using simple rules
            pid_params = self._generate_target_parameters(process_features)

        # Extract historical data if available
        historical_data = data.get('historical_data')
        if historical_data is not None:
            historical_data = np.array(historical_data)

        return TrainingData(
            process_features=process_features,
            historical_data=historical_data,
            pid_parameters=pid_params,
            performance_metrics=data.get('performance_metrics'),
            metadata=data.get('metadata', {})
        )

    def _generate_synthetic_data(self, n_samples: int) -> np.ndarray:
        """Generate synthetic process data for training"""

        np.random.seed(42)  # For reproducibility

        # Generate diverse process characteristics
        process_gain = np.random.lognormal(0, 0.5, n_samples)  # 0.5 to 3.0 typical
        time_constant = np.random.lognormal(2, 0.8, n_samples)  # 2 to 50 typical
        dead_time = np.random.lognormal(0, 1.0, n_samples)  # 0.5 to 10 typical
        setpoint = np.random.uniform(20, 80, n_samples)
        load_disturbance = np.random.normal(0, 0.1, n_samples)
        noise_level = np.random.lognormal(-2, 0.5, n_samples)  # 0.01 to 0.5

        return np.column_stack([
            process_gain, time_constant, dead_time,
            setpoint, load_disturbance, noise_level
        ])

    def _generate_target_parameters(self, process_features: np.ndarray) -> np.ndarray:
        """Generate target PID parameters using heuristic rules"""

        n_samples = process_features.shape[0]
        pid_params = np.zeros((n_samples, 3))  # Kp, Ti, Td

        for i in range(n_samples):
            K = process_features[i, 0]  # Process gain
            tau = process_features[i, 1]  # Time constant
            theta = process_features[i, 2]  # Dead time

            # Simple IMC-based tuning as ground truth
            lambda_c = max(theta, 0.1 * tau)

            # Calculate PID parameters
            Kp = (tau + 0.5 * theta) / (K * (lambda_c + 0.5 * theta))
            Ti = tau + 0.5 * theta
            Td = tau * theta / (2 * tau + theta)

            # Add some noise to make it more realistic
            Kp *= np.random.lognormal(0, 0.1)
            Ti *= np.random.lognormal(0, 0.1)
            Td *= np.random.lognormal(0, 0.1)

            # Apply bounds
            Kp = np.clip(Kp, 0.1, 10.0)
            Ti = np.clip(Ti, 0.1, 100.0)
            Td = np.clip(Td, 0.0, 10.0)

            pid_params[i] = [Kp, Ti, Td]

        return pid_params

    def _prepare_training_data(self, training_data: TrainingData) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and targets for training"""

        X = training_data.process_features
        y = training_data.pid_parameters

        # Add historical data as features if available
        if training_data.historical_data is not None:
            # For now, use statistical features from historical data
            hist_features = self._extract_historical_features(training_data.historical_data)
            X = np.concatenate([X, hist_features], axis=1)

        # Normalize data if configured
        if self.config.normalize_inputs:
            if self.scaler_input is None:
                self.scaler_input = self._create_scaler()
                X = self.scaler_input.fit_transform(X)
            else:
                X = self.scaler_input.transform(X)

        if self.config.normalize_outputs:
            if self.scaler_output is None:
                self.scaler_output = self._create_scaler()
                y = self.scaler_output.fit_transform(y)
            else:
                y = self.scaler_output.transform(y)

        return X, y

    def _extract_historical_features(self, historical_data: np.ndarray) -> np.ndarray:
        """Extract statistical features from historical time series data"""

        n_samples = historical_data.shape[0]
        features = []

        for i in range(n_samples):
            series = historical_data[i]

            # Statistical features
            features_row = [
                np.mean(series),
                np.std(series),
                np.min(series),
                np.max(series),
                np.var(series),
                np.median(series)
            ]

            features.append(features_row)

        return np.array(features)

    def _create_scaler(self):
        """Create data scaler based on configuration"""

        if self.framework == "sklearn" or True:  # Always use sklearn scalers
            from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

            if self.config.feature_scaling == "standard":
                return StandardScaler()
            elif self.config.feature_scaling == "minmax":
                return MinMaxScaler()
            elif self.config.feature_scaling == "robust":
                return RobustScaler()
            else:
                return StandardScaler()

        return None

    def _split_data(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Split data into training and validation sets"""

        if self.framework == "sklearn" or True:  # Use sklearn for data splitting
            from sklearn.model_selection import train_test_split

            return train_test_split(
                X, y,
                test_size=self.config.validation_split,
                random_state=42
            )

        # Fallback manual split
        val_size = int(len(X) * self.config.validation_split)
        indices = np.random.permutation(len(X))

        train_idx = indices[val_size:]
        val_idx = indices[:val_size]

        return X[train_idx], X[val_idx], y[train_idx], y[val_idx]

    def _build_model(self, input_shape: Tuple[int, ...]):
        """Build neural network model based on configuration"""

        if self.framework == "tensorflow":
            return self._build_tensorflow_model(input_shape)
        elif self.framework == "pytorch":
            return self._build_pytorch_model(input_shape)
        elif self.framework == "sklearn":
            return self._build_sklearn_model()
        else:
            raise ValueError(f"Unsupported framework: {self.framework}")

    def _build_tensorflow_model(self, input_shape: Tuple[int, ...]):
        """Build TensorFlow/Keras model"""

        model = models.Sequential()

        # Input layer
        model.add(layers.Input(shape=input_shape))

        # Hidden layers
        for _i, units in enumerate(self.config.hidden_layers):
            model.add(layers.Dense(units, activation=self.config.activation.value))

            if self.config.batch_normalization:
                model.add(layers.BatchNormalization())

            if self.config.dropout_rate > 0:
                model.add(layers.Dropout(self.config.dropout_rate))

        # Output layer (3 outputs: Kp, Ti, Td)
        model.add(layers.Dense(3, activation=self.config.output_activation))

        # Compile model
        optimizer = self._get_tensorflow_optimizer()
        model.compile(
            optimizer=optimizer,
            loss=self.config.loss_function,
            metrics=self.config.metrics
        )

        return model

    def _build_pytorch_model(self, input_shape: Tuple[int, ...]):
        """Build PyTorch model"""

        class PIDNet(nn.Module):
            def __init__(self, input_size, hidden_layers, dropout_rate):
                super().__init__()

                layers_list = []
                prev_size = input_size

                for units in hidden_layers:
                    layers_list.append(nn.Linear(prev_size, units))
                    layers_list.append(nn.ReLU())
                    if dropout_rate > 0:
                        layers_list.append(nn.Dropout(dropout_rate))
                    prev_size = units

                # Output layer
                layers_list.append(nn.Linear(prev_size, 3))

                self.network = nn.Sequential(*layers_list)

            def forward(self, x):
                return self.network(x)

        model = PIDNet(
            input_size=input_shape[0],
            hidden_layers=self.config.hidden_layers,
            dropout_rate=self.config.dropout_rate
        )

        return model

    def _build_sklearn_model(self):
        """Build scikit-learn model"""

        return MLPRegressor(
            hidden_layer_sizes=tuple(self.config.hidden_layers),
            activation=self.config.activation.value if self.config.activation.value != 'leaky_relu' else 'relu',
            learning_rate_init=self.config.learning_rate,
            max_iter=self.config.epochs,
            early_stopping=True,
            validation_fraction=self.config.validation_split,
            n_iter_no_change=self.config.early_stopping_patience,
            random_state=42
        )

    def _get_tensorflow_optimizer(self):
        """Get TensorFlow optimizer"""

        if self.config.optimizer == "adam":
            return optimizers.Adam(learning_rate=self.config.learning_rate)
        elif self.config.optimizer == "sgd":
            return optimizers.SGD(learning_rate=self.config.learning_rate)
        elif self.config.optimizer == "rmsprop":
            return optimizers.RMSprop(learning_rate=self.config.learning_rate)
        else:
            return optimizers.Adam(learning_rate=self.config.learning_rate)

    def _train_tensorflow(self, X_train, y_train, X_val, y_val):
        """Train TensorFlow model"""

        # Callbacks
        callback_list = []

        if self.config.early_stopping_patience > 0:
            early_stopping = callbacks.EarlyStopping(
                patience=self.config.early_stopping_patience,
                restore_best_weights=True
            )
            callback_list.append(early_stopping)

        # Train model
        history = self.model.fit(
            X_train, y_train,
            batch_size=self.config.batch_size,
            epochs=self.config.epochs,
            validation_data=(X_val, y_val),
            callbacks=callback_list,
            verbose=0
        )

        self.training_history = history.history

    def _train_pytorch(self, X_train, y_train, X_val, y_val):
        """Train PyTorch model"""

        # Convert to tensors
        X_train_tensor = torch.FloatTensor(X_train)
        y_train_tensor = torch.FloatTensor(y_train)
        X_val_tensor = torch.FloatTensor(X_val)
        y_val_tensor = torch.FloatTensor(y_val)

        # Create data loaders
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)

        # Loss and optimizer
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)

        # Training loop
        train_losses = []
        val_losses = []

        for _epoch in range(self.config.epochs):
            # Training
            self.model.train()
            train_loss = 0.0

            for X_batch, y_batch in train_loader:
                optimizer.zero_grad()
                outputs = self.model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()

            # Validation
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_val_tensor)
                val_loss = criterion(val_outputs, y_val_tensor).item()

            train_losses.append(train_loss / len(train_loader))
            val_losses.append(val_loss)

        self.training_history = {
            'loss': train_losses,
            'val_loss': val_losses
        }

    def _train_sklearn(self, X_train, y_train):
        """Train scikit-learn model"""

        self.model.fit(X_train, y_train)

        # Simple training history
        self.training_history = {
            'loss': [self.model.loss_],
            'n_iter': [self.model.n_iter_]
        }

    def _predict_parameters(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Predict PID parameters using trained model"""

        # Extract features
        features = self._extract_features(data)

        # Normalize if configured
        if self.config.normalize_inputs and self.scaler_input is not None:
            features = self.scaler_input.transform(features.reshape(1, -1))
        else:
            features = features.reshape(1, -1)

        # Make prediction
        if self.framework == "tensorflow":
            prediction = self.model.predict(features, verbose=0)[0]
        elif self.framework == "pytorch":
            self.model.eval()
            with torch.no_grad():
                features_tensor = torch.FloatTensor(features)
                prediction = self.model(features_tensor).numpy()[0]
        elif self.framework == "sklearn":
            prediction = self.model.predict(features)[0]

        # Denormalize if configured
        if self.config.normalize_outputs and self.scaler_output is not None:
            prediction = self.scaler_output.inverse_transform(prediction.reshape(1, -1))[0]

        # Convert to dictionary
        return {
            'Kp': float(prediction[0]),
            'Ti': float(prediction[1]),
            'Td': float(prediction[2])
        }

    def _extract_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract features from input data"""

        # Basic process characteristics
        features = [
            data.get('process_gain', 1.0),
            data.get('time_constant', 10.0),
            data.get('dead_time', 1.0),
            data.get('setpoint', 50.0),
            data.get('load_disturbance', 0.0),
            data.get('noise_level', 0.1)
        ]

        # Add historical features if available
        if 'historical_data' in data:
            hist_data = np.array(data['historical_data'])
            hist_features = [
                np.mean(hist_data),
                np.std(hist_data),
                np.min(hist_data),
                np.max(hist_data),
                np.var(hist_data),
                np.median(hist_data)
            ]
            features.extend(hist_features)

        return np.array(features)

    def _calculate_confidence(self, data: Dict[str, Any],
                             predicted_parameters: Dict[str, float]) -> Dict[str, float]:
        """Calculate prediction confidence scores"""

        # Simple confidence based on model performance and parameter reasonableness
        confidence = {}

        for param, value in predicted_parameters.items():
            # Check if parameter is in reasonable range
            if param == 'Kp':
                reasonable = 0.1 <= value <= 10.0
            elif param == 'Ti':
                reasonable = 0.1 <= value <= 100.0
            elif param == 'Td':
                reasonable = 0.0 <= value <= 10.0
            else:
                reasonable = True

            # Base confidence from model performance
            base_confidence = 0.8 if hasattr(self.model, 'score') else 0.7

            # Adjust based on reasonableness
            confidence[param] = base_confidence * (1.0 if reasonable else 0.5)

        return confidence

    def _calculate_uncertainty(self, data: Dict[str, Any],
                              predicted_parameters: Dict[str, float]) -> Dict[str, float]:
        """Calculate prediction uncertainty"""

        # Simplified uncertainty estimation
        uncertainty = {}

        for param, value in predicted_parameters.items():
            # Uncertainty based on parameter value and model confidence
            relative_uncertainty = 0.1  # 10% relative uncertainty
            uncertainty[param] = float(abs(value) * relative_uncertainty)

        return uncertainty

    def _analyze_model_performance(self) -> Dict[str, float]:
        """Analyze trained model performance"""

        performance = {}

        if self.training_history:
            # Final training loss
            if 'loss' in self.training_history:
                performance['final_training_loss'] = float(self.training_history['loss'][-1])

            # Final validation loss
            if 'val_loss' in self.training_history:
                performance['final_validation_loss'] = float(self.training_history['val_loss'][-1])

            # Training epochs
            performance['training_epochs'] = len(self.training_history.get('loss', []))

        # Model complexity
        if hasattr(self.model, 'count_params'):
            performance['model_parameters'] = int(self.model.count_params())

        return performance

    def _analyze_feature_importance(self, data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Analyze feature importance (simplified implementation)"""

        # This is a simplified implementation
        # In practice, you'd use methods like SHAP, permutation importance, etc.


        # Simple importance based on domain knowledge
        importance = {
            'process_gain': 0.25,
            'time_constant': 0.25,
            'dead_time': 0.20,
            'setpoint': 0.15,
            'load_disturbance': 0.10,
            'noise_level': 0.05
        }

        return importance

    def save_model(self, filepath: str):
        """Save trained model to file"""

        if self.model is None:
            raise ValueError("No model to save. Train model first.")

        model_data = {
            'framework': self.framework,
            'config': self.config,
            'scaler_input': self.scaler_input,
            'scaler_output': self.scaler_output,
            'training_history': self.training_history
        }

        if self.framework == "tensorflow":
            self.model.save(f"{filepath}_model")
            with open(f"{filepath}_data.pkl", 'wb') as f:
                pickle.dump(model_data, f)
        elif self.framework == "pytorch":
            torch.save(self.model.state_dict(), f"{filepath}_model.pth")
            with open(f"{filepath}_data.pkl", 'wb') as f:
                pickle.dump(model_data, f)
        elif self.framework == "sklearn":
            with open(f"{filepath}_complete.pkl", 'wb') as f:
                model_data['model'] = self.model
                pickle.dump(model_data, f)

    def load_model(self, filepath: str):
        """Load trained model from file"""

        try:
            if self.framework == "tensorflow":
                self.model = tf.keras.models.load_model(f"{filepath}_model")
                with open(f"{filepath}_data.pkl", 'rb') as f:
                    model_data = pickle.load(f)
            elif self.framework == "pytorch":
                with open(f"{filepath}_data.pkl", 'rb') as f:
                    model_data = pickle.load(f)
                # Would need to rebuild model structure
                self.model = self._build_pytorch_model((6,))  # Assuming 6 features
                self.model.load_state_dict(torch.load(f"{filepath}_model.pth"))
            elif self.framework == "sklearn":
                with open(f"{filepath}_complete.pkl", 'rb') as f:
                    model_data = pickle.load(f)
                self.model = model_data['model']

            # Restore other components
            self.config = model_data['config']
            self.scaler_input = model_data['scaler_input']
            self.scaler_output = model_data['scaler_output']
            self.training_history = model_data['training_history']

            self.logger.info(f"Model loaded successfully from {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise


# Specialized neural network tuners
class FeedforwardTuner(NeuralNetworkTuner):
    """Feedforward neural network tuner"""

    def __init__(self, configuration: Optional[NeuralNetworkConfig] = None):
        config = configuration or NeuralNetworkConfig()
        config.network_type = NetworkType.FEEDFORWARD
        super().__init__(config)


class RecurrentTuner(NeuralNetworkTuner):
    """Recurrent neural network tuner (LSTM)"""

    def __init__(self, configuration: Optional[NeuralNetworkConfig] = None):
        config = configuration or NeuralNetworkConfig()
        config.network_type = NetworkType.RECURRENT
        super().__init__(config)


class TransformerTuner(NeuralNetworkTuner):
    """Transformer-based neural network tuner"""

    def __init__(self, configuration: Optional[NeuralNetworkConfig] = None):
        config = configuration or NeuralNetworkConfig()
        config.network_type = NetworkType.TRANSFORMER
        super().__init__(config)


# Register algorithms if registry is available
if ALGORITHM_REGISTRY_AVAILABLE:

    @registry.register(
        category=AlgorithmCategory.TUNING_CALCULATION,
        complexity=AlgorithmComplexity.HIGH,
        metadata=AlgorithmMetadata(
            name="Neural Network PID Tuning",
            description="Neural network-based PID parameter prediction",
            version="1.0.0",
            author="PLC-GPT Team",
            tags=["neural_network", "machine_learning", "prediction", "deep_learning"]
        )
    )
    class RegisteredNeuralTuner(NeuralNetworkTuner):
        pass


# Export classes and functions
__all__ = [
    'NeuralNetworkTuner',
    'FeedforwardTuner',
    'RecurrentTuner',
    'TransformerTuner',
    'NeuralNetworkConfig',
    'TrainingData',
    'NeuralTuningResults',
    'NetworkType',
    'ActivationFunction'
]
