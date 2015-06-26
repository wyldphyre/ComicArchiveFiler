# ComicArchiveFiler
Examines comic archive files (.cbz and .cbz) and moves them to a new location based on configured rules.

The goal is a to provide an easy to use script that will look at the series metadata contained within a comic archive file and then file the archive by moving it to a new location, as specified by a simple rule configuration file.

# Requirements
- [ComicTagger](https://github.com/tomdelise/comictagger) (or [here, originally](https://code.google.com/p/comictagger/)) for extracting metadata from archive files

# Current Status
- Nothing yet, just getting started

# Roadmap:
- [Planned] Get the script to the going to the point of being able to examine an individual file and read the series infomation.
- [Planned] Read the configuration file that determines where an archive should be moved to
- [Planned] Send (optional) notification when a file is matched (maybe when no match made as well?). Pushover will be the initial target notification service/
- [Maybe] Handle folders and subfolders in addition to individual files
- [Maybe] Investigate using [ComicAPI](https://github.com/davide-romanini/comicapi) instead of requiring ComicTagger to be installed
