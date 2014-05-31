#
# This file is part of Gruvi. Gruvi is free software available under the
# terms of the MIT license. See the file "LICENSE" that was provided
# together with this source file for the licensing terms.
#
# Copyright (c) 2012-2014 the Gruvi authors. See the file "AUTHORS" for a
# complete list.

from __future__ import absolute_import, print_function

import os
import six
import hashlib

import gruvi
from gruvi.stream import *
from gruvi.transports import TransportError
from support import *


class TestStreamReader(UnitTest):

    def test_read(self):
        reader = StreamReader()
        reader.feed(b'foo')
        self.assertEqual(reader.read(100), b'foo')
        reader.feed(b'foo bar')
        self.assertEqual(reader.read(3), b'foo')
        self.assertEqual(reader.read(10), b' bar')

    def test_read_incr(self):
        reader = StreamReader()
        buf = b'foobar'
        for i in range(len(buf)):
            reader.feed(buf[i:i+1])
        reader.feed_eof()
        self.assertEqual(reader.read(), b'foobar')

    def test_read_eof(self):
        reader = StreamReader()
        reader.feed(b'foo')
        reader.feed_eof()
        self.assertEqual(reader.read(), b'foo')
        self.assertEqual(reader.read(), b'')
        reader.feed_error(RuntimeError)

    def test_read_wait_eof(self):
        reader = StreamReader()
        reader.feed(b'foo')
        def write_more():
            gruvi.sleep(0.01)
            reader.feed(b'bar')
            gruvi.sleep(0.01)
            reader.feed_eof()
        gruvi.spawn(write_more)
        self.assertEqual(reader.read(), b'foobar')
        self.assertEqual(reader.read(), b'')

    def test_read_error(self):
        reader = StreamReader()
        reader.feed(b'foo')
        reader.feed_error(RuntimeError)
        self.assertEqual(reader.read(), b'foo')
        self.assertRaises(RuntimeError, reader.read)

    def test_read_wait_error(self):
        reader = StreamReader()
        reader.feed(b'foo')
        def write_more():
            gruvi.sleep(0.01)
            reader.feed(b'bar')
            gruvi.sleep(0.01)
            reader.feed_error(RuntimeError)
        gruvi.spawn(write_more)
        self.assertEqual(reader.read(), b'foobar')
        self.assertRaises(RuntimeError, reader.read)

    def test_readline(self):
        reader = StreamReader()
        reader.feed(b'foo\n')
        self.assertEqual(reader.readline(), b'foo\n')
        reader.feed(b'bar\nbaz\n')
        self.assertEqual(reader.readline(), b'bar\n')
        self.assertEqual(reader.readline(), b'baz\n')

    def test_readline_incr(self):
        reader = StreamReader()
        buf = b'foo\nbar\n'
        for i in range(len(buf)):
            reader.feed(buf[i:i+1])
        self.assertEqual(reader.readline(), b'foo\n')
        self.assertEqual(reader.readline(), b'bar\n')

    def test_readline_limit(self):
        reader = StreamReader()
        reader.feed(b'foobar\n')
        self.assertEqual(reader.readline(3), b'foo')
        self.assertEqual(reader.readline(), b'bar\n')

    def test_readline_eof(self):
        reader = StreamReader()
        reader.feed(b'foo')
        reader.feed_eof()
        self.assertEqual(reader.readline(), b'foo')
        self.assertEqual(reader.readline(), b'')

    def test_readline_wait_eof(self):
        reader = StreamReader()
        reader.feed(b'foo')
        def write_more():
            gruvi.sleep(0.01)
            reader.feed(b'bar')
            gruvi.sleep(0.01)
            reader.feed_eof()
        gruvi.spawn(write_more)
        self.assertEqual(reader.readline(), b'foobar')
        self.assertEqual(reader.readline(), b'')

    def test_readline_error(self):
        reader = StreamReader()
        reader.feed(b'foo')
        reader.feed_error(RuntimeError)
        self.assertEqual(reader.readline(), b'foo')
        self.assertRaises(RuntimeError, reader.readline)

    def test_readline_wait_error(self):
        reader = StreamReader()
        reader.feed(b'foo')
        def write_more():
            gruvi.sleep(0.01)
            reader.feed(b'bar')
            gruvi.sleep(0.01)
            reader.feed_error(RuntimeError)
        gruvi.spawn(write_more)
        self.assertEqual(reader.readline(), b'foobar')
        self.assertRaises(RuntimeError, reader.readline)

    def test_readlines_limit(self):
        reader = StreamReader()
        reader.feed(b'foo\nbar\n')
        self.assertEqual(reader.readlines(4), [b'foo\n', b'bar\n'])

    def test_readlines_eof(self):
        reader = StreamReader()
        reader.feed(b'foo\nbar\n')
        reader.feed_eof()
        self.assertEqual(reader.readlines(), [b'foo\n', b'bar\n'])
        self.assertEqual(reader.readlines(), [])

    def test_readlines_wait_eof(self):
        reader = StreamReader()
        reader.feed(b'foo\n')
        def write_more():
            gruvi.sleep(0.01)
            reader.feed(b'bar\n')
            gruvi.sleep(0.01)
            reader.feed_eof()
        gruvi.spawn(write_more)
        self.assertEqual(reader.readlines(), [b'foo\n', b'bar\n'])
        self.assertEqual(reader.readlines(), [])
 
    def test_readlines_error(self):
        reader = StreamReader()
        reader.feed(b'foo\nbar\n')
        reader.feed_error(RuntimeError)
        self.assertEqual(reader.readlines(), [b'foo\n', b'bar\n'])
        self.assertRaises(RuntimeError, reader.readlines)

    def test_readlines_wait_error(self):
        reader = StreamReader()
        reader.feed(b'foo\n')
        def write_more():
            gruvi.sleep(0.01)
            reader.feed(b'bar\n')
            gruvi.sleep(0.01)
            reader.feed_error(RuntimeError)
        gruvi.spawn(write_more)
        self.assertEqual(reader.readlines(), [b'foo\n', b'bar\n'])
        self.assertRaises(RuntimeError, reader.readlines)

    def test_iter_eof(self):
        reader = StreamReader()
        reader.feed(b'foo\nbar\n')
        reader.feed_eof()
        it = iter(reader)
        self.assertEqual(six.next(it), b'foo\n')
        self.assertEqual(six.next(it), b'bar\n')
        self.assertRaises(StopIteration, six.next, it)

    def test_iter_wait_eof(self):
        reader = StreamReader()
        reader.feed(b'foo\n')
        def write_more():
            gruvi.sleep(0.01)
            reader.feed(b'bar\n')
            gruvi.sleep(0.01)
            reader.feed_eof()
        gruvi.spawn(write_more)
        it = iter(reader)
        self.assertEqual(six.next(it), b'foo\n')
        self.assertEqual(six.next(it), b'bar\n')
        self.assertRaises(StopIteration, six.next, it)

    def test_iter_error(self):
        reader = StreamReader()
        reader.feed(b'foo\nbar\n')
        reader.feed_error(RuntimeError)
        it = iter(reader)
        self.assertEqual(six.next(it), b'foo\n')
        self.assertEqual(six.next(it), b'bar\n')
        self.assertRaises(RuntimeError, six.next, it)

    def test_iter_wait_error(self):
        reader = StreamReader()
        reader.feed(b'foo\n')
        def write_more():
            gruvi.sleep(0.01)
            reader.feed(b'bar\n')
            gruvi.sleep(0.01)
            reader.feed_error(RuntimeError)
        gruvi.spawn(write_more)
        it = iter(reader)
        self.assertEqual(six.next(it), b'foo\n')
        self.assertEqual(six.next(it), b'bar\n')
        self.assertRaises(RuntimeError, six.next, it)


