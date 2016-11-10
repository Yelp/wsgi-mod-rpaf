from __future__ import absolute_import
from __future__ import unicode_literals

import io
import ipaddress

import pytest
import webtest

import wsgi_mod_rpaf


def test_parse_file():
    f = io.StringIO(
        '\n'
        '# I am a comment\n'
        '# This is an ip without a mask\n'
        'RPAFproxy_ips 1.2.3.4\n'
        '# This is an ip with a mask\n'
        'RPAFproxy_ips 10.0.0.0/8\n'
    )
    ret = wsgi_mod_rpaf._parse_file(f)
    assert ret == (
        ipaddress.ip_network('1.2.3.4'), ipaddress.ip_network('10.0.0.0/8'),
    )


def remote_addr_app(environ, start_response):
    start_response(str('200 OK'), [(str('Content-Type'), str('text/plain'))])
    return [environ['REMOTE_ADDR'].encode('UTF-8')]


@pytest.yield_fixture
def wrapped_app():
    yield webtest.TestApp(wsgi_mod_rpaf.wsgi_mod_rpaf_middleware(
        'testing/rpaf.conf', remote_addr_app,
    ))


REMOTE_ADDR = str('REMOTE_ADDR')
HTTP_X_FORWARDED_FOR = str('HTTP_X_FORWARDED_FOR')


@pytest.mark.parametrize(
    'environ',
    (
        # no HTTP_X_FORWARDED_FOR (no rpaf occurs)
        {REMOTE_ADDR: str('1.2.3.4')},
        # ip is not a proxy ip (no rpaf occurs)
        {
            REMOTE_ADDR: str('1.2.3.4'),
            HTTP_X_FORWARDED_FOR: str('5.6.7.8, 127.0.0.1'),
        },
        # rpaf occurs, proxied twice
        {
            REMOTE_ADDR: str('127.0.0.1'),
            HTTP_X_FORWARDED_FOR: str('1.2.3.4, 10.1.2.3, 127.0.0.1'),
        },
        # rpaf occurs, no spaces after commas
        {
            REMOTE_ADDR: str('127.0.0.1'),
            HTTP_X_FORWARDED_FOR: str('1.2.3.4,127.0.0.1'),
        },
        # X-Forwarded-For contains garbage entries (rpaf ignores garbage)
        {
            REMOTE_ADDR: str('127.0.0.1'),
            HTTP_X_FORWARDED_FOR: str('1.2.3.4, garbage, 127.0.0.1'),
        },
    ),
)
def test_rpaf_middleware(wrapped_app, environ):
    assert wrapped_app.get('/', extra_environ=environ).body == b'1.2.3.4'


def test_x_forwarded_for_is_all_proxy_ips(wrapped_app):
    """Shouldn't ever happen, but it is a reasonable test"""
    environ = {
        REMOTE_ADDR: str('127.0.0.1'),
        HTTP_X_FORWARDED_FOR: str('10.1.2.3, 127.0.0.1'),
    }
    assert wrapped_app.get('/', extra_environ=environ).body == b'127.0.0.1'
