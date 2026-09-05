"""
Test suite to certify that the old frontend has been completely eliminated
and the new AI Teacher Prototype frontend is served exclusively.
"""

import pytest
import re
from app import create_app
from app.config import Settings


@pytest.fixture
def client():
    settings = Settings.from_env()
    app = create_app(settings)
    app.config['TESTING'] = True
    return app.test_client()


def test_root_serves_new_prototype_frontend(client):
    """Asserts that GET / serves the compiled React/Vite prototype frontend."""
    res = client.get('/')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    
    # Assert presence of new prototype markers
    assert '<div id="root"></div>' in html
    assert 'Apurva AI Teacher' in html
    assert '/assets/' in html
    
    # Assert complete absence of old monolithic template markers
    assert 'PHASE 9' not in html
    assert 'bg-slate-950' not in html
    assert 'animate-talk' not in html
    assert 'animate-blink' not in html
    assert 'switchStage' not in html


def test_demo_route_serves_new_prototype_frontend(client):
    """Asserts that GET /demo serves the compiled React/Vite prototype frontend."""
    res = client.get('/demo')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert '<div id="root"></div>' in html
    assert 'PHASE 9' not in html


def test_static_assets_served_correctly(client):
    """Asserts that compiled JS and CSS bundles are served with HTTP 200."""
    res = client.get('/')
    html = res.data.decode('utf-8')
    
    # Find CSS and JS asset paths
    css_match = re.search(r'href="/assets/([^"]+\.css)"', html)
    js_match = re.search(r'src="/assets/([^"]+\.js)"', html)
    
    assert css_match is not None, 'CSS asset link not found in root HTML'
    assert js_match is not None, 'JS asset link not found in root HTML'
    
    css_res = client.get(f'/assets/{css_match.group(1)}')
    assert css_res.status_code == 200
    assert len(css_res.data) > 1000
    
    js_res = client.get(f'/assets/{js_match.group(1)}')
    assert js_res.status_code == 200
    assert len(js_res.data) > 1000


def test_spa_routes_serve_index(client):
    """Asserts that client-side SPA routes serve the application shell."""
    for route in ['/dashboard', '/lesson-player', '/create-lesson', '/learning-path', '/analytics', '/app']:
        res = client.get(route)
        assert res.status_code == 200
        assert b'<div id="root"></div>' in res.data


def test_diagnostics_endpoint_valid(client):
    """Asserts that /api/v1/diagnostics returns valid JSON report without leakage."""
    res = client.get('/api/v1/diagnostics')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, dict)
    assert data.get('success') is True
    assert 'diagnostics' in data
    assert 'gemini' in data['diagnostics']


def test_corrupted_svg_route_absent(client):
    """Asserts that corrupted/accidental 'svg' routes are not served."""
    res = client.get('/demosvg')
    assert res.status_code == 404

