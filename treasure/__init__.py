from datetime import datetime
import io
import zlib
import json
import uuid

from flask import Flask, jsonify, request, abort
from libhoney import Client

from .settings import config

app = Flask(__name__)
app.config.update(**config)

client = Client(writekey = config['HONEYCOMB_KEY'], dataset = config['HONEYCOMB_CLIENT_DATASET'], debug = True)

def submit_event(log):
    ev = client.new_event()
    ev.add_field('meta.span_type', 'span_event')
    # Make up a trace_id, else Honeycomb chokes.
    ev.add_field('trace.trace_id', str(uuid.uuid4()))
    ev.created_at = datetime.utcfromtimestamp(log['time'])
    ev.add_field('name', log['event'])
    
    # Iterate through fields, providing data for ones in the inclusion list,
    # and crying about anything that we don't recognize.
    includelist = [
        'device_phone.model',
        'data.screen',
        'app.locale',
        'app.version_code',
        'device.remote_device.transport',
        'collection',
        'device.remote_device.firmware_description.version.firmware.recovery_fw_version',
        'app.version',
        'device_phone.locale',
        'platform',
        'device_phone.system_name',
        'device.remote_device.hw_version',
        'device.remote_device.type',
        'device_phone.system_version',
        'device.remote_device.firmware_description.version.firmware.fw_version',
        'device_phone.supports_ble',
        'carrier_info.mobile_network_code',
        'device_phone.is_jailbroken',
        'device.remote_device.firmware_description.version.firmware.fw_version_language_isocode',
        'carrier_info.mobile_country_code',
        'app_state.onboarding_complete',
        'data.button_id',
        'device_phone.system_build',
        'carrier_info.carrier_name',
        'device.remote_device.firmware_description.version.firmware.fw_version_language_version',
        'device.remote_device.firmware_description.version.firmware.bootloader_version',
        'carrier_info.iso_country_code',
        'device.remote_device.firmware_description.version.firmware.fw_version_timestamp',
    ]
    
    # Don't complain about ones on the blacklist.
    blacklist = [
        'session',
        'device.remote_device.serial_number',
        'identity.serial_number',
        'device.remote_device.bt_address',
        'identity.device',
        'identity.user',
        'time',
        'event',
        'pebble_event_uuid',
        'device_phone.name',
        'keen.timestamp',
        'keen.location.coordinates',
    ]
    
    unknown_fields = []
    for field_raw in log:
        field = field_raw.replace('_0_', '.')
        data = log[field_raw]
        
        if field in blacklist:
            continue
        if field not in includelist:
            print(f"CAUTION: unknown field {field} on event {log['event']}")
            unknown_fields += [field]
            continue
        
        ev.add_field(field, data)
    
    if len(unknown_fields) > 0:
        ev.add_field("unknown_fields", ','.join(unknown_fields))
    
    ev.send()
    
    return { "success": "true" }

@app.route('/ios/v3/event', methods=['POST'])
@app.route('/android/v3/event', methods=['POST'])
def event_post():
    print(request.headers)
    if getattr(request, 'content_encoding', None) == 'deflate':
        rdata = zlib.decompress(request.data)
    else:
        rdata = request.data
    req = json.loads(rdata)
    
    # The only table we support right now is pebble.phone_events.
    resp = {}
    if 'pebble.phone_events' in req:
        resp['pebble.phone_events'] = [ submit_event(ev) for ev in req['pebble.phone_events'] ]
    return jsonify(resp)

@app.route('/heartbeat')
def heartbeat():
    return 'ok'
