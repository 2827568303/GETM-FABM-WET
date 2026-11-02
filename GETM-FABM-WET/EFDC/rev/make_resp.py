import base64, json, os

LIC = r"C:\Users\Public\DSI\EEMS8.4\license.lic"
OUT = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\demo_resp.txt"

lic_b64 = base64.b64encode(open(LIC, "rb").read()).decode()

payload = (
    "<XmlResult>"
    "<error>0</error>"
    "<errorMessage></errorMessage>"
    "<result>"
    "<hostIds><hostId>DISK_SERIAL_NUM=2db6323c</hostId></hostIds>"
    "<fulfillmentInfo><fulfillmentID>"
    "<id>A0ABBD96-D22B-46A2-AD1A-6D4FB37DAA47</id>"
    "<state>ACTIVE</state>"
    "<fulfillmentDate>2020-01-01</fulfillmentDate>"
    "<uniqueId>FB5BE307-6E85-410A-9265-B9389E71E38D</uniqueId>"
    "<expirationDate>2030-01-01</expirationDate>"
    "<versionDate>2030-01-01</versionDate>"
    "<product>"
    "<productName>EFDC_Explorer8.4</productName>"
    "<productVersion>8.4</productVersion>"
    "<seatsTotal>100</seatsTotal>"
    "<seatsAvailable>100</seatsAvailable>"
    "</product>"
    "<licenseText>" + lic_b64 + "</licenseText>"
    "</fulfillmentID></fulfillmentInfo>"
    "<fulfillmentIds>"
    "<fileLocation>" + LIC + "</fileLocation>"
    "<fulfillmentId>14AC1ACA-EFD2-4C01-A1DD-4397B7F19715</fulfillmentId>"
    "<UniqueId>FB5BE307-6E85-410A-9265-B9389E71E38D</UniqueId>"
    "</fulfillmentIds>"
    "</result>"
    "</XmlResult>"
)

body = json.dumps({"Status": "Success", "ReturnedData": payload, "Exception": ""}, ensure_ascii=False)
open(OUT, "w", encoding="utf-8").write(body)
print("wrote", len(body), "bytes; licenseText", len(lic_b64))
