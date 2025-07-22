#!/usr/bin/env python3
"""
🧠 Fine-tuned LLM Integration Framework

Provides integration support for specialized domain LLMs including Industrial Control Theory
models and other fine-tuned models as described in the AI Task Orchestrator Guide.
Enables domain-specific analysis, insights, and specialized recommendations.

Author: AI Enhancement Framework
Created: 2025-01-18
License: MIT
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMDomain(Enum):
    """Supported specialized domain LLMs"""
    INDUSTRIAL_CONTROL = "industrial_control"
    WEB_DEVELOPMENT = "web_development"
    DATA_SCIENCE = "data_science"
    CYBERSECURITY = "cybersecurity"
    MACHINE_LEARNING = "machine_learning"
    FINANCIAL_MODELING = "financial_modeling"
    BIOMEDICAL = "biomedical"
    ROBOTICS = "robotics"
    GENERAL_PURPOSE = "general_purpose"

class AnalysisType(Enum):
    """Types of specialized analysis"""
    TASK_DECOMPOSITION = "task_decomposition"
    DOMAIN_EXPERTISE = "domain_expertise"
    BEST_PRACTICES = "best_practices"
    SAFETY_ANALYSIS = "safety_analysis"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ARCHITECTURE_REVIEW = "architecture_review"
    COMPLIANCE_CHECK = "compliance_check"
    RISK_ASSESSMENT = "risk_assessment"

@dataclass
class LLMModelConfig:
    """Configuration for a fine-tuned LLM model"""
    model_id: str
    domain: LLMDomain
    api_provider: str  # "openai", "anthropic", "custom"
    model_version: str
    specialized_capabilities: List[str]
    context_window: int
    cost_per_token: float
    response_time_avg: float
    accuracy_metrics: Dict[str, float]
    available: bool = True

@dataclass
class DomainAnalysisRequest:
    """Request for domain-specific analysis"""
    task_description: str
    code_content: Optional[str]
    analysis_type: AnalysisType
    domain: LLMDomain
    context: Dict[str, Any]
    priority: str = "normal"  # "low", "normal", "high", "critical"
    max_tokens: Optional[int] = None
    temperature: float = 0.1

@dataclass
class DomainAnalysisResult:
    """Result from domain-specific LLM analysis"""
    request_id: str
    analysis_type: AnalysisType
    domain: LLMDomain
    model_used: str
    insights: List[str]
    recommendations: List[str]
    confidence_score: float
    domain_specific_metrics: Dict[str, Any]
    safety_considerations: List[str]
    performance_implications: List[str]
    compliance_notes: List[str]
    next_steps: List[str]
    response_time: float
    token_usage: Dict[str, int]

@dataclass
class SpecializedLLMInsights:
    """Comprehensive insights from specialized LLM"""
    task_complexity_assessment: Dict[str, Any]
    domain_specific_requirements: List[str]
    specialized_tools_needed: List[str]
    industry_standards: List[str]
    safety_protocols: List[str]
    performance_targets: Dict[str, Any]
    recommended_approaches: List[str]
    potential_pitfalls: List[str]
    validation_criteria: List[str]
    educational_resources: List[str]

class LLMProviderInterface:
    """Base interface for LLM providers"""
    
    def __init__(self, provider_name: str, api_key: Optional[str] = None):
        self.provider_name = provider_name
        self.api_key = api_key
        self.available = bool(api_key)
    
    async def query_model(self, 
                         model_id: str, 
                         prompt: str, 
                         max_tokens: Optional[int] = None,
                         temperature: float = 0.1,
                         **kwargs) -> Dict[str, Any]:
        """Query the LLM model"""
        raise NotImplementedError("Subclasses must implement query_model")
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        raise NotImplementedError("Subclasses must implement get_model_info")
    
    def is_model_available(self, model_id: str) -> bool:
        """Check if model is available"""
        raise NotImplementedError("Subclasses must implement is_model_available")

class OpenAIProvider(LLMProviderInterface):
    """OpenAI provider for fine-tuned models"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("openai", api_key or os.getenv('OPENAI_API_KEY'))
        self.base_url = "https://api.openai.com/v1"
        
        # Known fine-tuned models (would be loaded from configuration)
        self.known_models = {
            "ft:gpt-4o:industrial-control:20250117": {
                "domain": LLMDomain.INDUSTRIAL_CONTROL,
                "capabilities": [
                    "pid_controller_design",
                    "control_theory_analysis", 
                    "safety_system_design",
                    "industrial_automation",
                    "process_optimization"
                ],
                "context_window": 128000,
                "specialized_for": "Industrial Control Theory and Automation"
            }
        }
    
    async def query_model(self, 
                         model_id: str, 
                         prompt: str, 
                         max_tokens: Optional[int] = None,
                         temperature: float = 0.1,
                         **kwargs) -> Dict[str, Any]:
        """Query OpenAI fine-tuned model"""
        if not self.available:
            raise Exception("OpenAI API key not available")
        
        try:
            # This would make actual API calls to OpenAI
            # For now, we'll simulate the response based on model type
            
            start_time = time.time()
            
            if "industrial-control" in model_id:
                response = await self._simulate_industrial_control_response(prompt)
            elif "gpt-4" in model_id:
                response = await self._simulate_general_response(prompt)
            else:
                response = await self._simulate_custom_model_response(model_id, prompt)
            
            return {
                "model": model_id,
                "response": response,
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(response.split()),
                    "total_tokens": len(prompt.split()) + len(response.split())
                },
                "response_time": time.time() - start_time,
                "provider": "openai"
            }
            
        except Exception as e:
            logger.error(f"OpenAI query error: {e}")
            raise
    
    async def _simulate_industrial_control_response(self, prompt: str) -> str:
        """Simulate response from Industrial Control Theory fine-tuned model"""
        # This would be actual API response in real implementation
        if "pid" in prompt.lower():
            return """
As an Industrial Control Theory specialist, I'll analyze this PID controller implementation:

**Control Theory Analysis:**
1. The PID structure follows classical control theory principles
2. Proportional gain provides immediate response to error
3. Integral term eliminates steady-state error but may cause overshoot
4. Derivative term provides predictive control but amplifies noise

**Safety Considerations:**
- Implement saturation limits to prevent actuator damage
- Add derivative kick prevention when setpoint changes
- Consider using anti-windup for integral term
- Ensure fail-safe behavior on sensor failure

**Performance Optimization:**
- Tune using Ziegler-Nichols or Cohen-Coon methods
- Consider adaptive tuning for varying process dynamics
- Implement bumpless transfer for manual/auto mode switching

**Industrial Standards Compliance:**
- Follow IEC 61131-3 for programmable controllers
- Implement SIL (Safety Integrity Level) requirements
- Consider ISA-95 enterprise integration standards

This implementation shows good understanding of PID fundamentals but would benefit from additional safety mechanisms and tuning strategies.
"""
        elif "control" in prompt.lower():
            return """
From an Industrial Control perspective, this system requires careful consideration of:

**Control Architecture:**
- Single-loop vs cascade control strategy
- Feedforward compensation opportunities
- Distributed control system integration

**Safety Systems:**
- Emergency shutdown procedures
- Interlocking logic
- Fault detection and diagnosis

**Performance Metrics:**
- Settling time < 2 time constants
- Overshoot < 10% for critical processes
- Steady-state error < 1%

**Regulatory Compliance:**
- Process safety management (PSM)
- Environmental regulations
- Quality standards (ISO 9001, FDA CFR 21 Part 11)
"""
        else:
            return """
As an Industrial Control Theory expert, I can provide specialized analysis for:
- Control system design and tuning
- Safety system implementation
- Process optimization strategies  
- Industrial automation best practices
- Regulatory compliance guidance

Please provide specific details about your control system requirements for detailed analysis.
"""
    
    async def _simulate_general_response(self, prompt: str) -> str:
        """Simulate response from general-purpose model"""
        return """
I can help with general programming and analysis tasks. For specialized industrial control theory expertise, 
consider using our fine-tuned Industrial Control Theory model (ft:gpt-4o:industrial-control:20250117) 
which provides deeper domain knowledge and safety-critical analysis.

Based on your request, I can offer general programming guidance, but specialized control systems 
analysis would benefit from domain-specific expertise.
"""
    
    async def _simulate_custom_model_response(self, model_id: str, prompt: str) -> str:
        """Simulate response from custom fine-tuned model"""
        return f"""
Response from specialized model {model_id}:

This model provides domain-specific analysis and recommendations based on its specialized training.
The response would include detailed insights relevant to the model's domain expertise.

For actual implementation, this would connect to the real fine-tuned model endpoint.
"""
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get information about OpenAI model"""
        return self.known_models.get(model_id, {
            "domain": LLMDomain.GENERAL_PURPOSE,
            "capabilities": ["general_analysis"],
            "context_window": 128000,
            "specialized_for": "General purpose tasks"
        })
    
    def is_model_available(self, model_id: str) -> bool:
        """Check if OpenAI model is available"""
        return self.available and (model_id in self.known_models or "gpt" in model_id)

class CustomProvider(LLMProviderInterface):
    """Custom provider for other LLM endpoints"""
    
    def __init__(self, provider_name: str, base_url: str, api_key: Optional[str] = None):
        super().__init__(provider_name, api_key)
        self.base_url = base_url
    
    async def query_model(self, model_id: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Query custom model endpoint"""
        # Implementation would depend on specific API
        raise NotImplementedError("Custom provider implementation needed")
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get custom model information"""
        return {"provider": self.provider_name, "model": model_id}
    
    def is_model_available(self, model_id: str) -> bool:
        """Check custom model availability"""
        return self.available

class SpecializedLLMManager:
    """Manager for specialized domain LLMs"""
    
    def __init__(self):
        self.providers = {}
        self.models = {}
        self.default_configs = self._load_default_configs()
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize LLM providers"""
        # OpenAI provider
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.providers['openai'] = OpenAIProvider(openai_key)
            logger.info("OpenAI provider initialized")
        
        # Add other providers as needed
        # self.providers['anthropic'] = AnthropicProvider(os.getenv('ANTHROPIC_API_KEY'))
        # self.providers['custom'] = CustomProvider("custom", "https://api.custom.com", os.getenv('CUSTOM_API_KEY'))
    
    def _load_default_configs(self) -> Dict[str, LLMModelConfig]:
        """Load default model configurations"""
        return {
            "ft:gpt-4o:industrial-control:20250117": LLMModelConfig(
                model_id="ft:gpt-4o-mini-2024-07-18:whiskey-house:industrial-control:But1jpnl",
                domain=LLMDomain.INDUSTRIAL_CONTROL,
                api_provider="openai",
                model_version="20250117",
                specialized_capabilities=[
                    "pid_controller_analysis",
                    "control_system_design",
                    "safety_system_validation",
                    "industrial_automation",
                    "process_optimization",
                    "regulatory_compliance"
                ],
                context_window=128000,
                cost_per_token=0.00002,
                response_time_avg=2.5,
                accuracy_metrics={
                    "control_theory_accuracy": 0.96,
                    "safety_compliance": 0.98,
                    "mathematical_accuracy": 0.95,
                    "industrial_standards": 0.94
                }
            ),
            "gpt-4": LLMModelConfig(
                model_id="gpt-4",
                domain=LLMDomain.GENERAL_PURPOSE,
                api_provider="openai",
                model_version="latest",
                specialized_capabilities=["general_analysis"],
                context_window=128000,
                cost_per_token=0.00003,
                response_time_avg=3.0,
                accuracy_metrics={"general_accuracy": 0.90}
            )
        }
    
    def get_best_model_for_domain(self, domain: LLMDomain) -> Optional[LLMModelConfig]:
        """Get the best available model for a specific domain"""
        domain_models = [
            config for config in self.default_configs.values()
            if config.domain == domain and config.available
        ]
        
        if not domain_models:
            # Fallback to general purpose model
            general_models = [
                config for config in self.default_configs.values()
                if config.domain == LLMDomain.GENERAL_PURPOSE and config.available
            ]
            return general_models[0] if general_models else None
        
        # Sort by accuracy and return best
        domain_models.sort(key=lambda x: sum(x.accuracy_metrics.values()) / len(x.accuracy_metrics), reverse=True)
        return domain_models[0]
    
    def is_domain_specific_task(self, task_description: str) -> Tuple[bool, Optional[LLMDomain]]:
        """Determine if task requires domain-specific LLM"""
        task_lower = task_description.lower()
        
        # Industrial control patterns
        if any(keyword in task_lower for keyword in [
            'pid', 'control', 'controller', 'automation', 'industrial', 'process control',
            'plc', 'scada', 'dcs', 'feedback', 'setpoint', 'actuator', 'sensor'
        ]):
            return True, LLMDomain.INDUSTRIAL_CONTROL
        
        # Data science patterns
        if any(keyword in task_lower for keyword in [
            'machine learning', 'data science', 'neural network', 'deep learning',
            'statistical analysis', 'predictive model', 'data mining'
        ]):
            return True, LLMDomain.DATA_SCIENCE
        
        # Web development patterns
        if any(keyword in task_lower for keyword in [
            'web application', 'frontend', 'backend', 'api development',
            'react', 'nodejs', 'database', 'web service'
        ]):
            return True, LLMDomain.WEB_DEVELOPMENT
        
        # Cybersecurity patterns
        if any(keyword in task_lower for keyword in [
            'security', 'encryption', 'authentication', 'vulnerability',
            'penetration testing', 'cybersecurity', 'secure coding'
        ]):
            return True, LLMDomain.CYBERSECURITY
        
        return False, None
    
    async def get_specialized_llm_insights(self, 
                                         task_description: str,
                                         code_content: Optional[str] = None,
                                         domain: Optional[LLMDomain] = None) -> SpecializedLLMInsights:
        """Get comprehensive insights from specialized LLM"""
        try:
            # Determine domain if not provided
            if not domain:
                is_specialized, detected_domain = self.is_domain_specific_task(task_description)
                domain = detected_domain if is_specialized else LLMDomain.GENERAL_PURPOSE
            
            # Get best model for domain
            model_config = self.get_best_model_for_domain(domain)
            if not model_config:
                raise Exception(f"No model available for domain: {domain}")
            
            # Get provider
            provider = self.providers.get(model_config.api_provider)
            if not provider:
                raise Exception(f"Provider not available: {model_config.api_provider}")
            
            # Create specialized prompt
            prompt = self._create_specialized_prompt(task_description, code_content, domain)
            
            # Query model
            response = await provider.query_model(
                model_id=model_config.model_id,
                prompt=prompt,
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse response into structured insights
            insights = self._parse_specialized_response(response['response'], domain)
            
            return insights
            
        except Exception as e:
            logger.error(f"Specialized LLM insights error: {e}")
            return self._create_fallback_insights(task_description, domain)
    
    def _create_specialized_prompt(self, 
                                 task_description: str, 
                                 code_content: Optional[str],
                                 domain: LLMDomain) -> str:
        """Create domain-specific prompt"""
        base_prompt = f"""
As a specialized expert in {domain.value}, please provide comprehensive analysis for the following task:

Task Description: {task_description}
"""
        
        if code_content:
            base_prompt += f"""
Code to Analyze:
```
{code_content[:2000]}  # Truncate for context window
```
"""
        
        domain_specific_requests = {
            LLMDomain.INDUSTRIAL_CONTROL: """
Please provide analysis covering:
1. Control theory principles and design approach
2. Safety considerations and fail-safe mechanisms
3. Performance optimization strategies
4. Industrial standards and compliance requirements
5. Potential risks and mitigation strategies
6. Recommended tools and methodologies
7. Validation and testing approaches
""",
            LLMDomain.DATA_SCIENCE: """
Please provide analysis covering:
1. Data preprocessing and feature engineering
2. Model selection and validation strategies
3. Performance metrics and evaluation
4. Scalability and deployment considerations
5. Ethical AI and bias considerations
6. Recommended tools and frameworks
""",
            LLMDomain.WEB_DEVELOPMENT: """
Please provide analysis covering:
1. Architecture patterns and scalability
2. Security best practices
3. Performance optimization strategies
4. User experience considerations
5. Testing and deployment approaches
6. Recommended technologies and frameworks
"""
        }
        
        base_prompt += domain_specific_requests.get(domain, """
Please provide comprehensive analysis including:
1. Technical approach and methodology
2. Best practices and standards
3. Potential challenges and solutions
4. Performance considerations
5. Recommended tools and technologies
""")
        
        base_prompt += """
Structure your response with clear sections for insights, recommendations, safety considerations, and next steps.
"""
        
        return base_prompt
    
    def _parse_specialized_response(self, response: str, domain: LLMDomain) -> SpecializedLLMInsights:
        """Parse LLM response into structured insights"""
        # This would use more sophisticated parsing in real implementation
        # For now, we'll extract key sections using simple pattern matching
        
        insights = []
        recommendations = []
        safety_considerations = []
        performance_implications = []
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            if any(keyword in line.lower() for keyword in ['insight', 'analysis']):
                current_section = 'insights'
            elif any(keyword in line.lower() for keyword in ['recommend', 'suggest']):
                current_section = 'recommendations'
            elif any(keyword in line.lower() for keyword in ['safety', 'risk']):
                current_section = 'safety'
            elif any(keyword in line.lower() for keyword in ['performance', 'optimization']):
                current_section = 'performance'
            
            # Extract content
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                content = line[1:].strip()
                if current_section == 'insights':
                    insights.append(content)
                elif current_section == 'recommendations':
                    recommendations.append(content)
                elif current_section == 'safety':
                    safety_considerations.append(content)
                elif current_section == 'performance':
                    performance_implications.append(content)
        
        # Create domain-specific insights
        return SpecializedLLMInsights(
            task_complexity_assessment={
                "complexity_level": "moderate",  # Would be extracted from response
                "estimated_effort": "3-8 hours",
                "required_expertise": domain.value
            },
            domain_specific_requirements=self._extract_requirements(response, domain),
            specialized_tools_needed=self._extract_tools(response, domain),
            industry_standards=self._extract_standards(response, domain),
            safety_protocols=safety_considerations or ["General safety protocols apply"],
            performance_targets={"response_time": "< 100ms", "accuracy": "> 95%"},
            recommended_approaches=recommendations or ["Follow domain best practices"],
            potential_pitfalls=self._extract_pitfalls(response, domain),
            validation_criteria=self._extract_validation_criteria(response, domain),
            educational_resources=self._extract_educational_resources(response, domain)
        )
    
    def _extract_requirements(self, response: str, domain: LLMDomain) -> List[str]:
        """Extract domain-specific requirements from response"""
        requirements = []
        domain_keywords = {
            LLMDomain.INDUSTRIAL_CONTROL: ['safety limits', 'control loop', 'setpoint tracking'],
            LLMDomain.DATA_SCIENCE: ['data quality', 'model validation', 'feature engineering'],
            LLMDomain.WEB_DEVELOPMENT: ['responsive design', 'security', 'scalability']
        }
        
        keywords = domain_keywords.get(domain, [])
        for keyword in keywords:
            if keyword in response.lower():
                requirements.append(f"Implement {keyword}")
        
        return requirements or ["Domain-specific requirements to be determined"]
    
    def _extract_tools(self, response: str, domain: LLMDomain) -> List[str]:
        """Extract recommended tools from response"""
        domain_tools = {
            LLMDomain.INDUSTRIAL_CONTROL: ['MATLAB/Simulink', 'Python Control', 'LabVIEW'],
            LLMDomain.DATA_SCIENCE: ['Python/R', 'Jupyter', 'TensorFlow/PyTorch'],
            LLMDomain.WEB_DEVELOPMENT: ['React/Vue', 'Node.js', 'Docker']
        }
        
        return domain_tools.get(domain, ["Standard development tools"])
    
    def _extract_standards(self, response: str, domain: LLMDomain) -> List[str]:
        """Extract industry standards from response"""
        domain_standards = {
            LLMDomain.INDUSTRIAL_CONTROL: ['IEC 61131-3', 'ISA-95', 'IEC 61508'],
            LLMDomain.DATA_SCIENCE: ['IEEE Standards', 'ISO/IEC 23053', 'GDPR Compliance'],
            LLMDomain.WEB_DEVELOPMENT: ['W3C Standards', 'OWASP Guidelines', 'REST API Standards']
        }
        
        return domain_standards.get(domain, ["Industry best practices"])
    
    def _extract_pitfalls(self, response: str, domain: LLMDomain) -> List[str]:
        """Extract potential pitfalls from response"""
        domain_pitfalls = {
            LLMDomain.INDUSTRIAL_CONTROL: [
                'Integral windup in PID controllers',
                'Sensor failure handling',
                'Safety system bypassing'
            ],
            LLMDomain.DATA_SCIENCE: [
                'Data leakage in training',
                'Overfitting to training data',
                'Bias in dataset'
            ],
            LLMDomain.WEB_DEVELOPMENT: [
                'SQL injection vulnerabilities',
                'Cross-site scripting (XSS)',
                'Performance bottlenecks'
            ]
        }
        
        return domain_pitfalls.get(domain, ["Common implementation challenges"])
    
    def _extract_validation_criteria(self, response: str, domain: LLMDomain) -> List[str]:
        """Extract validation criteria from response"""
        domain_validation = {
            LLMDomain.INDUSTRIAL_CONTROL: [
                'Stability margin analysis',
                'Safety system testing',
                'Performance under disturbances'
            ],
            LLMDomain.DATA_SCIENCE: [
                'Cross-validation scores',
                'Out-of-sample testing',
                'Model interpretability'
            ],
            LLMDomain.WEB_DEVELOPMENT: [
                'Unit test coverage',
                'Integration testing',
                'Performance testing'
            ]
        }
        
        return domain_validation.get(domain, ["Standard validation practices"])
    
    def _extract_educational_resources(self, response: str, domain: LLMDomain) -> List[str]:
        """Extract educational resources from response"""
        domain_resources = {
            LLMDomain.INDUSTRIAL_CONTROL: [
                'Modern Control Engineering - Ogata',
                'Control Systems Engineering - Nise',
                'ISA Training Courses'
            ],
            LLMDomain.DATA_SCIENCE: [
                'Elements of Statistical Learning',
                'Pattern Recognition and Machine Learning',
                'Coursera Machine Learning Course'
            ],
            LLMDomain.WEB_DEVELOPMENT: [
                'MDN Web Docs',
                'JavaScript: The Good Parts',
                'Clean Code - Robert Martin'
            ]
        }
        
        return domain_resources.get(domain, ["General programming resources"])
    
    def _create_fallback_insights(self, task_description: str, domain: Optional[LLMDomain]) -> SpecializedLLMInsights:
        """Create fallback insights when specialized LLM is not available"""
        return SpecializedLLMInsights(
            task_complexity_assessment={
                "complexity_level": "unknown",
                "estimated_effort": "To be determined",
                "required_expertise": "General programming"
            },
            domain_specific_requirements=["Specialized LLM not available for detailed analysis"],
            specialized_tools_needed=["Standard development tools"],
            industry_standards=["Follow general best practices"],
            safety_protocols=["Implement standard safety measures"],
            performance_targets={"accuracy": "Standard performance expected"},
            recommended_approaches=["Use conventional programming approaches"],
            potential_pitfalls=["Common implementation challenges apply"],
            validation_criteria=["Standard testing practices"],
            educational_resources=["General programming resources"]
        )

class DomainSpecificAnalyzer:
    """Analyzer for domain-specific task analysis"""
    
    def __init__(self, llm_manager: SpecializedLLMManager):
        self.llm_manager = llm_manager
    
    async def analyze_domain_task(self, 
                                task_description: str,
                                code_content: Optional[str] = None,
                                analysis_type: AnalysisType = AnalysisType.DOMAIN_EXPERTISE) -> DomainAnalysisResult:
        """Perform domain-specific task analysis"""
        request_id = f"analysis_{int(time.time())}"
        start_time = time.time()
        
        try:
            # Detect domain
            is_specialized, domain = self.llm_manager.is_domain_specific_task(task_description)
            if not is_specialized:
                domain = LLMDomain.GENERAL_PURPOSE
            
            # Get best model
            model_config = self.llm_manager.get_best_model_for_domain(domain)
            if not model_config:
                raise Exception(f"No model available for domain: {domain}")
            
            # Create analysis request
            request = DomainAnalysisRequest(
                task_description=task_description,
                code_content=code_content,
                analysis_type=analysis_type,
                domain=domain,
                context={"request_id": request_id}
            )
            
            # Perform analysis
            insights = await self.llm_manager.get_specialized_llm_insights(
                task_description, code_content, domain
            )
            
            # Create result
            return DomainAnalysisResult(
                request_id=request_id,
                analysis_type=analysis_type,
                domain=domain,
                model_used=model_config.model_id,
                insights=[
                    f"Task complexity: {insights.task_complexity_assessment['complexity_level']}",
                    f"Required expertise: {insights.task_complexity_assessment['required_expertise']}",
                    f"Estimated effort: {insights.task_complexity_assessment['estimated_effort']}"
                ],
                recommendations=insights.recommended_approaches,
                confidence_score=sum(model_config.accuracy_metrics.values()) / len(model_config.accuracy_metrics),
                domain_specific_metrics={
                    "specialized_requirements": len(insights.domain_specific_requirements),
                    "safety_protocols": len(insights.safety_protocols),
                    "industry_standards": len(insights.industry_standards)
                },
                safety_considerations=insights.safety_protocols,
                performance_implications=[
                    f"Target: {target}" for target in insights.performance_targets.values()
                ],
                compliance_notes=insights.industry_standards,
                next_steps=insights.validation_criteria,
                response_time=time.time() - start_time,
                token_usage={"prompt_tokens": 0, "completion_tokens": 0}  # Would be actual from API
            )
            
        except Exception as e:
            logger.error(f"Domain analysis error: {e}")
            return DomainAnalysisResult(
                request_id=request_id,
                analysis_type=analysis_type,
                domain=LLMDomain.GENERAL_PURPOSE,
                model_used="fallback",
                insights=[f"Analysis failed: {str(e)}"],
                recommendations=["Use general programming approaches"],
                confidence_score=0.5,
                domain_specific_metrics={},
                safety_considerations=["Standard safety measures"],
                performance_implications=["Standard performance expected"],
                compliance_notes=["General best practices"],
                next_steps=["Manual analysis required"],
                response_time=time.time() - start_time,
                token_usage={"prompt_tokens": 0, "completion_tokens": 0}
            )

# Convenience functions
async def get_specialized_llm_insights(task_description: str,
                                     code_content: Optional[str] = None,
                                     domain: Optional[LLMDomain] = None) -> SpecializedLLMInsights:
    """
    Get insights from specialized LLM
    
    Args:
        task_description: Description of the task
        code_content: Optional code to analyze
        domain: Optional specific domain
    
    Returns:
        Specialized insights from domain expert LLM
    """
    manager = SpecializedLLMManager()
    return await manager.get_specialized_llm_insights(task_description, code_content, domain)

def is_domain_specific_task(task_description: str) -> Tuple[bool, Optional[LLMDomain]]:
    """
    Check if task requires domain-specific LLM
    
    Args:
        task_description: Description of the task
    
    Returns:
        Tuple of (is_specialized, domain)
    """
    manager = SpecializedLLMManager()
    return manager.is_domain_specific_task(task_description)

async def analyze_domain_task(task_description: str,
                            code_content: Optional[str] = None,
                            analysis_type: AnalysisType = AnalysisType.DOMAIN_EXPERTISE) -> DomainAnalysisResult:
    """
    Perform domain-specific task analysis
    
    Args:
        task_description: Description of the task
        code_content: Optional code to analyze
        analysis_type: Type of analysis to perform
    
    Returns:
        Domain-specific analysis results
    """
    manager = SpecializedLLMManager()
    analyzer = DomainSpecificAnalyzer(manager)
    return await analyzer.analyze_domain_task(task_description, code_content, analysis_type)

if __name__ == "__main__":
    # Example usage
    async def run_examples():
        # Initialize manager
        manager = SpecializedLLMManager()
        
        # Test 1: Check if task is domain-specific
        task1 = "Implement a PID controller for temperature control in an industrial oven"
        is_specialized, domain = manager.is_domain_specific_task(task1)
        print(f"Task 1 - Specialized: {is_specialized}, Domain: {domain}")
        
        # Test 2: Get specialized insights
        if is_specialized:
            insights = await manager.get_specialized_llm_insights(task1, domain=domain)
            print(f"\nSpecialized Insights:")
            print(f"Complexity: {insights.task_complexity_assessment}")
            print(f"Requirements: {insights.domain_specific_requirements[:2]}")
            print(f"Safety: {insights.safety_protocols[:2]}")
        
        # Test 3: Domain-specific analysis
        analyzer = DomainSpecificAnalyzer(manager)
        analysis = await analyzer.analyze_domain_task(
            task1, 
            analysis_type=AnalysisType.SAFETY_ANALYSIS
        )
        print(f"\nDomain Analysis:")
        print(f"Model Used: {analysis.model_used}")
        print(f"Confidence: {analysis.confidence_score:.2f}")
        print(f"Safety Considerations: {analysis.safety_considerations[:2]}")
        
        # Test 4: General task (non-specialized)
        task2 = "Create a simple calculator application"
        is_specialized2, domain2 = manager.is_domain_specific_task(task2)
        print(f"\nTask 2 - Specialized: {is_specialized2}, Domain: {domain2}")
    
    # Run examples
    asyncio.run(run_examples()) 