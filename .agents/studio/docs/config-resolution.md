# Configuration resolution

Run the existing helper explicitly from the resolved project root:

    bash .agents/studio/hooks/yaml-helper.sh resolve_config --keys rigor,automation,workflow,qa.level,review_mode,testing.strict,engine_values

Read one setting with resolve_setting; read raw YAML leaves with get_yaml_key. Inspect diagnostics even if an informational command returns 0. Do not introduce a second YAML parser or rely on source-host injected shell output.

Precedence: whitelisted local override, project YAML, legacy mirrors, rigor expansion for the six derived knobs, terminal defaults. New projects write only absent minimal rigor and guided automation. Existing explicit values win, including custom test/run commands and per-system workflow.

The system override key is the GDD filename stem; use a TR alias only as fallback. Validate orphan overrides at a gate where GDDs should exist, not while creating the first GDD. Invalid configuration or an orphan local file is an error rather than permission to invent defaults.

Schema 1 is retained. settings uses config-set.sh preview then an authorized write and readback. Stage writes use set-stage.sh. Reserved settings remain reported as reserved. See effects-map.md, workflow-modes.md and config-reference.md for individual settings.
