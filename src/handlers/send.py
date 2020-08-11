from datetime import datetime
from email.message import EmailMessage
import logging
import aiosmtplib
import azure.functions as func
from sremail import message, address
from src.handlers.request_schema import parse_request_body
from src.handlers.attachment_randomiser import AttachmentRandomiser


def create_email_message(tenant_id: str,
                         sender: str,
                         recipient: str,
                         attachment_randomiser: AttachmentRandomiser) -> EmailMessage:
    """Create the email message to send."""
    msg = message.Message("This is a test email",
                          to=[recipient],
                          from_addresses=[sender],
                          date=datetime.now()).attach(attachment_randomiser.select_random_attachment())
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

    for tenant_id in req_body.tenant_ids:
        logging.info(f"Creating email to send to {tenant_id}...")
        msg_to_send = create_email_message(tenant_id,
                                        req_body.sender.email,
                                        req_body.recipient.email,
                                        ar)

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
