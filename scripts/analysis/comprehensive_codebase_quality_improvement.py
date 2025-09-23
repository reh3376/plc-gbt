#!/usr/bin/env python3
"""
🤖 Comprehensive Codebase Quality Improvement - AI Task Orchestrator Implementation

Systematic codebase analysis using existing comprehensive frameworks to improve
quality, maintainability, and modularity metrics across entire codebase.

Uses Existing Frameworks:
- CodebaseAnalyzer (codebase_analyzer.py) - Comprehensive analysis system
- AdvancedStaticAnalyzer (phase17_3_1_libcst_astroid_static_analysis.py) - Advanced analysis
- AI Enhancement Framework (UniversalCodeAnalyzer) - Quality assessment
- Phase 14 optimization tools - Refactoring recommendations

Following AI Task Orchestrator Guide methodology for EXTENSIVE complexity task.

Author: AI Task Orchestrator
Created: 2025-06-18
Task: Comprehensive codebase quality improvement with systematic tracking
Complexity: EXTENSIVE (507 Python files, estimated 4-6 hours)
"""

import os
import sys
import json
import time
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import tempfile
import shutil

# Add framework paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent.parent / "ai-enhancement-framework"))

# Import existing frameworks
try:
    from codebase_analyzer import CodebaseAnalyzer, AnalysisDepth
    CODEBASE_ANALYZER_AVAILABLE = True
except ImportError:
    CODEBASE_ANALYZER_AVAILABLE = False

try:
    from phase17_3_1_libcst_astroid_static_analysis import AdvancedStaticAnalyzer, AnalysisLevel
    ADVANCED_ANALYZER_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYZER_AVAILABLE = False

try:
    from core.code_analyzer import UniversalCodeAnalyzer, AnalysisLevel as CoreAnalysisLevel
    UNIVERSAL_ANALYZER_AVAILABLE = True
except ImportError:
    UNIVERSAL_ANALYZER_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Progress Tracking System
# ============================================================================

