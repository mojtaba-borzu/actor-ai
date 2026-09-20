# State system and event mapping

Two separate things, deliberately kept apart:

- **Agent events** — what the tooling actually emits. Dozens of them, most firing in well under a second.
- **Visual states** — what the character can actually show. Far fewer, because at 180 px a human cannot distinguish more than about a dozen ambient poses.

The brief's 40 "states" are agent events, not visual states. About 26 of them are pose-identical at real render size. They are all still mapped — through **12 pose families** differentiated by FX shape, accent colour and rhythm.

---

## 1. Pose families

| # | Family | Type | Covers (brief state numbers) | Differentiated by |
|---|--------|------|------------------------------|-------------------|
| F1 | IDLE | loop | 01 idle, 03 waiting, 27 break | energy near zero; break adds a sit |
| F2 | THINK | loop | 02 thinking, 09 reading, 10 searching, 11 analyzing | `fx_front` head particles → drifting cards (search) → orbiting fragments (analyze) → single panel (read) |
| F3 | WORK | loop | 07 working, 08 coding, 14 file-created, 15 file-edited, 17 build, 16 git-commit | `fx_back` panel type + blade activity level |
| F4 | STRIKE | one-shot | 12 tool-call, 13 terminal-command, 25 deployment | portal (tool) vs horizontal line (command) vs upward trail (deploy) |
| F5 | INSPECT | loop | 18 running-tests, 19 debugging | crouch depth; test results tint fragments teal/orange |
| F6 | ASK | loop | 04 user-input-required, 05 permission-required, 38 notification | open palm (ask) vs hand near blade (permission) vs raised finger (notify) |
| F7 | ALERT | one-shot | 20 error, 39 warning, 21 retry | shard (error) vs chevrons (warning) vs recompose (retry) |
| F8 | WIN | one-shot | 22 success, 23 big-success, 24 finished, 40 celebration | ring count and duration only — same body animation |
| F9 | REST | loop | 26 night-work, 28 sleep, 29 wake-up | night-work is a colour grade applied to F1/F3, not a pose |
| F10 | MOVE | loop | 30 walk, 31 run, 32 climb | side view rig, v1.1 |
| F11 | LIFECYCLE | one-shot | 35 appear, 36 disappear, 37 goodbye | assembly / dissolve direction |
| F12 | PLAY | reactive | 33 sit-on-window, 34 dragged | driven by pointer, not by agent events |

**v1 ships nine states** (D3): `IDLE`, `THINK`, `WORK`, `STRIKE`, `ALERT`, `WIN`, `REST/sleep`, `appear`, `disappear`. Everything else maps onto those through FX presets on day one, and is upgraded to its own pose once the nine have survived real use.

**Night-work is not a state.** It is a colour grade applied by local clock, because no agent event carries the time of day. Keeping it out of the state machine avoids a state that can never be exited correctly.

## 2. What the tooling actually emits

Reference list of the agent hook events considered — **33 hook events**:

`SessionStart` · `Setup` · `InstructionsLoaded` · `UserPromptSubmit` · `UserPromptExpansion` · `MessageDisplay` · `PreToolUse` · `PermissionRequest` · `PostToolUse` · `PostToolUseFailure` · `PostToolBatch` · `PermissionDenied` · `Notification` · `SubagentStart` · `SubagentStop` · `TaskCreated` · `TaskCompleted` · `Stop` · `StopFailure` · `TeammateIdle` · `ConfigChange` · `CwdChanged` · `DirectoryAdded` · `FileChanged` · `WorktreeCreate` · `WorktreeRemove` · `PreCompact` · `PostCompact` · `PreModelSwitch` · `PostModelSwitch` · `SessionEnd` · `Elicitation` · `ElicitationResult`

Four facts that shape the design:

1. **`PermissionRequest` is the immediate permission signal.** `Notification` with the `permission_prompt` matcher only fires after the prompt has waited about six seconds. A mascot built on the notification would be six seconds late to the single most important "look at me" moment. Use `PermissionRequest`; treat `permission_prompt` as a fallback for the sandboxed-network case it does not cover.
2. **The transcript file lags.** `transcript_path` is written asynchronously and may not contain the current turn when a hook fires. It is fine for history, useless for liveness. For end-of-turn text use `last_assistant_message` on `Stop` / `SubagentStop`.
3. **Subagent hooks carry the parent's `session_id`.** The subagent is identified by the separate `agent_id` / `agent_type` fields. Keying the sprite on `session_id` alone merges N concurrent subagents into one state and produces flicker. Key on `session_id` + `agent_id`.
4. **`permission_mode` and `effort` are not on every event**, and `prompt_id` / `scratchpad_dir` appear only on recent versions. Every field read must tolerate absence. Note also that the `PostToolUse` result field is `tool_response`, not `tool_output` — code written against `tool_output` reads `undefined`.

