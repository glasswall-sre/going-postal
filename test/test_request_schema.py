import pytest
from src.handlers.send import parse_request_body

def test_parse_request_body():
    # Arrange
    body = {
        "endpoint":"localhost",
        "port":25,
        "tenant_ids":["test", "test2"],
        "sender":"test@test.com",
        "recipient":"test@test.com",
        "load":{
            "distribution" : [
                {
                    "file": "data/test.png",
                    "weight": 30.00
                },
                {
                    "file": "data/test.png",
                    "weight": 70.00
                }
            ]
        }
    }
    # Act
    response = parse_request_body(body)

    # Assert
    assert response.endpoint == "localhost"