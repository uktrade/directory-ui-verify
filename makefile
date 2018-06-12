build: docker_test

clean:
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete

test_requirements:
	pip install -r requirements_test.txt

FLAKE8 := flake8 . --exclude=migrations,.venv,node_modules
PYTEST := pytest . -v --ignore=node_modules --cov=. --cov-config=.coveragerc --capture=no $(pytest_args)
COLLECT_STATIC := python manage.py collectstatic --noinput
CODECOV := \
	if [ "$$CODECOV_REPO_TOKEN" != "" ]; then \
	   codecov --token=$$CODECOV_REPO_TOKEN ;\
	fi

test:
	$(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST) && $(CODECOV)

DJANGO_WEBSERVER := \
	python manage.py collectstatic --noinput && \
	python manage.py runserver 0.0.0.0:$$PORT

django_webserver:
	$(DJANGO_WEBSERVER)

DOCKER_COMPOSE_REMOVE_AND_PULL := docker-compose -f docker-compose.yml -f docker-compose-test.yml rm -f && docker-compose -f docker-compose.yml -f docker-compose-test.yml pull
DOCKER_COMPOSE_CREATE_ENVS := python ./docker/env_writer.py ./docker/env.json ./docker/env.test.json

docker_run:
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose up --build

DOCKER_SET_DEBUG_ENV_VARS := \
	export DIRECTORY_UI_VERIFICATION_SSO_PROXY_SIGNATURE_SECRET=api_signature_debug; \
	export DIRECTORY_UI_VERIFICATION_SSO_PROXY_API_CLIENT_BASE_URL=http://sso.trade.great:8004/; \
	export DIRECTORY_UI_VERIFICATION_SSO_PROXY_LOGIN_URL=http://sso.trade.great:8004/accounts/login/; \
	export DIRECTORY_UI_VERIFICATION_SSO_PROXY_LOGOUT_URL=http://sso.trade.great:8004/accounts/logout/?next=http://exred.trade.great:8007; \
	export DIRECTORY_UI_VERIFICATION_SSO_PROXY_SIGNUP_URL=http://sso.trade.great:8004/accounts/signup/; \
	export DIRECTORY_UI_VERIFICATION_SSO_PROFILE_URL=http://profile.trade.great:8006/about/; \
	export DIRECTORY_UI_VERIFICATION_SSO_PROXY_REDIRECT_FIELD_NAME=next; \
	export DIRECTORY_UI_VERIFICATION_SSO_PROXY_SESSION_COOKIE=debug_sso_session_cookie; \
	export DIRECTORY_UI_VERIFICATION_SESSION_COOKIE_SECURE=false; \
	export DIRECTORY_UI_VERIFICATION_PORT=8011; \
	export DIRECTORY_UI_VERIFICATION_SECRET_KEY=debug; \
	export DIRECTORY_UI_VERIFICATION_DEBUG=true; \
	export DIRECTORY_UI_VERIFICATION_GOOGLE_TAG_MANAGER_ID=GTM-NLJP5CL; \
	export DIRECTORY_UI_VERIFICATION_GOOGLE_TAG_MANAGER_ENV=&gtm_auth=S2-vb6_RF_jGWu2WJIORdQ&gtm_preview=env-5&gtm_cookies_win=x; \
	export DIRECTORY_UI_VERIFICATION_UTM_COOKIE_DOMAIN=.great; \
	export DIRECTORY_UI_VERIFICATION_COMPANIES_HOUSE_CLIENT_ID=debug-client-id; \
	export DIRECTORY_UI_VERIFICATION_COMPANIES_HOUSE_CLIENT_SECRET=debug-client-secret; \
	export DIRECTORY_UI_VERIFICATION_SECURE_HSTS_SECONDS=0; \
	export DIRECTORY_UI_VERIFICATION_PYTHONWARNINGS=all; \
	export DIRECTORY_UI_VERIFICATION_PYTHONDEBUG=true; \
	export DIRECTORY_UI_VERIFICATION_HEADER_FOOTER_URLS_GREAT_HOME=http://exred.trade.great:8007/; \
	export DIRECTORY_UI_VERIFICATION_HEADER_FOOTER_URLS_FAB=http://buyer.trade.great:8001; \
	export DIRECTORY_UI_VERIFICATION_HEADER_FOOTER_URLS_SOO=http://soo.trade.great:8008; \
	export DIRECTORY_UI_VERIFICATION_HEADER_FOOTER_URLS_CONTACT_US=http://contact.trade.great:8009/directory/; \
	export DIRECTORY_UI_VERIFICATION_SECURE_SSL_REDIRECT=false; \
	export DIRECTORY_UI_VERIFICATION_HEALTH_CHECK_TOKEN=debug; \
	export DIRECTORY_UI_VERIFICATION_VERIFY_PROVIDER_URL=http://localhost:50400; \
	export DIRECTORY_UI_VERIFICATION_COMPLIANCE_TOOL_SSO_URL=https://compliance-tool-reference.ida.digital.cabinet-office.gov.uk/SAML2/SSO/; \
	export DIRECTORY_UI_VERIFICATION_COMPLIANCE_TOOL_SET_TEST_DATA_URL=https://compliance-tool-reference.ida.digital.cabinet-office.gov.uk/service-test-data; \
	export DIRECTORY_UI_VERIFICATION_FEATURE_GOV_VERIFY_COMPLIANCE_TOOL_ENABLED=true; \
	export DIRECTORY_UI_VERIFICATION_VERIFY_SERVICE_PROVIDER_URL=http://localhost:50400; \
	export DIRECTORY_UI_VERIFICATION_VERIFY_SERVICE_PROVIDER_SAML_SIGNING_KEY=debug; \
	export DIRECTORY_UI_VERIFICATION_INTERNAL_CH_BASE_URL=http://localhost:8012; \
	export DIRECTORY_UI_VERIFICATION_INTERNAL_CH_API_KEY=debug; \
	export DIRECTORY_UI_VERIFICATION_API_SIGNATURE_SECRET=debug; \
	export DIRECTORY_UI_VERIFICATION_API_CLIENT_BASE_URL=http://api.trade.great:8000


