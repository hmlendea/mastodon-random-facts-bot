# Privacy and Personal Data

This document describes how Mastodon Random Facts Bot at https://github.com/hmlendea/mastodon-random-facts-bot manages personal data. It covers the application conduct and verified integrations described below. Where the software is self-hosted, the instance operator may have separate responsibilities described below.

## 📑 Table of Contents

- [What This Document Covers](#-what-this-document-covers)
- [Self-Hosted Deployments](#-self-hosted-deployments)
- [Data We Handle](#-data-we-handle)
  - [Data Provided to the Application](#data-provided-to-the-application)
  - [Data Generated or Collected by the Application](#data-generated-or-collected-by-the-application)
  - [Data Received from Integrations](#data-received-from-integrations)
- [Processing and Use](#-processing-and-use)
- [Storage, Retention, and Deletion](#-storage-retention-and-deletion)
- [External Processing and Integrations](#-external-processing-and-integrations)
- [Data Protection and Security](#-data-protection-and-security)
- [Document Changes](#-document-changes)
- [Contact](#-contact)

## 🔎 What This Document Covers

This document describes how Mastodon Random Facts Bot at https://github.com/hmlendea/mastodon-random-facts-bot manages personal data. It covers the application conduct and verified integrations described below. Where the software is self-hosted, the instance operator may have separate responsibilities described below.

## 🏠 Self-Hosted Deployments

This document covers the Mastodon Random Facts Bot application code. The software is designed for self-hosted deployment; the instance operator controls the instance's configuration, local storage, logs, backups, access controls, preservation, and request handling. The project maintainers do not operate a hosted service and do not receive data from self-hosted instances.

The application does not send telemetry, crash reports, update checks, or any other data to the project maintainers or external services beyond the verified integrations described below. Operators can deactivate external integrations by modifying the configuration or facts file.

## 📥 Data We Handle

### Data Provided to the Application

- Mastodon instance URL (command-line argument)
- Mastodon username (command-line argument)
- Mastodon access token (command-line argument) — secret credential
- Tags to add to posts (command-line argument)
- Language code (command-line argument)
- Facts file path (command-line argument) — contains the facts to be posted

### Data Generated or Collected by the Application

- Application secret file (`app_<instance>.secret`) created on first run to register the Mastodon application
- Standard output logs including posted fact content, media URLs, and operation status
- No personal data is generated or collected automatically beyond the above

### Data Received from Integrations

- Media content downloaded from URLs embedded in facts (images, GIFs, videos)
- Mastodon API responses (status post confirmation, media upload confirmation)

## 🧭 Processing and Use

The application processes the data described above for these verified functions:
- Posting a random fact to a Mastodon instance — Mastodon access token, instance URL, username, fact content, tags, language
- Uploading media attached to facts — media URLs from facts, downloaded media content
- Registering the application with the Mastodon instance — instance URL, username

## 🗄️ Storage, Retention, and Deletion

- **Application secret file** (`app_<instance>.secret`): stored locally in the working directory; persists until manually deleted by the operator
- **Facts file**: provided by the operator; stored locally; retention controlled by the operator
- **Logs**: written to standard output; retention depends on the operator's logging infrastructure (e.g., systemd journal)
- **Downloaded media**: held in memory during upload; not persisted to disk by the application
- For self-hosted deployments, the instance operator controls all local storage, deletion, and backups

## 🔗 External Processing and Integrations

| Service or integration | Purpose | Data involved | Configuration or documentation |
|-----------------------|---------|---------------|--------------------------------|
| Mastodon API | Post statuses, upload media, register application | Access token, instance URL, username, fact text, tags, media content | https://docs.joinmastodon.org/api/ |
| Requests (HTTP library) | Download media from URLs in facts | Media URLs, downloaded media content | https://docs.python-requests.org/ |
| fake_useragent | Generate browser-like User-Agent for media downloads | None (generates synthetic User-Agent strings) | https://pypi.org/project/fake-useragent/ |

## 🛡️ Data Protection and Security

- The Mastodon access token is a secret credential provided via command-line argument; it is not logged by the application
- The application secret file contains the Mastodon application credentials; operators should protect file permissions
- Media downloads use a synthetic User-Agent; no personal identifiers are sent to media hosts
- For self-hosted deployments, the operator is responsible for updates, secrets management, access controls, backups, network exposure, and log protection
- The original maintainers are not responsible for changes, modifications, or privacy issues introduced by downstream forks

## 🔄 Document Changes

Update this document when application data processes, storage, integrations, or deployment responsibilities change. The current version is published at https://github.com/hmlendea/mastodon-random-facts-bot/blob/master/PRIVACY.md.

## 📬 Contact

For questions about application data handling, contact the project maintainers via GitHub issues at https://github.com/hmlendea/mastodon-random-facts-bot/issues. For a self-hosted instance, contact the instance operator, unless the project explicitly manages the request. Include the Mastodon instance URL and deployment details if relevant; do not send passwords, access tokens, or other secrets.