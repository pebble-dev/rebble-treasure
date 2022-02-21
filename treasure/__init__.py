from datetime import datetime
import io
import zlib
import json
import uuid

from flask import Flask, jsonify, request, abort
from libhoney import Client
import beeline

from rws_common import honeycomb
from .settings import config

app = Flask(__name__)
app.config.update(**config)
honeycomb.init(app, 'treasure')
honeycomb.sample_rate = 1

client = Client(writekey = config['HONEYCOMB_WRITEKEY'], dataset = config['HONEYCOMB_CLIENT_DATASET'])

def submit_event(log, extra = {}):
    ev = client.new_event()
    ev.add_field('meta.span_type', 'span_event')
    # Make up a trace_id, else Honeycomb chokes.
    ev.add_field('trace.trace_id', str(uuid.uuid4()))
    ev.created_at = datetime.utcfromtimestamp(log['time'])
    ev.add_field('name', log['event'])
    
    # Users may wish to avoid handing us identifying information into
    # analytics by overriding the write key; if so, ignore watch serial
    # number information from the phone.
    noident = 'rebble.noident' in extra
    identfields = [
        'device.remote_device.serial_number',
        'device.remote_device.bt_address',
    ]
    
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
        *(identfields if not noident else []),
    ]
    
    # Don't complain about ones on the blacklist.
    blacklist = [
        'session',
        'identity.serial_number',
        'identity.device',
        'identity.user',
        'time',
        'event',
        'pebble_event_uuid',
        'device_phone.name',
        'keen.timestamp',
        'keen.location.coordinates',
        *(identfields if noident else []),
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

    for field in extra:
        ev.add_field(field, extra[field])

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
    
    extra = {}
    if 'X-Td-Write-Key' in request.headers:
        extra = dict([param.split('=') for param in request.headers['X-Td-Write-Key'].split(',')])
    
    # The only table we support right now is pebble.phone_events.
    resp = {}
    if 'pebble.phone_events' in req:
        resp['pebble.phone_events'] = [ submit_event(ev, extra) for ev in req['pebble.phone_events'] ]
        beeline.add_context_field('treasure.events.count', len(resp['pebble.phone_events']))
    return jsonify(resp)

@app.route('/heartbeat')
def heartbeat():
    return 'ok'
