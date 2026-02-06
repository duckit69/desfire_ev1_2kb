# DESFire EV1 Usage Documentation

This document explains how to interact with NXP DESFire EV1 smart cards using the provided Python codebase and an OMNIKEY contactless reader.

---

## 1. System Architecture Overview

The project is structured like a classic **Model-View-Controller (MVC)** application.

### The Three Main Parts

1.  **The Source Interface (The "Form")**
    *   **Role**: Collects data from the user.
    *   **Metaphor**: Think of this as the "Paperwork" at the warehouse output.
    *   **Actions**: User enters Driver Name, License, uploads a Photo, selects a Truck, and lists Articles.
    *   **File**: `ui/source_interface.py`

2.  **The Destination Interface (The "Report")**
    *   **Role**: Displays data read from the card and validates it.
    *   **Metaphor**: Think of this as the "Checkpoint Scanner" at the destination.
    *   **Actions**: Reads the card, checks if the mission matches the expected destination, and allows the guard to Approve/Reject.
    *   **File**: `ui/destination_interface.py`

3.  **The Main Module (The "Manager")**
    *   **Role**: Coordinates everything. It listens to the UI and talks to the Card.
    *   **Metaphor**: The "Manager" who takes the paperwork, walks to the truck (Card), and puts it in the glovebox (Writes data). At the other end, they take it out and read it.
    *   **Connections**:
        *   Receives `form_submitted` signal -> Calls `handle_form_data` -> Writes to Card.
        *   Receives `read_card` click -> Calls `on_read_card` -> Reads from Card -> Updates UI.
    *   **File**: `main.py`

---

## 2. Step-by-Step Transaction Logic

### Scenario A: Writing a Mission (At Source)

1.  **User Action**: Fills form & clicks "Submit".
2.  **Source Interface**: Bundles inputs into a dictionary `form_data`.
3.  **Main Module**:
    *   **Step 3.1: Driver App (AID `0x000001`)**
        *   Creates File `0x01` (Text Info) & File `0x02` (Photo).
        *   Authenticates with Key 0.
        *   Writes Name, License.
        *   Compresses Photo & writes it (using multiple frames if needed).
    *   **Step 3.2: Mission App (AID `0x000002`)**
        *   Creates File `0x01`.
        *   Authenticates.
        *   Writes Source, Destination, Truck Plate, initial Status (0=Pending).
    *   **Step 3.3: Article App (AID `0x000003`)**
        *   Creates Record File `0x01`.
        *   Authenticates.
        *   Loops through articles and writes them one by one.

### Scenario B: Validating Delivery (At Destination)

1.  **User Action**: Clicks "Read Card".
2.  **Main Module**:
    *   **Step 2.1**: Reads all data from the three Applications (Driver, Mission, Articles).
    *   **Step 2.2**: Sends raw data to `Destination Interface`.
3.  **Destination Interface**:
    *   **Check**: Does `card_destination` match `current_station`?
    *   **If Match**: Displays Driver Name, Photo, and Article List. Status = "Valid".
    *   **If Mismatch**: Shows "Invalid Card" error.

---

## 3. Card Usage & Concepts

### Key Concepts

*   **AID (Application ID)**: A 3-byte ID (like `0x112233`) identifying a "folder" on the card.
*   **File ID**: A 1-byte ID (like `0x01`) identifying a file within an Application.
*   **APDU**: The raw command bytes sent to the card (e.g., `0x90 0x5A ...`).
*   **Authentication (D40)**: proving you know the key (Key 0 in this project). Required before Writing/Reading protected files.

### Common Error Codes

| Status Word | Meaning on Card | What it means for proper usage |
| :--- | :--- | :--- |
| **0x91 0x00** | **Success** | Everything worked. |
| **0x91 0xAE** | **Auth Error** | Wrong Key. Check if your card uses the default factory key (`00..00`). |
| **0x91 0x7E** | **Length Error** | You tried to read/write more bytes than the file allows. Check definitions. |
| **0x91 0xAF** | **More Data** | Not an error! The card has more data. Send `0xAF` command to get the next chunk. |
| **0x91 0x9D** | **Perm. Denied** | You didn't authenticate before trying to read/write a protected file. |
| **0x91 0xF0** | **File Not Found**| You selected the wrong App or the file hasn't been created yet. |

---

## 4. Setup & Initialization

1.  **Hardware**: Plug in OMNIKEY reader.
2.  **Format Card**: If using a used card, click "Format Card" in the main menu to wipe it clean. **Warning**: This destroys all data.
3.  **Run**: `python3 main.py`
