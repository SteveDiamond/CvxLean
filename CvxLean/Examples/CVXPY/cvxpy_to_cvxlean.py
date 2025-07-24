#!/usr/bin/env python3
"""
CVXPY to CVXLean Complete Integration Tool

Provides end-to-end conversion from CVXPY optimization problems 
to ready-to-use CVXLean Lean code.

Usage:
    from cvxpy_to_cvxlean import cvxpy_to_lean_file
    
    # Convert CVXPY problem directly to Lean file
    cvxpy_to_lean_file(problem, "my_problem.lean", "portfolio_opt")
"""

import cvxpy as cp
from cvxpy_to_lean_json import problem_to_cvxlean_json
from json_to_lean import json_to_lean_code
import os
from typing import Optional


class CVXPYToCVXLeanConverter:
    """Complete converter from CVXPY to CVXLean Lean files."""
    
    def __init__(self):
        self.templates = {
            'basic': self._basic_template,
            'with_solver': self._solver_template, 
            'with_proof': self._proof_template
        }
    
    def convert_problem(self, problem: cp.Problem, prob_name: str, 
                       template: str = 'basic') -> str:
        """Convert CVXPY problem to Lean code using specified template."""
        
        # Step 1: Convert to JSON
        json_str = problem_to_cvxlean_json(problem, prob_name)
        
        # Step 2: Convert JSON to Lean
        lean_code = json_to_lean_code(json_str)
        
        # Step 3: Apply template
        if template in self.templates:
            lean_code = self.templates[template](lean_code, prob_name, problem)
        
        return lean_code
    
    def _basic_template(self, lean_code: str, prob_name: str, problem: cp.Problem) -> str:
        """Basic template with minimal setup."""
        return lean_code
    
    def _solver_template(self, lean_code: str, prob_name: str, problem: cp.Problem) -> str:
        """Template that includes solver integration."""
        lines = lean_code.split('\n')
        
        # Find the line with "sorry" and replace with solver call
        for i, line in enumerate(lines):
            if 'sorry' in line:
                lines[i] = line.replace('sorry', '-- Solve using external solver\n    sorry -- TODO: Add solver call')
        
        # Add solver configuration at the top
        imports_end = 0
        for i, line in enumerate(lines):
            if line.startswith('import') or line.strip() == '':
                imports_end = i
            else:
                break
        
        solver_config = [
            "-- Solver configuration",
            "#check Mosek  -- Uncomment if using Mosek solver",
            ""
        ]
        
        lines = lines[:imports_end+1] + solver_config + lines[imports_end+1:]
        return '\n'.join(lines)
    
    def _proof_template(self, lean_code: str, prob_name: str, problem: cp.Problem) -> str:
        """Template with proof structure."""
        lines = lean_code.split('\n')
        
        # Add proof structure
        proof_section = [
            "",
            f"-- Correctness proof for {prob_name}",
            f"theorem {prob_name}_is_optimal : sorry := by sorry",
            "",
            f"-- Solution extraction",
            f"#check {prob_name}_solution",
            ""
        ]
        
        lines.extend(proof_section)
        return '\n'.join(lines)
    
    def save_to_file(self, problem: cp.Problem, filename: str, 
                    prob_name: str, template: str = 'basic'):
        """Convert problem and save to Lean file."""
        lean_code = self.convert_problem(problem, prob_name, template)
        
        # Ensure .lean extension
        if not filename.endswith('.lean'):
            filename += '.lean'
        
        with open(filename, 'w') as f:
            f.write(lean_code)
        
        print(f"Saved CVXLean code to {filename}")
        return filename


def cvxpy_to_lean_code(problem: cp.Problem, prob_name: str, 
                      template: str = 'basic') -> str:
    """
    Convert CVXPY problem directly to Lean code.
    
    Args:
        problem: CVXPY Problem to convert
        prob_name: Name for the optimization problem  
        template: Template type ('basic', 'with_solver', 'with_proof')
        
    Returns:
        Complete Lean optimization code
    """
    converter = CVXPYToCVXLeanConverter()
    return converter.convert_problem(problem, prob_name, template)


