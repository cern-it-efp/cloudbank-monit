#!/usr/bin/env python3

import sys
import signal
import time
import logging
import argparse

from prometheus_client import start_http_server, PROCESS_COLLECTOR, PLATFORM_COLLECTOR, Summary
from prometheus_client.core import REGISTRY, CounterMetricFamily
from collector import YandexCollector
import config


logger = logging.getLogger(__name__)


def parse_args():
    """Parse the command line arguments."""

    parser = argparse.ArgumentParser(
        prog = 'yandex-exporter',
        description = 'Python Yandex Prometheus Exporter'
    )

    parser.add_argument(
        '-p', '--port',
        dest = 'port',
        type = int,
        default = config.PORT,
        metavar = 'PORT',
        required = False,
        help = f'Serve the exporter on this port (Default: {config.DEFAULT_PORT})'
    )

    parser.add_argument(
        '--log-level',
        dest = 'log_level',
        type = str,
        default = config.LOG_LEVEL,
        metavar = 'LEVEL',
        required = False,
        help = f'Logging level (Default: {config.DEFAULT_LOG_LEVEL})'
    )

    parser.add_argument(
        '--log-format',
        dest = 'log_format',
        type = str,
        default = config.LOG_FORMAT,
        metavar = 'FORMAT',
        required = False,
        help = f'Logging format string'
    )

    parser.add_argument(
        '--log-datefmt',
        dest = 'log_datefmt',
        type = str,
        default = config.LOG_DATEFMT,
        metavar = 'DATE_FORMAT',
        required = False,
        help = f'Logging date/time format string'
    )

    return parser.parse_args()


def main():
    """Register the Yandex collector and start a HTTP server."""

    args = parse_args()

    logging.basicConfig(
        format = args.log_format,
        datefmt = args.log_datefmt,
        level = args.log_level.upper()
    )

    try:
        # Unregister default collectors https://github.com/prometheus/client_python/issues/414
        REGISTRY.unregister(PROCESS_COLLECTOR)
        REGISTRY.unregister(PLATFORM_COLLECTOR)
        REGISTRY.unregister(REGISTRY._names_to_collectors['python_gc_objects_collected_total'])
        # Register the collector (its 'collect' method is called on registration)
        REGISTRY.register(YandexCollector())
    except BaseException as exc:
        logger.exception('There was an error starting the Yandex exporter')
        sys.exit(1)

    # Start an http server, to serve requests comming from the Prometheus server
    start_http_server(args.port)

    logger.info(f'Serving the application on port %s' % args.port)

    # Keep the application running
    while True:
        time.sleep(1)


if __name__ == '__main__':
    def signal_handler(sig, frame):
        logger.info('Stopping the server...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    main()
