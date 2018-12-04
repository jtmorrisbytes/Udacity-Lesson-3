#!/usr/bin/env python3
#
# A *bookmark server* or URI shortener that maintains a mapping (dictionary)
# between short names and long URIs, checking that each new URI added to the
# mapping actually works (i.e. returns a 200 OK).
#
# This server is intended to serve three kinds of requests:
#
#   * A GET request to the / (root) path.  The server returns a form allowing
#     the user to submit a new name/URI pairing.  The form also includes a
#     listing of all the known pairings.
#   * A POST request containing "longuri" and "shortname" fields.  The server
#     checks that the URI is valid (by requesting it), and if so, stores the
#     mapping from shortname to longuri in its dictionary.  The server then
#     redirects back to the root path.
#   * A GET request whose path contains a short name.  The server looks up
#     that short name in its dictionary and redirects to the corresponding
#     long URI.
#
# Your job in this exercise is to finish the server code.
#
# Here are the steps you need to complete:
#
# 1. Write the CheckURI function, which takes a URI and returns True if a
#    request to that URI returns a 200 OK, and False otherwise.
#
# 2. Write the code inside do_GET that sends a 303 redirect to a known name.
#
# 3. Write the code inside do_POST that sends a 400 error if the form fields
#    are missing.
#
# 4. Write the code inside do_POST that sends a 303 redirect to the form
#    after saving a newly submitted URI.
#
# 5. Write the code inside do_POST that sends a 404 error if a URI is not
#    successfully checked (i.e. if CheckURI returns false).
#
# In each step, you'll need to delete a line of code that raises the
# NotImplementedError exception.  These are there as placeholders in the
# starter code.
#
# After writing each step, restart the server and run test.py to test it.

import http.server
import requests
from urllib.parse import unquote, parse_qs, urlparse, quote

memory = {}

form = '''<!DOCTYPE html>
<title>Bookmark Server</title>
<form method="POST">
    <label>Long URI:
        <input name="longuri">
    </label>
    <br>
    <label>Short name:
        <input name="shortname">
    </label>
    <br>
    <button type="submit">Save it!</button>
</form>
<p>URIs I know about:
<pre>
{}
</pre>
'''





def CheckURI(uri, timeout=5):
    '''Check whether this URI is reachable, i.e. does it return a 200 OK?

    This function returns True if a GET request to uri returns a 200 OK, and
    False if that GET request returns any other response, or doesn't return
    (i.e. times out).
    '''
    isValidScheme = False
    isValidNetLoc = False
    print(uri)
    URL =   urlparse(uri)
    scheme = URL[0]
    netloc = URL[1]
    path = URL[2]
    query = URL[4]
    
    if len(scheme) > 0 and (scheme == "http" or scheme == "https"):
        isValidScheme = True
    if (len(netloc) > 0 and (netloc.find("@") < 0)):
        isValidNetLoc = True
    
    if isValidScheme and isValidNetLoc:

        testURI = scheme +"://" + quote(netloc) + quote(path) + "?" + quote(query, safe="=,&,_,+")
        try:
            response = requests.get(testURI,timeout=3)
            response_netloc = urlparse(response.url).netloc
            response.raise_for_status() 
            if response_netloc != netloc:
                print("the requested hostname did not match the responding hostname")
        except TimeoutError:
            print("request timed out")
            
            return False
        except requests.exceptions.HTTPError as httpError:
            print(httpError)
        else:
            return True

    
    #print("{}://{}{}?{}".format(scheme,netloc,path,query))
    # 1. Write this function.  Delete the following line.
    else: return False

errorTemplate = '''
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="{3}; URL='{4}'" />
<title>Error {0}: {1}</title>
<body>
<h1>Error {0}: {1}</h1>
<h2>{2}</h2>
<br />
<p> redirecting to url "{4}" in {3} seconds or
 click <a href="{4}">here</a> to go back now
</p>
</body>
</html>

'''
class httpErrorCodes:
    badRequest = 400
    notFound = 404
    internalError = 500
    requestTimeout = 408

class httpResponseCodes:
    permanentRedirect = 301 
    seeOther = 303

errorStatuses = {
    400: "Bad Request",
    404: "Resource Not Found",
    408: "Request Timed out",
    500: "Internal Server Error"
}

class Shortener(http.server.BaseHTTPRequestHandler):
    def sendError(self,errCode, errMessage, redirectDelay=15, redirectURL = '/'):
        errName = errorStatuses[errCode]


        errResponse = errorTemplate.format(errCode, errName, errMessage, redirectDelay, redirectURL)
        self.send_response(errCode)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(errResponse.encode())
    def doRedirect(self, redirectTo):
        self.send_response(httpResponseCodes.seeOther)
        self.send_header("Location", redirectTo)
        self.end_headers()
    
    def do_GET(self):
        # A GET request will either be for / (the root path) or for /some-name.
        # Strip off the / and we have either empty string or a name.
        if self.path[0] == '/':
            name = unquote(self.path[1:])
        else:
            name = unquote(self.path)
        if name:
            if name in memory:
                # 2. Send a 303 redirect to the long URI in memory[name].
                #    Delete the following line.
                self.doRedirect(memory[name])
                
            else:
                # We don't know that name! Send a 404 error.
                self.sendError(httpErrorCodes.notFound, 'I dont know about the url "{}" '.format(name))
        else:
            # Root path. Send the form.
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # List the known associations in the form.
            known = "\n".join("{} : {}".format(key, memory[key])
                              for key in sorted(memory.keys()))
            self.wfile.write(form.format(unquote(known)).encode())

    def do_POST(self):
        # Decode the form data.
        length = int(self.headers.get('Content-length', 0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)

        # Check that the user submitted the form fields.
        if "longuri" not in params or "shortname" not in params:
            # 3. Serve a 400 error with a useful message.
            #    Delete the following line.
            errMessage = ""
            if "longuri" not in params and "shortname" not in params:
                errMessage = 'Fields "Long URI" and "Short name" cannot be empty'
            elif "longuri" not in params:
                errMessage = 'Field "Long URI" cannot be empty'
            else:
                errMessage = 'Field "Short name" cannot be empty'


            self.sendError(httpErrorCodes.badRequest, errMessage)

        longuri = params["longuri"][0]
        shortname = params["shortname"][0]

        if CheckURI(longuri):
            # This URI is good!  Remember it under the specified name.
            memory[shortname] = longuri

            # 4. Serve a redirect to the root page (the form).
            #    Delete the following line.
            self.doRedirect("/")
            
        else:
            # Didn't successfully fetch the long URI.

            # 5. Send a 404 error with a useful message.
            #    Delete the following line.
            self.sendError(httpErrorCodes.notFound,
                      errMessage="Failed to fetch the long uri")
            #raise NotImplementedError("Step 5 isn't written yet!")

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, Shortener)
    httpd.serve_forever()
