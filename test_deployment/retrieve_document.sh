#!/bin/bash

CONTAINER_NAME="example_storage"
IP=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${CONTAINER_NAME})

curl -GET "http://${IP}:8000/api/v1/organizations/ORG/documents/01_sample_acquisition"