docker_test_env_files:
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS)

DOCKER_REMOVE_ALL := \
	docker ps -a | \
	grep directoryui_ | \
	awk '{print $$1 }' | \
	xargs -I {} docker rm -f {}

docker_remove_all:
	$(DOCKER_REMOVE_ALL)

docker_debug: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	docker-compose pull && \
	docker-compose build && \
	docker-compose run --service-ports webserver make django_webserver

docker_webserver_bash:
	docker exec -it directoryui_webserver_1 sh

docker_test: docker_remove_all
	$(DOCKER_SET_DEBUG_ENV_VARS) && \
	$(DOCKER_COMPOSE_CREATE_ENVS) && \
	$(DOCKER_COMPOSE_REMOVE_AND_PULL) && \
	docker-compose -f docker-compose-test.yml build && \
	docker-compose -f docker-compose-test.yml run sut

docker_build:
	docker build -t ukti/directory-ui-export-readiness:latest .

DEBUG_SET_ENV_VARS := \
	export PORT=8011; \
	export SECRET_KEY=debug; \
	export DEBUG=true ;\
	export SSO_PROXY_SIGNATURE_SECRET=proxy_signature_debug; \
	export SSO_PROXY_API_CLIENT_BASE_URL=http://sso.trade.great:8004/; \
	export SSO_PROXY_LOGIN_URL=http://sso.trade.great:8004/accounts/login/; \
	export SSO_PROXY_LOGOUT_URL=http://sso.trade.great:8004/accounts/logout/?next=http://exred.trade.great:8007; \
	export SSO_PROXY_SIGNUP_URL=http://sso.trade.great:8004/accounts/signup/; \
	export SSO_PROFILE_URL=http://profile.trade.great:8006/about/; \
	export SSO_PROXY_REDIRECT_FIELD_NAME=next; \
	export SSO_PROXY_SESSION_COOKIE=debug_sso_session_cookie; \
	export SESSION_COOKIE_SECURE=false; \
	export GOOGLE_TAG_MANAGER_ID=GTM-NLJP5CL; \
	export GOOGLE_TAG_MANAGER_ENV=&gtm_auth=S2-vb6_RF_jGWu2WJIORdQ&gtm_preview=env-5&gtm_cookies_win=x; \
	export UTM_COOKIE_DOMAIN=.great; \
	export COMPANIES_HOUSE_CLIENT_ID=debug-client-id; \
	export COMPANIES_HOUSE_CLIENT_SECRET=debug-client-secret; \
	export SECURE_HSTS_SECONDS=0; \
	export PYTHONWARNINGS=all; \
	export PYTHONDEBUG=true; \
	export HEADER_FOOTER_URLS_GREAT_HOME=http://exred.trade.great:8007/; \
	export HEADER_FOOTER_URLS_FAB=http://buyer.trade.great:8001; \
	export HEADER_FOOTER_URLS_SOO=http://soo.trade.great:8008; \
	export HEADER_FOOTER_URLS_CONTACT_US=http://contact.trade.great:8009/directory/; \
	export SECURE_SSL_REDIRECT=false; \
	export HEALTH_CHECK_TOKEN=debug; \
	export VERIFY_SERVICE_PROVIDER_URL=http://localhost:50400; \
	export VERIFY_SERVICE_PROVIDER_SAML_SIGNING_KEY=$$DIRECTORY_UI_VERIFICATION_VERIFY_SERVICE_PROVIDER_SAML_SIGNING_KEY; \
	export COMPLIANCE_TOOL_SSO_URL=https://compliance-tool-reference.ida.digital.cabinet-office.gov.uk/SAML2/SSO/; \
	export COMPLIANCE_TOOL_SET_TEST_DATA_URL=https://compliance-tool-reference.ida.digital.cabinet-office.gov.uk/service-test-data; \
	export COMPLIANCE_TOOL_CONSUMER_SERVICE_URL=http://verification.trade.great:8011/eligibility-check/; \
	export COMPLIANCE_TOOL_SIGNING_CERTIFICATE=$$DIRECTORY_UI_VERIFICATION_COMPLIANCE_TOOL_SIGNING_CERTIFICATE; \
	export COMPLIANCE_TOOL_ENCRYPTION_CERTIFICATE=$$DIRECTORY_UI_VERIFICATION_COMPLIANCE_TOOL_ENCRYPTION_CERTIFICATE; \
	export COMPLIANCE_TOOL_MATCHING_SERVICE_SIGNING_PRIVATE_KEY=$$DIRECTORY_UI_VERIFICATION_COMPLIANCE_TOOL_MATCHING_SERVICE_SIGNING_PRIVATE_KEY; \
	export COMPLIANCE_TOOL_MATCHING_SERVICE_ENTITY_ID=http://verification.trade.great:8011/identity-verify/; \
	export FEATURE_GOV_VERIFY_COMPLIANCE_TOOL_ENABLED=true; \
	export INTERNAL_CH_BASE_URL=http://localhost:8012; \
	export INTERNAL_CH_API_KEY=debug; \
	export FEATURE_OFFICER_CACHE_ENABLED=true; \
	export REDIS_CACHE_URL=redis://127.0.0.1:6379; \
	export API_SIGNATURE_SECRET=debug; \
	export API_CLIENT_BASE_URL=http://api.trade.great:8000


