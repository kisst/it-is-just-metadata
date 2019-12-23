#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
# import pytest
from lib import aws

KNOWN_R53_IP = "205.251.192.0"
KNOWN_R53_HC_IP = "107.23.255.0"


def test_aws_ip_mapping_private_c():
    """
    Private Ip pools can't be part of AWS ranges
    """
    assert aws.map_ipv4_to_service("192.168.0.1") is None


def test_aws_ip_mapping_private_a():
    """
    Private Ip pools can't be part of AWS ranges
    """
    assert aws.map_ipv4_to_service("10.0.0.1") is None


def test_aws_ip_mapping_private_b():
    """
    Private Ip pools can't be part of AWS ranges
    """
    assert aws.map_ipv4_to_service("172.16.0.1") is None


def test_service_with_known_aws_ip_match():
    """
    Route53 is pretty static let's use that for testing.
    """
    assert aws.is_aws_service_ipv4(KNOWN_R53_IP, "ROUTE53")


def test_service_with_known_aws_ip_no_match():
    """
    Route53 is pretty static let's use that for testing.
    """
    assert not aws.is_aws_service_ipv4(KNOWN_R53_IP, "")


def test_region_with_known_aws_ip():
    """
    Route53 is pretty static let's use that for testing.
    """
    assert aws.map_ipv4_to_region(KNOWN_R53_IP) == "GLOBAL"


def test_map_ipv4_to_multi_service():
    """
    This pool is used for more then one service no one2one mapping possible
    """
    assert aws.map_ipv4_to_service(KNOWN_R53_IP) == "ROUTE53"


def test_map_ipv4_to_single_service():
    """
    This pool at the time of writing the test is used only for Route53 HC
    """
    assert aws.map_ipv4_to_service(KNOWN_R53_HC_IP) == "ROUTE53_HEALTHCHECKS"


# @pytest.mark.skip(reason="This test is not ready, need to figure out mocking")
def test_ranges_fetch_old():
    """
    Let's fake that the data is old, and see it fetched
    """
    # mock the settings here, but how ?
    ranges = aws.ip_pools_v4()
    assert ranges


# @pytest.mark.skip(reason="Local testing cause the API endpoint to limit")
def test_ranges_fetch_missing():
    """
    Let's make sure no local copy exist, and see it fetched
    """
    cwd = os.path.dirname(__file__)
    json_file = os.path.join(cwd, "../../../data/ip-ranges.json")
    # remove it so that it will be pulled
    os.remove(json_file)
    ranges = aws.ip_pools_v4()
    assert ranges


# @pytest.mark.skip(reason="This test is not ready, need to figure out mocking")
def test_ranges_fetch_failed():
    """
    Let's make sure no local copy exist, and see it fetched
    """
    # make sure the fetch failed, but how ?
    ranges = aws.ip_pools_v4()
    assert ranges
