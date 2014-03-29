#
# This file is part of Gruvi. Gruvi is free software available under the
# terms of the MIT license. See the file "LICENSE" that was provided
# together with this source file for the licensing terms.
#
# Copyright (c) 2012-2013 the Gruvi authors. See the file "AUTHORS" for a
# complete list.

from __future__ import absolute_import, print_function

import gruvi
from gruvi.http import *
from gruvi.http import HttpParser, HttpMessage, urlsplit2, split_header_options
from tests.support import *


class TestUrlsplit2(UnitTest):

    def test_basic(self):
        parsed = urlsplit2('foo.org')
        self.assertEqual(parsed.scheme, 'http')
        self.assertEqual(parsed.netloc, 'foo.org:80')
        self.assertEqual(parsed.hostname, 'foo.org')
        self.assertEqual(parsed.port, 80)
        self.assertEqual(parsed.path, '/')

    def test_scheme(self):
        parsed = urlsplit2('foo.org', default_scheme='https')
        self.assertEqual(parsed.scheme, 'https')
        parsed = urlsplit2('http://foo.org', default_scheme='https')
        self.assertEqual(parsed.scheme, 'http')

    def test_port(self):
        parsed = urlsplit2('http://foo.org')
        self.assertEqual(parsed.port, 80)
        parsed = urlsplit2('https://foo.org')
        self.assertEqual(parsed.port, 443)
        parsed = urlsplit2('http://foo.org:81')
        self.assertEqual(parsed.port, 81)
        parsed = urlsplit2('https://foo.org:444')
        self.assertEqual(parsed.port, 444)

    def test_path(self):
        parsed = urlsplit2('foo.org')
        self.assertEqual(parsed.path, '/')
        parsed = urlsplit2('foo.org/a')
        self.assertEqual(parsed.path, '/a')


class TestSplitHeaderOptions(UnitTest):

    def test_basic(self):
        parsed = split_header_options('text/plain; charset=foo')
        self.assertIsInstance(parsed, tuple)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0], 'text/plain')
        self.assertEqual(parsed[1], {'charset': 'foo'})

    def test_plain(self):
        parsed = split_header_options('text/plain')
        self.assertEqual(parsed, ('text/plain', {}))

    def test_iso8859_1(self):
        parsed = split_header_options('text/plain; foo="bar\xfe"')
        self.assertEqual(parsed, ('text/plain', {'foo': 'bar\xfe'}))

    def test_whitespace(self):
        parsed = split_header_options('text/plain;   charset=foo    ')
        self.assertEqual(parsed, ('text/plain', {'charset': 'foo'}))

    def test_quoted(self):
        parsed = split_header_options('text/plain; charset="foo bar"')
        self.assertEqual(parsed, ('text/plain', {'charset': 'foo bar'}))

    def test_multiple(self):
        parsed = split_header_options('text/plain; foo=bar baz=qux')
        self.assertEqual(parsed, ('text/plain', {'foo': 'bar', 'baz': 'qux'}))

    def test_empty(self):
        parsed = split_header_options('text/plain; charset=""')
        self.assertEqual(parsed, ('text/plain', {'charset': ''}))


