# Data Dictionary

This document provides detailed column-level definitions for all tables in the database.

## audit_log_entries

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `instance_id` | `uuid` | Standard field |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `payload` | `json` | Standard field |
| `created_at` | `timestamp with time zone` | Standard field |
| `ip_address` | `character varying(64) DEFAULT ''::character varying NOT NULL` | (Required, Has Default) |

## flow_state

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `user_id` | `uuid` | Standard field |
| `auth_code` | `text NOT NULL` | (Required) |
| `code_challenge_method` | `auth.code_challenge_method NOT NULL` | (Required) |
| `code_challenge` | `text NOT NULL` | (Required) |
| `provider_type` | `text NOT NULL` | (Required) |
| `provider_access_token` | `text` | Standard field |
| `provider_refresh_token` | `text` | Standard field |
| `created_at` | `timestamp with time zone` | Standard field |
| `updated_at` | `timestamp with time zone` | Standard field |
| `authentication_method` | `text NOT NULL` | (Required) |
| `auth_code_issued_at` | `timestamp with time zone` | Standard field |

## identities

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `provider_id` | `text NOT NULL` | (Required) |
| `user_id` | `uuid NOT NULL` | (Required, FK to `auth.users`) |
| `identity_data` | `jsonb NOT NULL` | (Required) |
| `provider` | `text NOT NULL` | (Required) |
| `last_sign_in_at` | `timestamp with time zone` | Standard field |
| `created_at` | `timestamp with time zone` | Standard field |
| `updated_at` | `timestamp with time zone` | Standard field |
| `email` | `text GENERATED ALWAYS AS (lower((identity_data ->> 'email'::text))) STORED` | Standard field |
| `id` | `uuid DEFAULT gen_random_uuid() NOT NULL` | (Required, Has Default, Primary Key) |

## instances

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `uuid` | `uuid` | Standard field |
| `raw_base_config` | `text` | Standard field |
| `created_at` | `timestamp with time zone` | Standard field |
| `updated_at` | `timestamp with time zone` | Standard field |

## mfa_amr_claims

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `session_id` | `uuid NOT NULL` | (Required, FK to `auth.sessions`) |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |
| `updated_at` | `timestamp with time zone NOT NULL` | (Required) |
| `authentication_method` | `text NOT NULL` | (Required) |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |

## mfa_challenges

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `factor_id` | `uuid NOT NULL` | (Required, FK to `auth.mfa_factors`) |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |
| `verified_at` | `timestamp with time zone` | Standard field |
| `ip_address` | `inet NOT NULL` | (Required) |
| `otp_code` | `text` | Standard field |
| `web_authn_session_data` | `jsonb` | Standard field |

## mfa_factors

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `user_id` | `uuid NOT NULL` | (Required, FK to `auth.users`) |
| `friendly_name` | `text` | Standard field |
| `factor_type` | `auth.factor_type NOT NULL` | (Required) |
| `status` | `auth.factor_status NOT NULL` | (Required) |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |
| `updated_at` | `timestamp with time zone NOT NULL` | (Required) |
| `secret` | `text` | Standard field |
| `phone` | `text` | Standard field |
| `last_challenged_at` | `timestamp with time zone` | Standard field |
| `web_authn_credential` | `jsonb` | Standard field |
| `web_authn_aaguid` | `uuid` | Standard field |
| `last_webauthn_challenge_data` | `jsonb` | Standard field |

