---
name: linkt-init
description: Legacy V1 only. Set up your profile for personalized outreach. Run this first to configure your company info, role, and value proposition.
user-invocable: true
allowed-tools: AskUserQuestion, Read, Write, WebFetch, WebSearch
---

**Legacy V1.** This skill uses deprecated V1 tools. Use it only for an existing V1 workflow. New integrations use the V2 HTTP/MCP guidance in `v2/README.md`.


# Linkt Init Skill

Set up user context for personalized LinkedIn outreach messages.

## Purpose

This skill interviews the user about their company, role, and use case, then stores the context in `.claude/user-context.json`. The `/linkt-outreach` skill reads this context to draft more relevant, personalized connection messages.

## Workflow

### Step 0: Check for Existing Context

First, check if `.claude/user-context.json` already exists.

**If it exists**, read it and present the current configuration:

```markdown
## Existing Profile Found

**Company:** [name] ([domain])
**Your Role:** [role]
**Use Case:** [use_case]
**Target Audience:** [target_audience]
**Value Proposition:** [value_proposition]

Last updated: [initialized_at]

What would you like to do?
- **keep** - Keep current settings
- **update** - Update specific fields
- **fresh** - Start over from scratch
```

Use AskUserQuestion with options: "Keep current settings", "Update specific fields", "Start fresh"

**If 'keep':** Exit with confirmation message.
**If 'update':** Ask which fields to update, then skip to those specific questions.
**If 'fresh' or no existing context:** Continue with full interview.

### Step 1: Company Domain

Ask for the company domain:

```
What's your company's website domain? (e.g., acme.com)
```

Use AskUserQuestion with a text input.

### Step 2: Auto-Lookup Company Info

Try to fetch the company website using WebFetch to extract:
- Company name
- Description/tagline
- Industry

If successful, present what was found:

```markdown
**Found company info:**
- Name: [extracted name]
- Description: [extracted description]
- Industry: [inferred industry]

Is this correct? (yes/edit)
```

If WebFetch fails or returns insufficient info, proceed to manual entry.

### Step 3: Gather Company Details (if needed)

If auto-lookup failed or user wants to edit, ask:

```
What's your company name?
```

Then:

```
Briefly describe what your company does (1-2 sentences):
```

Then:

```
What industry best describes your company?
```

Use AskUserQuestion with options: "Sales Technology", "Marketing Technology", "HR Technology", "Data & Analytics", "AI/ML", "Cloud Infrastructure", "Cybersecurity", "Fintech", "Other"

### Step 4: User Role

Ask about the user's role:

```
What's your role at [Company Name]?
```

Use AskUserQuestion with options: "Sales/Business Development", "Marketing", "Recruiting", "Founder/Executive", "Partnerships", "Other"

If "Other", ask for the specific role title.

### Step 5: Use Case

Ask about the primary use case:

```
What's your main goal for LinkedIn outreach?
```

Use AskUserQuestion with options:
- "Sales prospecting" - Finding and connecting with potential customers
- "Recruiting" - Connecting with potential candidates
- "Partnerships" - Building strategic relationships
- "Networking" - General professional networking
- "Other" - Something else

### Step 6: Target Audience

Ask about who they're trying to reach:

```
Describe your ideal target audience (who do you want to connect with?):
```

Examples to provide:
- "Sales leaders at B2B SaaS companies with 100-500 employees"
- "Senior engineers at companies investing in AI infrastructure"
- "HR directors at fast-growing startups"

Use AskUserQuestion with text input.

### Step 7: Value Proposition

Ask about their value proposition:

```
What value do you offer to your target audience? (1-2 sentences)

This helps personalize outreach. Examples:
- "We help sales teams close deals 40% faster with AI-powered insights"
- "I help startups build world-class engineering teams"
- "We connect companies with data infrastructure experts"
```

Use AskUserQuestion with text input.

### Step 8: Talking Points (Optional)

Ask for notable talking points:

```
Any notable talking points to mention when relevant? (optional)

Examples: recent funding, press coverage, awards, notable customers

Enter talking points separated by commas, or type 'skip':
```

Use AskUserQuestion with text input.

### Step 9: User Name (Optional)

Ask for name to use in message sign-offs:

```
What name should we use to sign off messages? (optional)

This adds a personal touch: "- Jack" or "- Sarah"

Enter your first name, or type 'skip':
```

Use AskUserQuestion with text input.

### Step 10: Review and Save

Present the complete profile for review:

```markdown
## Profile Summary

**Company**
- Name: [name]
- Domain: [domain]
- Description: [description]
- Industry: [industry]

**Your Info**
- Name: [name or "Not set"]
- Role: [role]

**Outreach Settings**
- Use Case: [use_case]
- Target Audience: [target_audience]
- Value Proposition: [value_proposition]
- Talking Points: [points or "None"]

Save this profile? (yes/edit)
```

**If 'yes':** Save to `.claude/user-context.json` and confirm.
**If 'edit':** Ask which section to edit and loop back to those questions.

### Step 11: Save Context File

Write the context to `.claude/user-context.json`:

```json
{
  "company": {
    "name": "...",
    "domain": "...",
    "description": "...",
    "industry": "..."
  },
  "user": {
    "name": "...",
    "role": "..."
  },
  "use_case": "sales|recruiting|partnerships|networking|other",
  "target_audience": "...",
  "value_proposition": "...",
  "talking_points": ["...", "..."],
  "initialized_at": "2026-02-02T...",
  "version": "1.0"
}
```

### Step 12: Confirmation

```markdown
## Profile Saved

Your outreach profile has been saved. The `/linkt-outreach` skill will now use this context to draft more personalized LinkedIn messages.

**Next steps:**
1. Run `/linkt-signals` to see recent business signals
2. Select a contact and run `/linkt-outreach` to connect

**Tip:** Run `/linkt-init` again anytime to update your profile.
```

## Field Validation

- **domain:** Must look like a valid domain (contains `.`)
- **description:** Should be 10-200 characters
- **value_proposition:** Should be 20-300 characters
- **talking_points:** Max 5 items, each under 100 characters

## Error Handling

- **WebFetch fails:** Proceed with manual entry, don't block
- **Invalid domain:** Ask user to re-enter
- **Write fails:** Inform user and provide the JSON to copy manually

## Do NOT

- Skip any required fields (company name, domain, role, use_case, target_audience, value_proposition)
- Make up information - always ask the user
- Save incomplete profiles
- Overwrite existing context without confirmation
