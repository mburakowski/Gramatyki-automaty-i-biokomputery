*** Settings ***
Library    Process
Library    String

*** Variables ***
${PY}        python
${SCRIPT}    ${EXECDIR}${/}train_and_evaluate.py

# List of all supported regular languages
@{LANGUAGES}
...    even_a
...    ends_with_ab
...    contains_aa
...    no_bb
...    mod3_a

*** Test Cases ***
# Trains and validates the learning pipeline for all supported languages
# This test ensures that the full pipeline completes without errors
Train And Validate All Languages
    FOR    ${lang}    IN    @{LANGUAGES}
        Run Language Test    ${lang}
    END

*** Keywords ***
# Executes the training and evaluation pipeline for a single language
# and verifies that basic output metrics are produced
Run Language Test
    [Arguments]    ${LANG}

    # Log the currently tested language for traceability
    Log    Testing language: ${LANG}

    # Run the full training and evaluation process for the given language
    ${result}=    Run Process
    ...    ${PY}
    ...    ${SCRIPT}
    ...    --language    ${LANG}
    ...    stdout=PIPE
    ...    stderr=PIPE

    # Verify that the process completed successfully
    Should Be Equal As Integers    ${result.rc}    0

    # Capture standard output for further validation
    ${out}=    Set Variable    ${result.stdout}

    # Verify that key evaluation metrics are reported
    Should Contain    ${out}    Accuracy:
    Should Contain    ${out}    Equivalent:
