#!/usr/bin/env python3
"""
Delegation Engine - Spawns sub-specialist agents after OUTPUT stage
and aggregates their results.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from engine.kojiki_core import load_specialist, call_model, ScopedContext
# PipelineRunner imported locally to avoid circular import


@dataclass
class SubTask:
    """A task delegated to a sub-specialist."""
    sub_agent_name: str
    task_description: str
    input_data: Dict[str, Any]
    priority: int = 1
    depends_on: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class SubTaskResult:
    """Result from a sub-specialist execution."""
    sub_agent_name: str
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    execution_time_ms: int = 0


class DelegationEngine:
    """Manages spawning and coordination of sub-specialist agents."""
    
    def __init__(self, parent_specialist, dispatch: Dict[str, Any], department: str):
        self.parent_specialist = parent_specialist
        self.dispatch = dispatch
        self.department = department
        self.sub_agents_dir = Path(__file__).parent.parent.parent / "specialists" / parent_specialist.name / "sub-agents"
        self.results: List[SubTaskResult] = []
    
    def discover_sub_agents(self) -> List[str]:
        """Discover available sub-specialist agents."""
        if not self.sub_agents_dir.exists():
            return []
        
        sub_agents = []
        for item in self.sub_agents_dir.iterdir():
            if item.is_dir() and (item / "config.yaml").exists():
                sub_agents.append(item.name)
        return sub_agents
    
    def parse_execution_plan(self, output_stage_result: Dict[str, Any]) -> List[SubTask]:
        """Parse the execution_plan from OUTPUT stage into sub-tasks."""
        execution_plan = output_stage_result.get("execution_plan", {})
        tasks = execution_plan.get("tasks", [])
        
        sub_tasks = []
        for i, task in enumerate(tasks):
            # Map task to appropriate sub-specialist
            sub_agent = self._map_task_to_sub_agent(task)
            if sub_agent:
                sub_tasks.append(SubTask(
                    sub_agent_name=sub_agent,
                    task_description=task.get("description", ""),
                    input_data={
                        "task": task,
                        "parent_context": self._get_relevant_parent_context(output_stage_result),
                        "dispatch": self.dispatch
                    },
                    priority=task.get("priority", 1),
                    depends_on=task.get("depends_on", [])
                ))
        
        return sub_tasks
    
    def _map_task_to_sub_agent(self, task: Dict[str, Any]) -> Optional[str]:
        """Map a task to the appropriate sub-specialist based on task type/category."""
        task_type = task.get("type", "").lower()
        task_category = task.get("category", "").lower()
        task_description = task.get("description", "").lower()
        
        # Marketing sub-agent mapping
        mapping = {
            "seo": "seo-specialist",
            "search": "seo-specialist",
            "keyword": "seo-specialist",
            "paid social": "paid-social-specialist",
            "meta ads": "paid-social-specialist",
            "facebook ads": "paid-social-specialist",
            "linkedin ads": "paid-social-specialist",
            "tiktok ads": "paid-social-specialist",
            "content": "content-creator",
            "copywriting": "content-creator",
            "blog": "content-creator",
            "article": "content-creator",
            "growth": "growth-hacker",
            "experiment": "growth-hacker",
            "viral": "growth-hacker",
            "conversion": "growth-hacker",
            "email": "email-strategist",
            "newsletter": "email-strategist",
            "lifecycle": "email-strategist",
            "automation": "email-strategist",
            "pr": "pr-communications",
            "press": "pr-communications",
            "media": "pr-communications",
            "crisis": "pr-communications",
            "carousel": "carousel-growth",
            "instagram": "carousel-growth",
            "brand": "brand-guardian",
            "guideline": "brand-guardian",
            "identity": "brand-guardian",
            "visual": "visual-storyteller",
            "storytelling": "visual-storyteller",
            "multimedia": "visual-storyteller",
            "aeo": "aeo-specialist",
            "geo": "aeo-specialist",
            "ai citation": "aeo-specialist",
            "llm visibility": "aeo-specialist",
            "agentic": "agentic-search-optimizer",
            "mcp": "agentic-search-optimizer",
            "webmcp": "agentic-search-optimizer",
            "video": "video-optimizer",
            "youtube": "video-optimizer",
            "thumbnail": "video-optimizer",
        }
        
        # Check all text fields for matches
        search_text = f"{task_type} {task_category} {task_description}"
        for keyword, agent in mapping.items():
            if keyword in search_text:
                # Verify agent exists
                if agent in self.discover_sub_agents():
                    return agent
        
        return None
    
    def _get_relevant_parent_context(self, output_stage_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant context from parent for sub-agent."""
        return {
            "strategy": output_stage_result.get("accepted_strategy", {}),
            "interpretation": output_stage_result.get("accepted_interpretation", {}),
            "evidence": output_stage_result.get("accepted_evidence", {}),
            "problem": output_stage_result.get("accepted_problem", {}),
            "department": self.department,
            "parent_agent": self.parent_specialist.name
        }
    
    def get_stage_output(self, context: ScopedContext, stage: str) -> Optional[Dict[str, Any]]:
        """Get output from a specific stage."""
        return context.stage_outputs.get(stage)
    
    async def execute_sub_task(self, sub_task: SubTask) -> SubTaskResult:
        """Execute a single sub-task by spawning a sub-specialist."""
        start_time = datetime.now()
        
        try:
            # Load sub-specialist
            sub_specialist_name = f"{self.parent_specialist.name}.{sub_task.sub_agent_name}"
            sub_specialist = load_specialist(sub_specialist_name)
            
            # Create sub-dispatch
            sub_dispatch = {
                "task_id": f"{self.dispatch.get('task_id', 'unknown')}.{sub_task.sub_agent_name}",
                "parent_task_id": self.dispatch.get("task_id"),
                "delegated_from": self.parent_specialist.name,
                "sub_task": asdict(sub_task),
                **self.dispatch
            }
            
            # Run sub-specialist pipeline
            from kojiki.core.runner import PipelineRunner
            runner = PipelineRunner(sub_specialist, sub_dispatch)
            result = await runner.run()
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return SubTaskResult(
                sub_agent_name=sub_task.sub_agent_name,
                success=True,
                output=result,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            return SubTaskResult(
                sub_agent_name=sub_task.sub_agent_name,
                success=False,
                output={},
                error=str(e),
                execution_time_ms=execution_time
            )
    
    async def execute_all(self, sub_tasks: List[SubTask]) -> List[SubTaskResult]:
        """Execute all sub-tasks with dependency resolution."""
        # Simple topological sort for dependencies
        remaining = {t.sub_agent_name: t for t in sub_tasks}
        completed = set()
        results = []
        
        while remaining:
            # Find tasks with no unmet dependencies
            ready = [
                t for t in remaining.values()
                if all(dep in completed for dep in (t.depends_on or []))
            ]
            
            if not ready:
                # Circular dependency or missing dependency - execute anyway
                ready = list(remaining.values())[:1]
            
            # Execute ready tasks in parallel
            tasks = [self.execute_sub_task(t) for t in ready]
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for sub_task, result in zip(ready, task_results):
                if isinstance(result, Exception):
                    result = SubTaskResult(
                        sub_agent_name=sub_task.sub_agent_name,
                        success=False,
                        output={},
                        error=str(result)
                    )
                
                results.append(result)
                completed.add(sub_task.sub_agent_name)
                del remaining[sub_task.sub_agent_name]
        
        self.results = results
        return results
    
    def aggregate_results(self) -> Dict[str, Any]:
        """Aggregate sub-specialist results into a summary."""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        return {
            "delegation_summary": {
                "total_sub_tasks": len(self.results),
                "successful": len(successful),
                "failed": len(failed),
                "total_execution_time_ms": sum(r.execution_time_ms for r in self.results)
            },
            "sub_agent_results": {
                r.sub_agent_name: {
                    "success": r.success,
                    "output": r.output,
                    "error": r.error,
                    "execution_time_ms": r.execution_time_ms
                }
                for r in self.results
            },
            "aggregated_outputs": self._merge_outputs(successful)
        }
    
    def _merge_outputs(self, successful_results: List[SubTaskResult]) -> Dict[str, Any]:
        """Merge outputs from successful sub-agents."""
        merged = {}
        for result in successful_results:
            output = result.output
            # Merge key outputs
            for key in ["strategy", "output", "evidence", "interpretation", "learning"]:
                if key in output:
                    if key not in merged:
                        merged[key] = {}
                    merged[key][result.sub_agent_name] = output[key]
        return merged


async def run_delegation_stage(
    runner,
    dispatch: Dict[str, Any],
    context: ScopedContext,
    department: str
) -> Dict[str, Any]:
    """
    Execute DELEGATION stage - spawn sub-specialists based on OUTPUT execution_plan.
    This runs AFTER the OUTPUT stage.
    """
    print("\n--- STAGE 5.5: DELEGATION ---")
    
    # Get OUTPUT stage result
    engine = DelegationEngine(runner.specialist, dispatch, department)
    output_result = engine.get_stage_output(context, "output")
    if not output_result:
        print("  No OUTPUT result found, skipping delegation")
        return {"delegation_skipped": True, "reason": "No OUTPUT result"}
    
    # Check if delegation is enabled
    specialist = runner.specialist
    delegation_config = specialist.stages.get("delegation")
    if not delegation_config or not getattr(delegation_config, "enabled", True):
        print("  Delegation disabled for this specialist")
        return {"delegation_skipped": True, "reason": "Disabled in config"}
    
    # Discover available sub-agents
    available_agents = engine.discover_sub_agents()
    print(f"  Available sub-agents: {available_agents}")
    
    if not available_agents:
        print("  No sub-agents configured, skipping delegation")
        return {"delegation_skipped": True, "reason": "No sub-agents found"}
    
    # Parse execution plan into sub-tasks
    sub_tasks = engine.parse_execution_plan(output_result)
    print(f"  Parsed {len(sub_tasks)} sub-tasks from execution plan")
    
    if not sub_tasks:
        print("  No sub-tasks to delegate")
        return {"delegation_skipped": True, "reason": "No sub-tasks in execution plan"}
    
    # Execute sub-tasks
    print(f"  Executing {len(sub_tasks)} sub-tasks...")
    results = await engine.execute_all(sub_tasks)
    
    # Aggregate results
    aggregated = engine.aggregate_results()
    
    # Store in context
    context.set_stage_output("delegation", aggregated)
    
    print(f"  Delegation complete: {aggregated['delegation_summary']['successful']}/{aggregated['delegation_summary']['total_sub_tasks']} successful")
    
    return aggregated