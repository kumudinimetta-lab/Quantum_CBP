import json, numpy as np

print('\n=== LARGE SCALE ALPHA AUDIT ===')
try:
    with open('../paper/results/large_scale_benchmark.json') as f:
        data = json.load(f)['data']
    print('Pisinger Class | n | Seeds/Instances | Raw Data File | alpha available? | median alpha | Q1 | Q3 | IQR | mean | std | min | max')
    for row in data:
        if 'alphas' in row:
            alphas = np.array(row['alphas'])
            med = np.median(alphas)
            q1 = np.percentile(alphas, 25)
            q3 = np.percentile(alphas, 75)
            iqr = q3 - q1
            mean = np.mean(alphas)
            std = np.std(alphas)
            mi = np.min(alphas)
            ma = np.max(alphas)
            print(f'{row["class"]} | {row["n"]} | {len(alphas)} | ../paper/results/large_scale_benchmark.json | YES | {med:.5f} | {q1:.5f} | {q3:.5f} | {iqr:.5f} | {mean:.5f} | {std:.5f} | {mi:.5f} | {ma:.5f}')
except Exception as e:
    print('Error:', e)
