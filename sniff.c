// sniff.c -- simple Linux AF_PACKET raw socket sniffer
#include <arpa/inet.h>
#include <errno.h>
#include <linux/if_packet.h>
#include <net/ethernet.h> // ETH_P_ALL
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

// Print MAC address
void print_mac(const unsigned char *mac) {
    printf("%02x:%02x:%02x:%02x:%02x:%02x",
           mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

void hexdump(const unsigned char *data, int len) {
    for (int i = 0; i < len; i += 16) {
        printf("%04x  ", i);
        for (int j = 0; j < 16; ++j) {
            if (i + j < len) printf("%02x ", data[i + j]);
            else printf("   ");
        }
        printf(" ");
        for (int j = 0; j < 16 && i + j < len; ++j) {
            unsigned char c = data[i + j];
            printf("%c", (c >= 32 && c <= 126) ? c : '.');
        }
        printf("\n");
    }
}

int main() {
    int sockfd;
    unsigned char buffer[65536];

    // Create raw socket
    if ((sockfd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))) < 0) {
        perror("socket");
        return 1;
    }

    printf("Listening (Ctrl-C to stop)...\n");

    while (1) {
        ssize_t numbytes = recvfrom(sockfd, buffer, sizeof(buffer), 0, NULL, NULL);
        if (numbytes < 0) {
            perror("recvfrom");
            break;
        }

        struct ethhdr *eth = (struct ethhdr *)buffer;
        printf("\n=== Ethernet ===\n");
        printf("Src MAC: "); print_mac(eth->h_source); printf("  ");
        printf("Dst MAC: "); print_mac(eth->h_dest); printf("  ");
        printf("Type: 0x%04x\n", ntohs(eth->h_proto));

        if (ntohs(eth->h_proto) == ETH_P_IP && numbytes >= (sizeof(struct ethhdr) + sizeof(struct iphdr))) {
            struct iphdr *ip = (struct iphdr *)(buffer + sizeof(struct ethhdr));
            struct in_addr saddr, daddr;
            saddr.s_addr = ip->saddr;
            daddr.s_addr = ip->daddr;
            char src[INET_ADDRSTRLEN], dst[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &saddr, src, sizeof(src));
            inet_ntop(AF_INET, &daddr, dst, sizeof(dst));
            printf("IPv4 %s -> %s  proto=%d  header_len=%d\n", src, dst, ip->protocol, ip->ihl*4);

            if (ip->protocol == IPPROTO_TCP) {
                size_t ip_header_len = ip->ihl * 4;
                struct tcphdr *tcp = (struct tcphdr *)(buffer + sizeof(struct ethhdr) + ip_header_len);
                printf("TCP %u -> %u  seq=%u ack=%u\n", ntohs(tcp->source), ntohs(tcp->dest), ntohl(tcp->seq), ntohl(tcp->ack_seq));
                unsigned char *payload = buffer + sizeof(struct ethhdr) + ip_header_len + tcp->doff*4;
                int payload_len = numbytes - (sizeof(struct ethhdr) + ip_header_len + tcp->doff*4);
                if (payload_len > 0) {
                    printf("Payload (first 128 bytes):\n");
                    hexdump(payload, payload_len < 128 ? payload_len : 128);
                }
            } else {
                // Other IP protocols
            }
        } else {
            // Non-IP or too short
            printf("Non-IPv4 frame or short frame\n");
        }
    }

    close(sockfd);
    return 0;
}
