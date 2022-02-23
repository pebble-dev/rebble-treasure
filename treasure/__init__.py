from datetime import datetime
import io
import zlib
import json
import uuid

from flask import Flask, jsonify, request, abort
import libhoney
import beeline
from google.cloud import bigquery

from rws_common import honeycomb
from .settings import config
from .fields import IDENT, INCLUDE, BLOCK

app = Flask(__name__)
app.config.update(**config)
honeycomb.init(app, 'treasure')
honeycomb.sample_rate = 1

bq = bigquery.Client()
bqtable = bq.get_table(config['BIGQUERY_TABLE'])

# Update the schema, as needed.  This is a really big mess!  Ugh!
newschema = bqtable.schema[:]
modified = False
for n,field in enumerate(newschema):
    if field.name == 'data':
        # Construct a new one.
        fields = list(field.fields)
        for maybeins in [*IDENT, *INCLUDE]:
            newname = maybeins.replace(".", "_0_") # Everything old is new again, I suppose.
            found = False
            for subfield in fields:
                if subfield.name == newname:
                    found = True
                    break
            if found:
                continue
            modified = True
            print(f"updating BigQuery schema with new field {newname}")
            fields.append(bigquery.SchemaField(newname, "STRING", mode = "NULLABLE"))
        if modified:
            newschema[n] = bigquery.SchemaField('data', 'RECORD', fields = fields)
        break
if modified:
    bqtable.schema = newschema
    bqtable = bq.update_table(bqtable, ["schema"])

honey = libhoney.Client(writekey = config['HONEYCOMB_WRITEKEY'], dataset = config['HONEYCOMB_CLIENT_DATASET'])

def submit_event(log, extra = {}):
    bqrow = {}
    bqrow["event_name"] = log["event"]
    bqrow["time"] = log["time"]
    
    if 'rebble.user' in extra and 'rebble.noident' not in extra:
        bqrow['rebble_user'] = extra['rebble.user']
    if 'rebble.subscribed' in extra and 'rebble.noident' not in extra:
        bqrow['rebble_subscribed'] = extra['rebble.subscribed']
    
    bqrow["data"] = {}

    ev = honey.new_event()
    ev.add_field('meta.span_type', 'span_event')
    # Make up a trace_id, else Honeycomb chokes.
    ev.add_field('trace.trace_id', str(uuid.uuid4()))
    ev.created_at = datetime.utcfromtimestamp(log['time'])
    ev.add_field('name', log['event'])
    
    # Users may wish to avoid handing us identifying information into
    # analytics by overriding the write key; if so, ignore watch serial
    # number information from the phone.
    noident = 'rebble.noident' in extra
    
    # Iterate through fields, providing data for ones in the inclusion list,
    # and crying about anything that we don't recognize.
    includelist = [
        *INCLUDE,
        *(IDENT if not noident else []),
    ]
    
    # Don't complain about ones on the blacklist.
    blocklist = [
        *BLOCK,
        *(IDENT if noident else []),
    ]
    
    unknown_fields = []
    for field_raw in log:
        field = field_raw.replace('_0_', '.')
        data = log[field_raw]
        
        if field in blocklist:
            continue
        if field not in includelist:
            print(f"CAUTION: unknown field {field} on event {log['event']}")
            unknown_fields += [field]
            continue
        
        ev.add_field(field, data)
        bqrow["data"][field_raw] = str(data)

    for field in extra:
        ev.add_field(field, extra[field])

    if len(unknown_fields) > 0:
        ev.add_field("unknown_fields", ','.join(unknown_fields))
        bqrow["unknown_fields"] = unknown_fields
    
    ev.send()
    
    return bqrow

# { "success": "true" }

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
        toinsert = [ submit_event(ev, extra) for ev in req['pebble.phone_events'] ]
        errors = bq.insert_rows_json(config['BIGQUERY_TABLE'], toinsert)
        if errors != []:
            raise RuntimeError(errors)
        # Sigh.
        resp['pebble.phone_events'] = [ { "success": "true" } for _ in toinsert ]
        beeline.add_context_field('treasure.events.count', len(resp['pebble.phone_events']))
        
    return jsonify(resp)

@app.route('/heartbeat')
def heartbeat():
    return 'ok'
