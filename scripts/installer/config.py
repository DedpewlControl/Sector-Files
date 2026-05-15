FIRS = ["LFBB", "LFEE", "LFFF", "LFMM", "LFRR"]

REPO_LAYOUT_MAP = {
    "LFBB": "LFBB",
    "LFEE": "LFEE",
    "LFFF": "LFFF",
    "LFMM": "LFMM",
    "LFRR": "LFRR",
    "LFFM": "LFFM",
    "LFXX": "LFXX",
}

GNG_ONLY_FILES = [
    "LFXX/Sectors/*.sct",
    "LFXX/Sectors/*.ese",
    "LFXX/Sectors/*.rwy",
    "*/NavData/*.txt",
    "*/ICAO/*.txt",
    "*/Settings/LoginProfiles.txt",
    "*/Settings/VoiceChannels.txt",
]

# GitHub repo settings
GITHUB_OWNER = "DedpewlControl"
GITHUB_REPO = "Sector-Files"
GITHUB_BRANCH = "main"