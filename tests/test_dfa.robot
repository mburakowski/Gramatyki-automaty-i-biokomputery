*** Settings ***
Library    ${CURDIR}/resources/KeywordsLibrary.py

*** Test Cases ***
Test Word Accepted
    ${res}=    Check Accepts    aab
    Should Be True    ${res}

Test Word Rejected
    ${res}=    Check Accepts    abaa
    Should Be False    ${res}
