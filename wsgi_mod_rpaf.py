from __future__ import absolute_import
from __future__ import unicode_literals

import io
import ipaddress

import six


if six.PY2:  # pragma: no cover (py2)
    def wsgi_to_text(s):
        # Use latin-1, the encoding of ip addresses isn't important (they'll
        # always be either ascii, or invalidated by the ipaddress module)
        return s.decode('LATIN-1')

    def text_to_wsgi(s):
        return s.encode('US-ASCII')
else:  # pragma: no cover (py3)
    def wsgi_to_text(s):
        return s

    def text_to_wsgi(s):
        return s


PROXY_IPS_DIRECTIVE = 'RPAFproxy_ips '


def _parse_file(f):
    networks = []
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        assert line.startswith(PROXY_IPS_DIRECTIVE), line
        line = line[len(PROXY_IPS_DIRECTIVE):]
        networks.append(ipaddress.ip_network(line))

    return tuple(networks)


UNPARSEABLE_IP = type(str('UNPARSEABLE_IP'), (object,), {'__slots__': ()})()


def _safe_parse_ip(s):
    """Returns None if it is not a valid IP"""
    try:
        return ipaddress.ip_address(s)
    except ValueError:
        return UNPARSEABLE_IP


def _ip_in_networks(ip, networks):
    return any(
        ip is not UNPARSEABLE_IP and ip in network
        for network in networks
    )


def _rewrite_environ(environ, networks):
    addr = _safe_parse_ip(wsgi_to_text(environ['REMOTE_ADDR']))
    if not _ip_in_networks(addr, networks):
        return environ
    environ = dict(environ)
    x_forwarded_for = wsgi_to_text(environ['HTTP_X_FORWARDED_FOR'])
    # Search from the end for the first ip which is not a proxy ip
    ip_to_set = None
    for ip in x_forwarded_for.split(',')[::-1]:
        ip = _safe_parse_ip(ip.strip())
        if _ip_in_networks(ip, networks):
            ip_to_set = ip
            continue
        elif ip is not UNPARSEABLE_IP:
            ip_to_set = ip
            break
    if ip_to_set is not None:
        environ[str('REMOTE_ADDR')] = text_to_wsgi(six.text_type(ip_to_set))
    return environ


def wsgi_mod_rpaf_middleware(app, conf):
    with io.open(conf) as conf_file:
        networks = _parse_file(conf_file)

    def wsgi_mod_rpaf_app(environ, start_response):
        if (
                'REMOTE_ADDR' in environ and
                'HTTP_X_FORWARDED_FOR' in environ
        ):
            environ = _rewrite_environ(environ, networks)
        return app(environ, start_response)

    return wsgi_mod_rpaf_app
