from abc import ABC, abstractmethod
from datetime import datetime


class Employee(ABC):

    _employee_count = 0
    _tax_rate = 0.1

    def __init__(self, emp_id: str, name: str, department: str, salary: float):
        self._emp_id = emp_id
        self._name = name
        self._department = department
        self._salary = salary
        self._hire_date = datetime.now()
        self._performance_rating = 0.0
        Employee._employee_count += 1

    # Properties
    @property
    def emp_id(self) -> str:
        return self._emp_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        self._name = value

    @property
    def department(self) -> str:
        return self._department

    @department.setter
    def department(self, value: str):
        if not value or not value.strip():
            raise ValueError("Department cannot be empty")
        self._department = value

    @property
    def salary(self) -> float:
        return self._salary

    @salary.setter
    def salary(self, value: float):
        if value < 0:
            raise ValueError("Salary must be positive")
        self._salary = value

    @property
    def performance_rating(self) -> float:
        return self._performance_rating

    @performance_rating.setter
    def performance_rating(self, value: float):
        if not 0 <= value <= 5:
            raise ValueError("Rating must be between 0 and 5")
        self._performance_rating = value

    # Abstract methods
    @abstractmethod
    def get_role(self) -> str:
        pass

    @abstractmethod
    def calculate_bonus(self) -> float:
        pass

    # Concrete methods
    def calculate_net_salary(self) -> float:
        return self._salary * (1 - Employee._tax_rate)

    def __str__(self) -> str:
        return (f"[{self._emp_id}] {self._name} - {self.get_role()} | "
                f"{self._department} | ${self._salary:,.2f}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self._emp_id}', name='{self._name}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Employee):
            return False
        return self._emp_id == other._emp_id

    def __hash__(self) -> int:
        return hash(self._emp_id)

    @classmethod
    def get_employee_count(cls) -> int:
        return cls._employee_count

    @classmethod
    def set_tax_rate(cls, rate: float):
        if 0 <= rate <= 1:
            cls._tax_rate = rate
        else:
            raise ValueError("Tax rate must be between 0 and 1")


class Manager(Employee):

    def __init__(self, emp_id: str, name: str, department: str, salary: float,
                 team_size: int = 0):
        super().__init__(emp_id, name, department, salary)
        self._team_size = team_size

    @property
    def team_size(self) -> int:
        return self._team_size

    @team_size.setter
    def team_size(self, value: int):
        if value < 0:
            raise ValueError("Team size cannot be negative")
        self._team_size = value

    def get_role(self) -> str:
        return "Manager"

    def calculate_bonus(self) -> float:
        base = self.salary * 0.2
        team_bonus = self._team_size * 500
        return (base + team_bonus) * (1 + self.performance_rating / 10)

    def __str__(self) -> str:
        return f"{super().__str__()} | Team: {self._team_size}"


class Developer(Employee):
    
    def __init__(self, emp_id: str, name: str, department: str, salary: float,
                 languages: list[str] | None = None, experience: int = 0):
        super().__init__(emp_id, name, department, salary)
        self._languages = languages or []
        self._experience = experience

    @property
    def languages(self) -> list:
        return self._languages

    @property
    def experience(self) -> int:
        return self._experience

    def add_language(self, language: str):
        if language not in self._languages:
            self._languages.append(language)

    def get_role(self) -> str:
        return "Developer"

    def calculate_bonus(self) -> float:
        base = self.salary * 0.15
        exp_bonus = self._experience * 200
        lang_bonus = len(self._languages) * 300
        return base + exp_bonus + lang_bonus

    def __str__(self) -> str:
        langs = ", ".join(self._languages) or "None"
        return f"{super().__str__()} | {langs} | {self._experience}y exp"


class Designer(Employee):

    def __init__(self, emp_id: str, name: str, department: str, salary: float,
                 tools: list[str] | None = None, portfolio_size: int = 0):
        super().__init__(emp_id, name, department, salary)
        self._tools = tools or []
        self._portfolio_size = portfolio_size

    @property
    def tools(self) -> list:
        return self._tools

    @property
    def portfolio_size(self) -> int:
        return self._portfolio_size

    def get_role(self) -> str:
        return "Designer"

    def calculate_bonus(self) -> float:
        base = self.salary * 0.12
        tool_bonus = len(self._tools) * 250
        portfolio_bonus = self._portfolio_size * 100
        return base + tool_bonus + portfolio_bonus

    def __str__(self) -> str:
        tools = ", ".join(self._tools) or "None"
        return f"{super().__str__()} | {tools} | Portfolio: {self._portfolio_size}"


class Intern(Employee):

    def __init__(self, emp_id: str, name: str, department: str, salary: float,
                 university: str = "", mentor_id: str | None = None):
        super().__init__(emp_id, name, department, salary)
        self._university = university
        self._mentor_id = mentor_id

    @property
    def university(self) -> str:
        return self._university

    @property
    def mentor_id(self) -> str | None:
        return self._mentor_id

    def get_role(self) -> str:
        return "Intern"

    def calculate_bonus(self) -> float:
        return self.salary * 0.05

    def __str__(self) -> str:
        mentor = self._mentor_id or "None"
        return f"{super().__str__()} | {self._university} | Mentor: {mentor}"
