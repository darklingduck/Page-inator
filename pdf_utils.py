import os
import shutil
from pypdf import PdfReader, PdfWriter, PdfMerger


# ============================================================
# ✅ PDF OPERATIONS (UNCHANGED — YOUR ORIGINAL CODE)
# ============================================================
class PDFHelper:

    # =========================
    # Split into individual pages
    # =========================
    @staticmethod
    def split_pdf_into_pages(file_path, output_dir):
        reader = PdfReader(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        os.makedirs(output_dir, exist_ok=True)

        output_files = []

        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)

            output_file = os.path.join(
                output_dir,
                f"{base_name}_page_{i + 1}.pdf"
            )

            with open(output_file, "wb") as f:
                writer.write(f)

            output_files.append(output_file)

        return output_files


    # =========================
    # Split at specific page
    # =========================
    @staticmethod
    def split_pdf_at_page(file_path, output_dir, split_page):
        reader = PdfReader(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        os.makedirs(output_dir, exist_ok=True)

        total_pages = len(reader.pages)

        if split_page < 1 or split_page >= total_pages:
            raise ValueError(
                f"Split page must be between 1 and {total_pages - 1}"
            )

        # First part
        writer1 = PdfWriter()
        for i in range(split_page):
            writer1.add_page(reader.pages[i])

        output_file1 = os.path.join(output_dir, f"{base_name}_part1.pdf")
        with open(output_file1, "wb") as f:
            writer1.write(f)

        # Second part
        writer2 = PdfWriter()
        for i in range(split_page, total_pages):
            writer2.add_page(reader.pages[i])

        output_file2 = os.path.join(output_dir, f"{base_name}_part2.pdf")
        with open(output_file2, "wb") as f:
            writer2.write(f)

        return [output_file1, output_file2]


    # =========================
    # Merge PDFs
    # =========================
    @staticmethod
    def merge_pdfs(file_list, output_file):
        merger = PdfMerger()

        for file in file_list:
            merger.append(file)

        with open(output_file, "wb") as f:
            merger.write(f)

        merger.close()


# ============================================================
# ✅ NEW: LOGGING + VALIDATION (FOR LAUNCHER / SYSTEM)
# ============================================================

def log(log_file, message):
    try:
        with open(log_file, "a") as f:
            f.write(message + "\n")
    except:
        pass


# ======================
# File validation
# ======================
def validate_file(path, description, log_file=None):
    if not os.path.exists(path):
        msg = (
            f"ERROR: {description} NOT FOUND\n"
            f"Expected at: {path}\n"
            f"Check:\n"
            f" - Network connection\n"
            f" - File exists on server\n"
            f" - File name matches exactly\n"
        )

        if log_file:
            log(log_file, msg)

        raise FileNotFoundError(msg)

    return True


# ======================
# Directory validation
# ======================
def validate_directory(path, description, log_file=None):
    if not os.path.exists(path):
        msg = (
            f"ERROR: {description} folder NOT FOUND\n"
            f"Expected at: {path}\n"
            f"Check:\n"
            f" - Network path exists\n"
            f" - Folder structure is correct\n"
        )

        if log_file:
            log(log_file, msg)

        raise FileNotFoundError(msg)

    return True


# ======================
# Safe file copy
# ======================
def safe_copy(src, dst, description, log_file=None):
    validate_file(src, description, log_file)

    try:
        shutil.copy2(src, dst)
    except Exception as e:
        msg = f"ERROR copying {description}: {e}"

        if log_file:
            log(log_file, msg)

        raise


# ======================
# Safe directory copy
# ======================
def safe_copytree(src, dst, description, log_file=None):
    validate_directory(src, description, log_file)

    try:
        shutil.copytree(src, dst)
    except Exception as e:
        msg = f"ERROR copying {description} folder: {e}"

        if log_file:
            log(log_file, msg)

        raise
