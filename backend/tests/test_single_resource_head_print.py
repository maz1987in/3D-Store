from app import create_app
import pytest

@pytest.fixture(scope='module')
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

# Assuming fixtures / seeds create at least one print job; if not adjust by creating one.

def _first_job_id(client):
    resp = client.get('/print/jobs')
    if resp.status_code != 200:
        pytest.skip('print jobs endpoint unavailable')
    data = resp.get_json().get('data', [])
    if not data:
        pytest.skip('no print jobs to test head on')
    return data[0]['id']

def test_head_print_job_resource(client):
    job_id = _first_job_id(client)
    # Initial HEAD
    h = client.head(f'/print/jobs/{job_id}')
    assert h.status_code == 200
    etag = h.headers.get('ETag')
    last_mod = h.headers.get('Last-Modified')
    assert etag and last_mod
    # Conditional
    h2 = client.head(f'/print/jobs/{job_id}', headers={'If-None-Match': etag})
    assert h2.status_code == 304
    # GET with same validators returns body
    g = client.get(f'/print/jobs/{job_id}', headers={'If-None-Match': '"different"'})
    assert g.status_code == 200
    assert g.is_json