## oauth_authorizations

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `authorization_id` | `text NOT NULL` | (Required) |
| `client_id` | `uuid NOT NULL` | (Required, FK to `auth.oauth_clients`) |
| `user_id` | `uuid` | (FK to `auth.users`) |
| `redirect_uri` | `text NOT NULL` | (Required) |
| `scope` | `text NOT NULL` | (Required) |
| `state` | `text` | Standard field |
| `resource` | `text` | Standard field |
| `code_challenge` | `text` | Standard field |
| `code_challenge_method` | `auth.code_challenge_method` | Standard field |
| `response_type` | `auth.oauth_response_type DEFAULT 'code'::auth.oauth_response_type NOT NULL` | (Required, Has Default) |
| `status` | `auth.oauth_authorization_status DEFAULT 'pending'::auth.oauth_authorization_status NOT NULL` | (Required, Has Default) |
| `authorization_code` | `text` | Standard field |
| `created_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `expires_at` | `timestamp with time zone DEFAULT (now() + '00:03:00'::interval) NOT NULL` | (Required, Has Default) |
| `approved_at` | `timestamp with time zone` | Standard field |
| `nonce` | `text` | Standard field |

## oauth_client_states

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `provider_type` | `text NOT NULL` | (Required) |
| `code_verifier` | `text` | Standard field |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |

## oauth_clients

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `client_secret_hash` | `text` | Standard field |
| `registration_type` | `auth.oauth_registration_type NOT NULL` | (Required) |
| `redirect_uris` | `text NOT NULL` | (Required) |
| `grant_types` | `text NOT NULL` | (Required) |
| `client_name` | `text` | Standard field |
| `client_uri` | `text` | Standard field |
| `logo_uri` | `text` | Standard field |
| `created_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `updated_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `deleted_at` | `timestamp with time zone` | Standard field |
| `client_type` | `auth.oauth_client_type DEFAULT 'confidential'::auth.oauth_client_type NOT NULL` | (Required, Has Default) |

## oauth_consents

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `user_id` | `uuid NOT NULL` | (Required, FK to `auth.users`) |
| `client_id` | `uuid NOT NULL` | (Required, FK to `auth.oauth_clients`) |
| `scopes` | `text NOT NULL` | (Required) |
| `granted_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `revoked_at` | `timestamp with time zone` | Standard field |

