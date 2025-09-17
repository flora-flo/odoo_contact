# config.py
TEST_CONFIG = {
    "base_url": "https://healio-test.ddns.net/",
    "headless": True,
    "timeout": 10,
    "invalid_emails": [
        "wrong@example.com",
        "invalid.email",
        "test@test",
        "admin",
        ""
    ],
    "invalid_passwords": [
        "wrongpass",
        "",
        "123456",
        "password"
    ]
}