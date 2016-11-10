[![Build Status](https://travis-ci.org/Yelp/wsgi_mod_rpaf.svg?branch=master)](https://travis-ci.org/Yelp/wsgi_mod_rpaf)
[![Coverage Status](https://img.shields.io/coveralls/Yelp/wsgi_mod_rpaf.svg?branch=master)](https://coveralls.io/r/Yelp/wsgi_mod_rpaf)

wsgi-mod-rpaf
=============

Implement mod-rpaf as a wsgi middleware so it can be used with any python web
framework.

## Usage


```python
from wsgi_mod_rpaf import wsgi_mod_rpaf_middleware

...

app = wsgi_mod_rpaf_middleware('/path/to/rpaf.conf', app)
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
proxy ips.  The first one found is the ip to set

If none are found:
    return
```
