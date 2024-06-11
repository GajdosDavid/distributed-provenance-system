curl --location 'http://provenance-storage-provider.com:8000/api/v1/organizations/UniGraz' \
--header 'Content-Type: application/json' \
--data '{
    "clientCertificate": "-----BEGIN CERTIFICATE-----\nMIIDQDCCAiigAwIBAgIBAzANBgkqhkiG9w0BAQsFADApMQswCQYDVQQGEwJBVDEa\nMBgGA1UEAwwRaW50ZXJtZWRpYXRlMV9jYTEwHhcNMjQwNDA3MTYxODE1WhcNMzQw\nMjE0MTYxODE1WjA5MQswCQYDVQQGEwJBVDEbMBkGA1UECgwSVW5pdmVyc2l0eSBv\nZiBHcmF6MQ0wCwYDVQQDDARHcmF6MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB\nCgKCAQEAnN4//wTx3r3HFEHHCCzJKX533w1JR4QExi2BuWCMwZXcklEh9UsSIbGj\n9dfD5wW+4ZGN3463HNvuVT4jV1ZUzf0mWE0Vht7lq9qbSZ77LLvrPfm1ODbdVUfO\nURX2OSItsZ5Z5Qkv1U6SrJh9nENCn+WHTJuJaicKyiU0oVDdVjEAT5PjY2etjDo7\nNGBm3I8OM8IcFQbBWLWpBejeTUqZ3sgiMe9jeY9LdU1XwROC8dMJRYhCaxgroyny\nculH42AihJABVTv/das49dK3vYG3SEkwLZCfgNeJNcfm3vBlztB7TB7XP4ecYASa\niqz2M8BJ90MXBGROhkfOJuFkiEa/FQIDAQABo2MwYTAfBgNVHREBAf8EFTAThhF1\ncm46dXVpZDp1bmktZ3JhejAdBgNVHQ4EFgQUkcq8H1PsH3zIkjHaNYBu66ObOfww\nHwYDVR0jBBgwFoAU5tlKE278cb1vJtj1UOkBxeg+MjswDQYJKoZIhvcNAQELBQAD\nggEBAGa1yDta/UspT9JdGoOg6zD8GYXER+9pVgXgZ6QhJ/PAa8kD8+ko4pRg4+ND\nMGelAF22NF+xnlDu0nHUG+KLfsk98kdjO7DwEZnjhSHtM2dFGGZHktax2yRILgUq\nKphQHNBUWoIBPJJpJUvotEBaWGJVmU/+StfrZSxD/F9REti+hGpEIlJVeCRVrHF+\nN/hky5GZaWtO7XcHY1BC8JNdTJrQR5aZWIWITc5VxH2fNPmlrl0u9kKZXoPBwYQW\nHMVYSNXafhvHRh5dlV2puqnuVeP3WukJ7yiUo/3UhHqDcsVYSjFHSqjdGvrWvkwH\nReQmRYa2LnUH7rCOJqpZmnVVrYA=\n-----END CERTIFICATE-----\n",
    "intermediateCertificates": [
        "-----BEGIN CERTIFICATE-----\nMIIDXDCCAkSgAwIBAgIBAjANBgkqhkiG9w0BAQsFADApMQswCQYDVQQGEwJBVDEa\nMBgGA1UEAwwRaW50ZXJtZWRpYXRlMl9jYTEwHhcNMjQwNDA3MTYxODEzWhcNMzQw\nMjE1MTYxODEzWjApMQswCQYDVQQGEwJBVDEaMBgGA1UEAwwRaW50ZXJtZWRpYXRl\nMV9jYTEwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQD1oLOZP9Of8wRt\nKsQtttnuoDlDklU8gPTwIZG1oFzUzNW/HNrOxR2mD6o6uQj37vBIUsV+nUxjbr5m\nS5+L8yu9jAJaRQrVf5prSsBjeoVLbbF3RZ4U9thfj5O1vsoaXqB9Cumejdq509Wv\n9wQ0aKHZ+dQhNqnf1zBH60FkuitpKNEI9srAzPjaY/d2mPdtYMWGYGUbDTNG/vx5\nVT3je6L/bwmqMCmxKXvYE9ddxYqinVqOi7T76bawteQFUMB4ucK8WlTVr37aAlzI\nxWVh3Zulu+QpgJrXgFdDms+f6o4f7c6hC8m9vjQC4sG+afgPchSQlLEc5weocozc\nMnlylSt7AgMBAAGjgY4wgYswDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC\nAgQwKAYDVR0RAQH/BB4wHIYadXJuOnV1aWQ6aW50ZXJtZWRpYXRlMV9jYTEwHQYD\nVR0OBBYEFObZShNu/HG9bybY9VDpAcXoPjI7MB8GA1UdIwQYMBaAFK06Adi07LrA\nn3tFsSy5F/0hOkzQMA0GCSqGSIb3DQEBCwUAA4IBAQAK5R8/zSMXM+GuETh7H9HR\nfcbBLxqBaBbgsZes8xnVgYQCegPJEW6YKlzxhrXPwzbmeJlpKR2Fhy3LqASYMVGy\nzzjsdRNyM0mmmhGk9pNB9YYkJBKZEHWdQADutsDmXwDrcozkDsmQA0nKqzViB376\n8WltWX2/nMQ+N2/a/1DXNncUYKTi3pk4UOjsfmpkaJvfYg1Pf1duKykURr+wIiHb\naFSWJf5zBqr2kcLQN576aNfjfl3nU5JQEUL3RjAF4ZdspVBiY6BGFLcsm3CdN85K\nHKjJkKzJB+DZledvp28u4LXlQb2CevWlWOwgC3p2rUw8q1PIa36hysvNcBczUBE+\n-----END CERTIFICATE-----\n",
        "-----BEGIN CERTIFICATE-----\nMIIDTjCCAjagAwIBAgIBBTANBgkqhkiG9w0BAQsFADAbMQswCQYDVQQGEwJBVDEM\nMAoGA1UEAwwDQ0ExMB4XDTI0MDQwNzE2MTgxMloXDTM0MDIxNjE2MTgxMlowKTEL\nMAkGA1UEBhMCQVQxGjAYBgNVBAMMEWludGVybWVkaWF0ZTJfY2ExMIIBIjANBgkq\nhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxSqsPxdaXjoJ0IvqbMTxKzSQsSTUihm5\nVTXOUteqaQeGQw9Nu/P1REzMXHYBkvDgjbYzX4rmoAHNcdNXFhq+RnTwpi5WIkdz\nvlRwjoc2D7Q86jXGRf6dRYp+sY5t36ugZ86ZWJ/03tkY8YhqUP0U8t2rhDxpSAyQ\nsOHr9maS0IuemAA1lT2RSlieZr2UCAOwRDXNu6F7MM7pJ5JeGpVsq590dpS+MzDu\nT58KkpYvJO8ezYMmWrbnM0QHf8uIV3upi3+ZkaNHibJk/KUvmHbrGyjKx/at0ji5\nVrseSUV+ggTRPlkWPAWiNM1Eqa484UtFn31hmTZdgF0eAZVtb40aoQIDAQABo4GO\nMIGLMA8GA1UdEwEB/wQFMAMBAf8wDgYDVR0PAQH/BAQDAgIEMCgGA1UdEQEB/wQe\nMByGGnVybjp1dWlkOmludGVybWVkaWF0ZTJfY2ExMB0GA1UdDgQWBBStOgHYtOy6\nwJ97RbEsuRf9ITpM0DAfBgNVHSMEGDAWgBREUHL0Jt3LAhvSaVfPB4cboLGKPDAN\nBgkqhkiG9w0BAQsFAAOCAQEA0Cj3D60orbI5zG2A/eGX3pY7eZsa5zD+i2YBK81P\nD0vC3/b4ouan4uBB1196tVo1vJ8P/MPmd9jrf/Bs+zTNjajX92ROifYAKUpKxred\nxHWVgyqXX1IkCLKbQpPi/Fgbx5N2gPT50ID52HQz1ezwxA9TYvMxraXTWoEkVLe8\ncLnk9GYPK8gl+3uo8OM2N4NpJXquEtdOWjYMswR1quosChlXwnYJbAunkUOFchrz\nQd17CBaP2k9J1GcZ8mUIHHbDSJogkDMWUNNPTyuwSk7NaXj3rL4j4eKFXxoVb/cm\nTHoFp5u/KVlbKZrXUgXD0MS5OlJ5/QA3EqnAstW1As1yOg==\n-----END CERTIFICATE-----\n"
    ],
    "TrustedPartyUri": "http://austria-trusted-party.at:7000",
    "clearancePeriod": 30
}'