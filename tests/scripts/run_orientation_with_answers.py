import asyncio
from engine.kojiki_core.orientation_protocol import run_orientation_protocol

async def test():
    result = await run_orientation_protocol(
        raw_goal='Develop and launch an interactive storytelling mobile application where users assume the protagonist role guided by an AI narrator with sub-agents as persistent characters, delivering genuinely branching narratives driven by user choices that alter long-term story arcs and character relationships, targeting a phased rollout starting in Japan (Q1 FY27) and South Korea (Q2 FY27) with subsequent US/EU expansion, ensuring compliance with platform odds-disclosure requirements for any gacha-based content unlocks, achieving $50K MRR by Q3 FY27 contingent on 14-day retention validation of the core choice-memory-branching loop, with key stakeholders including end-users, product/engineering teams, investors, Apple/Google platform reviewers, and regional regulators; out of scope are multiplayer modes, VR/AR integration, user-generated content tools, and non-mobile platforms for the initial release.',
        context={
            'clarifying_answers': [
                {'id': 'c_goal_meaning', 'question': 'You said: \'Develop and launch an interactive storytelling mobile application where users assume the protagonist role guided by an AI narrator with sub-agents as persistent characters, delivering genuinely branching narratives driven by user choices that alter long-term story arcs and character relationships, targeting a phased rollout starting in Japan (Q1 FY27) and South Korea (Q2 FY27) with subsequent US/EU expansion, ensuring compliance with platform odds-disclosure requirements for any gacha-based content unlocks, achieving $50K MRR by Q3 FY27 contingent on 14-day retention validation of the core choice-memory-branching loop, with key stakeholders including end-users, product/engineering teams, investors, Apple/Google platform reviewers, and regional regulators; out of scope are multiplayer modes, VR/AR integration, user-generated content tools, and non-mobile platforms for the initial release.\'. What specifically does that involve? Give a concrete example.', 'answer': 'For example a Murder mystery where you have a time limit in book world - and you have the right questions to get who the murderer is and depending on how you ask it will either be faster or slower to the answer.'},
                {'id': 'c_goal_trigger', 'question': 'What happened recently that made this a priority now?', 'answer': 'Nothing really - Just want to utilize the new advancements in LLM tech.'},
                {'id': 'c_success_criteria', 'question': 'Six months from now, what specific metrics or outcomes mean \'this succeeded\'?', 'answer': 'I want to have more opprotunity for collaboration because you can be clever with subconcious addition of marketing products through story telling.'},
                {'id': 'c_constraints', 'question': 'What\'s absolutely non-negotiable? (Hard budget cap? Regulatory deadline? Team capacity?)', 'answer': 'Want to start with $0 as much as possible'}
            ]
        },
        max_clarifying=4,
        max_follow_ups=4
    )
    print('=== CLARIFYING PHASE COMPLETE ===')
    print('Refined Goal:', result.get('refined_goal'))
    print()
    print('Research Brief:', result.get('research_brief'))
    print()
    print('Follow-up Questions:')
    for q in result.get('follow_up_questions', []):
        print(f'  {q["id"]}: {q["question"]} [{q.get("category", "")}]')
    print()
    return result

asyncio.run(test())