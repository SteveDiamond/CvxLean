#!/usr/bin/env python3
"""
Complete CVXPY to CVXLean Workflow Examples

Demonstrates the full pipeline from CVXPY optimization problems
to working CVXLean Lean code with different templates and use cases.
"""

import cvxpy as cp
import numpy as np
import json
from cvxpy_to_lean_json import problem_to_cvxlean_json
from json_to_lean import json_to_lean_code
from cvxpy_to_cvxlean import cvxpy_to_lean_file, cvxpy_to_lean_code


def example_1_simple_workflow():
    """Example 1: Basic linear programming workflow."""
    print("=" * 60)
    print("EXAMPLE 1: Simple Linear Program Workflow")
    print("=" * 60)
    
    print("\nStep 1: Define CVXPY problem")
    print("-" * 30)
    
    # Define the optimization problem in CVXPY
    x = cp.Variable(name="x")
    y = cp.Variable(name="y")
    
    objective = cp.Minimize(3*x + 2*y)
    constraints = [
        x + y >= 1,
        2*x + y <= 3,
        x >= 0,
        y >= 0
    ]
    
    problem = cp.Problem(objective, constraints)
    print("CVXPY Problem:")
    print(problem)
    
    print("\nStep 2: Convert to JSON")
    print("-" * 30)
    json_str = problem_to_cvxlean_json(problem, "linear_program")
    print("Generated JSON (formatted):")
    print(json.dumps(json.loads(json_str), indent=2))
    
    print("\nStep 3: Convert to Lean code")
    print("-" * 30)
    lean_code = json_to_lean_code(json_str)
    print("Generated Lean code:")
    print(lean_code)
    
    print("\nStep 4: Save to file")
    print("-" * 30)
    filename = cvxpy_to_lean_file(problem, "linear_program.lean", "linear_program")
    print(f"Saved to {filename}")
    
    return problem, json_str, lean_code


def example_2_portfolio_optimization():
    """Example 2: Portfolio optimization with different templates."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Portfolio Optimization with Templates")
    print("=" * 60)
    
    # Modern portfolio theory problem
    n_assets = 4
    np.random.seed(42)
    
    # Expected returns
    mu = np.array([0.12, 0.10, 0.07, 0.03])
    
    # Risk aversion parameter
    gamma = 0.5
    
    print("\nStep 1: Define portfolio optimization problem")
    print("-" * 40)
    
    # Portfolio weights
    w = cp.Variable(n_assets, name="weights")
    
    # Objective: maximize return - risk penalty
    # Using sum_squares as a simple risk model
    objective = cp.Minimize(gamma * cp.sum_squares(w) - mu.T @ w)
    
    constraints = [
        cp.sum(w) == 1,  # Weights sum to 1
        w >= 0,          # Long-only portfolio
        w <= 0.4         # No more than 40% in any asset
    ]
    
    portfolio_problem = cp.Problem(objective, constraints)
    print("Portfolio Problem:")
    print(portfolio_problem)
    
    print("\nStep 2: Generate with different templates")
    print("-" * 40)
    
    # Basic template
    print("2a. Basic template:")
    basic_code = cvxpy_to_lean_code(portfolio_problem, "portfolio_basic", "basic")
    with open("portfolio_basic.lean", "w") as f:
        f.write(basic_code)
    print("  ✓ Saved to portfolio_basic.lean")
    
    # Solver template
    print("2b. Solver template:")
    solver_code = cvxpy_to_lean_code(portfolio_problem, "portfolio_solver", "with_solver")
    with open("portfolio_solver.lean", "w") as f:
        f.write(solver_code)
    print("  ✓ Saved to portfolio_solver.lean")
    
    # Proof template
    print("2c. Proof template:")
    proof_code = cvxpy_to_lean_code(portfolio_problem, "portfolio_proof", "with_proof") 
    with open("portfolio_proof.lean", "w") as f:
        f.write(proof_code)
    print("  ✓ Saved to portfolio_proof.lean")
    
    return portfolio_problem


def example_3_quadratic_programming():
    """Example 3: Quadratic programming with constraints."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Quadratic Programming")
    print("=" * 60)
    
    print("\nStep 1: Define QP problem")
    print("-" * 30)
    
    # Quadratic program: minimize ||Ax - b||^2 subject to constraints
    m, n = 3, 2
    np.random.seed(123)
    A = np.random.randn(m, n)
    b = np.random.randn(m)
    
    x = cp.Variable(n, name="x")
    
    objective = cp.Minimize(cp.sum_squares(A @ x - b))
    constraints = [
        cp.sum(x) <= 1,
        x >= 0
    ]
    
    qp_problem = cp.Problem(objective, constraints)
    print("Quadratic Problem:")
    print(qp_problem)
    
    print("\nStep 2: Show JSON structure") 
    print("-" * 30)
    json_str = problem_to_cvxlean_json(qp_problem, "quadratic_program")
    data = json.loads(json_str)
    
    print("Objective S-expression:")
    print(f"  {data['target']['obj_fun']}")
    print("\nConstraints:")
    for name, sexpr in data['target']['constrs']:
        print(f"  {name}: {sexpr}")
    
    print("\nStep 3: Generate Lean code")
    print("-" * 30)
    lean_code = cvxpy_to_lean_code(qp_problem, "quadratic_program", "with_solver")
    filename = "quadratic_program.lean"
    with open(filename, "w") as f:
        f.write(lean_code)
    print(f"✓ Saved to {filename}")
    
    return qp_problem


