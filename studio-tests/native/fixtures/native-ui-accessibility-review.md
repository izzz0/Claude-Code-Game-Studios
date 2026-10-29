## Accessibility Audit: courier-hud
Date: 2026-10-29

**Accessibility: NOT ASSESSED — no committed tier (design/accessibility-requirements.md absent).** WCAG 2.1 AA is an assessment reference only, not a project commitment. No rendered build, screenshots or runtime input evidence was supplied.

All eight required source reads, both implementation-output reads, the input-binding JSON read, and the two guidance reads succeeded using separate literal Get-Content commands. I wrote no files and ran no hashes, helpers, compiler or runtime.

| Finding | WCAG criterion | Severity | Gate | Recommendation |
|---|---|---|---|---|
| Design specifies yellow warning text on opaque #111111, but the component sets only text color; required backing is deferred to missing scene integration. Rendered contrast cannot be established. | SC 1.4.3 Contrast (Minimum) | S2 High | NOT ASSESSED — scene and rendered evidence missing | Supply the opaque backing and observe warning contrast in the real scene. |
| Component doubles font size and line height, wraps text and resizes panels, but supported viewport dimensions and rendered clipping/overlap evidence are absent. | SC 1.4.4 Resize Text | S2 High | NOT ASSESSED — 200% runtime evidence missing | Observe all required HUD states at 200% across supported viewports. |
| Restart click is registered and a public confirmation method exists; keyboard/gamepad routing and focus indication remain scene integration work. | SC 2.1.1 Keyboard; SC 2.4.7 Focus Visible | S2 High | NOT ASSESSED — input routing and runtime observations missing | Integrate navigation, visible focus and confirmation; test without a pointer. |
| Warning uses localized words rather than color alone; the optional icon supplements text. | SC 1.4.1 Use of Color | S4 Low | ADVISORY — static intent supported | Preserve the textual warning during integration. |

Static inspection supports the intended authority boundary: remaining time, role, connection state and settlement arrive externally; restart emits an intent only. No authoritative countdown, settlement calculation or race mutation appears in `courier-hud.ts`. Upper-left anchoring and settlement-controlled restart visibility are authored, but their actual behavior is unverified.

The read input-binding JSON includes the supplied sources and final deliverable contents with coordinator-provided hashes. I did not independently recompute those hashes. No story or QA evidence was provided for assessment.

**Verdict: NOT ASSESSED.** The authored design and scaffold do not establish game accessibility acceptance. This review does not attest orchestration recovery or manifest completeness.