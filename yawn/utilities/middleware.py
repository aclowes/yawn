from whitenoise.middleware import WhiteNoiseMiddleware


class DefaultFileMiddleware(WhiteNoiseMiddleware):
    """
    Serve index.html if not /api/ or a static file

    This allows users to navigate directly to a URL like http://127.0.0.1:8000/workflows/2
    and we return index.html, and then react-router interprets the path.
    """

    def process_request(self, request):

        if request.path_info.startswith('/api'):
            return  # handled by Django

        static_file = self.files.get(request.path_info)

        if static_file is None:
            # serve the homepage on non-existent file
            static_file = self.files.get('/index.html')

        return self.serve(static_file, request)
