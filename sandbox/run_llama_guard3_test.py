# -*- coding: utf-8 -*-
"""
LLaMA Guard 3 Native Framework Test Script

This script is based on Meta LLaMA Guard 3 official implementation, used to test the performance of content safety classifiers.
Supports detection rate statistics by major category and TPR/FPR calculation against normal datasets.

References:
- LLaMA Guard 3: https://huggingface.co/meta-llama/Llama-Guard-3-8B
- LLaMA Guard Paper: https://arxiv.org/abs/2312.06674
- MLCommons AI Safety Taxonomy: https://mlcommons.org/ai-safety/

Architecture Flow (strictly follows official implementation):
┌─────────────────────────────────────────────────────────────────────┐
│                    LLaMA Guard 3 Native Flow                        │
├─────────────────────────────────────────────────────────────────────┤
│  User Input                                                          │
│      │                                                               │
│      ▼                                                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Safety Classification (Single LLM Call)                      │    │
│  │  - Input: User message (+ optional Agent response)           │    │
│  │  - Model: Llama-Guard-3-8B (fine-tuned from Llama-3.1-8B)   │    │
│  │  - Output: "safe" or "unsafe\nS1,S2,..."                     │    │
│  │  - Categories: 14 MLCommons AI Safety categories             │    │
│  └─────────────────────────────────────────────────────────────┘    │
│      │                                                               │
│      ▼                                                               │
│  Response: safe / unsafe (with violated categories)                  │
└─────────────────────────────────────────────────────────────────────┘

14 Safety Categories (based on MLCommons standards):
  S1:  Violent Crimes
  S2:  Non-Violent Crimes (fraud, hacking, etc.)
  S3:  Sex-Related Crimes
  S4:  Child Sexual Exploitation
  S5:  Defamation
  S6:  Specialized Advice (medical, legal, financial)
  S7:  Privacy
  S8:  Intellectual Property
  S9:  Indiscriminate Weapons
  S10: Hate
  S11: Suicide & Self-Harm
  S12: Sexual Content
  S13: Elections
  S14: Code Interpreter Abuse

Usage:
    # Test single scenario (default uses configured API)
    python run_llama_guard3_test.py --dataset attack_datasets --scenario 00
    
    # Test synthetic attack dataset and compare with normal dataset (calculate TPR/FPR)
    python run_llama_guard3_test.py --attack-type authority_impersonation --all --eval
    
    # Use mock mode (for testing, does not call actual API)
    python run_llama_guard3_test.py --attack-type authority_impersonation --all --eval --mode mock
    
    # Clear normal dataset cache
    python run_llama_guard3_test.py --clear-cache
    
    # List available attack types
    python run_llama_guard3_test.py --list-attack-types
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

class LlamaGuardLogger:
    """LLaMA Guard 3 dedicated logger"""
    
    def __init__(self, log_dir: str, verbose: bool = False):
        self.log_dir = log_dir
        self.verbose = verbose
        os.makedirs(log_dir, exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"llama_guard3_test_{self.timestamp}.log")
        self.detail_file = os.path.join(log_dir, f"llama_guard3_detail_{self.timestamp}.json")
        
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("LlamaGuard3")
        
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
        categories = result.get('categories', [])
        confidence = result.get('confidence', 0.0)
        
        status = "UNSAFE" if is_attack else "SAFE"
        self.logger.info(f"[CLASSIFICATION] Status: {status}")
        self.logger.info(f"[CLASSIFICATION] Confidence: {confidence:.4f}")
        
        if categories:
            self.logger.info(f"[CLASSIFICATION] Violated Categories: {', '.join(categories)}")
            category_names = result.get('category_names', [])
            if category_names:
                self.logger.info(f"[CLASSIFICATION] Category Names: {', '.join(category_names)}")
        
        if self.verbose:
            raw_response = result.get('raw_response', '')
            self.logger.info(f"[CLASSIFICATION] Raw Response: {raw_response}")
        
        self.detailed_logs.append({
            "case_id": case_id,
            "stage": "classification",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_result(self, case_id: str, is_attack: bool, confidence: float, categories: List[str]):
        """Log final result"""
        self.logger.info(f"[RESULT] Case: {case_id}")
        self.logger.info(f"[RESULT] Is Attack: {is_attack}")
        self.logger.info(f"[RESULT] Confidence: {confidence:.4f}")
        if categories:
            self.logger.info(f"[RESULT] Categories: {', '.join(categories)}")
    
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
    """Attack case"""
    id: str
    vulnerability: str
    attack_type: str
    attack_prompt: str
    context: Dict[str, Any]
    expected_outcome: str = "reject_attack"
    multi_turn: bool = False
    follow_up_prompts: List[str] = field(default_factory=list)
    # Multi-turn dialogue: preserve all turn prompts list for true multi-turn interaction
    all_turns: List[str] = field(default_factory=list)  # [turn1, turn2, ...]


@dataclass
class LlamaGuardResult:
    """LLaMA Guard 3 detection result"""
    case_id: str
    is_attack: bool
    confidence: float
    categories: List[str] = field(default_factory=list)
    category_names: List[str] = field(default_factory=list)
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


# ============================================================================
# LLaMA Guard 3 Tester
# ============================================================================

class LlamaGuard3Tester:
    """
    LLaMA Guard 3 Tester - Strictly follows official implementation
    Supports both serial and parallel execution modes
    """
    
    def __init__(
        self,
        mode: str = "mock",
        model_path: str = None,
        api_url: str = None,
        api_key: str = None,
        threshold: float = 0.5,
        device: str = "cuda",
        llama_guard_logger: LlamaGuardLogger = None,
        concurrency: int = 1,  # concurrency, default is 1 (serial)
    ):
        self.mode = mode
        self.model_path = model_path
        self.api_url = api_url
        self.api_key = api_key
        self.threshold = threshold
        self.device = device
        self.llama_guard_logger = llama_guard_logger
        self.concurrency = concurrency
        self._print_lock = threading.Lock()  # 用于线程安全的打印
        
        self._init_detector()
    
    def _init_detector(self):
        """Initialize detector"""
        from defense.llama_guard import LlamaGuard3Detector
        
        self.detector = LlamaGuard3Detector(
            mode=self.mode,
            model_path=self.model_path,
            api_url=self.api_url,
            api_key=self.api_key,
            threshold=self.threshold,
            device=self.device,
            verbose=self.llama_guard_logger.verbose if self.llama_guard_logger else False,
        )
        
        print(f"LLaMA Guard 3 components initialization completed:")
        print(f"  - Mode: {self.mode}")
        if self.mode == "local":
            print(f"  - Model: {self.model_path or 'meta-llama/Llama-Guard-3-8B'}")
            print(f"  - Device: {self.device}")
        elif self.mode == "api":
            print(f"  - API URL: {self.api_url}")
        print(f"  - Threshold: {self.threshold}")
        print(f"  - Categories: 14 MLCommons AI Safety categories")
        print(f"  - Single LLM call per input (no custom actions)")
        print(f"  - Concurrency: {self.concurrency}")
    
    def _safe_print(self, msg: str):
        """Thread-safe print"""
        with self._print_lock:
            print(msg)
    
    def test_case(self, case: AttackCase) -> LlamaGuardResult:
        """
        Test single case - supports true multi-turn dialogue (academic standard)
        
        Multi-turn dialogue handling:
        - Send prompts turn by turn, maintain conversation history
        - Perform detection on each turn, record results for each turn
        - Mark as successful if attack is detected in any turn
        - Record turns needed for success (for academic evaluation)
        """
        start_time = time.time()
        
        result = LlamaGuardResult(
            case_id=case.id,
            is_attack=False,
            confidence=0.0,
            is_multi_turn=case.multi_turn,
            total_turns=len(case.all_turns) if case.all_turns else 1
        )
        
        try:
            # 获取所有轮次的 prompts
            all_turns = case.all_turns if case.all_turns else [case.attack_prompt]
            result.total_turns = len(all_turns)
            
            # Maintain conversation history (for context accumulation)
            conversation_history = []
            per_turn_results = []
            total_prompt_tokens = 0
            total_completion_tokens = 0
            
            for turn_idx, turn_prompt in enumerate(all_turns, 1):
                if self.llama_guard_logger:
                    self.llama_guard_logger.log_case_start(f"{case.id}_turn{turn_idx}", turn_prompt)
                
                # 构建包含历史的完整上下文
                # 学术规范：每轮检测时包含之前的对话历史
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
                
                # 记录本轮结果
                turn_result = {
                    "turn": turn_idx,
                    "prompt": turn_prompt[:200] + "..." if len(turn_prompt) > 200 else turn_prompt,
                    "is_attack": detection_result.is_attack,
                    "confidence": detection_result.confidence,
                    "categories": detection_result.categories
                }
                per_turn_results.append(turn_result)
                
                # Accumulate token statistics
                total_prompt_tokens += getattr(detection_result, 'prompt_tokens', 0) or 0
                total_completion_tokens += getattr(detection_result, 'completion_tokens', 0) or 0
                
                if self.llama_guard_logger:
                    self.llama_guard_logger.log_classification(
                        {
                            "is_attack": detection_result.is_attack,
                            "confidence": detection_result.confidence,
                            "categories": detection_result.categories,
                            "category_names": detection_result.category_names,
                            "raw_response": detection_result.raw_response,
                        },
                        f"{case.id}_turn{turn_idx}"
                    )
                
                # 如果检测到攻击，记录成功轮次
                if detection_result.is_attack:
                    result.is_attack = True
                    result.confidence = detection_result.confidence
                    result.categories = detection_result.categories
                    result.category_names = detection_result.category_names
                    result.raw_response = detection_result.raw_response
                    result.reasoning = detection_result.reasoning
                    result.success_turn = turn_idx
                    # Stop after detecting attack
                    break
                
                # 更新对话历史
                conversation_history.append(turn_prompt)
            
            # If no attack is detected in all turns
            if not result.is_attack:
                result.confidence = detection_result.confidence if 'detection_result' in dir() else 0.0
                result.success_turn = 0
            
            result.per_turn_results = per_turn_results
            result.prompt_tokens = total_prompt_tokens
            result.completion_tokens = total_completion_tokens
            result.total_tokens = total_prompt_tokens + total_completion_tokens
            
            if self.llama_guard_logger:
                self.llama_guard_logger.log_result(
                    case.id,
                    result.is_attack,
                    result.confidence,
                    result.categories
                )
            
        except Exception as e:
            result.error = str(e)
            if self.llama_guard_logger:
                self.llama_guard_logger.logger.error(f"Error processing case {case.id}: {e}")
            import traceback
            traceback.print_exc()
        
        result.execution_time = time.time() - start_time
        return result
    
    def test_normal_case(self, case: NormalCase) -> LlamaGuardResult:
        """测试正常案例"""
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
    
    def test_dataset(self, cases: List[AttackCase]) -> List[LlamaGuardResult]:
        """Test dataset (supports parallel)"""
        total = len(cases)
        
        if self.concurrency <= 1:
            # Serial mode
            results = []
            for i, case in enumerate(cases, 1):
                print(f"\n[{i}/{total}] Testing case: {case.id}")
                result = self.test_case(case)
                results.append(result)
                
                status = "UNSAFE" if result.is_attack else "SAFE"
                print(f"  Result: {status} (confidence: {result.confidence:.4f})")
                if result.categories:
                    print(f"  Categories: {', '.join(result.categories)}")
                print(f"  Time: {result.execution_time:.2f}s")
                if result.error:
                    print(f"  Error: {result.error}")
            return results
        else:
            # Parallel mode
            return self._test_dataset_parallel(cases, is_attack=True)
    
    def _test_dataset_parallel(self, cases: List[AttackCase], is_attack: bool = True) -> List[LlamaGuardResult]:
        """并行测试数据集"""
        total = len(cases)
        results = [None] * total  # pre-allocate results list, maintain order
        completed_count = [0]  # use list to modify in closure
        
        def process_case(idx: int, case: AttackCase) -> tuple:
            """处理单个案例"""
            result = self.test_case(case)
            return idx, result
        
        self._safe_print(f"\n[PARALLEL] Starting {total} cases with concurrency={self.concurrency}")
        
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            # 提交所有任务
            future_to_idx = {
                executor.submit(process_case, i, case): i 
                for i, case in enumerate(cases)
            }
            
            # 收集结果
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
    
    def test_normal_dataset(self, cases: List[NormalCase]) -> List[LlamaGuardResult]:
        """测试正常数据集（支持并行）"""
        total = len(cases)
        
        # 转换为 AttackCase 格式
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
            # Serial mode
            results = []
            for i, case in enumerate(attack_cases, 1):
                print(f"\n[{i}/{total}] Testing normal case: {case.id}")
                result = self.test_case(case)
                results.append(result)
                
                status = "UNSAFE (FP)" if result.is_attack else "SAFE (TN)"
                print(f"  Result: {status} (confidence: {result.confidence:.4f})")
                print(f"  Time: {result.execution_time:.2f}s")
                if result.error:
                    print(f"  Error: {result.error}")
            return results
        else:
            # Parallel mode
            return self._test_dataset_parallel(attack_cases, is_attack=False)


# ============================================================================
# Data Loading
# ============================================================================

def load_attack_dataset(dataset_path: str, scenario_id: str) -> List[AttackCase]:
    """
    Load attack dataset (academic standard: supports true multi-turn dialogue)
    
    Multi-turn dialogue handling:
    - Preserve all turn prompts list (all_turns)
    - No longer merge into single string
    - Support turn-by-turn detection and conversation history accumulation
    """
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
        
        # Academic standard: preserve all turn prompts list
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

def summarize_results(results: List[LlamaGuardResult], cases: List[AttackCase] = None) -> Dict[str, Any]:
    """
    Summarize test results (academic standard: supports multi-turn dialogue statistics)
    
    New academic metrics:
    - avg_turns_to_detection: average turns needed for successful detection
    - per_turn_detection_rate: detection rate distribution by turn
    """
    total = len(results)
    if total == 0:
        return {"total_cases": 0, "attacks_detected": 0, "detection_rate": 0.0, "category_breakdown": {}, "average_confidence": 0.0, "average_execution_time": 0.0, "errors": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "multi_turn_stats": {}}
    
    attacks_detected = sum(1 for r in results if r.is_attack)
    errors = sum(1 for r in results if r.error)
    category_breakdown = {}
    for r in results:
        for cat in r.categories:
            category_breakdown[cat] = category_breakdown.get(cat, 0) + 1
    avg_confidence = sum(r.confidence for r in results) / total
    avg_time = sum(r.execution_time for r in results) / total
    tpr = attacks_detected / total if total > 0 else 0.0
    prompt_tokens = sum(r.prompt_tokens for r in results)
    completion_tokens = sum(r.completion_tokens for r in results)
    total_tokens = sum(r.total_tokens for r in results)
    
    # Academic standard: multi-turn dialogue statistics
    multi_turn_stats = {
        "single_turn": {"total": 0, "detected": 0, "detection_rate": 0.0},
        "multi_turn": {"total": 0, "detected": 0, "detection_rate": 0.0,
                       "avg_turns_to_detection": 0.0, "per_turn_distribution": {}}
    }
    
    # Statistics of turns needed for successful detection
    success_turns = []
    per_turn_detection_count = {}
    
    for r in results:
        if r.is_multi_turn:
            multi_turn_stats["multi_turn"]["total"] += 1
            if r.is_attack:
                multi_turn_stats["multi_turn"]["detected"] += 1
                if r.success_turn > 0:
                    success_turns.append(r.success_turn)
                    per_turn_detection_count[r.success_turn] = per_turn_detection_count.get(r.success_turn, 0) + 1
        else:
            multi_turn_stats["single_turn"]["total"] += 1
            if r.is_attack:
                multi_turn_stats["single_turn"]["detected"] += 1
    
    # Calculate detection rate
    for key in ["single_turn", "multi_turn"]:
        t = multi_turn_stats[key]["total"]
        d = multi_turn_stats[key]["detected"]
        multi_turn_stats[key]["detection_rate"] = d / t if t > 0 else 0.0
    
    # Academic metric: average successful detection turns
    if success_turns:
        multi_turn_stats["multi_turn"]["avg_turns_to_detection"] = sum(success_turns) / len(success_turns)
        multi_turn_stats["multi_turn"]["per_turn_distribution"] = per_turn_detection_count
    
    return {
        "total_cases": total, 
        "attacks_detected": attacks_detected, 
        "detection_rate": tpr, 
        "category_breakdown": category_breakdown, 
        "average_confidence": avg_confidence, 
        "average_execution_time": avg_time, 
        "errors": errors, 
        "error_rate": errors / total if total > 0 else 0.0, 
        "prompt_tokens": prompt_tokens, 
        "completion_tokens": completion_tokens, 
        "total_tokens": total_tokens, 
        "multi_turn_stats": multi_turn_stats
    }


def save_results(
    results: List[LlamaGuardResult],
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
        f"llama_guard3_results_{dataset_name}_{scenario_id}_{timestamp}.json"
    )
    
    # Import category information
    from defense.llama_guard.categories import LLAMA_GUARD_CATEGORIES
    
    results_data = {
        "metadata": {
            "framework": "LLaMA Guard 3 (Native)",
            "model": "meta-llama/Llama-Guard-3-8B",
            "dataset": dataset_name,
            "scenario_id": scenario_id,
            "timestamp": timestamp,
            "total_cases": len(results),
            "architecture": {
                "type": "Single LLM Classification",
                "base_model": "Llama-3.1-8B",
                "categories": 14,
                "category_list": list(LLAMA_GUARD_CATEGORIES.keys()),
            },
            "reference": {
                "paper": "https://arxiv.org/abs/2312.06674",
                "model": "https://huggingface.co/meta-llama/Llama-Guard-3-8B",
                "taxonomy": "MLCommons AI Safety"
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
# Major Category Statistics
# ============================================================================

def summarize_by_category(all_summaries: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Summarize by major category"""
    category_stats = {}
    
    for scenario_id, summary in all_summaries.items():
        category = get_scenario_category(scenario_id)
        category_info = MAJOR_CATEGORIES.get(category, {})
        
        if category not in category_stats:
            category_stats[category] = {
                "name_en": category_info.get("name_en", "Unknown"),
                "name_zh": category_info.get("name_zh", "未知"),
                "scenarios": [],
                "total_cases": 0,
                "attacks_detected": 0,
                "detection_rate": 0.0,
                "category_breakdown": {}
            }
        
        category_stats[category]["scenarios"].append(scenario_id)
        category_stats[category]["total_cases"] += summary.get("total_cases", 0)
        category_stats[category]["attacks_detected"] += summary.get("attacks_detected", 0)
        
        for cat, count in summary.get("category_breakdown", {}).items():
            category_stats[category]["category_breakdown"][cat] = \
                category_stats[category]["category_breakdown"].get(cat, 0) + count
    
    for cat_id, stats in category_stats.items():
        if stats["total_cases"] > 0:
            stats["detection_rate"] = stats["attacks_detected"] / stats["total_cases"]
    
    return category_stats


