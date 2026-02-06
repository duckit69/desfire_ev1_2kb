# Mission Card Manager (PyQt5 + MIFARE DESFire EV1)

Desktop application to manage **delivery missions** on a **MIFARE DESFire EV1** smart card. The app has two main roles:

- **Source interface**: create a mission, assign a driver and truck, select articles, and write everything to the card.  
- **Destination interface**: read a card at the delivery point, validate the mission against expected missions, and show driver + article details.

Smart card access is implemented with a small DESFire helper library (`desfire_ev1`), using DES authentication and APDU commands.

## Smart Card Data Model

Each card is organized into **applications** and **files** on the DESFire EV1 PICC.

### Applications

The PICC contains these application IDs (AIDs):

* 000000 – Master application (PICC, used for formatting/auth)
* 000001 – Driver application
* 000002 – Mission application
* 000003 – Articles application

All applications currently use **DES key 0x00** and allow operations after authenticating with key 0.

### Driver Application (`000001`)

**Driver info file** (`file_id = 0x01`, Standard file):  
Fixed string: driver_name + driver_license (20 bytes)

**Driver photo file** (`file_id = 0x02`, Standard file):

[meta_length 4B] + [JSON metadata] + [compressed image data]

### Mission Application (`000002`)

**Mission file** (`file_id = 0x01`, Standard file, 57 bytes):

| Field        | Offset | Size | Description                    |
|--------------|--------|------|--------------------------------|
| mission_id   | 0      | 8    | `MSN00001`                     |
| truck_id     | 8      | 8    | Truck plate                    |
| status       | 16     | 1    | 0=Pending, 1=InTransit, 2=Delivered |
| source       | 17     | 20   | Source location                |
| destination  | 37     | 20   | Destination location           |

### Articles Application (`000003`)

**Articles file** (`file_id = 0x01`, Linear record file):

record_size = 8 bytes, max_records = 50

Record layout:
* Bytes 0-3: 4-letters code ("LAPT")    
* Bytes 4-7: quantity (32-bit little-endian)


## Smart Card Operations

### Format Card
1. Select master app 000000
2. Authenticate with PICC master key (DES all zeros)
3. Send FormatPICC (0xFC)

### Source Interface (Write Mission)

Create apps 000001/000002/000003.

For each app:
1. Select app
2. Create files
3. Authenticate (key 0)
4. Write data

### Destination Interface (Read + Validate)
* Read mission (app 000002) → parse 57-byte file
* Read driver info + photo (app 000001)
* Read all article records (app 000003)
* Compare mission_id against expected missions for destination
    * If valid: display driver + articles
    * On approve: update status byte to 2 (Delivered)


## DESFire Helper Library (`desfire_ev1`)

## DesfireCard
├── connect via PC/SC  
├── authenticate(key_number, key_value) → DES CBC challenge/response  
├── select_application(aid)  
└── format_card()

## ApplicationManager
├── create_application(aid, key_settings=0x0B, num_keys=1)  
└── delete_application(aid)

## FileManager
├── **Standard files:**  
│ ├── create_standard_file(file_id, size)  
│ ├── write_data(file_id, offset, data)  
│ └── read_data(file_id, offset, length)  
├── **Record files:**  
│ ├── create_linear_record_file(file_id, record_size, max_records)  
│ ├── write_record(file_id, offset, data)  
│ └── read_records(file_id, record_offset, num_records)  
└── **Utils:** to_3bytes(), to_4bytes(), from_4bytes()

utils.py: byte from/to integer conversion

crypto.py: DES CBC encrypt/decrypt

## Running the Application

```bash
pip install -r requirements.txt
python main.py
```
## Requirements:

* PC/SC smart card reader
* MIFARE DESFire EV1 (EV2/EV3 compatible)

# Workflow

1. Source: Driver fills form → card is written with mission + driver + articles
2. Destination: Tap card → validates mission_id → shows driver photo + article table
3. Approve: status → Delivered, update database

# Project Structure

## Root Directory
├── main.py                 
├── ui/  
│   ├── source_interface.py 
│   └── destination_interface.py  
├── desfire_ev1/             
│   ├── card.py  
│   ├── applications.py  
│   ├── files.py  
│   ├── crypto.py  
│   └── utils.py  
└── pic_codec.py           