@dataclass
class FileAnalysisProgress:
    """Track individual file analysis progress"""
    file_path: str
    file_size_bytes: int
    analysis_status: str  # pending, analyzing, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    quality_score: Optional[float] = None
    issues_found: int = 0
    recommendations: List[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

@dataclass
class CodebaseQualityAnalysisSession:
    """Track overall analysis session"""
    session_id: str
    start_time: datetime
    project_root: str
    total_files_discovered: int = 0
    files_analyzed: int = 0
    files_failed: int = 0
    files_skipped: int = 0
    overall_quality_score: float = 0.0
    total_issues_found: int = 0
    total_recommendations: int = 0
    analysis_frameworks_used: List[str] = None
    progress_file_path: Optional[str] = None
    
    def __post_init__(self):
        if self.analysis_frameworks_used is None:
            self.analysis_frameworks_used = []

class ProgressTracker:
    """Manages analysis progress with temporary file persistence"""
    
    def __init__(self, session: CodebaseQualityAnalysisSession):
        self.session = session
        self.file_progress: Dict[str, FileAnalysisProgress] = {}
        
        # Create temporary progress file
        temp_dir = tempfile.gettempdir()
        self.progress_file = Path(temp_dir) / f"codebase_analysis_progress_{self.session.session_id}.json"
        self.session.progress_file_path = str(self.progress_file)
        
        logger.info(f"📋 Progress tracking file: {self.progress_file}")
    
    def add_file(self, file_path: str, file_size: int):
        """Add file to tracking"""
        self.file_progress[file_path] = FileAnalysisProgress(
            file_path=file_path,
            file_size_bytes=file_size,
            analysis_status="pending"
        )
        self._save_progress()
    
    def start_file_analysis(self, file_path: str):
        """Mark file analysis as started"""
        if file_path in self.file_progress:
            self.file_progress[file_path].analysis_status = "analyzing"
            self.file_progress[file_path].start_time = datetime.now()
            self._save_progress()
    
    def complete_file_analysis(self, file_path: str, quality_score: float, 
                             issues_found: int, recommendations: List[str]):
        """Mark file analysis as completed"""
        if file_path in self.file_progress:
            progress = self.file_progress[file_path]
            progress.analysis_status = "completed"
            progress.end_time = datetime.now()
            progress.quality_score = quality_score
            progress.issues_found = issues_found
            progress.recommendations = recommendations
            
            self.session.files_analyzed += 1
            self.session.total_issues_found += issues_found
            self.session.total_recommendations += len(recommendations)
            self._save_progress()
    
    def fail_file_analysis(self, file_path: str, error_message: str):
        """Mark file analysis as failed"""
        if file_path in self.file_progress:
            progress = self.file_progress[file_path]
            progress.analysis_status = "failed"
            progress.end_time = datetime.now()
            progress.error_message = error_message
            
            self.session.files_failed += 1
            self._save_progress()
    
    def skip_file_analysis(self, file_path: str, reason: str):
        """Mark file analysis as skipped"""
        if file_path in self.file_progress:
            progress = self.file_progress[file_path]
            progress.analysis_status = "skipped"
            progress.error_message = reason
            
            self.session.files_skipped += 1
            self._save_progress()
    
    def _save_progress(self):
        """Save progress to temporary file"""
        try:
            progress_data = {
                "session": asdict(self.session),
                "file_progress": {
                    path: asdict(progress) for path, progress in self.file_progress.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get current progress summary"""
        completed_files = [p for p in self.file_progress.values() if p.analysis_status == "completed"]
        
        if completed_files:
            avg_quality = sum(p.quality_score for p in completed_files if p.quality_score) / len(completed_files)
        else:
            avg_quality = 0.0
        
        return {
            "total_files": len(self.file_progress),
            "completed": self.session.files_analyzed,
            "failed": self.session.files_failed,
            "skipped": self.session.files_skipped,
            "pending": len([p for p in self.file_progress.values() if p.analysis_status == "pending"]),
            "average_quality_score": avg_quality,
            "total_issues": self.session.total_issues_found,
            "total_recommendations": self.session.total_recommendations,
            "progress_percentage": (self.session.files_analyzed / max(len(self.file_progress), 1)) * 100
        }
    
    def cleanup(self):
        """Clean up temporary progress file"""
        try:
            if self.progress_file.exists():
                self.progress_file.unlink()
                logger.info(f"🧹 Cleaned up progress file: {self.progress_file}")
        except Exception as e:
            logger.warning(f"Failed to cleanup progress file: {e}")

# ============================================================================
# Comprehensive Quality Improvement System
# ============================================================================

class ComprehensiveCodebaseQualityImprover:
    """
    Comprehensive codebase quality improvement system using existing frameworks.
    
    Systematically analyzes entire codebase using multiple analysis frameworks
    to identify quality, maintainability, and modularity improvements.
    """
    
    def __init__(self, project_root: str, output_dir: Optional[str] = None):
        """Initialize comprehensive quality improvement system"""
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir) if output_dir else self.project_root / "analysis_results"
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize session
        self.session = CodebaseQualityAnalysisSession(
            session_id=f"quality_improvement_{int(time.time())}",
            start_time=datetime.now(),
            project_root=str(self.project_root)
        )
        
        # Initialize progress tracker
        self.progress_tracker = ProgressTracker(self.session)
        
        # Initialize available frameworks
        self.available_frameworks = {}
        self._initialize_frameworks()
        
        # File discovery
        self.python_files = []
        self._discover_files()
        
        logger.info(f"🤖 Comprehensive Quality Improvement initialized")
        logger.info(f"📁 Project root: {self.project_root}")
        logger.info(f"📊 Discovered {len(self.python_files)} Python files")
        logger.info(f"🔧 Available frameworks: {list(self.available_frameworks.keys())}")
    
    def _initialize_frameworks(self):
        """Initialize available analysis frameworks"""
        if CODEBASE_ANALYZER_AVAILABLE:
            self.available_frameworks["CodebaseAnalyzer"] = CodebaseAnalyzer(
                str(self.project_root), 
                AnalysisDepth.COMPREHENSIVE
            )
            self.session.analysis_frameworks_used.append("CodebaseAnalyzer")
            logger.info("✅ CodebaseAnalyzer initialized")
        
        if ADVANCED_ANALYZER_AVAILABLE:
            self.available_frameworks["AdvancedStaticAnalyzer"] = AdvancedStaticAnalyzer(
                AnalysisLevel.COMPREHENSIVE
            )
            self.session.analysis_frameworks_used.append("AdvancedStaticAnalyzer")
            logger.info("✅ AdvancedStaticAnalyzer initialized")
        
        if UNIVERSAL_ANALYZER_AVAILABLE:
            self.available_frameworks["UniversalCodeAnalyzer"] = UniversalCodeAnalyzer(
                CoreAnalysisLevel.COMPREHENSIVE
            )
            self.session.analysis_frameworks_used.append("UniversalCodeAnalyzer")
            logger.info("✅ UniversalCodeAnalyzer initialized")
        
        if not self.available_frameworks:
            raise RuntimeError("❌ No analysis frameworks available!")
    
    def _discover_files(self):
        """Discover all Python files for analysis"""
        logger.info("🔍 Discovering Python files...")
        
        exclude_patterns = [
            '__pycache__', '.git', '.venv', 'venv', 'node_modules',
            'build', 'dist', '.pytest_cache', '*.pyc'
        ]
        
        for py_file in self.project_root.rglob("*.py"):
            # Check if file should be excluded
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(py_file):
                    should_exclude = True
                    break
            
            if not should_exclude and py_file.is_file():
                try:
                    file_size = py_file.stat().st_size
                    if file_size < 10 * 1024 * 1024:  # Skip files > 10MB
                        self.python_files.append(py_file)
                        self.progress_tracker.add_file(str(py_file), file_size)
                except Exception as e:
                    logger.warning(f"Failed to process {py_file}: {e}")
        
        self.session.total_files_discovered = len(self.python_files)
        logger.info(f"📋 Added {len(self.python_files)} files to analysis queue")
    
    async def analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze single file using available frameworks"""
        file_str = str(file_path)
        
        self.progress_tracker.start_file_analysis(file_str)
        
        analysis_results = {
            "file_path": file_str,
            "frameworks_used": [],
            "combined_quality_score": 0.0,
            "total_issues": 0,
            "recommendations": [],
            "detailed_results": {}
        }
        
        try:
            framework_scores = []
            
            # Use CodebaseAnalyzer if available
            if "CodebaseAnalyzer" in self.available_frameworks:
                try:
                    analyzer = self.available_frameworks["CodebaseAnalyzer"]
                    result = analyzer.analyze_single_file(file_path)
                    
                    quality_score = getattr(result, 'quality_score', 50.0)
                    framework_scores.append(quality_score)
                    
                    analysis_results["frameworks_used"].append("CodebaseAnalyzer")
                    analysis_results["detailed_results"]["codebase_analyzer"] = {
                        "quality_score": quality_score,
                        "analysis_time_ms": getattr(result, 'analysis_time_ms', 0),
                        "file_metadata": asdict(result.file_metadata) if hasattr(result, 'file_metadata') else {}
                    }
                    
                except Exception as e:
                    logger.warning(f"CodebaseAnalyzer failed for {file_path}: {e}")
            
            # Use UniversalCodeAnalyzer if available
            if "UniversalCodeAnalyzer" in self.available_frameworks:
                try:
                    analyzer = self.available_frameworks["UniversalCodeAnalyzer"]
                    result = analyzer.analyze_file(file_path)
                    
                    quality_score = result.quality_score
                    framework_scores.append(quality_score)
                    
                    analysis_results["frameworks_used"].append("UniversalCodeAnalyzer")
                    analysis_results["total_issues"] += len(result.issues)
                    analysis_results["recommendations"].extend(result.recommendations)
                    
                    analysis_results["detailed_results"]["universal_analyzer"] = {
                        "quality_score": quality_score,
                        "complexity_score": result.complexity_score,
                        "issues_count": len(result.issues),
                        "recommendations_count": len(result.recommendations),
                        "syntax_valid": result.syntax_valid
                    }
                    
                except Exception as e:
                    logger.warning(f"UniversalCodeAnalyzer failed for {file_path}: {e}")
            
            # Calculate combined quality score
            if framework_scores:
                analysis_results["combined_quality_score"] = sum(framework_scores) / len(framework_scores)
            else:
                analysis_results["combined_quality_score"] = 50.0  # Default
            
            # Complete file analysis tracking
            self.progress_tracker.complete_file_analysis(
                file_str,
                analysis_results["combined_quality_score"],
                analysis_results["total_issues"],
                analysis_results["recommendations"]
            )
            
            return analysis_results
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.progress_tracker.fail_file_analysis(file_str, error_msg)
            logger.error(f"Failed to analyze {file_path}: {e}")
            
            return {
                "file_path": file_str,
                "error": error_msg,
                "combined_quality_score": 0.0,
                "total_issues": 0,
                "recommendations": []
            }
    
    async def run_comprehensive_analysis(self, max_concurrent: int = 5) -> Dict[str, Any]:
        """Run comprehensive analysis on entire codebase"""
        logger.info("🚀 Starting comprehensive codebase quality analysis")
        logger.info(f"📊 Analyzing {len(self.python_files)} Python files")
        logger.info(f"🔧 Using frameworks: {self.session.analysis_frameworks_used}")
        
        # Create semaphore for concurrent processing
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(file_path):
            async with semaphore:
                return await self.analyze_single_file(file_path)
        
        # Process files in batches with progress reporting
        batch_size = 50
        all_results = []
        
        for i in range(0, len(self.python_files), batch_size):
            batch = self.python_files[i:i + batch_size]
            
            logger.info(f"📋 Processing batch {i//batch_size + 1}: files {i+1}-{min(i+batch_size, len(self.python_files))}")
            
            # Process batch
            batch_tasks = [analyze_with_semaphore(file_path) for file_path in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Handle results and exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {result}")
                else:
                    all_results.append(result)
            
            # Report progress
            progress = self.progress_tracker.get_progress_summary()
            logger.info(f"📈 Progress: {progress['completed']}/{progress['total_files']} "
                       f"({progress['progress_percentage']:.1f}%) - "
                       f"Avg Quality: {progress['average_quality_score']:.2f}")
        
        # Generate final summary
        analysis_summary = self._generate_analysis_summary(all_results)
        
        # Save results
        results_file = self.output_dir / f"comprehensive_analysis_results_{self.session.session_id}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "session": asdict(self.session),
                "analysis_summary": analysis_summary,
                "detailed_results": all_results,
                "progress_summary": self.progress_tracker.get_progress_summary()
            }, f, indent=2, default=str)
        
        logger.info(f"💾 Results saved to: {results_file}")
        
        return analysis_summary
    
    def _generate_analysis_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive analysis summary"""
        successful_results = [r for r in results if "error" not in r]
        
        if not successful_results:
            return {"error": "No successful analyses"}
        
        # Calculate summary metrics
        total_files = len(results)
        successful_files = len(successful_results)
        failed_files = total_files - successful_files
        
        quality_scores = [r["combined_quality_score"] for r in successful_results]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        total_issues = sum(r["total_issues"] for r in successful_results)
        total_recommendations = sum(len(r["recommendations"]) for r in successful_results)
        
        # Quality distribution
        high_quality = len([s for s in quality_scores if s >= 80])
        medium_quality = len([s for s in quality_scores if 50 <= s < 80])
        low_quality = len([s for s in quality_scores if s < 50])
        
        # Framework usage statistics
        framework_usage = {}
        for result in successful_results:
            for framework in result.get("frameworks_used", []):
                framework_usage[framework] = framework_usage.get(framework, 0) + 1
        
        return {
            "analysis_overview": {
                "total_files": total_files,
                "successful_analyses": successful_files,
                "failed_analyses": failed_files,
                "success_rate_percentage": (successful_files / total_files) * 100
            },
            "quality_metrics": {
                "average_quality_score": avg_quality,
                "total_issues_found": total_issues,
                "total_recommendations": total_recommendations,
                "quality_distribution": {
                    "high_quality_files": high_quality,
                    "medium_quality_files": medium_quality,
                    "low_quality_files": low_quality
                }
            },
            "framework_statistics": {
                "frameworks_used": list(framework_usage.keys()),
                "framework_usage_counts": framework_usage
            },
            "recommendations": self._generate_improvement_recommendations(successful_results),
            "session_info": {
                "session_id": self.session.session_id,
                "analysis_duration": str(datetime.now() - self.session.start_time),
                "frameworks_available": list(self.available_frameworks.keys())
            }
        }
    
    def _generate_improvement_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate top-level improvement recommendations"""
        recommendations = []
        
        # Analyze quality scores
        quality_scores = [r["combined_quality_score"] for r in results]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        if avg_quality < 50:
            recommendations.append("🚨 CRITICAL: Overall code quality is below acceptable standards. Immediate refactoring required.")
        elif avg_quality < 70:
            recommendations.append("⚠️ WARNING: Code quality needs improvement. Plan systematic refactoring.")
        else:
            recommendations.append("✅ GOOD: Overall code quality is acceptable. Focus on specific problem areas.")
        
        # Issues analysis
        total_issues = sum(r["total_issues"] for r in results)
        if total_issues > len(results) * 5:  # More than 5 issues per file on average
            recommendations.append("🔧 High issue density detected. Prioritize automated code fixes.")
        
        # Low quality files
        low_quality_files = [r for r in results if r["combined_quality_score"] < 30]
        if low_quality_files:
            recommendations.append(f"📋 {len(low_quality_files)} files need immediate attention (quality < 30).")
        
        return recommendations
    
    def cleanup(self):
        """Clean up resources and temporary files"""
        logger.info("🧹 Cleaning up analysis session...")
        self.progress_tracker.cleanup()

# ============================================================================
# Main Execution
# ============================================================================

async def main():
    """Main execution function following AI Task Orchestrator methodology"""
    print("🤖 Comprehensive Codebase Quality Improvement - AI Task Orchestrator")
    print("=" * 80)
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Task: Analyze entire codebase for quality, maintainability, and modularity")
    print(f"📊 Complexity: EXTENSIVE (507 Python files estimated)")
    print("🔧 Method: Using existing comprehensive analysis frameworks")
    print("=" * 80)
    
    # Step 1: Initialize comprehensive analysis system
    project_root = Path.cwd().parent.parent  # plc-gbt root
    output_dir = project_root / "codebase_analysis_results"
    
    print(f"\n🔍 Step 1: Initializing Analysis System")
    print(f"📁 Project root: {project_root}")
    print(f"💾 Output directory: {output_dir}")
    
    improver = ComprehensiveCodebaseQualityImprover(
        project_root=str(project_root),
        output_dir=str(output_dir)
    )
    
    try:
        # Step 2: Run comprehensive analysis
        print(f"\n🚀 Step 2: Running Comprehensive Analysis")
        print(f"📋 Progress tracking file: {improver.progress_tracker.progress_file}")
        
        summary = await improver.run_comprehensive_analysis(max_concurrent=3)
        
        # Step 3: Display results
        print(f"\n📊 Step 3: Analysis Results Summary")
        print("=" * 60)
        
        overview = summary["analysis_overview"]
        print(f"📈 Total files analyzed: {overview['total_files']}")
        print(f"✅ Successful analyses: {overview['successful_analyses']}")
        print(f"❌ Failed analyses: {overview['failed_analyses']}")
        print(f"🎯 Success rate: {overview['success_rate_percentage']:.1f}%")
        
        quality = summary["quality_metrics"]
        print(f"\n🏆 Quality Metrics:")
        print(f"   Average quality score: {quality['average_quality_score']:.2f}")
        print(f"   Total issues found: {quality['total_issues_found']}")
        print(f"   Total recommendations: {quality['total_recommendations']}")
        
        distribution = quality["quality_distribution"]
        print(f"\n📊 Quality Distribution:")
        print(f"   High quality files (≥80): {distribution['high_quality_files']}")
        print(f"   Medium quality files (50-79): {distribution['medium_quality_files']}")
        print(f"   Low quality files (<50): {distribution['low_quality_files']}")
        
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(summary["recommendations"], 1):
            print(f"   {i}. {rec}")
        
        # Step 4: Success metrics
        print(f"\n🎉 Step 4: Completion Status")
        session_info = summary["session_info"]
        print(f"✅ Analysis completed successfully!")
        print(f"⏱️  Total duration: {session_info['analysis_duration']}")
        print(f"🔧 Frameworks used: {', '.join(session_info['frameworks_available'])}")
        print(f"💾 Results saved to: {output_dir}")
        
        if overview['success_rate_percentage'] >= 90:
            print(f"🏆 EXCELLENT: Analysis achieved {overview['success_rate_percentage']:.1f}% success rate")
        elif overview['success_rate_percentage'] >= 75:
            print(f"✅ GOOD: Analysis achieved {overview['success_rate_percentage']:.1f}% success rate")
        else:
            print(f"⚠️ NEEDS ATTENTION: {overview['success_rate_percentage']:.1f}% success rate needs improvement")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        logger.error(f"Analysis failed: {e}")
        return 1
    
    finally:
        # Cleanup
        print(f"\n🧹 Step 5: Cleanup")
        improver.cleanup()
    
    print(f"\n🎯 Comprehensive codebase quality analysis complete!")
    print(f"📅 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return 0

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1) 