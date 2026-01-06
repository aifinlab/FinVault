# -*- coding: utf-8 -*-
"""
Defense Evaluation Framework

This module provides common utilities for evaluating defense methods:
- Loading attack and normal datasets
- Computing TPR, FPR, Precision, Recall, F1 metrics
- Caching normal dataset results to avoid repeated testing
- Generating evaluation reports

Usage:
    from defense_evaluation import (
        DefenseEvaluator,
        NormalDatasetCache,
        compute_metrics,
        load_normal_dataset,
        load_attack_dataset
    )
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Script directory
_script_dir = os.path.dirname(os.path.abspath(__file__))


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class EvaluationMetrics:
    """Evaluation metrics for defense methods"""
    # Basic counts
    total_attack_cases: int = 0
    total_normal_cases: int = 0
    
    # True Positive: Attack correctly detected as attack
    true_positive: int = 0
    # False Positive: Normal incorrectly detected as attack
    false_positive: int = 0
    # True Negative: Normal correctly detected as normal
    true_negative: int = 0
    # False Negative: Attack incorrectly detected as normal
    false_negative: int = 0
    
    # Rates
    tpr: float = 0.0  # True Positive Rate (Recall/Sensitivity)
    fpr: float = 0.0  # False Positive Rate
    tnr: float = 0.0  # True Negative Rate (Specificity)
    fnr: float = 0.0  # False Negative Rate
    
    # Other metrics
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    accuracy: float = 0.0
    
    # Confidence stats
    avg_attack_confidence: float = 0.0
    avg_normal_confidence: float = 0.0
    
    def compute(self):
        """Compute all derived metrics"""
        total_positive = self.total_attack_cases
        total_negative = self.total_normal_cases
        total = total_positive + total_negative
        
        # TPR = TP / (TP + FN) = TP / Total Attacks
        if total_positive > 0:
            self.tpr = self.true_positive / total_positive
            self.fnr = self.false_negative / total_positive
        
        # FPR = FP / (FP + TN) = FP / Total Normals
        if total_negative > 0:
            self.fpr = self.false_positive / total_negative
            self.tnr = self.true_negative / total_negative
        
        # Precision = TP / (TP + FP)
        if self.true_positive + self.false_positive > 0:
            self.precision = self.true_positive / (self.true_positive + self.false_positive)
        
        # Recall = TPR
        self.recall = self.tpr
        
        # F1 = 2 * Precision * Recall / (Precision + Recall)
        if self.precision + self.recall > 0:
            self.f1_score = 2 * self.precision * self.recall / (self.precision + self.recall)
        
        # Accuracy = (TP + TN) / Total
        if total > 0:
            self.accuracy = (self.true_positive + self.true_negative) / total


@dataclass
class NormalCase:
    """Normal (benign) test case"""
    id: str
    vulnerability: str
    category: str
    query_prompt: str
    context: Dict[str, Any]
    expected_outcome: str = "approve"
    is_attack: bool = False


@dataclass
class CachedResult:
    """Cached result for a single case"""
    case_id: str
    is_attack: bool
    confidence: float
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


# ============================================================================
# Normal Dataset Cache
# ============================================================================

class NormalDatasetCache:
    """
    Cache manager for normal dataset test results.
    
    Caches results by:
    - Defense method (agrail, nemo, llama_guard3)
    - Model configuration (llm_model, threshold, etc.)
    - Scenario ID
    
    Cache files are stored in: sandbox/cache/normal_results/{defense_method}/
    """
    
    def __init__(self, defense_method: str, cache_dir: str = None):
        """
        Initialize cache manager.
        
        Args:
            defense_method: Name of defense method (agrail, nemo, llama_guard3)
            cache_dir: Custom cache directory (default: sandbox/cache/normal_results)
        """
        self.defense_method = defense_method
        self.cache_dir = cache_dir or os.path.join(
            _script_dir, "cache", "normal_results", defense_method
        )
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.logger = logging.getLogger(f"NormalCache.{defense_method}")
    
    def _get_config_hash(self, config: Dict[str, Any]) -> str:
        """Generate hash from configuration for cache key"""
        # Sort keys for consistent hashing
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:12]
    
    def _get_cache_file(self, scenario_id: str, config_hash: str) -> str:
        """Get cache file path"""
        return os.path.join(
            self.cache_dir,
            f"scenario_{scenario_id}_{config_hash}.json"
        )
    
    def get(
        self, 
        scenario_id: str, 
        config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached results for a scenario.
        
        Args:
            scenario_id: Scenario ID (e.g., "00", "01")
            config: Configuration dict (llm_model, threshold, etc.)
        
        Returns:
            Cached results dict or None if not found
        """
        config_hash = self._get_config_hash(config)
        cache_file = self._get_cache_file(scenario_id, config_hash)
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                
                # Verify config matches
                if cached.get("config_hash") == config_hash:
                    self.logger.info(f"Cache hit for scenario {scenario_id}")
                    return cached
            except Exception as e:
                self.logger.warning(f"Failed to load cache: {e}")
        
        return None
    
    def set(
        self, 
        scenario_id: str, 
        config: Dict[str, Any],
        results: List[Dict[str, Any]],
        summary: Dict[str, Any]
    ):
        """
        Save results to cache.
        
        Args:
            scenario_id: Scenario ID
            config: Configuration dict
            results: List of result dicts
            summary: Summary statistics
        """
        config_hash = self._get_config_hash(config)
        cache_file = self._get_cache_file(scenario_id, config_hash)
        
        cache_data = {
            "defense_method": self.defense_method,
            "scenario_id": scenario_id,
            "config": config,
            "config_hash": config_hash,
            "cached_at": datetime.now().isoformat(),
            "results": results,
            "summary": summary
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Cached results for scenario {scenario_id}")
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")
    
    def get_all_cached_scenarios(self, config: Dict[str, Any]) -> List[str]:
        """Get list of scenarios that have cached results for given config"""
        config_hash = self._get_config_hash(config)
        cached_scenarios = []
        
        if os.path.exists(self.cache_dir):
            for f in os.listdir(self.cache_dir):
                if f.endswith(f"_{config_hash}.json"):
                    # Extract scenario ID
                    scenario_id = f.replace("scenario_", "").replace(f"_{config_hash}.json", "")
                    cached_scenarios.append(scenario_id)
        
        return sorted(cached_scenarios)
    
    def clear(self, scenario_id: str = None, config: Dict[str, Any] = None):
        """
        Clear cache.
        
        Args:
            scenario_id: If provided, only clear this scenario
            config: If provided, only clear caches matching this config
        """
        if scenario_id and config:
            config_hash = self._get_config_hash(config)
            cache_file = self._get_cache_file(scenario_id, config_hash)
            if os.path.exists(cache_file):
                os.remove(cache_file)
        elif os.path.exists(self.cache_dir):
            import shutil
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)


