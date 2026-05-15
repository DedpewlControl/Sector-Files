FIRS = ["LFBB", "LFEE", "LFFF", "LFMM", "LFRR"]

REPO_LAYOUT_MAP = {
    "LFBB": "LFBB",
    "LFEE": "LFEE",
    "LFFF": "LFFF",
    "LFMM": "LFMM",
    "LFRR": "LFRR",
    "LFFM": "LFXX",
    "LFXX": "LFXX",
}

GNG_ONLY_FILES = [
    "LFXX/Sector/*.sct",
    "LFXX/Sector/*.ese",
    "LFXX/Sector/*.rwy",
    "*/NavData/*.txt",
    "*/ICAO/*.txt",
    "*/Settings/LoginProfiles.txt",
    "*/Settings/VoiceChannels.txt",
]

GITHUB_OWNER = "DedpewlControl"
GITHUB_REPO = "Sector-Files"
GITHUB_BRANCH = "main"

APP_NAME = "vACCFR Controller Pack Installer"