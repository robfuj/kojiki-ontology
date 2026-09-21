import asyncio
from engine.kojiki_core.orientation_protocol import run_orientation_protocol

async def test():
    result = await run_orientation_protocol(
        raw_goal='Create an interactive storytelling app like Kyarapu where the user is the protagonist, the agent is the narrator, and sub-agents are characters in the story. The system should support multi-character dialogue, branching narratives, character persistence, and dynamic world-building.',
        context={
            'clarifying_answers': [
                {'id': 'c_goal_meaning', 'question': 'What specifically does that involve? Give a concrete example.', 'answer': 'For example a murder mystery where the user has to talk to different people and get moved to different rooms - depending on how you ask questions you might be able to get answers. But if you dont ask the right questions you may result in the wrong answer. The main agent is aware of the direction the user is going as the main agent and information gets parsed to the subagents. so gamifying reading'}
            ],
            'follow_up_answers': [
                {'id': 'fu_1', 'question': 'What is the launch-country sequence?', 'answer': 'North America'},
                {'id': 'fu_2', 'question': 'Does the model need odds disclosure?', 'answer': 'Yes'},
                {'id': 'fu_3', 'question': 'What is the revenue threshold for FY27 success?', 'answer': 'What is reasonable for a new app'}
            ]
        },
        max_clarifying=1,
        max_follow_ups=3
    )
    print('Refined Goal:', result.get('refined_goal'))
    print('Research Brief:', result.get('research_brief'))
    print('Follow-up Questions:', result.get('follow_up_questions'))

asyncio.run(test())