TEST_SET_ENV_VARS := \
	export FEATURE_OFFICER_CACHE_ENABLED=false


debug_webserver:
	$(DEBUG_SET_ENV_VARS) && $(DJANGO_WEBSERVER)

debug_pytest:
	$(DEBUG_SET_ENV_VARS) && $(TEST_SET_ENV_VARS) && $(COLLECT_STATIC) && $(PYTEST)

debug_test:
	$(DEBUG_SET_ENV_VARS) && $(TEST_SET_ENV_VARS) && $(COLLECT_STATIC) && $(FLAKE8) && $(PYTEST) --cov-report=html

debug_test_last_failed:
	make debug_test pytest_args='-v --last-failed'

debug_manage:
	$(DEBUG_SET_ENV_VARS) && ./manage.py $(cmd)

debug_shell:
	$(DEBUG_SET_ENV_VARS) && ./manage.py shell

debug: test_requirements debug_test

heroku_deploy_dev:
	docker build -t registry.heroku.com/directory-ui-verification-dev/web .
	docker push registry.heroku.com/directory-ui-verification-dev/web

compile_requirements:
	python3 -m piptools compile requirements.in

compile_test_requirements:
	python3 -m piptools compile requirements_test.in

compile_all_requirements: compile_requirements compile_test_requirements

