#!/usr/bin/env python3

import socket
import argparse
import sys

ip = '0.0.0.0'
RECV_BYTES = 512


def get_cmd_args():
    parser = argparse.ArgumentParser(
        prog='dnsserver', description='A dns server')
    parser.add_argument('-p', dest='port', type=int,
                        help='The port where the dns server should bind to')
    parser.add_argument('-n', dest='name',
                        help='The name to be translated to an ip')
    args = parser.parse_args()
    if args.port is None or args.name is None:
        parser.print_help()
        sys.exit(1)
    return args.port, args.name


def get_as_bytes(val, num_of_bytes):
    return val.to_bytes(num_of_bytes, byteorder='big')


def get_second_16_bits(data):
    # Second 16 bits - QR + OPCODE + AA + TC + RD + RA + Z + RCODE
    # QR 1 bit - 0 for request, 1 for response
    qr = '1'
    # OPCODE 4 bits - kind of query
    opcode_data = data[2] >> 3
    opcode = ''
    for b in range(1, 5):
        opcode += str((data[2] >> 3) & b)
    # AA 1 bit - Authoritative
    aa = '1'
    # TC 1 bit - truncated
    tc = '0'
    # RD 1 bit - recursion desired, should pursue query repeatedly
    rd = '0'
    # RA 1 bit - recursion available
    ra = '0'
    # Z 3 bits - Future use
    z = '000'
    # RCODE 4 bits - return code 0: no error
    rcode = '0000'
    # return int('1000010000000000', 2).to_bytes(2, 'big')
    return get_as_bytes(int(qr + opcode + aa + tc + rd + ra + z + rcode, 2), 2)


def get_domain_name(data):
    l = 0
    domain_name = ''
    index = 0
    for byte in data:
        index += 1
        if byte == 0:
            break
        if l == 0:
            l = byte
            domain_name += '.'
            continue
        domain_name += chr(byte)
        l -= 1
    question = data[:index + 4]
    qtype = data[index: index + 2]
    qclass = data[index + 2: index + 4]
    return domain_name.lstrip('.'), qtype, qclass, question


def get_response(data, name):
    # HEADER + QUESTION + ANSWER + AUTHORITY + ADDITIONAL

    # HEADER
    # Transaction id - 16 bits
    tId = data[:2]
    # 2nd 16 bits
    # QDCOUNT - Question count; 16 bits
    qdcount = data[4:6]
    # ANCOUNT - Answer count; 16 bits
    # TODO: Handle mutip[e responses
    ancount = get_as_bytes(1, 2)
    # NSCOUNT - Number of name server resource records; 16 bits
    nscount = get_as_bytes(0, 2)
    # ARCOUNt - Number of resource records; 16 bits
    arcount = get_as_bytes(0, 2)

    header = tId + \
        get_second_16_bits(data) + qdcount + ancount + nscount + arcount

    # QUESTION
    domain_name, qtype, qclass, question = get_domain_name(data[12:])
    # ANSWER
    aname = b'\xc0\x0c'
    typ = b'\x00\x01'
    clas = b'\x00\x01'
    ttl = get_as_bytes(400, 4)
    rdlen = get_as_bytes(4, 2)
    ip = '129.10.117.187'
    rdata = b''

    answer = aname + typ + clas + ttl + rdlen + rdata

    if qtype != b'\x00\x01':
        print(f'QTYPE of {qtype} not supported')
        return header + question + answer
    if qclass != b'\x00\x01':
        print(f'QCLASS of {qclass} not supported')
        return header + question + answer

    if domain_name != name:
        print(
            f'No DNS Record found for {domain_name}. {name} is the only record supported.')
        return header + question + answer

    for byte in ip.split('.'):
        rdata += bytes([int(byte)])

    answer = aname + typ + clas + ttl + rdlen + rdata
    return header + question + answer


def main():
    port, name = get_cmd_args()

    # Setup socket connection
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip, port))

    while True:
        data, addr = s.recvfrom(RECV_BYTES)
        s.sendto(get_response(data, name), addr)


if __name__ == '__main__':
    main()