## one_time_tokens

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `user_id` | `uuid NOT NULL` | (Required, FK to `auth.users`) |
| `token_type` | `auth.one_time_token_type NOT NULL` | (Required) |
| `token_hash` | `text NOT NULL` | (Required) |
| `relates_to` | `text NOT NULL` | (Required) |
| `created_at` | `timestamp without time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `updated_at` | `timestamp without time zone DEFAULT now() NOT NULL` | (Required, Has Default) |

## refresh_tokens

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `instance_id` | `uuid` | Standard field |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `token` | `character varying(255)` | Standard field |
| `user_id` | `character varying(255)` | Standard field |
| `revoked` | `boolean` | Standard field |
| `created_at` | `timestamp with time zone` | Standard field |
| `updated_at` | `timestamp with time zone` | Standard field |
| `parent` | `character varying(255)` | Standard field |
| `session_id` | `uuid` | (FK to `auth.sessions`) |

## saml_providers

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `sso_provider_id` | `uuid NOT NULL` | (Required, FK to `auth.sso_providers`) |
| `entity_id` | `text NOT NULL` | (Required) |
| `metadata_xml` | `text NOT NULL` | (Required) |
| `metadata_url` | `text` | Standard field |
| `attribute_mapping` | `jsonb` | Standard field |
| `created_at` | `timestamp with time zone` | Standard field |
| `updated_at` | `timestamp with time zone` | Standard field |
| `name_id_format` | `text` | Standard field |

## saml_relay_states

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `sso_provider_id` | `uuid NOT NULL` | (Required, FK to `auth.sso_providers`) |
| `request_id` | `text NOT NULL` | (Required) |
| `for_email` | `text` | Standard field |
| `redirect_to` | `text` | Standard field |
| `created_at` | `timestamp with time zone` | Standard field |
| `updated_at` | `timestamp with time zone` | Standard field |
| `flow_state_id` | `uuid` | (FK to `auth.flow_state`) |

## schema_migrations

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `version` | `character varying(255) NOT NULL` | (Required) |

## sessions

_User login sessions._

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `user_id` | `uuid NOT NULL` | (Required, FK to `auth.users`) |
| `created_at` | `timestamp with time zone` | Standard field |
| `updated_at` | `timestamp with time zone` | Standard field |
| `factor_id` | `uuid` | Standard field |
| `aal` | `auth.aal_level` | Standard field |
| `not_after` | `timestamp with time zone` | Standard field |
| `refreshed_at` | `timestamp without time zone` | Standard field |
| `user_agent` | `text` | Standard field |
| `ip` | `inet` | Standard field |
| `tag` | `text` | Standard field |
| `oauth_client_id` | `uuid` | (FK to `auth.oauth_clients`) |
| `refresh_token_hmac_key` | `text` | Standard field |
| `refresh_token_counter` | `bigint` | Standard field |
| `scopes` | `text` | Standard field |

## sso_domains

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `sso_provider_id` | `uuid NOT NULL` | (Required, FK to `auth.sso_providers`) |
| `domain` | `text NOT NULL` | (Required) |
| `created_at` | `timestamp with time zone` | Standard field |
| `updated_at` | `timestamp with time zone` | Standard field |

## sso_providers

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `resource_id` | `text` | Standard field |
| `created_at` | `timestamp with time zone` | Standard field |
| `updated_at` | `timestamp with time zone` | Standard field |
| `disabled` | `boolean` | Standard field |

## users

_Supabase managed user identities (linked to public.seydam_customuser)._

**Schema**: `auth`

| Column | Type | Description |
| :--- | :--- | :--- |
| `instance_id` | `uuid` | Standard field |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `aud` | `character varying(255)` | Standard field |
| `role` | `character varying(255)` | Standard field |
| `email` | `character varying(255)` | Standard field |
| `encrypted_password` | `character varying(255)` | Standard field |
| `email_confirmed_at` | `timestamp with time zone` | Standard field |
| `invited_at` | `timestamp with time zone` | Standard field |
| `confirmation_token` | `character varying(255)` | Standard field |
| `confirmation_sent_at` | `timestamp with time zone` | Standard field |
| `recovery_token` | `character varying(255)` | Standard field |
| `recovery_sent_at` | `timestamp with time zone` | Standard field |
| `email_change_token_new` | `character varying(255)` | Standard field |
| `email_change` | `character varying(255)` | Standard field |
| `email_change_sent_at` | `timestamp with time zone` | Standard field |
| `last_sign_in_at` | `timestamp with time zone` | Standard field |
| `raw_app_meta_data` | `jsonb` | Standard field |
| `raw_user_meta_data` | `jsonb` | Standard field |
| `is_super_admin` | `boolean` | Standard field |
| `created_at` | `timestamp with time zone` | Standard field |
| `updated_at` | `timestamp with time zone` | Standard field |
| `phone` | `text DEFAULT NULL::character varying` | (Has Default) |
| `phone_confirmed_at` | `timestamp with time zone` | Standard field |
| `phone_change` | `text DEFAULT ''::character varying` | (Has Default) |
| `phone_change_token` | `character varying(255) DEFAULT ''::character varying` | (Has Default) |
| `phone_change_sent_at` | `timestamp with time zone` | Standard field |
| `confirmed_at` | `timestamp with time zone GENERATED ALWAYS AS (LEAST(email_confirmed_at, phone_confirmed_at)) STORED` | Standard field |
| `email_change_token_current` | `character varying(255) DEFAULT ''::character varying` | (Has Default) |
| `email_change_confirm_status` | `smallint DEFAULT 0` | (Has Default) |
| `banned_until` | `timestamp with time zone` | Standard field |
| `reauthentication_token` | `character varying(255) DEFAULT ''::character varying` | (Has Default) |
| `reauthentication_sent_at` | `timestamp with time zone` | Standard field |
| `is_sso_user` | `boolean DEFAULT false NOT NULL` | (Required, Has Default) |
| `deleted_at` | `timestamp with time zone` | Standard field |
| `is_anonymous` | `boolean DEFAULT false NOT NULL` | (Required, Has Default) |

## account_emailaddress

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer NOT NULL` | (Required, Primary Key) |
| `email` | `character varying(254) NOT NULL` | (Required) |
| `verified` | `boolean NOT NULL` | (Required) |
| `primary` | `boolean NOT NULL` | (Required) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## account_emailconfirmation

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer NOT NULL` | (Required, Primary Key) |
| `created` | `timestamp with time zone NOT NULL` | (Required) |
| `sent` | `timestamp with time zone` | Standard field |
| `key` | `character varying(64) NOT NULL` | (Required) |
| `email_address_id` | `integer NOT NULL` | (Required, FK to `public.account_emailaddress`) |

## auth_group

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer NOT NULL` | (Required, Primary Key) |
| `name` | `character varying(150) NOT NULL` | (Required) |

## auth_group_permissions

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `group_id` | `integer NOT NULL` | (Required, FK to `public.auth_group`) |
| `permission_id` | `integer NOT NULL` | (Required, FK to `public.auth_permission`) |