def example_4_advanced_constraints():
    """Example 4: Advanced constraints (norms, etc.)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Advanced Constraints")
    print("=" * 60)
    
    print("\nStep 1: Problem with various constraint types")
    print("-" * 40)
    
    # Variables
    x = cp.Variable(3, name="x")
    y = cp.Variable(name="y")
    
    # Objective with mixed terms
    objective = cp.Minimize(cp.sum(x) + cp.square(y))
    
    # Various constraint types
    constraints = [
        cp.norm(x, 2) <= 1,      # L2 norm constraint
        cp.sum(x) == y,          # Equality constraint
        x >= 0,                  # Non-negativity
        y <= 5,                  # Upper bound
        cp.norm(x, 1) <= 2       # L1 norm constraint (if supported)
    ]
    
    advanced_problem = cp.Problem(objective, constraints)
    print("Advanced Problem:")
    print(advanced_problem)
    
    print("\nStep 2: Analyze S-expression translation")
    print("-" * 40)
    
    json_str = problem_to_cvxlean_json(advanced_problem, "advanced_constraints")
    data = json.loads(json_str)
    
    print("S-expressions generated:")
    print(f"Objective: {data['target']['obj_fun']}")
    for i, (name, sexpr) in enumerate(data['target']['constrs']):
        print(f"Constraint {i+1}: {sexpr}")
    
    print("\nStep 3: Generate final Lean code") 
    print("-" * 40)
    filename = cvxpy_to_lean_file(advanced_problem, "advanced_constraints.lean", 
                                 "advanced_constraints", "with_proof")
    print(f"✓ Generated {filename}")
    
    return advanced_problem


def workflow_summary():
    """Print summary of the complete workflow."""
    print("\n" + "=" * 60)
    print("WORKFLOW SUMMARY")
    print("=" * 60)
    
    print("""
The CVXPY to CVXLean conversion workflow consists of:

1. **CVXPY Problem Definition**
   - Define variables: x = cp.Variable(...)
   - Set objective: cp.Minimize(...) or cp.Maximize(...)
   - Add constraints: [constraint1, constraint2, ...]
   - Create problem: cp.Problem(objective, constraints)

2. **JSON Generation** 
   - Convert to EggRequest format: problem_to_cvxlean_json(problem, name)
   - S-expressions capture problem structure
   - Domain information extracted from constraints

3. **Lean Translation**
   - Parse S-expressions to Lean syntax
   - Generate variable declarations
   - Create optimization block with CVXLean syntax
   - Add solving template (basic/solver/proof)

4. **CVXLean Integration**
   - Import generated .lean file into your CVXLean project
   - Use pre_dcp tactic for DCP transformation
   - Add solver calls for numerical solution
   - Develop correctness proofs as needed

Key Files Generated:
""")
    
    import os
    lean_files = [f for f in os.listdir('.') if f.endswith('.lean')]
    for filename in sorted(lean_files):
        if os.path.exists(filename):
            print(f"  ✓ {filename}")
    
    print(f"""
Total: {len(lean_files)} Lean files generated

Next Steps:
- Copy .lean files to your CVXLean project
- Add appropriate imports and dependencies  
- Customize solver configuration
- Develop formal proofs of optimality
- Integrate with existing Lean mathematics
""")


if __name__ == "__main__":
    print("CVXPY to CVXLean: Complete Workflow Examples")
    print("=" * 60)
    
    # Run all examples
    try:
        example_1_simple_workflow()
        example_2_portfolio_optimization() 
        example_3_quadratic_programming()
        example_4_advanced_constraints()
        workflow_summary()
        
        print("\n" + "=" * 60)
        print("🎉 All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error in workflow: {e}")
        import traceback
        traceback.print_exc()