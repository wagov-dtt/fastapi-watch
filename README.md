# fastapi-watch

audit passed http requests with traefik and fastapi (to enable enhanced logging)

## Overview

![diagram showing rough concept](overview.png)

The justfile in this repository should be able to build am audit namespace on a kubernetes cluster, that can be configured to pass requests to any origin which has a path for adding requester information to a request. In parallel to passing requests, the backend should be queried and the correlated request information logged as clean json for further processing by the kubernetes cluster hosting the audit namespace.

## Roadmap

- [ ] Cleanly convert request into json for logging
- [ ] Add header validation for CDN/WAFs
- [ ] Call separate origin path and add info to logs

## Activities to try

The current setup doesn't have validation configured or decent mock endpoints. We could:

- Add a mock_origin endpoint to `main.py` to test header validation of a backend (i.e. only allowing requests when a shared secret is set e.g. via traefik)
- Adjust the kustomize template to enable multiple namespaces (i.e. one namespace per origin configuration)
- Extend a kustomize overlay to support eks on aws (i.e. as per [ADR operations/002-workloads.md](https://github.com/wagov-dtt/architecture-decision-records/blob/main/operations/002-workloads.md) )