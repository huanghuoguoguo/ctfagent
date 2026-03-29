from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

HOST = "0.0.0.0"
PORT = 5006


class Handler(BaseHTTPRequestHandler):
    def _send_html(self, body: str, status: int = 200) -> None:
        raw = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/":
            self._send_html(
                """
                <h1>XSS Training Lab</h1>
                <ul>
                  <li><a href="/reflect?q=test">/reflect?q=...</a></li>
                  <li><a href="/attr?q=test">/attr?q=...</a></li>
                  <li><a href="/dom?msg=test">/dom?msg=...</a></li>
                </ul>
                """
            )
            return

        if parsed.path == "/reflect":
            value = query.get("q", ["guest"])[0]
            self._send_html(
                f"""
                <html>
                  <body>
                    <h1>Search Result</h1>
                    <div id="result">You searched for: {value}</div>
                  </body>
                </html>
                """
            )
            return

        if parsed.path == "/attr":
            value = query.get("q", ["guest"])[0]
            self._send_html(
                f"""
                <html>
                  <body>
                    <h1>Profile Preview</h1>
                    <input id="nickname" value="{value}">
                  </body>
                </html>
                """
            )
            return

        if parsed.path == "/dom":
            value = query.get("msg", ["guest"])[0]
            safe = html.escape(value)
            self._send_html(
                f"""
                <html>
                  <body>
                    <h1>DOM Preview</h1>
                    <div id="sink"></div>
                    <script>
                      const raw = decodeURIComponent("{safe}");
                      document.getElementById("sink").innerHTML = raw;
                    </script>
                  </body>
                </html>
                """
            )
            return

        self._send_html("<h1>Not Found</h1>", status=404)


if __name__ == "__main__":
    HTTPServer((HOST, PORT), Handler).serve_forever()
