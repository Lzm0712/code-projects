"""
ECC Loop — Goal Freeze (Best Practice #2: 保持规格不变)

Prevents scope creep mid-loop by freezing the goal specification.
"""
from ecc_loop import seed

FROZEN_KEY = "_frozen_goal"


def freeze(goal: str, seed_path: str = "~/.hermes/ecc-loop-seed.json") -> str:
    """Freeze the current goal. Returns the frozen goal hash."""
    import hashlib
    state = seed.load_seed(seed_path)
    goal_hash = hashlib.sha256(goal.encode()).hexdigest()[:12]
    state[FROZEN_KEY] = {"goal": goal, "hash": goal_hash}
    seed.save_seed(state, seed_path)
    return goal_hash


def check(goal: str, seed_path: str = "~/.hermes/ecc-loop-seed.json") -> bool:
    """Check if a goal matches the frozen spec. Returns True if match or no freeze."""
    import hashlib
    state = seed.load_seed(seed_path)
    frozen = state.get(FROZEN_KEY)
    if not frozen:
        return True  # No freeze — allow anything
    goal_hash = hashlib.sha256(goal.encode()).hexdigest()[:12]
    return goal_hash == frozen["hash"]


def unfreeze(seed_path: str = "~/.hermes/ecc-loop-seed.json") -> None:
    """Remove the goal freeze."""
    state = seed.load_seed(seed_path)
    if FROZEN_KEY in state:
        del state[FROZEN_KEY]
        seed.save_seed(state, seed_path)
