# -*- coding: utf-8 -*-
"""
GPT-OSS-Safeguard-20B Safety Detection Test Script

This script is based on the OpenAI GPT-OSS-Safeguard-20B safety model, used to test the performance of content safety classifiers.
Supports detection rate statistics by major category and TPR/FPR calculation against normal datasets.

GPT-OSS-Safeguard-20B Features:
- Policy-based general safety model (no preset fixed categories)
- Uses native Harmony policy format
- Provides complete Chain of Thought (CoT)
- Supports configurable reasoning effort levels

References:
- HuggingFace: https://huggingface.co/openai/gpt-oss-safeguard-20b
- OpenRouter: https://openrouter.ai/openai/gpt-oss-safeguard-20b

Architectural Flow:
... (diagram omitted for brevity but keeping original structure) ...

Safety Policy (Harmony format):
  - Unauthorized Financial Operations
  - Security Control Bypass
  - Sensitive Data Exposure
  - System Manipulation
  - Social Engineering
  - Fraudulent Activities

Usage:
    # Test a single scenario (default uses configured API)
    python run_gpt_oss_safeguard_test.py --dataset attack_datasets --scenario 00
    
    # Test synthetic attack dataset and compare with normal dataset (compute TPR/FPR)
    python run_gpt_oss_safeguard_test.py --attack-type authority_impersonation --all --eval
    
    # Use mock mode (for testing, does not call actual API)
    python run_gpt_oss_safeguard_test.py --attack-type authority_impersonation --all --eval --mode mock
    
    # Clear normal dataset cache
    python run_gpt_oss_safeguard_test.py --clear-cache
    
    # List available attack types
    python run_gpt_oss_safeguard_test.py --list-attack-types
"""

import sys
import os
import json
import argparse
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Set path
_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)

# Load environment variables
from dotenv import load_dotenv
_env_paths = [
    os.path.join(_script_dir, '.env'),
    os.path.join(_script_dir, 'config', '.env'),
]
for _env_path in _env_paths:
    if os.path.exists(_env_path):
        load_dotenv(_env_path, override=True)
        break

# Import scenario category configuration
from config.scenario_categories import (
    MAJOR_CATEGORIES, SCENARIO_CATEGORY_MAPPING, SCENARIO_INFO, ATTACK_TYPES,
    get_scenario_category, get_scenarios_by_category, get_all_categories,
    get_all_attack_types, group_scenarios_by_category
)

# Import evaluation framework
from defense_evaluation import (
    NormalDatasetCache, AttackDatasetCache, EvaluationMetrics, NormalCase,
    load_normal_dataset, get_available_normal_scenarios,
    get_attack_types, get_available_scenarios_for_attack_type,
    compute_metrics, compute_metrics_by_scenario,
    print_evaluation_report, print_scenario_breakdown, save_evaluation_report
)


# ============================================================================
# Logging Configuration
# ============================================================================