## auth_permission

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer NOT NULL` | (Required, Primary Key) |
| `name` | `character varying(255) NOT NULL` | (Required) |
| `content_type_id` | `integer NOT NULL` | (Required, FK to `public.django_content_type`) |
| `codename` | `character varying(100) NOT NULL` | (Required) |

## authtoken_token

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `key` | `character varying(40) NOT NULL` | (Required) |
| `created` | `timestamp with time zone NOT NULL` | (Required) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## django_admin_log

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer NOT NULL` | (Required, Primary Key) |
| `action_time` | `timestamp with time zone NOT NULL` | (Required) |
| `object_id` | `text` | Standard field |
| `object_repr` | `character varying(200) NOT NULL` | (Required) |
| `action_flag` | `smallint NOT NULL` | (Required) |
| `change_message` | `text NOT NULL` | (Required) |
| `content_type_id` | `integer` | (FK to `public.django_content_type`) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## django_content_type

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer NOT NULL` | (Required, Primary Key) |
| `app_label` | `character varying(100) NOT NULL` | (Required) |
| `model` | `character varying(100) NOT NULL` | (Required) |

## django_migrations

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `app` | `character varying(255) NOT NULL` | (Required) |
| `name` | `character varying(255) NOT NULL` | (Required) |
| `applied` | `timestamp with time zone NOT NULL` | (Required) |

## django_session

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `session_key` | `character varying(40) NOT NULL` | (Required) |
| `session_data` | `text NOT NULL` | (Required) |
| `expire_date` | `timestamp with time zone NOT NULL` | (Required) |

## django_site

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer NOT NULL` | (Required, Primary Key) |
| `domain` | `character varying(100) NOT NULL` | (Required) |
| `name` | `character varying(50) NOT NULL` | (Required) |

## seydam_contactus

_User contact form submissions._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `name` | `text NOT NULL` | (Required) |
| `email` | `text NOT NULL` | (Required) |
| `subject` | `text NOT NULL` | (Required) |
| `message` | `text NOT NULL` | (Required) |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |

## seydam_customuser

_Core user table, extending the default Django user model._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | **Unique numeric ID for the user.** (Required, Primary Key) |
| `password` | `character varying(128) NOT NULL` | (Required) |
| `last_login` | `timestamp with time zone` | Standard field |
| `is_superuser` | `boolean NOT NULL` | (Required) |
| `first_name` | `character varying(150) NOT NULL` | (Required) |
| `last_name` | `character varying(150) NOT NULL` | (Required) |
| `is_staff` | `boolean NOT NULL` | (Required) |
| `is_active` | `boolean NOT NULL` | **True if the user is allowed to login.** (Required) |
| `date_joined` | `timestamp with time zone NOT NULL` | **Timestamp of registration.** (Required) |
| `username` | `character varying(150)` | Standard field |
| `email` | `character varying(254) NOT NULL` | **Primary email address (used for login).** (Required) |

## seydam_customuser_groups

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `customuser_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |
| `group_id` | `integer NOT NULL` | (Required, FK to `public.auth_group`) |

## seydam_customuser_user_permissions

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `customuser_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |
| `permission_id` | `integer NOT NULL` | (Required, FK to `public.auth_permission`) |

## seydam_emailotp

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `email` | `text NOT NULL` | (Required) |
| `otp` | `bigint NOT NULL` | (Required) |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |

## seydam_jsonreport

_Stores the full JSON structure of generated reports._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `report_json` | `jsonb NOT NULL` | (Required) |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |
| `report_id` | `uuid` | (FK to `public.seydam_reports`) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_outline

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `outline` | `jsonb NOT NULL` | (Required) |
| `report_id` | `uuid` | (FK to `public.seydam_reports`) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_payment

_Records user payments and credit purchases._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `reports_paid` | `integer NOT NULL` | **Number of credits/reports purchased in this transaction.** (Required) |
| `last_reference` | `character varying(255)` | Standard field |
| `last_amount` | `integer NOT NULL` | **Monetary amount charged (in smallest currency unit, usually cents).** (Required) |
| `last_status` | `character varying(50) NOT NULL` | **Status from payment gateway (succeeded, failed).** (Required) |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |
| `updated_at` | `timestamp with time zone NOT NULL` | (Required) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_rawhtmlcode

