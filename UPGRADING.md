# Upgrading the Codex template

The full migration extends core commit bcc5607 and fixes the upstream source
baseline at 05ad7c8. Skills remain repository-local under .agents/skills/ with
ccgs- names. Configuration stays schema 1; existing project/local values are
preserved rather than seeded from new defaults.

Use Git to review and merge template changes into an existing project. Do not
copy project.yaml over a configured game or overwrite existing stories, IDs,
engine references or evidence. New projects initialize only absent rigor and
automation defaults. Original reserved settings remain reserved.

Project-local profiles and hooks are new native resources. Review hook
definitions in the host after updating; do not bypass trust or install them
globally. Parent model/provider/permissions remain inherited.

Run framework checks, then the affected native and engine acceptance cases.
Existing game evidence is reusable only when its inputs and affected acceptance
criteria remain current. A passing structure check alone is not a migration
acceptance result.
