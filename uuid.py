# Creates unique UUIDs

import uuid

# Generate random UUIDs
service_uuid = str(uuid.uuid4())
characteristic_uuid = str(uuid.uuid4())

print("Service UUID:", service_uuid)
print("Characteristic UUID:", characteristic_uuid)