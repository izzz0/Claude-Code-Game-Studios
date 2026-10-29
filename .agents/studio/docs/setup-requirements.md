# Setup requirements

Use an existing local Codex desktop/CLI installation that supports project-local skills, standalone custom agents and lifecycle hooks. Follow the [official Codex documentation](https://learn.chatgpt.com/docs) for installation and host settings. The current probe discovered 74 enabled skills; native hook discovery/listing is empty and therefore remains unresolved, not trusted by inference. The `ccgs-help` typed invocation probe failed during Windows sandbox setup and remains `NOT ASSESSED`.

Required tools are Git, Python 3.11 or newer (including tomllib), and Bash. On Windows use Git for Windows' Bash; a WSL launcher or Windows Store placeholder is not evidence Bash works. The native hook adapter runs Python; preserved business helpers additionally require Bash. Optional jq accelerates the preserved commit parser; Python handles native hook JSON.

Run git --version, python --version and Bash's --version in the actual host environment. Windows hook commands use python; POSIX commands use python3. Both must resolve to a working Python 3.11+ interpreter. CCGS_BASH may explicitly select a working Bash executable for this project invocation. Do not change global PATH or Codex settings implicitly.

Open this checkout as the chat's project. Start with $ccgs-start, which reports discovered skills/roles, engine and capability limits. A separate chat in another project does not discover this repository's skills.

Review and trust the project's current hook definitions through the host's hook controls. A configured file is not proof the definitions are trusted or events ran. Definition changes require renewed review. Never bypass hook trust for acceptance.

Select and install the actual game engine separately. The only current engine evidence is the Godot headless export probe recorded in `.scratch/full-acceptance-20261025/toolchain/export-probe-report.md`; it is not a full game acceptance run. Godot 4.6.1/GDScript remains the target, while Unity, Unreal and Cocos remain `NOT ASSESSED` until exercised. The Cocos adapter is planned around `engine.name: Cocos`, plural roots and Node TAP, with Cocos 3.8.8 verification pending.

Configuration remains project.yaml, with whitelisted personal overrides in ignored project.local.yaml. Host model, provider, permissions and account settings remain inherited. Framework automation settings do not change host permissions. No extra model API credentials or global skill/agent/Hook installation is required.

Run python -m unittest discover -s studio-tests/codex -v for framework checks. Game tests, input/visual observation and local exported-build verification are separate checks; missing tools/results stay NOT ASSESSED.
