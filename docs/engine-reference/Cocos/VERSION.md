# Cocos Creator 3.8.8

This reference is pinned to the authorized Cocos Creator release. The version
must still be recorded in the project's `project.yaml`; this snapshot does not
prove that an editor or license is installed.

## Project roots

Creator projects keep authored TypeScript below `assets/scripts`. In a client
package the equivalent root is `client/assets/scripts`. A Cocos adapter resolves
these only from the package's `creator.version` metadata. Monorepos may also
expose the authoritative `packages/core/src`, `packages/protocol/src`, and
`server/src` roots when those directories exist.

## Test evidence

The studio adapter accepts an explicit Node/TAP command and recognizes TAP test
points, plans, `SKIP`, `TODO`, and cancellation markers. A process exit of zero
without a fresh recognized report is not test evidence.
