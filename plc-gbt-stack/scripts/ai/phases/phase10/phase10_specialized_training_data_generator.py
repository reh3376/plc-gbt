#!/usr/bin/env python3
"""
Phase 10: Specialized Control Theory Training Data Generator
==========================================================

AI Task Orchestrator implementation for generating specialized control theory
Q&A pairs using the distillation control dataset for world's first Industrial
Control Theory LLM training.

Dataset: Distillation column control with 1M+ data points
Target: 10,000+ specialized Q&A pairs for control theory expertise

Author: PLC-GPT Development Team
Date: January 17, 2025
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import openai
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ControlScenario:
    """Data class for control scenarios"""
    scenario_type: str
    time_range: Tuple[str, str]
    pv_values: List[float]
    cv_values: List[float]
    sp_values: List[float]
    dv_values: Dict[str, List[float]]
    performance_metrics: Dict[str, float]
    description: str

class SpecializedTrainingDataGenerator:
    """
    Generate specialized control theory Q&A pairs from distillation dataset
    """

    def __init__(self, dataset_path: str):
        """Initialize the generator with dataset path"""
        self.dataset_path = Path(dataset_path)
        self.df = None
        self.openai_client = None
        self.session_id = f"phase10_training_{int(datetime.now().timestamp())}"

        # Training data categories with specialized focus
        self.training_categories = {
            'temperature_control': {
                'target_count': 2000,
                'description': 'Temperature control in distillation columns',
                'complexity_levels': ['basic', 'intermediate', 'advanced']
            },
            'pid_tuning': {
                'target_count': 1500,
                'description': 'PID controller tuning for temperature control',
                'complexity_levels': ['basic', 'intermediate', 'advanced']
            },
            'disturbance_rejection': {
                'target_count': 1500,
                'description': 'Disturbance rejection in process control',
                'complexity_levels': ['basic', 'intermediate', 'advanced']
            },
            'process_dynamics': {
                'target_count': 1000,
                'description': 'Process dynamics and system identification',
                'complexity_levels': ['intermediate', 'advanced']
            },
            'performance_analysis': {
                'target_count': 1000,
                'description': 'Control performance analysis and optimization',
                'complexity_levels': ['intermediate', 'advanced']
            },
            'mathematical_validation': {
                'target_count': 3000,
                'description': 'Mathematical validation of control calculations',
                'complexity_levels': ['basic', 'intermediate', 'advanced']
            }
        }

        # Initialize OpenAI client
        self.setup_openai_client()

    def setup_openai_client(self):
        """Setup OpenAI client for Q&A generation"""
        try:
            # Use the existing configuration
            openai.api_key = open('.env').read().split('OPENAI_API_KEY=')[1].split('\n')[0]
            self.openai_client = openai.OpenAI(api_key=openai.api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self.openai_client = None

    def load_dataset(self) -> bool:
        """Load the distillation control dataset"""
        try:
            logger.info(f"Loading distillation control dataset from: {self.dataset_path}")

            # Load dataset
            self.df = pd.read_csv(self.dataset_path, dtype='object')

            # Clean numeric columns
            numeric_columns = ['PV01', 'PV02', 'PV03', 'CV01', 'CV01_SP', 'DV01', 'DV02', 'DV03']
            for col in numeric_columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

            # Parse timestamps
            if 'Timestamp' in self.df.columns:
                self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'], format='%m/%d/%y:%H:%M:%S:%f', errors='coerce')

            # Remove incomplete records
            self.df = self.df.dropna()

            logger.info(f"Dataset loaded successfully: {len(self.df):,} records")
            return True

        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            return False

    def extract_control_scenarios(self) -> List[ControlScenario]:
        """Extract interesting control scenarios from the dataset"""
        logger.info("Extracting control scenarios from dataset...")

        scenarios = []

        # 1. Setpoint tracking scenarios
        sp_changes = self.df['CV01_SP'].diff().abs() > 0.1
        change_indices = self.df.index[sp_changes].tolist()

        for i, idx in enumerate(change_indices[:20]):  # First 20 setpoint changes
            start_idx = max(0, idx - 100)
            end_idx = min(len(self.df), idx + 200)

            scenario_data = self.df.iloc[start_idx:end_idx]

            scenario = ControlScenario(
                scenario_type='setpoint_tracking',
                time_range=(scenario_data['Timestamp'].iloc[0].isoformat(),
                          scenario_data['Timestamp'].iloc[-1].isoformat()),
                pv_values=scenario_data['PV01'].tolist(),
                cv_values=scenario_data['CV01'].tolist(),
                sp_values=scenario_data['CV01_SP'].tolist(),
                dv_values={
                    'DV01': scenario_data['DV01'].tolist(),
                    'DV02': scenario_data['DV02'].tolist(),
                    'DV03': scenario_data['DV03'].tolist()
                },
                performance_metrics={
                    'mae': float(np.mean(np.abs(scenario_data['PV01'] - scenario_data['CV01_SP']))),
                    'settling_time': len(scenario_data) * 5 / 60,  # 5 second intervals to minutes
                    'overshoot': float(max(scenario_data['PV01']) - scenario_data['CV01_SP'].iloc[-1])
                },
                description=f"Setpoint tracking scenario {i+1}: temperature setpoint change"
            )
            scenarios.append(scenario)

        # 2. Disturbance rejection scenarios
        for dv_col in ['DV01', 'DV02', 'DV03']:
            dv_changes = self.df[dv_col].diff().abs() > 2 * self.df[dv_col].std()
            disturbance_indices = self.df.index[dv_changes].tolist()

            for i, idx in enumerate(disturbance_indices[:10]):  # First 10 disturbances per variable
                start_idx = max(0, idx - 50)
                end_idx = min(len(self.df), idx + 150)

                scenario_data = self.df.iloc[start_idx:end_idx]

                scenario = ControlScenario(
                    scenario_type='disturbance_rejection',
                    time_range=(scenario_data['Timestamp'].iloc[0].isoformat(),
                              scenario_data['Timestamp'].iloc[-1].isoformat()),
                    pv_values=scenario_data['PV01'].tolist(),
                    cv_values=scenario_data['CV01'].tolist(),
                    sp_values=scenario_data['CV01_SP'].tolist(),
                    dv_values={
                        'DV01': scenario_data['DV01'].tolist(),
                        'DV02': scenario_data['DV02'].tolist(),
                        'DV03': scenario_data['DV03'].tolist()
                    },
                    performance_metrics={
                        'mae': float(np.mean(np.abs(scenario_data['PV01'] - scenario_data['CV01_SP']))),
                        'disturbance_magnitude': float(abs(scenario_data[dv_col].diff().max())),
                        'recovery_time': len(scenario_data) * 5 / 60
                    },
                    description=f"Disturbance rejection scenario: {dv_col} disturbance"
                )
                scenarios.append(scenario)

        # 3. Performance comparison scenarios
        error = self.df['PV01'] - self.df['CV01_SP']
        error_rolling = error.rolling(window=500).apply(lambda x: np.mean(np.abs(x)))

        # Best performance period
        best_idx = error_rolling.idxmin()
        best_start = max(0, best_idx - 250)
        best_end = min(len(self.df), best_idx + 250)
        best_data = self.df.iloc[best_start:best_end]

        best_scenario = ControlScenario(
            scenario_type='excellent_control',
            time_range=(best_data['Timestamp'].iloc[0].isoformat(),
                      best_data['Timestamp'].iloc[-1].isoformat()),
            pv_values=best_data['PV01'].tolist(),
            cv_values=best_data['CV01'].tolist(),
            sp_values=best_data['CV01_SP'].tolist(),
            dv_values={
                'DV01': best_data['DV01'].tolist(),
                'DV02': best_data['DV02'].tolist(),
                'DV03': best_data['DV03'].tolist()
            },
            performance_metrics={
                'mae': float(error_rolling.min()),
                'stability_index': float(best_data['CV01'].std()),
                'efficiency': float(1 - error_rolling.min() / best_data['CV01_SP'].mean())
            },
            description="Excellent control performance period"
        )
        scenarios.append(best_scenario)

        # Worst performance period
        worst_idx = error_rolling.idxmax()
        worst_start = max(0, worst_idx - 250)
        worst_end = min(len(self.df), worst_idx + 250)
        worst_data = self.df.iloc[worst_start:worst_end]

        worst_scenario = ControlScenario(
            scenario_type='poor_control',
            time_range=(worst_data['Timestamp'].iloc[0].isoformat(),
                      worst_data['Timestamp'].iloc[-1].isoformat()),
            pv_values=worst_data['PV01'].tolist(),
            cv_values=worst_data['CV01'].tolist(),
            sp_values=worst_data['CV01_SP'].tolist(),
            dv_values={
                'DV01': worst_data['DV01'].tolist(),
                'DV02': worst_data['DV02'].tolist(),
                'DV03': worst_data['DV03'].tolist()
            },
            performance_metrics={
                'mae': float(error_rolling.max()),
                'stability_index': float(worst_data['CV01'].std()),
                'efficiency': float(1 - error_rolling.max() / worst_data['CV01_SP'].mean())
            },
            description="Poor control performance period requiring improvement"
        )
        scenarios.append(worst_scenario)

        logger.info(f"Extracted {len(scenarios)} control scenarios")
        return scenarios

    async def generate_temperature_control_qa(self, scenarios: List[ControlScenario]) -> List[Dict]:
        """Generate Q&A pairs for temperature control"""
        logger.info("Generating temperature control Q&A pairs...")

        qa_pairs = []

        # Template questions for different complexity levels
        templates = {
            'basic': [
                "What is the primary controlled variable in this distillation column?",
                "What is the typical temperature range for this process?",
                "How many temperature measurement points are used in this system?",
                "What is the purpose of multiple temperature sensors in distillation control?"
            ],
            'intermediate': [
                "Analyze the temperature control performance in this scenario. What is the MAE?",
                "How does the controller respond to setpoint changes in this system?",
                "What factors affect the temperature control loop stability?",
                "Compare the performance of different temperature measurement points."
            ],
            'advanced': [
                "Design a control strategy for this multi-temperature distillation system.",
                "Analyze the interaction between temperature control and disturbance variables.",
                "Propose tuning parameters for optimal temperature control performance.",
                "Evaluate the economic impact of temperature control performance."
            ]
        }

        for scenario in scenarios[:10]:  # Use first 10 scenarios
            for level, questions in templates.items():
                for question in questions:
                    # Create context from scenario data
                    context = f"""
                    Scenario: {scenario.description}
                    Time Range: {scenario.time_range[0]} to {scenario.time_range[1]}
                    Temperature Range: {min(scenario.pv_values):.1f}°F to {max(scenario.pv_values):.1f}°F
                    Controller Output: {min(scenario.cv_values):.1f}% to {max(scenario.cv_values):.1f}%
                    Performance: MAE = {scenario.performance_metrics['mae']:.2f}°F
                    """

                    # Generate answer using OpenAI
                    if self.openai_client:
                        try:
                            response = await self.generate_openai_response(question, context, level)
                            qa_pairs.append({
                                'question': question,
                                'answer': response,
                                'category': 'temperature_control',
                                'complexity': level,
                                'scenario_type': scenario.scenario_type,
                                'context': context.strip()
                            })
                        except Exception as e:
                            logger.error(f"Error generating response: {str(e)}")

        logger.info(f"Generated {len(qa_pairs)} temperature control Q&A pairs")
        return qa_pairs

    async def generate_openai_response(self, question: str, context: str, complexity: str) -> str:
        """Generate response using OpenAI API"""

        system_prompt = f"""
        You are an expert in industrial control theory specializing in distillation column control.
        Generate a comprehensive, technically accurate answer for a {complexity} level question.

        For basic questions: Focus on fundamental concepts and definitions.
        For intermediate questions: Include analysis, calculations, and comparisons.
        For advanced questions: Provide detailed technical analysis, design recommendations, and economic considerations.

        Always include specific numerical values from the provided data when relevant.
        Use proper control theory terminology and cite relevant industry standards when applicable.
        """

        user_prompt = f"""
        Context: {context}

        Question: {question}

        Please provide a comprehensive answer that demonstrates expert knowledge of industrial control theory.
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"Error generating response: {str(e)}"

    async def generate_all_categories(self, scenarios: List[ControlScenario]) -> Dict[str, List[Dict]]:
        """Generate Q&A pairs for all categories"""
        logger.info("Generating Q&A pairs for all categories...")

        all_qa_pairs = {}

        # Generate for each category
        for category, config in self.training_categories.items():
            logger.info(f"Generating {category} Q&A pairs...")

            if category == 'temperature_control':
                qa_pairs = await self.generate_temperature_control_qa(scenarios)
            else:
                # For other categories, use scenario-based generation
                qa_pairs = await self.generate_category_qa(category, scenarios, config['target_count'])

            all_qa_pairs[category] = qa_pairs

        return all_qa_pairs

    async def generate_category_qa(self, category: str, scenarios: List[ControlScenario], target_count: int) -> List[Dict]:
        """Generate Q&A pairs for a specific category"""
        # Implementation for other categories would go here
        # For now, return placeholder
        return []

    def export_training_data(self, qa_pairs: Dict[str, List[Dict]]) -> str:
        """Export training data in OpenAI fine-tuning format"""
        logger.info("Exporting training data...")

        # Create results directory
        results_dir = Path('results/phase10')
        results_dir.mkdir(parents=True, exist_ok=True)

        # Flatten all Q&A pairs
        all_pairs = []
        for _category, pairs in qa_pairs.items():
            all_pairs.extend(pairs)

        # Create training data in OpenAI format
        training_data = []
        for pair in all_pairs:
            training_data.append({
                "messages": [
                    {"role": "user", "content": pair['question']},
                    {"role": "assistant", "content": pair['answer']}
                ],
                "metadata": {
                    "category": pair['category'],
                    "complexity": pair.get('complexity', 'intermediate'),
                    "scenario_type": pair.get('scenario_type', 'general')
                }
            })

        # Export to JSONL
        output_file = results_dir / f"phase10_specialized_training_data_{self.session_id}.jsonl"
        with open(output_file, 'w') as f:
            for item in training_data:
                f.write(json.dumps(item) + '\n')

        # Export summary
        summary_file = results_dir / f"phase10_training_summary_{self.session_id}.json"
        summary = {
            'generation_date': datetime.now().isoformat(),
            'session_id': self.session_id,
            'total_qa_pairs': len(all_pairs),
            'categories': {cat: len(pairs) for cat, pairs in qa_pairs.items()},
            'training_file': str(output_file),
            'dataset_source': str(self.dataset_path)
        }

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Training data exported to: {output_file}")
        logger.info(f"Summary exported to: {summary_file}")

        return str(output_file)

    async def run_training_data_generation(self) -> Dict[str, Any]:
        """Run complete training data generation process"""
        logger.info("🚀 Starting specialized training data generation...")

        # Step 1: Load dataset
        if not self.load_dataset():
            raise Exception("Failed to load dataset")

        # Step 2: Extract control scenarios
        scenarios = self.extract_control_scenarios()

        # Step 3: Generate Q&A pairs for all categories
        qa_pairs = await self.generate_all_categories(scenarios)

        # Step 4: Export training data
        output_file = self.export_training_data(qa_pairs)

        # Generate summary
        total_pairs = sum(len(pairs) for pairs in qa_pairs.values())

        summary = {
            'status': 'completed',
            'session_id': self.session_id,
            'total_scenarios': len(scenarios),
            'total_qa_pairs': total_pairs,
            'categories': {cat: len(pairs) for cat, pairs in qa_pairs.items()},
            'output_file': output_file,
            'phase10_progress': f"{total_pairs:,} Q&A pairs generated"
        }

        logger.info("✅ Specialized training data generation completed!")
        return summary

def main():
    """Main execution function"""
    dataset_path = "/Users/reh3376/repos/plc-gbt/docs/context/dataset_still_steam_till_03_02.csv"

    generator = SpecializedTrainingDataGenerator(dataset_path)

    # Run async generation
    results = asyncio.run(generator.run_training_data_generation())

    print("\n🎉 Training Data Generation Complete!")
    print(f"Session ID: {results['session_id']}")
    print(f"Total Scenarios: {results['total_scenarios']}")
    print(f"Total Q&A Pairs: {results['total_qa_pairs']:,}")
    print(f"Output File: {results['output_file']}")

    print("\n📊 Category Breakdown:")
    for category, count in results['categories'].items():
        print(f"  • {category}: {count} pairs")

if __name__ == "__main__":
    main()
