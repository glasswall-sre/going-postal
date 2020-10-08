import pytest
from src.handlers.send import AttachmentRandomiser, parse_request_body

def test_attachment_randomiser_init():
    # Arrange
    attachment_randomiser = AttachmentRandomiser()
    # Act

    # Assert
    assert len(attachment_randomiser.files_loaded) == 0


# def test_load_all_attachments_to_memory():
#     # Arrange
#     attachment_randomiser = AttachmentRandomiser()
#     # Act
#     attachment_randomiser.load_all_attachments_to_memory()
#     # Assert
#     assert len(attachment_randomiser.files_loaded) == 18


# def test_import_distribution():
#     # Arrange
#     body = {
#         "endpoint":"localhost",
#         "port":25,
#         "tenant_ids":["test", "test2"],
#         "sender":"test@test.com",
#         "recipient":"test@test.com",
#         "load":{
#             "distribution" : [
#                 {
#                     "file": "data/test.png",
#                     "weight": 30.00
#                 },
#                 {
#                     "file": "data/test.png",
#                     "weight": 70.00
#                 }
#             ],
#             "attachment_count": [0, 100]
#         }
#     }
#     response = parse_request_body(body)
#     ar = AttachmentRandomiser()
#     # Act
#     ar.import_distribution(response.load.distribution)
#     # Assert
#     assert ar.total_weight == 100

# def test_select_random_attachment():
#     # Arrange
#     body = {
#         "endpoint":"localhost",
#         "port":25,
#         "tenant_ids":["test", "test2"],
#         "sender":"test@test.com",
#         "recipient":"test@test.com",
#         "load":{
#             "distribution" : [
#                 {
#                     "file": "data/test.png",
#                     "weight": 00.00
#                 },
#                 {
#                     "file": "data/test.bmp",
#                     "weight": 100.00
#                 }
#             ],
#             "attachment_count": [0, 100]
#         }
#     }
#     response = parse_request_body(body)
#     ar = AttachmentRandomiser()
#     ar.import_distribution(response.load.distribution)
#     # Act
#     selected = ar.select_random_attachment()
#     assert selected == "data/test.bmp"


# def test_parse_request_body():
#     # Arrange
#     body = {
#         "endpoint":"localhost",
#         "port":25,
#         "tenant_ids":["test", "test2"],
#         "sender":"test@test.com",
#         "recipient":"test@test.com",
#         "load":{
#             "distribution" : [
#                 {
#                     "file": "data/test.png",
#                     "weight": 30.00
#                 },
#                 {
#                     "file": "data/test.bmp",
#                     "weight": 70.00
#                 }
#             ],
#             "attachment_count": [0, 100]
#         }
#     }
#     # Act
#     response = parse_request_body(body)

#     # Assert
#     assert response.endpoint == "localhost"

# def test_import_attachment_count():
#     # Arrange
#     body = {
#         "endpoint":"localhost",
#         "port":25,
#         "tenant_ids":["test", "test2"],
#         "sender":"test@test.com",
#         "recipient":"test@test.com",
#         "load":{
#             "distribution" : [
#                 {
#                     "file": "data/test.png",
#                     "weight": 30.00
#                 },
#                 {
#                     "file": "data/test.bmp",
#                     "weight": 70.00
#                 }
#             ],
#             "attachment_count": [0, 100, 0]
#         }
#     }
#     response = parse_request_body(body)
#     ar = AttachmentRandomiser()
#     # Act
#     ar.import_distribution(response.load.distribution)
#     ar.import_attachment_weights(response.load.attachment_count)

#     count = ar.select_random_attachment_count()
#     # Assert
#     assert count == 1

# def test_import_attachment_count_2():
#     # Arrange
#     body = {
#         "endpoint":"localhost",
#         "port":25,
#         "tenant_ids":["test", "test2"],
#         "sender":"test@test.com",
#         "recipient":"test@test.com",
#         "load":{
#             "distribution" : [
#                 {
#                     "file": "data/test.png",
#                     "weight": 30.00
#                 },
#                 {
#                     "file": "data/test.bmp",
#                     "weight": 70.00
#                 }
#             ],
#             "attachment_count": [100, 0, 0]
#         }
#     }
#     response = parse_request_body(body)
#     ar = AttachmentRandomiser()
#     # Act
#     ar.import_distribution(response.load.distribution)
#     ar.import_attachment_weights(response.load.attachment_count)

#     count = ar.select_random_attachment_count()
#     # Assert
#     assert count == 0

# def test_import_attachment_count_3():
#     # Arrange
#     body = {
#         "endpoint":"localhost",
#         "port":25,
#         "tenant_ids":["test", "test2"],
#         "sender":"test@test.com",
#         "recipient":"test@test.com",
#         "load":{
#             "distribution" : [
#                 {
#                     "file": "data/test.png",
#                     "weight": 30.00
#                 },
#                 {
#                     "file": "data/test.bmp",
#                     "weight": 70.00
#                 }
#             ],
#             "attachment_count": [0, 0, 100]
#         }
#     }
#     response = parse_request_body(body)
#     ar = AttachmentRandomiser()
#     # Act
#     ar.import_distribution(response.load.distribution)
#     ar.import_attachment_weights(response.load.attachment_count)

#     count = ar.select_random_attachment_count()
#     # Assert
#     assert count == 2

# def test_10_attachments_equal_weight():
#     # Arrange
#     body = {
#         "endpoint":"localhost",
#         "port":25,
#         "tenant_ids":["test", "test2"],
#         "sender":"test@test.com",
#         "recipient":"test@test.com",
#         "load":{
#             "distribution" : [
#                 {
#                     "file": "data/test.bmp",
#                     "weight": 10.00
#                 },
#                 {
#                     "file": "data/test.doc",
#                     "weight": 10.00
#                 },
#                 {
#                     "file": "data/test.docx",
#                     "weight": 10.00
#                 },
#                 {
#                     "file": "data/test.emf",
#                     "weight": 10.00
#                 },
#                 {
#                     "file": "data/test.gif",
#                     "weight": 10.00
#                 },
#                 {
#                     "file": "data/test.jpg",
#                     "weight": 10.00
#                 },
#                 {
#                     "file": "data/test.mp3",
#                     "weight": 10.00
#                 },
#                 {
#                     "file": "data/test.mp4",
#                     "weight": 10.00
#                 },
#                 {
#                     "file": "data/test.mpg",
#                     "weight": 10.00
#                 },
#                 {
#                     "file": "data/test.pdf",
#                     "weight": 10.00
#                 }
#             ],
#             "attachment_count": [0, 0, 0, 0, 0 , 0, 0, 100]
#         }
#     }
#     req_body = parse_request_body(body)
#     ar = AttachmentRandomiser()
#     ar.import_distribution( req_body.load.distribution )
#     ar.import_attachment_weights(req_body.load.attachment_count)
#     sent_items = [

#     ]
#     attachments = []
#     for i in range( ar.select_random_attachment_count() ):
#         attachment = ar.select_random_attachment()
#         attachments.append( attachment )
#         sent_items.append({
#         })
#     assert 1 == 1 

def test_float_weights():
    # TODO
    assert 1 == 1