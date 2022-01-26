#!/usr/bin/env python3

import logging

from prometheus_client import Summary
from prometheus_client.core import CounterMetricFamily, UnknownMetricFamily
from utils import getAWS

logger = logging.getLogger(__name__)


class AWSCollector(object):
    """AWS collector."""

    def collect(self):
        """Collects AWS Data. This method will be called on registration and
           every time the metrics are requested.

        Yields:
            AWS metrics.
        """

        logger.debug('Collecting metrics...')

        for key1, value1 in getAWS().items():
            # key1: metric name
            # value1: metric values for all projects

            counterMetric = UnknownMetricFamily("%s" % key1,
                                                'Help text',
                                                labels=['platform','projectid'])

            for key2, value2 in value1.items():
                # key2: project name
                # value2: metric value for project

                counterMetric.add_metric([
                            "AWS",
                            str(key2)], # this is project identifier
                            value2)

            yield counterMetric

        logger.debug('Metrics collection finished')

    def collect_og(self):
        """Collects AWS Data. This method will be called on registration and
           every time the metrics are requested.

        Yields:
            AWS metrics.
        """

        logger.debug('Collecting metrics...')

        data = getAWS()
        month = data["month"]
        del data["month"]

        for key1, value1 in data.items():
            # key1: metric name
            # value1: metric values for all projects

            counterMetric = UnknownMetricFamily("testAWS_%s" % key1,
                                                'Help text',
                                                labels=['month','projectid'])

            for key2, value2 in value1.items():
                # key2: project name
                # value2: metric value for project

                counterMetric.add_metric([
                            month,
                            str(key2)], # this is project identifier
                            value2)

            yield counterMetric

        logger.debug('Metrics collection finished')
