# going-postal
An Azure function with a HTTP trigger for sending email to an SMTP endpoint, 
to be used with concurrency for load testing.

## Documentation

### `/send`

#### Methods 
`POST`

#### Body
```json
{
    "endpoint": "smtp.some-endpoint.com",
    "port": 25,
    "timeout": 3.5,
    "tenant_id": ["f45af6e4-4206-4e5b-8675-d4852a158dbf"],
    "recipient": "someone@example.com",
    "sender": "someone_else@example.com",
    "load": {
        "distribution" : [
            {
                "file": "data/test.png",
                "weight": 10.00
            },
            {
                "file": "data/test.bmp",
                "weight": 90.00
            }
        ],
        "attachment_count": [25, 70, 5] //Position in index represents attachment count
    }
}
```
All fields are required, with the exception of:
- `port`, which defaults to `25` if not specified.
- `timeout`, which defaults to `null` if not specified.



#### Responses
- `200`: if email successfully sent to endpoint.
- `400`: if request body not present or malformed.
- `500`: if there was a general error in the function.
- `502`: if there was some error sending the email to the SMTP endpoint.

## Development

### Requirements
- Serverless framework
- Python 3.8
- Pipenv

### Quick start
1. Clone this repo.
2. Set up your pipenv by running `pipenv sync --dev`.
3. Launch the function with `pipenv run serverless offline --region uksouth --azure_storage_connection_string $AZURE_STORAGE_CONNECTION_STRING`.
4. Edit the code and test. I use [HTTPie](https://httpie.org/) for making requests.
5. In order to have something to test with, you can run a postfix blackhole mail server on port 25 using Docker, with: `docker run --name blackhole -d -p 25:25 simap/smtpblackhole`.
6. Now, using HTTPie to make a request to the locally running function: `http post http://localhost:7071/api/send endpoint=localhost port=25 tenant_id=test sender=test@test.com recipient=test@test.com`.
7. You should get back something like this:
   ```
   HTTP/1.1 200 OK
   Content-Type: text/plain; charset=utf-8
   Date: Tue, 30 Jun 2020 13:51:51 GMT
   Server: Kestrel
   Transfer-Encoding: chunked
   
   Successfully sent to 'localhost:25'
   ```
