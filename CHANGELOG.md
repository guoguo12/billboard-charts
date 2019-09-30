# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## 5.3.0 - 2019-09-29
### Added
- Partial support for new Billboard.com UI used for some (but not all) charts.
  The `image` attribute is always set to `None` for such charts.

## 5.2.3 - 2019-09-06
### Fixed
- Fix `lastPos` again in response to UI change.
- Raise when HTTP request for `charts()` fails.

## 5.2.2 - 2019-08-27
### Fixed
- Stop sending HTTP header that was causing all requests to fail with HTTP 403.

## 5.2.1 - 2019-08-11
### Fixed
- Fix bug in which `lastPos` was set to the position two weeks prior instead of last week's position.

## 5.2.0 - 2019-08-09
### Added (since the last release, 5.1.1)
- This changelog file.
- The `charts` function for listing all charts (#40).
- Validation for dates passed to `ChartData` (#40).