_Stores the rendered HTML version of reports._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `html` | `text NOT NULL` | (Required) |
| `saved_at` | `timestamp with time zone NOT NULL` | (Required) |
| `report_id` | `uuid NOT NULL` | (Required, FK to `public.seydam_reports`) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_referencejobid

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `job_id` | `text NOT NULL` | (Required) |
| `status` | `character varying(32) NOT NULL` | (Required) |
| `attempts` | `integer NOT NULL` | (Required) |
| `last_checked` | `timestamp with time zone` | Standard field |
| `last_error` | `text` | Standard field |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |
| `updated_at` | `timestamp with time zone NOT NULL` | (Required) |
| `report_id` | `uuid` | (FK to `public.seydam_reports`) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_references

_Stores citations and references used in report generation._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `reference_list` | `jsonb NOT NULL` | (Required) |
| `report_id` | `uuid` | (FK to `public.seydam_reports`) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_reportdirectory

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `project_directory` | `text NOT NULL` | (Required) |
| `project_id` | `uuid NOT NULL` | (Required, FK to `public.seydam_reports`) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_reportjobid

_Tracks the status of background report generation jobs._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `job_id` | `text` | Standard field |
| `status` | `character varying(32) NOT NULL` | (Required) |
| `attempts` | `integer NOT NULL` | (Required) |
| `last_checked` | `timestamp with time zone` | Standard field |
| `last_error` | `text` | Standard field |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |
| `updated_at` | `timestamp with time zone NOT NULL` | (Required) |
| `stage` | `character varying(64) NOT NULL` | (Required) |
| `progress` | `smallint NOT NULL` | (Required) |
| `report_id` | `uuid` | (FK to `public.seydam_reports`) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_reports

_Stores metadata for AI-generated reports._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid NOT NULL` | (Required, Primary Key) |
| `report_topic` | `text NOT NULL` | **User-provided topic for the report.** (Required) |
| `description` | `text NOT NULL` | (Required) |
| `status` | `text NOT NULL` | **Workflow status (e.g., pending, completed, failed).** (Required) |
| `amounted_credits` | `integer NOT NULL` | **Credits deducted for this report.** (Required) |
| `used_credits` | `integer NOT NULL` | (Required) |
| `is_free` | `boolean NOT NULL` | **True if this report did not consume paid credits.** (Required) |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_surveyresponse

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `satisfaction_score` | `smallint NOT NULL` | (Required) |
| `recommend_score` | `text NOT NULL` | (Required) |
| `process_easy` | `boolean NOT NULL` | (Required) |
| `process_feedback` | `text` | Standard field |
| `met_expectations` | `boolean NOT NULL` | (Required) |
| `most_valuable_feature` | `character varying(50) NOT NULL` | (Required) |
| `submitted_at` | `timestamp with time zone NOT NULL` | (Required) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_tokenusage

_Log of LLM token consumption per user for billing/analytics._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `output_tokens` | `integer NOT NULL` | (Required) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_uploadedimage

_Images uploaded by users for analysis or profile._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `description` | `text NOT NULL` | (Required) |
| `image` | `character varying(100) NOT NULL` | (Required) |
| `uploaded_at` | `timestamp with time zone NOT NULL` | (Required) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## seydam_waitlist

_Email waitlist for pre-launch interest._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `email` | `text NOT NULL` | (Required) |
| `created_at` | `timestamp with time zone NOT NULL` | (Required) |

## socialaccount_socialaccount

_Linked social login accounts (cached from providers)._

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer NOT NULL` | (Required, Primary Key) |
| `provider` | `character varying(200) NOT NULL` | (Required) |
| `uid` | `character varying(191) NOT NULL` | (Required) |
| `last_login` | `timestamp with time zone NOT NULL` | (Required) |
| `date_joined` | `timestamp with time zone NOT NULL` | (Required) |
| `extra_data` | `jsonb NOT NULL` | (Required) |
| `user_id` | `bigint NOT NULL` | (Required, FK to `public.seydam_customuser`) |

