"""Central enum-like definitions to avoid typos in permission/service strings.
Extend cautiously; never rename codes silently—create new ones and deprecate old via migration if needed.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict

SERVICES = ['SALES', 'PRINT', 'ACC', 'INV', 'CAT', 'PO', 'RPR', 'RPT', 'ADMIN']

SERVICE_ACTIONS = {
    'SALES': ['READ', 'CREATE', 'UPDATE', 'DELETE', 'APPROVE', 'EXPORT'],
    'PRINT': ['READ', 'CREATE', 'UPDATE', 'DELETE', 'START', 'COMPLETE'],
    'ACC': ['READ', 'UPDATE', 'APPROVE', 'PAY', 'EXPORT'],
    'INV': ['READ', 'ADJUST', 'RECEIVE_PO'],
    'CAT': ['READ', 'MANAGE'],
    'PO': ['READ', 'CREATE', 'RECEIVE', 'CLOSE'],
    'RPR': ['READ', 'MANAGE'],
    'RPT': ['READ'],
    'ADMIN': ['USER.MANAGE', 'ROLE.MANAGE', 'GROUP.MANAGE', 'SETTINGS.MANAGE']
}


def build_all_permission_codes() -> List[str]:
    codes: List[str] = []
    for svc, actions in SERVICE_ACTIONS.items():
        for act in actions:
            codes.append(f"{svc}.{act}")
    return codes

ALL_PERMISSION_CODES = build_all_permission_codes()

ROLE_PRESETS: Dict[str, List[str]] = {
    'Seller': ['SALES.CREATE', 'SALES.READ', 'RPT.READ'],
    'Printer': ['PRINT.READ', 'PRINT.START', 'PRINT.COMPLETE', 'RPR.MANAGE', 'RPT.READ'],
    'Accounting': ['ACC.READ', 'ACC.UPDATE', 'ACC.APPROVE', 'ACC.PAY', 'ACC.EXPORT', 'RPT.READ'],
    # Manager: broad operational authority (READ + key transition actions across domains, excluding ADMIN)
    'Manager': [
        'SALES.READ','SALES.APPROVE','SALES.FULFILL','SALES.COMPLETE','SALES.CANCEL',
        'PRINT.READ','PRINT.START','PRINT.COMPLETE',
        'ACC.READ','ACC.APPROVE','ACC.PAY',
        'INV.READ','INV.ADJUST',
        'CAT.READ','CAT.MANAGE',
        'PO.READ','PO.RECEIVE','PO.CLOSE',
        'RPR.READ','RPR.MANAGE',
        'RPT.READ'
    ],
    'Owner': ['*']
}
