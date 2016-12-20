""""
Integration tests for various pieces involved in external provider support.
"""

from unittest import TestCase, main
from stormpath.resources import WebConfig

try:
    from mock import MagicMock
except ImportError:
    from unittest.mock import MagicMock


class TestApplicationWebConfig(TestCase):

    @staticmethod
    def test_modifying_application_web_config():
        ds = MagicMock()
        ds.update_resource.return_value = {}

        pp = WebConfig(
            client=MagicMock(data_store=ds, BASE_URL='http://example.com'),
            href='application-web-config')

        pp._set_properties(
            {
                'status':
                    WebConfig.STATUS_ENABLED,
                'dns_label':
                    'a-dns-label'
            })
        pp.save()

        ds.update_resource.assert_called_once_with(
            'application-web-config',
            {
                'status':
                    WebConfig.STATUS_ENABLED,
                'dnsLabel':
                    'a-dns-label'
            })


if __name__ == '__main__':
    main()
