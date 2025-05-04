# tests/test_handler.py
import json
import pytest
from lambda import handler

from unittest.mock import patch, MagicMock

@pytest.fixture
def sample_event_get():
    return {
        "requestContext": {"http": {"method": "GET"}}
    }

@pytest.fixture
def sample_event_post():
    return {
        "requestContext": {"http": {"method": "POST"}},
        "body": json.dumps({
            "label": "root",
            "parentId": None
        })
    }

@patch("lambda.handler.redis_client")
@patch("lambda.handler.table")
def test_get_cached_tree(mock_table, mock_redis, sample_event_get):
    # Redis has the cached tree
    mock_redis.get.return_value = json.dumps([{"id": "1", "label": "root", "children": []}])

    response = handler.lambda_handler(sample_event_get, None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"])[0]["label"] == "root"
    mock_redis.get.assert_called_with("tree")
    mock_table.scan.assert_not_called()  # should not hit DynamoDB if cached

@patch("lambda.handler.redis_client")
@patch("lambda.handler.table")
def test_post_and_invalidate_cache(mock_table, mock_redis, sample_event_post):
    response = handler.lambda_handler(sample_event_post, None)

    assert response["statusCode"] == 200
    assert "message" in json.loads(response["body"])
    mock_table.put_item.assert_called_once()
    mock_redis.delete.assert_called_with("tree")
