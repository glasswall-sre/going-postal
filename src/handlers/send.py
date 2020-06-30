from datetime import datetime
from email.message import EmailMessage
import logging
from typing import Any, Optional

import aiosmtplib
import azure.functions as func
from marshmallow import Schema, fields, post_load, EXCLUDE, ValidationError
from sremail import message


class RequestBody:
    """The body of a request to the send endpoint.

    Attributes:
        endpoint (str): The SMTP endpoint to send to.
        port (int): The port to send the SMTP message over.
        timeout (float): The timeout of the SMTP connection.
        tenant_id (str): The tenant ID of the SaaS tenant.
        recipient (str): The email to send to.
        sender (str): The email to send from.
    """
    def __init__(self, endpoint: str, port: int, timeout: float,
                 tenant_id: str, recipient: str, sender: str) -> None:
        self.endpoint = endpoint
        self.port = port
        self.timeout = timeout
        self.tenant_id = tenant_id
        self.recipient = recipient
        self.sender = sender


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
    tenant_id = fields.Str(required=True, allow_none=False)
    recipient = fields.Str(required=True, allow_none=False)
    sender = fields.Str(required=True, allow_none=False)

    @post_load
    def make_request_body(self, data, **kwargs) -> RequestBody:
        return RequestBody(**data)


REQUEST_BODY_SCHEMA = RequestBodySchema(unknown=EXCLUDE)


def parse_request_body(body: Any) -> RequestBody:
    """Parse raw request data into a RequestBody."""
    return REQUEST_BODY_SCHEMA.load(body)


def create_email_message(tenant_id: str, sender: str,
                         recipient: str) -> EmailMessage:
    """Create the email message to send."""
    msg = message.Message("This is a test email",
                          to=[recipient],
                          from_addresses=[sender],
                          date=datetime.now()).attach("data/test.png")
    msg.headers["X-FileTrust-Tenant"] = tenant_id
    return msg.as_mime()


def set_tenant_id(tenant_id: str, msg: EmailMessage) -> None:
    """Set the FileTrust tenant ID of an email message."""
    msg["X-FileTrust-Tenant"] = tenant_id


async def main(req: func.HttpRequest) -> func.HttpResponse:
    """Entry point of the Azure function."""
    logging.info('Python HTTP trigger function processed a request.')

    # parse the request body
    try:
        req_body = req.get_json()
        req_body = parse_request_body(req_body)
    except ValidationError as err:
        # construct a string containing all validation error messages
        invalid_fields = ", ".join([
            f"{field_name}: {err_msgs}"
            for field_name, err_msgs in err.messages.items()
        ])
        err_string = f"Malformed request: {invalid_fields}"
        return func.HttpResponse(err_string, status_code=400)
    except ValueError as err:
        return func.HttpResponse(
            "Malformed request: please supply a JSON "
            "body containing an SMTP endpoint and tenant ID",
            status_code=400)

    logging.info("Opening SMTP connection to endpoint '%s:%d'",
                 req_body.endpoint, req_body.port)
    smtp_conn = aiosmtplib.SMTP(req_body.endpoint,
                                port=req_body.port,
                                timeout=req_body.timeout)
    try:
        await smtp_conn.connect()
    except Exception as err:
        # if there was some error connecting, return a 502 bad gateway
        return func.HttpResponse(str(err), status_code=502)

    logging.info("Creating email to send...")
    msg_to_send = create_email_message(req_body.tenant_id, req_body.sender,
                                       req_body.recipient)
    set_tenant_id(req_body.tenant_id, msg_to_send)

    logging.info("Sending email to endpoint '%s:%d'...", req_body.endpoint,
                 req_body.port)
    try:
        await smtp_conn.send_message(msg_to_send)
    except Exception as err:
        # if there was some error sending, return a 502 bad gateway
        return func.HttpResponse(str(err), status_code=502)

    # sending the message was a success!
    return func.HttpResponse(
        f"Successfully sent to '{req_body.endpoint}:{req_body.port}'",
        status_code=200)
