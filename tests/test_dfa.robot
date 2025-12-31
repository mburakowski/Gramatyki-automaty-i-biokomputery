*** Settings ***
Library    ${CURDIR}/resources/KeywordsLibrary.py
Library    Collections

*** Test Cases ***
# Verifies that a word which should belong to the language
# (even number of 'a' symbols) is accepted by the teacher DFA
Test Word Accepted
    ${res}=    Teacher Accepts    even_a    aab
    Should Be True    ${res}

# Verifies that a word which violates the language definition
# (odd number of 'a' symbols) is correctly rejected by the teacher DFA
Test Word Rejected
    ${res}=    Teacher Accepts    even_a    abaa
    Should Be Equal As Strings    ${res}    False
