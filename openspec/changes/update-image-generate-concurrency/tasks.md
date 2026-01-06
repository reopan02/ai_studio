## 1. Implementation
- [x] 1.1 Update provider client generation to omit outbound `n` and execute `n` concurrent calls.
- [x] 1.2 Update `/api/v1/images/generations` to aggregate concurrent results into a single OpenAI-compatible response.
- [x] 1.3 Ensure stored request/response payloads accurately reflect the new behaviour (no provider `n` in outbound request payload).
- [ ] 1.4 Manual validation: request `n=2..4` in the Image Generate UI and confirm the response contains `n` images and upstream requests omit `n`.
- [x] 1.5 Update `/api/v1/images/edits` to accept `n` and execute `n` concurrent single-image edit calls.
- [x] 1.6 Update `/api/v1/images/edits` storage payloads to record concurrency and omit provider `n`.
- [ ] 1.7 Manual validation: submit `POST /api/v1/images/edits` with `n=2..4` and confirm the response contains `n` images and upstream requests omit `n`.