class GPTOSSSafeguardLogger:
    """GPT-OSS-Safeguard dedicated logger"""
    
    def __init__(self, log_dir: str, verbose: bool = False):
        self.log_dir = log_dir
        self.verbose = verbose
        os.makedirs(log_dir, exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"gpt_oss_safeguard_test_{self.timestamp}.log")
        self.detail_file = os.path.join(log_dir, f"gpt_oss_safeguard_detail_{self.timestamp}.json")
        
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("GPTOSSSafeguard")
        
        self.detailed_logs: List[Dict] = []
    
    def log_case_start(self, case_id: str, attack_prompt: str):
        """Log case start"""
        self.logger.info(f"=" * 80)
        self.logger.info(f"Case: {case_id}")
        self.logger.info(f"=" * 80)
        if self.verbose:
            self.logger.info(f"Attack Prompt:\n{attack_prompt[:500]}...")
    
    def log_classification(self, result: Dict[str, Any], case_id: str = ""):
        """Log classification result"""
        is_attack = result.get('is_attack', False)
        violated_rules = result.get('violated_rules', [])
        confidence = result.get('confidence', 0.0)
        
        status = "UNSAFE" if is_attack else "SAFE"
        self.logger.info(f"[CLASSIFICATION] Status: {status}")
        self.logger.info(f"[CLASSIFICATION] Confidence: {confidence:.4f}")
        
        if violated_rules:
            self.logger.info(f"[CLASSIFICATION] Violated Rules: {', '.join(violated_rules)}")
        
        if self.verbose:
            reasoning = result.get('reasoning', '')
            self.logger.info(f"[CLASSIFICATION] Reasoning: {reasoning}")
        
        self.detailed_logs.append({
            "case_id": case_id,
            "stage": "classification",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_result(self, case_id: str, is_attack: bool, confidence: float, violated_rules: List[str]):
        """Log final result"""
        self.logger.info(f"[RESULT] Case: {case_id}")
        self.logger.info(f"[RESULT] Is Attack: {is_attack}")
        self.logger.info(f"[RESULT] Confidence: {confidence:.4f}")
        if violated_rules:
            self.logger.info(f"[RESULT] Violated Rules: {', '.join(violated_rules)}")
    
    def save_detailed_logs(self):
        """Save detailed logs"""
        with open(self.detail_file, 'w', encoding='utf-8') as f:
            json.dump(self.detailed_logs, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Detailed logs saved to: {self.detail_file}")


# ============================================================================
# Data Class Definitions
# ============================================================================

@dataclass
class AttackCase:
    """Attack Case"""
    id: str
    vulnerability: str
    attack_type: str
    attack_prompt: str
    context: Dict[str, Any]
    expected_outcome: str = "reject_attack"
    multi_turn: bool = False
    follow_up_prompts: List[str] = field(default_factory=list)
    all_turns: List[str] = field(default_factory=list)


@dataclass
class GPTOSSSafeguardTestResult:
    """GPT-OSS-Safeguard Detection Result"""
    case_id: str
    is_attack: bool
    confidence: float
    violated_rules: List[str] = field(default_factory=list)
    raw_response: str = ""
    reasoning: str = ""
    execution_time: float = 0.0
    error: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    is_multi_turn: bool = False
    total_turns: int = 1
    success_turn: int = 0
    per_turn_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Compatibility properties
    @property
    def categories(self) -> List[str]:
        """Compatibility with old interface"""
        return self.violated_rules
    
    @property
    def category_names(self) -> List[str]:
        """Compatibility with old interface"""
        return self.violated_rules


# ============================================================================
# GPT-OSS-Safeguard Tester
# ============================================================================

class GPTOSSSafeguardTester:
    """
    GPT-OSS-Safeguard Tester
    Supports both serial and parallel execution modes
    """
    
    def __init__(
        self,
        mode: str = "mock",
        model_name: str = None,
        api_url: str = None,
        api_key: str = None,
        threshold: float = 0.5,
        logger: GPTOSSSafeguardLogger = None,
        concurrency: int = 1,
        reasoning_effort: str = "medium",
    ):
        self.mode = mode
        self.model_name = model_name
        self.api_url = api_url
        self.api_key = api_key
        self.threshold = threshold
        self.safeguard_logger = logger
        self.concurrency = concurrency
        self.reasoning_effort = reasoning_effort
        self._print_lock = threading.Lock()
        
        self._init_detector()
    
    def _init_detector(self):
        """Initialize detector"""
        from defense.gpt_oss_safeguard import GPTOSSSafeguardDetector
        
        self.detector = GPTOSSSafeguardDetector(
            mode=self.mode,
            model_name=self.model_name,
            api_url=self.api_url,
            api_key=self.api_key,
            threshold=self.threshold,
            verbose=self.safeguard_logger.verbose if self.safeguard_logger else False,
            reasoning_effort=self.reasoning_effort,
        )
        
        print(f"GPT-OSS-Safeguard components initialization completed:")
        print(f"  - Mode: {self.mode}")
        if self.mode == "api":
            print(f"  - API URL: {self.api_url or '(from config file)'}")
            print(f"  - Model: {self.model_name or 'openai/gpt-oss-safeguard-20b'}")
        print(f"  - Threshold: {self.threshold}")
        print(f"  - Reasoning Effort: {self.reasoning_effort}")
        print(f"  - Policy: Financial Agent Safety Policy (Harmony format)")
        print(f"  - Concurrency: {self.concurrency}")
    
    def _safe_print(self, msg: str):
        """Thread-safe print"""
        with self._print_lock:
            print(msg)
    
    def test_case(self, case: AttackCase) -> GPTOSSSafeguardTestResult:
        """Test single case - supports multi-turn dialogue"""
        start_time = time.time()
        
        result = GPTOSSSafeguardTestResult(
            case_id=case.id,
            is_attack=False,
            confidence=0.0,
            is_multi_turn=case.multi_turn,
            total_turns=len(case.all_turns) if case.all_turns else 1
        )
        
        try:
            all_turns = case.all_turns if case.all_turns else [case.attack_prompt]
            result.total_turns = len(all_turns)
            
            conversation_history = []
            per_turn_results = []
            total_prompt_tokens = 0
            total_completion_tokens = 0
            
            for turn_idx, turn_prompt in enumerate(all_turns, 1):
                if self.safeguard_logger:
                    self.safeguard_logger.log_case_start(f"{case.id}_turn{turn_idx}", turn_prompt)
                
                # Build complete context including history
                if conversation_history:
                    context_with_history = "\n\n".join([
                        f"[Turn {i+1}]: {msg}" 
                        for i, msg in enumerate(conversation_history)
                    ]) + f"\n\n[Turn {turn_idx}]: {turn_prompt}"
                else:
                    context_with_history = turn_prompt
                
                # Call detector
                detection_result = self.detector.detect(
                    text=context_with_history,
                    context=case.context,
                )
                
                # Record results for this turn
                turn_result = {
                    "turn": turn_idx,
                    "prompt": turn_prompt[:200] + "..." if len(turn_prompt) > 200 else turn_prompt,
                    "is_attack": detection_result.is_attack,
                    "confidence": detection_result.confidence,
                    "violated_rules": detection_result.violated_rules,
                    "reasoning": detection_result.reasoning[:200] if detection_result.reasoning else ""
                }
                per_turn_results.append(turn_result)
                
                total_prompt_tokens += getattr(detection_result, 'prompt_tokens', 0) or 0
                total_completion_tokens += getattr(detection_result, 'completion_tokens', 0) or 0
                
                if self.safeguard_logger:
                    self.safeguard_logger.log_classification(
                        {
                            "is_attack": detection_result.is_attack,
                            "confidence": detection_result.confidence,
                            "violated_rules": detection_result.violated_rules,
                            "reasoning": detection_result.reasoning,
                        },
                        f"{case.id}_turn{turn_idx}"
                    )
                
                if detection_result.is_attack:
                    result.is_attack = True
                    result.confidence = detection_result.confidence
                    result.violated_rules = detection_result.violated_rules
                    result.raw_response = detection_result.raw_response
                    result.reasoning = detection_result.reasoning
                    result.success_turn = turn_idx
                    break
                
                conversation_history.append(turn_prompt)
            
            if not result.is_attack:
                result.confidence = detection_result.confidence if 'detection_result' in dir() else 0.0
                result.success_turn = 0
            
            result.per_turn_results = per_turn_results
            result.prompt_tokens = total_prompt_tokens
            result.completion_tokens = total_completion_tokens
            result.total_tokens = total_prompt_tokens + total_completion_tokens
            
            if self.safeguard_logger:
                self.safeguard_logger.log_result(
                    case.id,
                    result.is_attack,
                    result.confidence,
                    result.violated_rules
                )
            
        except Exception as e:
            result.error = str(e)
            if self.safeguard_logger:
                self.safeguard_logger.logger.error(f"Error processing case {case.id}: {e}")
            import traceback
            traceback.print_exc()
        
        result.execution_time = time.time() - start_time
        return result
    
    def test_normal_case(self, case: NormalCase) -> GPTOSSSafeguardTestResult:
        """Test normal case"""
        attack_case = AttackCase(
            id=case.id,
            vulnerability=case.vulnerability,
            attack_type="normal",
            attack_prompt=case.query_prompt,
            context=case.context,
            expected_outcome=case.expected_outcome,
            multi_turn=False
        )
        return self.test_case(attack_case)
    
    def test_dataset(self, cases: List[AttackCase]) -> List[GPTOSSSafeguardTestResult]:
        """Test dataset (supports parallel)"""
        total = len(cases)
        
        if self.concurrency <= 1:
            results = []
            for i, case in enumerate(cases, 1):
                print(f"\n[{i}/{total}] Testing case: {case.id}")
                result = self.test_case(case)
                results.append(result)
                
                status = "UNSAFE" if result.is_attack else "SAFE"
                print(f"  Result: {status} (confidence: {result.confidence:.4f})")
                if result.violated_rules:
                    print(f"  Violated Rules: {', '.join(result.violated_rules)}")
                print(f"  Time: {result.execution_time:.2f}s")
                if result.error:
                    print(f"  Error: {result.error}")
            return results
        else:
            return self._test_dataset_parallel(cases, is_attack=True)
    
    def _test_dataset_parallel(self, cases: List[AttackCase], is_attack: bool = True) -> List[GPTOSSSafeguardTestResult]:
        """Test dataset in parallel"""
        total = len(cases)
        results = [None] * total
        completed_count = [0]
        
        def process_case(idx: int, case: AttackCase) -> tuple:
            """Process single case"""
            result = self.test_case(case)
            return idx, result
        
        self._safe_print(f"\n[PARALLEL] Starting {total} cases with concurrency={self.concurrency}")
        
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            future_to_idx = {
                executor.submit(process_case, i, case): i 
                for i, case in enumerate(cases)
            }
            
            for future in as_completed(future_to_idx):
                idx, result = future.result()
                results[idx] = result
                completed_count[0] += 1
                
                # Print progress
                case = cases[idx]
                status = "UNSAFE" if result.is_attack else "SAFE"
                if is_attack:
                    label = "TP" if result.is_attack else "FN"
                else:
                    label = "FP" if result.is_attack else "TN"
                
                self._safe_print(
                    f"[{completed_count[0]}/{total}] {case.id}: {status} ({label}) "
                    f"conf={result.confidence:.2f} time={result.execution_time:.2f}s"
                    + (f" err={result.error[:50]}..." if result.error else "")
                )
        
        self._safe_print(f"[PARALLEL] Completed {total} cases")
        return results
    
    def test_normal_dataset(self, cases: List[NormalCase]) -> List[GPTOSSSafeguardTestResult]:
        """Test normal dataset (supports parallel)"""
        attack_cases = []
        for case in cases:
            attack_case = AttackCase(
                id=case.id,
                vulnerability=case.vulnerability,
                attack_type="normal",
                attack_prompt=case.query_prompt,
                context=case.context,
                expected_outcome=case.expected_outcome,
                multi_turn=False
            )
            attack_cases.append(attack_case)
        
        if self.concurrency <= 1:
            results = []
            for i, case in enumerate(attack_cases, 1):
                print(f"\n[{i}/{len(attack_cases)}] Testing normal case: {case.id}")
                result = self.test_case(case)
                results.append(result)
                
                status = "UNSAFE (FP)" if result.is_attack else "SAFE (TN)"
                print(f"  Result: {status} (confidence: {result.confidence:.4f})")
                print(f"  Time: {result.execution_time:.2f}s")
                if result.error:
                    print(f"  Error: {result.error}")
            return results
        else:
            return self._test_dataset_parallel(attack_cases, is_attack=False)


# ============================================================================
# Data Loading
# ============================================================================

def load_attack_dataset(dataset_path: str, scenario_id: str) -> List[AttackCase]:
    """Load attack dataset"""
    file_path = os.path.join(dataset_path, f"scenario_{scenario_id}_attacks.json")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    attacks = data.get("attacks", [])
    if not attacks:
        attacks = data.get("scenarios", [])
    if not attacks:
        attacks = data.get("attack_cases", [])
    if not attacks:
        attacks = data.get("cases", [])
    
    cases = []
    for attack in attacks:
        vulnerability = attack.get("vulnerability") or attack.get("target_vulnerability") or \
                       attack.get("context", {}).get("target_vulnerability") or ""
        
        attack_prompt = attack.get("attack_prompt", "")
        follow_up_prompts = attack.get("follow_up_prompts", [])
        is_multi_turn = attack.get("multi_turn", False)
        
        if is_multi_turn and follow_up_prompts:
            all_turns = [attack_prompt] + follow_up_prompts
        else:
            all_turns = [attack_prompt]
        
        cases.append(AttackCase(
            id=attack.get("id", attack.get("case_id", "unknown")),
            vulnerability=vulnerability,
            attack_type=attack.get("attack_type", ""),
            attack_prompt=attack_prompt,
            context=attack.get("context", attack.get("system_data", {})),
            expected_outcome=attack.get("expected_outcome", "reject_attack"),
            multi_turn=is_multi_turn,
            follow_up_prompts=follow_up_prompts,
            all_turns=all_turns
        ))
    
    return cases


def get_available_scenarios(dataset_path: str) -> List[str]:
    """Get available scenario ID list"""
    scenarios = []
    if os.path.exists(dataset_path):
        for f in os.listdir(dataset_path):
            if f.startswith("scenario_") and f.endswith("_attacks.json"):
                scenario_id = f.replace("scenario_", "").replace("_attacks.json", "")
                scenarios.append(scenario_id)
    return sorted(scenarios)


# ============================================================================
# Result Summary
# ============================================================================

def summarize_results(results: List[GPTOSSSafeguardTestResult], cases: List[AttackCase] = None) -> Dict[str, Any]:
    """Summarize test results"""
    total = len(results)
    if total == 0:
        return {"total_cases": 0, "attacks_detected": 0, "detection_rate": 0.0}
    
    attacks_detected = sum(1 for r in results if r.is_attack)
    errors = sum(1 for r in results if r.error)
    rule_breakdown = {}
    for r in results:
        for rule in r.violated_rules:
            rule_breakdown[rule] = rule_breakdown.get(rule, 0) + 1
    avg_confidence = sum(r.confidence for r in results) / total
    avg_time = sum(r.execution_time for r in results) / total
    tpr = attacks_detected / total if total > 0 else 0.0
    prompt_tokens = sum(r.prompt_tokens for r in results)
    completion_tokens = sum(r.completion_tokens for r in results)
    total_tokens = sum(r.total_tokens for r in results)
    
    return {
        "total_cases": total, 
        "attacks_detected": attacks_detected, 
        "detection_rate": tpr, 
        "rule_breakdown": rule_breakdown, 
        "average_confidence": avg_confidence, 
        "average_execution_time": avg_time, 
        "errors": errors, 
        "error_rate": errors / total if total > 0 else 0.0, 
        "prompt_tokens": prompt_tokens, 
        "completion_tokens": completion_tokens, 
        "total_tokens": total_tokens,
    }


def save_results(
    results: List[GPTOSSSafeguardTestResult],
    summary: Dict[str, Any],
    output_dir: str,
    scenario_id: str,
    dataset_name: str
):
    """Save test results"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    detail_file = os.path.join(
        output_dir,
        f"gpt_oss_safeguard_results_{dataset_name}_{scenario_id}_{timestamp}.json"
    )
    
    from defense.gpt_oss_safeguard.categories import FINANCIAL_AGENT_SAFETY_POLICY
    
    results_data = {
        "metadata": {
            "framework": "GPT-OSS-Safeguard-20B",
            "model": "openai/gpt-oss-safeguard-20b",
            "dataset": dataset_name,
            "scenario_id": scenario_id,
            "timestamp": timestamp,
            "total_cases": len(results),
            "architecture": {
                "type": "Safety Reasoning Model (MoE)",
                "parameters": "21B (3.6B active)",
                "policy_format": "Harmony (custom safety policy)",
                "policy_type": "Financial Agent Safety Policy",
            },
            "reference": {
                "huggingface": "https://huggingface.co/openai/gpt-oss-safeguard-20b",
                "openrouter": "https://openrouter.ai/openai/gpt-oss-safeguard-20b",
            }
        },
        "summary": summary,
        "results": [asdict(r) for r in results]
    }
    
    with open(detail_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {detail_file}")
    return detail_file


# ============================================================================
# Evaluation Mode
# ============================================================================

def _process_single_scenario(
    scenario_id: str,
    attack_type: str,
    args,
    config: Dict[str, Any],
    attack_dataset_path: str,
    normal_dataset_path: str,
    normal_cache: NormalDatasetCache,
    attack_cache: AttackDatasetCache,
    print_lock: threading.Lock = None
) -> Dict[str, Any]:
    """Process single scenario test"""
    def safe_print(msg: str):
        if print_lock:
            with print_lock:
                print(msg)
        else:
            print(msg)
    
    result = {
        "scenario_id": scenario_id,
        "attack_results": [],
        "normal_results": [],
        "error": None
    }
    
    try:
        safe_print(f"\n[Scenario {scenario_id}] Starting...")
        
        # Test attack dataset
        attack_cases = load_attack_dataset(attack_dataset_path, scenario_id)
        if args.max_cases:
            attack_cases = attack_cases[:args.max_cases]
        safe_print(f"[Scenario {scenario_id}] Loaded {len(attack_cases)} attack cases")
        
        # Check attack dataset cache
        attack_cached = attack_cache.get(scenario_id, config)
        cached_case_ids = set()
        if attack_cached and not getattr(args, 'no_cache', False):
            cached_case_ids = {r["case_id"] for r in attack_cached.get("results", [])}
            safe_print(f"[Scenario {scenario_id}] Found {len(cached_case_ids)} cached attack results")
        
        cases_to_test = [c for c in attack_cases if c.id not in cached_case_ids]
        
        tester = None
        if cases_to_test:
            safe_print(f"[Scenario {scenario_id}] Testing {len(cases_to_test)} new attack cases...")
            
            case_concurrency = 1 if getattr(args, 'scenario_parallel', 1) > 1 else getattr(args, 'concurrency', 1)
            
            tester = GPTOSSSafeguardTester(
                mode=args.mode,
                model_name=args.model_name,
                api_url=args.api_url,
                api_key=args.api_key,
                threshold=args.threshold,
                logger=None,
                concurrency=case_concurrency,
                reasoning_effort=args.reasoning_effort,
            )
            
            new_attack_results = tester.test_dataset(cases_to_test)
            new_attack_results_dicts = [
                {
                    "case_id": r.case_id, 
                    "is_attack": r.is_attack, 
                    "confidence": r.confidence,
                    "prompt_tokens": r.prompt_tokens,
                    "completion_tokens": r.completion_tokens,
                    "total_tokens": r.total_tokens,
                    "execution_time": r.execution_time
                }
                for r in new_attack_results
            ]
        else:
            safe_print(f"[Scenario {scenario_id}] All attack cases cached, skipping testing")
            new_attack_results_dicts = []
        
        # Merge cached results
        if attack_cached:
            cached_results = {r["case_id"]: r for r in attack_cached.get("results", [])}
        else:
            cached_results = {}
        
        for r in new_attack_results_dicts:
            cached_results[r["case_id"]] = r
        
        attack_results_dicts = []
        for case in attack_cases:
            if case.id in cached_results:
                attack_results_dicts.append(cached_results[case.id])
        
        # Update cache
        if new_attack_results_dicts:
            attack_summary = {
                "total_cases": len(attack_results_dicts),
                "attacks_detected": sum(1 for r in attack_results_dicts if r["is_attack"]),
                "detection_rate": sum(1 for r in attack_results_dicts if r["is_attack"]) / len(attack_results_dicts) if attack_results_dicts else 0
            }
            attack_cache.set(scenario_id, config, attack_results_dicts, attack_summary)
        
        result["attack_results"] = attack_results_dicts
        
        # Test normal dataset
        cached = normal_cache.get(scenario_id, config)
        if cached and not getattr(args, 'no_cache', False):
            safe_print(f"[Scenario {scenario_id}] Using cached normal results")
            normal_results_dicts = cached.get("results", [])
        else:
            try:
                normal_cases = load_normal_dataset(normal_dataset_path, scenario_id)
                if args.max_cases:
                    normal_cases = normal_cases[:args.max_cases]
                safe_print(f"[Scenario {scenario_id}] Loaded {len(normal_cases)} normal cases")
                
                if tester is None:
                    case_concurrency = 1 if getattr(args, 'scenario_parallel', 1) > 1 else getattr(args, 'concurrency', 1)
                    tester = GPTOSSSafeguardTester(
                        mode=args.mode,
                        model_name=args.model_name,
                        api_url=args.api_url,
                        api_key=args.api_key,
                        threshold=args.threshold,
                        logger=None,
                        concurrency=case_concurrency,
                        reasoning_effort=args.reasoning_effort,
                    )
                
                normal_results = tester.test_normal_dataset(normal_cases)
                normal_results_dicts = [
                    {
                        "case_id": r.case_id, 
                        "is_attack": r.is_attack, 
                        "confidence": r.confidence,
                        "prompt_tokens": r.prompt_tokens,
                        "completion_tokens": r.completion_tokens,
                        "total_tokens": r.total_tokens,
                        "execution_time": r.execution_time
                    }
                    for r in normal_results
                ]
                
                normal_summary = {
                    "total_cases": len(normal_results),
                    "false_positives": sum(1 for r in normal_results if r.is_attack),
                    "true_negatives": sum(1 for r in normal_results if not r.is_attack)
                }
                normal_cache.set(scenario_id, config, normal_results_dicts, normal_summary)
                
            except FileNotFoundError:
                safe_print(f"[Scenario {scenario_id}] Normal dataset not found, skipping...")
                normal_results_dicts = []
        
        result["normal_results"] = normal_results_dicts
        
        attack_detected = sum(1 for r in attack_results_dicts if r["is_attack"])
        normal_fp = sum(1 for r in normal_results_dicts if r["is_attack"])
        tpr = attack_detected / len(attack_results_dicts) * 100 if attack_results_dicts else 0
        fpr = normal_fp / len(normal_results_dicts) * 100 if len(normal_results_dicts) > 0 else 0
        safe_print(f"[Scenario {scenario_id}] Done: Attack {attack_detected}/{len(attack_results_dicts)} (TPR={tpr:.1f}%), Normal FP={normal_fp}/{len(normal_results_dicts)} (FPR={fpr:.1f}%)")
        
    except Exception as e:
        result["error"] = str(e)
        safe_print(f"[Scenario {scenario_id}] Error: {e}")
        import traceback
        traceback.print_exc()
    
    return result


def run_evaluation(
    attack_type: str,
    scenarios: List[str],
    args,
    logger: GPTOSSSafeguardLogger,
    output_dir: str
):
    """Run evaluation mode"""
    print(f"\n{'='*80}")
    print(f"                    EVALUATION MODE")
    print(f"                    Attack Type: {attack_type}")
    print(f"{'='*80}")
    
    config = {
        "mode": args.mode,
        "threshold": args.threshold,
        "model_name": args.model_name,
        "api_url": args.api_url,
        "reasoning_effort": args.reasoning_effort,
    }
    
    normal_cache = NormalDatasetCache("gpt_oss_safeguard")
    attack_cache = AttackDatasetCache("gpt_oss_safeguard", attack_type)
    
    attack_dataset_path = os.path.join(_script_dir, "attack_datasets_synthesis", attack_type)
    normal_dataset_path = os.path.join(_script_dir, "normal_datasets")
    
    scenario_parallel = getattr(args, 'scenario_parallel', 1)
    
    all_attack_results = []
    all_normal_results = []
    attack_results_by_scenario = {}
    normal_results_by_scenario = {}
    
    if scenario_parallel <= 1:
        for scenario_id in scenarios:
            print(f"\n{'='*60}")
            print(f"Scenario {scenario_id}")
            print(f"{'='*60}")
            
            result = _process_single_scenario(
                scenario_id=scenario_id,
                attack_type=attack_type,
                args=args,
                config=config,
                attack_dataset_path=attack_dataset_path,
                normal_dataset_path=normal_dataset_path,
                normal_cache=normal_cache,
                attack_cache=attack_cache,
                print_lock=None
            )
            
            all_attack_results.extend(result["attack_results"])
            all_normal_results.extend(result["normal_results"])
            attack_results_by_scenario[scenario_id] = result["attack_results"]
            normal_results_by_scenario[scenario_id] = result["normal_results"]
    else:
        print(f"\n[SCENARIO PARALLEL] Using {scenario_parallel} workers for {len(scenarios)} scenarios")
        print_lock = threading.Lock()
        
        with ThreadPoolExecutor(max_workers=scenario_parallel) as executor:
            future_to_scenario = {
                executor.submit(
                    _process_single_scenario,
                    scenario_id=sid,
                    attack_type=attack_type,
                    args=args,
                    config=config,
                    attack_dataset_path=attack_dataset_path,
                    normal_dataset_path=normal_dataset_path,
                    normal_cache=normal_cache,
                    attack_cache=attack_cache,
                    print_lock=print_lock
                ): sid
                for sid in scenarios
            }
            
            completed = 0
            for future in as_completed(future_to_scenario):
                scenario_id = future_to_scenario[future]
                completed += 1
                
                try:
                    result = future.result()
                    all_attack_results.extend(result["attack_results"])
                    all_normal_results.extend(result["normal_results"])
                    attack_results_by_scenario[result["scenario_id"]] = result["attack_results"]
                    normal_results_by_scenario[result["scenario_id"]] = result["normal_results"]
                    
                    with print_lock:
                        print(f"[SCENARIO PARALLEL] Completed {completed}/{len(scenarios)}: {scenario_id}")
                        
                except Exception as e:
                    with print_lock:
                        print(f"[SCENARIO PARALLEL] Failed {scenario_id}: {e}")
        
        print(f"\n[SCENARIO PARALLEL] All {len(scenarios)} scenarios completed")
    
    # Calculate overall metrics
    if all_attack_results or all_normal_results:
        overall_metrics = compute_metrics(all_attack_results, all_normal_results)
        scenario_metrics = compute_metrics_by_scenario(
            attack_results_by_scenario, 
            normal_results_by_scenario
        )
        
        print_evaluation_report(overall_metrics, attack_type, "GPT-OSS-Safeguard-20B")
        
        # Token statistics
        total_prompt_tokens = sum(r.get('prompt_tokens', 0) for r in all_attack_results) + \
                              sum(r.get('prompt_tokens', 0) for r in all_normal_results)
        total_completion_tokens = sum(r.get('completion_tokens', 0) for r in all_attack_results) + \
                                 sum(r.get('completion_tokens', 0) for r in all_normal_results)
        total_tokens = sum(r.get('total_tokens', 0) for r in all_attack_results) + \
                       sum(r.get('total_tokens', 0) for r in all_normal_results)
        
        total_attack_time = sum(r.get('execution_time', 0) for r in all_attack_results)
        total_normal_time = sum(r.get('execution_time', 0) for r in all_normal_results)
        total_time = total_attack_time + total_normal_time
        
        total_cases = len(all_attack_results) + len(all_normal_results)
        total_attack_cases = len(all_attack_results)
        
        print(f"\n[Token Statistics]")
        print(f"  Prompt Tokens: {total_prompt_tokens:,}")
        print(f"  Completion Tokens: {total_completion_tokens:,}")
        print(f"  Total Tokens: {total_tokens:,}")
        if total_cases > 0:
            print(f"  Average Tokens per Case: {total_tokens / total_cases:,.1f}")
        
        print(f"\n[Time Consumption Statistics]")
        print(f"  Total Time: {total_time:.2f}s")
        if total_attack_cases > 0:
            print(f"  Average Attack Case Time: {total_attack_time / total_attack_cases:.2f}s")
        if total_cases > 0:
            print(f"  Average Time per Case: {total_time / total_cases:.2f}s")
        
        scenario_info_dict = {
            sid: {"name_en": SCENARIO_INFO.get(sid).name_en if SCENARIO_INFO.get(sid) else "Unknown"}
            for sid in scenarios
        }
        print_scenario_breakdown(scenario_metrics, scenario_info_dict)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(
            output_dir,
            f"gpt_oss_safeguard_evaluation_{attack_type}_{timestamp}.json"
        )
        save_evaluation_report(
            overall_metrics,
            scenario_metrics,
            all_attack_results,
            all_normal_results,
            report_file,
            metadata={
                "defense_method": "GPT-OSS-Safeguard-20B",
                "attack_type": attack_type,
                "scenarios": scenarios,
                "config": config
            }
        )


# ============================================================================
# Main Function
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="GPT-OSS-Safeguard-20B Safety Detection Test Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Test single scenario (default uses configured OpenRouter API)
    python run_gpt_oss_safeguard_test.py --dataset attack_datasets --scenario 00
    
    # Test synthetic attack dataset and compare with normal dataset (calculate TPR/FPR)
    python run_gpt_oss_safeguard_test.py --attack-type authority_impersonation --all --eval
    
    # Use mock mode (for testing, does not call actual API)
    python run_gpt_oss_safeguard_test.py --attack-type authority_impersonation --all --eval --mode mock
    
    # Clear normal dataset cache
    python run_gpt_oss_safeguard_test.py --clear-cache
    
    # List available attack types
    python run_gpt_oss_safeguard_test.py --list-attack-types
        """
    )
    
    # Dataset selection
    parser.add_argument("--dataset", type=str, help="Dataset directory name")
    parser.add_argument("--attack-type", type=str, help="Attack type, multiple types separated by commas")
    parser.add_argument("--scenario", type=str, help="Scenario ID")
    parser.add_argument("--all", action="store_true", help="Test all scenarios")
    parser.add_argument("--category", type=str, help="Test by major category")
    
    # Evaluation mode
    parser.add_argument("--eval", action="store_true", help="Enable evaluation mode")
    
    # Cache management
    parser.add_argument("--clear-cache", action="store_true", help="Clear cache")
    parser.add_argument("--no-cache", action="store_true", help="Do not use cache")
    
    # List options
    parser.add_argument("--list-attack-types", action="store_true", help="List attack types")
    parser.add_argument("--list-categories", action="store_true", help="List major categories")
    
    # Model configuration
    parser.add_argument("--mode", type=str, default="api", choices=["api", "mock"],
                        help="Running mode: api=use API (default), mock=mock mode")
    parser.add_argument("--model-name", type=str, default=None,
                        help="Model name (default: openai/gpt-oss-safeguard-20b)")
    parser.add_argument("--api-url", type=str, default=None,
                        help="API URL (read from config file by default)")
    parser.add_argument("--api-key", type=str, default=None,
                        help="API key (read from config file by default)")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="Confidence threshold (default: 0.5)")
    parser.add_argument("--reasoning-effort", type=str, default="medium",
                        choices=["low", "medium", "high"],
                        help="Reasoning effort level (default: medium)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory (default: sandbox/gpt_oss_safeguard_results)")
    parser.add_argument("--max-cases", type=int, default=None,
                        help="Maximum number of test cases per scenario")
    parser.add_argument("--concurrency", "-c", type=int, default=5,
                        help="Case-level concurrency (default: 5)")
    parser.add_argument("--scenario-parallel", type=int, default=20,
                        help="Scenario-level parallelism (default: 10)")
    
    args = parser.parse_args()
    
    # List attack types
    if args.list_attack_types:
        print("\nAvailable attack types:")
        print("-" * 50)
        attack_types = get_attack_types()
        for at in attack_types:
            scenarios = get_available_scenarios_for_attack_type(at)
            print(f"  {at:<30} ({len(scenarios)} scenarios)")
        print("-" * 50)
        return
    
    # List major categories
    if args.list_categories:
        print("\nAvailable major categories:")
        print("-" * 70)
        groups = group_scenarios_by_category()
        for cat_id, cat_info in MAJOR_CATEGORIES.items():
            scenarios = groups.get(cat_id, [])
            print(f"  {cat_id:<20} {cat_info['name_en']:<30} ({cat_info['name_zh']}) - {len(scenarios)} scenarios")
        print("-" * 70)
        return
    
    # Clear cache
    if args.clear_cache:
        cache = NormalDatasetCache("gpt_oss_safeguard")
        cache.clear()
        print("Cache cleared successfully.")
        return
    
    # Set output directory
    output_dir = args.output_dir or os.path.join(_script_dir, "gpt_oss_safeguard_results")
    log_dir = os.path.join(output_dir, "logs")
    
    # Initialize logger
    safeguard_logger = GPTOSSSafeguardLogger(log_dir, args.verbose)
    
    # Evaluation mode
    if args.eval and args.attack_type:
        attack_types = [at.strip() for at in args.attack_type.split(",")]
        
        for attack_type in attack_types:
            if args.all:
                scenarios = get_available_scenarios_for_attack_type(attack_type)
            elif args.scenario:
                scenarios = [args.scenario]
            else:
                print(f"Error: Please specify --scenario or --all for attack type {attack_type}")
                continue
            
            if not scenarios:
                print(f"No scenarios found for attack type: {attack_type}")
                continue
            
            run_evaluation(attack_type, scenarios, args, safeguard_logger, output_dir)
        
        safeguard_logger.save_detailed_logs()
        print(f"\n日志文件: {safeguard_logger.log_file}")
        print(f"详细日志: {safeguard_logger.detail_file}")
        return
    
    # Legacy mode
    if not args.dataset:
        print("Error: --dataset is required (or use --attack-type with --eval)")
        parser.print_help()
        sys.exit(1)
    
    dataset_path = os.path.join(_script_dir, args.dataset)
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset path not found: {dataset_path}")
        sys.exit(1)
    
    dataset_name = args.dataset.replace("/", "_").replace("\\", "_")
    
    if args.category:
        scenarios = get_scenarios_by_category(args.category)
        available = get_available_scenarios(dataset_path)
        scenarios = [s for s in scenarios if s in available]
        if not scenarios:
            print(f"Error: No scenarios found for category {args.category}")
            sys.exit(1)
    elif args.all:
        scenarios = get_available_scenarios(dataset_path)
        if not scenarios:
            print(f"Error: No scenarios found in {dataset_path}")
            sys.exit(1)
    elif args.scenario:
        scenarios = [args.scenario]
    else:
        print("Error: Please specify --scenario, --all, or --category")
        parser.print_help()
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"GPT-OSS-Safeguard-20B Safety Detection Test")
    print(f"{'='*80}")
    print(f"Dataset: {args.dataset}")
    print(f"Scenarios: {scenarios}")
    print(f"Running mode: {args.mode}")
    print(f"Reasoning effort level: {args.reasoning_effort}")
    print(f"Confidence threshold: {args.threshold}")
    print(f"{'='*80}\n")
    
    all_results = []
    all_summaries = {}
    
    for scenario_id in scenarios:
        print(f"\n{'='*60}")
        print(f"Scenario {scenario_id}")
        print(f"{'='*60}")
        
        try:
            cases = load_attack_dataset(dataset_path, scenario_id)
            if args.max_cases:
                cases = cases[:args.max_cases]
            print(f"Scenario {scenario_id}: Loaded {len(cases)} test cases")
            
            tester = GPTOSSSafeguardTester(
                mode=args.mode,
                model_name=args.model_name,
                api_url=args.api_url,
                api_key=args.api_key,
                threshold=args.threshold,
                logger=safeguard_logger,
                concurrency=args.concurrency,
                reasoning_effort=args.reasoning_effort,
            )
            
            results = tester.test_dataset(cases)
            summary = summarize_results(results)
            
            print(f"\nScenario {scenario_id} Results:")
            print(f"  - Total cases: {summary['total_cases']}")
            print(f"  - Attacks detected: {summary['attacks_detected']}")
            print(f"  - Detection rate (TPR): {summary['detection_rate']:.2%}")
            
            save_results(results, summary, output_dir, scenario_id, dataset_name)
            
            all_results.extend(results)
            all_summaries[scenario_id] = summary
            
        except Exception as e:
            print(f"Error testing scenario {scenario_id}: {e}")
            import traceback
            traceback.print_exc()
    
    safeguard_logger.save_detailed_logs()
    
    if len(scenarios) > 1:
        print(f"\n{'='*80}")
        print(f"Overall Summary")
        print(f"{'='*80}")
        
        total_cases = sum(s['total_cases'] for s in all_summaries.values())
        total_detected = sum(s['attacks_detected'] for s in all_summaries.values())
        
        print(f"Total test cases: {total_cases}")
        print(f"Total attacks detected: {total_detected}")
        print(f"Overall detection rate: {total_detected/total_cases:.2%}" if total_cases > 0 else "N/A")
    
    print(f"\nLog file: {safeguard_logger.log_file}")
    print(f"Detailed log: {safeguard_logger.detail_file}")


if __name__ == "__main__":
    main()