class TestHttpParser(UnitTest):

    def test_simple_request(self):
        r = b'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_REQUEST)
        self.assertEqual(msg.url, '/')
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Host', 'example.com')])
        self.assertEqual(msg.body.read(), b'')

    def test_request_with_body(self):
        r = b'GET / HTTP/1.1\r\nHost: example.com\r\n' \
            b'Content-Length: 3\r\n\r\nFoo'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_REQUEST)
        self.assertEqual(msg.url, '/')
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Host', 'example.com'), ('Content-Length', '3')])
        self.assertEqual(msg.body.read(), b'Foo')

    def test_request_with_body_incremental(self):
        r = b'GET / HTTP/1.1\r\nHost: example.com\r\n' \
            b'Content-Length: 3\r\n\r\nFoo'
        parser = HttpParser()
        for i in range(len(r)):
            nbytes = parser.feed(r[i:i+1])
            self.assertEqual(nbytes, 1)
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_REQUEST)
        self.assertEqual(msg.url, '/')
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Host', 'example.com'), ('Content-Length', '3')])
        self.assertEqual(msg.body.read(), b'Foo')

    def test_request_with_chunked_body(self):
        r = b'GET / HTTP/1.1\r\nHost: example.com\r\n' \
            b'Transfer-Encoding: chunked\r\n\r\n' \
            b'3\r\nFoo\r\n0\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_REQUEST)
        self.assertEqual(msg.url, '/')
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Host', 'example.com'),
                                       ('Transfer-Encoding', 'chunked')])
        self.assertEqual(msg.body.read(), b'Foo')

    def test_request_with_chunked_body_incremental(self):
        r = b'GET / HTTP/1.1\r\nHost: example.com\r\n' \
            b'Transfer-Encoding: chunked\r\n\r\n' \
            b'3\r\nFoo\r\n0\r\n\r\n'
        parser = HttpParser()
        for i in range(len(r)):
            nbytes = parser.feed(r[i:i+1])
            self.assertEqual(nbytes, 1)
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_REQUEST)
        self.assertEqual(msg.url, '/')
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Host', 'example.com'),
                                       ('Transfer-Encoding', 'chunked')])
        self.assertEqual(msg.body.read(), b'Foo')

    def test_request_with_chunked_body_and_trailers(self):
        r = b'GET / HTTP/1.1\r\nHost: example.com\r\n' \
            b'Transfer-Encoding: chunked\r\n\r\n' \
            b'3\r\nFoo\r\n0\r\nETag: foo\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_REQUEST)
        self.assertEqual(msg.url, '/')
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Host', 'example.com'),
                                       ('Transfer-Encoding', 'chunked')])
        self.assertEqual(msg.trailers, [('ETag', 'foo')])
        self.assertEqual(msg.body.read(), b'Foo')

    def test_pipelined_requests(self):
        r = b'GET /0 HTTP/1.1\r\nHost: example0.com\r\n\r\n' \
            b'GET /1 HTTP/1.1\r\nHost: example1.com\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        for i in range(2):
            msg = parser.pop_message()
            self.assertIsInstance(msg, HttpMessage)
            self.assertEqual(msg.message_type, parser.HTTP_REQUEST)
            self.assertEqual(msg.url, '/{0}'.format(i))
            self.assertEqual(msg.version, (1, 1))
            self.assertEqual(msg.headers, [('Host', 'example{0}.com'.format(i))])
            self.assertEqual(msg.body.read(), b'')

    def test_pipelined_requests_with_body(self):
        r = b'GET / HTTP/1.1\r\nHost: example.com\r\n' \
            b'Content-Length: 4\r\n\r\nFoo0' \
            b'GET / HTTP/1.1\r\nHost: example.com\r\n' \
            b'Content-Length: 4\r\n\r\nFoo1'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        for i in range(2):
            msg = parser.pop_message()
            self.assertIsInstance(msg, HttpMessage)
            self.assertEqual(msg.message_type, parser.HTTP_REQUEST)
            self.assertEqual(msg.url, '/')
            self.assertEqual(msg.version, (1, 1))
            self.assertEqual(msg.headers, [('Host', 'example.com'), ('Content-Length', '4')])
            self.assertEqual(msg.body.read(), 'Foo{0}'.format(i).encode('ascii'))

    def test_request_url(self):
        r = b'GET http://user:pass@example.com:80/foo/bar?baz=qux#quux HTTP/1.1\r\n' \
            b'Host: example.com\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        msg = parser.pop_message()
        parsed_url = msg.parsed_url
        self.assertEqual(parsed_url, ['http', 'example.com', '80', '/foo/bar',
                                      'baz=qux', 'quux', 'user:pass'])

    def test_short_request_url(self):
        r = b'GET /foo/bar HTTP/1.1\r\n' \
            b'Host: example.com\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        msg = parser.pop_message()
        parsed_url = msg.parsed_url
        self.assertEqual(parsed_url, ['', '', '', '/foo/bar', '', '', ''])

    def test_simple_response(self):
        r = b'HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_RESPONSE)
        self.assertEqual(msg.status_code, 200)
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Content-Length', '0')])
        self.assertEqual(msg.body.read(), b'')

    def test_response_with_body(self):
        r = b'HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\nFoo'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_RESPONSE)
        self.assertEqual(msg.status_code, 200)
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Content-Length', '3')])
        self.assertEqual(msg.body.read(), b'Foo')

    def test_response_with_body_incremental(self):
        r = b'HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\nFoo'
        parser = HttpParser()
        for i in range(len(r)):
            nbytes = parser.feed(r[i:i+1])
            self.assertEqual(nbytes, 1)
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_RESPONSE)
        self.assertEqual(msg.status_code, 200)
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Content-Length', '3')])
        self.assertEqual(msg.body.read(), b'Foo')

    def test_response_with_chunked_body(self):
        r = b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n' \
            b'3\r\nFoo\r\n0\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_RESPONSE)
        self.assertEqual(msg.status_code, 200)
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Transfer-Encoding', 'chunked')])
        self.assertEqual(msg.body.read(), b'Foo')

    def test_response_with_chunked_body_incremental(self):
        r = b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n' \
            b'3\r\nFoo\r\n0\r\n\r\n'
        parser = HttpParser()
        for i in range(len(r)):
            nbytes = parser.feed(r[i:i+1])
            self.assertEqual(nbytes, 1)
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_RESPONSE)
        self.assertEqual(msg.status_code, 200)
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Transfer-Encoding', 'chunked')])
        self.assertEqual(msg.body.read(), b'Foo')

    def test_response_with_chunked_body_and_trailers(self):
        r = b'HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n' \
            b'3\r\nFoo\r\n0\r\nETag: foo\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_RESPONSE)
        self.assertEqual(msg.status_code, 200)
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Transfer-Encoding', 'chunked')])
        self.assertEqual(msg.trailers, [('ETag', 'foo')])
        self.assertEqual(msg.body.read(), b'Foo')

    def test_pipelined_responses(self):
        r = b'HTTP/1.1 200 OK\r\nContent-Length: 0\r\nCookie: foo0\r\n\r\n' \
            b'HTTP/1.1 200 OK\r\nContent-Length: 0\r\nCookie: foo1\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        for i in range(2):
            msg = parser.pop_message()
            self.assertIsInstance(msg, HttpMessage)
            self.assertEqual(msg.message_type, parser.HTTP_RESPONSE)
            self.assertEqual(msg.status_code, 200)
            self.assertEqual(msg.version, (1, 1))
            self.assertEqual(msg.headers, [('Content-Length', '0'),
                                           ('Cookie', 'foo{0}'.format(i))])
            self.assertEqual(msg.body.read(), b'')

    def test_pipelined_responses_with_body(self):
        r = b'HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\nFoo0' \
            b'HTTP/1.1 200 OK\r\nContent-Length: 4\r\n\r\nFoo1'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        for i in range(2):
            msg = parser.pop_message()
            self.assertIsInstance(msg, HttpMessage)
            self.assertEqual(msg.message_type, parser.HTTP_RESPONSE)
            self.assertEqual(msg.status_code, 200)
            self.assertEqual(msg.version, (1, 1))
            self.assertEqual(msg.headers, [('Content-Length', '4')])
            self.assertEqual(msg.body.read(), 'Foo{0}'.format(i).encode('ascii'))

    def test_pipelined_head_responses(self):
        r = b'HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\n' \
            b'HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\n'
        parser = HttpParser()
        parser.push_request('HEAD')
        parser.push_request('HEAD')
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        for i in range(2):
            msg = parser.pop_message()
            self.assertIsInstance(msg, HttpMessage)
            self.assertEqual(msg.message_type, parser.HTTP_RESPONSE)
            self.assertEqual(msg.status_code, 200)
            self.assertEqual(msg.version, (1, 1))
            self.assertEqual(msg.headers, [('Content-Length', '3')])
            self.assertEqual(msg.body.read(), b'')

    def test_pipelined_empty_responses(self):
        r = b'HTTP/1.1 100 OK\r\nCookie: foo0\r\n\r\n' \
            b'HTTP/1.1 204 OK\r\nCookie: foo1\r\n\r\n' \
            b'HTTP/1.1 304 OK\r\nCookie: foo2\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r)
        self.assertEqual(nbytes, len(r))
        for i in range(3):
            msg = parser.pop_message()
            self.assertIsInstance(msg, HttpMessage)
            self.assertEqual(msg.message_type, parser.HTTP_RESPONSE)
            self.assertEqual(msg.version, (1, 1))
            self.assertEqual(msg.headers, [('Cookie', 'foo{0}'.format(i))])
            self.assertEqual(msg.body.read(), b'')

    def test_pipelined_responses_eof(self):
        r = b'HTTP/1.1 200 OK\r\nCookie: foo0\r\n\r\n' \
            b'HTTP/1.1 204 OK\r\nCookie: foo1\r\n\r\n'
        parser = HttpParser()
        nbytes = parser.feed(r); parser.feed(b'')  # EOF
        self.assertEqual(nbytes, len(r))
        msg = parser.pop_message()
        self.assertIsInstance(msg, HttpMessage)
        self.assertEqual(msg.message_type, parser.HTTP_RESPONSE)
        self.assertEqual(msg.version, (1, 1))
        self.assertEqual(msg.headers, [('Cookie', 'foo0')])
        self.assertEqual(msg.body.read(), b'HTTP/1.1 204 OK\r\nCookie: foo1\r\n\r\n')


