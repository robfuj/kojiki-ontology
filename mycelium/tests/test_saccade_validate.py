#!/usr/bin/env python3
"""Test for SACCADE validate_output boundary enforcement."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mycelium.engine.saccade import SACCADE, Problem


def test_validate_output_rejects_strategy_language():
    """Test that validate_output rejects strategy language."""
    saccade = SACCADE()
    
    # Problem with strategy language
    problem = Problem(
        id="P-0001",
        goal="Increase revenue by 20%",
        constraints=["Budget: $100k", "Timeline: Q4"],
        assumptions=["Market stable"],
        unknowns=["Current baseline"],
        version=1
    )
    problem.constraints.append("We should implement a new sales program")  # Strategy
    
    assert saccade.validate_output(problem) == False, "Should reject strategy language"
    print("✅ test_validate_output_rejects_strategy_language PASSED")


def test_validate_output_rejects_evidence_language():
    """Test that validate_output rejects evidence citations."""
    saccade = SACCADE()
    
    problem = Problem(
        id="P-0002",
        goal="Reduce churn by 15%",
        constraints=["Budget: $50k"],
        assumptions=["Product quality adequate"],
        unknowns=["Root cause of churn"],
        version=1
    )
    problem.assumptions.append("According to study X, churn is driven by price")  # Evidence
    
    assert saccade.validate_output(problem) == False, "Should reject evidence language"
    print("✅ test_validate_output_rejects_evidence_language PASSED")


def test_validate_output_rejects_empty_goal():
    """Test that validate_output rejects empty goal."""
    saccade = SACCADE()
    
    problem = Problem(
        id="P-0003",
        goal="",  # Empty
        constraints=["Budget: $50k"],
        assumptions=["Product quality adequate"],
        unknowns=["Root cause"],
        version=1
    )
    
    assert saccade.validate_output(problem) == False, "Should reject empty goal"
    print("✅ test_validate_output_rejects_empty_goal PASSED")


def test_validate_output_rejects_no_constraints():
    """Test that validate_output rejects missing constraints."""
    saccade = SACCADE()
    
    problem = Problem(
        id="P-0004",
        goal="Increase revenue by 20%",
        constraints=[],  # Empty
        assumptions=["Market stable"],
        unknowns=["Current baseline"],
        version=1
    )
    
    assert saccade.validate_output(problem) == False, "Should reject no constraints"
    print("✅ test_validate_output_rejects_no_constraints PASSED")


def test_validate_output_rejects_no_assumptions():
    """Test that validate_output rejects missing assumptions."""
    saccade = SACCADE()
    
    problem = Problem(
        id="P-0005",
        goal="Increase revenue by 20%",
        constraints=["Budget: $100k"],
        assumptions=[],  # Empty
        unknowns=["Current baseline"],
        version=1
    )
    
    assert saccade.validate_output(problem) == False, "Should reject no assumptions"
    print("✅ test_validate_output_rejects_no_assumptions PASSED")


def test_validate_output_rejects_no_unknowns():
    """Test that validate_output rejects missing unknowns."""
    saccade = SACCADE()
    
    problem = Problem(
        id="P-0006",
        goal="Increase revenue by 20%",
        constraints=["Budget: $100k"],
        assumptions=["Market stable"],
        unknowns=[],  # Empty
        version=1
    )
    
    assert saccade.validate_output(problem) == False, "Should reject no unknowns"
    print("✅ test_validate_output_rejects_no_unknowns PASSED")


def test_validate_output_rejects_non_measurable_goal():
    """Test that validate_output rejects goals without measurable intent."""
    saccade = SACCADE()
    
    problem = Problem(
        id="P-0007",
        goal="Make things better",  # No measurable intent
        constraints=["Budget: $100k"],
        assumptions=["Market stable"],
        unknowns=["Current baseline"],
        version=1
    )
    
    assert saccade.validate_output(problem) == False, "Should reject non-measurable goal"
    print("✅ test_validate_output_rejects_non_measurable_goal PASSED")


def test_validate_output_accepts_valid_problem():
    """Test that validate_output accepts a well-formed problem."""
    saccade = SACCADE()
    
    problem = Problem(
        id="P-0008",
        goal="Increase ARR by 20% by Q4 2026",
        constraints=["Budget: $100k", "Team: 5 FTE", "Timeline: 6 months"],
        assumptions=["Market conditions stable", "Product-market fit confirmed"],
        unknowns=["Current ARR baseline", "Competitor pricing changes", "Seasonal demand variation"],
        version=1
    )
    
    assert saccade.validate_output(problem) == True, "Should accept valid problem"
    print("✅ test_validate_output_accepts_valid_problem PASSED")


def test_validate_output_accepts_explicit_no_constraints():
    """Test that explicit 'no constraints' statement is accepted."""
    saccade = SACCADE()
    
    problem = Problem(
        id="P-0009",
        goal="Define problem scope by end of week",
        constraints=["No explicit constraints provided"],  # Explicit statement
        assumptions=["Stakeholders available"],
        unknowns=["Full requirements"],
        version=1
    )
    
    assert saccade.validate_output(problem) == True, "Should accept explicit no-constraints"
    print("✅ test_validate_output_accepts_explicit_no_constraints PASSED")


if __name__ == "__main__":
    test_validate_output_rejects_strategy_language()
    test_validate_output_rejects_evidence_language()
    test_validate_output_rejects_empty_goal()
    test_validate_output_rejects_no_constraints()
    test_validate_output_rejects_no_assumptions()
    test_validate_output_rejects_no_unknowns()
    test_validate_output_rejects_non_measurable_goal()
    test_validate_output_accepts_valid_problem()
    test_validate_output_accepts_explicit_no_constraints()
    print("\n✅ All SACCADE validate_output tests passed")