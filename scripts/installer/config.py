FIRS = ["LFBB", "LFEE", "LFFF", "LFMM", "LFRR"]

REPO_LAYOUT_MAP = {
    "LFBB": "LFBB",
    "LFEE": "LFEE",
    "LFFF": "LFFF",
    "LFMM": "LFMM",
    "LFRR": "LFRR",
    "LFXX": "LFXX",
}

GNG_ONLY_FILES = [
    "LFXX/Sector/*.sct",
    "LFXX/Sector/*.ese",
    "LFXX/Sector/*.rwy",

    "LFXX/Alias/*",

    "LFBB/ICAO/*",
    "LFBB/NavData/*",
    "LFBB/Settings/LoginProfiles.txt",
    "LFBB/Settings/VoiceChannels.txt",

    "LFEE/ICAO/*",
    "LFEE/NavData/*",
    "LFEE/Settings/LoginProfiles.txt",
    "LFEE/Settings/VoiceChannels.txt",

    "LFFF/ICAO/*",
    "LFFF/NavData/*",
    "LFFF/Settings/LoginProfiles.txt",
    "LFFF/Settings/VoiceChannels.txt",

    "LFMM/ICAO/*",
    "LFMM/NavData/*",
    "LFMM/Settings/LoginProfiles.txt",
    "LFMM/Settings/VoiceChannels.txt",

    "LFRR/ICAO/*",
    "LFRR/NavData/*",
    "LFRR/Settings/LoginProfiles.txt",
    "LFRR/Settings/VoiceChannels.txt",
]

GITHUB_OWNER = "DedpewlControl"
GITHUB_REPO = "Sector-Files"
GITHUB_BRANCH = "main"

APP_NAME = "Controller Pack Installer"
VERSION_FILE = ".github/installer-version.txt"