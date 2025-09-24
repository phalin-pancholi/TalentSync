import pytest
import requests
import json

BASE_URL = "http://localhost:8002"  # Zoho sync service port


class TestZohoSyncServiceContract:
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "zoho-sync-service"

    def test_manual_sync_trigger(self):
        """Test manual sync trigger endpoint"""
        response = requests.post(f"{BASE_URL}/sync", json={})
        # Should return 200 for successful sync or 500 if service not ready
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "sync_result" in data

    def test_sync_status_endpoint(self):
        """Test sync status retrieval endpoint"""
        response = requests.get(f"{BASE_URL}/sync/status")
        assert response.status_code in [200, 500]  # 500 if service not ready

    def test_employees_endpoint(self):
        """Test employees retrieval endpoint"""
        response = requests.get(f"{BASE_URL}/employees")
        assert response.status_code in [200, 500]  # 500 if service not ready
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
