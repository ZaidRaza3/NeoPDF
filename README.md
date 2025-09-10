# NeoPDF
A modern way of handling PDFs.

In an age where we rely on online tools for everything, a common concern is what happens to our data. When I needed to organize, merge, or convert my PDF files, I grew uneasy uploading personal and sensitive documents to anonymous third-party websites. Due to these concerns about data privacy and the security of my files, I decided to build my own secure and private PDF tool.

This tool is a simple yet powerful web application designed to handle common PDF operations without ever storing your files. All processing is done on your local server or on a temporary instance, and your files are immediately discarded after the task is completed. You get full control and peace of mind, knowing your documents are safe.

### Features
- Organize PDF: Rearrange, delete, or rotate pages in your PDF document with an intuitive drag-and-drop interface.
- Merge PDFs: Combine multiple PDF files into a single document.
- Split PDF: Extract specific pages or a custom range of pages to create new PDF files.
- Compress PDF: Reduce the file size of your PDF for faster sharing and storage. Note: I am continuously working to improve the compression algorithm, so results may vary.
- Protect PDF: Add a password to your PDF to secure it from unauthorized access.
- Unlock PDF: Remove the password from a locked PDF document.
- Convert Files: Transform your PDF to other formats like JPG or Word, and vice-versa.

### Technology Stack
* Frontend: HTML, CSS, JavaScript
* Backend: Python with the Flask framework

### 🚀 Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ZaidRaza3/NeoPDF.git
    cd NeoPDF
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Application:**
    ```bash
    gunicorn app:app
    ```

### Usage
- After starting the backend, open the index.html file in your preferred web browser (e.g., Chrome, Firefox, Edge).
- The web application will automatically connect to your running backend server.
- Use the different tabs to access the various PDF tools. Simply drag and drop your file into the designated area or click to browse.

### Privacy and Security
- The core purpose of this tool is to protect your privacy.
- No Cloud Storage: Your files are processed on a temporary server instance and are never stored long-term.
- Local Control: When self-hosting, all file operations occur on your own machine.
- Transparent Code: The entire codebase is open and transparent, so you can inspect exactly how your files are handled.

### Upcoming Features
I am actively developing NeoPDF and have plans to add more functionality soon, including:
  * Support for more file types in the conversion tool.
  * Advanced PDF editing features like adding text, images, and signatures.
