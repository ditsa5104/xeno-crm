import os


class Settings:
    CHANNEL_STUB_SECRET: str = os.environ.get('CHANNEL_STUB_SECRET', 'dev-stub-secret')
    CRM_WEBHOOK_URL: str = os.environ.get('CRM_WEBHOOK_URL', 'http://crm:8000/api/v1/webhooks/channel-event/')


settings = Settings()