`Notification` matchers worth handling explicitly: `permission_prompt`, `idle_prompt`, `agent_needs_input`, `agent_completed`, `elicitation_dialog`, and the three `quota_auto_resume_*` types — the last of which are how a usage limit becomes visible at all.

## 3. Event → family map

| Signal | Family | Notes |
|---|---|---|
| `SessionStart` | `appear` → IDLE | |
| `UserPromptSubmit` | THINK | enters immediately; the model's reasoning itself emits nothing |
| `PreToolUse` Read/Glob/Grep | THINK + search FX | |
| `PreToolUse` Edit/Write/NotebookEdit | WORK + code FX | |
| `PreToolUse` Bash | STRIKE | horizontal line |
| `PreToolUse` WebSearch/WebFetch | THINK + card FX | |
| `PreToolUse` `mcp__*` | STRIKE | portal |
| `PreToolUse` Task | WORK + satellite | see §5 |
| `PostToolUse` | return to previous family | |
| `PostToolUseFailure` | ALERT (minor) | |
| `PermissionRequest` | ASK | highest priority; immediate |
| `PermissionDenied` | ALERT (minor) → IDLE | |
| `Notification` `idle_prompt` | IDLE → dormant | ~60 s after the turn ends |
| `Notification` `agent_needs_input` | ASK | |
| `Notification` `quota_auto_resume_*` | ALERT (warning) then wait | the only visible sign of a usage limit |
| `Elicitation` / `ElicitationResult` | ASK / resume | |
| `PreCompact` / `PostCompact` | THINK + compaction FX | long and otherwise unexplained pause |
| `PreModelSwitch` / `PostModelSwitch` | cosmetic | eye-line tint shift only, no state change |
| `SubagentStart` / `SubagentStop` | satellite count ±1 | never its own sprite |
| `TaskCreated` / `TaskCompleted` | WORK / WIN (small) | |
| `FileChanged` | WORK micro-beat | FX only, no pose change |
| `Stop` | WIN (short) → IDLE | |
| `StopFailure` | ALERT | |
| `SessionEnd` | `goodbye` → `disappear` | |

**Not observable, and therefore inferred or cut:** model reasoning has no start/stop event — "thinking" is inferred from the gap between `UserPromptSubmit` / `PostToolUse` and the next event. Time of day is local clock. Git, test runners, builds and IDE activity have no agent hook — they are v2 integrations via file watching or their own hooks, and v1 does not pretend to show them.

## 4. Timing policy

Tool calls routinely complete faster than any animation can be perceived. Without a policy the character strobes.

- **Debounce** 250 ms: an event that arrives and resolves inside that window produces FX only, never a pose change.
- **Minimum dwell** 700 ms per family. A family that is entered is held for at least that long, even if its cause has already finished.
- **Burst detector**: more than 5 events in 2 s enters a WORK *burst* variant, which does not replay its entry animation and lets FX carry the rate. This is what stops a tight edit-test loop from looking like a seizure.
- **Interruptibility**: `WIN` and `goodbye` always complete. `STRIKE` is interruptible after the apex of the slash. `ALERT` is interruptible after 400 ms. Everything else is interruptible immediately.
- **Priority**, highest first: `ASK` → `ALERT` → `WIN` → `STRIKE` → `WORK` → `THINK` → `IDLE` → `REST`. A lower-priority event never preempts a higher-priority one that is still in its minimum dwell.
- **No queue.** Queueing means the character is still playing tool-call animations thirty seconds after the task finished — it would be lying about the present state. Dropped events are dropped.

Do not hard-code assumed tool latencies. If real numbers are needed they are measurable: the agent's OTLP tool-execution span carries `duration_ms`, and a blocked-on-user span separates permission-wait from execution time.

## 5. Concurrency

One character, N sessions and subagents.

- The **focused session drives the sprite.** Focus follows the most recent user interaction, not the most recent event — otherwise a background session steals the character mid-sentence.
- **Subagents are satellites**, not sprites: small `fx_back` fragments orbiting the character, one per active subagent, capped at five with a "5+" density change beyond that. They never change the pose.
- **Background sessions** contribute a single dim marker, and their completion produces one `WIN` beat only if no foreground state is playing.
- Never spawn a second character window. Two mascots on a desktop is two problems.

## 6. Transitions

The transition graph must be **total**: any state can be interrupted by any other, so an unnamed pair must still resolve.

- **Default** for every unnamed pair: 150 ms cross-dissolve of the pose, with FX cut immediately.
- **Named transitions** exist only where a dissolve visibly pops: `IDLE→THINK`, `THINK→WORK`, `WORK→STRIKE`, `WORK→ALERT`, `ALERT→retry→WORK`, `WORK→WIN`, `WIN→IDLE`, `IDLE→REST`, `REST→wake→IDLE`, `appear→IDLE`, `IDLE→goodbye`.
- Because the sword materialises rather than being drawn (D2), every transition into and out of an execution state already has a natural 6–8 frame bridge, which removes most of the popping the brief's transition list was trying to solve.
