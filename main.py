import csv
import os

# Student Registration & Contact Intelligence System
# Developed by Ashwin

INPUT_FILE = "contacts.csv"
OUTPUT_FILE = "students_clean.csv"


def validate_contact(name, phone, email):
    name = name.strip()
    phone = phone.strip()
    email = email.strip()

    if len(name) == 0:
        return False, "Name is blank"

    if not (
        len(phone) == 10
        and phone.isdigit()
        and phone[0] in ("6", "7", "8", "9")
    ):
        return False, "Phone must be 10 digits starting with 6, 7, 8, or 9."

    if " " in email or email.count("@") != 1:
        return False, "Invalid email format"

    local_part, domain_part = email.split("@")
    if len(local_part) == 0 or "." not in domain_part:
        return False, "Invalid email format"

    if domain_part.startswith(".") or domain_part.endswith("."):
        return False, "Invalid email format"

    return True, "Valid"


def save_clean_students(students, output_file=OUTPUT_FILE):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "phone", "email"])
        writer.writeheader()
        writer.writerows(students)


def load_and_clean_contacts(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    valid_students = []
    seen_phones = {}
    seen_emails = set()

    stats = {
        "total": 0,
        "valid": 0,
        "rejected": 0,
        "reasons": {"phone": 0, "email": 0, "name": 0, "duplicate": 0},
        "duplicate_details": [],
    }

    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' not found in the current folder.")
        return valid_students, stats

    with open(input_file, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats["total"] += 1
            name = (row.get("name") or "").strip()
            phone = (row.get("phone") or "").strip()
            email = (row.get("email") or "").strip().lower()

            is_valid, reason = validate_contact(name, phone, email)
            if not is_valid:
                stats["rejected"] += 1
                if "Name" in reason:
                    stats["reasons"]["name"] += 1
                elif "Phone" in reason:
                    stats["reasons"]["phone"] += 1
                else:
                    stats["reasons"]["email"] += 1
                print(
                    f"[REJECTED] {name or '<Blank>'} | {phone or '<Blank>'} |"
                    f" {email} -> {reason}"
                )
                continue

            if phone in seen_phones:
                stats["rejected"] += 1
                stats["reasons"]["duplicate"] += 1
                msg = (
                    f"{name} ({phone}, {email}) - Phone {phone} already"
                    f" registered to {seen_phones[phone]}"
                )
                stats["duplicate_details"].append(msg)
                print(f"[DUPLICATE] {msg}")
                continue

            if email in seen_emails:
                stats["rejected"] += 1
                stats["reasons"]["duplicate"] += 1
                msg = (
                    f"{name} ({phone}, {email}) - Email {email} already"
                    " registered"
                )
                stats["duplicate_details"].append(msg)
                print(f"[DUPLICATE] {msg}")
                continue

            seen_phones[phone] = name
            seen_emails.add(email)
            stats["valid"] += 1
            valid_students.append({
                "id": f"STU{stats['valid']:03d}",
                "name": name,
                "phone": phone,
                "email": email,
            })

    save_clean_students(valid_students, output_file)
    return valid_students, stats


def generate_report(students, stats):
    total = stats["total"]
    valid = stats["valid"]
    rejected = stats["rejected"]
    accuracy = (valid / total * 100) if total > 0 else 0.0

    series_counts = {"9": 0, "8": 0, "7": 0, "6": 0}
    domain_counts = {}

    for s in students:
        first_digit = s["phone"][0]
        if first_digit in series_counts:
            series_counts[first_digit] += 1

        domain = "@" + s["email"].split("@")[1]
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    sorted_domains = sorted(
        domain_counts.items(), key=lambda x: x[1], reverse=True
    )

    print("\n" + "=" * 54)
    print("  STUDENT REGISTRATION — BUSINESS INTELLIGENCE REPORT")
    print("                  Developed by Ashwin")
    print("=" * 54)
    print(f"Total Contacts Processed : {total}")
    print(f"Valid Registrations      : {valid}")
    print(f"Rejected Records         : {rejected}")
    print(f"Data Quality Accuracy    : {accuracy:.1f}%")
    print(
        f"Rejections Breakdown     : Phone={stats['reasons']['phone']}, "
        f"Email={stats['reasons']['email']}, Name={stats['reasons']['name']}, "
        f"Duplicate={stats['reasons']['duplicate']}"
    )

    print("\nTelecom Network Breakdown:")
    print(f"  9-Series (Jio/Airtel)  : {series_counts['9']} students")
    print(f"  8-Series (Vi/Airtel)   : {series_counts['8']} students")
    print(f"  7-Series (BSNL/Vi)     : {series_counts['7']} students")
    print(f"  6-Series               : {series_counts['6']} students")

    print("\nTop Email Domains:")
    for domain, count in sorted_domains:
        print(f"  {domain:<22} : {count} students")

    if stats["duplicate_details"]:
        print("\nDuplicate Record(s) Caught:")
        for dup in stats["duplicate_details"]:
            print(f"  - {dup}")
    print("=" * 54)


def view_students(students):
    print("\n" + "-" * 68)
    print(f"{'ID':<8} {'Name':<20} {'Phone':<14} {'Email'}")
    print("-" * 68)
    if not students:
        print("No student records found.")
    for s in students:
        print(f"{s['id']:<8} {s['name']:<20} {s['phone']:<14} {s['email']}")
    print("-" * 68)


def search_student(students):
    query = input("Enter Phone, Email, or Name to search: ").strip().lower()
    matches = [
        s
        for s in students
        if query in s["name"].lower()
        or query == s["phone"]
        or query == s["email"].lower()
    ]
    if not matches:
        print("No matching student found.")
    else:
        view_students(matches)


def register_student(students):
    name = input("Enter student name: ").strip()
    phone = input("Enter 10-digit phone number: ").strip()
    email = input("Enter email address: ").strip().lower()

    is_valid, reason = validate_contact(name, phone, email)
    if not is_valid:
        print(f"Error: {reason}")
        return

    if any(s["phone"] == phone for s in students):
        print("Error: Duplicate phone number already registered.")
        return

    if any(s["email"] == email for s in students):
        print("Error: Duplicate email address already registered.")
        return

    next_num = len(students) + 1
    new_student = {
        "id": f"STU{next_num:03d}",
        "name": name,
        "phone": phone,
        "email": email,
    }
    students.append(new_student)
    print(f"Success: Registered {name} with ID {new_student['id']}.")


def update_student(students):
    target = input("Enter Student ID or Phone to update: ").strip()
    for s in students:
        if s["id"].lower() == target.lower() or s["phone"] == target:
            new_name = input(f"New name [{s['name']}]: ").strip() or s["name"]
            new_phone = (
                input(f"New phone [{s['phone']}]: ").strip() or s["phone"]
            )
            new_email = (
                input(f"New email [{s['email']}]: ").strip() or s["email"]
            ).lower()

            is_valid, reason = validate_contact(new_name, new_phone, new_email)
            if not is_valid:
                print(f"Error: {reason}")
                return

            if any(
                other is not s and other["phone"] == new_phone
                for other in students
            ):
                print("Error: Another student already uses this phone number.")
                return

            if any(
                other is not s and other["email"] == new_email
                for other in students
            ):
                print("Error: Another student already uses this email.")
                return

            s["name"], s["phone"], s["email"] = new_name, new_phone, new_email
            print("Student record updated successfully.")
            return
    print("Student not found.")


def delete_student(students):
    target = input("Enter Student ID or Phone to delete: ").strip()
    for i, s in enumerate(students):
        if s["id"].lower() == target.lower() or s["phone"] == target:
            removed = students.pop(i)
            print(f"Deleted record for {removed['name']} ({removed['id']}).")
            return
    print("Student not found.")


def main():
    print("Loading and validating contacts.csv...\n")
    students, stats = load_and_clean_contacts()

    while True:
        print("\n" + "=" * 50)
        print("   STUDENT REGISTRATION & INTELLIGENCE SYSTEM")
        print("                 Made by Ashwin")
        print("=" * 50)
        print("1. View All Students")
        print("2. Search Record")
        print("3. Register Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Analytics Report")
        print("7. Exit")

        choice = input("\nEnter your choice (1-7): ").strip()

        if choice == "1":
            view_students(students)
        elif choice == "2":
            search_student(students)
        elif choice == "3":
            register_student(students)
        elif choice == "4":
            update_student(students)
        elif choice == "5":
            delete_student(students)
        elif choice == "6":
            generate_report(students, stats)
        elif choice == "7":
            save_clean_students(students)
            print("Saved clean records to students_clean.csv. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-7.")


if __name__ == "__main__":
    main()
