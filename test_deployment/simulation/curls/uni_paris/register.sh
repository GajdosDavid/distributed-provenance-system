curl --location 'http://provenance-storage-provider.com:8000/api/v1/organizations/UniParis' \
--header 'Content-Type: application/json' \
--data '{
    "clientCertificate": "-----BEGIN CERTIFICATE-----\nMIIDQzCCAiugAwIBAgIBBDANBgkqhkiG9w0BAQsFADApMQswCQYDVQQGEwJBVDEa\nMBgGA1UEAwwRaW50ZXJtZWRpYXRlMV9jYTEwHhcNMjQwNDA3MTYxODE2WhcNMzQw\nMjE0MTYxODE2WjA7MQswCQYDVQQGEwJGUjEcMBoGA1UECgwTVW5pdmVyc2l0eSBv\nZiBQYXJpczEOMAwGA1UEAwwFUGFyaXMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAw\nggEKAoIBAQCoaIM6YWxXE9yNh2KX44GvWhJ3yP9J2GD31k6u2HBh8E4nxr2MKhll\nMXSQfck7BB3vxYqLMOjchqazyCEzAlC0P4K2xRfbjb4qIp8Xq5sxIgjp9qX0S0Xy\nOjXFtREQzdr9Os+Npo6thsgf9867MSJ8putKLik0xzex76IPi+EvdDvcwocza/7g\nizTS7yhr5fGM0agWHc6Tr4x6Yu/bv3PjJmVgEBAoSLMIji6qx4Ey7HC9xkki5OLy\nIq+TG36csvtf2gcvGSEzArk9ZT6mxA5qUw1s9sSMp4h7nD3p+JIsMtkDY5TEvUvQ\nR0tr6c3O/VBIdnJ8Jw80AmmWuT0HbKFLAgMBAAGjZDBiMCAGA1UdEQEB/wQWMBSG\nEnVybjp1dWlkOnVuaS1wYXJpczAdBgNVHQ4EFgQUZthGS6oGYlFmnX3zs9DAbEVa\n0zowHwYDVR0jBBgwFoAU5tlKE278cb1vJtj1UOkBxeg+MjswDQYJKoZIhvcNAQEL\nBQADggEBAKtkYjINIaRUv4uDS2+5p/Y9Lk9X+RvS3Udtch82rMXrN6QJodcRCjcS\noVLCbvf18yZjGMh5lcuxSFiVtUDNVqFRN0Irk39jNbnU1adztRVUIT4nrftSqkMV\nkDQfuqhfdyLbJV2kRSHoDXw9hRSKtl2TXpSzOW1HsHJwFqHqRW9Mjl/CuhtEXYZX\nD14RFHs98GpNiCGzv+0vgkKX8LaqYPl0vHv+za7lqw3AVZzIEhKP2aJe4KSzgu7/\nWlKUYvJP9GveivmUu8Qs9eSmd6jr+kX2ZonIY+okoxOOpQ4VfFW8C78mD1Yli+Eo\ney0VLRHPqpQDc6LZTIuVbcF66YfBe1E=\n-----END CERTIFICATE-----\n",
    "intermediateCertificates": [
        "-----BEGIN CERTIFICATE-----\nMIIDXDCCAkSgAwIBAgIBAjANBgkqhkiG9w0BAQsFADApMQswCQYDVQQGEwJBVDEa\nMBgGA1UEAwwRaW50ZXJtZWRpYXRlMl9jYTEwHhcNMjQwNDA3MTYxODEzWhcNMzQw\nMjE1MTYxODEzWjApMQswCQYDVQQGEwJBVDEaMBgGA1UEAwwRaW50ZXJtZWRpYXRl\nMV9jYTEwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQD1oLOZP9Of8wRt\nKsQtttnuoDlDklU8gPTwIZG1oFzUzNW/HNrOxR2mD6o6uQj37vBIUsV+nUxjbr5m\nS5+L8yu9jAJaRQrVf5prSsBjeoVLbbF3RZ4U9thfj5O1vsoaXqB9Cumejdq509Wv\n9wQ0aKHZ+dQhNqnf1zBH60FkuitpKNEI9srAzPjaY/d2mPdtYMWGYGUbDTNG/vx5\nVT3je6L/bwmqMCmxKXvYE9ddxYqinVqOi7T76bawteQFUMB4ucK8WlTVr37aAlzI\nxWVh3Zulu+QpgJrXgFdDms+f6o4f7c6hC8m9vjQC4sG+afgPchSQlLEc5weocozc\nMnlylSt7AgMBAAGjgY4wgYswDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC\nAgQwKAYDVR0RAQH/BB4wHIYadXJuOnV1aWQ6aW50ZXJtZWRpYXRlMV9jYTEwHQYD\nVR0OBBYEFObZShNu/HG9bybY9VDpAcXoPjI7MB8GA1UdIwQYMBaAFK06Adi07LrA\nn3tFsSy5F/0hOkzQMA0GCSqGSIb3DQEBCwUAA4IBAQAK5R8/zSMXM+GuETh7H9HR\nfcbBLxqBaBbgsZes8xnVgYQCegPJEW6YKlzxhrXPwzbmeJlpKR2Fhy3LqASYMVGy\nzzjsdRNyM0mmmhGk9pNB9YYkJBKZEHWdQADutsDmXwDrcozkDsmQA0nKqzViB376\n8WltWX2/nMQ+N2/a/1DXNncUYKTi3pk4UOjsfmpkaJvfYg1Pf1duKykURr+wIiHb\naFSWJf5zBqr2kcLQN576aNfjfl3nU5JQEUL3RjAF4ZdspVBiY6BGFLcsm3CdN85K\nHKjJkKzJB+DZledvp28u4LXlQb2CevWlWOwgC3p2rUw8q1PIa36hysvNcBczUBE+\n-----END CERTIFICATE-----\n",
        "-----BEGIN CERTIFICATE-----\nMIIDTjCCAjagAwIBAgIBBTANBgkqhkiG9w0BAQsFADAbMQswCQYDVQQGEwJBVDEM\nMAoGA1UEAwwDQ0ExMB4XDTI0MDQwNzE2MTgxMloXDTM0MDIxNjE2MTgxMlowKTEL\nMAkGA1UEBhMCQVQxGjAYBgNVBAMMEWludGVybWVkaWF0ZTJfY2ExMIIBIjANBgkq\nhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxSqsPxdaXjoJ0IvqbMTxKzSQsSTUihm5\nVTXOUteqaQeGQw9Nu/P1REzMXHYBkvDgjbYzX4rmoAHNcdNXFhq+RnTwpi5WIkdz\nvlRwjoc2D7Q86jXGRf6dRYp+sY5t36ugZ86ZWJ/03tkY8YhqUP0U8t2rhDxpSAyQ\nsOHr9maS0IuemAA1lT2RSlieZr2UCAOwRDXNu6F7MM7pJ5JeGpVsq590dpS+MzDu\nT58KkpYvJO8ezYMmWrbnM0QHf8uIV3upi3+ZkaNHibJk/KUvmHbrGyjKx/at0ji5\nVrseSUV+ggTRPlkWPAWiNM1Eqa484UtFn31hmTZdgF0eAZVtb40aoQIDAQABo4GO\nMIGLMA8GA1UdEwEB/wQFMAMBAf8wDgYDVR0PAQH/BAQDAgIEMCgGA1UdEQEB/wQe\nMByGGnVybjp1dWlkOmludGVybWVkaWF0ZTJfY2ExMB0GA1UdDgQWBBStOgHYtOy6\nwJ97RbEsuRf9ITpM0DAfBgNVHSMEGDAWgBREUHL0Jt3LAhvSaVfPB4cboLGKPDAN\nBgkqhkiG9w0BAQsFAAOCAQEA0Cj3D60orbI5zG2A/eGX3pY7eZsa5zD+i2YBK81P\nD0vC3/b4ouan4uBB1196tVo1vJ8P/MPmd9jrf/Bs+zTNjajX92ROifYAKUpKxred\nxHWVgyqXX1IkCLKbQpPi/Fgbx5N2gPT50ID52HQz1ezwxA9TYvMxraXTWoEkVLe8\ncLnk9GYPK8gl+3uo8OM2N4NpJXquEtdOWjYMswR1quosChlXwnYJbAunkUOFchrz\nQd17CBaP2k9J1GcZ8mUIHHbDSJogkDMWUNNPTyuwSk7NaXj3rL4j4eKFXxoVb/cm\nTHoFp5u/KVlbKZrXUgXD0MS5OlJ5/QA3EqnAstW1As1yOg==\n-----END CERTIFICATE-----\n"
    ],
    "clearancePeriod": 30
}'