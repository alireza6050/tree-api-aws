import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import pytest
from tree_lambda import handler

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
@patch("tree_lambda.handler.get_redis_client")
@patch("tree_lambda.handler.get_table")
def test_get_cached_tree(mock_table_fn, mock_redis_fn, sample_event_get):
    mock_table = MagicMock()
    mock_redis = MagicMock()
    mock_table_fn.return_value = mock_table
    mock_redis_fn.return_value = mock_redis

    # Redis has the cached tree
    mock_redis.get.return_value = json.dumps([{"id": "1", "label": "root", "children": []}])

    response = handler.lambda_handler(sample_event_get, None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"])[0]["label"] == "root"
    mock_redis.get.assert_called_with("tree")
    mock_table.scan.assert_not_called()


@patch("tree_lambda.handler.get_redis_client")
@patch("tree_lambda.handler.get_table")
def test_post_and_invalidate_cache(mock_table_fn, mock_redis_fn, sample_event_post):
    mock_table = MagicMock()
    mock_redis = MagicMock()
    mock_table_fn.return_value = mock_table
    mock_redis_fn.return_value = mock_redis

    response = handler.lambda_handler(sample_event_post, None)

    assert response["statusCode"] == 200
    assert "message" in json.loads(response["body"])
    mock_table.put_item.assert_called_once()
    mock_redis.delete.assert_called_with("tree")


@patch("tree_lambda.handler.get_redis_client")
@patch("tree_lambda.handler.get_table")
def test_get_from_dynamo_if_not_cached(mock_table_fn, mock_redis_fn, sample_event_get):
    mock_table = MagicMock()
    mock_redis = MagicMock()
    mock_table_fn.return_value = mock_table
    mock_redis_fn.return_value = mock_redis

    mock_redis.get.return_value = None
    mock_table.scan.return_value = {"Items": [{"id": "1", "label": "root", "parentId": None}]}

    response = handler.lambda_handler(sample_event_get, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert isinstance(body, list)
    assert body[0]["label"] == "root"
    mock_redis.set.assert_called_once()
    mock_table.scan.assert_called_once()