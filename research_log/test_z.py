def solve_fractional(weights, values, capacity):
    # compute LP bound manually
    n = len(weights)
    eff = [(values[k]/weights[k], k) for k in range(n)]
    eff.sort(reverse=True)
    z = 0.0
    rem = capacity
    s = -1
    for e, k in eff:
        if weights[k] <= rem:
            rem -= weights[k]
            z += values[k]
        else:
            z += e * rem
            s = k
            break
    return z

w = [10, 20, 30, 40, 50]
v = [100, 180, 240, 280, 300]
# e = [10, 9, 8, 7, 6]
W = 40 
# sorted by e: 10, 20, 30.
# cap=40. 
# i=0 (w=10), i=1 (w=20) -> sum=30.
# split is i=2 (w=30). R = 40 - 30 = 10.
# e_s = 8.
# Z_LP = 100 + 180 + 8*10 = 360.
# Check i=0 (w_i=10). Condition: w_i <= w_s - R -> 10 <= 30 - 10 -> 10 <= 20. Holds!
# Z'_0 expected = 360 - 10*(10 - 8) = 340.
# If we force i=0 OUT: available = 10 (forced out) + 20 + 30 + 40 + 50.
# w_new = [20, 30, 40, 50], v_new = [180, 240, 280, 300]
# eff: 9, 8, 7, 6.
z_out_0 = solve_fractional([20, 30, 40, 50], [180, 240, 280, 300], 40)
print(f"Z'_0 (holds): Formula = 340, True = {z_out_0}")

# Example where it fails:
# w_i > w_s - R.
# Let's force i=1 (w_i=20). Condition: 20 <= 20? Yes.
# Let's make w_i = 25.
w = [25, 20, 30, 40, 50]
v = [250, 180, 240, 280, 300]
# e = [10, 9, 8, 7, 6]
W = 40
# i=0 (w=25), split is i=1 (w=20). R = 40 - 25 = 15.
# w_i = 25. Condition: 25 <= 20 - 15 (25 <= 5). Fails!
# Z_LP = 250 + 9*15 = 385.
# Expected Z'_0 = 385 - 25*(10 - 9) = 360.
z_out_1 = solve_fractional([20, 30, 40, 50], [180, 240, 280, 300], 40)
print(f"Z'_0 (fails): Formula = 360, True = {z_out_1}")

# Symmetric case: j > s.
# w = [10, 20, 30, 40, 50], W = 40. split i=2, w_s=30, R=10.
# j=3 (w=40, e=7). Force IN. 
# condition: w_j <= R -> 40 <= 10. Fails!
# formula Z'_3 = 360 - 40*(8 - 7) = 320.
# True: capacity remaining for others = 40 - 40 = 0.
z_in_3 = solve_fractional([10, 20, 30, 50], [100, 180, 240, 300], 0) + 280
print(f"Z'_3 IN (fails): Formula = 320, True = {z_in_3}")

# j=3, w=5.
w = [10, 20, 30, 5, 50]
v = [100, 180, 240, 35, 300]
# j=3, w=5, e=7. condition: 5 <= 10. Holds!
# formula: 360 - 5*(8 - 7) = 355.
z_in_3_holds = solve_fractional([10, 20, 30, 50], [100, 180, 240, 300], 40 - 5) + 35
print(f"Z'_3 IN (holds): Formula = 355, True = {z_in_3_holds}")
