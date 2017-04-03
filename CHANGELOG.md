# Change Log
All notable changes to this project will be documented in this file.

## [v0.0.0]
### Added
- Added the ability to parse a filename without reading data. This
  allows one to more easily convert filenames to `DatasetID`'s.
  
### Changed
- Moved MMParser to the leb extension.
- Default datasetType for the `parseFilename` method is now set to
  `Localizations` instead of the old `LocResults`.

### Fixed
- Fixed bug related to accessing the data attritubte of a Parser's
  dataset before the MMParser was fully initialized.

[v0.0.0]: https://github.com/kmdouglass/bsplugins-leb/releases/tag/v0.0.0

