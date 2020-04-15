#!/usr/bin/env python3
# coding=utf-8

import configparser
import json
import socket
from time import sleep

from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkcore.client import AcsClient


def domain_split(domain: str):
    parts = domain.split(".")
    if len(parts) >= 2:
        top = ".".join(parts[-2:])
        sub = ".".join(parts[:-2])
        if sub == "":
            sub = "@"
        return [sub, top]
    else:
        raise ValueError("Invalid domain.")


def get_dns_record(client: AcsClient, subdomain: str, topdomain: str):
    result = {
        "ipv4": None,
        "ipv6": None
    }
    request = DescribeDomainRecordsRequest()
    request.set_accept_format("json")
    request.set_DomainName(topdomain)
    request.set_RRKeyWord(subdomain)
    response = client.do_action_with_exception(request)
    response = json.loads(response)
    for record in response["DomainRecords"]["Record"]:
        if result["ipv4"] is None and record["Type"] == "AA":
            result["ipv4"] = record
        if result["ipv6"] is None and record["Type"] == "AAAA":
            result["ipv6"] = record
    return result


def set_dns_record(client: AcsClient, record: dict, value: str):
    request = UpdateDomainRecordRequest()
    request.set_accept_format("json")
    request.set_RecordId(record["RecordId"])
    request.set_RR(record["RR"])
    request.set_Type(record["Type"])
    request.set_Value(value)
    client.do_action_with_exception(request)
    print("Updated [%s]:\n%s %s %s\n" % (
        (record["RR"] + "." + record["DomainName"]),
        record["RecordId"],
        record["Type"],
        value
    ))


def get_ipv4_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def get_ipv6_address():
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    s.connect(("2001:4860:4860::8888", 80, 0, 0))
    ip = s.getsockname()[0]
    s.close()
    return ip


def run(config: configparser.ConfigParser):
    akid = config.get("auth", "accessKeyId", fallback="")
    aksecret = config.get("auth", "accessKeySecret", fallback="")
    client = AcsClient(akid, aksecret, "cn-hangzhou")

    domain = config.get("main", "domain", fallback="")
    subdomain, topdomain = domain_split(domain)
    records = get_dns_record(client, subdomain, topdomain)

    if records["ipv4"] is not None and config.getboolean("main", "ipv4", fallback=False):
        set_dns_record(client, records["ipv4"], get_ipv4_address())

    if records["ipv6"] is not None and config.getboolean("main", "ipv6", fallback=False):
        set_dns_record(client, records["ipv6"], get_ipv6_address())


def main():
    config = configparser.ConfigParser()
    config.read("config.ini")

    frequency = config.getint("main", "frequency", fallback=0)
    if frequency <= 0:
        run(config)
        exit(0)
    else:
        while True:
            try:
                run(config)
            except Exception as e:
                print(e)
            sleep(frequency)


if __name__ == '__main__':
    main()