def hello_app(environ, start_response):
    headers = [('Content-Type', 'text/plain')]
    start_response('200 OK', headers)
    return ['Hello!']


def echo_app(environ, start_response):
    headers = [('Content-Type', 'text/plain')]
    body = environ['wsgi.input'].read()
    start_response('200 OK', headers)
    return [body]


class TestHttp(UnitTest):

    def test_simple(self):
        server = HttpServer(hello_app)
        server.listen(('localhost', 0))
        port = server.transport.getsockname()[1]
        client = HttpClient()
        client.connect(('localhost', port))
        client.request('GET', '/')
        response = client.getresponse()
        self.assertEqual(response.version, (1, 1))
        self.assertEqual(response.status, 200)
        server = response.get_header('Server')
        self.assertTrue(server.startswith('gruvi.http'))
        ctype = response.get_header('Content-Type')
        self.assertEqual(ctype, 'text/plain')
        self.assertEqual(response.read(), b'Hello!')

    def test_request_headers_not_changed(self):
        server = HttpServer(hello_app)
        server.listen(('localhost', 0))
        addr = gruvi.getsockname(server.transport)
        client = HttpClient()
        client.connect(addr)
        headers = []
        client.request('GET', '/', headers)
        self.assertEqual(headers, [])
        client.close()
        server.close()

    def test_request_body_bytes(self):
        server = HttpServer(echo_app)
        server.listen(('localhost', 0))
        addr = gruvi.getsockname(server.transport)
        client = HttpClient()
        client.connect(addr)
        client.request('POST', '/', body=b'foo')
        response = client.getresponse()
        body = response.read()
        self.assertEqual(body, b'foo')

    def test_request_body_string(self):
        server = HttpServer(echo_app)
        server.listen(('localhost', 0))
        addr = gruvi.getsockname(server.transport)
        client = HttpClient()
        client.connect(addr)
        client.request('POST', '/', body='foo')
        response = client.getresponse()
        body = response.read()
        self.assertEqual(body, b'foo')

    def test_request_body_bytes_sequence(self):
        server = HttpServer(echo_app)
        server.listen(('localhost', 0))
        addr = gruvi.getsockname(server.transport)
        client = HttpClient()
        client.connect(addr)
        client.request('POST', '/', body=[b'foo', b'bar'])
        response = client.getresponse()
        body = response.read()
        self.assertEqual(body, b'foobar')

    def test_request_body_string_sequence(self):
        server = HttpServer(echo_app)
        server.listen(('localhost', 0))
        addr = gruvi.getsockname(server.transport)
        client = HttpClient()
        client.connect(addr)
        client.request('POST', '/', body=['foo', 'bar'])
        response = client.getresponse()
        body = response.read()
        self.assertEqual(body, b'foobar')


if __name__ == '__main__':
    unittest.main()
