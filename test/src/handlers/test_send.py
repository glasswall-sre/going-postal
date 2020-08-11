import pytest
from src.handlers.send import AttachmentRandomiser, parse_request_body

def test_attachment_randomiser_init():
    # Arrange
    attachment_randomiser = AttachmentRandomiser()
    # Act

    # Assert
    assert len(attachment_randomiser.files_loaded) == 0


def test_load_all_attachments_to_memory():
    # Arrange
    attachment_randomiser = AttachmentRandomiser()
    # Act
    attachment_randomiser.load_all_attachments_to_memory()
    # Assert
    assert len(attachment_randomiser.files_loaded) == 5


def test_import_distribution():
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
            ],
            "attachment_count": [0, 100]
        }
    }
    response = parse_request_body(body)
    ar = AttachmentRandomiser()
    # Act
    ar.import_distribution(response.load.distribution)
    # Assert
    assert ar.total_weight == 100

def test_select_random_attachment():
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
                    "weight": 20.00
                },
                {
                    "file": "data/test.bmp",
                    "weight": 80.00
                }
            ],
            "attachment_count": [0, 100]
        }
    }
    response = parse_request_body(body)
    ar = AttachmentRandomiser()
    ar.import_distribution(response.load.distribution)
    # Act
    selected = {}
    for i in range(100):
        attachment = ar.select_random_attachment()

        if not attachment in selected:
            selected[attachment] = 0

        selected[attachment] += 1
    # Assert
    if selected["data/test.png"] == None:
        selected["data/test.png"] = 0
    assert selected.get("data/test.png") < selected.get("data/test.bmp")


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
            ],
            "attachment_count": [0, 100]
        }
    }
    # Act
    response = parse_request_body(body)

    # Assert
    assert response.endpoint == "localhost"

def test_import_attachment_count():
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
            ],
            "attachment_count": [0, 100, 0]
        }
    }
    response = parse_request_body(body)
    ar = AttachmentRandomiser()
    # Act
    ar.import_distribution(response.load.distribution)
    ar.import_attachment_weights(response.load.attachment_count)

    count = ar.select_random_attachment_count()
    # Assert
    assert count == 1

def test_import_attachment_count_2():
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
            ],
            "attachment_count": [100, 0, 0]
        }
    }
    response = parse_request_body(body)
    ar = AttachmentRandomiser()
    # Act
    ar.import_distribution(response.load.distribution)
    ar.import_attachment_weights(response.load.attachment_count)

    count = ar.select_random_attachment_count()
    # Assert
    assert count == 0

def test_import_attachment_count_3():
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
            ],
            "attachment_count": [0, 0, 100]
        }
    }
    response = parse_request_body(body)
    ar = AttachmentRandomiser()
    # Act
    ar.import_distribution(response.load.distribution)
    ar.import_attachment_weights(response.load.attachment_count)

    count = ar.select_random_attachment_count()
    # Assert
    assert count == 2