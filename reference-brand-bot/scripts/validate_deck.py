#!/usr/bin/env python3
"""
Deck Validator for Kojiki SYNAPSIS Pipeline

Enforces consultant framework compliance in DECK stage output:
1. Pyramid Principle - First slide must be answer_first
2. SCQ Framework - Slides must follow Situation → Complication → Question → Answer order
3. MECE - No duplicate points across groups in mece_grouped slides
4. Storyboarding - All slide titles unique and non-empty
5. Schema - Validates against schema/deck.json
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple
from jsonschema import validate, ValidationError


SCQ_LAYOUT_ORDER = ["context", "problem", "question", "answer_first"]


def load_schema(schema_path: Path) -> dict:
    """Load JSON schema from file."""
    with open(schema_path) as f:
        return json.load(f)


def validate_schema(deck: dict, schema_path: Path) -> Tuple[bool, List[str]]:
    """Validate deck against JSON schema."""
    try:
        schema = load_schema(schema_path)
        validate(instance=deck, schema=schema)
        return True, []
    except ValidationError as e:
        return False, [f"Schema: {e.message}"]
    except FileNotFoundError:
        return False, [f"Schema file not found: {schema_path}"]


def validate_pyramid(deck: dict) -> List[str]:
    """Validate Pyramid Principle: first slide must be answer_first."""
    errors = []
    slides = deck.get("slides", [])
    if not slides:
        errors.append("Pyramid: No slides in deck")
        return errors
    
    first_slide = slides[0]
    layout = first_slide.get("layout", "")
    if layout != "answer_first":
        errors.append(f"Pyramid: First slide layout is '{layout}', must be 'answer_first'")
    
    return errors


def validate_scq(deck: dict) -> List[str]:
    """Validate SCQ Framework: slides must follow Situation→Complication→Question→Answer order.
    
    Note: Pyramid Principle requires answer_first as slide 1. SCQ order applies to the
    remaining SCQ-structured slides after the opening answer_first.
    """
    errors = []
    slides = deck.get("slides", [])
    
    # Extract layouts in order
    layouts = [s.get("layout", "") for s in slides]
    
    # Find the sequence of SCQ layouts
    scq_sequence = [l for l in layouts if l in SCQ_LAYOUT_ORDER]
    
    if not scq_sequence:
        errors.append("SCQ: No SCQ-structured slides found (need context/problem/question/answer_first)")
        return errors
    
    # If first slide is answer_first (Pyramid Principle), skip it for SCQ ordering
    # SCQ order applies to the rest: context → problem → question → answer_first
    if scq_sequence[0] == "answer_first":
        scq_sequence = scq_sequence[1:]
    
    # Check that the sequence follows the required order
    expected_idx = 0
    for layout in scq_sequence:
        if layout == SCQ_LAYOUT_ORDER[expected_idx]:
            if expected_idx < len(SCQ_LAYOUT_ORDER) - 1:
                expected_idx += 1
        elif layout in SCQ_LAYOUT_ORDER[expected_idx + 1:]:
            # Found a later SCQ layout before an earlier one
            expected_pos = SCQ_LAYOUT_ORDER.index(layout)
            actual_pos = expected_idx
            errors.append(
                f"SCQ: Layout '{layout}' appears before required '{SCQ_LAYOUT_ORDER[expected_idx]}' "
                f"(order must be: {' → '.join(SCQ_LAYOUT_ORDER)})"
            )
            break
    
    # Must have at least context and answer_first
    if "context" not in layouts:
        errors.append("SCQ: Missing 'context' (Situation) slide")
    if "answer_first" not in layouts:
        errors.append("SCQ: Missing 'answer_first' (Answer) slide")
    
    return errors


def validate_mece(deck: dict) -> List[str]:
    """Validate MECE: no duplicate points across groups in mece_grouped slides."""
    errors = []
    slides = deck.get("slides", [])
    
    for slide in slides:
        if slide.get("layout") != "mece_grouped":
            continue
        
        content = slide.get("content", {})
        groups = content.get("groups", [])
        
        if not groups:
            errors.append(f"MECE: Slide {slide.get('slide_id')} has mece_grouped layout but no groups")
            continue
        
        # Check each group has at least one point
        for i, group in enumerate(groups):
            points = group.get("points", [])
            if not points:
                errors.append(f"MECE: Slide {slide.get('slide_id')} group {i} ('{group.get('label')}') has no points")
        
        # Check for duplicate points across groups
        all_points: Dict[str, List[str]] = {}  # point_text -> [group_labels]
        for group in groups:
            label = group.get("label", "unknown")
            for point in group.get("points", []):
                normalized = point.strip().lower()
                if normalized not in all_points:
                    all_points[normalized] = []
                all_points[normalized].append(label)
        
        for point_text, group_labels in all_points.items():
            if len(group_labels) > 1:
                errors.append(
                    f"MECE: Slide {slide.get('slide_id')} - point appears in multiple groups: "
                    f"'{point_text}' in {', '.join(group_labels)}"
                )
    
    return errors


def validate_storyboarding(deck: dict) -> List[str]:
    """Validate Storyboarding: all slide titles unique and non-empty."""
    errors = []
    slides = deck.get("slides", [])
    
    titles = []
    for slide in slides:
        title = slide.get("title", "").strip()
        slide_id = slide.get("slide_id", "unknown")
        
        if not title:
            errors.append(f"Storyboarding: Slide {slide_id} has empty title")
        titles.append((slide_id, title))
    
    # Check uniqueness
    seen: Set[str] = set()
    for slide_id, title in titles:
        if title in seen:
            errors.append(f"Storyboarding: Duplicate title '{title}' (slide {slide_id})")
        seen.add(title)
    
    return errors


def validate_deck(deck_path: Path, schema_path: Path) -> Tuple[bool, List[str]]:
    """Run all validations on a deck file."""
    with open(deck_path) as f:
        deck = json.load(f)
    
    all_errors = []
    
    # Schema validation
    schema_ok, schema_errors = validate_schema(deck, schema_path)
    if not schema_ok:
        all_errors.extend(schema_errors)
    
    # Consultant framework validations
    all_errors.extend(validate_pyramid(deck))
    all_errors.extend(validate_scq(deck))
    all_errors.extend(validate_mece(deck))
    all_errors.extend(validate_storyboarding(deck))
    
    return len(all_errors) == 0, all_errors


def main():
    parser = argparse.ArgumentParser(description="Validate DECK output against consultant frameworks")
    parser.add_argument("deck", help="Path to deck.json file")
    parser.add_argument("--schema", default="schema/deck.json", help="Path to schema file")
    args = parser.parse_args()
    
    deck_path = Path(args.deck)
    schema_path = Path(args.schema)
    
    if not deck_path.exists():
        print(f"Deck not found: {deck_path}")
        return 1
    
    if not schema_path.exists():
        # Try relative to deck file
        schema_path = deck_path.parent / args.schema
    
    if not schema_path.exists():
        print(f"Schema not found: {schema_path}")
        return 1
    
    print(f"Validating {deck_path} against {schema_path}")
    print("-" * 60)
    
    valid, errors = validate_deck(deck_path, schema_path)
    
    if valid:
        print("✅ ALL VALIDATIONS PASSED")
        return 0
    else:
        print(f"❌ VALIDATION FAILED ({len(errors)} errors):")
        for err in errors:
            print(f"  - {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())