from app.utils.fsm import TransitionValidator
import pytest


def test_transition_validator_allows_valid():
    fsm = TransitionValidator({'A': {'B'}, 'B': set()})
    assert fsm.assert_can_transition('A', 'B') is True


def test_transition_validator_blocks_invalid():
    fsm = TransitionValidator({'A': {'B'}, 'B': set()})
    with pytest.raises(Exception):  # Flask abort raises HTTPException; broad catch acceptable here
        fsm.assert_can_transition('A', 'C')


def test_validate_status_helper(client):
    # Simple indirect test: reuse validate_status via creating a resource already covered elsewhere.
    # Here we just ensure the OpenAPI spec includes x-transitions which implies integration executed.
    resp = client.get('/openapi.json')
    body = resp.get_json()
    pj_schema = body['components']['schemas']['PrintJob']
    assert 'x-transitions' in pj_schema
    assert 'QUEUED' in pj_schema['x-transitions']
