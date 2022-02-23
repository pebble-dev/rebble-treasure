IDENT = [
    'device.remote_device.serial_number',
    'device.remote_device.bt_address',
    'data.watch_serial_number',
]

INCLUDE = [
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
    'data.firmware.fw_type',
    'data.firmware.fw_version',
    'data.firmware.fw_version_shortname',
    'data.firmware.fw_version_timestamp',
    'data.language_displayed_count',
    'data.accepted',
    'data.type_of_mobile_alert_invoked',
    
    # BLE failure
    'data.transport',
    'data.attempt_count',
    'data.set_goal_disconnect',
    'data.has_ever_connected',
    'data.failing_state',
    'data.failing_gatt_status',
    'data.adapter_enabled',
    'data.reason',
    'data.is_already_connected',
    'data.attempt_count',
    'data.secs_since_adapter_enabled',
    'data.unfaithful_reason',
    
    # voice
    'data.error_returned',
    'data.failed_to_connect',
    'data.speech_sent_timestamp_secs',
    'data.voice_language',
    'data.nuance_session_id',
    'data.data_volume_bytes',
    'data.latency_ms',
    'data.transcription_length_bytes',
    'data.audio_duration_ms',
    'data.is_first_party_app',
    'data.nuance_host',
    'data.voice_dictation_http_code',
]

BLOCK = [
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
    
    # notifications
    'data.app_name',
    'data.hasContentIntent',
    'data.app_version',
    'data.notifications_enabled',
    'data.sentToWatch',
    'data.wearActions',
    'data.actions',
    'data.pagesCount',
    'data.contentAction',
    'data.package_name',
    'data.isClearable',
    'data.wearActionCount',
    'data.isDuplicate',
    'data.actionCount',
    'data.notifications_muted',
    'data.source',
    'data.hasMessagingStyle',
    'data.isGroupSummary',
    'data.action_type',
    'data.action_title',
    
    # local BT address
    'data.bt_address',
    'data.serial', # ???
    
    # voice
    'data.nuance_context',
    'data.application_name',
    'data.application_uuid',
    
    'data.token', # onboarding complete
    'data.uuid', # watchface changed
    
    # health
    'data.switch_id',
    'data.enabled',
]
