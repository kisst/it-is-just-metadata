#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the AWS functions
"""
import os
import json
import arrow
# import pytest
from pathlib import Path
from lib import aws
from lib import settings

# TO DO create a dummy IP-ranges.json for testing
KNOWN_R53_IP = "205.251.192.0"
KNOWN_R53_HC_IP = "107.23.255.0"
KNOWN_NOT_AWS_IP = "8.8.8.8"


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


def test_service_with_known_aws_ip_fail_fast():
    """
    Route53 is pretty static let's use that for testing.
    """
    assert not aws.is_aws_service_ipv4("192.168.0.1", "")


def test_region_with_known_aws_ip():
    """
    Route53 is pretty static let's use that for testing.
    """
    assert aws.map_ipv4_to_region(KNOWN_R53_IP) == "GLOBAL"


def test_region_with_known_not_aws_ip():
    """
    Route53 is pretty static let's use that for testing.
    """
    assert aws.map_ipv4_to_region(KNOWN_NOT_AWS_IP) is None


def test_region_fail_fast():
    """
    Route53 is pretty static let's use that for testing.
    """
    assert aws.map_ipv4_to_region('192.168.0.1') is None


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


def test_ranges_fetch_old():
    """
    Let's fake that the data is old, and see it fetched
    """
    this_file = os.path.dirname(__file__)
    proot = Path(this_file).parent.parent.parent
    json_file = proot.joinpath("data", "ip-ranges.json")
    now_date = arrow.utcnow()
    too_much_shift = settings.AWS_POOL_MAX_AGE - 1
    shift_date = now_date.shift(days=too_much_shift)

    with open(json_file, 'r') as file_data:
        data = json.load(file_data)
        data['createDate'] = shift_date.format("YYYY-MM-DD-HH-mm-SS")
    os.remove(json_file)
    with open(json_file, 'w') as file_data:
        json.dump(data, file_data, indent=4)
    ranges = aws.ip_pools_v4()
    assert ranges


# @pytest.mark.skip(reason="Local testing cause the API endpoint to limit")
def test_ranges_fetch_missing():
    """
    Let's make sure no local copy exist, and see it fetched
    """
    this_file = os.path.dirname(__file__)
    proot = Path(this_file).parent.parent.parent
    json_file = proot.joinpath("data", "ip-ranges.json")
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
