# Model card: term-deposit call prioritisation

## Purpose
A Portuguese bank can phone only 10 % of the clients on a list in one campaign wave. The model scores every client before any call is made, and the 10 % with the highest scores are called. This is a teaching model built on the UCI Bank Marketing data (2008-2010). It must not be used to draw conclusions about real banks or real clients.

## Data
- `train.csv`: 32,940 rows, 11.3 % "yes". `test.csv`: 8,236 rows without the answer.
- `test.csv` has no `y` and no `duration`. `duration` (call length) is known only after the call, so using it would be data leakage and I did not use it. I also dropped `id`, which is only a row number.
- The value "unknown" appears in job, marital, education, default, housing and loan (for example default: 6,871 rows). `pdays = 999` means "never contacted before" and covers 96.2 % of the rows.
- I kept 20 % of `train.csv` as my own hold-out (stratified, fixed seed) and used it only once, at the end.

## Pipeline
1. `pdays` is replaced by a flag `pdays_never` and the value 0 (helper function in `features.py`).
2. Numeric columns are standardised and categorical columns are one-hot encoded ("unknown" stays as its own category).
3. Random forest (200 trees, `min_samples_leaf = 5`).

All steps are inside one scikit-learn Pipeline, so they are fitted on the training folds only. The saved pipeline accepts the raw columns of `test.csv` without any manual step.

## Model selection
5-fold stratified cross-validation on the development part, the same folds for every model (mean ± std over folds).
- Majority class: ROC-AUC 0.5000, accuracy 0.8873. Accuracy is misleading on these data.
- Logistic regression: ROC-AUC 0.7906 ± 0.0124, AP 0.4518 ± 0.0199.
- Random forest: ROC-AUC 0.7908 ± 0.0126, AP 0.4699 ± 0.0178.
- Decision tree (depth 5): ROC-AUC 0.7701 ± 0.0134, clearly worse in all folds.
- In ROC-AUC, logistic regression and the forest are tied (inside the noise). In average precision the forest was better in all 5 folds (mean difference +0.018), so I chose it.
- Balanced class weights and imputing "unknown" with the most frequent value changed the scores only inside the noise, so I did not use them. Tuning C of logistic regression gave no gain either.

## Results on the hold-out (used once)
- ROC-AUC 0.8001, average precision 0.4794 (close to the cross-validation results).
- Top 10 % rule (659 clients called, cutoff 0.3371): precision 0.516, recall 0.458, lift 4.58 over calling at random.
- Of the 659 called clients, 340 said yes and 319 said no. 402 buyers were not reached because of the 10 % limit.

## Limits and ways it can fail
- The split is random, but real use is "train on the past, call in the future". The model has seen the same market conditions (for example euribor3m levels) as the hold-out clients, so these numbers are probably too optimistic.
- The data are from 2008-2010. If interest rates or the economy change, the score distribution can shift and the ranking can get worse.
- The cutoff is a rank (top 10 %), not a probability, so it depends on the list being scored.
- Clients with a successful previous campaign are strongly favoured, so new clients may be ranked low.

## What to monitor after launch
- The share of "yes" among called clients compared with the expected 51.6 % precision.
- The distribution of scores and of euribor3m compared with the training data.
- The share of "unknown" values in the incoming data.
- The conversion rate in a small random sample of clients who are not called, to check recall.