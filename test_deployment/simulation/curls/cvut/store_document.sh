curl --location 'http://munich-prov-storage-provider.de:8000/api/v1/organizations/CVUT/documents/04_preprocessing' \
--header 'Content-Type: application/json' \
--data '{
  "document": "ewogICJwcmVmaXgiIDogewogICAgInhzZCIgOiAiaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEjIiwKICAgICJuc19SREMiIDogImh0dHA6Ly9tdW5pY2gtcHJvdi1zdG9yYWdlLXByb3ZpZGVyLmRlOjgwMDAvYXBpL3YxL29yZ2FuaXphdGlvbnMvQ1ZVVC9kb2N1bWVudHMvIiwKICAgICJwcm92IiA6ICJodHRwOi8vd3d3LnczLm9yZy9ucy9wcm92IyIKICB9LAogICJidW5kbGUiIDogewogICAgIm5zX1JEQzowNF9wcmVwcm9jZXNzaW5nIiA6IHsKICAgICAgInByZWZpeCIgOiB7CiAgICAgICAgIm5zX1JEQyIgOiAiaHR0cDovL211bmljaC1wcm92LXN0b3JhZ2UtcHJvdmlkZXIuZGU6ODAwMC9hcGkvdjEvb3JnYW5pemF0aW9ucy9DVlVUL2RvY3VtZW50cy8iLAogICAgICAgICJjcG0iIDogImh0dHBzOi8vd3d3LmNvbW1vbnByb3ZlbmFuY2Vtb2RlbC5vcmcvY3BtLW5hbWVzcGFjZS12MS0wLyIsCiAgICAgICAgImRjdCIgOiAiaHR0cDovL3B1cmwub3JnL2RjL3Rlcm1zLyIsCiAgICAgICAgImNvbm5lY3RvciIgOiAiaHR0cDovL3Byb3ZlbmFuY2Utc3RvcmFnZS1wcm92aWRlci5jb206ODAwMC9hcGkvdjEvY29ubmVjdG9ycy8iLAogICAgICAgICJzZWxmX2Nvbm5lY3RvciIgOiAiaHR0cDovL211bmljaC1wcm92LXN0b3JhZ2UtcHJvdmlkZXIuZGU6ODAwMC9hcGkvdjEvY29ubmVjdG9ycy8iLAogICAgICAgICJtZXRhIiA6ICJodHRwOi8vbXVuaWNoLXByb3Ytc3RvcmFnZS1wcm92aWRlci5kZTo4MDAwL2FwaS92MS9kb2N1bWVudHMvbWV0YS8iLAogICAgICAgICJ4c2QiIDogImh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hIyIsCiAgICAgICAgIm5zX3BhdGhvbG9neSIgOiAiaHR0cDovL3Byb3ZlbmFuY2Utc3RvcmFnZS1wcm92aWRlci5jb206ODAwMC9hcGkvdjEvb3JnYW5pemF0aW9ucy9VbmlQYXJpcy8iLAogICAgICAgICJwcm92IiA6ICJodHRwOi8vd3d3LnczLm9yZy9ucy9wcm92IyIKICAgICAgfSwKICAgICAgImVudGl0eSIgOiB7CiAgICAgICAgIm5zX1JEQzp0aWxlc0JhdGNoMSIgOiB7CiAgICAgICAgICAiY3BtOmV4dGVybmFsSWQiIDogWyAiYmF0Y2gtaWQtMSIgXQogICAgICAgIH0sCiAgICAgICAgIm5zX1JEQzp0ZXN0RGF0YXNldCIgOiB7CiAgICAgICAgICAiY3BtOmV4dGVybmFsSWQiIDogWyAiZGF0YXNldElkMiIgXQogICAgICAgIH0sCiAgICAgICAgIm5zX1JEQzp0cmFpbkRhdGFzZXQiIDogewogICAgICAgICAgImNwbTpleHRlcm5hbElkIiA6IFsgImRhdGFzZXRJZDEiIF0KICAgICAgICB9LAogICAgICAgICJzZWxmX2Nvbm5lY3Rvcjp0cmFpbkRhdGFzZXRDb25uZWN0b3IiIDogewogICAgICAgICAgImNwbTpyZWNlaXZlclNlcnZpY2VVcmkiIDogWyAiI1VSSSMiIF0sCiAgICAgICAgICAicHJvdjp0eXBlIiA6IFsgewogICAgICAgICAgICAidHlwZSIgOiAicHJvdjpRVUFMSUZJRURfTkFNRSIsCiAgICAgICAgICAgICIkIiA6ICJjcG06Zm9yd2FyZENvbm5lY3RvciIKICAgICAgICAgIH0gXQogICAgICAgIH0sCiAgICAgICAgIm5zX3BhdGhvbG9neTpXU0lEYXRhQ29ubmVjdG9yMi1iIiA6IHsKICAgICAgICAgICJjcG06ZXh0ZXJuYWxJZCIgOiBbICJ3c2ktaWQtMSIgXQogICAgICAgIH0sCiAgICAgICAgInNlbGZfY29ubmVjdG9yOnRlc3REYXRhc2V0Q29ubmVjdG9yIiA6IHsKICAgICAgICAgICJjcG06cmVjZWl2ZXJTZXJ2aWNlVXJpIiA6IFsgIiNVUkkjIiBdLAogICAgICAgICAgInByb3Y6dHlwZSIgOiBbIHsKICAgICAgICAgICAgInR5cGUiIDogInByb3Y6UVVBTElGSUVEX05BTUUiLAogICAgICAgICAgICAiJCIgOiAiY3BtOmZvcndhcmRDb25uZWN0b3IiCiAgICAgICAgICB9IF0KICAgICAgICB9LAogICAgICAgICJjb25uZWN0b3I6V1NJRGF0YUNvbm5lY3RvcjIiIDogewogICAgICAgICAgImNwbTpzZW5kZXJTZXJ2aWNlVXJpIiA6IFsgIiNVUkkjIiBdLAogICAgICAgICAgImNwbTpzZW5kZXJCdW5kbGVJZCIgOiBbIHsKICAgICAgICAgICAgInR5cGUiIDogInByb3Y6UVVBTElGSUVEX05BTUUiLAogICAgICAgICAgICAiJCIgOiAibnNfcGF0aG9sb2d5OjAyX3NjYW5uaW5nIgogICAgICAgICAgfSBdLAogICAgICAgICAgInByb3Y6dHlwZSIgOiBbIHsKICAgICAgICAgICAgInR5cGUiIDogInByb3Y6UVVBTElGSUVEX05BTUUiLAogICAgICAgICAgICAiJCIgOiAiY3BtOmJhY2t3YXJkQ29ubmVjdG9yIgogICAgICAgICAgfSBdCiAgICAgICAgfQogICAgICB9LAogICAgICAiYWN0aXZpdHkiIDogewogICAgICAgICJuc19SREM6cHJlcHJvY2Vzc2luZyIgOiB7CiAgICAgICAgICAiY3BtOm1ldGFidW5kbGUiIDogWyB7CiAgICAgICAgICAgICJ0eXBlIiA6ICJwcm92OlFVQUxJRklFRF9OQU1FIiwKICAgICAgICAgICAgIiQiIDogIm1ldGE6bWV0YTIiCiAgICAgICAgICB9IF0sCiAgICAgICAgICAiZGN0Omhhc1BhcnQiIDogWyB7CiAgICAgICAgICAgICJ0eXBlIiA6ICJwcm92OlFVQUxJRklFRF9OQU1FIiwKICAgICAgICAgICAgIiQiIDogIm5zX1JEQzp0aWxlc0dlbmVyYXRpb24iCiAgICAgICAgICB9LCB7CiAgICAgICAgICAgICJ0eXBlIiA6ICJwcm92OlFVQUxJRklFRF9OQU1FIiwKICAgICAgICAgICAgIiQiIDogIm5zX1JEQzpkYXRhc2V0U3BsaXQiCiAgICAgICAgICB9IF0sCiAgICAgICAgICAicHJvdjp0eXBlIiA6IFsgewogICAgICAgICAgICAidHlwZSIgOiAicHJvdjpRVUFMSUZJRURfTkFNRSIsCiAgICAgICAgICAgICIkIiA6ICJjcG06bWFpbkFjdGl2aXR5IgogICAgICAgICAgfSwgewogICAgICAgICAgICAidHlwZSIgOiAicHJvdjpRVUFMSUZJRURfTkFNRSIsCiAgICAgICAgICAgICIkIiA6ICJjcG06ZGF0YUhhbmRsaW5nIgogICAgICAgICAgfSBdCiAgICAgICAgfSwKICAgICAgICAibnNfUkRDOnRpbGVzR2VuZXJhdGlvbiIgOiB7IH0sCiAgICAgICAgIm5zX1JEQzpkYXRhc2V0U3BsaXQiIDogeyB9CiAgICAgIH0sCiAgICAgICJhZ2VudCIgOiB7CiAgICAgICAgIm5zX1JEQzpwYXRob2xvZ3lEZXBhcnRtZW50IiA6IHsKICAgICAgICAgICJjcG06Y29udGFjdElkUGlkIiA6IFsgIiIgXSwKICAgICAgICAgICJwcm92OnR5cGUiIDogWyB7CiAgICAgICAgICAgICJ0eXBlIiA6ICJwcm92OlFVQUxJRklFRF9OQU1FIiwKICAgICAgICAgICAgIiQiIDogImNwbTpzZW5kZXJBZ2VudCIKICAgICAgICAgIH0gXQogICAgICAgIH0sCiAgICAgICAgIm5zX1JEQzpyZXNlYXJjaERhdGFDZW50ZXIiIDogewogICAgICAgICAgImNwbTpjb250YWN0SWRQaWQiIDogWyAiIiBdLAogICAgICAgICAgInByb3Y6dHlwZSIgOiBbIHsKICAgICAgICAgICAgInR5cGUiIDogInByb3Y6UVVBTElGSUVEX05BTUUiLAogICAgICAgICAgICAiJCIgOiAiY3BtOnJlY2VpdmVyQWdlbnQiCiAgICAgICAgICB9IF0KICAgICAgICB9CiAgICAgIH0sCiAgICAgICJ1c2VkIiA6IHsKICAgICAgICAiXzpuNCIgOiB7CiAgICAgICAgICAicHJvdjphY3Rpdml0eSIgOiAibnNfUkRDOmRhdGFzZXRTcGxpdCIsCiAgICAgICAgICAicHJvdjplbnRpdHkiIDogIm5zX1JEQzp0aWxlc0JhdGNoMSIKICAgICAgICB9LAogICAgICAgICJfOm4xMCIgOiB7CiAgICAgICAgICAicHJvdjphY3Rpdml0eSIgOiAibnNfUkRDOnByZXByb2Nlc3NpbmciLAogICAgICAgICAgInByb3Y6ZW50aXR5IiA6ICJjb25uZWN0b3I6V1NJRGF0YUNvbm5lY3RvcjIiCiAgICAgICAgfSwKICAgICAgICAiXzpuMSIgOiB7CiAgICAgICAgICAicHJvdjphY3Rpdml0eSIgOiAibnNfUkRDOnRpbGVzR2VuZXJhdGlvbiIsCiAgICAgICAgICAicHJvdjplbnRpdHkiIDogIm5zX3BhdGhvbG9neTpXU0lEYXRhQ29ubmVjdG9yMi1iIgogICAgICAgIH0KICAgICAgfSwKICAgICAgIndhc0F0dHJpYnV0ZWRUbyIgOiB7CiAgICAgICAgIl86bjgiIDogewogICAgICAgICAgInByb3Y6ZW50aXR5IiA6ICJzZWxmX2Nvbm5lY3Rvcjp0ZXN0RGF0YXNldENvbm5lY3RvciIsCiAgICAgICAgICAicHJvdjphZ2VudCIgOiAibnNfUkRDOnJlc2VhcmNoRGF0YUNlbnRlciIKICAgICAgICB9LAogICAgICAgICJfOm45IiA6IHsKICAgICAgICAgICJwcm92OmVudGl0eSIgOiAic2VsZl9jb25uZWN0b3I6dHJhaW5EYXRhc2V0Q29ubmVjdG9yIiwKICAgICAgICAgICJwcm92OmFnZW50IiA6ICJuc19SREM6cmVzZWFyY2hEYXRhQ2VudGVyIgogICAgICAgIH0sCiAgICAgICAgIl86bjciIDogewogICAgICAgICAgInByb3Y6ZW50aXR5IiA6ICJjb25uZWN0b3I6V1NJRGF0YUNvbm5lY3RvcjIiLAogICAgICAgICAgInByb3Y6YWdlbnQiIDogIm5zX1JEQzpwYXRob2xvZ3lEZXBhcnRtZW50IgogICAgICAgIH0KICAgICAgfSwKICAgICAgInNwZWNpYWxpemF0aW9uT2YiIDogewogICAgICAgICJfOm4xNiIgOiB7CiAgICAgICAgICAicHJvdjpzcGVjaWZpY0VudGl0eSIgOiAibnNfUkRDOnRyYWluRGF0YXNldCIsCiAgICAgICAgICAicHJvdjpnZW5lcmFsRW50aXR5IiA6ICJzZWxmX2Nvbm5lY3Rvcjp0cmFpbkRhdGFzZXRDb25uZWN0b3IiCiAgICAgICAgfSwKICAgICAgICAiXzpuMTUiIDogewogICAgICAgICAgInByb3Y6c3BlY2lmaWNFbnRpdHkiIDogIm5zX1JEQzp0ZXN0RGF0YXNldCIsCiAgICAgICAgICAicHJvdjpnZW5lcmFsRW50aXR5IiA6ICJzZWxmX2Nvbm5lY3Rvcjp0ZXN0RGF0YXNldENvbm5lY3RvciIKICAgICAgICB9LAogICAgICAgICJfOm4xNyIgOiB7CiAgICAgICAgICAicHJvdjpzcGVjaWZpY0VudGl0eSIgOiAibnNfcGF0aG9sb2d5OldTSURhdGFDb25uZWN0b3IyLWIiLAogICAgICAgICAgInByb3Y6Z2VuZXJhbEVudGl0eSIgOiAiY29ubmVjdG9yOldTSURhdGFDb25uZWN0b3IyIgogICAgICAgIH0KICAgICAgfSwKICAgICAgIndhc0Rlcml2ZWRGcm9tIiA6IHsKICAgICAgICAiXzpuMiIgOiB7CiAgICAgICAgICAicHJvdjpnZW5lcmF0ZWRFbnRpdHkiIDogIm5zX1JEQzp0ZXN0RGF0YXNldCIsCiAgICAgICAgICAicHJvdjp1c2VkRW50aXR5IiA6ICJuc19SREM6dGlsZXNCYXRjaDEiCiAgICAgICAgfSwKICAgICAgICAiXzpuMTMiIDogewogICAgICAgICAgInByb3Y6Z2VuZXJhdGVkRW50aXR5IiA6ICJzZWxmX2Nvbm5lY3Rvcjp0cmFpbkRhdGFzZXRDb25uZWN0b3IiLAogICAgICAgICAgInByb3Y6dXNlZEVudGl0eSIgOiAiY29ubmVjdG9yOldTSURhdGFDb25uZWN0b3IyIgogICAgICAgIH0sCiAgICAgICAgIl86bjMiIDogewogICAgICAgICAgInByb3Y6Z2VuZXJhdGVkRW50aXR5IiA6ICJuc19SREM6dHJhaW5EYXRhc2V0IiwKICAgICAgICAgICJwcm92OnVzZWRFbnRpdHkiIDogIm5zX1JEQzp0aWxlc0JhdGNoMSIKICAgICAgICB9LAogICAgICAgICJfOm4xMSIgOiB7CiAgICAgICAgICAicHJvdjpnZW5lcmF0ZWRFbnRpdHkiIDogInNlbGZfY29ubmVjdG9yOnRlc3REYXRhc2V0Q29ubmVjdG9yIiwKICAgICAgICAgICJwcm92OnVzZWRFbnRpdHkiIDogImNvbm5lY3RvcjpXU0lEYXRhQ29ubmVjdG9yMiIKICAgICAgICB9CiAgICAgIH0sCiAgICAgICJ3YXNHZW5lcmF0ZWRCeSIgOiB7CiAgICAgICAgIl86bjUiIDogewogICAgICAgICAgInByb3Y6ZW50aXR5IiA6ICJuc19SREM6dHJhaW5EYXRhc2V0IiwKICAgICAgICAgICJwcm92OmFjdGl2aXR5IiA6ICJuc19SREM6ZGF0YXNldFNwbGl0IgogICAgICAgIH0sCiAgICAgICAgIl86bjYiIDogewogICAgICAgICAgInByb3Y6ZW50aXR5IiA6ICJuc19SREM6dGVzdERhdGFzZXQiLAogICAgICAgICAgInByb3Y6YWN0aXZpdHkiIDogIm5zX1JEQzpkYXRhc2V0U3BsaXQiCiAgICAgICAgfSwKICAgICAgICAiXzpuMTIiIDogewogICAgICAgICAgInByb3Y6ZW50aXR5IiA6ICJzZWxmX2Nvbm5lY3Rvcjp0ZXN0RGF0YXNldENvbm5lY3RvciIsCiAgICAgICAgICAicHJvdjphY3Rpdml0eSIgOiAibnNfUkRDOnByZXByb2Nlc3NpbmciCiAgICAgICAgfSwKICAgICAgICAiXzpuMCIgOiB7CiAgICAgICAgICAicHJvdjplbnRpdHkiIDogIm5zX1JEQzp0aWxlc0JhdGNoMSIsCiAgICAgICAgICAicHJvdjphY3Rpdml0eSIgOiAibnNfUkRDOnRpbGVzR2VuZXJhdGlvbiIKICAgICAgICB9LAogICAgICAgICJfOm4xNCIgOiB7CiAgICAgICAgICAicHJvdjplbnRpdHkiIDogInNlbGZfY29ubmVjdG9yOnRyYWluRGF0YXNldENvbm5lY3RvciIsCiAgICAgICAgICAicHJvdjphY3Rpdml0eSIgOiAibnNfUkRDOnByZXByb2Nlc3NpbmciCiAgICAgICAgfQogICAgICB9CiAgICB9CiAgfQp9",
  "documentFormat": "json",
  "signature": "YkiIDYm3QRzARK4AauQrYOuhCqCvi+jhESxTv7/i7mvd0ZZ8wPtiIgNg3Ofg6G9dNJzNrAQRiZFXraNHsnLOsdgJhky3Cg3PLNA7Sy+XMDpJoHsc5R2Rf3xXpT7gMaHNnZJrs9LD15BOLgnFyBj5UJLgKs9vYdsF2U2DJndHYVy5hxtwm9CEhaDdIC+GjWfDtNGoG1fGhl1k1Dbopq5NTSMxrr2Qiixk3Mms/URQvVYOochVA8d2LPstPboFNJPMTkXRocmuHpCISO3tQ8XVZew3rvQ3Cw1QkByB+Qm7FXIiTgmpZB1SbugINSC4YF7uNFrkciMPyokOeKLvAviLTA==",
  "createdOn": 1716112998
}
'