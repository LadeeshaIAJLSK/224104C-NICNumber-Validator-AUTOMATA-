"""
Sri Lankan National Identity Card (NIC) Validator
Using Deterministic Finite Automaton (DFA)

Author: 224104C
Date: December 2025
"""

class NICValidator:
    """
    DFA-based validator for Sri Lankan NIC numbers
    Accepts:
    - Old Format: 9 digits + 'V' or 'X' (e.g., 952861907V)
    - New Format: 12 digits (e.g., 199528619078)
    """
    
    def __init__(self):
        # Define the alphabet
        self.digits = set('0123456789')
        self.old_format_endings = set('VX')
        
        # Define states
        self.states = [f'q{i}' for i in range(14)] + ['qErr']
        self.start_state = 'q0'
        self.accept_states = {'q10', 'q13'}  # q10 for old, q13 for new
        
        # Current state during validation
        self.current_state = self.start_state
        self.input_string = ""
    
    def transition(self, state, char):
        """
        Transition function δ(state, character) → next_state
        
        Logic:
        - q0 to q9: Read 9 digits
        - q9 → q10: Read V or X (old format complete)
        - q9 → q11: Read 10th digit (continue to new format)
        - q11 → q12 → q13: Read remaining digits for new format
        """
        
        # States q0 to q8: Must read digits
        if state in ['q0', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8']:
            if char in self.digits:
                state_num = int(state[1:])  # Extract number from 'q0' → 0
                return f'q{state_num + 1}'
            else:
                return 'qErr'
        
        # State q9: Branch point (9 digits read)
        elif state == 'q9':
            if char in self.old_format_endings:  # V or X
                return 'q10'  # Old format path
            elif char in self.digits:
                return 'q11'  # New format path (10th digit)
            else:
                return 'qErr'
        
        # State q10: Old format complete (should not accept more input)
        elif state == 'q10':
            return 'qErr'  # Any additional character is invalid
        
        # States q11 and q12: Continue new format
        elif state == 'q11':
            if char in self.digits:
                return 'q12'
            else:
                return 'qErr'
        
        elif state == 'q12':
            if char in self.digits:
                return 'q13'
            else:
                return 'qErr'
        
        # State q13: New format complete (should not accept more input)
        elif state == 'q13':
            return 'qErr'
        
        # Error state: Stay in error
        else:
            return 'qErr'
    
    def validate(self, nic_number):
        """
        Main validation function
        Returns: (is_valid, format_type, message)
        """
        self.input_string = nic_number.strip().upper()  # Normalize input
        self.current_state = self.start_state
        
        # Empty input check
        if not self.input_string:
            return False, None, "ERROR: Empty input"
        
        # Process each character through DFA
        for i, char in enumerate(self.input_string):
            next_state = self.transition(self.current_state, char)
            
            # Debug: Print state transitions (useful for learning)
            # print(f"Step {i+1}: '{char}' | {self.current_state} → {next_state}")
            
            self.current_state = next_state
            
            # Early termination if error state reached
            if self.current_state == 'qErr':
                return False, None, f"REJECTED: Invalid character '{char}' at position {i+1}"
        
        # Check if final state is accepting
        if self.current_state in self.accept_states:
            if self.current_state == 'q10':
                format_type = "Old Format (9 digits + V/X)"
            else:  # q13
                format_type = "New Format (12 digits)"
            
            return True, format_type, f"ACCEPTED: Valid {format_type}"
        else:
            return False, None, f"REJECTED: Incomplete NIC (ended in state {self.current_state})"
    
    def get_state_info(self):
        """Returns current state information"""
        return {
            'current_state': self.current_state,
            'is_accepting': self.current_state in self.accept_states,
            'input': self.input_string
        }


def extract_info_from_nic(nic_number):
    """
    Extract birth year and days from old format NIC
    (Educational purpose - showing practical application)
    """
    nic = nic_number.strip().upper()
    
    # Old format extraction
    if len(nic) == 10 and nic[-1] in 'VX':
        year_part = nic[:2]
        days = int(nic[2:5])
        
        # Determine century
        year = int(year_part)
        if year >= 0 and year <= 25:  # Assuming 2000-2025
            full_year = 1900 + year
        else:
            full_year = 1900 + year
        
        # Gender determination (500+ days = female)
        if days > 500:
            gender = "Female"
            days -= 500
        else:
            gender = "Male"
        
        return {
            'birth_year': full_year,
            'day_of_year': days,
            'gender': gender,
            'serial': nic[5:9]
        }
    
    # New format extraction
    elif len(nic) == 12 and nic.isdigit():
        year = int(nic[:4])
        days = int(nic[4:7])
        
        if days > 500:
            gender = "Female"
            days -= 500
        else:
            gender = "Male"
        
        return {
            'birth_year': year,
            'day_of_year': days,
            'gender': gender,
            'serial': nic[7:11]
        }
    
    return None


def run_test_cases():
    """Test the validator with various inputs"""
    validator = NICValidator()
    
    test_cases = [
        # Valid old format
        ("952861907V", True, "Valid old format NIC"),
        ("751234567X", True, "Valid old format with X"),
        ("200012345V", True, "Valid year 2000 NIC"),
        
        # Valid new format
        ("199528619078", True, "Valid new format NIC"),
        ("200501012345", True, "Valid 2005 new format"),
        
        # Invalid: Too short/long
        ("12345", False, "Too short"),
        ("952861907VX", False, "Too long (11 chars)"),
        ("95286190", False, "Only 8 digits"),
        ("1995286190789", False, "13 digits - too long"),
        
        # Invalid: Wrong letters
        ("952861907A", False, "Wrong ending letter (A instead of V/X)"),
        ("95286190A7", False, "Letter in middle"),
        ("19952861907A", False, "Letter in 12-digit format"),
        ("ABCDEFGHIJ", False, "All letters"),
        
        # Invalid: Special characters
        ("952-861-907V", False, "Contains hyphen"),
        ("952 861 907V", False, "Contains spaces"),
        ("952@861907V", False, "Contains @ symbol"),
        ("952#861907V", False, "Contains # symbol"),
        ("952$861907V", False, "Contains $ symbol"),
        ("952%861907V", False, "Contains % symbol"),
        ("952&861907V", False, "Contains & symbol"),
        ("952*861907V", False, "Contains * symbol"),
        ("952+861907V", False, "Contains + symbol"),
        ("952=861907V", False, "Contains = symbol"),
        ("952/861907V", False, "Contains / symbol"),
        ("952\\861907V", False, "Contains backslash"),
        ("952.861.907V", False, "Contains periods"),
        ("952,861,907V", False, "Contains commas"),
        ("952;861907V", False, "Contains semicolon"),
        ("952:861907V", False, "Contains colon"),
        ("952!861907V", False, "Contains exclamation"),
        ("952?861907V", False, "Contains question mark"),
        ("(952861907V)", False, "Contains parentheses"),
        ("[952861907V]", False, "Contains brackets"),
        ("{952861907V}", False, "Contains braces"),
        ("952_861_907V", False, "Contains underscores"),
        ("952|861907V", False, "Contains pipe"),
        ("952~861907V", False, "Contains tilde"),
        ("952`861907V", False, "Contains backtick"),
        ("952'861907V", False, "Contains single quote"),
        ('952"861907V', False, "Contains double quote"),
        
        # Invalid: Special cases
        ("", False, "Empty string"),
        ("          ", False, "Only spaces"),
        ("\t952861907V", False, "Starts with tab"),
        ("952861907V\n", False, "Ends with newline"),
        
        # Edge cases with new format
        ("199528619078@", False, "New format with special char at end"),
        ("1995-28619078", False, "New format with hyphen in middle"),
    ]
    
    print("=" * 80)
    print("SRI LANKAN NIC VALIDATOR - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for nic, expected_valid, description in test_cases:
        is_valid, format_type, message = validator.validate(nic)
        
        # Check if result matches expectation
        test_passed = (is_valid == expected_valid)
        
        if test_passed:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1
        
        print(f"{status} | Input: {nic:20s} | {message}")
        print(f"     | Description: {description}")
        
        # Show extracted info for valid NICs
        if is_valid:
            info = extract_info_from_nic(nic)
            if info:
                print(f"     | Extracted: Year={info['birth_year']}, Day={info['day_of_year']}, Gender={info['gender']}")
        
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)


def interactive_mode():
    """Interactive testing mode"""
    validator = NICValidator()
    
    print("\n" + "=" * 80)
    print("SRI LANKAN NIC VALIDATOR - INTERACTIVE MODE")
    print("=" * 80)
    print("\nEnter NIC numbers to validate (type 'exit' to quit)")
    print("Examples: 952861907V (old) or 199528619078 (new)")
    print()
    
    while True:
        try:
            nic_input = input("Enter NIC: ").strip()
            
            if nic_input.lower() in ['exit', 'quit', 'q']:
                print("\nThank you for using NIC Validator!")
                break
            
            if not nic_input:
                print("⚠ Please enter a NIC number\n")
                continue
            
            # Validate
            is_valid, format_type, message = validator.validate(nic_input)
            
            print(f"\n{'='*60}")
            if is_valid:
                print(f"✓ {message}")
                print(f"  Format: {format_type}")
                
                # Extract and show info
                info = extract_info_from_nic(nic_input)
                if info:
                    print(f"\n  Extracted Information:")
                    print(f"  • Birth Year: {info['birth_year']}")
                    print(f"  • Day of Year: {info['day_of_year']}")
                    print(f"  • Gender: {info['gender']}")
                    print(f"  • Serial Number: {info['serial']}")
            else:
                print(f"✗ {message}")
            
            print(f"{'='*60}\n")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    # Run automated tests first
    run_test_cases()
    
    # Ask user if they want interactive mode
    print("\nWould you like to try interactive mode? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice in ['y', 'yes']:
        interactive_mode()