#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AWS related functions and classes and etc
"""
import os
import json
import ipaddress
import logging as log
import requests
import arrow
from lib import settings


def ip_pools_v4():
    """
    Args: None
    Doc: If in the local data pool does not exist, or
    if the local data is too old, pull down the IP ranges from AWS
    """
    cwd = os.path.dirname(__file__)
    json_file = os.path.join(cwd, "../data/ip-ranges.json")
    exists = os.path.isfile(json_file)
    good = True
    if exists:
        with open(json_file) as json_file_data:
            data = json.load(json_file_data)
            created = data["createDate"]
            created_date = arrow.get(created, "YYYY-MM-DD-HH-mm-SS")
            now_date = arrow.utcnow()
            shift_date = now_date.shift(days=settings.AWS_POOL_MAX_AGE)
            if created_date < shift_date:
                log.debug("This is old, let's get a new one if we can")
                good = False
            else:
                log.debug("This is fresh just give it back")
                return data["prefixes"]
    else:
        good = False
    if not good:
        ranges = requests.get("https://ip-ranges.amazonaws.com/ip-ranges.json")
        print(ranges)
        if ranges.status_code == 200:
            with open(json_file, "wb") as handle:
                for block in ranges.iter_content(1024):
                    handle.write(block)
            return ranges.content
        else:
            log.info("Pulling from remote failed")
            if exists:
                log.debug("Failing back to the lastest")
                return data["prefixes"]
            else:
                log.error("Error loading either local or remote")
                return False


def map_ipv4_to_service(ipv4):
    """
    Args: A single IPv4 IP adress
    Return: The name of the service, if the IP belongs to an AWS network, None if not AWS address
    """
    aws_pools = ip_pools_v4()
    if ipaddress.IPv4Address(ipv4).is_private:
        return
    for pool in aws_pools:
        if ipaddress.IPv4Address(ipv4) in ipaddress.IPv4Network(pool["ip_prefix"]):
            log.info("Match found: %s", pool)
            return pool["service"]
    return


def map_ipv4_to_region(ipv4):
    """
    Args: A single IPv4 IP adress
    Return: The region code of the IP if the IP belongs to an AWS network, None if not AWS address
    """
    aws_pools = ip_pools_v4()
    if ipaddress.IPv4Address(ipv4).is_private:
        return
    for pool in aws_pools:
        if ipaddress.IPv4Address(ipv4) in ipaddress.IPv4Network(pool["ip_prefix"]):
            log.info("Match found: %s", pool)
            return pool["region"]
    return


def is_aws_service_ipv4(ipv4, service):
    """
    Args:
      A single IPv4 IP adress
      An AWS service marked in the ranges file
    Return: True if the IP belongs to the service in quesion, False if not
    Valid / marked services at the moment:
      AMAZON
      AMAZON_CONNECT
      API_GATEWAY
      CLOUD9
      CLOUDFRONT
      CODEBUILD
      DYNAMODB
      EC2
      EC2_INSTANCE_CONNECT
      GLOBALACCELERATOR
      ROUTE53
      ROUTE53_HEALTHCHECKS
      S3
      WORKSPACES_GATEWAYS
    """
    aws_pools = ip_pools_v4()
    if ipaddress.IPv4Address(ipv4).is_private:
        return False
    for pool in aws_pools:
        if (
            ipaddress.IPv4Address(ipv4) in ipaddress.IPv4Network(pool["ip_prefix"])
            and pool["service"] == service
        ):
            log.info("That's an %s IP in %s", service, pool["region"])
            return True
    return False