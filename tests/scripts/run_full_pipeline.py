import asyncio
from engine.orchestrator.orchestrator import Orchestrator

async def run_full_pipeline():
    orchestrator = Orchestrator()
    
    # Run full orchestration with all answers pre-populated
    result = await orchestrator.orchestrate(
        raw_goal='Develop and launch an interactive storytelling mobile application where users assume the protagonist role guided by an AI narrator with sub-agents as persistent characters, delivering genuinely branching narratives driven by user choices that alter long-term story arcs and character relationships, targeting a phased rollout starting in Japan (Q1 FY27) and South Korea (Q2 FY27) with subsequent US/EU expansion, ensuring compliance with platform odds-disclosure requirements for any gacha-based content unlocks, achieving $50K MRR by Q3 FY27 contingent on 14-day retention validation of the core choice-memory-branching loop, with key stakeholders including end-users, product/engineering teams, investors, Apple/Google platform reviewers, and regional regulators; out of scope are multiplayer modes, VR/AR integration, user-generated content tools, and non-mobile platforms for the initial release.',
        context={
            'clarifying_answers': [
                {'id': 'c_goal_meaning', 'question': 'You said: \'Develop and launch an interactive storytelling mobile application where users assume the protagonist role guided by an AI narrator with sub-agents as persistent characters, delivering genuinely branching narratives driven by user choices that alter long-term story arcs and character relationships, targeting a phased rollout starting in Japan (Q1 FY27) and South Korea (Q2 FY27) with subsequent US/EU expansion, ensuring compliance with platform odds-disclosure requirements for any gacha-based content unlocks, achieving $50K MRR by Q3 FY27 contingent on 14-day retention validation of the core choice-memory-branching loop, with key stakeholders including end-users, product/engineering teams, investors, Apple/Google platform reviewers, and regional regulators; out of scope are multiplayer modes, VR/AR integration, user-generated content tools, and non-mobile platforms for the initial release.\'. What specifically does that involve? Give a concrete example.', 'answer': 'For example a Murder mystery where you have a time limit in book world - and you have the right questions to get who the murderer is and depending on how you ask it will either be faster or slower to the answer.'},
                {'id': 'c_goal_trigger', 'question': 'What happened recently that made this a priority now?', 'answer': 'Nothing really - Just want to utilize the new advancements in LLM tech.'},
                {'id': 'c_success_criteria', 'question': 'Six months from now, what specific metrics or outcomes mean \'this succeeded\'?', 'answer': 'I want to have more opprotunity for collaboration because you can be clever with subconcious addition of marketing products through story telling.'},
                {'id': 'c_constraints', 'question': 'What\'s absolutely non-negotiable? (Hard budget cap? Regulatory deadline? Team capacity?)', 'answer': 'Want to start with $0 as much as possible'}
            ],
            'follow_up_answers': [
                {'id': 'fu_1', 'question': 'What is the launch-country sequence?', 'answer': 'I would want to start in North America'},
                {'id': 'fu_2', 'question': 'Does the model need odds disclosure?', 'answer': 'I would assume so'},
                {'id': 'fu_3', 'question': 'What is the revenue threshold for FY27 success?', 'answer': 'I don\'t know - I would hope that it would be more so # of users like getting 10,000 users'}
            ]
        },
        require_approval=False
    )
    
    print('=== ORCHESTRATION COMPLETE ===')
    print(f'Orchestration ID: {result.orchestration_id}')
    print(f'Departments: {[c.specialist_name for c in result.department_choices]}')
    print(f'Corporate OKR: {result.okr_decomposition.get("corporate_objective", {}).get("name", "N/A")}')
    print(f'Department OKRs: {list(result.okr_decomposition.get("department_okrs", {}).keys())}')
    print(f'Execution Results: {list(result.execution_results.keys())}')
    return result

asyncio.run(run_full_pipeline())