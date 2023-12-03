def get_values_by_key(json_obj, target_key):
    results = []

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if key == target_key:
                results.append(value)
            else:
                results.extend(get_values_by_key(value, target_key))
    elif isinstance(json_obj, list):
        for item in json_obj:
            results.extend(get_values_by_key(item, target_key))

    return results

# Example usage
json_data = {
    "name": "John",
    "age": 30,
    "address": {
        "city": "New York",
        "zipcode": "10001",
        "details": {
            "street": "123 Main St"
        }
    },
    "friends": [
        {"name": "Alice", "age": 28},
        {"name": "Bob", "age": 32}
    ]
}

target_key = "street"
result = get_values_by_key(json_data, target_key)
print(f"Values for key '{target_key}': {result}")