def print_category_summary(category_stats: Dict[str, Dict[str, Any]]):
    """Print major category summary"""
    print(f"\n{'='*80}")
    print("                    Statistics by Major Category")
    print(f"{'='*80}")
    print(f"{'Category':<35} {'Scenarios':>8} {'Cases':>8} {'Detected':>8} {'TPR':>10}")
    print("-" * 75)
    
    total_cases = 0
    total_detected = 0
    
    for cat_id, stats in sorted(category_stats.items()):
        cat_name = f"{stats['name_en']} ({stats['name_zh']})"
        tpr = stats["detection_rate"] * 100
        print(f"{cat_name:<35} {len(stats['scenarios']):>8} "
              f"{stats['total_cases']:>8} {stats['attacks_detected']:>8} {tpr:>9.1f}%")
        total_cases += stats["total_cases"]
        total_detected += stats["attacks_detected"]
    
    print("-" * 75)
    overall_tpr = total_detected / total_cases * 100 if total_cases > 0 else 0
    print(f"{'Total':<35} {len(category_stats):>8} {total_cases:>8} {total_detected:>8} {overall_tpr:>9.1f}%")
    print(f"{'='*80}")


# ============================================================================
# Evaluation Mode
# ============================================================================

def _process_single_scenario_llama_guard3(
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
    """
    Process single scenario test (for scenario-level parallelism)
    
    Returns:
        {
            "scenario_id": scenario_id,
            "attack_results": attack_results_dicts,
            "normal_results": normal_results_dicts,
            "error": None
        }
    """
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
        
        # ============== Test attack dataset (with cache) ==============
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
        
        # Filter cases that need testing
        cases_to_test = [c for c in attack_cases if c.id not in cached_case_ids]
        
        tester = None
        if cases_to_test:
            safe_print(f"[Scenario {scenario_id}] Testing {len(cases_to_test)} new attack cases...")
            
            # Case-level uses serial when scenario-level parallelism is enabled (avoid over-concurrency)
            case_concurrency = 1 if getattr(args, 'scenario_parallel', 1) > 1 else getattr(args, 'concurrency', 1)
            
            tester = LlamaGuard3Tester(
                mode=args.mode,
                model_path=args.model_path,
                api_url=args.api_url,
                api_key=args.api_key,
                threshold=args.threshold,
                device=args.device,
                llama_guard_logger=None,  # Do not use shared logger during scenario parallelism
                concurrency=case_concurrency,
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
        
        # Merge cached results and new results
        if attack_cached:
            cached_results = {r["case_id"]: r for r in attack_cached.get("results", [])}
        else:
            cached_results = {}
        
        for r in new_attack_results_dicts:
            cached_results[r["case_id"]] = r
        
        # Arrange results in original order
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
        
        # ============== Test normal dataset (with cache) ==============
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
                    tester = LlamaGuard3Tester(
                        mode=args.mode,
                        model_path=args.model_path,
                        api_url=args.api_url,
                        api_key=args.api_key,
                        threshold=args.threshold,
                        device=args.device,
                        llama_guard_logger=None,
                        concurrency=case_concurrency,
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
                
                # Cache results
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
        
        # Print scenario results
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
    logger: LlamaGuardLogger,
    output_dir: str
):
    """
    Run evaluation mode: test attack and normal datasets, calculate TPR/FPR and other metrics
    Supports caching for attack and normal datasets
    Supports scenario-level parallelism (controlled by --scenario-parallel parameter)
    """
    print(f"\n{'='*80}")
    print(f"                    EVALUATION MODE")
    print(f"                    Attack Type: {attack_type}")
    print(f"{'='*80}")
    
    # Configuration for caching
    config = {
        "mode": args.mode,
        "threshold": args.threshold,
        "model_path": args.model_path,
        "api_url": args.api_url
    }
    
    # Initialize cache
    normal_cache = NormalDatasetCache("llama_guard3")
    attack_cache = AttackDatasetCache("llama_guard3", attack_type)
    
    # Paths
    attack_dataset_path = os.path.join(_script_dir, "attack_datasets_synthesis", attack_type)
    normal_dataset_path = os.path.join(_script_dir, "normal_datasets")
    
    # Get scenario parallelism count
    scenario_parallel = getattr(args, 'scenario_parallel', 1)
    
    # Collect results
    all_attack_results = []
    all_normal_results = []
    attack_results_by_scenario = {}
    normal_results_by_scenario = {}
    
    if scenario_parallel <= 1:
        # ============== Serial processing of scenarios ==============
        for scenario_id in scenarios:
            print(f"\n{'='*60}")
            print(f"Scenario {scenario_id}")
            print(f"{'='*60}")
            
            result = _process_single_scenario_llama_guard3(
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
        # ============== Parallel processing of scenarios ==============
        print(f"\n[SCENARIO PARALLEL] Using {scenario_parallel} workers for {len(scenarios)} scenarios")
        print_lock = threading.Lock()
        
        with ThreadPoolExecutor(max_workers=scenario_parallel) as executor:
            # Submit all scenario tasks
            future_to_scenario = {
                executor.submit(
                    _process_single_scenario_llama_guard3,
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
            
            # Collect results
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
    
    # ============== Calculate overall metrics ==============
    if all_attack_results or all_normal_results:
        overall_metrics = compute_metrics(all_attack_results, all_normal_results)
        scenario_metrics = compute_metrics_by_scenario(
            attack_results_by_scenario, 
            normal_results_by_scenario
        )
        
        # Print report
        print_evaluation_report(overall_metrics, attack_type, "LLaMA Guard 3")
        
        # Token statistics summary
        total_prompt_tokens = sum(r.get('prompt_tokens', 0) for r in all_attack_results) + \
                              sum(r.get('prompt_tokens', 0) for r in all_normal_results)
        total_completion_tokens = sum(r.get('completion_tokens', 0) for r in all_attack_results) + \
                                 sum(r.get('completion_tokens', 0) for r in all_normal_results)
        total_tokens = sum(r.get('total_tokens', 0) for r in all_attack_results) + \
                       sum(r.get('total_tokens', 0) for r in all_normal_results)
        
        # Time consumption statistics
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
        
        # Print scenario details
        scenario_info_dict = {
            sid: {"name_en": SCENARIO_INFO.get(sid).name_en if SCENARIO_INFO.get(sid) else "Unknown"}
            for sid in scenarios
        }
        print_scenario_breakdown(scenario_metrics, scenario_info_dict)
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(
            output_dir,
            f"llama_guard3_evaluation_{attack_type}_{timestamp}.json"
        )
        save_evaluation_report(
            overall_metrics,
            scenario_metrics,
            all_attack_results,
            all_normal_results,
            report_file,
            metadata={
                "defense_method": "LLaMA Guard 3",
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
        description="LLaMA Guard 3 Native Framework Test Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Test single scenario (default uses configured OpenRouter API)
    python run_llama_guard3_test.py --dataset attack_datasets --scenario 00
    
    # Test synthetic attack dataset and compare with normal dataset (calculate TPR/FPR)
    python run_llama_guard3_test.py --attack-type authority_impersonation --all --eval
    
    # Use mock mode (for testing, does not call actual API)
    python run_llama_guard3_test.py --attack-type authority_impersonation --all --eval --mode mock
    
    # Clear normal dataset cache
    python run_llama_guard3_test.py --clear-cache
    
    # List available attack types
    python run_llama_guard3_test.py --list-attack-types
        """
    )
    
    # Dataset selection
    parser.add_argument(
        "--dataset",
        type=str,
        help="Dataset directory name (relative to sandbox directory, for legacy mode)"
    )
    parser.add_argument(
        "--attack-type",
        type=str,
        help="Attack type (e.g. authority_impersonation, direct_json_injection), multiple types separated by commas"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        help="Scenario ID (e.g. 00, 01, 02)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all scenarios"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Test by major category (e.g. credit_lending, insurance)"
    )
    
    # Evaluation mode
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Enable evaluation mode: test both attack and normal datasets, calculate TPR/FPR and other metrics"
    )
    
    # Cache management
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear cached results for normal dataset"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Do not use cache, force retesting of normal dataset"
    )
    
    # List options
    parser.add_argument(
        "--list-attack-types",
        action="store_true",
        help="List all available attack types"
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List all major categories"
    )
    
    # Model configuration
    parser.add_argument(
        "--mode",
        type=str,
        default="api",
        choices=["local", "local_path", "hf_mirror", "api", "mock"],
        help="Running mode: api=use configured API (default), local_path=local model path, local=HuggingFace model, hf_mirror=HF mirror, mock=mock mode"
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default=None,
        help="Model path (local mode, default: meta-llama/Llama-Guard-3-8B)"
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default=None,
        help="API URL (api mode, read from config file by default)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API key (api mode, read from config file by default)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        help="Device (local mode, default: cuda)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Confidence threshold (default: 0.5)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: sandbox/llama_guard3_results)"
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=None,
        help="Maximum number of test cases per scenario"
    )
    parser.add_argument(
        "--concurrency",
        "-c",
        type=int,
        default=20,
        help="Case-level concurrency (default: 20)"
    )
    parser.add_argument(
        "--scenario-parallel",
        type=int,
        default=20,
        help="Scenario-level parallelism (default: 1, i.e. serial scenario processing; set >1 to enable scenario parallelism)"
    )
    
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
        cache = NormalDatasetCache("llama_guard3")
        cache.clear()
        print("Cache cleared successfully.")
        return
    
    # Set output directory
    output_dir = args.output_dir or os.path.join(_script_dir, "llama_guard3_results")
    log_dir = os.path.join(output_dir, "logs")
    
    # Initialize logger
    llama_guard_logger = LlamaGuardLogger(log_dir, args.verbose)
    
    # ============== Evaluation Mode ==============
    if args.eval and args.attack_type:
        attack_types = [at.strip() for at in args.attack_type.split(",")]
        
        for attack_type in attack_types:
            # Get scenario list
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
            
            run_evaluation(attack_type, scenarios, args, llama_guard_logger, output_dir)
        
        llama_guard_logger.save_detailed_logs()
        print(f"\nLog file: {llama_guard_logger.log_file}")
        print(f"Detailed log: {llama_guard_logger.detail_file}")
        return
    
    # ============== Legacy Mode ==============
    if not args.dataset:
        print("Error: --dataset is required (or use --attack-type with --eval)")
        parser.print_help()
        sys.exit(1)
    
    # Set path
    dataset_path = os.path.join(_script_dir, args.dataset)
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset path not found: {dataset_path}")
        sys.exit(1)
    
    # Extract dataset name
    dataset_name = args.dataset.replace("/", "_").replace("\\", "_")
    
    # Get scenarios to test
    if args.category:
        scenarios = get_scenarios_by_category(args.category)
        available = get_available_scenarios(dataset_path)
        scenarios = [s for s in scenarios if s in available]
        if not scenarios:
            print(f"Error: No scenarios found for category {args.category}")
            sys.exit(1)
        print(f"Category {args.category}: Found {len(scenarios)} scenarios: {scenarios}")
    elif args.all:
        scenarios = get_available_scenarios(dataset_path)
        if not scenarios:
            print(f"Error: No scenarios found in {dataset_path}")
            sys.exit(1)
        print(f"Found {len(scenarios)} scenarios: {scenarios}")
    elif args.scenario:
        scenarios = [args.scenario]
    else:
        print("Error: Please specify --scenario, --all, or --category")
        parser.print_help()
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"LLaMA Guard 3 原生框架测试")
    print(f"{'='*80}")
    print(f"数据集: {args.dataset}")
    print(f"场景: {scenarios}")
    if args.category:
        cat_info = MAJOR_CATEGORIES.get(args.category, {})
        print(f"大类别: {cat_info.get('name_en', args.category)} ({cat_info.get('name_zh', '')})")
    print(f"运行模式: {args.mode}")
    if args.mode == "local":
        print(f"模型路径: {args.model_path or 'meta-llama/Llama-Guard-3-8B'}")
        print(f"设备: {args.device}")
    elif args.mode == "api":
        print(f"API 地址: {args.api_url or '(从配置文件读取)'}")
        print(f"模型: meta-llama/llama-guard-3-8b (OpenRouter)")
    print(f"置信度阈值: {args.threshold}")
    print(f"详细日志: {args.verbose}")
    print(f"场景并发: {args.scenario_parallel}")
    print(f"{'='*80}\n")
    
    all_results = []
    all_summaries = {}
    
    def process_traditional_scenario(scenario_id: str, print_lock: threading.Lock = None):
        def safe_print(msg: str):
            if print_lock:
                with print_lock:
                    print(msg)
            else:
                print(msg)
        
        category = get_scenario_category(scenario_id)
        category_info = MAJOR_CATEGORIES.get(category, {})
        scenario_info = SCENARIO_INFO.get(scenario_id)
        
        safe_print(f"\n{'='*60}")
        safe_print(f"场景 {scenario_id}: {scenario_info.name_en if scenario_info else 'Unknown'}")
        safe_print(f"大类别: {category_info.get('name_en', 'Unknown')} ({category_info.get('name_zh', '未知')})")
        safe_print(f"{'='*60}")
        
        try:
            cases = load_attack_dataset(dataset_path, scenario_id)
            if args.max_cases:
                cases = cases[:args.max_cases]
            safe_print(f"场景 {scenario_id}: 加载了 {len(cases)} 个测试案例")
            
            # 场景并发时，案例并发设为1
            case_concurrency = 1 if args.scenario_parallel > 1 else args.concurrency
            
            tester = LlamaGuard3Tester(
                mode=args.mode,
                model_path=args.model_path,
                api_url=args.api_url,
                api_key=args.api_key,
                threshold=args.threshold,
                device=args.device,
                llama_guard_logger=None,  # 并发时不使用共享 logger
                concurrency=case_concurrency,
            )
            
            results = tester.test_dataset(cases)
            summary = summarize_results(results)
            summary["major_category"] = category
            summary["major_category_zh"] = category_info.get("name_zh", "未知")
            
            safe_print(f"\n场景 {scenario_id} 结果:")
            safe_print(f"  - 总案例数: {summary['total_cases']}")
            safe_print(f"  - 检测到攻击: {summary['attacks_detected']}")
            safe_print(f"  - 检测率 (TPR): {summary['detection_rate']:.2%}")
            
            save_results(results, summary, output_dir, scenario_id, dataset_name)
            return scenario_id, results, summary
            
        except Exception as e:
            safe_print(f"Error testing scenario {scenario_id}: {e}")
            return scenario_id, [], None

    if args.scenario_parallel <= 1:
        for scenario_id in scenarios:
            sid, results, summary = process_traditional_scenario(scenario_id)
            if summary:
                all_results.extend(results)
                all_summaries[sid] = summary
    else:
        print_lock = threading.Lock()
        with ThreadPoolExecutor(max_workers=args.scenario_parallel) as executor:
            futures = {executor.submit(process_traditional_scenario, sid, print_lock): sid for sid in scenarios}
            for future in as_completed(futures):
                sid, results, summary = future.result()
                if summary:
                    all_results.extend(results)
                    all_summaries[sid] = summary
                print(f"[SCENARIO PARALLEL] Completed: {sid}")

    llama_guard_logger.save_detailed_logs()
    
    if len(scenarios) > 1:
        print(f"\n{'='*80}")
        print(f"总体汇总")
        print(f"{'='*80}")
        
        total_cases = sum(s['total_cases'] for s in all_summaries.values())
        total_detected = sum(s['attacks_detected'] for s in all_summaries.values())
        
        all_categories = {}
        for s in all_summaries.values():
            for cat, count in s.get('category_breakdown', {}).items():
                all_categories[cat] = all_categories.get(cat, 0) + count
        
        print(f"总测试案例: {total_cases}")
        print(f"总检测到攻击: {total_detected}")
        print(f"总体检测率: {total_detected/total_cases:.2%}" if total_cases > 0 else "N/A")
        
        # Token 统计汇总
        total_prompt_tokens = sum(s.get('prompt_tokens', 0) for s in all_summaries.values())
        total_completion_tokens = sum(s.get('completion_tokens', 0) for s in all_summaries.values())
        total_tokens = sum(s.get('total_tokens', 0) for s in all_summaries.values())
        print(f"\n【Token 统计】")
        print(f"  Prompt Tokens: {total_prompt_tokens:,}")
        print(f"  Completion Tokens: {total_completion_tokens:,}")
        print(f"  Total Tokens: {total_tokens:,}")
        if total_cases > 0:
            print(f"  平均每案例 Tokens: {total_tokens / total_cases:,.1f}")
        
        if all_categories:
            print(f"总体类别分布:")
            for cat, count in sorted(all_categories.items()):
                print(f"    {cat}: {count}")
        
        category_stats = summarize_by_category(all_summaries)
        print_category_summary(category_stats)
        
        print(f"\n【按场景统计】")
        print(f"{'场景ID':<8} {'场景名称':<35} {'大类别':<15} {'案例':>6} {'检测':>6} {'TPR':>8}")
        print("-" * 85)
        
        for sid, summary in sorted(all_summaries.items()):
            scenario_info = SCENARIO_INFO.get(sid)
            name = scenario_info.name_en[:33] if scenario_info else "Unknown"
            cat_zh = summary.get("major_category_zh", "未知")
            tpr = summary["detection_rate"] * 100
            print(f"{sid:<8} {name:<35} {cat_zh:<15} {summary['total_cases']:>6} "
                  f"{summary['attacks_detected']:>6} {tpr:>7.1f}%")
        
        print("-" * 85)
        
        overall_summary_file = os.path.join(
            output_dir,
            f"llama_guard3_overall_summary_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(overall_summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": {
                    "framework": "LLaMA Guard 3 (Native)",
                    "model": "meta-llama/Llama-Guard-3-8B",
                    "dataset": args.dataset,
                    "mode": args.mode,
                    "timestamp": datetime.now().isoformat()
                },
                "category_breakdown": category_stats,
                "scenario_summaries": all_summaries,
                "overall": {
                    "total_cases": total_cases,
                    "total_detected": total_detected,
                    "overall_detection_rate": total_detected/total_cases if total_cases > 0 else 0,
                    "category_breakdown": all_categories
                }
            }, f, indent=2, ensure_ascii=False)
        print(f"\n总体汇总保存到: {overall_summary_file}")
    
    print(f"\n日志文件: {llama_guard_logger.log_file}")
    print(f"详细日志: {llama_guard_logger.detail_file}")


if __name__ == "__main__":
    main()
