# AsyncProxy

An asynchronous HTTP proxy built with Python and Twisted complying to the requirements specified below:

## Requirements

1. Range requests support as defined in [RFC2616](https://www.ietf.org/rfc/rfc2616.txt), but also via `range` query parameter.

2. Return 416 error in case where both header and query parameter are specified, but with different value.

3. Expose proxy statistics at /stats endpoint (total bytes transferred, uptime).

4. Proxy should be delivered with appropriate `Dockerfile` and `docker-compose.yml` (Hint: use python:3.5 image).

5. Proxy should be configureable via environmental variables.