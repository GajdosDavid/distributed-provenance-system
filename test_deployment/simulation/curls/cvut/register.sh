curl --location 'http://munich-prov-storage-provider.de:8000/api/v1/organizations/CVUT' \
--header 'Content-Type: application/json' \
--data '{
    "clientCertificate": "-----BEGIN CERTIFICATE-----\nMIIDMjCCAhqgAwIBAgIBBjANBgkqhkiG9w0BAQsFADApMQswCQYDVQQGEwJQTDEa\nMBgGA1UEAwwRaW50ZXJtZWRpYXRlMV9jYTQwHhcNMjQwNDA3MTYzMDI2WhcNMzQw\nMjE0MTYzMDI2WjArMQswCQYDVQQGEwJDWjENMAsGA1UECgwEQ1ZVVDENMAsGA1UE\nAwwEQ1ZVVDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMCUniAOQJCl\nko4mT6h0yMMzw3rtMpUS6YwRckgwnVeB9i2qg3w8SptdeqGeSZwNOomFPwQZ+dTi\nZ4tal/HPe9YoJRBEz8zKzdqYznC6QTmc7eLFwZQjoCUbwgIpWgQolnvFewSCu4EA\nauztS+Ss1Ria0XfJlO0kAIuGcR2IQ9epl7FUq3gyJUqCPon3ekH1YSm8Ygo0jHPT\nukd/1GAlj5iVAIlej1xbcx4+5SV7MK45I+Syv8OvuKSDS7g1uDH/8VrWzzTT2Adm\nrbSjDEZPmiTdNdUiDdGxtr31GqPpQQvEfsrLLcrgEh7LXyf1yAH4y3RlcqLTYQhk\n9lTq66ZUs5cCAwEAAaNjMGEwHwYDVR0RAQH/BBUwE4YRdXJuOnV1aWQ6dW5pLWN2\ndXQwHQYDVR0OBBYEFHXgh2EPMhKfq4EIFG0SDEclNj4NMB8GA1UdIwQYMBaAFA0D\nEbiyh2pJ6qCD8Xg0IsuUMg+JMA0GCSqGSIb3DQEBCwUAA4IBAQBDPT3bdRFInCfM\nas+PdjkZ/0EAGckOb9+tJWsMhnjxaEA2IE7EodH1LSLKbpQlDH72hnpZdaiYz/vg\nFyTgOSw2BH25Vd6yUS9pMQmqOLYFWxaUy2iwbAsaubeLh6r5ZtAvVXqYD+R5r2Pg\n7t4fXAQ/LHOqBZzX3Sj1quMpgoNK8p4yJhB7uJ4BKUIUJwTYGgr+qn5AmjtYgMDS\nsreY+dleRYquLkJOWQjRH7puH88KvZ+sQZhZZ2AVATxnUUiPaI7+rgabhjyq3Br3\ncWfxZLwtUpNrz25YHURSNI+hrpVEmcb86e22UagaCEf/XK01oTNT1Skf5Kpd+Kro\nqeYP0nIM\n-----END CERTIFICATE-----\n",
    "intermediateCertificates": [
        "-----BEGIN CERTIFICATE-----\nMIIDXDCCAkSgAwIBAgIBAzANBgkqhkiG9w0BAQsFADApMQswCQYDVQQGEwJQTDEa\nMBgGA1UEAwwRaW50ZXJtZWRpYXRlMl9jYTQwHhcNMjQwNDA3MTYzMDI0WhcNMzQw\nMjE1MTYzMDI0WjApMQswCQYDVQQGEwJQTDEaMBgGA1UEAwwRaW50ZXJtZWRpYXRl\nMV9jYTQwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDyB+mrjjoGkrvj\nb+Bfdn/ZVfbYAZemQ3L7ZJbLFgSKAEv2ATbvbto4OIidJxrpah59lRScI1M2TDgh\ntAu8pYhGkeApJdKpKyW7kinZ8JntUTIVfH5Gk/ecl7B2tVhlTD+8QfY1OM+6lhyn\nS/VZ2sI8c8ZcOmcH2Z7L2Gi5pSUarxX/Xe189ro1wFoNjYz3DxVUBdXS1LjNCwvc\nK6YEOvMPWacYy1d+/DTFARabQHpzMbKkwRpW01W5btVIlAZFn8fkhNFQRzkSco7N\nxYJHyDwLsbKizeoAHztb3bbYPxku4MmThL6KQNKoIPkkH6i2dg7smVihV/jn4OKE\n4Xxth52fAgMBAAGjgY4wgYswDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC\nAgQwKAYDVR0RAQH/BB4wHIYadXJuOnV1aWQ6aW50ZXJtZWRpYXRlMV9jYTQwHQYD\nVR0OBBYEFA0DEbiyh2pJ6qCD8Xg0IsuUMg+JMB8GA1UdIwQYMBaAFAxsfpwuzw7D\nksOE2PJoyXA9oG0RMA0GCSqGSIb3DQEBCwUAA4IBAQCGMt627Kll0GjcCSkEeDaI\nC+pgh9ESQ1TbhJoBLPbYX/aCW/lr8O/PynIJYjA1OJVNJTrSKFinluAF8U6S7FM2\nSm2aYhNLN1HUARSX4zfGDu24LJu9fAEsWWh0PhoaWVUtZwZvm5vhoy4/1jdp3ICG\nEYpyvkYs3/mY1cUcWjXqjFGkR+49lp2EGxSIfpf8MvuDpBUgUsKoA9PgmVYvrV93\n4zHBwD1LDxrogx+0T2EYQ4RLdg1xouDizm4fNtrYZvif9KlS3o/TgCliV35/txe5\nudqfJLyyaRQAIprVhnpDebdk4/HSLKWJDriJ+mBXagf3nyQp6VOXnA7w2lsDxAc3\n-----END CERTIFICATE-----\n",
        "-----BEGIN CERTIFICATE-----\nMIIDTjCCAjagAwIBAgIBBzANBgkqhkiG9w0BAQsFADAbMQswCQYDVQQGEwJQTDEM\nMAoGA1UEAwwDQ0E0MB4XDTI0MDQwNzE2MzAyM1oXDTM0MDIxNjE2MzAyM1owKTEL\nMAkGA1UEBhMCUEwxGjAYBgNVBAMMEWludGVybWVkaWF0ZTJfY2E0MIIBIjANBgkq\nhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvTGcCZ0x3SMH07twRrlH3Hu1MRYDgm2s\n4Z3jqnJygd4W+hsRsGvnWJIGTObB2rr5nyfLRSv2d58dFUEUth1E45jqQKVKQgro\n5xGGJSFP72S1/70chCSDH2PgoUEqVW4eq0oTBjficferFnMShMBDwwd9nvJPIWnQ\nd/zhhswMKuXNJyRu9c4+5ESegtXyDJLyrUWIUBVOgsr9Dr6rr7zEf4xCkb8DxTFA\nTYSLF4FsnWnhWOL8+Hest+uhKhUWi964isC3rvR7Dcau2uiXgVcUYojD6oTfPZT5\nA74dS5QflYjd+s7HQ7kPmE/bYiSoznzdXuzzLQWioAxKexCRYoiBcwIDAQABo4GO\nMIGLMA8GA1UdEwEB/wQFMAMBAf8wDgYDVR0PAQH/BAQDAgIEMCgGA1UdEQEB/wQe\nMByGGnVybjp1dWlkOmludGVybWVkaWF0ZTJfY2E0MB0GA1UdDgQWBBQMbH6cLs8O\nw5LDhNjyaMlwPaBtETAfBgNVHSMEGDAWgBSZL14LLuO0TDeId0a57ioIMA0ShDAN\nBgkqhkiG9w0BAQsFAAOCAQEATv0PsTzN3a2FAo9aamIKXssMow4kdaVGvzoYRvZ7\nhhGy54fVKTqK/YJeiQNvClJq3B12H13yuUxU+NRtTv6h/m9oUwBOgugqy6haRTTo\nGuDdCcxlx+y5xJtW1OjCjP/5o08NL8EpEUHG8kt1Sm8kz3EDKh5mcT+qzh9Tyt8B\n6wjk3qIUH0j7Aqmx9lymgGsoK4PWg8qj21BLCiPS+8iAixztympBm2eEQOwHhKkJ\ncaiATd00j7TfQDW5Un0ZPweZteQVYNKcuaVngJ11mrGM5+7g8JQ5CPWu4xAC1c8z\naZArVG5cjXicnQ0aKbFISutKfEcQkxXrf+O9tyNFxWqObg==\n-----END CERTIFICATE-----\n"
    ],
    "clearancePeriod": 30
}
'
