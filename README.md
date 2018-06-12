# directory-ui-verification

[![circle-ci-image]][circle-ci]
[![codecov-image]][codecov]

**Verification - the Department for International Trade (DIT)**  

---
### See also:
| [directory-api](https://github.com/uktrade/directory-api) | [directory-ui-buyer](https://github.com/uktrade/directory-ui-buyer) | [directory-ui-supplier](https://github.com/uktrade/directory-ui-supplier) | [directory-ui-export-readiness](https://github.com/uktrade/directory-ui-export-readiness) |
| --- | --- | --- | --- |
| **[directory-sso](https://github.com/uktrade/directory-sso)** | **[directory-sso-proxy](https://github.com/uktrade/directory-sso-proxy)** | **[directory-sso-profile](https://github.com/uktrade/directory-sso-profile)** |  |

For more information on installation please check the [Developers Onboarding Checklist](https://uktrade.atlassian.net/wiki/spaces/ED/pages/32243946/Developers+onboarding+checklist)


## Development

We aim to follow [GDS service standards](https://www.gov.uk/service-manual/service-standard) and [GDS design principles](https://www.gov.uk/design-principles).


## Requirements
[Python 3.5](https://www.python.org/downloads/release/python-352/)


### Docker
To use Docker in your local development environment you will also need the following dependencies:

[Docker >= 1.10](https://docs.docker.com/engine/installation/)

[Docker Compose >= 1.8](https://docs.docker.com/compose/install/)

## Running locally with Docker
This requires all host environment variables to be set.

    $ make docker_run

### Run debug webserver in Docker

    $ make docker_debug

### Run tests in Docker

    $ make docker_test

### Host environment variables for docker-compose
``.env`` files will be automatically created (with ``env_writer.py`` based on ``env.json``) by ``make docker_test``, based on host environment variables with ``DIRECTORY_UI_VERIFICATION_`` prefix.

#### Web server

## Running locally without Docker

### Installing
    $ git clone https://github.com/uktrade/directory-ui-verification
    $ cd directory-ui-verification
    $ virtualenv .venv -p python3.5
    $ source .venv/bin/activate
    $ pip install -r requirements_test.txt

### Running the webserver
    $ source .venv/bin/activate
    $ make debug_webserver

### Running the tests

    $ make debug_test

## Session

Signed cookies are used as the session backend to avoid using a database. We therefore must avoid storing non-trivial data in the session, because the browser will be exposed to the data.

## SSO
To make sso work locally add the following to your machine's `/etc/hosts`:

| IP Adress | URL                      |
| --------  | ------------------------ |
| 127.0.0.1 | buyer.trade.great    |
| 127.0.0.1 | supplier.trade.great |
| 127.0.0.1 | sso.trade.great      |
| 127.0.0.1 | api.trade.great      |
| 127.0.0.1 | profile.trade.great  |
| 127.0.0.1 | exred.trade.great    |
| 127.0.0.1 | verification.trade.great    |

Then log into `directory-sso` via `sso.trade.great:8001`, and use `directory-ui-verification` on `verification.trade.great:8011`

Note in production, the `directory-sso` session cookie is shared with all subdomains that are on the same parent domain as `directory-sso`. However in development we cannot share cookies between subdomains using `localhost` - that would be like trying to set a cookie for `.com`, which is not supported by any RFC.

Therefore to make cookie sharing work in development we need the apps to be running on subdomains. Some stipulations:
 - `directory-ui-export-readiness` and `directory-sso` must both be running on sibling subdomains (with same parent domain)
 - `directory-sso` must be told to target cookies at the parent domain.

## Matching Service Adapter

The MSA is a Java service that sits between gov verify hub and our Local Matching Service.

Download and install it from [here](http://alphagov.github.io/rp-onboarding-tech-docs/pages/matching/matchingserviceadapter.html#msause), extract it to `./verify-matching-service-adapter`.

To run it locally make sure you have generated the required certificates by running `make generate_matching_service_adapter_certificates`.

Update the `test-config.yml`'s `matchingServiceAdapter.entityId` to `http://verification.trade.great:8011/identity-verify/` and `matchingServiceAdapter.externalUrl` to `http://verification.trade.great:8011/identity-verify/`

Then run:

`make run_matching_service_adapter`


## Verify Service Provider

The VSP is a Java service used to generate and decode SAML when communicating with gov Verify.

Download it from [here](https://github.com/alphagov/verify-service-provider/releases) and extract it to `./verify-service-provider`

To run it locally set the following environment variables on your host machine:

- `DIRECTORY_UI_VERIFICATION_VERIFY_SERVICE_PROVIDER_SAML_SIGNING_KEY`: Retrieve this by running `openssl base64 -A -in ./verify-matching-service-adapter/test_primary_signing.pk8`
- `DIRECTORY_UI_VERIFICATION_VERIFY_SERVICE_PROVIDER_SAML_PRIMARY_ENCRYPTION_KEY`: set to the value of `openssl base64 -A -in ./verify-matching-service-adapter/test_msa_encryption_1.pk8`

Then run `$ make run_verify_serivce_provider`


## Compliance tool

Gov Verify provide a tool to trigger Verify hub to make requests to the service. To use it first set the environment variables on your host machine:

- `DIRECTORY_UI_VERIFICATION_VERIFY_SERVICE_PROVIDER_SAML_SIGNING_KEY`: set to the value of make `openssl base64 -A -in ./verify-matching-service-adapter/test_primary_signing.pk8`
- `DIRECTORY_UI_VERIFICATION_COMPLIANCE_TOOL_SIGNING_CERTIFICATE`: Set to the value of `./verify-matching-service-adapter/test_primary_signing.crt`, without the BEGIN and END headers, and with no carriage returns.
- `DIRECTORY_UI_VERIFICATION_COMPLIANCE_TOOL_ENCRYPTION_CERTIFICATE`: Set to the value of `./verify-matching-service-adapter/test_msa_encryption_1.crt`, without the BEGIN and END headers, and with no carriage returns.

Once that is done navigate to `http://verification.trade.great:8011/compliance-tool/` to be redirected to the suite of tests (click on the url of each test to begin the test.)

[circle-ci-image]: https://circleci.com/gh/uktrade/directory-ui-export-readiness/tree/master.svg?style=svg
[circle-ci]: https://circleci.com/gh/uktrade/directory-ui-export-readiness/tree/master

[codecov-image]: https://codecov.io/gh/uktrade/directory-ui-export-readiness/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/uktrade/directory-ui-export-readiness
