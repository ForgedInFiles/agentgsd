---
name: brainstorming
description: Refines rough ideas through Socratic questioning, explores alternatives, and presents design in digestible chunks for validation. This is the first step in the gsdmode workflow.
license: MIT
metadata:
  author: adapted from obra/superpowers
  version: "1.0"
  tags: brainstorming,design,planning,workflow
---

# Brainstorming Skill (gsdmode)

## Overview
This skill activates before any implementation work begins. It takes rough ideas and user goals, then refines them through targeted questioning to:
- Explore alternatives and edge cases
- Identify hidden assumptions and requirements
- Break down complex problems into manageable components
- Present the emerging design in digestible chunks for user validation
- Save a refined design document that serves as the foundation for all subsequent work

The brainstorming skill follows the gsdmode philosophy of "complexity reduction" - it seeks the simplest solution that fully addresses the user's needs while maintaining flexibility for future evolution.

## When to Activate
This skill should automatically activate when:
- The user presents a new feature request or problem to solve
- The conversation shifts from discussion to implementation intent
- A rough idea needs refinement before planning begins
- The user asks for help "figuring out how to approach" something

It should NOT activate when:
- The user is asking for clarification on existing code
- The user wants to make small, isolated changes
- The user is requesting explanations or tutorials
- Work is already in progress on an established plan

## Core Process

### 1. Initial Understanding
Start by restating the user's goal in your own words to confirm understanding. Ask:
- "What problem are we trying to solve?"
- "Who will use this and how?"
- "What does success look like?"

### 2. Constraint Discovery
Identify all constraints and non-functional requirements:
- Performance requirements
- Platform/technology constraints
- Team/size limitations
- Timeline considerations
- Compliance or security needs
- Integration requirements with existing systems

### 3. Exploration Phase
Actively explore alternatives by asking:
- "What are 2-3 completely different ways we could approach this?"
- "What would the simplest possible solution look like?"
- "What would happen if we ignored [specific constraint]?"
- "How would [different technology/method] handle this?"
- "What's the minimum viable version of this?"

### 4. Complexity Reduction
Relentlessly seek simplicity by questioning:
- "What if we removed [feature/requirement] - would the core solution still work?"
- "Can we defer [complex aspect] to a later version?"
- "Is there a built-in or existing solution we could leverage instead?"
- "What's the 80/20 solution here?"

### 5. Risk Assessment
Identify potential pitfalls and failure modes:
- "What could go wrong with this approach?"
- "What assumptions are we making that might not hold?"
- "Where have similar approaches failed in the past?"
- "What would make this solution obsolete or problematic in 6 months?"

### 6. Component Breakdown
Decompose the solution into logical, implementable pieces:
- What are the natural seams in this system?
- Which components can be built and tested independently?
- What interfaces need to be defined between components?
- What would be the logical order of implementation?

### 7. Validation Preparation
Prepare the design for user review by:
- Organizing thoughts into clear, numbered sections
- Writing in plain language (minimize jargon)
- Including concrete examples where helpful
- Calling out open questions that need user input
- Clearly marking assumptions

## Output Format
The brainstorming skill should produce a design document with these sections:

### 🎯 Goal Statement
A clear, concise restatement of what we're trying to achieve.

### 🔍 Key Constraints
Important limitations, requirements, and boundaries.

### 💡 Core Approach
The fundamental solution strategy after exploration and simplification.

### 🧩 Component Breakdown
Logical decomposition into implementable pieces.

### 🚨 Open Questions & Assumptions
Items requiring user confirmation or that carry risk.

### 📋 Next Steps
Recommended actions for moving to the planning phase.

## Tool Usage Patterns

### Using with Agent Tools
```yaml
# Typical workflow
1. User: "I need a way to track user preferences in my web app"
2. Agent activates brainstorming skill
3. Agent uses `read` to examine existing code structure
4. Agent uses `grep` to understand current patterns
5. Agent asks clarifying questions through conversation
6. Agent uses `write` to create design document
7. Agent presents design in chunks for user validation
```

### Conversation Patterns
Instead of making statements, frame explorations as questions:
- "Have we considered..." instead of "We should..."
- "What would happen if..." instead of "This won't work because..."
- "Could we simplify by..." instead of "This is too complex..."
- "I'm wondering about..." instead of "We need to decide..."

## Integration with gsdmode Workflow
This skill is the first in the gsdmode sequence:
1. **Brainstorming** (this skill) → Refines the idea
2. **Git Worktrees** → Sets up clean implementation environment
3. **Writing Plans** → Creates detailed implementation tasks
4. **Subagent-Driven Development** → Executes the plan with quality gates
5. **TDD** → Ensures correctness during implementation
6. **Code Review** → Maintains quality between tasks
7. **Finishing Branch** → Completes the work cycle

The agent should automatically progress to the next skill when:
- The user has validated the design document
- Open questions have been resolved
- There's clear consensus on the core approach
- The user indicates readiness to move to planning

## Best Practices

### Do ✅
- Start with the user's words, not your assumptions
- Question everything, especially "obvious" solutions
- Seek the simplest solution that meets core needs
- Make trade-offs explicit, not hidden
- Save all work products for future reference
- Think in terms of evolution, not perfection

### Don't ❌
- Jump to solutions before understanding the problem
- Assume constraints without verifying
- Over-engineer for hypothetical future needs
- Present incomplete thoughts as finished designs
- Forget to validate with the user before proceeding
- Let perfectionism block progress

## Example Session

**User**: "I want to add user authentication to my blog"

**Agent (Brainstorming)**:
1. Restates goal: "So we need a way for users to create accounts, log in, and have their identity recognized when creating/viewing blog posts?"
2. Explores constraints: "Should this work with your existing data storage? Any preference for authentication methods (email/password, OAuth, etc.)?"
3. Considers alternatives: "We could implement a simple session-based system, use JWT tokens, or integrate with an existing Auth service..."
4. Seeks simplicity: "For a blog, would email/password with server-side sessions be sufficient to start?"
5. Identifies components: "User model, registration form, login form, session middleware, protected routes..."
6. Prepares validation: Creates design doc with these sections and asks: "Does this capture what you had in mind? What would you adjust?"

**User**: "Yes, that looks good. Let's move to planning."

**Agent**: Deactivates brainstorming skill, activates git worktrees skill.

---
*Adapted from obra/superpowers brainstorming skill for agentgsd gsdmode*
