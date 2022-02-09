import json

import aiohttp as aiohttp

from dydx3.errors import DydxApiError
from dydx3.helpers.request_helpers import remove_nones

# TODO: Use a separate session per client instance.
core_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'dydx/python',
}


class DyDxSession():

    def __init__(self, session: aiohttp.ClientSession = None):
        self.session = session
        self.self_created = False

    async def get_session(self):
        if self.session is None:
            self.self_created = True
            connector = aiohttp.TCPConnector(enable_cleanup_closed=True)
            self.session = aiohttp.ClientSession(connector=connector)
        return self.session

    async def close(self):
        if self.self_created:
            await self.session.close()


class Response(object):
    def __init__(self, data={}, headers=None):
        self.data = data
        self.headers = headers


async def request(session: aiohttp.ClientSession, uri, method, headers=None, data_values=None):
    if data_values is None:
        data_values = {}
    if headers is None:
        headers = {}
    response = await send_request(
        session,
        uri,
        method,
        headers,
        data=json.dumps(
            remove_nones(data_values)
        )
    )
    if not str(response.status).startswith('2'):
        raise await DydxApiError.create(response)

    if response.content:
        return Response(await response.json(), response.headers)
    else:
        return Response('{}', response.headers)


async def send_request(session: aiohttp.ClientSession, uri, method, headers=None, **kwargs) -> aiohttp.ClientResponse:
    if headers is None:
        headers = {}
    return await getattr(session, method)(uri, headers={**core_headers, **headers}, **kwargs)
