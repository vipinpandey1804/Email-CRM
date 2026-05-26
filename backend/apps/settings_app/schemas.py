from ninja import Schema


class SMTPConfigIn(Schema):
    host: str
    port: int = 587
    username: str = ''
    password: str = ''
    use_tls: bool = True
    use_ssl: bool = False


class SMTPConfigOut(Schema):
    host: str
    port: int
    username: str
    use_tls: bool
    use_ssl: bool
    is_verified: bool


class TestEmailIn(Schema):
    to_email: str


class AIKeyIn(Schema):
    openai_api_key: str
