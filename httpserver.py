#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import sys
import http.client

content = None
origin = None


def get_cmd_args():
    parser = argparse.ArgumentParser(
        prog='httpserver', description='An HTTP server')
    parser.add_argument('-p', dest='port', type=int,
                        help='The port at which the HTTP server should be running.')
    parser.add_argument('-o', dest='origin',
                        help='The origin server.')
    args = parser.parse_args()
    if args.port is None or args.origin is None:
        parser.print_help()
        sys.exit(1)
    return args.port, args.origin


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global content
        filename = self.path.lstrip('/')
        if filename != 'test.html':
            self.send_error(404, 'Not Found')
            return
        if content is None:
            # Fetch content
            client = http.client.HTTPConnection(origin)
            client.request('GET', '/index.html')
            response = client.getresponse()
            if response.status == 200:
                content = response.read()
            else:
                print('Could not fetch test.html from origin')
                client.close()
                sys.exit(1)
            client.close()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content)
        return


def main():
    global origin
    port, origin = get_cmd_args()
    if origin.startswith('http://'):
        origin = origin.lstrip('http://')
    server = HTTPServer(('', port), RequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
