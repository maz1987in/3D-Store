from __future__ import annotations
"""Simple finite state machine utility for enforcing allowed status transitions.

Designed for lightweight lifecycle models (PrintJob, PurchaseOrder, RepairTicket).
Usage:
    from app.utils.fsm import TransitionValidator
    PRINT_FSM = TransitionValidator({
        'QUEUED': {'STARTED'},
        'STARTED': {'COMPLETED'},
        'COMPLETED': set(),
    })
    PRINT_FSM.assert_can_transition(current_status, target_status)

Raises 400 abort if invalid.
"""
from typing import Dict, Set
from flask import abort

class TransitionValidator:
    def __init__(self, graph: Dict[str, Set[str]], field_name: str = 'status'):
        self.graph = graph
        self.field_name = field_name

    def assert_can_transition(self, current: str, target: str):
        allowed = self.graph.get(current, set())
        if target not in allowed:
            abort(400, description=f"Invalid {self.field_name} transition {current} -> {target}")
        return True

__all__ = ['TransitionValidator']
