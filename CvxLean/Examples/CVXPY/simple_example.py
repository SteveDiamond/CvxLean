#!/usr/bin/env python3
"""
Simple CVXPY to CVXLean example following the pattern of other examples in CvxLean/Examples/

This demonstrates the basic workflow for converting CVXPY optimization problems
to CVXLean Lean code that can be integrated into formal verification workflows.
"""

import cvxpy as cp
import numpy as np
from cvxpy_to_cvxlean import cvxpy_to_lean_file


def simple_linear_program():
    """Simple linear program similar to examples in CVXLean."""
    print("=== Simple Linear Program ===")
    
    # Variables
    x = cp.Variable(name="x")
    y = cp.Variable(name="y")
    
    # Objective: minimize cost 
    objective = cp.Minimize(3*x + 2*y)
    
    # Constraints
    constraints = [
        x + y >= 1,      # demand constraint
        2*x + y <= 3,    # capacity constraint  
        x >= 0,          # non-negativity
        y >= 0
    ]
    
    # Create problem
    problem = cp.Problem(objective, constraints)
    
    print("CVXPY Problem:")
    print(problem)
    
    # Convert to Lean
    filename = cvxpy_to_lean_file(problem, "SimpleLinearProgram.lean", "simple_lp")
    print(f"\nGenerated Lean file: {filename}")
    
    return problem


def portfolio_optimization():
    """Portfolio optimization example."""
    print("\n=== Portfolio Optimization ===")
    
    # Problem parameters
    n_assets = 3
    expected_returns = np.array([0.12, 0.10, 0.07])  # Expected returns
    risk_aversion = 0.5
    
    # Decision variable: portfolio weights
    w = cp.Variable(n_assets, name="weights")
    
    # Objective: maximize return - risk penalty
    # Using sum_squares as simple risk model
    objective = cp.Minimize(risk_aversion * cp.sum_squares(w) - expected_returns.T @ w)
    
    # Constraints
    constraints = [
        cp.sum(w) == 1,  # weights sum to 1
        w >= 0,          # long-only (no short selling)
        w <= 0.4         # max 40% in any single asset
    ]
    
    # Create problem
    problem = cp.Problem(objective, constraints)
    
    print("CVXPY Problem:")
    print(problem)
    
    # Convert to Lean with proof template
    filename = cvxpy_to_lean_file(problem, "PortfolioOptimization.lean", 
                                 "portfolio_opt", "with_proof")
    print(f"\nGenerated Lean file: {filename}")
    
    return problem


def quadratic_program():
    """Quadratic programming example."""
    print("\n=== Quadratic Program ===")
    
    # Variables
    x = cp.Variable(2, name="x")
    
    # Quadratic objective: minimize ||x - target||^2
    target = np.array([1.0, 0.5])
    objective = cp.Minimize(cp.sum_squares(x - target))
    
    # Linear constraints
    A = np.array([[1, 1], [1, -1]])
    b = np.array([1, 0])
    constraints = [
        A @ x <= b,  # linear inequality constraints
        x >= 0       # non-negativity
    ]
    
    # Create problem
    problem = cp.Problem(objective, constraints)
    
    print("CVXPY Problem:")
    print(problem)
    
    # Convert to Lean with solver template
    filename = cvxpy_to_lean_file(problem, "QuadraticProgram.lean", 
                                 "quadratic_prog", "with_solver")
    print(f"\nGenerated Lean file: {filename}")
    
    return problem


if __name__ == "__main__":
    print("CVXPY to CVXLean Integration Examples")
    print("=" * 50)
    
    # Run examples
    lp_problem = simple_linear_program()
    portfolio_problem = portfolio_optimization()
    qp_problem = quadratic_program()
    
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)
    print("""
Generated Lean files:
  ✓ SimpleLinearProgram.lean    - Basic linear program
  ✓ PortfolioOptimization.lean  - Portfolio optimization with proofs
  ✓ QuadraticProgram.lean       - Quadratic program with solver setup

Usage in CVXLean:
1. Copy these .lean files to your CVXLean project
2. Import them in your Lean code
3. Use the pre_dcp tactic for DCP transformation
4. Add solver calls for numerical solutions
5. Develop formal proofs of optimality

Example Lean usage:
```lean
import SimpleLinearProgram

#check simple_lp  -- Check the optimization problem
-- Add solver and proof development
```
""")