define generate_certificate
	cd ./verify-matching-service-adapter
	# Generate a private key:
	openssl genrsa -des3 -passout pass:x -out "$(1).pass.key" 2048
	openssl rsa -passin pass:x -in "$(1).pass.key" -out "$(1).key"
	# Generate a certificate signing request (CSR):
	openssl req -batch -new -subj "/CN=$(2)" -key "$(1).key" -out "$(1).csr"
	# Generate a self signed certificate:
	openssl x509 -req -sha256 -in "$(1).csr" -signkey "$(1).key" -out "$(1).crt"
	# Convert the private key to .pk8 format:
	openssl pkcs8 -topk8 -inform PEM -outform DER -in "$(1).key" -out "$(1).pk8" -nocrypt
	# Clean up the files you don’t need anymore:
	rm "$(1).pass.key"
	rm "$(1).csr"
	rm "$(1).key"
endef

generate_matching_service_adapter_certificates:
	$(call generate_certificate,test_primary_signing,Service MSA Signing)
	$(call generate_certificate,test_secondary_signing,Service MSA Signing)
	$(call generate_certificate,test_msa_encryption_1,Service MSA Signing)
	$(call generate_certificate,test_msa_encryption_2,Service MSA Signing)

generate_service_provider_encryption_key:
	openssl genrsa -des3 -passout pass:x 2048 | openssl rsa -passin pass:x -out key-name.pem; \
	openssl pkcs8 -topk8 -inform PEM -outform DER -in key-name.pem -nocrypt | openssl base64 -A; echo; \
	rm key-name.pem

run_verify_serivce_provider:
	cd ./verify-service-provider; \
	VERIFY_ENVIRONMENT=COMPLIANCE_TOOL \
	SERVICE_ENTITY_IDS='["http://verification.trade.great:8011/eligibility-check/"]' \
	MSA_ENTITY_ID=http://verification.trade.great:8011/identity-verify/ \
	MSA_METADATA_URL=http://localhost:8080/matching-service/SAML2/metadata \
	SAML_SIGNING_KEY=$$DIRECTORY_UI_VERIFICATION_VERIFY_SERVICE_PROVIDER_SAML_SIGNING_KEY \
	SAML_PRIMARY_ENCRYPTION_KEY=$$DIRECTORY_UI_VERIFICATION_VERIFY_SERVICE_PROVIDER_SAML_PRIMARY_ENCRYPTION_KEY \
	./bin/verify-service-provider server verify-service-provider.yml

run_matching_service_adapter:
	cd verify-matching-service-adapter; \
	java -jar ./verify-matching-service-adapter.jar server test-config.yml

.PHONY: build clean test_requirements docker_run docker_debug docker_webserver_bash docker_test debug_webserver debug_test debug heroku_deploy_dev heroku_deploy_demo
