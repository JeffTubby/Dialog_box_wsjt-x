# Configuration for FLEX Radio Beacon
#lat=-35.135731
#lon=139.249263

import aprslib
from aprslib.packets.position import PositionReport

import FLEX_RADIO_get_my_data_funcs
from FLEX_RADIO_get_my_data_funcs import get_flex_callsign as gcs
from FLEX_RADIO_get_my_data_funcs import get_flex_frequency as gff
from FLEX_RADIO_get_my_data_funcs import get_flex_mode as gfm

radio_callsign = gcs()
raw_frequency = gff() or "0"
try:
	radio_frequency = float(str(raw_frequency).split()[0])
except (TypeError, ValueError):
	radio_frequency = 0.0
radio_frequency = f"{radio_frequency:.3f}"

radio_mode = gfm()
if radio_mode == "DIGU":
	radio_mode = "FT8"

CALL = "VK5IU-8"
PASSCODE = 17888
SERVER = "aunz.aprs2.net"
PORT = 14580
ICON = "i"
LATITUDE = -35.135731
LONGITUDE = 139.249263
MESSAGE = f"{radio_callsign},{radio_frequency},{radio_mode} on air"
POSITION_PACKET = PositionReport(
    {
        "from": CALL,
        "to": "APRS",
        "path": ["TCPIP*", "qAC", "T2TAS"],
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "symbol": ICON,
        "comment": "Beacon",
    }
)
STATUS_PACKET = f"{CALL}>APRS,TCPIP*,qAC,T2TAS:>{MESSAGE}"


def validate_packet(packet):
	packet_text = str(packet)
	if ":" not in packet_text:
		raise ValueError(f"Packet missing APRS header/body separator: {packet_text!r}")
	if ">" not in packet_text.split(":", 1)[0]:
		raise ValueError(f"Packet missing sender/destination header: {packet_text!r}")
	return packet_text


def main():
	packets_to_send = [POSITION_PACKET, STATUS_PACKET]
	for packet in packets_to_send:
		try:
			packet_text = validate_packet(packet)
		except ValueError as exc:
			print(f"Invalid APRS packet: {exc}")
			return
		print(f"Prepared: {packet_text}")

	ais = aprslib.IS(CALL, passwd=str(PASSCODE), host=SERVER, port=PORT)
	try:
		ais.connect()
		for packet in packets_to_send:
			packet_text = validate_packet(packet)
			ais.sendall(packet_text)
			print(f"Sent: {packet_text}")
	finally:
		ais.close()


if __name__ == "__main__":
	main()