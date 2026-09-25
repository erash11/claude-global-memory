# Handoff: Sportsmith video processing and transcript review

Date: 2026-09-24

## Context and current state
The user is processing videos from Sportsmith's Fundamentals of on-field rehabilitation course and asked that video, locally generated transcript, and summary be saved together at:

`G:\My Drive\00_Primary_Storage_Drive\09_PRO_DEV\SS_Course_OnFieldRTP\Video Transcripts`

Part 2, “On-field rehab frameworks,” has been downloaded and processed. Its transcript was compared against the full set of cues visible in Vimeo's transcript panel. Clear recognition errors and technical terms were corrected. The local Whisper draft and Vimeo captions can each contain errors. The browser environment cannot independently listen to the player audio, so the transcript is explicitly marked caption-cross-checked, not human-verified word-for-word. If the user needs verbatim accuracy, review disputed lines by listening to the local video.

## Part 2 deliverables
- Video: `G:\My Drive\00_Primary_Storage_Drive\09_PRO_DEV\SS_Course_OnFieldRTP\Video Transcripts\Part 2 - On-field rehab frameworks.mp4` (10:54; 205,396,393 bytes)
- Transcript: `G:\My Drive\00_Primary_Storage_Drive\09_PRO_DEV\SS_Course_OnFieldRTP\Video Transcripts\Part 2 - On-field rehab frameworks - transcript.md`
- Summary: `G:\My Drive\00_Primary_Storage_Drive\09_PRO_DEV\SS_Course_OnFieldRTP\Video Transcripts\Part 2 - On-field rehab frameworks - summary.md`
- Working transcript: `C:\Users\eric_rash\Documents\Codex\2026-09-24\can-x20\outputs\Part 2 - On-field rehab frameworks - transcript.md`
- Working summary: `C:\Users\eric_rash\Documents\Codex\2026-09-24\can-x20\outputs\Part 2 - On-field rehab frameworks - summary.md`
- Local transcription script: `C:\Users\eric_rash\Documents\Codex\2026-09-24\can-x20\work\transcribe_sportsmith_part2.py`
- Transcript and summary Drive copies were SHA-256 checked against their local copies.
- Workflow preference note: `C:\Users\eric_rash\.codex\memories\extensions\ad_hoc\notes\2026-09-24-video-transcript-verification-workflow.md`

Part 2's visible Vimeo transcript was accessed through the normal player UI; player video ID `1106166134`. Local transcription used faster-whisper `small.en`, CPU int8. `yt-dlp.exe` is at `C:\Users\eric_rash\bin\yt-dlp.exe`; call by full path if it is not on a process PATH. `ffmpeg` and `ffprobe` are available. Temporary `TMP`/`TEMP` workaround for uv is noted in the working script's session context if another transcript is generated.

## Decisions and user preferences
- For future videos, compare the local transcript with captions/transcript visibly exposed by the player; treat both ASR sources as fallible.
- Correct clear recognition and sport-science terminology errors. Listen to disagreements or high-impact passages when audio review is available. State verification limits; do not call a transcript human-verified unless someone has listened through it.
- Generate lesson summaries from the corrected transcript. Save video, transcript, and summary together and verify file copies.
- User asked to record the follow-up task of creating a reusable video-processing and transcript-review skill for different harnesses. Recommended authoring location is the canonical `C:\Users\eric_rash\.claude\skills` repo, followed by the existing sync process to generated Codex and `.agents` views. The skill itself has not yet been created.

## Luna versus Sol for this workflow
Official OpenAI API documentation (checked 2026-09-24): GPT-6 Luna is positioned for efficient focused/high-volume tasks and lists API rates of $0.10/M input and $0.50/M output tokens; GPT-6 Sol is positioned for complex coding/agentic work and lists $2/M input and $10/M output tokens. That is a 20x API token-price difference, not a measured Codex subscription or latency ratio. The model pages list audio/video input as unsupported. Practical split: keep audio transcription local; use Luna for routine caption comparison, transcript cleanup, and concise summaries; use Sol to resolve difficult domain-specific disagreements or complex multi-step extraction. Escalate only uncertain segments to Sol to control cost. References: https://developers.openai.com/api/docs/models/gpt-6-luna and https://developers.openai.com/api/docs/models/gpt-6-sol

## Closeout findings
The DEV-wide closeout sweep checked 147 repositories and 13 nested repositories under `.claude`. All were clean and on `main`/`master` except `SpeedProfiling` (branch `add-2025-smu`) and `PT_Dash` (branch `claude/cmj-performance-report-011CURrnCVZRnL3cTVQHoiGN`); both branches are clean and synced with their remotes. The closeout initially found `RunningTheRoom` on `main` with uncommitted docs and no remote configured; it created local commit `ff3cefd`. A concurrent session then added commits `2ef8623` and `3a97c0c` and configured/pushed `origin/main`. The project now reports clean and synced.

## Next actions
1. Create and validate the portable video workflow skill, documenting extraction, local ASR, caption cross-check, audio-review limitations, summary generation, provenance, and verification.
2. If exact transcript fidelity is needed, perform a human audio review of Part 2 and revise both the transcript and summary accordingly.
3. Continue with the next course lesson only when the user requests it or confirms the batch scope.



