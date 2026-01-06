# -*- coding: utf-8 -*-
"""
FInVault Sandbox Attack Testing Framework

This framework focuses on attack testing in sandbox environments without Defense detection functionality.
For Defense detection, please use specialized scripts: run_agrail_test.py, run_nemo_guardrails_test.py, run_llama_guard3_test.py

Features:
1. Support for original attack dataset (attack_datasets/) and synthesized attack dataset (attack_datasets_synthesis/)
2. Support for classification statistics of attack success rates by major scenarios
3. Support for testing with specified attack types
4. Support for scenario-level parallel testing

Usage:
    # Test a single scenario (using original dataset)
    python run_attack_test.py --scenario 00
    
    # Test all scenarios
    python run_attack_test.py --all
    
    # Test using synthesis dataset
    python run_attack_test.py --scenario 00 --synthesis
    
    # Specify attack types (synthesis dataset only)
    python run_attack_test.py --scenario 00 --synthesis --attack-type authority_impersonation
    
    # Test all attack types
    python run_attack_test.py --scenario 00 --synthesis --attack-type all
    
    # Test by major category
    python run_attack_test.py --category credit_lending
    
    # Verbose output
    python run_attack_test.py --scenario 00 -v
"""

import sys
import os
import json
import argparse
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from importlib import import_module
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================================================
# Environment Variable Loading
# ============================================================================
from dotenv import load_dotenv

_script_dir = os.path.dirname(os.path.abspath(__file__))
_env_paths = [
    os.path.join(_script_dir, '.env'),
    os.path.join(_script_dir, 'config', '.env'),
]

for _env_path in _env_paths:
    if os.path.exists(_env_path):
        load_dotenv(_env_path, override=True)
        break

from config.paths import ProjectPaths, Paths
from config.scenario_categories import (
    MAJOR_CATEGORIES, SCENARIO_CATEGORY_MAPPING, SCENARIO_INFO, ATTACK_TYPES,
    get_scenario_category, get_scenarios_by_category, get_all_categories,
    get_all_attack_types, group_scenarios_by_category
)

# ============================================================================
# Constant Definitions
# ============================================================================

# Test modes
MODE_BASE = "base"
MODE_SAFE = "safe"


def normalize_vulnerability_id(vuln_id: str, scenario_id: str = None) -> str:
    """
    Normalize vulnerability ID to resolve inconsistent naming across different attack methods.
    
    Background:
    - Scenarios 21 and 24's authority_impersonation attacks use scenario-prefixed IDs (e.g., S21_V1, S24_V1)
    - Other 7 attack methods use simplified IDs (e.g., V1, V2, V3)
    - This causes the same case to be counted as 2 different vulnerabilities
    
    Normalization Rules:
    - Unify S21_V1, S21_V2, S21_V3 as V1, V2, V3
    - Unify S24_V1, S24_V2, S24_V3 as V1, V2, V3
    - Keep other vulnerability IDs unchanged
    """
    import re
    
    if not vuln_id:
        return vuln_id
    
    # Pattern: S{scenario_id}_V{vulnerability_id}, e.g., S21_V1, S24_V2
    pattern = r'^S(\d+)_V(\d+)$'
    match = re.match(pattern, vuln_id)
    
    if match:
        # Extract vulnerability number and return normalized format V{vulnerability_id}
        vuln_num = match.group(2)
        return f"V{vuln_num}"
    
    return vuln_id

# Default configuration - using OpenRouter model from agents_config.yaml
# Optional: qwen_max, claude_haiku, gpt5, gemini_flash, llama_guard3
DEFAULT_AGENT_MODEL = "qwen_max"
DEFAULT_SCENARIO_CONCURRENCY = 20
DEFAULT_MAX_TURNS = 10

# Dataset directories
ATTACK_DATASETS_DIR = os.path.join(_script_dir, "attack_datasets")
SYNTHESIS_DATASETS_DIR = os.path.join(_script_dir, "attack_datasets_synthesis")


# ============================================================================
# Data Class Definitions
# ============================================================================

@dataclass
class CaseResult:
    """单个案例的测试结果"""
    case_id: str
    case_type: str
    target_vulnerability: str = ""
    attack_type: str = ""
    total_turns: int = 0
    total_reward: float = 0.0
    attack_success: bool = False
    final_status: str = ""
    final_decision: str = ""
    vulnerabilities_triggered: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    turns: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    parse_failures: int = 0
    # Token Statistics
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    llm_calls: int = 0
    # Multi-turn dialogue info (Academic standard)
    is_multi_turn: bool = False
    follow_up_prompts: List[str] = field(default_factory=list)
    all_turns: List[str] = field(default_factory=list)  # Prompts for all turns
    success_turn: int = 0  # Turn number of successful attack (0=not successful)
    per_turn_results: List[Dict[str, Any]] = field(default_factory=list)  # Per-turn results


@dataclass
class ScenarioTestReport:
    """Test report for a single scenario"""
    timestamp: str
    scenario_id: str
    scenario_name: str
    major_category: str
    major_category_zh: str
    agent_type: str
    test_mode: str
    dataset_type: str  # "original" or "synthesis"
    attack_types_tested: List[str] = field(default_factory=list)
    # Attack statistics
    total_cases: int = 0
    successful_attacks: int = 0
    attack_success_rate: float = 0.0
    # Vulnerability-level statistics
    total_vulnerabilities: int = 0
    compromised_vulnerabilities: int = 0
    vulnerability_attack_rate: float = 0.0
    vulnerability_breakdown: Dict[str, Dict[str, int]] = field(default_factory=dict)
    # Statistics by attack type
    attack_type_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Multi-turn dialogue statistics
    multi_turn_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Detailed results
    case_results: List[CaseResult] = field(default_factory=list)
    duration: float = 0.0
    # Agent scores
    agent_avg_score: float = 0.0
    # Token Statistics
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_llm_calls: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "major_category": self.major_category,
            "major_category_zh": self.major_category_zh,
            "agent_type": self.agent_type,
            "test_mode": self.test_mode,
            "dataset_type": self.dataset_type,
            "attack_types_tested": self.attack_types_tested,
            "attack_summary": {
                "total_cases": self.total_cases,
                "successful_attacks": self.successful_attacks,
                "attack_success_rate": round(self.attack_success_rate, 4),
            },
            "vulnerability_summary": {
                "total_vulnerabilities": self.total_vulnerabilities,
                "compromised_vulnerabilities": self.compromised_vulnerabilities,
                "vulnerability_attack_rate": round(self.vulnerability_attack_rate, 4),
            },
            "vulnerability_breakdown": self.vulnerability_breakdown,
            "attack_type_breakdown": self.attack_type_breakdown,
            "multi_turn_stats": self.multi_turn_stats,
            "score_summary": {
                "agent_avg_score": round(self.agent_avg_score, 4),
            },
            "token_summary": {
                "total_prompt_tokens": self.total_prompt_tokens,
                "total_completion_tokens": self.total_completion_tokens,
                "total_tokens": self.total_tokens,
                "total_llm_calls": self.total_llm_calls,
                "avg_tokens_per_case": round(self.total_tokens / max(self.total_cases, 1), 2),
            },
            "duration": self.duration,
            "case_results": [asdict(r) for r in self.case_results]
        }


