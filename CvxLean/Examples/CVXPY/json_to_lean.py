#!/usr/bin/env python3
"""
JSON S-expression to Lean Syntax Translator

Converts JSON output from cvxpy_to_lean_json to valid CVXLean Lean code.
Bridges the gap between CVXPY problems and CVXLean optimization syntax.

Usage:
    from json_to_lean import json_to_lean_code
    
    # Convert JSON to Lean code
    lean_code = json_to_lean_code(json_string)
    print(lean_code)
"""

import json
import re
from typing import Dict, Any, List, Set, Tuple, Optional


class SExprToLeanTranslator:
    """Translates S-expressions to Lean optimization syntax."""
    
    def __init__(self):
        self.variable_names = set()
        self.parameter_names = set()
        
        # Mapping from CVXLean S-expr operators to Lean syntax
        self.operator_map = {
            'add': '+',
            'sub': '-', 
            'mul': '*',
            'div': '/',
            'pow': '^',
            'neg': '-',
            'abs': 'abs',
            'sqrt': 'sqrt',
            'log': 'log',
            'exp': 'exp',
            'sq': '· ^ 2',  # Square in Lean
            'ssq': 'sum_squares',  # Will need special handling
            'norm2': '‖ · ‖',  # Norm in Lean
            'max': 'max',
            'min': 'min',
            'sum': 'sum',
            'tr': 'trace',
            
            # Constraint operators
            'eq': '=',
            'le': '≤',
            'ge': '≥',
            'lt': '<',
            'gt': '>'
        }
    
    def parse_sexpr(self, sexpr: str) -> Any:
        """Parse S-expression string into a nested structure."""
        sexpr = sexpr.strip()
        
        if not sexpr:
            return ""
            
        if not sexpr.startswith('('):
            # Atomic expression (number, variable name, etc.)
            try:
                # Try to parse as number
                if '.' in sexpr:
                    return float(sexpr)
                else:
                    return int(sexpr)
            except ValueError:
                return sexpr
        
        # Parse nested S-expression
        tokens = self._tokenize_sexpr(sexpr)
        return self._parse_tokens(tokens)
    
    def _tokenize_sexpr(self, sexpr: str) -> List[str]:
        """Tokenize S-expression into list of tokens."""
        tokens = []
        i = 0
        while i < len(sexpr):
            char = sexpr[i]
            if char in '()':
                tokens.append(char)
                i += 1
            elif char.isspace():
                i += 1
            else:
                # Read token until space or parenthesis
                token = ""
                while i < len(sexpr) and sexpr[i] not in '() \t\n':
                    token += sexpr[i]
                    i += 1
                if token:
                    tokens.append(token)
        return tokens
    
    def _parse_tokens(self, tokens: List[str]) -> Any:
        """Parse tokenized S-expression."""
        if not tokens:
            return []
            
        if tokens[0] != '(':
            # Single token
            token = tokens[0]
            try:
                if '.' in token:
                    return float(token)
                else:
                    return int(token)
            except ValueError:
                return token
        
        # Parse list starting with '('
        result = []
        i = 1  # Skip opening paren
        while i < len(tokens) and tokens[i] != ')':
            if tokens[i] == '(':
                # Find matching closing paren
                paren_count = 1
                j = i + 1
                while j < len(tokens) and paren_count > 0:
                    if tokens[j] == '(':
                        paren_count += 1
                    elif tokens[j] == ')':
                        paren_count -= 1
                    j += 1
                # Recursively parse sub-expression
                sub_expr = self._parse_tokens(tokens[i:j])
                result.append(sub_expr)
                i = j
            else:
                # Single token
                token = tokens[i]
                try:
                    if '.' in token:
                        result.append(float(token))
                    else:
                        result.append(int(token))
                except ValueError:
                    result.append(token)
                i += 1
        
        return result
    
    def sexpr_to_lean(self, sexpr: str) -> str:
        """Convert S-expression to Lean syntax."""
        parsed = self.parse_sexpr(sexpr)
        return self._translate_parsed(parsed)
    
    def _translate_parsed(self, parsed: Any) -> str:
        """Translate parsed S-expression to Lean syntax."""
        if isinstance(parsed, (int, float)):
            if isinstance(parsed, float) and parsed.is_integer():
                return str(int(parsed))
            return str(parsed)
        
        if isinstance(parsed, str):
            return parsed
        
        if not isinstance(parsed, list) or len(parsed) == 0:
            return "0"
        
        op = parsed[0]
        args = parsed[1:] if len(parsed) > 1 else []
        
        # Handle special cases
        if op == 'var':
            if len(args) >= 1:
                var_name = str(args[0])
                self.variable_names.add(var_name)
                return var_name
            return "x"
        
        elif op == 'param':
            if len(args) >= 1:
                param_name = str(args[0])
                self.parameter_names.add(param_name)
                return param_name
            return "p"
        
        elif op == 'objFun':
            if len(args) >= 1:
                return self._translate_parsed(args[0])
            return "0"
        
        # Binary operators
        elif op in ['add', 'sub', 'mul', 'div']:
            if len(args) == 2:
                left = self._translate_parsed(args[0])
                right = self._translate_parsed(args[1])
                lean_op = self.operator_map[op]
                return f"({left} {lean_op} {right})"
            elif len(args) > 2:
                # Chain operations (left-associative)
                result = self._translate_parsed(args[0])
                lean_op = self.operator_map[op]
                for arg in args[1:]:
                    arg_str = self._translate_parsed(arg)
                    result = f"({result} {lean_op} {arg_str})"
                return result
            elif len(args) == 1:
                return self._translate_parsed(args[0])
            return "0"
        
        # Unary operators
        elif op == 'neg':
            if len(args) >= 1:
                arg_str = self._translate_parsed(args[0])
                return f"(-{arg_str})"
            return "0"
        
        elif op == 'sq':
            if len(args) >= 1:
                arg_str = self._translate_parsed(args[0])
                return f"{arg_str} ^ 2"
            return "0"
        
        elif op == 'pow':
            if len(args) >= 2:
                base = self._translate_parsed(args[0])
                exp = self._translate_parsed(args[1])
                return f"{base} ^ {exp}"
            return "0"
        
        elif op in ['abs', 'sqrt', 'log', 'exp']:
            if len(args) >= 1:
                arg_str = self._translate_parsed(args[0])
                func_name = self.operator_map[op]
                return f"{func_name} {arg_str}"
            return "0"
        
        # Special functions
        elif op == 'ssq':
            if len(args) >= 1:
                arg_str = self._translate_parsed(args[0])
                return f"sum_squares {arg_str}"
            return "0"
        
        elif op == 'norm2':
            if len(args) >= 1:
                arg_str = self._translate_parsed(args[0])
                return f"‖{arg_str}‖"
            return "0"
        
        elif op == 'sum':
            if len(args) >= 1:
                arg_str = self._translate_parsed(args[0])
                return f"sum {arg_str}"
            return "0"
        
        # Constraint operators
        elif op in ['eq', 'le', 'ge', 'lt', 'gt']:
            if len(args) >= 2:
                left = self._translate_parsed(args[0])
                right = self._translate_parsed(args[1])
                lean_op = self.operator_map[op]
                return f"{left} {lean_op} {right}"
            return "true"  # Trivial constraint
        
        # Fallback: function call syntax
        else:
            if len(args) == 0:
                return op
            elif len(args) == 1:
                arg_str = self._translate_parsed(args[0])
                return f"{op} {arg_str}"
            else:
                args_str = " ".join(self._translate_parsed(arg) for arg in args)
                return f"{op} {args_str}"


