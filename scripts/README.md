# Trusted party manual checker

This directory contains a script `TP_manual_checker.py`. When [registering an organizaton](https://app.swaggerhub.com/apis/DAVIDGAJDOS/provenance_storage/1.0.0#/default/post_organizations__org_id_)
via POST request, one may specify a `TrustedPartyUri` in the request. As of now the system is designed in such a way
that this `TrustedPartyUri` chosen by an organization needs to be manually checked to prevent a malicious
organization to specify a URI to only a mocked Trusted party resulting in avoiding storage of certain evidence.

This is a script which is used for the manual checking. The script is interactive and allows one to view the organization information
the Trusted party certificate and its detailed information and mark the Trusted party as valid or invalid. 

## Running the script
The script only needs a URI and authentication information to the running Neo4J database. This unfortunately isn't
taken from the CLI arguments, but is hardcoded in the script so one must need to manually modify the script. After correct
URI and authentication credentials are presented it suffices to run the script like `python3 TP_manual_checker.py`.