class TestStreamProtocol(UnitTest):

    def test_read(self):
        # Test that read() works.
        transport = MockTransport()
        protocol = StreamProtocol()
        transport.start(protocol)
        protocol.data_received(b'foo')
        self.assertEqual(protocol.read(100), b'foo')
        protocol.data_received(b'bar')
        protocol.eof_received()
        self.assertEqual(protocol.read(), b'bar')

    def test_read_after_error(self):
        # Test that the buffer can be emptied after an error occurs.
        transport = MockTransport()
        protocol = StreamProtocol()
        transport.start(protocol)
        protocol.data_received(b'foobar')
        protocol.connection_lost(RuntimeError)
        self.assertEqual(protocol.read(3), b'foo')
        self.assertEqual(protocol.read(3), b'bar')
        self.assertEqual(protocol.read(), b'')

    def test_readline(self):
        # Test that readline() works.
        transport = MockTransport()
        protocol = StreamProtocol()
        transport.start(protocol)
        protocol.data_received(b'foo\n')
        self.assertEqual(protocol.readline(), b'foo\n')
 
    def test_readlines(self):
        # Test that readlines() works.
        transport = MockTransport()
        protocol = StreamProtocol()
        transport.start(protocol)
        protocol.data_received(b'foo\nbar\n')
        protocol.eof_received()
        self.assertEqual(protocol.readlines(), [b'foo\n', b'bar\n'])
 
    def test_iter(self):
        # Ensure that iterating over a stream protocol produces lines.
        transport = MockTransport()
        protocol = StreamProtocol()
        transport.start(protocol)
        protocol.data_received(b'foo\nbar\n')
        protocol.eof_received()
        it = iter(protocol)
        self.assertEqual(six.next(it), b'foo\n')
        self.assertEqual(six.next(it), b'bar\n')
        self.assertRaises(StopIteration, six.next, it)

    def test_write(self):
        # Test that write() works.
        transport = MockTransport()
        protocol = StreamProtocol()
        transport.start(protocol)
        protocol.write(b'foo')
        self.assertEqual(transport.buffer.getvalue(), b'foo')

    def test_writelines(self):
        # Test that writelines() works.
        transport = MockTransport()
        protocol = StreamProtocol()
        transport.start(protocol)
        protocol.writelines([b'foo', b'bar'])
        self.assertEqual(transport.buffer.getvalue(), b'foobar')

    def test_write_eof(self):
        # Test that write_eof() works.
        transport = MockTransport()
        protocol = StreamProtocol()
        transport.start(protocol)
        self.assertFalse(transport.eof)
        protocol.write_eof()
        self.assertTrue(transport.eof)

    def test_read_write_flow_control(self):
        # Test the read and write flow control of a stream transport.
        transport = MockTransport()
        protocol = StreamProtocol()
        transport.start(protocol)
        protocol.set_read_buffer_limits(100)
        transport.set_write_buffer_limits(50)
        def reader():
            while True:
                buf = protocol.read(20)
                protocol.write(buf)
        gruvi.spawn(reader)
        buf = b'x' * 20
        interrupted = 0
        for i in range(100):
            protocol.data_received(buf)
            if protocol._reading:
                continue
            interrupted += 1
            self.assertGreater(protocol._read_buffer_size, 0)
            # Switch to the reader() fiber which will fill up the transport
            # write buffer.
            gruvi.sleep(0)
            # The transport write buffer should be full but the protocol read
            # buffer should still contain something.
            self.assertTrue(protocol._reading)
            self.assertGreater(protocol._read_buffer_size, 0)
            self.assertFalse(protocol._may_write)
            # Drain write buffer and resume writing
            transport.buffer.seek(0)
            transport.buffer.truncate()
            protocol.resume_writing()
        self.assertGreater(interrupted, 30)


