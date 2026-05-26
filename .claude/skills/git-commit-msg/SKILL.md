---
name: git-commit-msg
description: Draft a conventional-commit message for the current staged/unstaged changes and present it for the user to copy. Never executes the commit.
allowed-tools: Bash
---

# Git Commit Message

Draft a commit message for the current changes. The user runs the commit themselves — never execute `git commit`.

## Steps

1. Inspect the change in parallel:
   - `git status --short`
   - `git diff --staged` (if anything is staged) and `git diff` (unstaged)
   - `git log --oneline -10` for style reference

2. If nothing has changed, say so and stop.

3. Compose a message following the rules below.

4. Output the message in a single fenced code block so it is easy to copy. Do not add commentary above or below unless the user asked for an explanation.

## Rules

**Title** — `type(scope): Title Case summary`

- Past tense: "Added", "Fixed", "Refactored" — not "Add", "Fix".
- Title case after the type tag. Proper nouns (e.g. `iOS`, `TinaCMS`) keep their natural casing.
- Valid types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`, `perf`.
- Scope is optional. Only include one when there's a clearly distinct module (`fix(guestlist):`, `feat(newsletter):`). Plain `fix:` / `feat:` is fine otherwise — don't invent a scope.
- Keep the title self-sufficient. It already summarises the change.

**Body** — bullet points only

- Use asterisks (`*`), never hyphens.
- No prose paragraph between the title and the bullets.
- One bullet per logical change. Past tense, same as the title.
- Skip the body entirely if the title fully captures the change.

**Never** include `Co-Authored-By`, `Generated with`, or any attribution footer.

**Never** run `git commit`, `git add`, or `git push`. The user will commit.

## Example

```
fix(tina): Initialized ticketing object with default status

* Added React.useEffect hook to automatically set status to 'open' on mount
* Fixed missing guestlist button on frontend
* Removed need for defaultItem config
```
