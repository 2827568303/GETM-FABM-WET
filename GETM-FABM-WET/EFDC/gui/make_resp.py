# -*- coding: utf-8 -*-
"""Write a complete DSI fulfillResponse XML into rev/demo_resp.txt (the fake server's answer)."""
import json

MACHINE = "DISK_SERIAL_NUM=2db6323c"
XML = """<XmlResult>
  <error>0</error>
  <result>
    <hostIds>
      <hostId>{machine}</hostId>
    </hostIds>
    <fulfillmentInfo>
      <fulfillmentID>
        <state>ACTIVE</state>
        <id>14AC1ACA-EFD2-4C01-A1DD-4397B7F19715</id>
        <fulfillmentDate>2020-01-01T00:00:00</fulfillmentDate>
        <expirationDate>2030-01-01T00:00:00</expirationDate>
        <versionDate>2030-01-01T00:00:00</versionDate>
        <uniqueId>FB5BE307-6E85-410A-9265-B9389E71E38D</uniqueId>
        <product>
          <productName>EFDC_Explorer8.4</productName>
          <productVersion>8.4.3</productVersion>
          <seatsTotal>100</seatsTotal>
          <seatsAvailable>100</seatsAvailable>
        </product>
        <licenseText>SERIAL_NUM=2db6323c</licenseText>
      </fulfillmentID>
    </fulfillmentInfo>
    <fulfillmentIds>
      <fileLocation>C:\\Users\\Public\\DSI\\EEMS8.4\\license.lic</fileLocation>
      <fulfillmentId>14AC1ACA-EFD2-4C01-A1DD-4397B7F19715</fulfillmentId>
      <UniqueId>FB5BE307-6E85-410A-9265-B9389E71E38D</UniqueId>
    </fulfillmentIds>
    <UserInfo>
      <FirstName>E</FirstName>
      <LastName>F</LastName>
      <TelephoneNumber>0</TelephoneNumber>
      <Organization>D</Organization>
      <OrganizationAddress>A</OrganizationAddress>
      <CountryCode>CN</CountryCode>
      <Occupation>M</Occupation>
    </UserInfo>
  </result>
</XmlResult>""".format(machine=MACHINE)

payload = {"Status": "Success", "ReturnedData": XML, "Exception": ""}
out = json.dumps(payload, ensure_ascii=False)
open(r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\rev\demo_resp.txt", "w", encoding="utf-8").write(out)
print("wrote %d bytes" % len(out))
