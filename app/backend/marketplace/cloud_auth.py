"""Cloud Run IAM authentication alongside the gateway's scoped virtual key."""
import asyncio
import time
import httpx


class CloudRunAuth(httpx.Auth):
    def __init__(self, audience):
        self.audience = audience
        self.token = None
        self.refresh_at = 0
        self.lock = asyncio.Lock()

    async def async_auth_flow(self, request):
        async with self.lock:
            if self.token is None or time.monotonic() >= self.refresh_at:
                async with httpx.AsyncClient(timeout=5, trust_env=False) as metadata:
                    response = await metadata.get(
                        'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity',
                        headers={'Metadata-Flavor':'Google'},
                        params={'audience':self.audience,'format':'full'},
                    )
                    response.raise_for_status()
                    self.token = response.text.strip()
                    if not self.token:
                        raise RuntimeError('Cloud Run identity token unavailable')
                    # Metadata identity tokens last an hour; refresh well before expiry.
                    self.refresh_at = time.monotonic() + 3000
        request.headers['X-Serverless-Authorization'] = 'Bearer ' + self.token
        yield request
