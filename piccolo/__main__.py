import argparse
from pathlib import Path

from src.rest_api import RestAPI


def main() -> None:
    parser = argparse.ArgumentParser(description="Piccolo REST API server")
    parser.add_argument("--config", type=Path, help="Path to YAML configuration", required=False)
    parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    parser.add_argument("--port", type=int, default=8000, help="Bind port")
    args = parser.parse_args()

    api = RestAPI(config=args.config) if args.config else RestAPI()
    api.start(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
