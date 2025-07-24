import CvxLean

noncomputable section

open CvxLean Minimization Real BigOperators

def portfolio_optimization :=
  optimization (weights : Fin 3 → ℝ)
    minimize (∑ i, ((weights i) ^ 2) : ℝ)
    subject to
      c1 : ∑ i, (weights i) = 1
      c2 : ∀ i, 0 ≤ weights i

-- Solve the problem directly (applies pre_dcp automatically)
solve portfolio_optimization

-- Check the results
#eval portfolio_optimization.status
#eval portfolio_optimization.solution
#eval portfolio_optimization.value

end