class JSONToLeanConverter:
    """Converts CVXLean JSON to complete Lean optimization code."""
    
    def __init__(self):
        self.translator = SExprToLeanTranslator()
    
    def convert_json_to_lean(self, json_str: str) -> str:
        """Convert JSON string to complete Lean optimization problem."""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        
        if not isinstance(data, dict):
            raise ValueError("JSON must be an object")
        
        # Extract problem components
        prob_name = data.get("prob_name", "optimization_problem")
        domains = data.get("domains", [])
        target = data.get("target", {})
        
        obj_fun = target.get("obj_fun", "(objFun 0)")
        constrs = target.get("constrs", [])
        
        # Generate Lean code
        return self._generate_lean_code(prob_name, domains, obj_fun, constrs)
    
    def _generate_lean_code(self, prob_name: str, domains: List, obj_fun: str, constrs: List) -> str:
        """Generate complete Lean optimization code."""
        
        # Clear translator state
        self.translator.variable_names.clear()
        self.translator.parameter_names.clear()
        
        # Parse objective to collect variables
        obj_lean = self.translator.sexpr_to_lean(obj_fun)
        
        # Parse constraints to collect more variables
        constraint_lines = []
        for i, (constr_name, constr_sexpr) in enumerate(constrs):
            constr_lean = self.translator.sexpr_to_lean(constr_sexpr)
            constraint_lines.append(f"    c{i+1} : {constr_lean}")
        
        # Extract variable information from domains
        domain_info = {}
        for domain_name, domain_bounds in domains:
            domain_info[domain_name] = domain_bounds
        
        # Generate variable declarations
        variables = sorted(self.translator.variable_names)
        parameters = sorted(self.translator.parameter_names)
        
        # Build Lean code
        lines = []
        
        # Add imports
        lines.append("import CvxLean")
        lines.append("")
        
        # Add variable/parameter declarations if any
        if variables or parameters:
            all_vars = variables + parameters
            var_decl = " ".join(all_vars)
            lines.append(f"variable ({var_decl} : ℝ)")
            lines.append("")
        
        # Add domain constraints as separate lemmas if needed
        domain_constraints = []
        for var_name in variables:
            if var_name in domain_info:
                bounds = domain_info[var_name]
                lo, hi, lo_open, hi_open = bounds
                
                if lo != "-inf":
                    if lo_open == "0":  # closed bound
                        domain_constraints.append(f"    domain_{var_name}_lo : {lo} ≤ {var_name}")
                    else:  # open bound
                        domain_constraints.append(f"    domain_{var_name}_lo : {lo} < {var_name}")
                
                if hi != "inf":
                    if hi_open == "0":  # closed bound
                        domain_constraints.append(f"    domain_{var_name}_hi : {var_name} ≤ {hi}")
                    else:  # open bound
                        domain_constraints.append(f"    domain_{var_name}_hi : {var_name} < {hi}")
        
        # Generate the optimization problem
        lines.append(f"-- Optimization problem: {prob_name}")
        if variables:
            var_decl = " ".join(variables)
            lines.append(f"optimization ({var_decl} : ℝ)")
        else:
            lines.append("optimization")
        
        lines.append(f"  minimize {obj_lean}")
        
        if constraint_lines or domain_constraints:
            lines.append("  subject to")
            lines.extend(constraint_lines)
            lines.extend(domain_constraints)
        
        lines.append("  by")
        lines.append("    -- Use CVXLean's pre_dcp tactic to transform to DCP form")
        lines.append("    pre_dcp")
        lines.append("    -- Additional solving steps would go here")
        lines.append("    sorry")
        
        return "\n".join(lines)


