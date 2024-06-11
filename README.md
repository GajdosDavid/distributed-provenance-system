# Distributed provenance system

This is an implementation of integrity and non-repudiation into a system of distributed provenance. The full text of the thesis to which this implementation belongs it available at https://is.muni.cz/th/mo8f1/.

This repository consists of two web applications -- **Trusted party** and **Provenance storage**.

## How to run the applications seprately

In directories **./trusted\_party** and **./distributed\_prov\_system** there are scripts **manage.py**. For local
testing and development purposes this script can run a webserver by running `python manage.py runserver 127.0.0.1 8000`. 
This runs the service on localhost accessible under a TCP port 8000.

Both of the applications can be run this way, however mind that a working connection to a database 
(Postgres for trusted party and Neo4J for the distributed provenance storage) is required which is set in **settings.py** of individual applications.

Note that the `runserver` command should not be used in production. For more information about
deploying an application into production see [How to deploy Django](https://docs.djangoproject.com/en/5.0/howto/deployment/).

# How to run and test deployment

First start by running a trusted party and then run a provenance storage applicaiton.

Clone the github repository either via https or ssh.
```bash
https: git clone https://github.com/GajdosDavid/distributed-provenance-system.git
ssh: git clone git@github.com:GajdosDavid/distributed-provenance-system.git
```

## Trusted party

First start by pulling a docker image for trusted party with postgres preinstalled (also available [here](https://hub.docker.com/repository/docker/davidsdockershed/trusted_party/general))
```bash
docker pull davidsdockershed/trusted_party:latest
```

Now run a container from the pulled image.
```bash
docker run \
      -v <full_path_to_cloned_repo>/trusted_party/:/wa \
      -v <full_path_to_cloned_repo>/test_deployment/trusted_party/config/:/opt/config \
      -e APP_CONFIG_PATH=/opt/config/config.json \
      -d \
      --name example_tp davidsdockershed/trusted_party
```

This effectively maps the `./test_deployment/trusted_party/config/` directory to the `/opt/config/` directory inside the container.
For this test deployment this is okay, however in real deployment you might not want to do this and would rather modify the files
directly inside the container (there's already a directory structure prepared in the docker image under `/opt/config/`, the command above
just remaps it to something else). If you want to specify different certificates and key, run the above command without `       -v <full_path_to_cloned_repo>/test_deployment/trusted_party/config/:/opt/config`.

Execute into the container by running
```bash
docker exec -it example_tp /bin/bash
```

Inside of the container run
```bash
cd /wa/
# if running this for the first time, you need to run migrations
python3 manage.py migrate 
python3 manage.py runserver 0.0.0.0:7000
```
This runs the trusted party service. It must be running before provenance storage application runs.

## Provenance storage
Pull the docker image for provenance storage with neo4j and necessary python packages preinstalled 
(also available [here](https://hub.docker.com/repository/docker/davidsdockershed/prov_storage/general)).
```bash
docker pull davidsdockershed/prov_storage:latest
```

Now run a container from the pulled image.
```bash
docker run \
      -d \
      -e APP_CONFIG_PATH=/opt/config/config.json  \
      -v <full_path_to_cloned_repo>/distributed_prov_system/:/wa \
      --name example_storage davidsdockershed/prov_storage
```

To find out the IP address of the **provenance storage container** run (on the host)
```bash
STORAGE_IP=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' example_storage)
```

To find out the IP address of the **trused party** run (on the host)
```bash
TP_IP=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' example_tp)
```

Now exec to the container by running 
```bash
docker exec -it example_storage /bin/bash
```
and modify `/opt/config/config.json`. Below is what the JSON looks like. 
```json
{
  "id": "WHATEVER_ID_YOU_WANT",
  "fqdn": "http://${STORAGE_IP}:8000",
  "trustedPartyFqdn": "http://${TP_IP}:7000",
  "disableTrustedParty": false
}
```
Modify manually the missing values for `id`, `fqdn` and `trustedPartyFqdn` (the latter two obtained from the `docker inspect` commands above). If you want to run _provenance storage_ separately without
trusted party, you can do so by specifying `disableTrustedParty: true` (in such a case `trustedPartyFqdn` is ignored).

**In this setup however we're deploying with TP.**

Then **inside** the container exec
```bash
cd /wa
python3 manage.py runserver 0.0.0.0:8000
```

To test that the storage works as expected run a script `./test_deployment/store_document.sh`
The script should print the obtained non-repudiation token
```json
{
  "token": {
    "data": {
      "originatorId": "ORG",
      "authorityId": "ExampleTrustedParty",
      "tokenTimestamp": 1718086640,
      "documentCreationTimestamp": 123,
      "documentDigest": "e50678578364ff83e504ef3858d8151fc523fda0ac37ca575ad0a03b026ff364",
      "additionalData": {
        "bundle": "http://<YOUR_STORAGE_CONTAINER_IP>:8000/api/v1/organizations/ORG/documents/01_sample_acquisition",
        "hashFunction": "SHA256",
        "trustedPartyUri": "http://example-trusted-party.com",
        "trustedPartyCertificate": "-----BEGIN CERTIFICATE-----\nMIIDJjCCAg6gAwIBAgIBCDANBgkqhkiG9w0BAQsFADAmMQswCQYDVQQGEwJFVTEX\nMBUGA1UEAwwORVVUcnVzdGVkUGFydHkwHhcNMjQwNDA3MTY1NTUxWhcNMzQwMjE3\nMTY1NTUxWjAmMQswCQYDVQQGEwJFVTEXMBUGA1UEAwwORVVUcnVzdGVkUGFydHkw\nggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDOhLzSAM8gZWYFmaGHJ1gj\nhBuygzk+os74niZtDANemz6qGitKUkQMjGQwNH/E9oFVYv+9nhhjQmEfQxKWVBWH\nv12Y2kr3KQ0YdkDiV3mufmo+ONBeVtv+voxDf9P4ttDHp3cBcOkyrbAw26hw+vh5\nFW5fAiqebZKhhnJQjir4RY2I74IpdyBW3dJrYpBX8wSEMYgOg/SS4aJGAlsxxY3i\nEKiCEyKlLluXOdXMv6GT8UoQH/hJUmq10eGTUxVvw9A8yOrvuAy61EfM427wdLX5\nBXKqR/Ee4rCDPIrfvlopT0L1IXgiYSbsAPVSVCpsbOhQ0v56vAmshPxMxqMQEaFR\nAgMBAAGjXzBdMA8GA1UdEwEB/wQFMAMBAf8wDgYDVR0PAQH/BAQDAgIEMBsGA1Ud\nEQEB/wQRMA+GDXVybjp1dWlkOkVVVFAwHQYDVR0OBBYEFG6rvQKRA0i0o+gEPotz\nvNZXPkV6MA0GCSqGSIb3DQEBCwUAA4IBAQBioVUi0dt+ylQUDdo9tUEQahCzuUne\n3eLtZJEtlnl02mi2vTGMup6ra5n3+XFXKv5rjIAOHw2p29j2kO/FMXUqBFc8gSrH\nUKScpjNdVPIZ94h7jjLcSXiKg1mdwMpVnJf6u6OmNg4Ehbr7uD590LIvxIXVQcJr\ndRdlRM7zhqqpyLqAUJBz1U0Zbjuo3XakhYxpC5KDEAXxisB0sWOsTys2k7o6XdZx\nAPIZso0yuDZpK0p2yZQuAbQQ50TstMhyEYreaksirjmytxkRMZVhK7jADWqe0Qgq\nfReSYYrlGH/58qjkC9gGeNgdkWYIvJbVcTSlyszJawmBnzw/C18DoDB7\n-----END CERTIFICATE-----\n"
      }
    },
    "signature": "FY0RsVL5pEdiQ06OT3u69qYDRddv8x0ZKcdTthQIGB3ri230ddUdoJ0s7yL5lTLWmPHD8J3zIQfGnzsOSVX45iM2GWWyNxYdO7MkjHT6LHC8zDPTF1n7xzdVltTg8+CATbk5JK1ryJBurxe9QNj3LbkMfRtV4Wwf6b9F5cm+i4WNFvPNNId0vgVwDFTPgwenQ57o3NiJohzqwQSP3EbpSLDkL0DG0JfAFgLZB2NN5n8RS1bcXyX4Kya7qRUDzCA8Ix8w4K/rBpiBIImMMMqZzScY+9U2Ne61UCHote0RAT+ZlPVxKbKeoSNIn3bo7C80FGNzUTAYzkHlJlstSZ1u2g=="
  }
}
```

To retrieve the graph run a script `./test_deployment/retrieve_document.sh`. The script should output the following json.
```json
{
  "document": "ewogICJwcmVmaXgiIDogewogICAgInhzZCIgOiAiaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEjIiwKICAgICJwcm92IiA6ICJodHRwOi8vd3d3LnczLm9yZy9ucy9wcm92IyIsCiAgICAibnNfc3VyZ2VyeSIgOiAiaHR0cDovLzE3Mi4xNy4wLjQ6ODAwMC9hcGkvdjEvb3JnYW5pemF0aW9ucy9PUkcvZG9jdW1lbnRzLyIKICB9LAogICJidW5kbGUiIDogewogICAgIm5zX3N1cmdlcnk6MDFfc2FtcGxlX2FjcXVpc2l0aW9uIiA6IHsKICAgICAgInByZWZpeCIgOiB7CiAgICAgICAgImNwbSIgOiAiaHR0cHM6Ly93d3cuY29tbW9ucHJvdmVuYW5jZW1vZGVsLm9yZy9jcG0tbmFtZXNwYWNlLXYxLTAvIiwKICAgICAgICAiZGN0IiA6ICJodHRwOi8vcHVybC5vcmcvZGMvdGVybXMvIiwKICAgICAgICAic2VsZl9jb25uZWN0b3IiIDogImh0dHA6Ly8xNzIuMTcuMC40OjgwMDAvYXBpL3YxL2Nvbm5lY3RvcnMvIiwKICAgICAgICAibWV0YSIgOiAiaHR0cDovLzE3Mi4xNy4wLjQ6ODAwMC9hcGkvdjEvZG9jdW1lbnRzL21ldGEvIiwKICAgICAgICAieHNkIiA6ICJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYSMiLAogICAgICAgICJwcm92IiA6ICJodHRwOi8vd3d3LnczLm9yZy9ucy9wcm92IyIsCiAgICAgICAgIm5zX3N1cmdlcnkiIDogImh0dHA6Ly8xNzIuMTcuMC40OjgwMDAvYXBpL3YxL29yZ2FuaXphdGlvbnMvT1JHL2RvY3VtZW50cy8iCiAgICAgIH0sCiAgICAgICJlbnRpdHkiIDogewogICAgICAgICJuc19zdXJnZXJ5OnBhdGllbnQiIDogewogICAgICAgICAgIm5zX3N1cmdlcnk6YmlvcHRpYy1hcHAtaWQiIDogWyAiYXBwLWlkLTAiIF0sCiAgICAgICAgICAiY3BtOmV4dGVybmFsSWQiIDogWyAicGF0aWVudC1pZC0wIiBdCiAgICAgICAgfSwKICAgICAgICAic2VsZl9jb25uZWN0b3I6c2FtcGxlQ29ubmVjdG9yIiA6IHsKICAgICAgICAgICJjcG06cmVjZWl2ZXJTZXJ2aWNlVXJpIiA6IFsgIiNVUkkjIiBdLAogICAgICAgICAgInByb3Y6dHlwZSIgOiBbIHsKICAgICAgICAgICAgInR5cGUiIDogInByb3Y6UVVBTElGSUVEX05BTUUiLAogICAgICAgICAgICAiJCIgOiAiY3BtOmZvcndhcmRDb25uZWN0b3IiCiAgICAgICAgICB9IF0KICAgICAgICB9LAogICAgICAgICJuc19zdXJnZXJ5OlNhbXBsZSIgOiB7CiAgICAgICAgICAiY3BtOmV4dGVybmFsSWQiIDogWyAidGlzc3VlLWlkLTAiIF0KICAgICAgICB9LAogICAgICAgICJuc19zdXJnZXJ5OnRpc3N1ZVNhbXBsZSIgOiB7CiAgICAgICAgICAiY3BtOmV4dGVybmFsSWQiIDogWyAic2FtcGxlLWlkLTAiIF0KICAgICAgICB9LAogICAgICAgICJuc19zdXJnZXJ5OnByZXBhcmVkU2FtcGxlIiA6IHsKICAgICAgICAgICJjcG06ZXh0ZXJuYWxJZCIgOiBbICJzYW1wbGUtaWQtMCIgXQogICAgICAgIH0KICAgICAgfSwKICAgICAgImFjdGl2aXR5IiA6IHsKICAgICAgICAibnNfc3VyZ2VyeTpzYW1wbGVQcmVwYXJhdGlvbiIgOiB7IH0sCiAgICAgICAgIm5zX3N1cmdlcnk6c2FtcGxlVHJhbnNwb3J0IiA6IHsgfSwKICAgICAgICAibnNfc3VyZ2VyeTpiaW9tYXRlcmlhbENvbGxlY3Rpb24iIDogeyB9LAogICAgICAgICJuc19zdXJnZXJ5OnNhbXBsZUFjcXVpc2l0aW9uIiA6IHsKICAgICAgICAgICJjcG06bWV0YWJ1bmRsZSIgOiBbIHsKICAgICAgICAgICAgInR5cGUiIDogInByb3Y6UVVBTElGSUVEX05BTUUiLAogICAgICAgICAgICAiJCIgOiAibWV0YTptZXRhMSIKICAgICAgICAgIH0gXSwKICAgICAgICAgICJkY3Q6aGFzUGFydCIgOiBbIHsKICAgICAgICAgICAgInR5cGUiIDogInByb3Y6UVVBTElGSUVEX05BTUUiLAogICAgICAgICAgICAiJCIgOiAibnNfc3VyZ2VyeTpzYW1wbGVUcmFuc3BvcnQiCiAgICAgICAgICB9LCB7CiAgICAgICAgICAgICJ0eXBlIiA6ICJwcm92OlFVQUxJRklFRF9OQU1FIiwKICAgICAgICAgICAgIiQiIDogIm5zX3N1cmdlcnk6YmlvbWF0ZXJpYWxDb2xsZWN0aW9uIgogICAgICAgICAgfSwgewogICAgICAgICAgICAidHlwZSIgOiAicHJvdjpRVUFMSUZJRURfTkFNRSIsCiAgICAgICAgICAgICIkIiA6ICJuc19zdXJnZXJ5OnNhbXBsZVByZXBhcmF0aW9uIgogICAgICAgICAgfSBdLAogICAgICAgICAgInByb3Y6dHlwZSIgOiBbIHsKICAgICAgICAgICAgInR5cGUiIDogInByb3Y6UVVBTElGSUVEX05BTUUiLAogICAgICAgICAgICAiJCIgOiAiY3BtOm1haW5BY3Rpdml0eSIKICAgICAgICAgIH0sIHsKICAgICAgICAgICAgInR5cGUiIDogInByb3Y6UVVBTElGSUVEX05BTUUiLAogICAgICAgICAgICAiJCIgOiAiY3BtOnNhbXBsZUFjcXVpc2l0aW9uIgogICAgICAgICAgfSwgewogICAgICAgICAgICAidHlwZSIgOiAicHJvdjpRVUFMSUZJRURfTkFNRSIsCiAgICAgICAgICAgICIkIiA6ICJjcG06c2FtcGxlSGFuZGxpbmciCiAgICAgICAgICB9IF0KICAgICAgICB9CiAgICAgIH0sCiAgICAgICJhZ2VudCIgOiB7CiAgICAgICAgIm5zX3N1cmdlcnk6cGF0aG9sb2d5RGVwYXJ0bWVudCIgOiB7CiAgICAgICAgICAiY3BtOmNvbnRhY3RJZFBpZCIgOiBbICIiIF0sCiAgICAgICAgICAicHJvdjp0eXBlIiA6IFsgewogICAgICAgICAgICAidHlwZSIgOiAicHJvdjpRVUFMSUZJRURfTkFNRSIsCiAgICAgICAgICAgICIkIiA6ICJjcG06cmVjZWl2ZXJBZ2VudCIKICAgICAgICAgIH0gXQogICAgICAgIH0sCiAgICAgICAgIm5zX3N1cmdlcnk6c3VyZ2ljYWxEZXBhcnRtZW50IiA6IHsgfQogICAgICB9LAogICAgICAidXNlZCIgOiB7CiAgICAgICAgIl86bjgiIDogewogICAgICAgICAgInByb3Y6YWN0aXZpdHkiIDogIm5zX3N1cmdlcnk6c2FtcGxlUHJlcGFyYXRpb24iLAogICAgICAgICAgInByb3Y6ZW50aXR5IiA6ICJuc19zdXJnZXJ5OnRpc3N1ZVNhbXBsZSIKICAgICAgICB9LAogICAgICAgICJfOm41IiA6IHsKICAgICAgICAgICJwcm92OmFjdGl2aXR5IiA6ICJuc19zdXJnZXJ5OmJpb21hdGVyaWFsQ29sbGVjdGlvbiIsCiAgICAgICAgICAicHJvdjplbnRpdHkiIDogIm5zX3N1cmdlcnk6cGF0aWVudCIKICAgICAgICB9LAogICAgICAgICJfOm4xMiIgOiB7CiAgICAgICAgICAicHJvdjphY3Rpdml0eSIgOiAibnNfc3VyZ2VyeTpzYW1wbGVUcmFuc3BvcnQiLAogICAgICAgICAgInByb3Y6ZW50aXR5IiA6ICJuc19zdXJnZXJ5OnByZXBhcmVkU2FtcGxlIgogICAgICAgIH0KICAgICAgfSwKICAgICAgIndhc0Fzc29jaWF0ZWRXaXRoIiA6IHsKICAgICAgICAiXzpuMiIgOiB7CiAgICAgICAgICAicHJvdjphY3Rpdml0eSIgOiAibnNfc3VyZ2VyeTpiaW9tYXRlcmlhbENvbGxlY3Rpb24iLAogICAgICAgICAgInByb3Y6YWdlbnQiIDogIm5zX3N1cmdlcnk6c3VyZ2ljYWxEZXBhcnRtZW50IgogICAgICAgIH0sCiAgICAgICAgIl86bjMiIDogewogICAgICAgICAgInByb3Y6YWN0aXZpdHkiIDogIm5zX3N1cmdlcnk6c2FtcGxlUHJlcGFyYXRpb24iLAogICAgICAgICAgInByb3Y6YWdlbnQiIDogIm5zX3N1cmdlcnk6c3VyZ2ljYWxEZXBhcnRtZW50IgogICAgICAgIH0sCiAgICAgICAgIl86bjQiIDogewogICAgICAgICAgInByb3Y6YWN0aXZpdHkiIDogIm5zX3N1cmdlcnk6c2FtcGxlVHJhbnNwb3J0IiwKICAgICAgICAgICJwcm92OmFnZW50IiA6ICJuc19zdXJnZXJ5OnN1cmdpY2FsRGVwYXJ0bWVudCIKICAgICAgICB9CiAgICAgIH0sCiAgICAgICJ3YXNBdHRyaWJ1dGVkVG8iIDogewogICAgICAgICJfOm4xIiA6IHsKICAgICAgICAgICJwcm92OmVudGl0eSIgOiAic2VsZl9jb25uZWN0b3I6c2FtcGxlQ29ubmVjdG9yIiwKICAgICAgICAgICJwcm92OmFnZW50IiA6ICJuc19zdXJnZXJ5OnBhdGhvbG9neURlcGFydG1lbnQiCiAgICAgICAgfQogICAgICB9LAogICAgICAic3BlY2lhbGl6YXRpb25PZiIgOiB7CiAgICAgICAgIl86bjExIiA6IHsKICAgICAgICAgICJwcm92OnNwZWNpZmljRW50aXR5IiA6ICJuc19zdXJnZXJ5OlNhbXBsZSIsCiAgICAgICAgICAicHJvdjpnZW5lcmFsRW50aXR5IiA6ICJzZWxmX2Nvbm5lY3RvcjpzYW1wbGVDb25uZWN0b3IiCiAgICAgICAgfQogICAgICB9LAogICAgICAid2FzRGVyaXZlZEZyb20iIDogewogICAgICAgICJfOm4xNCIgOiB7CiAgICAgICAgICAicHJvdjpnZW5lcmF0ZWRFbnRpdHkiIDogIm5zX3N1cmdlcnk6U2FtcGxlIiwKICAgICAgICAgICJwcm92OnVzZWRFbnRpdHkiIDogIm5zX3N1cmdlcnk6cHJlcGFyZWRTYW1wbGUiCiAgICAgICAgfSwKICAgICAgICAiXzpuMTAiIDogewogICAgICAgICAgInByb3Y6Z2VuZXJhdGVkRW50aXR5IiA6ICJuc19zdXJnZXJ5OnByZXBhcmVkU2FtcGxlIiwKICAgICAgICAgICJwcm92OnVzZWRFbnRpdHkiIDogIm5zX3N1cmdlcnk6dGlzc3VlU2FtcGxlIgogICAgICAgIH0sCiAgICAgICAgIl86bjciIDogewogICAgICAgICAgInByb3Y6Z2VuZXJhdGVkRW50aXR5IiA6ICJuc19zdXJnZXJ5OnRpc3N1ZVNhbXBsZSIsCiAgICAgICAgICAicHJvdjp1c2VkRW50aXR5IiA6ICJuc19zdXJnZXJ5OnBhdGllbnQiCiAgICAgICAgfQogICAgICB9LAogICAgICAid2FzR2VuZXJhdGVkQnkiIDogewogICAgICAgICJfOm4xMyIgOiB7CiAgICAgICAgICAicHJvdjplbnRpdHkiIDogIm5zX3N1cmdlcnk6U2FtcGxlIiwKICAgICAgICAgICJwcm92OmFjdGl2aXR5IiA6ICJuc19zdXJnZXJ5OnNhbXBsZVRyYW5zcG9ydCIKICAgICAgICB9LAogICAgICAgICJfOm42IiA6IHsKICAgICAgICAgICJwcm92OmVudGl0eSIgOiAibnNfc3VyZ2VyeTp0aXNzdWVTYW1wbGUiLAogICAgICAgICAgInByb3Y6YWN0aXZpdHkiIDogIm5zX3N1cmdlcnk6YmlvbWF0ZXJpYWxDb2xsZWN0aW9uIgogICAgICAgIH0sCiAgICAgICAgIl86bjkiIDogewogICAgICAgICAgInByb3Y6ZW50aXR5IiA6ICJuc19zdXJnZXJ5OnByZXBhcmVkU2FtcGxlIiwKICAgICAgICAgICJwcm92OmFjdGl2aXR5IiA6ICJuc19zdXJnZXJ5OnNhbXBsZVByZXBhcmF0aW9uIgogICAgICAgIH0sCiAgICAgICAgIl86bjAiIDogewogICAgICAgICAgInByb3Y6ZW50aXR5IiA6ICJzZWxmX2Nvbm5lY3RvcjpzYW1wbGVDb25uZWN0b3IiLAogICAgICAgICAgInByb3Y6YWN0aXZpdHkiIDogIm5zX3N1cmdlcnk6c2FtcGxlQWNxdWlzaXRpb24iCiAgICAgICAgfQogICAgICB9CiAgICB9CiAgfQp9",
  "token": {
    "data": {
      "originatorId": "ORG",
      "authorityId": "ExampleTrustedParty",
      "tokenTimestamp": 1718086640,
      "documentCreationTimestamp": 123,
      "documentDigest": "e50678578364ff83e504ef3858d8151fc523fda0ac37ca575ad0a03b026ff364",
      "additionalData": {
        "bundle": "http://<YOUR_STORAGE_CONTAINER_IP>:8000/api/v1/organizations/ORG/documents/01_sample_acquisition",
        "hashFunction": "SHA256",
        "trustedPartyUri": "http://example-trusted-party.com",
        "trustedPartyCertificate": "-----BEGIN CERTIFICATE-----\nMIIDJjCCAg6gAwIBAgIBCDANBgkqhkiG9w0BAQsFADAmMQswCQYDVQQGEwJFVTEX\nMBUGA1UEAwwORVVUcnVzdGVkUGFydHkwHhcNMjQwNDA3MTY1NTUxWhcNMzQwMjE3\nMTY1NTUxWjAmMQswCQYDVQQGEwJFVTEXMBUGA1UEAwwORVVUcnVzdGVkUGFydHkw\nggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDOhLzSAM8gZWYFmaGHJ1gj\nhBuygzk+os74niZtDANemz6qGitKUkQMjGQwNH/E9oFVYv+9nhhjQmEfQxKWVBWH\nv12Y2kr3KQ0YdkDiV3mufmo+ONBeVtv+voxDf9P4ttDHp3cBcOkyrbAw26hw+vh5\nFW5fAiqebZKhhnJQjir4RY2I74IpdyBW3dJrYpBX8wSEMYgOg/SS4aJGAlsxxY3i\nEKiCEyKlLluXOdXMv6GT8UoQH/hJUmq10eGTUxVvw9A8yOrvuAy61EfM427wdLX5\nBXKqR/Ee4rCDPIrfvlopT0L1IXgiYSbsAPVSVCpsbOhQ0v56vAmshPxMxqMQEaFR\nAgMBAAGjXzBdMA8GA1UdEwEB/wQFMAMBAf8wDgYDVR0PAQH/BAQDAgIEMBsGA1Ud\nEQEB/wQRMA+GDXVybjp1dWlkOkVVVFAwHQYDVR0OBBYEFG6rvQKRA0i0o+gEPotz\nvNZXPkV6MA0GCSqGSIb3DQEBCwUAA4IBAQBioVUi0dt+ylQUDdo9tUEQahCzuUne\n3eLtZJEtlnl02mi2vTGMup6ra5n3+XFXKv5rjIAOHw2p29j2kO/FMXUqBFc8gSrH\nUKScpjNdVPIZ94h7jjLcSXiKg1mdwMpVnJf6u6OmNg4Ehbr7uD590LIvxIXVQcJr\ndRdlRM7zhqqpyLqAUJBz1U0Zbjuo3XakhYxpC5KDEAXxisB0sWOsTys2k7o6XdZx\nAPIZso0yuDZpK0p2yZQuAbQQ50TstMhyEYreaksirjmytxkRMZVhK7jADWqe0Qgq\nfReSYYrlGH/58qjkC9gGeNgdkWYIvJbVcTSlyszJawmBnzw/C18DoDB7\n-----END CERTIFICATE-----\n"
      }
    },
    "signature": "FY0RsVL5pEdiQ06OT3u69qYDRddv8x0ZKcdTthQIGB3ri230ddUdoJ0s7yL5lTLWmPHD8J3zIQfGnzsOSVX45iM2GWWyNxYdO7MkjHT6LHC8zDPTF1n7xzdVltTg8+CATbk5JK1ryJBurxe9QNj3LbkMfRtV4Wwf6b9F5cm+i4WNFvPNNId0vgVwDFTPgwenQ57o3NiJohzqwQSP3EbpSLDkL0DG0JfAFgLZB2NN5n8RS1bcXyX4Kya7qRUDzCA8Ix8w4K/rBpiBIImMMMqZzScY+9U2Ne61UCHote0RAT+ZlPVxKbKeoSNIn3bo7C80FGNzUTAYzkHlJlstSZ1u2g=="
  }
}
```

## Demo simulation

As part of the thesis a demo simulation was performed which is described and accessible under link https://is.muni.cz/th/mo8f1/ (Section 4.5 in the text).
As part of the thesis an archive with curls and used PROV documents was published which is also part of this repository as well (under `./test_deployment/simulation/`). 
These curls and documents can be used for testing of the deployment or as an inspiration for what the PROV documents should look like. These curls can also
be imported to **Postman** application which might be more convenient to work with.

When working with the curls, please keep in mind that you might need to change a few things (such as the URLs of the running storages
 and URLs inside of the documents).

The expected order in which the documents should be stored is the following:
```
uni_graz -> uni_paris -> muni -> cvut -> uni_warsaw -> uni_munich
```

After the storage you might retrieve connector tables, generated meta-provenance documents etc.

## OpenAPI speicfications

The OpenAPI specifications for the applications can be found under following links -- [provenance storage](https://app.swaggerhub.com/apis/DAVIDGAJDOS/provenance_storage/1.0.0)
and [trusted party](https://app.swaggerhub.com/apis/DAVIDGAJDOS/trusted_party/1.0.0).