[![Build Status](https://travis-ci.org/Yelp/wsgi-mod-rpaf.svg?branch=master)](https://travis-ci.org/Yelp/wsgi-mod-rpaf)
[![Coverage Status](https://coveralls.io/repos/github/Yelp/wsgi-mod-rpaf/badge.svg?branch=master)](https://coveralls.io/github/Yelp/wsgi-mod-rpaf?branch=master)

wsgi-mod-rpaf
=============

Implement mod-rpaf as a wsgi middleware so it can be used with any python web
framework.

## Usage


```python
from wsgi_mod_rpaf import wsgi_mod_rpaf_middleware

...

app = wsgi_mod_rpaf_middleware(app, '/path/to/rpaf.conf')
```

## Supported directives

### `RPAFproxy_ips`

Values: CIDR (`10.0.0.0/8`) or IP (`127.0.0.1`)

These IP ranges / IPs will be considered a valid "proxy" when processing the
`X-Forwarded-For` header.

### Comments

Lines that are blank or begin with a `#` are ignored.

## Algorithm

In pseudo-code this is approximately how the algorithm is implemented:

```
if REMOTE_ADDR not in proxy_ips:
    return

if 'X-Forwarded-For' not in headers:
    return

forwarded_ips = whitespace stripped, split by ',' of X-Forwarded-For header

look from the right of forwarded_ips, find the first ip that is not in the
proxy ips.  The first one found is the ip to set.  If all ips in
X-Forwarded-For are proxy ips, the leftmost one is set.

If none are found:
    return
```
