import sys, pathlib, pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.openapi_clean import ACTION_REGISTRY  # type: ignore
from app.constants.permissions import ROLE_PRESETS  # type: ignore


def test_action_permissions_exist_in_some_role():
    # Collect permissions listed in registry
    perms = set()
    for actions in ACTION_REGISTRY.values():
        for a in actions:
            perms.add(a['permission'])
    # Roles (exclude wildcard Owner)
    role_map = {r: set(p for p in codes if p != '*') for r, codes in ROLE_PRESETS.items() if r != 'Owner'}
    all_role_perms = set().union(*role_map.values()) if role_map else set()

    missing = sorted([p for p in perms if p not in all_role_perms])
    assert not missing, f"Action permissions not present in any concrete role: {missing}"
