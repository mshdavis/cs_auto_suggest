from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
import json
import argparse


class SuggestionServer(object):

    def __init__(self, config):
        self.backend = self.read_json(config['input_file'])
        self.url_map = Map([
            Rule('/autosuggest', endpoint='autosuggest'),
        ])

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except HTTPException, e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def on_autosuggest(self, request):
        out_json = {
            'suggestions': self.generate_suggestions(
                self.backend,
                request.args.get('q')
            )
        }
        return Response(json.dumps(out_json))

    def read_json(self, input_file):
        '''
        Helper method to wrap opening and reading a given file.
        '''

        with open(input_file) as file:
            data = json.load(file)

        return data

    def generate_suggestions(self, backend, query):
        '''
        Function to wrap actually retrieving the suggestions.

        In more of a production environment db might be an open
        connection to something like elasticsearch instead of
        just a reference to an object in memory.
        '''
        return backend.get(query.strip().lower(), [])[:5]


def create_app(input_file='./trigram_filtered.json'):

    app = SuggestionServer({
        'input_file': input_file,
    })
    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f')
    args = vars(parser.parse_args())
    input_file = args.get('f') if args.get('f') else './trigram_filtered.json'

    print "Starting autosuggestions server with {} as database.".format(input_file)

    from werkzeug.serving import run_simple
    app = create_app(input_file=input_file)
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
