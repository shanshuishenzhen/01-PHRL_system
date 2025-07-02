import uuid

def parse_question_id(id_str):
    """
    Parses the composite question ID string into its components.
    Example ID: "A-B-C-KP001-001"
    Returns a dictionary with components or raises ValueError on invalid format.
    """
    parts = id_str.strip().split('-')
    # Expecting at least 3 parts for level codes, 1 for knowledge point, 1 for sequence
    if len(parts) < 5: 
        raise ValueError(f"Invalid ID format: '{id_str}'. Expected at least 5 parts separated by hyphens (e.g., L1-L2-L3-KP-SEQ).")
    
    sequence_number = parts[-1]
    knowledge_point_code = parts[-2]
    level_codes = parts[:-2]

    if not sequence_number.isdigit():
        raise ValueError(f"Invalid sequence number in ID '{id_str}': '{sequence_number}' is not a number.")

    return {
        "full_id": id_str,
        "level_codes": level_codes, # List of strings, e.g., ['A', 'B', 'C']
        "knowledge_point_code": knowledge_point_code, # String, e.g., 'KP001'
        "sequence_number": sequence_number # String, e.g., '001'
    }

def generate_question_id(level_codes, knowledge_point_code, sequence_number):
    """
    Generates a composite question ID.
    level_codes: A list or tuple of strings for the hierarchical codes (e.g., ['A', 'B', 'C'])
    knowledge_point_code: String for the knowledge point code (e.g., 'KP001')
    sequence_number: Integer or string for the sequence (e.g., 1 or '001'). Will be zero-padded to 3 digits.
    Returns the formatted ID string.
    """
    if not isinstance(level_codes, (list, tuple)) or not all(isinstance(lc, str) for lc in level_codes):
        raise ValueError("level_codes must be a list or tuple of strings.")
    if not isinstance(knowledge_point_code, str) or not knowledge_point_code.strip():
        raise ValueError("knowledge_point_code must be a non-empty string.")
    
    try:
        seq_int = int(sequence_number)
        if seq_int < 0:
            raise ValueError("Sequence number cannot be negative.")
        # Zero-pad the sequence number, e.g., to 3 digits
        formatted_sequence = f"{seq_int:03d}"
    except ValueError:
        raise ValueError(f"Invalid sequence_number: '{sequence_number}'. Must be convertible to an integer.")

    id_parts = list(level_codes) + [knowledge_point_code.strip(), formatted_sequence]
    return "-".join(id_parts)

# Example Usage:
if __name__ == '__main__':
    try:
        parsed = parse_question_id("SYS-DEV-PY-OOP-001")
        print(f"Parsed ID: {parsed}")
    except ValueError as e:
        print(f"Error parsing: {e}")

    try:
        parsed_invalid = parse_question_id("A-B-1") # Too short
        print(f"Parsed Invalid ID: {parsed_invalid}")
    except ValueError as e:
        print(f"Error parsing invalid ID: {e}")

    new_id = generate_question_id(['SYS', 'WEB', 'API'], 'AUTH', 5)
    print(f"Generated ID: {new_id}") # Expected: SYS-WEB-API-AUTH-005

    new_id_str_seq = generate_question_id(['DATA', 'SQL'], 'QUERY', '042')
    print(f"Generated ID with str sequence: {new_id_str_seq}") # Expected: DATA-SQL-QUERY-042

    try:
        generate_question_id(['MOD1'], 'KP1', 'abc') # Invalid sequence
    except ValueError as e:
        print(f"Error generating ID: {e}")