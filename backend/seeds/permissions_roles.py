"""Seed definitions for permissions & role composition.
(Not an executable script yet – used as a single source of truth.)
"""

# Permission groups by service
PERMISSIONS = {
    'SALES': ['READ', 'CREATE', 'UPDATE', 'DELETE', 'APPROVE', 'EXPORT'],
    'PRINT': ['READ', 'CREATE', 'UPDATE', 'DELETE', 'START', 'COMPLETE'],
    'ACC': ['READ', 'UPDATE', 'APPROVE', 'PAY', 'EXPORT'],
    'INV': ['READ', 'ADJUST', 'RECEIVE_PO'],
    'CAT': ['READ', 'MANAGE'],
    'PO': ['READ', 'CREATE', 'RECEIVE', 'CLOSE', 'VENDOR.READ', 'VENDOR.CREATE', 'VENDOR.UPDATE', 'VENDOR.ACTIVATE', 'VENDOR.DEACTIVATE'],
    'RPR': ['READ', 'MANAGE'],
    'RPT': ['READ'],
    'ADMIN': ['USER.MANAGE', 'ROLE.MANAGE', 'GROUP.MANAGE', 'SETTINGS.MANAGE']
}

# Role → explicit permission codes
ROLES = {
    'Seller': ['SALES.CREATE', 'SALES.READ', 'RPT.READ'],
    'Printer': ['PRINT.READ', 'PRINT.START', 'PRINT.COMPLETE', 'RPR.MANAGE', 'RPT.READ'],
    'Accounting': ['ACC.READ', 'ACC.UPDATE', 'ACC.APPROVE', 'ACC.PAY', 'ACC.EXPORT', 'RPT.READ'],
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
    'Owner': ['*']  # implies all
}
