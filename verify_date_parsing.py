import datetime


def test_date_parsing():
    print("Testing date parsing...")
    input_date = "2023-10-27"
    try:
        parsed = datetime.datetime.strptime(input_date, "%Y-%m-%d").date()
        print(f"Parsed '{input_date}' to object: {parsed} (Type: {type(parsed)})")
        assert parsed.year == 2023
        assert parsed.month == 10
        assert parsed.day == 27
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")


if __name__ == "__main__":
    test_date_parsing()
