from models import Employee, Manager, Developer, Designer, Intern
from hr_system import HRSystem


def menu():
    print("\n" + "=" * 50)
    print("HR MANAGEMENT SYSTEM")
    print("=" * 50)
    print("1. Add Employee")
    print("2. Remove Employee")
    print("3. View All")
    print("4. Search")
    print("5. Update")
    print("6. Report")
    print("7. Save to JSON")
    print("8. Load from JSON")
    print("0. Exit")
    print("=" * 50)


def choose_type() -> str:
    print("\n1. Manager 2. Developer 3. Designer 4. Intern")
    m = {'1': 'Manager', '2': 'Developer', '3': 'Designer', '4': 'Intern'}
    return m.get(input("Type (1-4): ").strip(), 'Developer')


def add_interactive(hr: HRSystem):
    emp_type = choose_type()
    emp_id = input("ID: ").strip()
    name = input("Name: ").strip()
    dept = input("Department: ").strip()

    try:
        salary = float(input("Salary: $"))
    except ValueError:
        salary = 50000.0

    try:
        rating = float(input("Rating (0-5): "))
    except ValueError:
        rating = 3.0

    if emp_type == 'Manager':
        try:
            team = int(input("Team size: "))
        except ValueError:
            team = 0
        emp = Manager(emp_id, name, dept, salary, team)
    elif emp_type == 'Developer':
        langs = [l.strip() for l in input("Languages (comma-sep): ").split(',') if l.strip()]
        try:
            exp = int(input("Experience (years): "))
        except ValueError:
            exp = 0
        emp = Developer(emp_id, name, dept, salary, langs, exp)
    elif emp_type == 'Designer':
        tools = [t.strip() for t in input("Tools (comma-sep): ").split(',') if t.strip()]
        try:
            portfolio = int(input("Portfolio size: "))
        except ValueError:
            portfolio = 0
        emp = Designer(emp_id, name, dept, salary, tools, portfolio)
    else:
        uni = input("University: ").strip()
        mentor = input("Mentor ID: ").strip() or None
        emp = Intern(emp_id, name, dept, salary, uni, mentor)

    emp.performance_rating = rating
    hr.add_employee(emp)


def update_interactive(hr: HRSystem):
    emp_id = input("Employee ID to update: ").strip()
    emp = hr.get_employee(emp_id)
    if not emp:
        print(f"[X] Not found: {emp_id}")
        return

    print(f"Updating: {emp}")

    name = input(f"Name [{emp.name}]: ").strip()
    if name:
        emp.name = name

    dept = input(f"Department [{emp.department}]: ").strip()
    if dept:
        emp.department = dept

    salary = input(f"Salary [${emp.salary:,.2f}]: ").strip()
    if salary:
        try:
            emp.salary = float(salary)
        except ValueError:
            pass

    rating = input(f"Rating [{emp.performance_rating}]: ").strip()
    if rating:
        try:
            emp.performance_rating = float(rating)
        except ValueError:
            pass

    print("[+] Updated!")


def main():
    hr = HRSystem()
    
    print("\nHR Management System")
    print("OOP Concepts: Inheritance, Encapsulation, Polymorphism, Abstraction")
    
    hr.load_from_file()
    print(f"[*] Loaded {len(hr.get_all_employees())} employees from JSON\n")

    while True:
        menu()
        choice = input("Choice (0-8): ").strip()

        if choice == '1':
            add_interactive(hr)
        elif choice == '2':
            emp_id = input("Employee ID: ").strip()
            hr.remove_employee(emp_id)
        elif choice == '3':
            hr.display_all()
        elif choice == '4':
            query = input("Search: ").strip()
            results = hr.search(query)
            if results:
                for emp in results:
                    print(f" {emp}")
            else:
                print("No results")
        elif choice == '5':
            update_interactive(hr)
        elif choice == '6':
            hr.generate_report()
        elif choice == '7':
            hr.save_to_file()
        elif choice == '8':
            hr.load_from_file()
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("[X] Invalid choice")

        input("\nPress Enter...")


if __name__ == "__main__":
    main()