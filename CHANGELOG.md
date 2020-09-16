# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## 6.1.2 &ndash; 2020-09-15
### Fixed
- Fix parsing of `artist` for entries that are missing artists (#71).

## 6.1.1 &ndash; 2020-09-15
### Fixed
- Fix parsing of `previousDate`.

## 6.1.0 &ndash; 2020-03-21
### Changed
- Increased the default `max_retries` from 3 to 5.

## 6.0.3 &ndash; 2020-02-26
### Fixed
- Fix parsing of chart titles.

## 6.0.2 &ndash; 2020-02-01
### Fixed
- Fix parsing of entry stats for certain old-style charts.

## 6.0.1 &ndash; 2020-01-21
### Fixed
- Fix `peakPos` description.

## 6.0.0 &ndash; 2020-01-06
### Added
- Respect Retry-After headers when retrying (#65).
### Changed
- Switch to HTTPS for chart requests.

## 5.4.0 &ndash; 2019-12-27
### Added
- Connection retry logic (`max_retries`).

## 5.3.0 &ndash; 2019-09-29
### Added
- Partial support for new Billboard.com UI used for some (but not all) charts.
  The `image` attribute is always set to `None` for such charts.

## 5.2.3 &ndash; 2019-09-06
### Fixed
- Fix `lastPos` again in response to UI change.
- Raise when HTTP request for `charts()` fails.

## 5.2.2 &ndash; 2019-08-27
### Fixed
- Stop sending HTTP header that was causing all requests to fail with HTTP 403.

## 5.2.1 &ndash; 2019-08-11
### Fixed
- Fix bug in which `lastPos` was set to the position two weeks prior instead of last week's position.

## 5.2.0 &ndash; 2019-08-09
### Added (since the last release, 5.1.1)
- This changelog file.
- The `charts` function for listing all charts (#40).
- Validation for dates passed to `ChartData` (#40).
