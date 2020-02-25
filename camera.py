# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver
import os
from threading import Condition
from http import server

TITLE=os.getenv('CAMERA_NAME')
PAGE=f"""\
<html>
<head>
<link rel="icon" type="image/png" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAfQAAAH0CAYAAADL1t+KAAAgAElEQVR4nO3dabhdZXnw8cUQSmQQgoDGIFMkw1r3Q/QAaQxJ91n3fRJoxQGMqC9U6/xqcWxRq7bUYi1Wq23FStW3ry0qFqktjlUqWqBcrXVCKMp5nrVPckKABBFkEALJ7ockQMh0hr33vfbe//91/T7lyxqeZ93XztlDlhEREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREVGnWi2nHrqmKI9PuZ7cDHpaEntZJeXvRtH3JtGLothfxaCfTKKXpmBXRNGvRbGrk+g3U9AvJ9HLt/ybfioVenES/XAK+qep0Helwl6ZCn1uyvXklNszvM+VqE5VC8qjU64np0KfWxX6qlTou1LQP02iH06FXpyCfiqJXppEL9+6174Zxa6Ool9Lwa5IopfGoJ+MYn+1Za/qeyspfzeJvawZ9LSU68lrivL45qLGId7nSkRtKOV6ciXlqiT21iT64Sj2hRTs2iS2OgVrObg7Bf1ZFLs6Bf1UFD0/FfZbTWnM975WRO1sdOFwXoXyjCT2ziT6d0n0uynYLVHsHpe9t2XPXxODXhaDfigFe0sV9EWpGDnJ+1oR0eMaz1fOaua2Moqen4J9Lore5DSwp+uWLa9G7M+S2MtWix3nfW2JdlcVhufFoC+PQT+05X+wNNVgH03FT5LopVWhb68KHeGVPVEXamWNfVOuJ6egb45BL4tia2rwMOiYGGx9CnplFfQPUhjR9XnjQO97QINZOs6eHKU8PQW7IAb7RhK7y3t/dJY2k9hnK9E3ji20Z7WyVft43wOini/ldmoM+v6t/21Xg43uTPTHKehHo5Sne98b6t/W540DU2FnRtFLotj/uK97d/pADPrtFOyCZhhe7H1/iHqi8TlLZkbRFySx/7flFar3Rq4zfSCKfi0Wdt5YWHGs972j3q4qNCQp3xHFro5BN/qv7/qKwW5Nop+IUp7eGhqa4X3viGrTuhMaT6lC+eqt72j9lfdm7VVRNKagH4358FLve0q9UZTy9K2f5rjNe/32sPtSsCuqojw3HWdP9r6nRF2vOb9xTBJ9Wwr6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"/>
<title>{TITLE}</title>
</head>
<body>
<center><h1>{TITLE}</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()

