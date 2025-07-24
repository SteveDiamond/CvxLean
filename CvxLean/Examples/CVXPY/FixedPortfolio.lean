import CvxLean

noncomputable section

open CvxLean Minimization Real

def portfolio_optimization :=
  optimization (weights : ℝ)
    minimize (sum_squares weights : ℝ)
    subject to
      c1 : sum weights = 1
      c2 : 0 ≤ weights

-- Solve the problem directly (applies pre_dcp automatically)
solve portfolio_optimization

-- Check the results
#eval portfolio_optimization.status
#eval portfolio_optimization.solution
#eval portfolio_optimization.value

end