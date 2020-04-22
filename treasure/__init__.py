from datetime import datetime
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
#    ev.add_field('Timestamp', datetime.utcfromtimestamp(log['time']).isoformat("T") + ".000Z")
#    ev.add_field('Timestamp', str(log['time'] * 1000))
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
    ]
    
    unknown_fields = []
    for field_raw in log:
        field = field_raw.replace('_0_', '.')
        data = log[field_raw]
        
        if field in blacklist:
            continue
        if field not in includelist:
            print(f"CAUTION: unknown field {field} on event {log['event']}")
            unknown_fields += field
            continue
        
        ev.add_field(field, data)
    
    if len(unknown_fields) > 0:
        ev.add_field("unknown_fields", ','.join(unknown_fields))
    
    print(ev)
    ev.send()
    
    return { "success": "true" }

@app.route('/android/v3/event', methods=['POST'])
def android():
    print(request.headers)
    req = request.json
    print(req)
    
    # The only table we support right now is pebble.phone_events.
    resp = {}
    if 'pebble.phone_events' in req:
        resp['pebble.phone_events'] = [ submit_event(ev) for ev in req['pebble.phone_events'] ]
    return jsonify(resp)

@app.route('/heartbeat')
def heartbeat():
    return 'ok'
