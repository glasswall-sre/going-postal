import uuid
import datetime

def generate_subject():
    return f"{uuid.uuid4()} -- {datetime.datetime.now()}"