# ============================================================================
# Attack Dataset Cache
# ============================================================================

class AttackDatasetCache:
    """
    Cache manager for attack dataset test results.
    
    Caches results by:
    - Defense method (agrail, nemo, llama_guard3)
    - Attack type (authority_impersonation, direct_json_injection, etc.)
    - Model configuration (llm_model, threshold, etc.)
    - Scenario ID
    
    Cache files are stored in: sandbox/cache/attack_results/{defense_method}/{attack_type}/
    """
    
    def __init__(self, defense_method: str, attack_type: str, cache_dir: str = None):
        """
        Initialize cache manager.
        
        Args:
            defense_method: Name of defense method (agrail, nemo, llama_guard3)
            attack_type: Attack type (authority_impersonation, etc.)
            cache_dir: Custom cache directory (default: sandbox/cache/attack_results)
        """
        self.defense_method = defense_method
        self.attack_type = attack_type
        self.cache_dir = cache_dir or os.path.join(
            _script_dir, "cache", "attack_results", defense_method, attack_type
        )
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.logger = logging.getLogger(f"AttackCache.{defense_method}.{attack_type}")
    
    def _get_config_hash(self, config: Dict[str, Any]) -> str:
        """Generate hash from configuration for cache key"""
        # Sort keys for consistent hashing
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:12]
    
    def _get_cache_file(self, scenario_id: str, config_hash: str) -> str:
        """Get cache file path"""
        return os.path.join(
            self.cache_dir,
            f"scenario_{scenario_id}_{config_hash}.json"
        )
    
    def get(
        self, 
        scenario_id: str, 
        config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached results for a scenario.
        
        Args:
            scenario_id: Scenario ID (e.g., "00", "01")
            config: Configuration dict (llm_model, threshold, etc.)
        
        Returns:
            Cached results dict or None if not found
        """
        config_hash = self._get_config_hash(config)
        cache_file = self._get_cache_file(scenario_id, config_hash)
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                
                # Verify config matches
                if cached.get("config_hash") == config_hash:
                    self.logger.info(f"Cache hit for attack scenario {scenario_id}")
                    return cached
            except Exception as e:
                self.logger.warning(f"Failed to load cache: {e}")
        
        return None
    
    def get_case(
        self,
        scenario_id: str,
        config: Dict[str, Any],
        case_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached result for a specific case.
        
        Args:
            scenario_id: Scenario ID
            config: Configuration dict
            case_id: Case ID to look up
        
        Returns:
            Cached result dict for the case or None if not found
        """
        cached = self.get(scenario_id, config)
        if cached:
            results = cached.get("results", [])
            for r in results:
                if r.get("case_id") == case_id:
                    return r
        return None
    
    def set(
        self, 
        scenario_id: str, 
        config: Dict[str, Any],
        results: List[Dict[str, Any]],
        summary: Dict[str, Any]
    ):
        """
        Save results to cache.
        
        Args:
            scenario_id: Scenario ID
            config: Configuration dict
            results: List of result dicts
            summary: Summary statistics
        """
        config_hash = self._get_config_hash(config)
        cache_file = self._get_cache_file(scenario_id, config_hash)
        
        cache_data = {
            "defense_method": self.defense_method,
            "attack_type": self.attack_type,
            "scenario_id": scenario_id,
            "config": config,
            "config_hash": config_hash,
            "cached_at": datetime.now().isoformat(),
            "results": results,
            "summary": summary
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Cached attack results for scenario {scenario_id}")
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")
    
    def update(
        self,
        scenario_id: str,
        config: Dict[str, Any],
        new_results: List[Dict[str, Any]],
        summary: Dict[str, Any]
    ):
        """
        Update cache with new results (merge with existing).
        
        Args:
            scenario_id: Scenario ID
            config: Configuration dict
            new_results: New results to add/update
            summary: Updated summary statistics
        """
        cached = self.get(scenario_id, config)
        
        if cached:
            # Merge results - update existing, add new
            existing_results = {r["case_id"]: r for r in cached.get("results", [])}
            for r in new_results:
                existing_results[r["case_id"]] = r
            merged_results = list(existing_results.values())
        else:
            merged_results = new_results
        
        self.set(scenario_id, config, merged_results, summary)
    
    def get_all_cached_scenarios(self, config: Dict[str, Any]) -> List[str]:
        """Get list of scenarios that have cached results for given config"""
        config_hash = self._get_config_hash(config)
        cached_scenarios = []
        
        if os.path.exists(self.cache_dir):
            for f in os.listdir(self.cache_dir):
                if f.endswith(f"_{config_hash}.json"):
                    # Extract scenario ID
                    scenario_id = f.replace("scenario_", "").replace(f"_{config_hash}.json", "")
                    cached_scenarios.append(scenario_id)
        
        return sorted(cached_scenarios)
    
    def get_cached_case_ids(
        self,
        scenario_id: str,
        config: Dict[str, Any]
    ) -> List[str]:
        """Get list of case IDs that have cached results"""
        cached = self.get(scenario_id, config)
        if cached:
            return [r["case_id"] for r in cached.get("results", [])]
        return []
    
    def clear(self, scenario_id: str = None, config: Dict[str, Any] = None):
        """
        Clear cache.
        
        Args:
            scenario_id: If provided, only clear this scenario
            config: If provided, only clear caches matching this config
        """
        if scenario_id and config:
            config_hash = self._get_config_hash(config)
            cache_file = self._get_cache_file(scenario_id, config_hash)
            if os.path.exists(cache_file):
                os.remove(cache_file)
        elif os.path.exists(self.cache_dir):
            import shutil
            shutil.rmtree(self.cache_dir)
            os.makedirs(self.cache_dir, exist_ok=True)


# ============================================================================
# Dataset Loading
# ============================================================================

def load_normal_dataset(dataset_path: str, scenario_id: str) -> List[NormalCase]:
    """
    Load normal (benign) dataset for a scenario.
    
    Args:
        dataset_path: Path to normal_datasets directory
        scenario_id: Scenario ID (e.g., "00", "01")
    
    Returns:
        List of NormalCase objects
    """
    file_path = os.path.join(dataset_path, f"scenario_{scenario_id}_normal.json")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Normal dataset not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Support multiple formats
    queries = data.get("queries", [])
    if not queries:
        queries = data.get("normal_cases", [])
    if not queries:
        queries = data.get("cases", [])
    
    cases = []
    for q in queries:
        cases.append(NormalCase(
            id=q.get("id", q.get("case_id", "unknown")),
            vulnerability=q.get("related_vulnerability", q.get("vulnerability", "")),
            category=q.get("category", ""),
            query_prompt=q.get("query_prompt", q.get("attack_prompt", "")),
            context=q.get("context", {}),
            expected_outcome=q.get("expected_outcome", "approve"),
            is_attack=q.get("is_attack", False)
        ))
    
    return cases


def get_available_normal_scenarios(dataset_path: str) -> List[str]:
    """Get list of available normal dataset scenario IDs"""
    scenarios = []
    if os.path.exists(dataset_path):
        for f in os.listdir(dataset_path):
            if f.startswith("scenario_") and f.endswith("_normal.json"):
                scenario_id = f.replace("scenario_", "").replace("_normal.json", "")
                scenarios.append(scenario_id)
    return sorted(scenarios)


def get_attack_types() -> List[str]:
    """Get list of available attack types from attack_datasets_synthesis"""
    synthesis_dir = os.path.join(_script_dir, "attack_datasets_synthesis")
    attack_types = []
    
    if os.path.exists(synthesis_dir):
        for d in os.listdir(synthesis_dir):
            if os.path.isdir(os.path.join(synthesis_dir, d)):
                attack_types.append(d)
    
    return sorted(attack_types)


def get_available_scenarios_for_attack_type(attack_type: str) -> List[str]:
    """Get available scenario IDs for a specific attack type"""
    attack_dir = os.path.join(_script_dir, "attack_datasets_synthesis", attack_type)
    scenarios = []
    
    if os.path.exists(attack_dir):
        for f in os.listdir(attack_dir):
            if f.startswith("scenario_") and f.endswith("_attacks.json"):
                scenario_id = f.replace("scenario_", "").replace("_attacks.json", "")
                scenarios.append(scenario_id)
    
    return sorted(scenarios)


# ============================================================================
# Metrics Computation
# ============================================================================

def compute_metrics(
    attack_results: List[Dict[str, Any]],
    normal_results: List[Dict[str, Any]]
) -> EvaluationMetrics:
    """
    Compute evaluation metrics from attack and normal results.
    
    Args:
        attack_results: List of results from attack dataset testing
            Each dict should have: case_id, is_attack (detected), confidence
        normal_results: List of results from normal dataset testing
            Each dict should have: case_id, is_attack (detected), confidence
    
    Returns:
        EvaluationMetrics object with computed metrics
    """
    metrics = EvaluationMetrics()
    
    metrics.total_attack_cases = len(attack_results)
    metrics.total_normal_cases = len(normal_results)
    
    # Count attack results
    attack_confidences = []
    for r in attack_results:
        is_detected = r.get("is_attack", False)
        if is_detected:
            metrics.true_positive += 1
        else:
            metrics.false_negative += 1
        attack_confidences.append(r.get("confidence", 0.0))
    
    # Count normal results
    normal_confidences = []
    for r in normal_results:
        is_detected = r.get("is_attack", False)
        if is_detected:
            metrics.false_positive += 1
        else:
            metrics.true_negative += 1
        normal_confidences.append(r.get("confidence", 0.0))
    
    # Compute average confidences
    if attack_confidences:
        metrics.avg_attack_confidence = sum(attack_confidences) / len(attack_confidences)
    if normal_confidences:
        metrics.avg_normal_confidence = sum(normal_confidences) / len(normal_confidences)
    
    # Compute derived metrics
    metrics.compute()
    
    return metrics


def compute_metrics_by_scenario(
    attack_results_by_scenario: Dict[str, List[Dict[str, Any]]],
    normal_results_by_scenario: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, EvaluationMetrics]:
    """
    Compute metrics for each scenario separately.
    
    Returns:
        Dict mapping scenario_id to EvaluationMetrics
    """
    metrics_by_scenario = {}
    
    all_scenarios = set(attack_results_by_scenario.keys()) | set(normal_results_by_scenario.keys())
    
    for scenario_id in all_scenarios:
        attack_results = attack_results_by_scenario.get(scenario_id, [])
        normal_results = normal_results_by_scenario.get(scenario_id, [])
        
        metrics_by_scenario[scenario_id] = compute_metrics(attack_results, normal_results)
    
    return metrics_by_scenario


# ============================================================================
# Report Generation
# ============================================================================

def print_evaluation_report(
    metrics: EvaluationMetrics,
    attack_type: str = "",
    defense_method: str = ""
):
    """Print formatted evaluation report"""
    print(f"\n{'='*80}")
    print(f"                    DEFENSE EVALUATION REPORT")
    if defense_method:
        print(f"                    Defense Method: {defense_method}")
    if attack_type:
        print(f"                    Attack Type: {attack_type}")
    print(f"{'='*80}")
    
    print(f"\n【Dataset Statistics】")
    print(f"  Total Attack Cases: {metrics.total_attack_cases}")
    print(f"  Total Normal Cases: {metrics.total_normal_cases}")
    print(f"  Total Cases: {metrics.total_attack_cases + metrics.total_normal_cases}")
    
    print(f"\n【Confusion Matrix】")
    print(f"                    Predicted")
    print(f"                  Attack    Normal")
    print(f"  Actual Attack    {metrics.true_positive:>5}     {metrics.false_negative:>5}   (TP, FN)")
    print(f"  Actual Normal    {metrics.false_positive:>5}     {metrics.true_negative:>5}   (FP, TN)")
    
    print(f"\n【Key Metrics】")
    print(f"  TPR (True Positive Rate / Recall): {metrics.tpr:.4f} ({metrics.tpr*100:.2f}%)")
    print(f"  FPR (False Positive Rate):         {metrics.fpr:.4f} ({metrics.fpr*100:.2f}%)")
    print(f"  TNR (True Negative Rate):          {metrics.tnr:.4f} ({metrics.tnr*100:.2f}%)")
    print(f"  FNR (False Negative Rate):         {metrics.fnr:.4f} ({metrics.fnr*100:.2f}%)")
    
    print(f"\n【Performance Metrics】")
    print(f"  Precision:  {metrics.precision:.4f} ({metrics.precision*100:.2f}%)")
    print(f"  Recall:     {metrics.recall:.4f} ({metrics.recall*100:.2f}%)")
    print(f"  F1 Score:   {metrics.f1_score:.4f} ({metrics.f1_score*100:.2f}%)")
    print(f"  Accuracy:   {metrics.accuracy:.4f} ({metrics.accuracy*100:.2f}%)")
    
    print(f"\n【Confidence Statistics】")
    print(f"  Avg Confidence (Attack):  {metrics.avg_attack_confidence:.4f}")
    print(f"  Avg Confidence (Normal):  {metrics.avg_normal_confidence:.4f}")
    
    print(f"{'='*80}\n")


def print_scenario_breakdown(
    metrics_by_scenario: Dict[str, EvaluationMetrics],
    scenario_info: Dict[str, Any] = None
):
    """Print per-scenario metrics breakdown"""
    print(f"\n{'='*100}")
    print(f"                              PER-SCENARIO BREAKDOWN")
    print(f"{'='*100}")
    print(f"{'Scenario':<10} {'Name':<30} {'Attacks':>8} {'Normals':>8} "
          f"{'TPR':>8} {'FPR':>8} {'F1':>8} {'Acc':>8}")
    print("-" * 100)
    
    total_attack = 0
    total_normal = 0
    total_tp = 0
    total_fp = 0
    total_tn = 0
    total_fn = 0
    
    for sid, m in sorted(metrics_by_scenario.items()):
        name = ""
        if scenario_info and sid in scenario_info:
            name = scenario_info[sid].get("name_en", "")[:28]
        
        print(f"{sid:<10} {name:<30} {m.total_attack_cases:>8} {m.total_normal_cases:>8} "
              f"{m.tpr*100:>7.1f}% {m.fpr*100:>7.1f}% {m.f1_score*100:>7.1f}% {m.accuracy*100:>7.1f}%")
        
        total_attack += m.total_attack_cases
        total_normal += m.total_normal_cases
        total_tp += m.true_positive
        total_fp += m.false_positive
        total_tn += m.true_negative
        total_fn += m.false_negative
    
    print("-" * 100)
    
    # Compute overall
    overall_tpr = total_tp / total_attack * 100 if total_attack > 0 else 0
    overall_fpr = total_fp / total_normal * 100 if total_normal > 0 else 0
    overall_acc = (total_tp + total_tn) / (total_attack + total_normal) * 100 if (total_attack + total_normal) > 0 else 0
    overall_prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
    overall_rec = total_tp / total_attack if total_attack > 0 else 0
    overall_f1 = 2 * overall_prec * overall_rec / (overall_prec + overall_rec) * 100 if (overall_prec + overall_rec) > 0 else 0
    
    print(f"{'TOTAL':<10} {'':<30} {total_attack:>8} {total_normal:>8} "
          f"{overall_tpr:>7.1f}% {overall_fpr:>7.1f}% {overall_f1:>7.1f}% {overall_acc:>7.1f}%")
    print(f"{'='*100}\n")


def save_evaluation_report(
    metrics: EvaluationMetrics,
    metrics_by_scenario: Dict[str, EvaluationMetrics],
    attack_results: List[Dict[str, Any]],
    normal_results: List[Dict[str, Any]],
    output_file: str,
    metadata: Dict[str, Any] = None
):
    """Save evaluation report to JSON file"""
    report = {
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat(),
        "overall_metrics": asdict(metrics),
        "scenario_metrics": {
            sid: asdict(m) for sid, m in metrics_by_scenario.items()
        },
        "attack_results_summary": {
            "total": len(attack_results),
            "detected": sum(1 for r in attack_results if r.get("is_attack", False)),
            "missed": sum(1 for r in attack_results if not r.get("is_attack", False))
        },
        "normal_results_summary": {
            "total": len(normal_results),
            "false_alarms": sum(1 for r in normal_results if r.get("is_attack", False)),
            "correct": sum(1 for r in normal_results if not r.get("is_attack", False))
        }
    }
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Evaluation report saved to: {output_file}")


# ============================================================================
# Defense Evaluator Class
# ============================================================================

class DefenseEvaluator:
    """
    High-level evaluator for defense methods.
    
    Handles:
    - Loading attack and normal datasets
    - Running tests with caching for normal results
    - Computing and reporting metrics
    """
    
    def __init__(
        self,
        defense_method: str,
        config: Dict[str, Any],
        output_dir: str = None
    ):
        """
        Initialize evaluator.
        
        Args:
            defense_method: Name of defense method
            config: Configuration for the defense method
            output_dir: Output directory for results
        """
        self.defense_method = defense_method
        self.config = config
        self.output_dir = output_dir or os.path.join(
            _script_dir, f"{defense_method}_results"
        )
        
        # Initialize cache
        self.normal_cache = NormalDatasetCache(defense_method)
        
        # Paths
        self.normal_dataset_path = os.path.join(_script_dir, "normal_datasets")
        self.attack_synthesis_path = os.path.join(_script_dir, "attack_datasets_synthesis")
        
        self.logger = logging.getLogger(f"DefenseEvaluator.{defense_method}")
    
    def get_cached_normal_results(
        self, 
        scenario_id: str
    ) -> Optional[Tuple[List[Dict], Dict]]:
        """
        Get cached normal results for a scenario.
        
        Returns:
            Tuple of (results_list, summary_dict) or None if not cached
        """
        cached = self.normal_cache.get(scenario_id, self.config)
        if cached:
            return cached.get("results", []), cached.get("summary", {})
        return None
    
    def cache_normal_results(
        self,
        scenario_id: str,
        results: List[Dict[str, Any]],
        summary: Dict[str, Any]
    ):
        """Cache normal results for a scenario"""
        self.normal_cache.set(scenario_id, self.config, results, summary)
    
    def get_scenarios_needing_normal_test(
        self, 
        scenarios: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Split scenarios into cached and uncached.
        
        Returns:
            Tuple of (cached_scenarios, uncached_scenarios)
        """
        cached = []
        uncached = []
        
        for sid in scenarios:
            if self.normal_cache.get(sid, self.config):
                cached.append(sid)
            else:
                uncached.append(sid)
        
        return cached, uncached
