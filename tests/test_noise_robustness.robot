*** Settings ***
Library    Process
Library    OperatingSystem
Library    String

*** Variables ***
${PY}         python
${SCRIPT}     ${EXECDIR}${/}train_and_evaluate.py
${LANG}       even_a
${N_TRAIN}    200000
${MAX_LEN}    15
${SEED}       123
${FP_SEED}    123
${FP_RATE}    0.15

*** Test Cases ***
Clean Labels Pipeline Works (even_a)
    ${result}=    Run Process    ${PY}    ${SCRIPT}
    ...    --language    ${LANG}
    ...    --n_train     ${N_TRAIN}
    ...    --max_len     ${MAX_LEN}
    ...    --seed        ${SEED}
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ${out}=    Set Variable    ${result.stdout}
    Should Contain    ${out}    Base (clean labels)
    Should Contain    ${out}    Accuracy:
    Should Contain    ${out}    Equivalent:

Noisy Labels (False Positives) Pipeline Works (even_a)
    ${result}=    Run Process    ${PY}    ${SCRIPT}
    ...    --language    ${LANG}
    ...    --n_train     ${N_TRAIN}
    ...    --max_len     ${MAX_LEN}
    ...    --seed        ${SEED}
    ...    --fp_rate     ${FP_RATE}
    ...    --fp_seed     ${FP_SEED}
    ...    --fp_verbose
    ...    stdout=PIPE    stderr=PIPE
    Should Be Equal As Integers    ${result.rc}    0
    ${out}=    Set Variable    ${result.stdout}
    Should Contain    ${out}    Training with false positives
    Should Contain    ${out}    Training with FP (verbose / measured)
    Should Contain    ${out}    TP=
    Should Contain    ${out}    FP rate (measured):
    Should Contain    ${out}    FN rate (measured):
