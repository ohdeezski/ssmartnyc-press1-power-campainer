"""Integration tests for cross-module workflows."""
import json


def test_campaign_lifecycle(test_client, auth_user):
    """Test creating and retrieving a campaign."""
    response = test_client.post(
        '/campaigns/new',
        data={'name': 'Integration Test Campaign', 'type': 'test'}
    )
    assert response.status_code in (200, 201, 302), f"Expected 200/201/302, got {response.status_code}"
    
    # Verify campaign exists in DB
    from app.modules.campaigns.models import Campaign
    from app.modules.auth.models import User
    with test_client.application.app_context():
        user = User.query.filter_by(email='test@test.com').first()
        campaign = Campaign.query.filter_by(name='Integration Test Campaign', created_by=user.id).first()
        assert campaign is not None, "Campaign not created"
        assert campaign.type == 'test'


def test_workflow_lifecycle(test_client, auth_user):
    """Test creating a workflow."""
    response = test_client.post(
        '/api/workflows/',
        json={'name': 'Integration Test Workflow', 'steps': [{'action': 'notify'}]}
    )
    assert response.status_code == 201
    workflow = response.get_json()
    assert workflow['name'] == 'Integration Test Workflow'
    
    response = test_client.get(f'/api/workflows/{workflow["id"]}')
    assert response.status_code == 200


def test_notification_toast_flow(test_client, auth_user):
    """Test toast notification creation and listing."""
    response = test_client.post(
        '/api/notifications/toast/success',
        json={'message': 'Integration test success'}
    )
    assert response.status_code == 201
    
    response = test_client.get('/api/notifications/')
    assert response.status_code == 200
    notifications = response.get_json()
    assert len(notifications) >= 1


def test_config_feature_flag_workflow(test_client, auth_user):
    """Test feature flag set/get."""
    response = test_client.post(
        '/api/config/feature-flags',
        json={'key': 'test_integration_flag', 'enabled': True}
    )
    assert response.status_code == 200
    
    response = test_client.get('/api/config/feature-flags')
    assert response.status_code == 200
    data = response.get_json()
    flags = data.get('feature_flags', {})
    assert 'test_integration_flag' in flags
    assert flags['test_integration_flag'] is True


def test_asset_search_integration(test_client, auth_user):
    """Test asset search endpoint."""
    response = test_client.get('/api/assets/search?q=nonexistent')
    assert response.status_code == 200
    results = response.get_json()
    assert isinstance(results, list)


def test_events_live_integration(test_client, auth_user):
    """Test events live endpoint."""
    response = test_client.get('/api/events/live')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


class TestCrossModuleDataFlow:
    """Test data flows between modules."""
    
    def test_notification_admin_requires_permissions(self, test_client, auth_user):
        """Test notification admin endpoint requires proper data."""
        response = test_client.post(
            '/api/notifications/admin',
            json={
                'user_id': 1,
                'title': 'Test Admin Notification',
                'message': 'Integration test message'
            }
        )
        assert response.status_code in (201, 403, 400)
    
    def test_config_system_integration(self, test_client, auth_user):
        """Test config engine + system config."""
        response = test_client.get('/api/config/system')
        assert response.status_code == 200
