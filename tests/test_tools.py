from tools.calculator import calculator
from tools.file_reader import read_study_file


def test_calculator():
    result = calculator.invoke({"expression": "25 * 17"})
    assert "425" in result


def test_file_reader():
    result = read_study_file.invoke({"filename": "notes.txt"})
    assert "Agentic AI Study Notes" in result
