import time
import random

WINDOW_SIZE = 4
SEQ_NUM_MAX = 8
TOTAL_FRAMES = 10

base = 0
next_seq_num = 0
frames_to_send = list(range(TOTAL_FRAMES))

def is_window_full():
    return (next_seq_num - base) % SEQ_NUM_MAX == WINDOW_SIZE

def simulate_channel(packet, is_ack=False):
    time.sleep(0.05)
    if random.random() < 0.15:
        ptype = "ACK" if is_ack else "FRAME"
        print(f"   [Channel] !!! {ptype} {packet} LOST in transit. ")
        return None
    return packet

def sender_send():
    global next_seq_num
    while next_seq_num < TOTAL_FRAMES and not is_window_full():
        seq_num = next_seq_num % SEQ_NUM_MAX
        print(f"| SENDER | Sending Frame {next_seq_num} (Seq# {seq_num}). Window: [{base % SEQ_NUM_MAX}-{((base + WINDOW_SIZE - 1) % SEQ_NUM_MAX) if WINDOW_SIZE>0 else base}]")
        sent_frame = simulate_channel(seq_num)
        if sent_frame is not None:
            next_seq_num += 1

def receiver_receive(frame_seq_num, expected_frame):
    if frame_seq_num == expected_frame:
        print(f"| RECEIVER | Received expected Frame (Seq# {frame_seq_num}).")
        ack_num = (expected_frame + 1) % SEQ_NUM_MAX
        print(f"| RECEIVER | Sending ACK for Seq# {ack_num} (Requesting next frame).")
        return simulate_channel(ack_num, is_ack=True)
    else:
        print(f"| RECEIVER | Received OUT-OF-ORDER Frame (Seq# {frame_seq_num}). Discarding.")
        ack_num = expected_frame
        print(f"| RECEIVER | Resending ACK for Seq# {ack_num} (To prompt retransmission).")
        return simulate_channel(ack_num, is_ack=True)

def sender_receive_ack(ack_num):
    global base
    acked_seq = (ack_num - 1 + SEQ_NUM_MAX) % SEQ_NUM_MAX
    base_seq = base % SEQ_NUM_MAX
    if (base_seq <= acked_seq < (base + WINDOW_SIZE) % SEQ_NUM_MAX):
        if ack_num == (base + 1) % SEQ_NUM_MAX:
            base += 1
            print(f"| SENDER | Received ACK for Seq# {ack_num}. Window slides to Base {base % SEQ_NUM_MAX}.")
        elif ack_num > (base + 1) % SEQ_NUM_MAX or ack_num < (base % SEQ_NUM_MAX):
            if base % SEQ_NUM_MAX != ack_num:
                frames_acked = (ack_num - (base % SEQ_NUM_MAX) + SEQ_NUM_MAX) % SEQ_NUM_MAX
                if frames_acked > 0 and frames_acked <= WINDOW_SIZE:
                    base += frames_acked
                    print(f"| SENDER | Received CUMULATIVE ACK for Seq# {ack_num}. Window slides forward by {frames_acked} frames to Base {base % SEQ_NUM_MAX}.")
            else:
                print(f"| SENDER | Received DUPLICATE/INVALID ACK {ack_num}. Window remains at Base {base % SEQ_NUM_MAX}.")
    else:
        print(f"| SENDER | Received OUT-OF-WINDOW ACK {ack_num}. Discarding.")

print("--- SLIDING WINDOW PROTOCOL (GO-BACK-N) SIMULATION ---")
print(f"Total Frames: {TOTAL_FRAMES} | Window Size: {WINDOW_SIZE} | Sequence Space: 0 to {SEQ_NUM_MAX-1}\n")

expected_frame = 0
frame_buffer = {}

while base < TOTAL_FRAMES:
    sender_send()
    for i in range(base, next_seq_num):
        frame_seq_num = i % SEQ_NUM_MAX
        if i not in frame_buffer:
            if random.random() > 0.1:
                ack_to_sender = receiver_receive(frame_seq_num, expected_frame)
                if ack_to_sender is not None:
                    sender_receive_ack(ack_to_sender)
                    if base > i:
                        expected_frame = base % SEQ_NUM_MAX
                        frame_buffer[i] = True
            if i == base and i not in frame_buffer:
                if random.random() < 0.15:
                    print(f"| SENDER | TIMEOUT for Frame {base}. Retransmitting frames from Base {base % SEQ_NUM_MAX}.")
                    next_seq_num = base
                    break
    time.sleep(0.1)

print("\n--- SIMULATION COMPLETE ---")
print(f"Total Frames Sent and Acknowledged: {TOTAL_FRAMES}")
