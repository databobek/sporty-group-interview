# Design: Test execution and bug reports (Part A.2)

## Decision log

Decided on 2026-11-12.

| # | Decision | Options considered | Chosen |
|---|---|---|---|
| E1 | How steps are executed | all scripted / all by hand / mixed | Mixed: UI steps by hand, API steps as scripted HTTP calls with every exchange saved. UI and API share one balance, so each hand-over between them is coordinated. |
| E2 | Evidence | an `evidence/` folder / brief notes only | An `evidence/` folder in the repo, with screenshots and API exchanges and the user-id masked. |
| E3 | Exploratory scope | error modal / stake input / API protocol / filters | Stake input edge cases only. |
| E4 | Documents | one file in two parts / two files | Two files: `execution-results.md` and `bug-reports.md`. |
| E5 | TC-02 with the broken reset | as written, then by intent / by intent only / as written only | As written, then by intent: run the steps literally and record the deviations, then repeat the boundary with the real balance (balance + €0.01 rejected, a stake equal to the balance accepted). |
| E6 | Severity scale | money impact / user impact | Money impact. Critical: money moved or recorded wrongly, or a security hole. High: a wrong bet or a wrong record of a bet, or a spec rule not enforced. Medium: a spec deviation with a workaround or no direct money impact. Low: cosmetic or copy. |

## Calls made during execution

| # | Situation | Decision |
|---|---|---|
| E7 | TC-01 was run without the P3 reset | Step 2 stays valid. It records the starting balance, and the reset is a test-data precondition, not part of the feature. Later expectations are relative to the recorded €110.00. |
| E8 | TC-02 step 6 (€25.50) could not be placed because the balance was already negative | Recorded as "n/a, the expectation no longer applies". The run by intent (E5) covers the stake-equals-balance boundary. |
| E9 | The API €20.01 call ran after the balance had already reached €0.00 | The exact boundary (balance €20.00, stake €20.01) was re-run through the API alone. |
| E10 | The exploratory notes skipped X1 to X4, X8, X11 and X14 | The screenshots cover them, and the results were read from the screenshots. |
| E11 | The evidence for "bet on a past match accepted" existed only in the gitignored `allure-results/` | One €1 API bet was placed on a match dated 2026-02-27 to capture it in `evidence/`. |
| E12 | Severities | Assigned with the E6 scale. BUG-03 (reset) is rated Critical because the stored balance is wrong money; it is a test-support endpoint, so High is also defensible. |
