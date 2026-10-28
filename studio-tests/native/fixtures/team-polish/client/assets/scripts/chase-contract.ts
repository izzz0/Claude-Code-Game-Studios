// Isolated acceptance input: these are existing chase rules, not a runnable Cocos scene.
export const CHASE_RULES = Object.freeze({ captureDistance: 24, captureHoldMs: 300, durationMs: 60_000 });
export type ChaseRole = 'police' | 'thief';
export function settlement(captured: boolean, elapsedMs: number): ChaseRole | null {
  if (captured) return 'police';
  return elapsedMs >= CHASE_RULES.durationMs ? 'thief' : null;
}