## socialaccount_socialapp

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer NOT NULL` | (Required, Primary Key) |
| `provider` | `character varying(30) NOT NULL` | (Required) |
| `name` | `character varying(40) NOT NULL` | (Required) |
| `client_id` | `character varying(191) NOT NULL` | (Required) |
| `secret` | `character varying(191) NOT NULL` | (Required) |
| `key` | `character varying(191) NOT NULL` | (Required) |
| `provider_id` | `character varying(200) NOT NULL` | (Required) |
| `settings` | `jsonb NOT NULL` | (Required) |

## socialaccount_socialapp_sites

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `socialapp_id` | `integer NOT NULL` | (Required, FK to `public.socialaccount_socialapp`) |
| `site_id` | `integer NOT NULL` | (Required, FK to `public.django_site`) |

## socialaccount_socialtoken

**Schema**: `public`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer NOT NULL` | (Required, Primary Key) |
| `token` | `text NOT NULL` | (Required) |
| `token_secret` | `text NOT NULL` | (Required) |
| `expires_at` | `timestamp with time zone` | Standard field |
| `account_id` | `integer NOT NULL` | (Required, FK to `public.socialaccount_socialaccount`) |
| `app_id` | `integer` | (FK to `public.socialaccount_socialapp`) |

## messages

**Schema**: `realtime`

| Column | Type | Description |
| :--- | :--- | :--- |
| `topic` | `text NOT NULL` | (Required) |
| `extension` | `text NOT NULL` | (Required) |
| `payload` | `jsonb` | Standard field |
| `event` | `text` | Standard field |
| `private` | `boolean DEFAULT false` | (Has Default) |
| `updated_at` | `timestamp without time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `inserted_at` | `timestamp without time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `id` | `uuid DEFAULT gen_random_uuid() NOT NULL` | (Required, Has Default, Primary Key) |
| `PARTITION` | `BY RANGE (inserted_at` | Standard field |

## schema_migrations

**Schema**: `realtime`

| Column | Type | Description |
| :--- | :--- | :--- |
| `version` | `bigint NOT NULL` | (Required) |
| `inserted_at` | `timestamp(0) without time zone` | Standard field |

## subscription

_Active realtime subscriptions for live updates._

**Schema**: `realtime`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `bigint NOT NULL` | (Required, Primary Key) |
| `subscription_id` | `uuid NOT NULL` | (Required) |
| `entity` | `regclass NOT NULL` | (Required) |
| `filters` | `realtime.user_defined_filter[] DEFAULT '{}'::realtime.user_defined_filter[] NOT NULL` | (Required, Has Default) |
| `claims` | `jsonb NOT NULL` | (Required) |
| `claims_role` | `regrole GENERATED ALWAYS AS (realtime.to_regrole((claims ->> 'role'::text))) STORED NOT NULL` | (Required) |
| `created_at` | `timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL` | (Required, Has Default) |

## buckets

_Configuration for file storage buckets._

**Schema**: `storage`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `text NOT NULL` | (Required, Primary Key) |
| `name` | `text NOT NULL` | (Required) |
| `owner` | `uuid` | Standard field |
| `created_at` | `timestamp with time zone DEFAULT now()` | (Has Default) |
| `updated_at` | `timestamp with time zone DEFAULT now()` | (Has Default) |
| `public` | `boolean DEFAULT false` | (Has Default) |
| `avif_autodetection` | `boolean DEFAULT false` | (Has Default) |
| `file_size_limit` | `bigint` | Standard field |
| `allowed_mime_types` | `text[]` | Standard field |
| `owner_id` | `text` | Standard field |
| `type` | `storage.buckettype DEFAULT 'STANDARD'::storage.buckettype NOT NULL` | (Required, Has Default) |

## buckets_analytics

**Schema**: `storage`

| Column | Type | Description |
| :--- | :--- | :--- |
| `name` | `text NOT NULL` | (Required) |
| `type` | `storage.buckettype DEFAULT 'ANALYTICS'::storage.buckettype NOT NULL` | (Required, Has Default) |
| `format` | `text DEFAULT 'ICEBERG'::text NOT NULL` | (Required, Has Default) |
| `created_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `updated_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `id` | `uuid DEFAULT gen_random_uuid() NOT NULL` | (Required, Has Default, Primary Key) |
| `deleted_at` | `timestamp with time zone` | Standard field |

