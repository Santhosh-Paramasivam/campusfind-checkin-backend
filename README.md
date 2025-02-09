# CampusFind - RFID system backend  

## Overall Project Overview

can be found at [CampusFind GitRepo](https://github.com/Santhosh-Paramasivam/CampusFind)

## 📖 Overview

Http requests are made to the backend from an **RFID system** with an esp8266 and RC522 (RFID reader module) which detects RFID cards and transmits their uid, its own mac address with other data

This is a backend rest api written in Python which then handles the **secure updation of the location** and entry time of the user in **Cloud Firestore Database**  

## API Documentation

| Method | Endpoint | Description |
|:-------|:---------|:------------|
|   GET  | `/update_user_location_secure` | Update the location and entry time of a particular user in CampusFind securely |
|   POST  | `/last_online` | Updates the last online time for an RFID station, to help indicate that its working as intented |

## Environment Variables

Create an `.env` file with :

`

`

## Contact

[LinkedIn](https://github.com/Santhosh-Paramasivam/CampusFind/blob/main/www.linkedin.com/in/santhosh-paramasivam-2a430a267)

Submit an issue here on Github

## Contributing

I would very much appreciate your help! Contribute by forking the repo and opening pull requests.

All pull requests should be submitted to the main branch.  