def echo_handler(protocol):
    while True:
        buf = protocol.read(100)
        if not buf:
            break
        protocol.write(buf)


class TestStream(UnitTest):

    def test_echo_pipe(self):
        server = StreamServer(echo_handler)
        server.listen(self.pipename())
        client = StreamClient()
        client.connect(server.addresses[0])
        client.write(b'foo\n')
        client.write_eof()
        self.assertEqual(client.readline(), b'foo\n')
        self.assertEqual(client.readline(), b'')
        server.close()
        client.close()

    def test_echo_pipe_ssl(self):
        server = StreamServer(echo_handler)
        context = self.get_ssl_context()
        server.listen(self.pipename(), ssl=context)
        client = StreamClient()
        client.connect(server.addresses[0], ssl=context)
        client.write(b'foo\n')
        self.assertEqual(client.readline(), b'foo\n')
        server.close()
        client.close()

    def test_echo_tcp(self):
        server = StreamServer(echo_handler)
        server.listen(('127.0.0.1', 0))
        client = StreamClient()
        client.connect(server.addresses[0])
        client.write(b'foo\n')
        client.write_eof()
        self.assertEqual(client.readline(), b'foo\n')
        server.close()
        client.close()

    def test_echo_tcp_ssl(self):
        server = StreamServer(echo_handler)
        context = self.get_ssl_context()
        server.listen(('127.0.0.1', 0), ssl=context)
        client = StreamClient()
        client.connect(server.addresses[0], ssl=context)
        client.write(b'foo\n')
        self.assertEqual(client.readline(), b'foo\n')
        server.close()
        client.close()

    def test_echo_data(self):
        # Echo a bunch of data and ensure it is echoed identically
        server = StreamServer(echo_handler)
        server.listen(('127.0.0.1', 0))
        client = StreamClient()
        client.connect(server.addresses[0])
        md1 = hashlib.sha256()
        md2 = hashlib.sha256()
        def produce():
            for i in range(1000):
                chunk = os.urandom(1024)
                client.write(chunk)
                md1.update(chunk)
            client.write_eof()
        def consume():
            while True:
                buf = client.read(1024)
                if not buf:
                    break
                md2.update(buf)
        f1 = gruvi.spawn(produce)
        f2 = gruvi.spawn(consume)
        f1.join(); f2.join()
        self.assertEqual(md1.digest(), md2.digest())
        server.close()
        client.close()

    def test_connection_limit(self):
        server = StreamServer(echo_handler)
        server.listen(('127.0.0.1', 0))
        addr = server.addresses[0]
        server.max_connections = 10
        clients = []
        try:
            for i in range(15):
                client = StreamClient()
                client.connect(addr)
                client.write(b'foo\n')
                buf = client.readline()
                if buf == b'':  # conneciton closed: EOF
                    client.close()
                clients.append(client)
        except TransportError as e:
            pass
        self.assertLessEqual(len(server.connections), server.max_connections)
        for client in clients:
            client.close()
        server.close()


if __name__ == '__main__':
    os.environ.setdefault('VERBOSE', '1')
    unittest.main()