def cvxpy_to_lean_file(problem: cp.Problem, filename: str, 
                      prob_name: str, template: str = 'basic') -> str:
    """
    Convert CVXPY problem and save to Lean file.
    
    Args:
        problem: CVXPY Problem to convert
        filename: Output filename (will add .lean if needed)
        prob_name: Name for the optimization problem
        template: Template type ('basic', 'with_solver', 'with_proof')
        
    Returns:
        Path to generated file
    """
    converter = CVXPYToCVXLeanConverter()
    return converter.save_to_file(problem, filename, prob_name, template)


def generate_examples():
    """Generate example Lean files from common optimization problems."""
    
    print("Generating CVXLean examples from CVXPY problems...")
    
    # Example 1: Simple Linear Program
    print("\n1. Simple Linear Program")
    x = cp.Variable(name="x")
    y = cp.Variable(name="y") 
    
    objective = cp.Minimize(x + 2*y)
    constraints = [x >= 0, y >= 0, x + y <= 1]
    lp_problem = cp.Problem(objective, constraints)
    
    cvxpy_to_lean_file(lp_problem, "simple_lp.lean", "simple_lp")
    
    # Example 2: Quadratic Program  
    print("2. Quadratic Program")
    x = cp.Variable(name="x")
    
    objective = cp.Minimize(cp.square(x - 1))
    constraints = [x >= 0, x <= 2]
    qp_problem = cp.Problem(objective, constraints)
    
    cvxpy_to_lean_file(qp_problem, "quadratic.lean", "quadratic_problem", "with_solver")
    
    # Example 3: Portfolio Optimization
    print("3. Portfolio Optimization")
    import numpy as np
    n = 3
    w = cp.Variable(n, name="weights")
    mu = np.array([0.1, 0.2, 0.15])
    
    objective = cp.Minimize(cp.sum_squares(w) - mu.T @ w)
    constraints = [cp.sum(w) == 1, w >= 0]
    portfolio_problem = cp.Problem(objective, constraints)
    
    cvxpy_to_lean_file(portfolio_problem, "portfolio.lean", "portfolio_optimization", "with_proof")
    
    # Example 4: Norm Constraint
    print("4. Problem with Norm Constraint")
    x = cp.Variable(2, name="x")
    
    objective = cp.Minimize(cp.sum(x))
    constraints = [cp.norm(x, 2) <= 1, x >= 0]
    norm_problem = cp.Problem(objective, constraints)
    
    cvxpy_to_lean_file(norm_problem, "norm_constraint.lean", "norm_constrained")
    
    print("\nGenerated 4 example Lean files!")
    print("Files created:")
    for filename in ["simple_lp.lean", "quadratic.lean", "portfolio.lean", "norm_constraint.lean"]:
        if os.path.exists(filename):
            print(f"  ✓ {filename}")


if __name__ == "__main__":
    print("CVXPY to CVXLean Complete Integration Tool")
    print("=" * 50)
    
    # Generate examples
    generate_examples()
    
    print("\n" + "=" * 50)
    print("Usage examples:")
    print("=" * 50)
    
    # Show usage examples
    print("\nExample 1: Basic conversion")
    print("```python")
    print("import cvxpy as cp")
    print("from cvxpy_to_cvxlean import cvxpy_to_lean_file")
    print("")
    print("x = cp.Variable(name='x')")
    print("problem = cp.Problem(cp.Minimize(x), [x >= 0])")
    print("cvxpy_to_lean_file(problem, 'my_problem.lean', 'my_optimization')")
    print("```")
    
    print("\nExample 2: With solver template")
    print("```python")
    print("cvxpy_to_lean_file(problem, 'solver_problem.lean', 'optimization', 'with_solver')")
    print("```")
    
    print("\nExample 3: With proof template")
    print("```python") 
    print("cvxpy_to_lean_file(problem, 'proof_problem.lean', 'optimization', 'with_proof')")
    print("```")