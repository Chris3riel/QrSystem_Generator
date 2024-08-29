# Cammer Corporativo Industrial QR Label Generation System

## Overview
This is a FastAPI-based application designed for Cammer Corporativo Industrial to generate QR labels for their products. The system allows users to create and manage product information, generate QR codes, and retrieve product data.

## Features
- **Product Information Management:** Create, update, and delete product information, including serial number, date, SAP code, and other relevant details.
- **QR Code Generation:** Generate QR codes for each product, which can be used to retrieve product information.
- **Product Data Retrieval:** Retrieve product information by scanning the QR code or entering the serial number.

## Technical Details
- **Backend:** Built using FastAPI, a modern, high-performance web framework for building APIs with Python 3.7+.
- **Database:** Utilizes PostgreSQL as the database management system.
- **QR Code Library:** Employs the `qrcode` library to generate QR codes.
- **Template Engine:** Uses `Jinja2Templates` for rendering HTML templates.
- **Image Processing:** Utilizes `opencv-python` for QR code detection and processing.
- **Asynchronous Operations:** Managed with `asyncpg` for asynchronous PostgreSQL database access and `anyio` for asynchronous I/O operations.
- **Web Development:** Integrates `flet` for UI components and `httpx` for making HTTP requests.

## Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/Chris3riel/QrSystem_Generator.git
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a PostgreSQL database and update the `DATABASE_URL` environment variable accordingly.
4. Run the application:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
5. Access the application through a web browser: [http://localhost:8000](http://localhost:8000)

## API Endpoints
- **GET /**: Returns the index page.
- **GET /data/{item_noSerie}**: Retrieves product information by serial number.
- **GET /qrcode/{item_noSerie}**: Generates a QR code for the product with the specified serial number.
- **POST /carga**: Creates a new product entry.

## License
This application is licensed under the MIT License. See LICENSE for details.

## Contributing
Contributions are welcome! If you'd like to contribute to this project, please fork the repository, make your changes, and submit a pull request.

## Acknowledgments
This application was developed for Cammer Corporativo Industrial.
