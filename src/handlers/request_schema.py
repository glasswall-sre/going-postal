from typing import List, Any
from marshmallow import Schema, fields, post_load, EXCLUDE, ValidationError, validate
from sremail import address

class Disitribution:
    def __init__(self, file: str, weight: float):
        self.file = file
        self.weight = weight


class Load:
    def __init__(self, distribution: str):
        self.distribution = distribution


class RequestBody:
    """The body of a request to the send endpoint.

    Attributes:
        endpoint (str): The SMTP endpoint to send to.
        port (int): The port to send the SMTP message over.
        timeout (float): The timeout of the SMTP connection.
        tenant_ids (List[str]): The list of tenant ID/s of the SaaS tenant/s.
        recipient (Address): The email to send to.
        sender (Address): The email to send from.
    """
    def __init__(self, endpoint: str, port: int, timeout: float,
                 tenant_ids: List[str], recipient: address.Address,
                 sender: address.Address, load: Load) -> None:
        self.endpoint = endpoint
        self.port = port
        self.timeout = timeout
        self.tenant_ids = tenant_ids
        self.recipient = recipient
        self.sender = sender
        self.load = load


class DisitributionSchema(Schema):
    file = fields.Str(required=True)
    weight = fields.Float(required=True)

    @post_load
    def make_request_body(self, data, **kwargs):
        return Disitribution(**data)


class LoadSchema(Schema):
    distribution = fields.List(fields.Nested( DisitributionSchema))

    @post_load
    def make_request_body(self, data, **kwargs):
        return Load(**data)


class RequestBodySchema(Schema):
    """Marshmallow schema for creating/validating a RequestBody."""
    endpoint = fields.Str(required=True, allow_none=False)
    port = fields.Int(required=False, missing=25, default=25, allow_none=False)
    timeout = fields.Float(
        required=False,
        missing=None,
        default=None,
        allow_nan=False,
    )
    tenant_ids = fields.List(fields.Str(required=True), allow_none=False, validate=validate.Length(min=1))
    recipient = address.AddressField(required=True, allow_none=False)
    sender = address.AddressField(required=True, allow_none=False)
    load = fields.Nested(LoadSchema, required=True, allow_none=False)

    @post_load
    def make_request_body(self, data, **kwargs) -> RequestBody:
        return RequestBody(**data)


REQUEST_BODY_SCHEMA = RequestBodySchema(unknown=EXCLUDE)


def parse_request_body(body: Any) -> RequestBody:
    """Parse raw request data into a RequestBody."""
    return REQUEST_BODY_SCHEMA.load(body)
