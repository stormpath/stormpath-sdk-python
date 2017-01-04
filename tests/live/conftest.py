from os import getenv
from stormpath.client import Client


def pytest_keyboard_interrupt(excinfo):
    collection_resources = ['applications', 'organizations', 'directories']
    test_prefix = 'stormpath-sdk-python-test'
    auth_scheme = 'basic'
    base_url = getenv('STORMPATH_BASE_URL')
    api_key_id = getenv('STORMPATH_API_KEY_ID')
    api_key_secret = getenv('STORMPATH_API_KEY_SECRET')

    client = Client(id=api_key_id, secret=api_key_secret, base_url=base_url,
                    scheme=auth_scheme)
    for collection in collection_resources:
        for resource in list(getattr(client, collection).search(test_prefix)):
            resource.delete()
