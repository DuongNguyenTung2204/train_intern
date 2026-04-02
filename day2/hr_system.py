import json
import os
from typing import Optional

from models import Employee, Manager, Developer, Designer, Intern


DATA_FILE = "employees_data.json"


class HRSystem:

    def __init__(self):
        self._employees: dict[str, Employee] = {}

    def add_employee(self, employee: Employee) -> bool:
        if employee.emp_id in self._employees:
            print(f"[X] Employee {employee.emp_id} already exists")
            return False
        self._employees[employee.emp_id] = employee
        print(f"[+] Added: {employee}")
        return True

    def remove_employee(self, emp_id: str) -> bool:
        if emp_id in self._employees:
            removed = self._employees.pop(emp_id)
            print(f"[-] Removed: {removed.name}")
            return True
        print(f"[X] Employee {emp_id} not found")
        return False

    def get_employee(self, emp_id: str) -> Optional[Employee]:
        return self._employees.get(emp_id)

    def get_all_employees(self) -> list[Employee]:
        return list(self._employees.values())


    def display_all(self):
        if not self._employees:
            print("[ ] No employees in system")
            return

        print("\n" + "=" * 75)
        print(f"{'ID':<8} {'Name':<18} {'Role':<10} {'Department':<12} {'Salary':>12} {'Net':>12}")
        print("=" * 75)

        for emp in self._employees.values():
            print(f"{emp.emp_id:<8} {emp.name:<18} {emp.get_role():<10} "
                  f"{emp.department:<12} ${emp.salary:>10,.2f} ${emp.calculate_net_salary():>10,.2f}")

        print("=" * 75)
        total = sum(e.calculate_net_salary() for e in self._employees.values())
        print(f"Total: {len(self._employees)} employees | Payroll: ${total:,.2f}")


    def search(self, query: str) -> list[Employee]:
        query_lower = query.lower()
        return [
            emp for emp in self._employees.values()
            if query_lower in emp.name.lower()
            or query_lower in emp.department.lower()
            or query_lower in emp.get_role().lower()
        ]

    def save_to_file(self, filepath: str = DATA_FILE):
        data = []
        for emp in self._employees.values():
            emp_data = {
                'type': type(emp).__name__,
                'emp_id': emp.emp_id,
                'name': emp.name,
                'department': emp.department,
                'salary': emp.salary,
                'performance_rating': emp.performance_rating,
            }

            if isinstance(emp, Manager):
                emp_data['team_size'] = emp.team_size
            elif isinstance(emp, Developer):
                emp_data['languages'] = emp.languages
                emp_data['experience'] = emp.experience
            elif isinstance(emp, Designer):
                emp_data['tools'] = emp.tools
                emp_data['portfolio_size'] = emp.portfolio_size
            elif isinstance(emp, Intern):
                emp_data['university'] = emp.university
                emp_data['mentor_id'] = emp.mentor_id

            data.append(emp_data)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[*] Saved {len(data)} employees to {filepath}")

    def load_from_file(self, filepath: str = DATA_FILE) -> bool:
        if not os.path.exists(filepath):
            print(f"[ ] File {filepath} not found")
            return False

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            type_map = {
                'Manager': Manager,
                'Developer': Developer,
                'Designer': Designer,
                'Intern': Intern,
            }

            for item in data:
                emp_type = item.pop('type')
                item.pop('performance_rating', None)

                cls = type_map.get(emp_type)
                if cls:
                    emp = cls(**item)
                    self._employees[emp.emp_id] = emp

            print(f"[*] Loaded {len(self._employees)} employees from {filepath}")
            return True
        except Exception as e:
            print(f"[X] Error loading: {e}")
            return False

    def generate_report(self):
        print("\n" + "=" * 50)
        print("HR REPORT")
        print("=" * 50)
        print(f"Total Employees: {len(self._employees)}")
        print(f"Total Payroll: ${sum(e.calculate_net_salary() for e in self._employees.values()):,.2f}")

        # By role
        roles = {}
        for emp in self._employees.values():
            roles[emp.get_role()] = roles.get(emp.get_role(), 0) + 1

        print("\nBy Role:")
        for role, count in sorted(roles.items()):
            print(f"  {role}: {count}")

        # By department
        departments = {}
        for emp in self._employees.values():
            if emp.department not in departments:
                departments[emp.department] = []
            departments[emp.department].append(emp)

        print("\nBy Department:")
        for dept, emps in sorted(departments.items()):
            avg_salary = sum(e.salary for e in emps) / len(emps)
            print(f"  {dept}: {len(emps)} employees, avg ${avg_salary:,.2f}")

        # Top performers
        top = [e for e in self._employees.values() if e.performance_rating >= 4.0]
        if top:
            print("\nTop Performers:")
            for emp in sorted(top, key=lambda x: x.performance_rating, reverse=True)[:5]:
                print(f"  {emp.name}: {emp.performance_rating}/5.0")

        print("=" * 50)
