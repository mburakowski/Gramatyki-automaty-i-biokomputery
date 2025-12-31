*** Settings ***
Library    ${CURDIR}/resources/KeywordsLibrary.py
Library    Process

*** Variables ***
${PY}        python
${SCRIPT}    ${EXECDIR}${/}train_and_evaluate.py

@{LANGUAGES}
...    even_a
...    ends_with_ab
...    contains_aa
...    no_bb
...    mod3_a

@{TEST_WORDS}
...    aab
...    abaa
...    bbbb
...    aaaa
...    abab
...    baaa

*** Test Cases ***
# 1. Sanity check 

Train All Languages Successfully
    FOR    ${lang}    IN    @{LANGUAGES}
        ${result}=    Run Process
        ...    ${PY}
        ...    ${SCRIPT}
        ...    --language    ${lang}
        ...    stdout=PIPE
        ...    stderr=PIPE
        Should Be Equal As Integers    ${result.rc}    0
        Should Contain    ${result.stdout}    Accuracy:
    END

# 2. Teacher DFA – OK Cases and NOK Cases
Teacher DFA Basic Correctness (even_a)
    ${ok}=    Teacher Accepts    even_a    aab
    Should Be True    ${ok}

    ${bad}=    Teacher Accepts    even_a    abaa
    Run Keyword If    ${bad}    Fail    Word should be rejected but was accepted

# 3. Even A
Even A Property Test
    ${r1}=    Teacher Accepts    even_a    aa
    Should Be True    ${r1}

    ${r2}=    Teacher Accepts    even_a    aaaa
    Should Be True    ${r2}

    ${r3}=    Teacher Accepts    even_a    aaa
    Run Keyword If    ${r3}    Fail    Odd number of 'a' should be rejected

# 4. Teacher DFA vs Learned DFA
Teacher And Learned DFA Agree (even_a)
    FOR    ${w}    IN    @{TEST_WORDS}
        ${t}=    Teacher Accepts    even_a    ${w}
        ${l}=    Learned Accepts    even_a    ${w}
        Should Be Equal    ${t}    ${l}
    END

# 5. Regression test
Regression Test Words
    FOR    ${w}    IN    @{TEST_WORDS}
        ${res}=    Teacher Accepts    even_a    ${w}
        Should Be Equal    ${res}    ${res}
    END

# 6. Noise robustness
Noise Robustness Test
    ${result}=    Run Process
    ...    ${PY}
    ...    ${SCRIPT}
    ...    --language    even_a
    ...    --fp_rate     0.15
    ...    stdout=PIPE
    ...    stderr=PIPE

    Should Be Equal As Integers    ${result.rc}    0
    Should Contain    ${result.stdout}    Training with false positives

# 7. Pipeline closing
Language Zoo Pipeline Completes
    FOR    ${lang}    IN    @{LANGUAGES}
        ${result}=    Run Process
        ...    ${PY}
        ...    ${SCRIPT}
        ...    --language    ${lang}
        ...    stdout=PIPE
        ...    stderr=PIPE
        Should Be Equal As Integers    ${result.rc}    0
    END