## buckets_vectors

**Schema**: `storage`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `text NOT NULL` | (Required, Primary Key) |
| `type` | `storage.buckettype DEFAULT 'VECTOR'::storage.buckettype NOT NULL` | (Required, Has Default) |
| `created_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `updated_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |

## migrations

**Schema**: `storage`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer NOT NULL` | (Required, Primary Key) |
| `name` | `character varying(100) NOT NULL` | (Required) |
| `hash` | `character varying(40) NOT NULL` | (Required) |
| `executed_at` | `timestamp without time zone DEFAULT CURRENT_TIMESTAMP` | (Has Default) |

## objects

_Metadata for files stored in buckets._

**Schema**: `storage`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid DEFAULT gen_random_uuid() NOT NULL` | (Required, Has Default, Primary Key) |
| `bucket_id` | `text` | Standard field |
| `name` | `text` | Standard field |
| `owner` | `uuid` | Standard field |
| `created_at` | `timestamp with time zone DEFAULT now()` | (Has Default) |
| `updated_at` | `timestamp with time zone DEFAULT now()` | (Has Default) |
| `last_accessed_at` | `timestamp with time zone DEFAULT now()` | (Has Default) |
| `metadata` | `jsonb` | Standard field |
| `path_tokens` | `text[] GENERATED ALWAYS AS (string_to_array(name, '/'::text)) STORED` | Standard field |
| `version` | `text` | Standard field |
| `owner_id` | `text` | Standard field |
| `user_metadata` | `jsonb` | Standard field |
| `level` | `integer` | Standard field |

## prefixes

**Schema**: `storage`

| Column | Type | Description |
| :--- | :--- | :--- |
| `bucket_id` | `text NOT NULL` | (Required) |
| `name` | `text NOT NULL COLLATE pg_catalog."C"` | (Required) |
| `level` | `integer GENERATED ALWAYS AS (storage.get_level(name)) STORED NOT NULL` | (Required) |
| `created_at` | `timestamp with time zone DEFAULT now()` | (Has Default) |
| `updated_at` | `timestamp with time zone DEFAULT now()` | (Has Default) |

## s3_multipart_uploads

**Schema**: `storage`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `text NOT NULL` | (Required, Primary Key) |
| `in_progress_size` | `bigint DEFAULT 0 NOT NULL` | (Required, Has Default) |
| `upload_signature` | `text NOT NULL` | (Required) |
| `bucket_id` | `text NOT NULL` | (Required, FK to `storage.buckets`) |
| `key` | `text NOT NULL COLLATE pg_catalog."C"` | (Required) |
| `version` | `text NOT NULL` | (Required) |
| `owner_id` | `text` | Standard field |
| `created_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `user_metadata` | `jsonb` | Standard field |

## s3_multipart_uploads_parts

**Schema**: `storage`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `uuid DEFAULT gen_random_uuid() NOT NULL` | (Required, Has Default, Primary Key) |
| `upload_id` | `text NOT NULL` | (Required, FK to `storage.s3_multipart_uploads`) |
| `size` | `bigint DEFAULT 0 NOT NULL` | (Required, Has Default) |
| `part_number` | `integer NOT NULL` | (Required) |
| `bucket_id` | `text NOT NULL` | (Required, FK to `storage.buckets`) |
| `key` | `text NOT NULL COLLATE pg_catalog."C"` | (Required) |
| `etag` | `text NOT NULL` | (Required) |
| `owner_id` | `text` | Standard field |
| `version` | `text NOT NULL` | (Required) |
| `created_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |

## vector_indexes

**Schema**: `storage`

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `text DEFAULT gen_random_uuid() NOT NULL` | (Required, Has Default, Primary Key) |
| `name` | `text NOT NULL COLLATE pg_catalog."C"` | (Required) |
| `bucket_id` | `text NOT NULL` | (Required, FK to `storage.buckets_vectors`) |
| `data_type` | `text NOT NULL` | (Required) |
| `dimension` | `integer NOT NULL` | (Required) |
| `distance_metric` | `text NOT NULL` | (Required) |
| `metadata_configuration` | `jsonb` | Standard field |
| `created_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |
| `updated_at` | `timestamp with time zone DEFAULT now() NOT NULL` | (Required, Has Default) |

