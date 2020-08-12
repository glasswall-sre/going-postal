from datetime import datetime
from email.message import EmailMessage
import logging
import aiosmtplib
import azure.functions as func
from sremail import message, address
# Subject Generator 
import uuid
# Schema
from typing import List, Any
from marshmallow import Schema, fields, post_load, EXCLUDE, ValidationError, validate
from sremail import address
# Attachment Randomiser
import os
import random


# Schema--------------------------------------------------------------------
class Disitribution:
    def __init__(self, file: str, weight: float):
        self.file = file
        self.weight = weight

class Load:
    def __init__(self, distribution: str, attachment_count):
        self.distribution = distribution
        self.attachment_count = attachment_count

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
    attachment_count = fields.List(fields.Int())

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


DATA_DIRECTORY = "data"

# Attachment_Randomiser ------------------------------------------------
class AttachmentRandomiser:
    def __init__(self):
        self.attachments_sent = 0
        self.files_loaded = []
        self.total_weight = 0
        self.distribution = None
        # Currently Selected
        self.curr_selected = None
        self.curr_selected_size = None
        # Attachment Count
        self.attachment_count = []
        self.attachment_count_total_weight = 0
        self.curr_selected_attachment_count = None
        # Private
        self.__running_total_file_weight = 0
        self.__running_total_attach_count_weight = 0


    def load_all_attachments_to_memory(self):
        # Load Everything from data
        result = os.path.isdir(DATA_DIRECTORY)
        if result == True:
            items = os.listdir(DATA_DIRECTORY)
            self.files_loaded = items
        else:
            raise OSError("data directory not found")

    def import_distribution(self, distribution: List[Disitribution]):
        self.distribution = distribution
        for item in distribution:
            self.total_weight += item.weight
            file_info = {
                'name': item.file,
                'size': os.path.getsize(item.file)
            }
            self.files_loaded.append(file_info)

    def import_attachment_weights(self, attachment_count_weights: List[int]):
        self.attachment_count = attachment_count_weights
        total = 0
        for item in attachment_count_weights:
            total += item
        self.attachment_count_total_weight = total

    def select_random_attachment_count(self) -> int:
        if self.curr_selected_attachment_count == None:
            self.curr_selected_attachment_count = self.attachment_count[0]
        self.__running_total_attach_count_weight = self.__running_total_attach_count_weight
        i = 0
        for item in self.attachment_count:
            r = random.randint(0, self.__running_total_attach_count_weight + item)
            if r >= self.__running_total_attach_count_weight:
                self.curr_selected_attachment_count = i
            self.__running_total_attach_count_weight += item
            i += 1
        return self.curr_selected_attachment_count


    def select_random_attachment(self) -> str:
        if self.curr_selected == None:
            self.curr_selected = self.files_loaded[0]['name']
        self.__running_total_file_weight = self.__running_total_file_weight
        for item in self.distribution:
            r = random.randint(0, self.__running_total_file_weight + item.weight )
            if r >= self.__running_total_file_weight:
                self.curr_selected = item.file
            self.__running_total_file_weight += item.weight
        self.curr_selected_size = [x for x in self.files_loaded if x['name'] == self.curr_selected][0]['size']
        return self.curr_selected


def generate_subject():
    return f"{uuid.uuid4()} -- {datetime.now()}"


def create_email_message(tenant_id: str,
                         sender: str,
                         recipient: str,
                         attachments: List[str]) -> EmailMessage:
    """Create the email message to send."""
    msg = message.Message("This is a test email",
                          to=[recipient],
                          from_addresses=[sender],
                          date=datetime.now())

    for attachment in attachments:
        msg.attach(attachment)

    msg.headers["X-FileTrust-Tenant"] = tenant_id
    return msg.as_mime()


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

    # Select Attachment
    ar = AttachmentRandomiser()
    ar.import_distribution( req_body.load.distribution )
    ar.import_attachment_weights(req_body.load.attachment_count)
    attachments = []
    for i in range( ar.select_random_attachment_count() ):
        attachment = ar.select_random_attachment()
        attachments.append( attachment )
        logging.info(f"Attaching file... {attachment} at size... {ar.curr_selected_size}")

    
    for tenant_id in req_body.tenant_ids:
        logging.info(f"Creating email to send to {tenant_id}...")
        msg_to_send = create_email_message(tenant_id,
                                        req_body.sender.email,
                                        req_body.recipient.email,
                                        attachments)

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







