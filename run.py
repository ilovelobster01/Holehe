import argparse
from holehe_web import create_app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Holehe Web Interface')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the server to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    app = create_app()
    app.run(debug=args.debug, host=args.host, port=args.port)
