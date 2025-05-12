# TodoApp

## run tests

python -m pytest

## Authentication OAuth

### curl authenticate
curl -X POST localhost:8000/auth/token \
  -d "username=johndoe" \
  -d "password=secret"

### curl response:
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzQ2ODczMjIyfQ.Ee2qX4TBb9I9E8XjqOpbEIja2nQI_YYRlpg036odVqA","token_type":"bearer"}


### query http endpoints with authenticated token
curl -X GET http://127.0.0.1:8000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwiZXhwIjoxNzQ2ODczMjIyfQ.Ee2qX4TBb9I9E8XjqOpbEIja2nQI_YYRlpg036odVqA"

