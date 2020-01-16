#!/usr/bin/env python
 
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
 
# HTTPRequestHandler class
class MyServer(BaseHTTPRequestHandler):
 
    # GET
    def do_GET(self):
        
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_static')
        #print(self.path)
        if self.path == '/':
            filename = root + '/index.html'
        else:
            filename = root + self.path

        if self.path.startswith('/din/'):            
            self.get_dinamico()
        else:
            self.get_statico(filename)
        return
 
    def get_dinamico(self):

        code = 200
        if self.path == "/din/saluta":

            # Send message back to client
            message = "Hello world!"
            # Write content as utf-8 data
        else: 
            code = 404   # codice di  errore
            message = "ERRORE: "

        # Send response status code
        self.send_response(code)
            
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()
            
        self.wfile.write(bytes(message, "utf8"))


    def get_statico(self, filename):
        # Send response status code

        code = 200
        if filename[-4:] == '.css':
            content_type = 'text/css'
            self.send_header('Content-type', content_type)
        elif filename[-5:] == '.json':
            content_type = 'application/javascript'

        elif filename[-3:] == '.js':
            content_type = 'application/javascript'
        elif filename[-4:] == '.ico':
            content_type = 'image/x-icon'
        else:
            content_type = 'text/html'
            
        try: 
            print("Sto cercando di aprire il file %s" % filename)
            with open(filename, 'rb') as fh:
                html = fh.read()
                #html = bytes(html, 'utf8')
                self.send_response(code)            
                self.send_header('Content-type', content_type)
                self.end_headers()
                
                self.wfile.write(html)        
        except:
            self.send_response(500)                        
            # Send headers
            self.send_header('Content-type','text/html')
            self.end_headers()
            
            self.wfile.write(bytes("ERROR! Non sono riuscito a caricare %s " % filename , "utf8"))
    
def run():
    print('starting server...')

    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    
    # 0.0.0.0 rende il server accessibile a *tutta* la RETE
    # questo vuol dire che i vostri compagni di gruppo possono accedere al server sul vostro pc !
    
    # voi potete accedere al server con indirizzi tipo   http://localhost:8081/saluta
    # i vostri compagni possono usare X.Y.Z.W:8081/din/saluta
        
    server_address = ('0.0.0.0', 8081) 
    httpd = HTTPServer(server_address, MyServer)
    print('running server...')
    httpd.serve_forever()

run()