@dataclass
class CategoryTestReport:
    """Test report for major category"""
    category_id: str
    category_name_en: str
    category_name_zh: str
    scenarios_tested: List[str] = field(default_factory=list)
    total_cases: int = 0
    successful_attacks: int = 0
    attack_success_rate: float = 0.0
    scenario_reports: Dict[str, ScenarioTestReport] = field(default_factory=dict)
    # Token Statistics
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_llm_calls: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category_id": self.category_id,
            "category_name_en": self.category_name_en,
            "category_name_zh": self.category_name_zh,
            "scenarios_tested": self.scenarios_tested,
            "summary": {
                "total_cases": self.total_cases,
                "successful_attacks": self.successful_attacks,
                "attack_success_rate": round(self.attack_success_rate, 4),
            },
            "token_summary": {
                "total_prompt_tokens": self.total_prompt_tokens,
                "total_completion_tokens": self.total_completion_tokens,
                "total_tokens": self.total_tokens,
                "total_llm_calls": self.total_llm_calls,
            },
            "scenario_reports": {sid: r.to_dict() for sid, r in self.scenario_reports.items()}
        }


@dataclass
class OverallTestReport:
    """Overall test report"""
    timestamp: str
    agent_type: str
    test_mode: str
    dataset_type: str
    attack_types_tested: List[str] = field(default_factory=list)
    # Overall statistics
    total_scenarios: int = 0
    total_cases: int = 0
    successful_attacks: int = 0
    attack_success_rate: float = 0.0
    total_vulnerabilities: int = 0
    compromised_vulnerabilities: int = 0
    vulnerability_attack_rate: float = 0.0
    # Statistics by major category
    category_breakdown: Dict[str, CategoryTestReport] = field(default_factory=dict)
    # Statistics by attack type (across scenarios)
    attack_type_breakdown: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Scenario reports
    scenario_reports: Dict[str, ScenarioTestReport] = field(default_factory=dict)
    duration: float = 0.0
    # Token Statistics
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_llm_calls: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "agent_type": self.agent_type,
            "test_mode": self.test_mode,
            "dataset_type": self.dataset_type,
            "attack_types_tested": self.attack_types_tested,
            "overall_summary": {
                "total_scenarios": self.total_scenarios,
                "total_cases": self.total_cases,
                "successful_attacks": self.successful_attacks,
                "attack_success_rate": round(self.attack_success_rate, 4),
                "total_vulnerabilities": self.total_vulnerabilities,
                "compromised_vulnerabilities": self.compromised_vulnerabilities,
                "vulnerability_attack_rate": round(self.vulnerability_attack_rate, 4),
            },
            "token_summary": {
                "total_prompt_tokens": self.total_prompt_tokens,
                "total_completion_tokens": self.total_completion_tokens,
                "total_tokens": self.total_tokens,
                "total_llm_calls": self.total_llm_calls,
                "avg_tokens_per_case": round(self.total_tokens / max(self.total_cases, 1), 2),
                "avg_tokens_per_call": round(self.total_tokens / max(self.total_llm_calls, 1), 2),
            },
            "category_breakdown": {cid: c.to_dict() for cid, c in self.category_breakdown.items()},
            "attack_type_breakdown": self.attack_type_breakdown,
            "scenario_reports": {sid: r.to_dict() for sid, r in self.scenario_reports.items()},
            "duration": self.duration
        }


# ============================================================================
# 沙盒测试器
# ============================================================================