def json_to_lean_code(json_str: str) -> str:
    """
    Convert CVXLean JSON to Lean optimization code.
    
    Args:
        json_str: JSON string from cvxpy_to_lean_json converter
        
    Returns:
        Complete Lean optimization problem code
    """
    converter = JSONToLeanConverter()
    return converter.convert_json_to_lean(json_str)


def save_lean_code(json_str: str, filename: str):
    """Save converted Lean code to file."""
    lean_code = json_to_lean_code(json_str)
    with open(filename, 'w') as f:
        f.write(lean_code)


if __name__ == "__main__":
    # Example usage
    print("JSON to Lean Converter")
    print("=" * 40)
    
    # Example JSON from our converter
    example_json = '''
    {
      "request": "PerformRewrite",
      "prob_name": "simple_example",
      "domains": [
        ["x", ["0", "inf", "1", "1"]],
        ["y", ["0", "5", "1", "1"]]
      ],
      "target": {
        "obj_fun": "(objFun (add (var x) (var y)))",
        "constrs": [
          ["c1", "(le 0 (var x))"],
          ["c2", "(le (var y) 5)"]
        ]
      }
    }
    '''
    
    try:
        lean_code = json_to_lean_code(example_json)
        print("Generated Lean code:")
        print("-" * 40)
        print(lean_code)
    except Exception as e:
        print(f"Error: {e}")