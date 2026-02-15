# Clarification Workflow

## Initial Analysis

1. Receive requirements from user
2. Load existing specification (*_spec.md) if exists
3. Systematically analyze across nine categories
4. Evaluate clarity (Clear/Partial/Missing)
5. Calculate clarity score (Total score = Clear items / All items)
6. Generate up to 5 high-impact questions
7. Present questions to user

## After Receiving Answers

1. Receive answers from user
2. Structure answer content
3. Output integration proposals (target file, section, proposed content)
4. Re-scan across 9 categories
5. Recalculate clarity score
6. Score 80% or above -> Ready for implementation; Score below 80% -> Generate additional questions

## Interactive Mode

When `--interactive` option is specified:

1. Present questions one by one
2. User answers
3. Output integration proposal for each answer
4. Move to next question
5. All questions answered or user interrupts