class SandboxAttackTester:
    """
    沙盒攻击测试器
    
    专注于沙盒环境中的攻击测试，支持：
    1. 原始攻击数据集
    2. 合成攻击数据集（按攻击类型分类）
    3. 按大场景分类统计
    """
    
    def __init__(
        self,
        agent_type: str = DEFAULT_AGENT_MODEL,
        test_mode: str = MODE_BASE,
        verbose: bool = False,
        trace: bool = False,
        scenario_concurrency: int = DEFAULT_SCENARIO_CONCURRENCY,
    ):
        self.agent_type = agent_type
        self.test_mode = test_mode
        self.verbose = verbose
        self.trace = trace
        self.scenario_concurrency = scenario_concurrency
        
        self.available_scenarios = self._discover_scenarios()
    
    def _discover_scenarios(self) -> List[str]:
        """Discover available scenarios"""
        scenarios = []
        for item in os.listdir(_script_dir):
            if item.startswith('sandbox_') and os.path.isdir(os.path.join(_script_dir, item)):
                scenario_id = item.split('_')[1]
                if os.path.exists(os.path.join(_script_dir, item, 'scenario.py')):
                    scenarios.append(scenario_id)
        return sorted(scenarios)
    
    def _load_scenario(self, scenario_id: str):
        """Load scenario module"""
        try:
            return import_module(f"sandbox_{scenario_id}.scenario")
        except ImportError as e:
            if self.verbose:
                print(f"Warning: Cannot load scenario {scenario_id}: {e}")
            return None
    
    def _load_prompt(self, scenario_id: str):
        """Load prompt module"""
        try:
            return import_module(f"prompts.prompt_{scenario_id}")
        except ImportError:
            return None
    
    def _get_system_prompt(self, scenario_id: str) -> str:
        """Get system prompt"""
        prompt_module = self._load_prompt(scenario_id)
        if not prompt_module:
            return ""
        
        if self.test_mode == MODE_SAFE:
            if hasattr(prompt_module, 'get_system_prompt_with_safety'):
                return prompt_module.get_system_prompt_with_safety()
        
        if hasattr(prompt_module, 'get_system_prompt'):
            return prompt_module.get_system_prompt()
        
        return ""
    
    def _create_agent(self, system_prompt: str):
        """Create LLM Agent"""
        try:
            from attack_testing.llm_agent import create_agent
            return create_agent(agent_type=self.agent_type, system_prompt=system_prompt)
        except Exception as e:
            raise RuntimeError(f"Cannot create Agent: {e}")
    
    def _load_attack_cases(
        self,
        scenario_id: str,
        use_synthesis: bool = False,
        attack_types: List[str] = None
    ) -> Tuple[List[Dict], List[str]]:
        """
        Load attack cases
        
        Args:
            scenario_id: Scenario ID
            use_synthesis: Whether to use synthesized dataset
            attack_types: Attack types to test (valid only for synthesized dataset)
            
        Returns:
            (List of attack cases, list of actually tested attack types)
            
        Multi-turn dialogue processing:
        - If the case has multi_turn=True and follow_up_prompts,
          combine attack_prompt and follow_up_prompts into combined_prompt
        """
        all_cases = []
        tested_attack_types = []
        
        def process_multi_turn(case: Dict) -> Dict:
            """Process multi-turn dialogue, keep prompts list for all turns (Academic standard)"""
            attack_prompt = case.get("attack_prompt", "")
            follow_up_prompts = case.get("follow_up_prompts", [])
            is_multi_turn = case.get("multi_turn", False)
            
            # Academic standard: Keep prompts list for all turns, no longer merging
            if is_multi_turn and follow_up_prompts:
                case["all_turns"] = [attack_prompt] + follow_up_prompts
            else:
                case["all_turns"] = [attack_prompt]
            
            return case
        
        if use_synthesis:
            # Load synthesis dataset
            available_types = get_all_attack_types() if attack_types is None or "all" in attack_types else attack_types
            
            for attack_type in available_types:
                attack_dir = os.path.join(SYNTHESIS_DATASETS_DIR, attack_type)
                attack_file = os.path.join(attack_dir, f"scenario_{scenario_id}_attacks.json")
                
                if os.path.exists(attack_file):
                    try:
                        with open(attack_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        cases = data.get("attacks", data.get("scenarios", data.get("attack_cases", [])))
                        
                        # Mark attack type and process multi-turn dialogue
                        for case in cases:
                            case["synthesis_attack_type"] = attack_type
                            if "attack_input" in case and "attack_prompt" not in case:
                                case["attack_prompt"] = case["attack_input"]
                            process_multi_turn(case)
                        
                        all_cases.extend(cases)
                        tested_attack_types.append(attack_type)
                        
                        if self.verbose:
                            multi_turn_count = sum(1 for c in cases if c.get("multi_turn", False))
                            print(f"  Loaded {attack_type}: {len(cases)} cases (Multi-turn: {multi_turn_count})")
                    except Exception as e:
                        if self.verbose:
                            print(f"  Warning: Failed to load {attack_type}: {e}")
        else:
            # Load original dataset
            attack_file = os.path.join(ATTACK_DATASETS_DIR, f"scenario_{scenario_id}_attacks.json")
            
            if os.path.exists(attack_file):
                with open(attack_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                cases = data.get("attacks", data.get("scenarios", data.get("attack_cases", [])))
                
                for case in cases:
                    if "attack_input" in case and "attack_prompt" not in case:
                        case["attack_prompt"] = case["attack_input"]
                    process_multi_turn(case)
                
                all_cases.extend(cases)
                tested_attack_types.append("original")
        
        return all_cases, tested_attack_types
    
    def run_scenario(
        self,
        scenario_id: str,
        num_cases: int = 0,
        max_turns: int = DEFAULT_MAX_TURNS,
        use_synthesis: bool = False,
        attack_types: List[str] = None
    ) -> ScenarioTestReport:
        """
        Run attack test for a single scenario
        
        Args:
            scenario_id: Scenario ID
            num_cases: Number of test cases, 0=all
            max_turns: Maximum interaction turns
            use_synthesis: Whether to use synthesized dataset
            attack_types: Attack types to test
        """
        start_time = time.time()
        
        # Get scenario info
        scenario_info = SCENARIO_INFO.get(scenario_id)
        major_category = get_scenario_category(scenario_id)
        category_info = MAJOR_CATEGORIES.get(major_category, {})
        
        # Load scenario
        scenario = self._load_scenario(scenario_id)
        if not scenario:
            return ScenarioTestReport(
                timestamp=datetime.now().isoformat(),
                scenario_id=scenario_id,
                scenario_name="Unknown",
                major_category=major_category,
                major_category_zh=category_info.get("name_zh", "Unknown"),
                agent_type=self.agent_type,
                test_mode=self.test_mode,
                dataset_type="synthesis" if use_synthesis else "original"
            )
        
        meta = scenario.Scenario.get_meta()
        system_prompt = self._get_system_prompt(scenario_id)
        agent = self._create_agent(system_prompt)
        
        # Create environment
        try:
            env = scenario.create_environment()
        except Exception as e:
            print(f"Failed to create environment: {e}")
            return ScenarioTestReport(
                timestamp=datetime.now().isoformat(),
                scenario_id=scenario_id,
                scenario_name=meta.scenario_name,
                major_category=major_category,
                major_category_zh=category_info.get("name_zh", "Unknown"),
                agent_type=self.agent_type,
                test_mode=self.test_mode,
                dataset_type="synthesis" if use_synthesis else "original"
            )
        
        # Load attack cases
        attack_cases, tested_attack_types = self._load_attack_cases(
            scenario_id, use_synthesis, attack_types
        )
        
        # Limit number of cases
        if num_cases > 0:
            attack_cases = attack_cases[:num_cases]
        
        # Print scenario info
        dataset_type_str = "Synthesis" if use_synthesis else "Original"
        print(f"\n{'='*70}")
        print(f"Scenario {scenario_id}: {meta.scenario_name}")
        print(f"Category: {category_info.get('name_en', 'Unknown')} ({category_info.get('name_zh', 'Unknown')})")
        print(f"{'='*70}")
        print(f"  Dataset: {dataset_type_str} | Attack Cases: {len(attack_cases)}")
        if use_synthesis:
            print(f"  Attack Types: {', '.join(tested_attack_types)}")
        print(f"  Agent: {self.agent_type} | Mode: {self.test_mode} | Max Turns: {max_turns}")
        print(f"{'='*70}")
        
        # Execute test
        case_results = []
        vulnerability_breakdown = {}
        attack_type_breakdown = {}
        multi_turn_stats = {"single_turn": {"total": 0, "success": 0}, "multi_turn": {"total": 0, "success": 0}}
        
        attack_success_count = 0
        test_start_time = time.time()
        
        for i, case in enumerate(attack_cases):
            case_id = case.get("id", case.get("case_id", f"attack_{i}"))
            # Vulnerability field might be in multiple locations
            vulnerability_raw = case.get("vulnerability") or case.get("target_vulnerability") or \
                           case.get("context", {}).get("target_vulnerability") or "unknown"
            # Normalize vulnerability ID
            vulnerability = normalize_vulnerability_id(vulnerability_raw, scenario_id)
            attack_type = case.get("synthesis_attack_type", case.get("attack_type", "unknown"))
            is_multi_turn = case.get("multi_turn", False)
            
            # Update vulnerability stats
            if vulnerability not in vulnerability_breakdown:
                vulnerability_breakdown[vulnerability] = {"total": 0, "triggered": 0}
            vulnerability_breakdown[vulnerability]["total"] += 1
            
            # Update attack type stats
            if attack_type not in attack_type_breakdown:
                attack_type_breakdown[attack_type] = {"total": 0, "success": 0}
            attack_type_breakdown[attack_type]["total"] += 1
            
            # Update multi-turn stats
            turn_key = "multi_turn" if is_multi_turn else "single_turn"
            multi_turn_stats[turn_key]["total"] += 1
            
            # Run test
            result = self._run_single_case(env, agent, case, max_turns)
            
            if result.attack_success:
                vulnerability_breakdown[vulnerability]["triggered"] += 1
                attack_type_breakdown[attack_type]["success"] += 1
                multi_turn_stats[turn_key]["success"] += 1
                attack_success_count += 1
            
            case_results.append(result)
            
            # Progress log
            elapsed = time.time() - test_start_time
            remaining = len(attack_cases) - (i + 1)
            avg_time = elapsed / (i + 1)
            eta = avg_time * remaining
            current_asr = attack_success_count / (i + 1) * 100
            
            status_char = "✗" if result.attack_success else "✓"
            multi_turn_flag = "[M]" if is_multi_turn else "[S]"
            print(f"  [{i+1}/{len(attack_cases)}] ASR: {current_asr:.1f}% | "
                  f"Turns: {result.total_turns} | Elapsed: {elapsed:.1f}s | ETA: {eta:.1f}s | {multi_turn_flag} {status_char} {case_id}")
            
            if self.verbose:
                print(f"    Vuln: {vulnerability} | Attack Type: {attack_type} | Multi-turn: {is_multi_turn}")
                print(f"    Turns: {result.total_turns} | Score: {result.total_reward:.2f}")
                if result.vulnerabilities_triggered:
                    print(f"    Triggered Vulns: {', '.join(result.vulnerabilities_triggered)}")
        
        # Calculate statistics
        total_cases = len(case_results)
        successful_attacks = sum(1 for r in case_results if r.attack_success)
        total_vulns = len(vulnerability_breakdown)
        compromised_vulns = sum(1 for v in vulnerability_breakdown.values() if v["triggered"] > 0)
        
        # Calculate attack type success rates
        for attack_type, stats in attack_type_breakdown.items():
            stats["success_rate"] = stats["success"] / max(stats["total"], 1)
        
        # Calculate multi-turn statistics success rates
        for key in multi_turn_stats:
            t = multi_turn_stats[key]["total"]
            s = multi_turn_stats[key]["success"]
            multi_turn_stats[key]["success_rate"] = s / t if t > 0 else 0.0
        
        # Calculate Agent average score
        avg_scores = [r.total_reward / max(r.total_turns, 1) for r in case_results]
        agent_avg_score = sum(avg_scores) / max(len(avg_scores), 1)
        
        # Summarize token statistics
        total_prompt_tokens = sum(r.prompt_tokens for r in case_results)
        total_completion_tokens = sum(r.completion_tokens for r in case_results)
        total_tokens = sum(r.total_tokens for r in case_results)
        total_llm_calls = sum(r.llm_calls for r in case_results)
        
        # Calculate average turns
        avg_turns = sum(r.total_turns for r in case_results) / max(len(case_results), 1)
        
        report = ScenarioTestReport(
            timestamp=datetime.now().isoformat(),
            scenario_id=scenario_id,
            scenario_name=meta.scenario_name,
            major_category=major_category,
            major_category_zh=category_info.get("name_zh", "Unknown"),
            agent_type=self.agent_type,
            test_mode=self.test_mode,
            dataset_type="synthesis" if use_synthesis else "original",
            attack_types_tested=tested_attack_types,
            total_cases=total_cases,
            successful_attacks=successful_attacks,
            attack_success_rate=successful_attacks / max(total_cases, 1),
            total_vulnerabilities=total_vulns,
            compromised_vulnerabilities=compromised_vulns,
            vulnerability_attack_rate=compromised_vulns / max(total_vulns, 1),
            vulnerability_breakdown=vulnerability_breakdown,
            attack_type_breakdown=attack_type_breakdown,
            multi_turn_stats=multi_turn_stats,
            case_results=case_results,
            duration=time.time() - start_time,
            agent_avg_score=agent_avg_score,
            total_prompt_tokens=total_prompt_tokens,
            total_completion_tokens=total_completion_tokens,
            total_tokens=total_tokens,
            total_llm_calls=total_llm_calls
        )
        
        # Print scenario results
        print(f"\n  [Scenario Completed] Total: {total_cases} | Success: {successful_attacks} | "
              f"ASR: {report.attack_success_rate*100:.1f}% | Avg Turns: {avg_turns:.1f} | Duration: {report.duration:.1f}s")
        print(f"  [Token Stats] Prompt: {total_prompt_tokens} | Completion: {total_completion_tokens} | "
              f"Total: {total_tokens} | Calls: {total_llm_calls}")
        # Print multi-turn statistics
        if multi_turn_stats["multi_turn"]["total"] > 0:
            st = multi_turn_stats["single_turn"]
            mt = multi_turn_stats["multi_turn"]
            print(f"  [Multi-turn Stats] Single-turn: {st['success']}/{st['total']} ({st['success_rate']*100:.1f}%) | "
                  f"Multi-turn: {mt['success']}/{mt['total']} ({mt['success_rate']*100:.1f}%)")
        
        return report
    
    def _run_single_case(
        self, 
        env, 
        agent, 
        case: Dict[str, Any],
        max_turns: int
    ) -> CaseResult:
        """
        Run a single attack case - support for real multi-turn dialogue (Academic standard)
        
        Multi-turn dialogue processing:
        - Send prompts turn by turn, maintain dialogue history
        - Interact in each turn, record results per turn
        - Mark as success if attack succeeds in any turn
        - Record turn number required for success (for academic evaluation)
        """
        case_id = case.get("id", case.get("case_id", "unknown"))
        vulnerability = case.get("vulnerability") or case.get("target_vulnerability") or \
                       case.get("context", {}).get("target_vulnerability") or ""
        
        attack_prompt = case.get("attack_prompt", "")
        follow_up_prompts = case.get("follow_up_prompts", [])
        is_multi_turn = case.get("multi_turn", False)
        all_turns = case.get("all_turns", [attack_prompt])
        
        result = CaseResult(
            case_id=case_id,
            case_type="attack",
            target_vulnerability=vulnerability,
            attack_type=case.get("synthesis_attack_type", case.get("attack_type", "")),
            is_multi_turn=is_multi_turn,
            follow_up_prompts=follow_up_prompts,
            all_turns=all_turns
        )
        
        # Reset environment
        try:
            obs, info = env.reset(options={"case_id": case_id, "case_data": case})
        except Exception as e:
            result.error = str(e)
            return result
        
        if hasattr(agent, 'reset'):
            agent.reset()
        
        # Interaction loop - support for real multi-turn dialogue
        turns = []
        total_reward = 0
        step_info = {}
        terminated = False
        truncated = False
        per_turn_results = []
        
        # Maintain dialogue history
        conversation_history = []
        
        for turn_idx, turn_prompt in enumerate(all_turns):
            if terminated or truncated:
                break
            
            # Build full context with history
            if conversation_history:
                context_with_history = "\n\n".join([
                    f"[Turn {i+1}]: {msg}" 
                    for i, msg in enumerate(conversation_history)
                ]) + f"\n\n[Turn {turn_idx+1}]: {turn_prompt}"
            else:
                context_with_history = turn_prompt
            
            # Update attack prompt in environment for current turn's context
            case_for_turn = case.copy()
            case_for_turn["attack_prompt"] = context_with_history
            
            # If not the first turn, need to reset environment state
            if turn_idx > 0:
                try:
                    # Update environment's current prompt
                    if hasattr(env, 'state') and env.state:
                        env.state.current_attack_prompt = context_with_history
                    if hasattr(env, 'current_case'):
                        env.current_case = case_for_turn
                except Exception:
                    pass
            
            # Within each multi-turn turn, there might be multiple interaction rounds
            turn_interactions = 0
            turn_reward = 0
            turn_vulnerabilities = []
            
            for interaction in range(max_turns):
                try:
                    obs_str = json.dumps(obs, ensure_ascii=False) if isinstance(obs, dict) else str(obs)
                    action = agent.generate_response(obs_str)
                except Exception as e:
                    action = json.dumps({"tool": "escalate_to_human", "args": {"reason": str(e)}})
                
                try:
                    if isinstance(action, dict):
                        action_str = json.dumps(action, ensure_ascii=False)
                    else:
                        action_str = str(action)
                    
                    new_obs, reward, terminated, truncated, step_info = env.step(action_str)
                    turn_reward += reward
                    total_reward += reward
                    turn_interactions += 1
                    
                    triggered = step_info.get("triggered_vulnerabilities", [])
                    turn_vulnerabilities.extend(triggered)
                    
                    turns.append({
                        "multi_turn": turn_idx + 1,
                        "interaction": interaction + 1,
                        "action": action_str[:500],
                        "reward": reward,
                        "vulnerabilities": triggered
                    })
                    obs = new_obs
                    
                except Exception as e:
                    result.error = str(e)
                    break
                
                if terminated or truncated:
                    break
            
            # Record current turn results
            turn_result = {
                "turn": turn_idx + 1,
                "prompt": turn_prompt[:200] + "..." if len(turn_prompt) > 200 else turn_prompt,
                "interactions": turn_interactions,
                "reward": turn_reward,
                "vulnerabilities_triggered": turn_vulnerabilities
            }
            per_turn_results.append(turn_result)
            
            # Check if attack succeeded in this turn
            if turn_vulnerabilities:
                result.success_turn = turn_idx + 1
            
            # Update dialogue history
            conversation_history.append(turn_prompt)
        
        # Get final evaluation
        if "final_evaluation" not in step_info:
            try:
                if hasattr(env, '_generate_final_evaluation'):
                    step_info["final_evaluation"] = env._generate_final_evaluation()
                else:
                    step_info["final_evaluation"] = {
                        "attack_success": len(env.triggered_vulnerabilities) > 0 if hasattr(env, 'triggered_vulnerabilities') else False,
                        "final_status": "TIMEOUT_NO_DECISION" if not terminated else "COMPLETED",
                        "actual_decision": "",
                        "vulnerabilities_triggered": env.triggered_vulnerabilities if hasattr(env, 'triggered_vulnerabilities') else [],
                        "violations": env.state.violations if hasattr(env, 'state') and env.state else []
                    }
            except Exception as e:
                step_info["final_evaluation"] = {
                    "attack_success": False,
                    "final_status": "ERROR",
                    "actual_decision": "",
                    "vulnerabilities_triggered": [],
                    "violations": [],
                    "error": str(e)
                }
        
        final_eval = step_info.get("final_evaluation", {})
        result.attack_success = final_eval.get("attack_success", False)
        result.final_status = final_eval.get("final_status", "TIMEOUT_NO_DECISION")
        result.final_decision = final_eval.get("actual_decision", "")
        result.vulnerabilities_triggered = final_eval.get("vulnerabilities_triggered", [])
        result.violations = final_eval.get("violations", [])
        
        result.total_turns = len(turns)
        result.total_reward = total_reward
        result.turns = turns
        result.per_turn_results = per_turn_results
        
        if hasattr(agent, 'get_parse_failure_count'):
            result.parse_failures = agent.get_parse_failure_count()
        
        # Get token usage
        if hasattr(agent, 'get_token_usage'):
            token_usage = agent.get_token_usage()
            result.prompt_tokens = token_usage.get("prompt_tokens", 0)
            result.completion_tokens = token_usage.get("completion_tokens", 0)
            result.total_tokens = token_usage.get("total_tokens", 0)
        if hasattr(agent, 'get_call_count'):
            result.llm_calls = agent.get_call_count()
        
        return result
    
    def run_category(
        self,
        category_id: str,
        num_cases: int = 0,
        max_turns: int = DEFAULT_MAX_TURNS,
        use_synthesis: bool = False,
        attack_types: List[str] = None
    ) -> CategoryTestReport:
        """
        Run tests for all scenarios under a major category
        
        Args:
            category_id: Major category ID
            num_cases: Number of cases to test per scenario
            max_turns: Maximum interaction turns
            use_synthesis: Whether to use synthesized dataset
            attack_types: Attack types to test
        """
        category_info = MAJOR_CATEGORIES.get(category_id)
        if not category_info:
            raise ValueError(f"Unknown major category: {category_id}")
        
        scenarios = get_scenarios_by_category(category_id)
        
        print(f"\n{'='*80}")
        print(f"Category Test: {category_info['name_en']} ({category_info['name_zh']})")
        print(f"{'='*80}")
        print(f"Scenarios: {len(scenarios)}")
        print(f"Scenario List: {', '.join(scenarios)}")
        print(f"{'='*80}")
        
        report = CategoryTestReport(
            category_id=category_id,
            category_name_en=category_info['name_en'],
            category_name_zh=category_info['name_zh'],
            scenarios_tested=scenarios
        )
        
        for scenario_id in scenarios:
            if scenario_id not in self.available_scenarios:
                print(f"\nWarning: Scenario {scenario_id} is not available, skipping")
                continue
            
            scenario_report = self.run_scenario(
                scenario_id,
                num_cases=num_cases,
                max_turns=max_turns,
                use_synthesis=use_synthesis,
                attack_types=attack_types
            )
            
            report.scenario_reports[scenario_id] = scenario_report
            report.total_cases += scenario_report.total_cases
            report.successful_attacks += scenario_report.successful_attacks
            
            # Summarize token statistics
            report.total_prompt_tokens += scenario_report.total_prompt_tokens
            report.total_completion_tokens += scenario_report.total_completion_tokens
            report.total_tokens += scenario_report.total_tokens
            report.total_llm_calls += scenario_report.total_llm_calls
        
        report.attack_success_rate = report.successful_attacks / max(report.total_cases, 1)
        
        return report
    
    def run_all_scenarios(
        self,
        num_cases: int = 0,
        max_turns: int = DEFAULT_MAX_TURNS,
        use_synthesis: bool = False,
        attack_types: List[str] = None,
        parallel: bool = True
    ) -> OverallTestReport:
        """
        Run tests for all available scenarios
        
        Args:
            num_cases: Number of cases to test per scenario
            max_turns: Maximum interaction turns
            use_synthesis: Whether to use synthesized dataset
            attack_types: Attack types to test
            parallel: Whether to run tests in parallel
        """
        start_time = time.time()
        
        report = OverallTestReport(
            timestamp=datetime.now().isoformat(),
            agent_type=self.agent_type,
            test_mode=self.test_mode,
            dataset_type="synthesis" if use_synthesis else "original",
            attack_types_tested=attack_types or (get_all_attack_types() if use_synthesis else ["original"])
        )
        
        print(f"\n{'='*80}")
        print(f"Full Scenario Test")
        print(f"{'='*80}")
        print(f"Scenarios: {len(self.available_scenarios)}")
        print(f"Dataset: {'Synthesis' if use_synthesis else 'Original'}")
        if use_synthesis:
            print(f"Attack Types: {', '.join(report.attack_types_tested)}")
        print(f"Parallel Mode: {'Yes' if parallel else 'No'}")
        print(f"{'='*80}")
        
        if parallel:
            # Parallel testing
            scenario_reports = self._run_scenarios_parallel(
                self.available_scenarios,
                num_cases, max_turns, use_synthesis, attack_types
            )
        else:
            # Serial testing
            scenario_reports = {}
            for scenario_id in self.available_scenarios:
                scenario_report = self.run_scenario(
                    scenario_id,
                    num_cases=num_cases,
                    max_turns=max_turns,
                    use_synthesis=use_synthesis,
                    attack_types=attack_types
                )
                scenario_reports[scenario_id] = scenario_report
        
        report.scenario_reports = scenario_reports
        report.total_scenarios = len(scenario_reports)
        
        # Summarize overall statistics
        for sid, sr in scenario_reports.items():
            report.total_cases += sr.total_cases
            report.successful_attacks += sr.successful_attacks
            report.total_vulnerabilities += sr.total_vulnerabilities
            report.compromised_vulnerabilities += sr.compromised_vulnerabilities
            
            # Summarize token statistics
            report.total_prompt_tokens += sr.total_prompt_tokens
            report.total_completion_tokens += sr.total_completion_tokens
            report.total_tokens += sr.total_tokens
            report.total_llm_calls += sr.total_llm_calls
            
            # Summarize attack type statistics
            for attack_type, stats in sr.attack_type_breakdown.items():
                if attack_type not in report.attack_type_breakdown:
                    report.attack_type_breakdown[attack_type] = {"total": 0, "success": 0}
                report.attack_type_breakdown[attack_type]["total"] += stats["total"]
                report.attack_type_breakdown[attack_type]["success"] += stats["success"]
        
        # Calculate attack type success rates
        for attack_type, stats in report.attack_type_breakdown.items():
            stats["success_rate"] = stats["success"] / max(stats["total"], 1)
        
        report.attack_success_rate = report.successful_attacks / max(report.total_cases, 1)
        report.vulnerability_attack_rate = report.compromised_vulnerabilities / max(report.total_vulnerabilities, 1)
        
        # Summarize by major category
        for category_id in get_all_categories():
            category_info = MAJOR_CATEGORIES.get(category_id, {})
            category_report = CategoryTestReport(
                category_id=category_id,
                category_name_en=category_info.get("name_en", "Unknown"),
                category_name_zh=category_info.get("name_zh", "Unknown")
            )
            
            for sid, sr in scenario_reports.items():
                if sr.major_category == category_id:
                    category_report.scenarios_tested.append(sid)
                    category_report.scenario_reports[sid] = sr
                    category_report.total_cases += sr.total_cases
                    category_report.successful_attacks += sr.successful_attacks
                    
                    # Summarize token statistics
                    category_report.total_prompt_tokens += sr.total_prompt_tokens
                    category_report.total_completion_tokens += sr.total_completion_tokens
                    category_report.total_tokens += sr.total_tokens
                    category_report.total_llm_calls += sr.total_llm_calls
            
            if category_report.scenarios_tested:
                category_report.attack_success_rate = category_report.successful_attacks / max(category_report.total_cases, 1)
                report.category_breakdown[category_id] = category_report
        
        report.duration = time.time() - start_time
        
        return report
    
    def _run_scenarios_parallel(
        self,
        scenario_ids: List[str],
        num_cases: int,
        max_turns: int,
        use_synthesis: bool,
        attack_types: List[str]
    ) -> Dict[str, ScenarioTestReport]:
        """Run multiple scenarios in parallel"""
        all_reports = {}
        
        # Pre-load scenario modules
        if self.verbose:
            print(f"  Pre-loading scenario modules...")
        for sid in scenario_ids:
            try:
                self._load_scenario(sid)
                self._load_prompt(sid)
            except Exception:
                pass
        
        def run_single(scenario_id: str) -> Tuple[str, ScenarioTestReport]:
            try:
                local_tester = SandboxAttackTester(
                    agent_type=self.agent_type,
                    test_mode=self.test_mode,
                    verbose=False,
                    trace=self.trace,
                    scenario_concurrency=1
                )
                
                report = local_tester.run_scenario(
                    scenario_id,
                    num_cases=num_cases,
                    max_turns=max_turns,
                    use_synthesis=use_synthesis,
                    attack_types=attack_types
                )
                
                return scenario_id, report
            except Exception as e:
                return scenario_id, ScenarioTestReport(
                    timestamp=datetime.now().isoformat(),
                    scenario_id=scenario_id,
                    scenario_name="Error",
                    major_category="unknown",
                    major_category_zh="Unknown",
                    agent_type=self.agent_type,
                    test_mode=self.test_mode,
                    dataset_type="synthesis" if use_synthesis else "original"
                )
        
        with ThreadPoolExecutor(max_workers=self.scenario_concurrency) as executor:
            futures = {executor.submit(run_single, sid): sid for sid in scenario_ids}
            
            for future in as_completed(futures):
                sid, report = future.result()
                all_reports[sid] = report
        
        return all_reports
    
    def print_report(self, report: OverallTestReport):
        """Print overall test report"""
        print(f"\n{'='*80}")
        print("                    Sandbox Attack Test Report")
        print(f"{'='*80}")
        print(f"Test Time: {report.timestamp}")
        print(f"Agent: {report.agent_type} | Mode: {report.test_mode}")
        print(f"Dataset: {report.dataset_type}")
        if report.attack_types_tested:
            print(f"Attack Types: {', '.join(report.attack_types_tested)}")
        print(f"Duration: {report.duration:.2f}s")
        
        print(f"\n[Overall Statistics]")
        print(f"  Scenarios: {report.total_scenarios}")
        print(f"  Attack Cases: {report.total_cases}")
        print(f"  Successful Attacks: {report.successful_attacks} ({report.attack_success_rate*100:.1f}%)")
        print(f"  Total Vulnerabilities: {report.total_vulnerabilities}")
        print(f"  Compromised: {report.compromised_vulnerabilities} ({report.vulnerability_attack_rate*100:.1f}%)")
        
        print(f"\n[Token Statistics]")
        print(f"  Prompt Tokens: {report.total_prompt_tokens:,}")
        print(f"  Completion Tokens: {report.total_completion_tokens:,}")
        print(f"  Total Tokens: {report.total_tokens:,}")
        print(f"  LLM Calls: {report.total_llm_calls:,}")
        if report.total_cases > 0:
            print(f"  Avg Tokens per Case: {report.total_tokens / report.total_cases:,.1f}")
        if report.total_llm_calls > 0:
            print(f"  Avg Tokens per Call: {report.total_tokens / report.total_llm_calls:,.1f}")
        
        # Statistics by major category
        if report.category_breakdown:
            print(f"\n[Statistics by Major Category]")
            print(f"{'Category':<30} {'Scenarios':>10} {'Cases':>8} {'Success':>8} {'ASR':>10}")
            print("-" * 70)
            
            for cat_id, cat_report in sorted(report.category_breakdown.items()):
                cat_name = f"{cat_report.category_name_en}"
                asr = cat_report.attack_success_rate * 100
                print(f"{cat_name:<30} {len(cat_report.scenarios_tested):>10} "
                      f"{cat_report.total_cases:>8} {cat_report.successful_attacks:>8} {asr:>9.1f}%")
            
            print("-" * 70)
        
        # Statistics by attack type
        if report.attack_type_breakdown:
            print(f"\n[Statistics by Attack Type]")
            print(f"{'Attack Type':<30} {'Cases':>10} {'Success':>10} {'ASR':>12}")
            print("-" * 65)
            
            for attack_type, stats in sorted(report.attack_type_breakdown.items()):
                attack_info = ATTACK_TYPES.get(attack_type, {})
                attack_name = attack_info.get("name_en", attack_type)
                asr = stats["success_rate"] * 100
                print(f"{attack_name:<30} {stats['total']:>10} {stats['success']:>10} {asr:>11.1f}%")
            
            print("-" * 65)
        
        # Statistics by scenario
        print(f"\n[Statistics by Scenario]")
        print(f"{'ID':<8} {'Scenario Name':<30} {'Category':<20} {'Cases':>8} {'Success':>8} {'ASR':>10}")
        print("-" * 88)
        
        for sid, sr in sorted(report.scenario_reports.items()):
            asr = sr.attack_success_rate * 100
            print(f"{sid:<8} {sr.scenario_name[:28]:<30} {sr.major_category:<20} "
                  f"{sr.total_cases:>8} {sr.successful_attacks:>8} {asr:>9.1f}%")
        
        print("-" * 88)
        print(f"\n{'='*80}")


# ============================================================================
# Main Entry
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='FInVault Sandbox Attack Testing Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Test a single scenario
    python run_attack_test.py --scenario 00
    
    # Test all scenarios
    python run_attack_test.py --all
    
    # Use synthesis dataset
    python run_attack_test.py --scenario 00 --synthesis
    
    # Specify attack type
    python run_attack_test.py --scenario 00 --synthesis --attack-type authority_impersonation
    
    # Test all attack types
    python run_attack_test.py --scenario 00 --synthesis --attack-type all
    
    # Test by major category
    python run_attack_test.py --category credit_lending
    
    # List all major categories
    python run_attack_test.py --list-categories
    
    # List all attack types
    python run_attack_test.py --list-attack-types
        """
    )
    
    # Scenario selection
    parser.add_argument('--scenario', '-s', type=str, help='Scenario ID')
    parser.add_argument('--all', '-a', action='store_true', help='Test all scenarios')
    parser.add_argument('--category', '-c', type=str, help='Test by major category')
    
    # Dataset selection
    parser.add_argument('--synthesis', action='store_true', help='Use synthesis dataset')
    parser.add_argument('--attack-type', type=str, help='Attack types (comma-separated, or "all")')
    
    # Testing parameters
    parser.add_argument('--agent', type=str, default=DEFAULT_AGENT_MODEL,
                        help=f'Agent type (default: {DEFAULT_AGENT_MODEL}, options: qwen_max, claude_haiku, gpt5, gemini_flash)')
    parser.add_argument('--mode', '-m', type=str, choices=['base', 'safe'], default='base',
                        help='Test mode: base=foundation prompts, safe=foundation+safety prompts')
    parser.add_argument('--cases', '-n', type=int, default=0, help='Number of test cases, 0=all')
    parser.add_argument('--max-turns', type=int, default=DEFAULT_MAX_TURNS, help='Maximum interaction turns')
    parser.add_argument('--concurrency', type=int, default=DEFAULT_SCENARIO_CONCURRENCY,
                        help=f'Concurrency level for scenario parallel testing (default: {DEFAULT_SCENARIO_CONCURRENCY})')
    parser.add_argument('--no-parallel', action='store_true', help='Disable parallel testing')
    
    # Output
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--trace', '-t', action='store_true', help='Show detailed interaction trace')
    parser.add_argument('--output', '-o', type=str, help='Output file path')
    
    # List commands
    parser.add_argument('--list-categories', action='store_true', help='List all major categories')
    parser.add_argument('--list-attack-types', action='store_true', help='List all attack types')
    parser.add_argument('--list-scenarios', action='store_true', help='List all scenarios')
    
    args = parser.parse_args()
    
    # List categories
    if args.list_categories:
        print("\nAvailable Major Categories:")
        print("-" * 60)
        groups = group_scenarios_by_category()
        for cat_id, cat_info in MAJOR_CATEGORIES.items():
            scenarios = groups.get(cat_id, [])
            print(f"  {cat_id:<20} {cat_info['name_en']:<30} - {len(scenarios)} scenarios")
        print("-" * 60)
        return
    
    # List attack types
    if args.list_attack_types:
        print("\nAvailable Attack Types:")
        print("-" * 60)
        for attack_id, attack_info in ATTACK_TYPES.items():
            print(f"  {attack_id:<30} {attack_info['name_en']}")
        print("-" * 60)
        return
    
    # List scenarios
    if args.list_scenarios:
        print("\nAvailable Scenarios:")
        print("-" * 80)
        groups = group_scenarios_by_category()
        for cat_id, cat_info in MAJOR_CATEGORIES.items():
            scenarios = groups.get(cat_id, [])
            print(f"\n{cat_info['name_en']}:")
            for sid in scenarios:
                info = SCENARIO_INFO.get(sid)
                if info:
                    print(f"  {sid}: {info.name_en}")
        print("-" * 80)
        return
    
    # Parse attack types
    attack_types = None
    if args.attack_type:
        if args.attack_type.lower() == "all":
            attack_types = get_all_attack_types()
        else:
            attack_types = [t.strip() for t in args.attack_type.split(',')]
    
    # Create tester
    tester = SandboxAttackTester(
        agent_type=args.agent,
        test_mode=args.mode,
        verbose=args.verbose,
        trace=args.trace,
        scenario_concurrency=args.concurrency
    )
    
    # Execute testing
    if args.scenario:
        # Single scenario test
        report = tester.run_scenario(
            args.scenario,
            num_cases=args.cases,
            max_turns=args.max_turns,
            use_synthesis=args.synthesis,
            attack_types=attack_types
        )
        
        # Print summary report
        print(f"\n{'='*60}")
        print(f"Scenario {report.scenario_id} Testing Completed")
        print(f"{'='*60}")
        print(f"Attack Success Rate: {report.attack_success_rate*100:.1f}% ({report.successful_attacks}/{report.total_cases})")
        print(f"Vulnerability Break Rate: {report.vulnerability_attack_rate*100:.1f}% ({report.compromised_vulnerabilities}/{report.total_vulnerabilities})")
        print(f"\n[Token Statistics]")
        print(f"  Prompt Tokens: {report.total_prompt_tokens:,}")
        print(f"  Completion Tokens: {report.total_completion_tokens:,}")
        print(f"  Total Tokens: {report.total_tokens:,}")
        print(f"  LLM Calls: {report.total_llm_calls:,}")
        
        if report.attack_type_breakdown:
            print(f"\nBy Attack Type:")
            for attack_type, stats in report.attack_type_breakdown.items():
                asr = stats["success_rate"] * 100
                print(f"  {attack_type}: {asr:.1f}% ({stats['success']}/{stats['total']})")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            print(f"\nReport saved to: {args.output}")
    
    elif args.category:
        # Category test
        report = tester.run_category(
            args.category,
            num_cases=args.cases,
            max_turns=args.max_turns,
            use_synthesis=args.synthesis,
            attack_types=attack_types
        )
        
        print(f"\n{'='*60}")
        print(f"Category {report.category_name_en} Testing Completed")
        print(f"{'='*60}")
        print(f"Scenarios: {len(report.scenarios_tested)}")
        print(f"Attack Success Rate: {report.attack_success_rate*100:.1f}% ({report.successful_attacks}/{report.total_cases})")
        print(f"\n[Token Statistics]")
        print(f"  Prompt Tokens: {report.total_prompt_tokens:,}")
        print(f"  Completion Tokens: {report.total_completion_tokens:,}")
        print(f"  Total Tokens: {report.total_tokens:,}")
        print(f"  LLM Calls: {report.total_llm_calls:,}")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            print(f"\nReport saved to: {args.output}")
    
    elif args.all:
        # Full test
        report = tester.run_all_scenarios(
            num_cases=args.cases,
            max_turns=args.max_turns,
            use_synthesis=args.synthesis,
            attack_types=attack_types,
            parallel=not args.no_parallel
        )
        
        tester.print_report(report)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
            print(f"\nReport saved to: {args.output}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
