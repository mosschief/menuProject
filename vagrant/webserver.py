__author__ = 'mossc'
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import menu_functions
# handler

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        try:

            if self.path.endswith('/restaurants'):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    restaurants = menu_functions.getrestaurants()
                    output = ''
                    output += "<html><body><h1>Restaurants:</h1>"
                    for restaurant in restaurants:

                        output += "<h2>%s</h2>" % restaurant.name
                        output += "<a href='/restaurants/%s/edit'>edit</a><br>" %restaurant.id
                        output += "<a href='/restaurants/%s/delete'>delete</a>" %restaurant.id

                    self.wfile.write(output)

                    print(output)

            if self.path.endswith('/restaurants/new'):

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ''
                    output += "<form method='POST' enctype='multipart/form-data' \
                      action = 'new'> <h2>Enter name of restaurant:</h2> \
                     <input name='message' type='text' ><input type='submit' value='Submit'> </form>"
                    output += "</body></html>"

                    self.wfile.write(output)
                    print(output)




            if self.path.endswith('/edit'):

                    restaurntIDpath = self.path.split("/")[2]
                    myRestaurantQuery = menu_functions.get_restaurant(restaurntIDpath)

                    if myRestaurantQuery:

                        self.send_response(200)
                        self.send_header('content-type', 'text/html')
                        self.end_headers()
                        output = ''
                        output += "<form method='post' enctype='multipart/form-data' \
                          action = 'edit'> <h2>enter new name for %s: </h2> \
                         <input name='message' type='text' ><input type='submit' value='submit'> </form>" % myRestaurantQuery.name
                        output += "</body></html>"

                        self.wfile.write(output)
                        print(output)

            if self.path.endswith('/delete'):

                    restaurntIDpath = self.path.split("/")[2]
                    myRestaurantQuery = menu_functions.get_restaurant(restaurntIDpath)

                    if myRestaurantQuery:

                        self.send_response(200)
                        self.send_header('content-type', 'text/html')
                        self.end_headers()
                        output = ''
                        output += "<form method='post' action = 'delete'> <button name='delete' value='delete'>Delete</button></delete>"
                        output += "</body></html>"

                        self.wfile.write(output)
                        print(output)
        except IOError:

            self.send_error(404, 'File Not Found %s' % self.path)

    def do_POST(self):

        try:


            if self.path.endswith('/delete'):

                restaurntIDpath = self.path.split("/")[2]

                menu_functions.delete_restaurant(restaurntIDpath)

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()


            if self.path.endswith('/edit'):

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')
                    restaurntIDpath = self.path.split("/")[2]

                myRestaurantQuery = menu_functions.get_restaurant(restaurntIDpath)


                if myRestaurantQuery != []:

                    menu_functions.update_restaurant(myRestaurantQuery.id, messagecontent[0])

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()



            if self.path.endswith("/restaurants/new"):

                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                menu_functions.add_restaurant(messagecontent[0])
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()



        except:

            output = ""
            output += "<html><body>"
            output += "<h2>ERRORORORORORestaurant Added: </h2>"
            output += "<h1> </h1>"
            output += "<form method='POST' enctype='multipart/form-data' \
                      action = 'new'> <h2>Enter name of restaurant:</h2> \
                     <input name=' message' type='text' ><input type='submit' value='Submit'> </form>"
            output += "</body></html>"
            self.wfile.write(output)
            #pass




# main()

def main():

    try:

        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print('Web server running on port %s' %port)
        server.serve_forever()

    except KeyboardInterrupt:

        print('^C entered, stopping web server...')
        server.socket.close()


if __name__== '__main__':

    main()