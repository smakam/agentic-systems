import unittest
from unittest.mock import patch
import httpx2 as httpx
from marketplace.cloud_auth import CloudRunAuth


class CloudAuthTests(unittest.IsolatedAsyncioTestCase):
    async def test_iam_header_preserves_gateway_key_and_reuses_token(self):
        calls=[]
        async def metadata(request):
            calls.append(request)
            self.assertEqual(request.headers['Metadata-Flavor'],'Google')
            self.assertEqual(request.url.params['audience'],'https://gateway.example')
            return httpx.Response(200,text='synthetic-identity-token')
        original=httpx.AsyncClient
        def metadata_client(**kwargs):
            return original(transport=httpx.MockTransport(metadata),**kwargs)
        auth=CloudRunAuth('https://gateway.example')
        with patch('marketplace.cloud_auth.httpx.AsyncClient',side_effect=metadata_client):
            for _ in range(2):
                request=httpx.Request('POST','https://gateway.example/v1/chat/completions',headers={'Authorization':'Bearer synthetic-scoped-key'})
                flow=auth.async_auth_flow(request)
                forwarded=await anext(flow)
                self.assertEqual(forwarded.headers['Authorization'],'Bearer synthetic-scoped-key')
                self.assertEqual(forwarded.headers['X-Serverless-Authorization'],'Bearer synthetic-identity-token')
                await flow.aclose()
        self.assertEqual(len(calls),1)

    async def test_pinned_openai_sdk_accepts_cloud_auth(self):
        from openai import DefaultAsyncHttpxClient
        client = DefaultAsyncHttpxClient(auth=CloudRunAuth('https://gateway.example'))
        await client.aclose()

    async def test_metadata_failure_does_not_forward_request(self):
        original=httpx.AsyncClient
        def metadata_client(**kwargs):
            return original(transport=httpx.MockTransport(lambda request:httpx.Response(403)),**kwargs)
        with patch('marketplace.cloud_auth.httpx.AsyncClient',side_effect=metadata_client):
            flow=CloudRunAuth('https://gateway.example').async_auth_flow(httpx.Request('POST','https://gateway.example'))
            with self.assertRaises(httpx.HTTPStatusError):
                await anext(flow)
