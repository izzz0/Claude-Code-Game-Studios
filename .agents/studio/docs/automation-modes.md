# Automation modes

Configuration is resolved by yaml-helper.sh, not by duplicating precedence logic in a skill. New projects default to minimal rigor and guided automation; preserve explicit existing values.

- guided: explain the intended outcome, automatically perform routine edits/checks inside the authorized task, and ask only for consequential product, scope or architecture choices and genuinely missing input.
- collaborative: review each major phase draft before implementation; ordinary authorized writes do not need individual approval.
- autonomous: decide within accepted scope and record meaningful choices. This does not authorize external publication or override host permissions.

Honor modes.automation_always_ask and existing authorization. A required question with no answer remains pending. User selection of automatic studio execution enables native coordination and configured hooks, not unlimited work outside the request.

Configuration scope, review depth, workflow and team size are independent. Do not turn automatic execution into a forced full process or spawn the entire roster for a small task. An unsupported/untrusted host must be reported honestly; it does not imply the hooks ran.
